"""Domain contracts for rollback artifact capture and validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from poe_backup_orchestrator.models.restore_authoritative_target_preflight import (
    RestoreAuthoritativeTargetObservation,
)

RESTORE_ROLLBACK_ARTIFACT_CAPTURE_SCHEMA_VERSION = "1.0"


class RestoreRollbackArtifactCaptureStatus(StrEnum):
    """Rollback capture outcome."""

    NOT_REQUIRED = "not_required"
    CAPTURED = "captured"


class RestoreRollbackArtifactCaptureReasonCode(StrEnum):
    """Stable rollback capture reason codes."""

    PREFLIGHT_ACCEPTED = "preflight_accepted"
    ROLLBACK_NOT_REQUIRED = "rollback_not_required"
    SOURCE_MATCHED_PREFLIGHT = "source_matched_preflight"
    DESTINATION_CREATED_EXCLUSIVELY = "destination_created_exclusively"
    ROLLBACK_BYTES_COPIED = "rollback_bytes_copied"
    ROLLBACK_BYTES_SYNCHRONIZED = "rollback_bytes_synchronized"
    ROLLBACK_MODE_PRESERVED = "rollback_mode_preserved"
    BYTE_COUNT_MATCHED = "byte_count_matched"
    SHA256_MATCHED = "sha256_matched"
    SOURCE_REMAINED_STABLE = "source_remained_stable"
    ROLLBACK_CAPTURE_COMPLETE = "rollback_capture_complete"


@dataclass(frozen=True, slots=True)
class RestoreRollbackArtifactObservation:
    """Immutable observation of the captured rollback artifact."""

    path: Path
    size_bytes: int
    sha256: str
    mode: int
    modified_at_utc: datetime

    def __post_init__(self) -> None:
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        if len(self.sha256) != 64:
            raise ValueError("sha256 must contain 64 hexadecimal characters")
        try:
            int(self.sha256, 16)
        except ValueError as exc:
            raise ValueError("sha256 must be hexadecimal") from exc
        if self.modified_at_utc.tzinfo is None or self.modified_at_utc.utcoffset() is None:
            raise ValueError("modified_at_utc must be timezone-aware")
        if self.modified_at_utc.utcoffset() != UTC.utcoffset(self.modified_at_utc):
            raise ValueError("modified_at_utc must use UTC")


@dataclass(frozen=True, slots=True)
class RestoreRollbackArtifactCapture:
    """Immutable rollback artifact capture evidence."""

    schema_version: str
    plan_id: str
    captured_at_utc: datetime
    status: RestoreRollbackArtifactCaptureStatus
    reason_codes: tuple[RestoreRollbackArtifactCaptureReasonCode, ...]
    capture_required: bool
    source_path: Path | None
    destination_path: Path
    source_observation: RestoreAuthoritativeTargetObservation | None
    rollback_observation: RestoreRollbackArtifactObservation | None
    copied_bytes: int
    checksum_matched: bool
    source_remained_stable: bool
    mode_preserved: bool
    staged_artifact_modified: bool = False
    authoritative_target_modified: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.captured_at_utc.tzinfo is None or self.captured_at_utc.utcoffset() is None:
            raise ValueError("captured_at_utc must be timezone-aware")
        if self.captured_at_utc.utcoffset() != UTC.utcoffset(self.captured_at_utc):
            raise ValueError("captured_at_utc must use UTC")
        if self.copied_bytes < 0:
            raise ValueError("copied_bytes must not be negative")
        if self.capture_required:
            if self.status is not RestoreRollbackArtifactCaptureStatus.CAPTURED:
                raise ValueError("required capture must have captured status")
            if self.source_path is None:
                raise ValueError("required capture must identify source path")
            if self.source_observation is None:
                raise ValueError("required capture must include source observation")
            if self.rollback_observation is None:
                raise ValueError("required capture must include rollback observation")
            if not self.checksum_matched:
                raise ValueError("required capture must match checksum")
            if not self.source_remained_stable:
                raise ValueError("required capture requires stable source")
            if not self.mode_preserved:
                raise ValueError("required capture must preserve mode")
        else:
            if self.status is not RestoreRollbackArtifactCaptureStatus.NOT_REQUIRED:
                raise ValueError("unrequired capture must have not_required status")
            if self.source_path is not None:
                raise ValueError("unrequired capture must not identify source")
            if self.source_observation is not None:
                raise ValueError("unrequired capture must not include source observation")
            if self.rollback_observation is not None:
                raise ValueError("unrequired capture must not include rollback observation")
            if self.copied_bytes != 0:
                raise ValueError("unrequired capture must copy zero bytes")
        if self.staged_artifact_modified:
            raise ValueError("rollback capture cannot modify staged artifact")
        if self.authoritative_target_modified:
            raise ValueError("rollback capture cannot modify authoritative target")
