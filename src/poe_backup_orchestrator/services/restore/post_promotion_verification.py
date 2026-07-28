"""Verify authoritative promotion and emit restore-completion evidence."""

from __future__ import annotations

import hashlib
import json
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.restore_authoritative_promotion import (
    RestoreAuthoritativePromotion,
    RestoreAuthoritativePromotionStatus,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_post_promotion_verification import (
    RESTORE_POST_PROMOTION_VERIFICATION_SCHEMA_VERSION,
    RestorePostPromotionVerification,
    RestorePostPromotionVerificationReasonCode,
    RestorePostPromotionVerificationStatus,
)
from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
)


class RestorePostPromotionVerificationError(RuntimeError):
    """Raised when promoted authoritative state cannot be verified."""


@dataclass(frozen=True, slots=True)
class RestorePostPromotionVerificationService:
    """Verify one completed authoritative promotion without mutation."""

    digest_chunk_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.digest_chunk_size <= 0:
            raise ValueError("digest_chunk_size must be positive")

    def verify(
        self,
        plan: RestorePlan,
        promotion: RestoreAuthoritativePromotion,
        *,
        verified_at_utc: datetime,
    ) -> RestorePostPromotionVerification:
        """Verify promoted state and produce restore-completion evidence."""

        _require_utc(verified_at_utc, "verified_at_utc")
        _validate_promotion_contract(plan, promotion)
        _validate_ownership_lock(promotion.ownership)

        if plan.staging_target_path.exists() or plan.staging_target_path.is_symlink():
            raise RestorePostPromotionVerificationError(
                "staged path reappeared after authoritative promotion"
            )

        authoritative = _observe_regular_file(
            plan.authoritative_target_path,
            self.digest_chunk_size,
            "authoritative target",
        )
        _require_observation_match(
            authoritative,
            promotion.promoted_observation,
            "authoritative target changed after promotion",
        )

        rollback = _revalidate_rollback(plan, promotion, self.digest_chunk_size)
        _validate_ownership_lock(promotion.ownership)

        return RestorePostPromotionVerification(
            schema_version=RESTORE_POST_PROMOTION_VERIFICATION_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            verified_at_utc=verified_at_utc,
            status=RestorePostPromotionVerificationStatus.VERIFIED,
            reason_codes=(
                RestorePostPromotionVerificationReasonCode.PROMOTION_EVIDENCE_ACCEPTED,
                RestorePostPromotionVerificationReasonCode.EXECUTION_OWNERSHIP_REVALIDATED,
                RestorePostPromotionVerificationReasonCode.AUTHORITATIVE_ARTIFACT_VERIFIED,
                RestorePostPromotionVerificationReasonCode.STAGED_PATH_CONSUMPTION_VERIFIED,
                RestorePostPromotionVerificationReasonCode.ROLLBACK_ARTIFACT_PRESERVED,
                RestorePostPromotionVerificationReasonCode.POST_PROMOTION_VERIFICATION_COMPLETED,
                RestorePostPromotionVerificationReasonCode.RESTORE_COMPLETED,
            ),
            promotion_executed_at_utc=promotion.executed_at_utc,
            ownership=promotion.ownership,
            promoted_observation=promotion.promoted_observation,
            verified_authoritative_observation=authoritative,
            rollback_observation=rollback,
            authoritative_integrity_verified=True,
            staged_path_consumed=True,
            rollback_artifact_preserved=True,
            execution_ownership_continuous=True,
            post_promotion_verification_completed=True,
            restore_completed=True,
        )


