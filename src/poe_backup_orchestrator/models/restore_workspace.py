"""Immutable models for governed restore-workspace preflight."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION = "1.0"


class RestoreWorkspacePreflightReadiness(StrEnum):
    """Overall environmental readiness for future workspace materialization."""

    READY = "ready"
    BLOCKED = "blocked"


class RestoreWorkspacePreflightReasonCode(StrEnum):
    """Stable reason codes emitted by workspace preflight."""

    PREFLIGHT_READY = "preflight_ready"
    PLAN_BLOCKED = "plan_blocked"
    SOURCE_ARTIFACT_UNAVAILABLE = "source_artifact_unavailable"
    SOURCE_MANIFEST_UNAVAILABLE = "source_manifest_unavailable"
    TARGET_PARENT_UNAVAILABLE = "target_parent_unavailable"
    TARGET_INVALID = "target_invalid"
    STAGING_TARGET_CONFLICT = "staging_target_conflict"
    ROLLBACK_TARGET_CONFLICT = "rollback_target_conflict"
    STAGING_ANCESTOR_UNAVAILABLE = "staging_ancestor_unavailable"
    ROLLBACK_ANCESTOR_UNAVAILABLE = "rollback_ancestor_unavailable"
    GOVERNED_PATH_CONFLICT = "governed_path_conflict"


@dataclass(frozen=True, slots=True)
class RestoreWorkspacePreflightCheck:
    """One ordered environmental assertion."""

    ordinal: int
    code: str
    passed: bool
    path: Path | None
    detail: str

    def __post_init__(self) -> None:
        if self.ordinal < 1:
            raise ValueError("ordinal must be positive")
        if not self.code or not self.code.strip():
            raise ValueError("code must not be empty")
        if not self.detail or not self.detail.strip():
            raise ValueError("detail must not be empty")


@dataclass(frozen=True, slots=True)
class RestoreWorkspacePreflight:
    """Complete read-only workspace-preflight evidence."""

    schema_version: str
    plan_id: str
    evaluated_at_utc: datetime
    readiness: RestoreWorkspacePreflightReadiness
    reason_codes: tuple[RestoreWorkspacePreflightReasonCode, ...]
    checks: tuple[RestoreWorkspacePreflightCheck, ...]
    warnings: tuple[str, ...]
    mutation_performed: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version or not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id or not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.evaluated_at_utc.tzinfo is None or self.evaluated_at_utc.utcoffset() is None:
            raise ValueError("evaluated_at_utc must be timezone-aware")
        if self.evaluated_at_utc.utcoffset() != UTC.utcoffset(self.evaluated_at_utc):
            raise ValueError("evaluated_at_utc must use UTC")
        ordinals = tuple(check.ordinal for check in self.checks)
        if ordinals != tuple(range(1, len(self.checks) + 1)):
            raise ValueError("check ordinals must be contiguous beginning at one")
        if self.mutation_performed:
            raise ValueError("Slice 5B-4 preflight cannot report filesystem mutation")
        has_failure = any(not check.passed for check in self.checks)
        if self.readiness is RestoreWorkspacePreflightReadiness.READY and has_failure:
            raise ValueError("ready preflight cannot contain failed checks")
        if self.readiness is RestoreWorkspacePreflightReadiness.BLOCKED and not has_failure:
            raise ValueError("blocked preflight requires at least one failed check")
