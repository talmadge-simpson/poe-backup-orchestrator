"""Immutable domain models for governed restore planning."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_PLAN_SCHEMA_VERSION = "1.0"
RESTORE_PLAN_POLICY_VERSION = "5B.1"


class RestorePlanReadiness(StrEnum):
    """Governed readiness classification for a restore plan."""

    UNKNOWN = "unknown"
    READY = "ready"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"


class RestoreActionType(StrEnum):
    """Controlled vocabulary for actions a restore plan may describe."""

    INSPECT_TARGET = "inspect_target"
    STAGE_RECOVERY_ARTIFACT = "stage_recovery_artifact"
    VERIFY_STAGED_CHECKSUM = "verify_staged_checksum"
    VERIFY_STAGED_SQLITE_INTEGRITY = "verify_staged_sqlite_integrity"
    CREATE_ROLLBACK_ARTIFACT = "create_rollback_artifact"
    VERIFY_ROLLBACK_ARTIFACT = "verify_rollback_artifact"
    AWAIT_APPROVAL = "await_approval"
    PROMOTE_STAGED_ARTIFACT = "promote_staged_artifact"
    VERIFY_AUTHORITATIVE_TARGET = "verify_authoritative_target"
    PUBLISH_RESTORE_EVIDENCE = "publish_restore_evidence"


class RestorePlanReasonCode(StrEnum):
    """Stable reason codes emitted by future planning validation."""

    VALIDATION_NOT_PERFORMED = "validation_not_performed"
    PLAN_READY = "plan_ready"
    ELIGIBILITY_OVERRIDE_REQUIRED = "eligibility_override_required"
    TARGET_STATE_CONFLICT = "target_state_conflict"
    STAGING_STATE_CONFLICT = "staging_state_conflict"
    ROLLBACK_STATE_CONFLICT = "rollback_state_conflict"
    INSUFFICIENT_CAPACITY = "insufficient_capacity"
    RUNTIME_NOT_IDLE = "runtime_not_idle"
    REPOSITORY_NOT_HEALTHY = "repository_not_healthy"


def _require_text(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must use UTC")


@dataclass(frozen=True, slots=True)
class RestorePlanRequest:
    """Operator intent supplied to a future restore planning service."""

    recovery_point_id: str
    authoritative_target_path: Path
    staging_root: Path
    rollback_root: Path
    eligibility_override_requested: bool = False
    operator_rationale: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.recovery_point_id, "recovery_point_id")
        if self.eligibility_override_requested:
            if self.operator_rationale is None:
                raise ValueError(
                    "operator_rationale is required when eligibility override is requested"
                )
            _require_text(self.operator_rationale, "operator_rationale")


@dataclass(frozen=True, slots=True)
class RestoreAction:
    """One ordered future operation described by a restore plan."""

    ordinal: int
    action_type: RestoreActionType
    description: str
    source_path: Path | None = None
    destination_path: Path | None = None
    mutates_state: bool = False
    approval_required: bool = False

    def __post_init__(self) -> None:
        if self.ordinal < 1:
            raise ValueError("ordinal must be positive")
        _require_text(self.description, "description")


@dataclass(frozen=True, slots=True)
class RestoreWarning:
    """Non-blocking planning condition visible to the operator."""

    code: str
    message: str

    def __post_init__(self) -> None:
        _require_text(self.code, "code")
        _require_text(self.message, "message")


@dataclass(frozen=True, slots=True)
class RestoreConflict:
    """Condition that blocks or gates later restore execution."""

    code: str
    message: str
    blocking: bool = True
    approval_can_resolve: bool = False

    def __post_init__(self) -> None:
        _require_text(self.code, "code")
        _require_text(self.message, "message")
        if self.blocking and self.approval_can_resolve:
            raise ValueError("a blocking conflict cannot be approval-resolvable")


@dataclass(frozen=True, slots=True)
class RestorePlanValidation:
    """Governed readiness result attached to a restore plan."""

    readiness: RestorePlanReadiness
    reason_codes: tuple[RestorePlanReasonCode, ...]
    warnings: tuple[RestoreWarning, ...]
    conflicts: tuple[RestoreConflict, ...]
    approval_required: bool
    evaluated_at_utc: datetime
    policy_version: str = RESTORE_PLAN_POLICY_VERSION

    def __post_init__(self) -> None:
        _require_utc(self.evaluated_at_utc, "evaluated_at_utc")
        _require_text(self.policy_version, "policy_version")

        warning_codes = tuple(warning.code for warning in self.warnings)
        if len(set(warning_codes)) != len(warning_codes):
            raise ValueError("warning codes must be unique")

        conflict_codes = tuple(conflict.code for conflict in self.conflicts)
        if len(set(conflict_codes)) != len(conflict_codes):
            raise ValueError("conflict codes must be unique")

        has_blocking = any(conflict.blocking for conflict in self.conflicts)
        if self.readiness is RestorePlanReadiness.READY:
            if has_blocking:
                raise ValueError("a ready plan cannot contain blocking conflicts")
            if self.approval_required:
                raise ValueError("a ready plan cannot require approval")
        if self.readiness is RestorePlanReadiness.BLOCKED and not has_blocking:
            raise ValueError("a blocked plan requires a blocking conflict")
        if self.readiness is RestorePlanReadiness.APPROVAL_REQUIRED and not self.approval_required:
            raise ValueError("approval_required readiness must require approval")


@dataclass(frozen=True, slots=True)
class RestorePlan:
    """Complete immutable description of a proposed restore."""

    schema_version: str
    policy_version: str
    plan_id: str
    created_at_utc: datetime
    recovery_point_id: str
    source_artifact_path: Path
    source_manifest_path: Path
    authoritative_target_path: Path
    staging_target_path: Path
    rollback_artifact_path: Path
    actions: tuple[RestoreAction, ...]
    validation: RestorePlanValidation
    execution_authorized: bool = False

    def __post_init__(self) -> None:
        _require_text(self.schema_version, "schema_version")
        _require_text(self.policy_version, "policy_version")
        _require_text(self.plan_id, "plan_id")
        _require_text(self.recovery_point_id, "recovery_point_id")
        _require_utc(self.created_at_utc, "created_at_utc")

        if self.execution_authorized:
            raise ValueError("Slice 5B-1 plans cannot authorize execution")

        governed_paths = {
            self.authoritative_target_path,
            self.staging_target_path,
            self.rollback_artifact_path,
        }
        if len(governed_paths) != 3:
            raise ValueError("authoritative, staging, and rollback paths must be distinct")

        ordinals = tuple(action.ordinal for action in self.actions)
        expected = tuple(range(1, len(self.actions) + 1))
        if ordinals != expected:
            raise ValueError("action ordinals must be unique and contiguous beginning at one")