def _validate_promotion_contract(
    plan: RestorePlan,
    promotion: RestoreAuthoritativePromotion,
) -> None:
    if promotion.plan_id != plan.plan_id:
        raise RestorePostPromotionVerificationError("promotion plan_id does not match restore plan")
    if promotion.status is not RestoreAuthoritativePromotionStatus.PROMOTED:
        raise RestorePostPromotionVerificationError(
            "promotion evidence must report promoted status"
        )
    if not promotion.post_promotion_verification_required:
        raise RestorePostPromotionVerificationError(
            "promotion evidence does not require post-promotion verification"
        )
    if promotion.restore_completed:
        raise RestorePostPromotionVerificationError(
            "promotion evidence must not already declare restore completion"
        )
    if not promotion.atomic_replace_used:
        raise RestorePostPromotionVerificationError(
            "promotion evidence does not prove atomic replacement"
        )
    if not promotion.promoted_file_fsynced:
        raise RestorePostPromotionVerificationError(
            "promotion evidence does not prove promoted-file durability"
        )
    if not promotion.authoritative_parent_fsynced:
        raise RestorePostPromotionVerificationError(
            "promotion evidence does not prove parent-directory durability"
        )
    if promotion.promoted_observation.path != plan.authoritative_target_path:
        raise RestorePostPromotionVerificationError(
            "promotion authoritative path does not match restore plan"
        )
    if promotion.ownership.plan_id != plan.plan_id:
        raise RestorePostPromotionVerificationError(
            "promotion ownership plan_id does not match restore plan"
        )


def _validate_ownership_lock(ownership: RestoreExecutionOwnership) -> None:
    try:
        file_stat = ownership.lock_path.lstat()
    except OSError as exc:
        raise RestorePostPromotionVerificationError(
            f"execution ownership lock could not be inspected: {exc}"
        ) from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise RestorePostPromotionVerificationError(
            "execution ownership lock is not a regular file"
        )

    try:
        payload = json.loads(ownership.lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestorePostPromotionVerificationError(
            f"execution ownership lock could not be validated: {exc}"
        ) from exc

    expected = {
        "plan_id": ownership.plan_id,
        "owner_pid": ownership.owner_pid,
        "owner_hostname": ownership.owner_hostname,
        "acquired_at_utc": ownership.acquired_at_utc.isoformat(),
    }
    if payload != expected:
        raise RestorePostPromotionVerificationError(
            "execution ownership lock identity changed after promotion"
        )


def _revalidate_rollback(
    plan: RestorePlan,
    promotion: RestoreAuthoritativePromotion,
    chunk_size: int,
) -> RestorePromotionArtifactObservation | None:
    expected = promotion.rollback_observation
    rollback = plan.rollback_artifact_path

    if expected is None:
        if rollback.exists() or rollback.is_symlink():
            raise RestorePostPromotionVerificationError(
                "unexpected rollback artifact appeared after promotion"
            )
        return None

    actual = _observe_regular_file(rollback, chunk_size, "rollback artifact")
    _require_observation_match(
        actual,
        expected,
        "rollback artifact changed after promotion",
    )
    return actual


def _require_observation_match(
    actual: RestorePromotionArtifactObservation,
    expected: RestorePromotionArtifactObservation,
    message: str,
) -> None:
    if (
        actual.path != expected.path
        or actual.size_bytes != expected.size_bytes
        or actual.sha256 != expected.sha256
        or actual.mode != expected.mode
    ):
        raise RestorePostPromotionVerificationError(message)


def _observe_regular_file(
    path: Path,
    chunk_size: int,
    label: str,
) -> RestorePromotionArtifactObservation:
    try:
        before = path.lstat()
    except OSError as exc:
        raise RestorePostPromotionVerificationError(
            f"{label} could not be inspected: {exc}"
        ) from exc
    if not stat.S_ISREG(before.st_mode):
        raise RestorePostPromotionVerificationError(f"{label} is not a regular file")

    digest = hashlib.sha256()
    size_bytes = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
                size_bytes += len(chunk)
    except OSError as exc:
        raise RestorePostPromotionVerificationError(f"{label} could not be read: {exc}") from exc

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
        raise RestorePostPromotionVerificationError(f"{label} changed during verification")

    return RestorePromotionArtifactObservation(
        path=path,
        size_bytes=size_bytes,
        sha256=digest.hexdigest(),
        mode=stat.S_IMODE(after.st_mode),
        modified_at_utc=datetime.fromtimestamp(after.st_mtime, tz=UTC),
    )


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RestorePostPromotionVerificationError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise RestorePostPromotionVerificationError(f"{field_name} must use UTC")
