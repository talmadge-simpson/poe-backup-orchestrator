"""Immutable evidence for governed restore-workspace materialization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION = "1.0"


class RestoreWorkspaceMaterializationStatus(StrEnum):
    """Outcome of workspace directory materialization."""

    MATERIALIZED = "materialized"


class RestoreWorkspaceMaterializationReasonCode(StrEnum):
    """Stable reason codes emitted by successful materialization."""

    WORKSPACE_MATERIALIZED = "workspace_materialized"
    WORKSPACE_REUSED = "workspace_reused"


@dataclass(frozen=True, slots=True)
class RestoreWorkspaceDirectoryRecord:
    """One ordered directory materialization result."""

    ordinal: int
    purpose: str
    path: Path
    created: bool

    def __post_init__(self) -> None:
        if self.ordinal < 1:
            raise ValueError("ordinal must be positive")
        if not self.purpose or not self.purpose.strip():
            raise ValueError("purpose must not be empty")


@dataclass(frozen=True, slots=True)
class RestoreWorkspaceMaterialization:
    """Complete evidence for one successful directory materialization."""

    schema_version: str
    plan_id: str
    materialized_at_utc: datetime
    status: RestoreWorkspaceMaterializationStatus
    reason_codes: tuple[RestoreWorkspaceMaterializationReasonCode, ...]
    directories: tuple[RestoreWorkspaceDirectoryRecord, ...]
    artifact_copied: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version or not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id or not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.materialized_at_utc.tzinfo is None or self.materialized_at_utc.utcoffset() is None:
            raise ValueError("materialized_at_utc must be timezone-aware")
        if self.materialized_at_utc.utcoffset() != UTC.utcoffset(self.materialized_at_utc):
            raise ValueError("materialized_at_utc must use UTC")
        ordinals = tuple(record.ordinal for record in self.directories)
        if ordinals != tuple(range(1, len(self.directories) + 1)):
            raise ValueError("directory ordinals must be contiguous beginning at one")
        paths = tuple(record.path for record in self.directories)
        if len(paths) != len(set(paths)):
            raise ValueError("directory records must use distinct paths")
        if self.artifact_copied:
            raise ValueError("Slice 5B-5 cannot report artifact copying")

    @property
    def created_directories(self) -> tuple[Path, ...]:
        """Return directories created by this invocation."""

        return tuple(record.path for record in self.directories if record.created)

    @property
    def reused_directories(self) -> tuple[Path, ...]:
        """Return required directories that already existed."""

        return tuple(record.path for record in self.directories if not record.created)
