"""Read-only authoritative target preflight and rollback planning."""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.restore_authoritative_target_preflight import (
    RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION,
    RestoreAuthoritativeTargetObservation,
    RestoreAuthoritativeTargetPreflight,
    RestoreAuthoritativeTargetPreflightReasonCode,
    RestoreAuthoritativeTargetPreflightStatus,
    RestoreAuthoritativeTargetState,
    RestoreRollbackPlan,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_registry_application_validation import (
    RestoreRegistryApplicationValidation,
    RestoreRegistryApplicationValidationStatus,
)


class RestoreAuthoritativeTargetPreflightError(RuntimeError):
    """Raised when authoritative-target preflight is unsafe."""


@dataclass(frozen=True, slots=True)
class RestoreAuthoritativeTargetPreflightService:
    """Inspect target state and derive rollback obligations without mutation."""

    digest_chunk_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.digest_chunk_size <= 0:
            raise ValueError("digest_chunk_size must be positive")

    def preflight(
        self,
        plan: RestorePlan,
        application_validation: RestoreRegistryApplicationValidation,
        *,
        preflight_at_utc: datetime,
    ) -> RestoreAuthoritativeTargetPreflight:
        _validate_inputs(plan, application_validation, preflight_at_utc)
        _validate_path_separation(plan)

        target = plan.authoritative_target_path
        rollback = plan.rollback_artifact_path

        if rollback.exists() or rollback.is_symlink():
            raise RestoreAuthoritativeTargetPreflightError("rollback destination already exists")

        rollback_parent = rollback.parent
        if not rollback_parent.is_dir():
            raise RestoreAuthoritativeTargetPreflightError(
                "rollback destination parent does not exist"
            )
        if not os.access(rollback_parent, os.W_OK | os.X_OK):
            raise RestoreAuthoritativeTargetPreflightError(
                "rollback destination parent is not writable"
            )

        reason_codes = [
            RestoreAuthoritativeTargetPreflightReasonCode.APPLICATION_VALIDATION_ACCEPTED
        ]

        if not target.exists() and not target.is_symlink():
            state = RestoreAuthoritativeTargetState.ABSENT
            observation = None
            rollback_required = False
            rollback_source = None
            reason_codes.extend(
                (
                    RestoreAuthoritativeTargetPreflightReasonCode.AUTHORITATIVE_TARGET_ABSENT,
                    RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_NOT_REQUIRED,
                )
            )
        else:
            try:
                target_stat = target.stat()
            except OSError as exc:
                raise RestoreAuthoritativeTargetPreflightError(
                    f"authoritative target could not be inspected: {exc}"
                ) from exc

            if not stat.S_ISREG(target_stat.st_mode):
                raise RestoreAuthoritativeTargetPreflightError(
                    "authoritative target is not a regular file"
                )
            if not os.access(target, os.R_OK):
                raise RestoreAuthoritativeTargetPreflightError(
                    "authoritative target is not readable"
                )

            before = _stable_identity(target_stat)
            digest, size_bytes = _sha256(target, self.digest_chunk_size)
            try:
                after_stat = target.stat()
            except OSError as exc:
                raise RestoreAuthoritativeTargetPreflightError(
                    f"authoritative target changed during inspection: {exc}"
                ) from exc
            if before != _stable_identity(after_stat):
                raise RestoreAuthoritativeTargetPreflightError(
                    "authoritative target changed during inspection"
                )
            if size_bytes != after_stat.st_size:
                raise RestoreAuthoritativeTargetPreflightError(
                    "authoritative target byte count changed during inspection"
                )

            state = RestoreAuthoritativeTargetState.REGULAR_FILE
            observation = RestoreAuthoritativeTargetObservation(
                path=target,
                size_bytes=size_bytes,
                sha256=digest,
                mode=stat.S_IMODE(after_stat.st_mode),
                owner_uid=after_stat.st_uid,
                owner_gid=after_stat.st_gid,
                modified_at_utc=datetime.fromtimestamp(
                    after_stat.st_mtime,
                    tz=UTC,
                ),
            )
            rollback_required = True
            rollback_source = target
            reason_codes.extend(
                (
                    RestoreAuthoritativeTargetPreflightReasonCode.AUTHORITATIVE_TARGET_REGULAR_FILE,
                    RestoreAuthoritativeTargetPreflightReasonCode.AUTHORITATIVE_TARGET_READABLE,
                    RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_REQUIRED,
                )
            )

        reason_codes.extend(
            (
                RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_DESTINATION_AVAILABLE,
                RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_PARENT_READY,
                RestoreAuthoritativeTargetPreflightReasonCode.PREFLIGHT_READY,
            )
        )

        return RestoreAuthoritativeTargetPreflight(
            schema_version=RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            preflight_at_utc=preflight_at_utc,
            status=RestoreAuthoritativeTargetPreflightStatus.READY,
            reason_codes=tuple(reason_codes),
            authoritative_target_path=target,
            target_state=state,
            target_observation=observation,
            rollback_plan=RestoreRollbackPlan(
                required=rollback_required,
                source_path=rollback_source,
                destination_path=rollback,
                destination_parent_ready=True,
                destination_available=True,
            ),
            staged_artifact_modified=False,
            authoritative_target_modified=False,
            rollback_artifact_created=False,
        )


def preflight_authoritative_target(
    plan: RestorePlan,
    application_validation: RestoreRegistryApplicationValidation,
    *,
    preflight_at_utc: datetime,
    digest_chunk_size: int = 1024 * 1024,
) -> RestoreAuthoritativeTargetPreflight:
    """Perform one authoritative-target preflight."""

    return RestoreAuthoritativeTargetPreflightService(
        digest_chunk_size=digest_chunk_size
    ).preflight(
        plan,
        application_validation,
        preflight_at_utc=preflight_at_utc,
    )


def _validate_inputs(
    plan: RestorePlan,
    application_validation: RestoreRegistryApplicationValidation,
    preflight_at_utc: datetime,
) -> None:
    if preflight_at_utc.tzinfo is None or preflight_at_utc.utcoffset() is None:
        raise RestoreAuthoritativeTargetPreflightError("preflight_at_utc must be timezone-aware")
    if preflight_at_utc.utcoffset() != UTC.utcoffset(preflight_at_utc):
        raise RestoreAuthoritativeTargetPreflightError("preflight_at_utc must use UTC")
    if application_validation.plan_id != plan.plan_id:
        raise RestoreAuthoritativeTargetPreflightError(
            "application validation plan_id does not match restore plan"
        )
    if application_validation.status is not RestoreRegistryApplicationValidationStatus.VALID:
        raise RestoreAuthoritativeTargetPreflightError(
            "Registry application validation must be successful"
        )
    if application_validation.staged_path != plan.staging_target_path:
        raise RestoreAuthoritativeTargetPreflightError(
            "validated staged path does not match restore plan"
        )
    if application_validation.staged_artifact_modified:
        raise RestoreAuthoritativeTargetPreflightError(
            "application validation reports staged artifact modification"
        )
    if application_validation.authoritative_target_modified:
        raise RestoreAuthoritativeTargetPreflightError(
            "application validation reports authoritative target modification"
        )


def _validate_path_separation(plan: RestorePlan) -> None:
    target = plan.authoritative_target_path.resolve(strict=False)
    staged = plan.staging_target_path.resolve(strict=False)
    rollback = plan.rollback_artifact_path.resolve(strict=False)

    if target == staged:
        raise RestoreAuthoritativeTargetPreflightError(
            "authoritative target collides with staged artifact"
        )
    if target == rollback:
        raise RestoreAuthoritativeTargetPreflightError(
            "rollback destination collides with authoritative target"
        )
    if staged == rollback:
        raise RestoreAuthoritativeTargetPreflightError(
            "rollback destination collides with staged artifact"
        )


def _sha256(path: Path, chunk_size: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    size_bytes = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
                size_bytes += len(chunk)
    except OSError as exc:
        raise RestoreAuthoritativeTargetPreflightError(
            f"authoritative target could not be read: {exc}"
        ) from exc
    return digest.hexdigest(), size_bytes


def _stable_identity(file_stat: os.stat_result) -> tuple[int, int, int, int]:
    return (
        file_stat.st_dev,
        file_stat.st_ino,
        file_stat.st_size,
        file_stat.st_mtime_ns,
    )
