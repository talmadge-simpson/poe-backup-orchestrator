"""Domain contracts for authoritative target preflight and rollback planning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION = "1.0"


class RestoreAuthoritativeTargetState(StrEnum):
    """Observed authoritative target state."""

    ABSENT = "absent"
    REGULAR_FILE = "regular_file"


class RestoreAuthoritativeTargetPreflightStatus(StrEnum):
    """Successful preflight outcome."""

    READY = "ready"


class RestoreAuthoritativeTargetPreflightReasonCode(StrEnum):
    """Stable successful preflight reason codes."""

    APPLICATION_VALIDATION_ACCEPTED = "application_validation_accepted"
    AUTHORITATIVE_TARGET_ABSENT = "authoritative_target_absent"
    AUTHORITATIVE_TARGET_REGULAR_FILE = "authoritative_target_regular_file"
    AUTHORITATIVE_TARGET_READABLE = "authoritative_target_readable"
    ROLLBACK_NOT_REQUIRED = "rollback_not_required"
    ROLLBACK_REQUIRED = "rollback_required"
    ROLLBACK_DESTINATION_AVAILABLE = "rollback_destination_available"
    ROLLBACK_PARENT_READY = "rollback_parent_ready"
    PREFLIGHT_READY = "preflight_ready"


@dataclass(frozen=True, slots=True)
class RestoreAuthoritativeTargetObservation:
    """Immutable observations for a readable authoritative file."""

    path: Path
    size_bytes: int
    sha256: str
    mode: int
    owner_uid: int
    owner_gid: int
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
class RestoreRollbackPlan:
    """Deterministic rollback obligation for later execution."""

    required: bool
    source_path: Path | None
    destination_path: Path
    destination_parent_ready: bool
    destination_available: bool

    def __post_init__(self) -> None:
        if self.required and self.source_path is None:
            raise ValueError("required rollback must identify a source path")
        if not self.required and self.source_path is not None:
            raise ValueError("unrequired rollback must not identify a source")
        if not self.destination_parent_ready:
            raise ValueError("rollback destination parent must be ready")
        if not self.destination_available:
            raise ValueError("rollback destination must be available")


@dataclass(frozen=True, slots=True)
class RestoreAuthoritativeTargetPreflight:
    """Immutable successful authoritative-target preflight evidence."""

    schema_version: str
    plan_id: str
    preflight_at_utc: datetime
    status: RestoreAuthoritativeTargetPreflightStatus
    reason_codes: tuple[RestoreAuthoritativeTargetPreflightReasonCode, ...]
    authoritative_target_path: Path
    target_state: RestoreAuthoritativeTargetState
    target_observation: RestoreAuthoritativeTargetObservation | None
    rollback_plan: RestoreRollbackPlan
    staged_artifact_modified: bool = False
    authoritative_target_modified: bool = False
    rollback_artifact_created: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.preflight_at_utc.tzinfo is None or self.preflight_at_utc.utcoffset() is None:
            raise ValueError("preflight_at_utc must be timezone-aware")
        if self.preflight_at_utc.utcoffset() != UTC.utcoffset(self.preflight_at_utc):
            raise ValueError("preflight_at_utc must use UTC")
        if (
            self.target_state is RestoreAuthoritativeTargetState.ABSENT
            and self.target_observation is not None
        ):
            raise ValueError("absent target cannot have a file observation")
        if (
            self.target_state is RestoreAuthoritativeTargetState.REGULAR_FILE
            and self.target_observation is None
        ):
            raise ValueError("regular target requires a file observation")
        if self.staged_artifact_modified:
            raise ValueError("preflight cannot modify staged artifact")
        if self.authoritative_target_modified:
            raise ValueError("preflight cannot modify authoritative target")
        if self.rollback_artifact_created:
            raise ValueError("preflight cannot create rollback artifact")
