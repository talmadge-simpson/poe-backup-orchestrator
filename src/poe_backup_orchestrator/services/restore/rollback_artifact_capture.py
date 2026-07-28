"""Rollback artifact capture and cryptographic validation."""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.restore_authoritative_target_preflight import (
    RestoreAuthoritativeTargetObservation,
    RestoreAuthoritativeTargetPreflight,
    RestoreAuthoritativeTargetPreflightStatus,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_rollback_artifact_capture import (
    RESTORE_ROLLBACK_ARTIFACT_CAPTURE_SCHEMA_VERSION,
    RestoreRollbackArtifactCapture,
    RestoreRollbackArtifactCaptureReasonCode,
    RestoreRollbackArtifactCaptureStatus,
    RestoreRollbackArtifactObservation,
)


class RestoreRollbackArtifactCaptureError(RuntimeError):
    """Raised when rollback artifact capture cannot be completed safely."""


@dataclass(frozen=True, slots=True)
class RestoreRollbackArtifactCaptureService:
    """Capture and validate an immutable rollback artifact."""

    copy_chunk_size: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.copy_chunk_size <= 0:
            raise ValueError("copy_chunk_size must be positive")

    def capture(
        self,
        plan: RestorePlan,
        preflight: RestoreAuthoritativeTargetPreflight,
        *,
        captured_at_utc: datetime,
    ) -> RestoreRollbackArtifactCapture:
        _validate_inputs(plan, preflight, captured_at_utc)

        rollback_plan = preflight.rollback_plan
        destination = rollback_plan.destination_path

        if not rollback_plan.required:
            if destination.exists() or destination.is_symlink():
                raise RestoreRollbackArtifactCaptureError(
                    "rollback destination exists although capture is not required"
                )
            return RestoreRollbackArtifactCapture(
                schema_version=RESTORE_ROLLBACK_ARTIFACT_CAPTURE_SCHEMA_VERSION,
                plan_id=plan.plan_id,
                captured_at_utc=captured_at_utc,
                status=RestoreRollbackArtifactCaptureStatus.NOT_REQUIRED,
                reason_codes=(
                    RestoreRollbackArtifactCaptureReasonCode.PREFLIGHT_ACCEPTED,
                    RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_NOT_REQUIRED,
                ),
                capture_required=False,
                source_path=None,
                destination_path=destination,
                source_observation=None,
                rollback_observation=None,
                copied_bytes=0,
                checksum_matched=True,
                source_remained_stable=True,
                mode_preserved=True,
                staged_artifact_modified=False,
                authoritative_target_modified=False,
            )

        source = rollback_plan.source_path
        expected = preflight.target_observation
        if source is None or expected is None:
            raise RestoreRollbackArtifactCaptureError(
                "required rollback is missing source observation"
            )

        if destination.exists() or destination.is_symlink():
            raise RestoreRollbackArtifactCaptureError("rollback destination already exists")
        if not destination.parent.is_dir():
            raise RestoreRollbackArtifactCaptureError("rollback destination parent does not exist")

        source_before = _observe_source(source, self.copy_chunk_size)
        _require_observation_match(expected, source_before)

        created = False
        try:
            copied_bytes, copied_digest = _copy_exclusively(
                source,
                destination,
                mode=source_before.mode,
                chunk_size=self.copy_chunk_size,
            )
            created = True

            rollback_observation = _observe_rollback(
                destination,
                self.copy_chunk_size,
            )
            source_after = _observe_source(source, self.copy_chunk_size)

            _require_observation_match(source_before, source_after)

            if copied_bytes != source_before.size_bytes:
                raise RestoreRollbackArtifactCaptureError(
                    "copied byte count does not match authoritative source"
                )
            if copied_digest != source_before.sha256:
                raise RestoreRollbackArtifactCaptureError(
                    "streamed rollback digest does not match authoritative source"
                )
            if rollback_observation.size_bytes != source_before.size_bytes:
                raise RestoreRollbackArtifactCaptureError(
                    "rollback byte count does not match authoritative source"
                )
            if rollback_observation.sha256 != source_before.sha256:
                raise RestoreRollbackArtifactCaptureError(
                    "rollback SHA-256 does not match authoritative source"
                )
            if rollback_observation.mode != source_before.mode:
                raise RestoreRollbackArtifactCaptureError(
                    "rollback mode does not match authoritative source"
                )

            return RestoreRollbackArtifactCapture(
                schema_version=RESTORE_ROLLBACK_ARTIFACT_CAPTURE_SCHEMA_VERSION,
                plan_id=plan.plan_id,
                captured_at_utc=captured_at_utc,
                status=RestoreRollbackArtifactCaptureStatus.CAPTURED,
                reason_codes=(
                    RestoreRollbackArtifactCaptureReasonCode.PREFLIGHT_ACCEPTED,
                    RestoreRollbackArtifactCaptureReasonCode.SOURCE_MATCHED_PREFLIGHT,
                    RestoreRollbackArtifactCaptureReasonCode.DESTINATION_CREATED_EXCLUSIVELY,
                    RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_BYTES_COPIED,
                    RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_BYTES_SYNCHRONIZED,
                    RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_MODE_PRESERVED,
                    RestoreRollbackArtifactCaptureReasonCode.BYTE_COUNT_MATCHED,
                    RestoreRollbackArtifactCaptureReasonCode.SHA256_MATCHED,
                    RestoreRollbackArtifactCaptureReasonCode.SOURCE_REMAINED_STABLE,
                    RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_CAPTURE_COMPLETE,
                ),
                capture_required=True,
                source_path=source,
                destination_path=destination,
                source_observation=source_before,
                rollback_observation=rollback_observation,
                copied_bytes=copied_bytes,
                checksum_matched=True,
                source_remained_stable=True,
                mode_preserved=True,
                staged_artifact_modified=False,
                authoritative_target_modified=False,
            )
        except Exception:
            if created or destination.exists() or destination.is_symlink():
                try:
                    destination.unlink()
                except OSError:
                    pass
            raise


def capture_rollback_artifact(
    plan: RestorePlan,
    preflight: RestoreAuthoritativeTargetPreflight,
    *,
    captured_at_utc: datetime,
    copy_chunk_size: int = 1024 * 1024,
) -> RestoreRollbackArtifactCapture:
    """Capture one rollback artifact."""

    return RestoreRollbackArtifactCaptureService(copy_chunk_size=copy_chunk_size).capture(
        plan,
        preflight,
        captured_at_utc=captured_at_utc,
    )


def _validate_inputs(
    plan: RestorePlan,
    preflight: RestoreAuthoritativeTargetPreflight,
    captured_at_utc: datetime,
) -> None:
    if captured_at_utc.tzinfo is None or captured_at_utc.utcoffset() is None:
        raise RestoreRollbackArtifactCaptureError("captured_at_utc must be timezone-aware")
    if captured_at_utc.utcoffset() != UTC.utcoffset(captured_at_utc):
        raise RestoreRollbackArtifactCaptureError("captured_at_utc must use UTC")
    if preflight.status is not RestoreAuthoritativeTargetPreflightStatus.READY:
        raise RestoreRollbackArtifactCaptureError("authoritative target preflight must be ready")
    if preflight.plan_id != plan.plan_id:
        raise RestoreRollbackArtifactCaptureError("preflight plan_id does not match restore plan")
    if preflight.authoritative_target_path != plan.authoritative_target_path:
        raise RestoreRollbackArtifactCaptureError(
            "preflight authoritative target does not match restore plan"
        )
    if preflight.rollback_plan.destination_path != plan.rollback_artifact_path:
        raise RestoreRollbackArtifactCaptureError(
            "preflight rollback destination does not match restore plan"
        )
    if preflight.rollback_plan.required:
        if preflight.rollback_plan.source_path != plan.authoritative_target_path:
            raise RestoreRollbackArtifactCaptureError(
                "preflight rollback source does not match authoritative target"
            )
    if preflight.staged_artifact_modified:
        raise RestoreRollbackArtifactCaptureError("preflight reports staged artifact modification")
    if preflight.authoritative_target_modified:
        raise RestoreRollbackArtifactCaptureError(
            "preflight reports authoritative target modification"
        )
    if preflight.rollback_artifact_created:
        raise RestoreRollbackArtifactCaptureError("preflight reports rollback artifact creation")


def _observe_source(
    path: Path,
    chunk_size: int,
) -> RestoreAuthoritativeTargetObservation:
    try:
        before = path.stat()
    except OSError as exc:
        raise RestoreRollbackArtifactCaptureError(
            f"authoritative source could not be inspected: {exc}"
        ) from exc
    if not stat.S_ISREG(before.st_mode):
        raise RestoreRollbackArtifactCaptureError("authoritative source is not a regular file")

    digest, size_bytes = _sha256(path, chunk_size)

    try:
        after = path.stat()
    except OSError as exc:
        raise RestoreRollbackArtifactCaptureError(
            f"authoritative source changed during inspection: {exc}"
        ) from exc
    if _stable_identity(before) != _stable_identity(after):
        raise RestoreRollbackArtifactCaptureError("authoritative source changed during inspection")
    if size_bytes != after.st_size:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source byte count changed during inspection"
        )

    return RestoreAuthoritativeTargetObservation(
        path=path,
        size_bytes=size_bytes,
        sha256=digest,
        mode=stat.S_IMODE(after.st_mode),
        owner_uid=after.st_uid,
        owner_gid=after.st_gid,
        modified_at_utc=datetime.fromtimestamp(after.st_mtime, tz=UTC),
    )


