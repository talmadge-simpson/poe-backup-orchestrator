"""Immutable evidence for governed restore artifact staging."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_ARTIFACT_STAGING_SCHEMA_VERSION = "1.0"


class RestoreArtifactStagingStatus(StrEnum):
    """Outcome of governed artifact staging."""

    STAGED = "staged"


class RestoreArtifactStagingReasonCode(StrEnum):
    """Stable reason codes emitted by successful staging."""

    ARTIFACT_STAGED = "artifact_staged"


@dataclass(frozen=True, slots=True)
class RestoreArtifactStaging:
    """Complete evidence for one successful staging operation."""

    schema_version: str
    plan_id: str
    staged_at_utc: datetime
    status: RestoreArtifactStagingStatus
    reason_codes: tuple[RestoreArtifactStagingReasonCode, ...]
    source_path: Path
    staged_path: Path
    source_size_bytes: int
    staged_size_bytes: int
    authoritative_target_modified: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version or not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id or not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.staged_at_utc.tzinfo is None or self.staged_at_utc.utcoffset() is None:
            raise ValueError("staged_at_utc must be timezone-aware")
        if self.staged_at_utc.utcoffset() != UTC.utcoffset(self.staged_at_utc):
            raise ValueError("staged_at_utc must use UTC")
        if self.source_size_bytes < 0 or self.staged_size_bytes < 0:
            raise ValueError("artifact sizes must not be negative")
        if self.source_size_bytes != self.staged_size_bytes:
            raise ValueError("source and staged sizes must match")
        if self.source_path == self.staged_path:
            raise ValueError("source and staged paths must be distinct")
        if self.authoritative_target_modified:
            raise ValueError("Slice 5C-1 cannot modify the authoritative target")
