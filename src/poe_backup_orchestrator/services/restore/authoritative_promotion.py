"""Controlled atomic promotion of a staged restore artifact."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.restore_authoritative_promotion import (
    RESTORE_AUTHORITATIVE_PROMOTION_SCHEMA_VERSION,
    RestoreAuthoritativePromotion,
    RestoreAuthoritativePromotionReasonCode,
    RestoreAuthoritativePromotionStatus,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
    RestorePromotionReadiness,
    RestorePromotionReadinessStatus,
)


class RestoreAuthoritativePromotionError(RuntimeError):
    """Raised when controlled authoritative promotion cannot be proven safe."""


@dataclass(frozen=True, slots=True)
class RestoreAuthoritativePromotionService:
    """Perform one ownership-bound atomic authoritative promotion."""

    digest_chunk_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.digest_chunk_size <= 0:
            raise ValueError("digest_chunk_size must be positive")

    def execute(
        self,
        plan: RestorePlan,
        readiness: RestorePromotionReadiness,
        *,
        executed_at_utc: datetime,
    ) -> RestoreAuthoritativePromotion:
        """Atomically replace the authoritative target with the staged artifact."""

        _require_utc(executed_at_utc, "executed_at_utc")
        _validate_readiness(plan, readiness)
        _validate_path_separation(plan, readiness.ownership)
        _validate_ownership_lock(readiness.ownership)

        staged = _observe_regular_file(
            plan.staging_target_path,
            self.digest_chunk_size,
            "staged artifact",
        )
        _require_observation_match(
            staged,
            readiness.staged_observation,
            "staged artifact changed after readiness",
        )

        prior_authoritative = _revalidate_authoritative(plan, readiness, self.digest_chunk_size)
        rollback = _revalidate_rollback(plan, readiness, self.digest_chunk_size)

        try:
            os.replace(plan.staging_target_path, plan.authoritative_target_path)
        except OSError as exc:
            raise RestoreAuthoritativePromotionError(
                f"atomic authoritative promotion failed before completion: {exc}"
            ) from exc

        try:
            _fsync_regular_file(plan.authoritative_target_path)
            _fsync_directory(plan.authoritative_target_path.parent)
            promoted = _observe_regular_file(
                plan.authoritative_target_path,
                self.digest_chunk_size,
                "promoted authoritative artifact",
            )
        except (OSError, RestoreAuthoritativePromotionError) as exc:
            raise RestoreAuthoritativePromotionError(
                "authoritative promotion occurred but durability or observation "
                f"could not be established: {exc}"
            ) from exc

        if plan.staging_target_path.exists() or plan.staging_target_path.is_symlink():
            raise RestoreAuthoritativePromotionError(
                "authoritative promotion occurred but staged path was not consumed"
            )

        _require_observation_match(
            promoted,
            readiness.staged_observation,
            "promoted authoritative artifact does not match staged evidence",
            compare_path=False,
            compare_mode=False,
        )

        _validate_ownership_lock(readiness.ownership)
        _revalidate_rollback(plan, readiness, self.digest_chunk_size)

        return RestoreAuthoritativePromotion(
            schema_version=RESTORE_AUTHORITATIVE_PROMOTION_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            executed_at_utc=executed_at_utc,
            status=RestoreAuthoritativePromotionStatus.PROMOTED,
            reason_codes=(
                RestoreAuthoritativePromotionReasonCode.READINESS_ACCEPTED,
                RestoreAuthoritativePromotionReasonCode.EXECUTION_OWNERSHIP_REVALIDATED,
                RestoreAuthoritativePromotionReasonCode.STAGED_ARTIFACT_REVALIDATED,
                RestoreAuthoritativePromotionReasonCode.AUTHORITATIVE_BOUNDARY_REVALIDATED,
                RestoreAuthoritativePromotionReasonCode.ROLLBACK_ARTIFACT_PRESERVED,
                RestoreAuthoritativePromotionReasonCode.ATOMIC_PROMOTION_COMPLETED,
                RestoreAuthoritativePromotionReasonCode.DURABILITY_SYNC_COMPLETED,
                RestoreAuthoritativePromotionReasonCode.POST_PROMOTION_VERIFICATION_REQUIRED,
            ),
            readiness_evaluated_at_utc=readiness.evaluated_at_utc,
            ownership=readiness.ownership,
            staged_observation=readiness.staged_observation,
            prior_authoritative_observation=prior_authoritative,
            rollback_observation=rollback,
            promoted_observation=promoted,
            atomic_replace_used=True,
            promoted_file_fsynced=True,
            authoritative_parent_fsynced=True,
            staged_path_consumed=True,
            authoritative_target_modified=True,
            rollback_artifact_modified=False,
            post_promotion_verification_required=True,
            restore_completed=False,
        )


def _validate_readiness(
    plan: RestorePlan,
    readiness: RestorePromotionReadiness,
) -> None:
    if readiness.plan_id != plan.plan_id:
        raise RestoreAuthoritativePromotionError(
            "promotion readiness plan_id does not match restore plan"
        )
    if readiness.status is not RestorePromotionReadinessStatus.READY:
        raise RestoreAuthoritativePromotionError("promotion readiness must be ready")
    if readiness.promotion_performed:
        raise RestoreAuthoritativePromotionError("promotion has already been performed")
    if readiness.staged_artifact_modified:
        raise RestoreAuthoritativePromotionError(
            "readiness reports prohibited staged-artifact modification"
        )
    if readiness.authoritative_target_modified:
        raise RestoreAuthoritativePromotionError(
            "readiness reports prohibited authoritative-target modification"
        )
    if readiness.rollback_artifact_modified:
        raise RestoreAuthoritativePromotionError(
            "readiness reports prohibited rollback-artifact modification"
        )
    if readiness.staged_observation.path != plan.staging_target_path:
        raise RestoreAuthoritativePromotionError(
            "readiness staged path does not match restore plan"
        )


def _validate_path_separation(
    plan: RestorePlan,
    ownership: RestoreExecutionOwnership,
) -> None:
    paths = {
        plan.staging_target_path.resolve(strict=False),
        plan.authoritative_target_path.resolve(strict=False),
        plan.rollback_artifact_path.resolve(strict=False),
        ownership.lock_path.resolve(strict=False),
    }
    if len(paths) != 4:
        raise RestoreAuthoritativePromotionError("governed promotion paths are not distinct")


def _validate_ownership_lock(ownership: RestoreExecutionOwnership) -> None:
    try:
        file_stat = ownership.lock_path.lstat()
    except OSError as exc:
        raise RestoreAuthoritativePromotionError(
            f"execution ownership lock could not be inspected: {exc}"
        ) from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise RestoreAuthoritativePromotionError("execution ownership lock is not a regular file")

    try:
        payload = json.loads(ownership.lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreAuthoritativePromotionError(
            f"execution ownership lock could not be validated: {exc}"
        ) from exc

    expected = {
        "plan_id": ownership.plan_id,
        "owner_pid": ownership.owner_pid,
        "owner_hostname": ownership.owner_hostname,
        "acquired_at_utc": ownership.acquired_at_utc.isoformat(),
    }
    if payload != expected:
        raise RestoreAuthoritativePromotionError(
            "execution ownership lock identity changed after readiness"
        )


def _revalidate_authoritative(
    plan: RestorePlan,
    readiness: RestorePromotionReadiness,
    chunk_size: int,
) -> RestorePromotionArtifactObservation | None:
    expected = readiness.authoritative_observation
    target = plan.authoritative_target_path

    if expected is None:
        if target.exists() or target.is_symlink():
            raise RestoreAuthoritativePromotionError(
                "authoritative target appeared after readiness"
            )
        return None

    actual = _observe_regular_file(target, chunk_size, "authoritative target")
    _require_observation_match(
        actual,
        expected,
        "authoritative target changed after readiness",
    )
    return actual


def _revalidate_rollback(
    plan: RestorePlan,
    readiness: RestorePromotionReadiness,
    chunk_size: int,
) -> RestorePromotionArtifactObservation | None:
    expected = readiness.rollback_observation
    rollback = plan.rollback_artifact_path

    if expected is None:
        if rollback.exists() or rollback.is_symlink():
            raise RestoreAuthoritativePromotionError(
                "unexpected rollback artifact exists after readiness"
            )
        return None

    actual = _observe_regular_file(rollback, chunk_size, "rollback artifact")
    _require_observation_match(
        actual,
        expected,
        "rollback artifact changed after readiness",
    )
    return actual


def _require_observation_match(
    actual: RestorePromotionArtifactObservation,
    expected: RestorePromotionArtifactObservation,
    message: str,
    *,
    compare_path: bool = True,
    compare_mode: bool = True,
) -> None:
    mismatch = (
        actual.size_bytes != expected.size_bytes
        or actual.sha256 != expected.sha256
        or (compare_path and actual.path != expected.path)
        or (compare_mode and actual.mode != expected.mode)
    )
    if mismatch:
        raise RestoreAuthoritativePromotionError(message)


def _observe_regular_file(
    path: Path,
    chunk_size: int,
    label: str,
) -> RestorePromotionArtifactObservation:
    try:
        before = path.lstat()
    except OSError as exc:
        raise RestoreAuthoritativePromotionError(f"{label} could not be inspected: {exc}") from exc
    if not stat.S_ISREG(before.st_mode):
        raise RestoreAuthoritativePromotionError(f"{label} is not a regular file")

    digest = hashlib.sha256()
    size_bytes = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
                size_bytes += len(chunk)
    except OSError as exc:
        raise RestoreAuthoritativePromotionError(f"{label} could not be read: {exc}") from exc

    after = path.lstat()
    if (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    ) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise RestoreAuthoritativePromotionError(f"{label} changed during promotion evaluation")

    return RestorePromotionArtifactObservation(
        path=path,
        size_bytes=size_bytes,
        sha256=digest.hexdigest(),
        mode=stat.S_IMODE(after.st_mode),
        modified_at_utc=datetime.fromtimestamp(after.st_mtime, tz=UTC),
    )


def _fsync_regular_file(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RestoreAuthoritativePromotionError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise RestoreAuthoritativePromotionError(f"{field_name} must use UTC")
