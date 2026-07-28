"""Exclusive restore ownership and fail-closed promotion readiness."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.restore_authoritative_target_preflight import (
    RestoreAuthoritativeTargetPreflight,
    RestoreAuthoritativeTargetPreflightStatus,
    RestoreAuthoritativeTargetState,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RESTORE_PROMOTION_READINESS_SCHEMA_VERSION,
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
    RestorePromotionReadiness,
    RestorePromotionReadinessReasonCode,
    RestorePromotionReadinessStatus,
)
from poe_backup_orchestrator.models.restore_registry_application_validation import (
    RestoreRegistryApplicationValidation,
    RestoreRegistryApplicationValidationStatus,
)
from poe_backup_orchestrator.models.restore_rollback_artifact_capture import (
    RestoreRollbackArtifactCapture,
    RestoreRollbackArtifactCaptureStatus,
)
from poe_backup_orchestrator.models.restore_staged_artifact_validation import (
    RestoreStagedArtifactValidation,
    RestoreStagedArtifactValidationStatus,
)


class RestorePromotionReadinessError(RuntimeError):
    """Raised when promotion readiness cannot be established safely."""


@dataclass(slots=True)
class RestoreExecutionOwnershipHandle:
    """Held execution ownership that must be released explicitly."""

    evidence: RestoreExecutionOwnership
    _released: bool = False

    def release(self) -> None:
        """Release the ownership lock."""

        if self._released:
            return
        try:
            self.evidence.lock_path.unlink()
            _fsync_directory(self.evidence.lock_path.parent)
        except FileNotFoundError:
            pass
        except OSError as exc:
            raise RestorePromotionReadinessError(
                f"execution ownership could not be released: {exc}"
            ) from exc
        self._released = True

    def __enter__(self) -> RestoreExecutionOwnershipHandle:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.release()


@dataclass(frozen=True, slots=True)
class RestorePromotionReadinessService:
    """Acquire ownership and revalidate the complete promotion boundary."""

    digest_chunk_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.digest_chunk_size <= 0:
            raise ValueError("digest_chunk_size must be positive")

    def acquire_ownership(
        self,
        *,
        plan_id: str,
        lock_path: Path,
        acquired_at_utc: datetime,
    ) -> RestoreExecutionOwnershipHandle:
        _require_utc(acquired_at_utc, "acquired_at_utc")
        if not plan_id.strip():
            raise RestorePromotionReadinessError("plan_id must not be empty")
        if not lock_path.parent.is_dir():
            raise RestorePromotionReadinessError("execution ownership parent does not exist")

        evidence = RestoreExecutionOwnership(
            lock_path=lock_path,
            plan_id=plan_id,
            owner_pid=os.getpid(),
            owner_hostname=socket.gethostname(),
            acquired_at_utc=acquired_at_utc,
        )
        payload = {
            "plan_id": evidence.plan_id,
            "owner_pid": evidence.owner_pid,
            "owner_hostname": evidence.owner_hostname,
            "acquired_at_utc": evidence.acquired_at_utc.isoformat(),
        }

        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor: int | None = None
        try:
            descriptor = os.open(lock_path, flags, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8", closefd=True) as handle:
                descriptor = None
                json.dump(payload, handle, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            _fsync_directory(lock_path.parent)
        except FileExistsError as exc:
            raise RestorePromotionReadinessError(
                "restore execution ownership is already held"
            ) from exc
        except OSError as exc:
            try:
                lock_path.unlink()
            except OSError:
                pass
            raise RestorePromotionReadinessError(
                f"restore execution ownership could not be acquired: {exc}"
            ) from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)

        return RestoreExecutionOwnershipHandle(evidence=evidence)

    def evaluate(
        self,
        plan: RestorePlan,
        staged_validation: RestoreStagedArtifactValidation,
        application_validation: RestoreRegistryApplicationValidation,
        preflight: RestoreAuthoritativeTargetPreflight,
        rollback_capture: RestoreRollbackArtifactCapture,
        ownership: RestoreExecutionOwnership,
        *,
        evaluated_at_utc: datetime,
    ) -> RestorePromotionReadiness:
        _require_utc(evaluated_at_utc, "evaluated_at_utc")
        _validate_evidence_chain(
            plan,
            staged_validation,
            application_validation,
            preflight,
            rollback_capture,
            ownership,
        )
        _validate_path_separation(plan)

        staged = _observe_regular_file(
            plan.staging_target_path,
            self.digest_chunk_size,
            "staged artifact",
        )

        if staged.size_bytes != staged_validation.staged_size_bytes:
            raise RestorePromotionReadinessError("staged artifact size changed after validation")
        if staged.sha256 != staged_validation.staged_sha256:
            raise RestorePromotionReadinessError("staged artifact SHA-256 changed after validation")

        authoritative = _revalidate_authoritative(
            plan,
            preflight,
            self.digest_chunk_size,
        )
        rollback = _revalidate_rollback(
            plan,
            rollback_capture,
            self.digest_chunk_size,
        )

        return RestorePromotionReadiness(
            schema_version=RESTORE_PROMOTION_READINESS_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            evaluated_at_utc=evaluated_at_utc,
            status=RestorePromotionReadinessStatus.READY,
            reason_codes=(
                RestorePromotionReadinessReasonCode.EXECUTION_OWNERSHIP_ACQUIRED,
                RestorePromotionReadinessReasonCode.EVIDENCE_CHAIN_ACCEPTED,
                RestorePromotionReadinessReasonCode.GOVERNED_PATHS_DISTINCT,
                RestorePromotionReadinessReasonCode.STAGED_ARTIFACT_REVALIDATED,
                RestorePromotionReadinessReasonCode.AUTHORITATIVE_TARGET_REVALIDATED,
                RestorePromotionReadinessReasonCode.ROLLBACK_ARTIFACT_REVALIDATED,
                RestorePromotionReadinessReasonCode.PROMOTION_READY,
            ),
            ownership=ownership,
            staged_observation=staged,
            authoritative_observation=authoritative,
            rollback_observation=rollback,
            staged_artifact_modified=False,
            authoritative_target_modified=False,
            rollback_artifact_modified=False,
            promotion_performed=False,
        )


def _validate_evidence_chain(
    plan: RestorePlan,
    staged_validation: RestoreStagedArtifactValidation,
    application_validation: RestoreRegistryApplicationValidation,
    preflight: RestoreAuthoritativeTargetPreflight,
    rollback_capture: RestoreRollbackArtifactCapture,
    ownership: RestoreExecutionOwnership,
) -> None:
    if staged_validation.plan_id != plan.plan_id:
        raise RestorePromotionReadinessError(
            "staged validation plan_id does not match restore plan"
        )
    if staged_validation.status is not RestoreStagedArtifactValidationStatus.VALID:
        raise RestorePromotionReadinessError("staged artifact validation must be successful")
    if staged_validation.staged_path != plan.staging_target_path:
        raise RestorePromotionReadinessError("staged validation path does not match restore plan")
    if staged_validation.authoritative_target_modified:
        raise RestorePromotionReadinessError(
            "staged validation reports prohibited authoritative-target modification"
        )

    if application_validation.plan_id != plan.plan_id:
        raise RestorePromotionReadinessError(
            "application validation plan_id does not match restore plan"
        )
    if application_validation.status is not RestoreRegistryApplicationValidationStatus.VALID:
        raise RestorePromotionReadinessError("Registry application validation must be successful")
    if application_validation.staged_path != plan.staging_target_path:
        raise RestorePromotionReadinessError("validated staged path does not match restore plan")
    if preflight.plan_id != plan.plan_id:
        raise RestorePromotionReadinessError("preflight plan_id does not match restore plan")
    if preflight.status is not RestoreAuthoritativeTargetPreflightStatus.READY:
        raise RestorePromotionReadinessError("authoritative target preflight must be ready")
    if preflight.authoritative_target_path != plan.authoritative_target_path:
        raise RestorePromotionReadinessError(
            "preflight authoritative target does not match restore plan"
        )
    if rollback_capture.plan_id != plan.plan_id:
        raise RestorePromotionReadinessError("rollback capture plan_id does not match restore plan")
    if rollback_capture.destination_path != plan.rollback_artifact_path:
        raise RestorePromotionReadinessError("rollback destination does not match restore plan")
    if rollback_capture.capture_required != preflight.rollback_plan.required:
        raise RestorePromotionReadinessError(
            "rollback capture requirement does not match preflight"
        )
    if ownership.plan_id != plan.plan_id:
        raise RestorePromotionReadinessError(
            "execution ownership plan_id does not match restore plan"
        )
    if not ownership.lock_path.is_file():
        raise RestorePromotionReadinessError("execution ownership lock is not present")

    modification_flags = (
        application_validation.staged_artifact_modified,
        application_validation.authoritative_target_modified,
        preflight.staged_artifact_modified,
        preflight.authoritative_target_modified,
        preflight.rollback_artifact_created,
        rollback_capture.staged_artifact_modified,
        rollback_capture.authoritative_target_modified,
    )
    if any(modification_flags):
        raise RestorePromotionReadinessError(
            "evidence chain reports prohibited artifact modification"
        )


def _validate_path_separation(plan: RestorePlan) -> None:
    target = plan.authoritative_target_path.resolve(strict=False)
    staged = plan.staging_target_path.resolve(strict=False)
    rollback = plan.rollback_artifact_path.resolve(strict=False)
    if len({target, staged, rollback}) != 3:
        raise RestorePromotionReadinessError("governed restore paths are not distinct")


def _revalidate_authoritative(
    plan: RestorePlan,
    preflight: RestoreAuthoritativeTargetPreflight,
    chunk_size: int,
) -> RestorePromotionArtifactObservation | None:
    target = plan.authoritative_target_path
    if preflight.target_state is RestoreAuthoritativeTargetState.ABSENT:
        if target.exists() or target.is_symlink():
            raise RestorePromotionReadinessError("authoritative target appeared after preflight")
        return None

    expected = preflight.target_observation
    if expected is None:
        raise RestorePromotionReadinessError("authoritative target observation is missing")
    actual = _observe_regular_file(target, chunk_size, "authoritative target")
    if actual.size_bytes != expected.size_bytes:
        raise RestorePromotionReadinessError("authoritative target size changed after preflight")
    if actual.sha256 != expected.sha256:
        raise RestorePromotionReadinessError("authoritative target SHA-256 changed after preflight")
    if actual.mode != expected.mode:
        raise RestorePromotionReadinessError("authoritative target mode changed after preflight")
    return actual


def _revalidate_rollback(
    plan: RestorePlan,
    capture: RestoreRollbackArtifactCapture,
    chunk_size: int,
) -> RestorePromotionArtifactObservation | None:
    destination = plan.rollback_artifact_path
    if not capture.capture_required:
        if capture.status is not RestoreRollbackArtifactCaptureStatus.NOT_REQUIRED:
            raise RestorePromotionReadinessError("rollback capture status is inconsistent")
        if destination.exists() or destination.is_symlink():
            raise RestorePromotionReadinessError("unexpected rollback artifact exists")
        return None

    if capture.status is not RestoreRollbackArtifactCaptureStatus.CAPTURED:
        raise RestorePromotionReadinessError("required rollback artifact was not captured")
    expected = capture.rollback_observation
    if expected is None:
        raise RestorePromotionReadinessError("rollback observation is missing")
    actual = _observe_regular_file(destination, chunk_size, "rollback artifact")
    if actual.size_bytes != expected.size_bytes:
        raise RestorePromotionReadinessError("rollback artifact size changed after capture")
    if actual.sha256 != expected.sha256:
        raise RestorePromotionReadinessError("rollback artifact SHA-256 changed after capture")
    if actual.mode != expected.mode:
        raise RestorePromotionReadinessError("rollback artifact mode changed after capture")
    return actual


def _observe_regular_file(
    path: Path,
    chunk_size: int,
    label: str,
) -> RestorePromotionArtifactObservation:
    try:
        before = path.stat()
    except OSError as exc:
        raise RestorePromotionReadinessError(f"{label} could not be inspected: {exc}") from exc
    if not stat.S_ISREG(before.st_mode):
        raise RestorePromotionReadinessError(f"{label} is not a regular file")

    digest = hashlib.sha256()
    size_bytes = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
                size_bytes += len(chunk)
    except OSError as exc:
        raise RestorePromotionReadinessError(f"{label} could not be read: {exc}") from exc

    after = path.stat()
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
        raise RestorePromotionReadinessError(f"{label} changed during readiness evaluation")

    return RestorePromotionArtifactObservation(
        path=path,
        size_bytes=size_bytes,
        sha256=digest.hexdigest(),
        mode=stat.S_IMODE(after.st_mode),
        modified_at_utc=datetime.fromtimestamp(after.st_mtime, tz=UTC),
    )


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RestorePromotionReadinessError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise RestorePromotionReadinessError(f"{field_name} must use UTC")


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