def _observe_rollback(
    path: Path,
    chunk_size: int,
) -> RestoreRollbackArtifactObservation:
    try:
        file_stat = path.stat()
    except OSError as exc:
        raise RestoreRollbackArtifactCaptureError(
            f"rollback artifact could not be inspected: {exc}"
        ) from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise RestoreRollbackArtifactCaptureError("rollback artifact is not a regular file")
    digest, size_bytes = _sha256(path, chunk_size)
    final_stat = path.stat()
    return RestoreRollbackArtifactObservation(
        path=path,
        size_bytes=size_bytes,
        sha256=digest,
        mode=stat.S_IMODE(final_stat.st_mode),
        modified_at_utc=datetime.fromtimestamp(final_stat.st_mtime, tz=UTC),
    )


def _copy_exclusively(
    source: Path,
    destination: Path,
    *,
    mode: int,
    chunk_size: int,
) -> tuple[int, str]:
    digest = hashlib.sha256()
    copied_bytes = 0
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor: int | None = None
    try:
        descriptor = os.open(destination, flags, mode)
        with source.open("rb") as source_handle:
            with os.fdopen(descriptor, "wb", closefd=True) as destination_handle:
                descriptor = None
                while chunk := source_handle.read(chunk_size):
                    destination_handle.write(chunk)
                    digest.update(chunk)
                    copied_bytes += len(chunk)
                destination_handle.flush()
                os.fsync(destination_handle.fileno())
        os.chmod(destination, mode)
        _fsync_directory(destination.parent)
    except FileExistsError as exc:
        raise RestoreRollbackArtifactCaptureError("rollback destination already exists") from exc
    except OSError as exc:
        raise RestoreRollbackArtifactCaptureError(
            f"rollback artifact capture failed: {exc}"
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    return copied_bytes, digest.hexdigest()


def _sha256(path: Path, chunk_size: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    size_bytes = 0
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(chunk_size):
                digest.update(chunk)
                size_bytes += len(chunk)
    except OSError as exc:
        raise RestoreRollbackArtifactCaptureError(f"file could not be read: {exc}") from exc
    return digest.hexdigest(), size_bytes


def _require_observation_match(
    expected: RestoreAuthoritativeTargetObservation,
    actual: RestoreAuthoritativeTargetObservation,
) -> None:
    if expected.path != actual.path:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source path does not match preflight"
        )
    if expected.size_bytes != actual.size_bytes:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source size changed after preflight"
        )
    if expected.sha256 != actual.sha256:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source SHA-256 changed after preflight"
        )
    if expected.mode != actual.mode:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source mode changed after preflight"
        )
    if expected.owner_uid != actual.owner_uid:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source owner changed after preflight"
        )
    if expected.owner_gid != actual.owner_gid:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source group changed after preflight"
        )
    if expected.modified_at_utc != actual.modified_at_utc:
        raise RestoreRollbackArtifactCaptureError(
            "authoritative source modification time changed after preflight"
        )


def _stable_identity(file_stat: os.stat_result) -> tuple[int, int, int, int]:
    return (
        file_stat.st_dev,
        file_stat.st_ino,
        file_stat.st_size,
        file_stat.st_mtime_ns,
    )


def _fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
