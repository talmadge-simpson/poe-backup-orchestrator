"""Read-only environmental preflight for governed restore workspaces."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from poe_backup_orchestrator.models.restore_plan import RestorePlan, RestorePlanReadiness
from poe_backup_orchestrator.models.restore_workspace import (
    RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightCheck,
    RestoreWorkspacePreflightReadiness,
    RestoreWorkspacePreflightReasonCode,
)


class RestoreWorkspacePreflightError(ValueError):
    """Raised when preflight inputs cannot be evaluated safely."""


class WorkspacePathProbe(Protocol):
    """Read-only filesystem observations required by workspace preflight."""

    def is_readable_file(self, path: Path) -> bool: ...

    def is_directory(self, path: Path) -> bool: ...

    def is_writable_searchable_directory(self, path: Path) -> bool: ...

    def exists(self, path: Path) -> bool: ...

    def nearest_existing_ancestor(self, path: Path) -> Path | None: ...


@dataclass(frozen=True, slots=True)
class LocalWorkspacePathProbe:
    """Local filesystem implementation that performs no mutation."""

    def is_readable_file(self, path: Path) -> bool:
        return path.is_file() and os.access(path, os.R_OK)

    def is_directory(self, path: Path) -> bool:
        return path.is_dir()

    def is_writable_searchable_directory(self, path: Path) -> bool:
        return path.is_dir() and os.access(path, os.W_OK | os.X_OK)

    def exists(self, path: Path) -> bool:
        return path.exists()

    def nearest_existing_ancestor(self, path: Path) -> Path | None:
        candidate = path
        while True:
            if candidate.exists():
                return candidate if candidate.is_dir() else candidate.parent
            parent = candidate.parent
            if parent == candidate:
                return None
            candidate = parent


@dataclass(frozen=True, slots=True)
class RestoreWorkspacePreflightService:
    """Inspect live workspace conditions without modifying the filesystem."""

    path_probe: WorkspacePathProbe

    def evaluate(
        self,
        plan: RestorePlan,
        *,
        evaluated_at_utc: datetime,
    ) -> RestoreWorkspacePreflight:
        _require_utc(evaluated_at_utc)

        checks: list[RestoreWorkspacePreflightCheck] = []

        def add(code: str, passed: bool, path: Path | None, detail: str) -> None:
            checks.append(
                RestoreWorkspacePreflightCheck(
                    ordinal=len(checks) + 1,
                    code=code,
                    passed=passed,
                    path=path,
                    detail=detail,
                )
            )

        plan_viable = plan.validation.readiness is not RestorePlanReadiness.BLOCKED
        add(
            "plan_not_blocked",
            plan_viable,
            None,
            "Restore plan is not blocked."
            if plan_viable
            else "Restore plan is blocked and cannot proceed to workspace preparation.",
        )

        artifact_ok = self.path_probe.is_readable_file(plan.source_artifact_path)
        add(
            "source_artifact_readable",
            artifact_ok,
            plan.source_artifact_path,
            "Source recovery artifact is a readable regular file."
            if artifact_ok
            else "Source recovery artifact is missing, unreadable, or not a regular file.",
        )

        manifest_ok = self.path_probe.is_readable_file(plan.source_manifest_path)
        add(
            "source_manifest_readable",
            manifest_ok,
            plan.source_manifest_path,
            "Source manifest is a readable regular file."
            if manifest_ok
            else "Source manifest is missing, unreadable, or not a regular file.",
        )

        target_parent = plan.authoritative_target_path.parent
        target_parent_ok = self.path_probe.is_writable_searchable_directory(target_parent)
        add(
            "target_parent_capable",
            target_parent_ok,
            target_parent,
            "Authoritative target parent is writable and searchable."
            if target_parent_ok
            else "Authoritative target parent is unavailable or lacks write/search access.",
        )

        target_exists = self.path_probe.exists(plan.authoritative_target_path)
        target_ok = (not target_exists) or self.path_probe.is_readable_file(
            plan.authoritative_target_path
        )
        add(
            "target_state_valid",
            target_ok,
            plan.authoritative_target_path,
            (
                "Authoritative target is absent or is a readable regular file."
                if target_ok
                else "Existing authoritative target is unreadable or not a regular file."
            ),
        )

        staging_clear = not self.path_probe.exists(plan.staging_target_path)
        add(
            "staging_target_clear",
            staging_clear,
            plan.staging_target_path,
            "Planned staging target does not exist."
            if staging_clear
            else "Planned staging target already exists.",
        )

        rollback_clear = not self.path_probe.exists(plan.rollback_artifact_path)
        add(
            "rollback_target_clear",
            rollback_clear,
            plan.rollback_artifact_path,
            "Planned rollback artifact does not exist."
            if rollback_clear
            else "Planned rollback artifact already exists.",
        )

        staging_ancestor = self.path_probe.nearest_existing_ancestor(
            plan.staging_target_path.parent
        )
        staging_ancestor_ok = (
            staging_ancestor is not None
            and self.path_probe.is_writable_searchable_directory(staging_ancestor)
        )
        add(
            "staging_ancestor_capable",
            staging_ancestor_ok,
            staging_ancestor or plan.staging_target_path.parent,
            "Nearest existing staging ancestor is writable and searchable."
            if staging_ancestor_ok
            else "No writable and searchable staging ancestor is available.",
        )

        rollback_ancestor = self.path_probe.nearest_existing_ancestor(
            plan.rollback_artifact_path.parent
        )
        rollback_ancestor_ok = (
            rollback_ancestor is not None
            and self.path_probe.is_writable_searchable_directory(rollback_ancestor)
        )
        add(
            "rollback_ancestor_capable",
            rollback_ancestor_ok,
            rollback_ancestor or plan.rollback_artifact_path.parent,
            "Nearest existing rollback ancestor is writable and searchable."
            if rollback_ancestor_ok
            else "No writable and searchable rollback ancestor is available.",
        )

        paths_distinct = (
            len(
                {
                    plan.authoritative_target_path,
                    plan.staging_target_path,
                    plan.rollback_artifact_path,
                }
            )
            == 3
        )
        add(
            "governed_paths_distinct",
            paths_distinct,
            None,
            "Authoritative, staging, and rollback paths are distinct."
            if paths_distinct
            else "Authoritative, staging, and rollback paths conflict.",
        )

        failed_codes = _reason_codes(
            plan_viable=plan_viable,
            artifact_ok=artifact_ok,
            manifest_ok=manifest_ok,
            target_parent_ok=target_parent_ok,
            target_ok=target_ok,
            staging_clear=staging_clear,
            rollback_clear=rollback_clear,
            staging_ancestor_ok=staging_ancestor_ok,
            rollback_ancestor_ok=rollback_ancestor_ok,
            paths_distinct=paths_distinct,
        )
        readiness = (
            RestoreWorkspacePreflightReadiness.READY
            if not failed_codes
            else RestoreWorkspacePreflightReadiness.BLOCKED
        )
        reason_codes = (
            (RestoreWorkspacePreflightReasonCode.PREFLIGHT_READY,)
            if not failed_codes
            else failed_codes
        )

        return RestoreWorkspacePreflight(
            schema_version=RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            evaluated_at_utc=evaluated_at_utc,
            readiness=readiness,
            reason_codes=reason_codes,
            checks=tuple(checks),
            warnings=(),
            mutation_performed=False,
        )


def preflight_restore_workspace(
    plan: RestorePlan,
    *,
    evaluated_at_utc: datetime,
    path_probe: WorkspacePathProbe | None = None,
) -> RestoreWorkspacePreflight:
    """Evaluate one restore plan against current workspace conditions."""

    return RestoreWorkspacePreflightService(
        path_probe=path_probe or LocalWorkspacePathProbe()
    ).evaluate(plan, evaluated_at_utc=evaluated_at_utc)


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RestoreWorkspacePreflightError("evaluated_at_utc must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise RestoreWorkspacePreflightError("evaluated_at_utc must use UTC")


def _reason_codes(
    *,
    plan_viable: bool,
    artifact_ok: bool,
    manifest_ok: bool,
    target_parent_ok: bool,
    target_ok: bool,
    staging_clear: bool,
    rollback_clear: bool,
    staging_ancestor_ok: bool,
    rollback_ancestor_ok: bool,
    paths_distinct: bool,
) -> tuple[RestoreWorkspacePreflightReasonCode, ...]:
    reasons: list[RestoreWorkspacePreflightReasonCode] = []
    if not plan_viable:
        reasons.append(RestoreWorkspacePreflightReasonCode.PLAN_BLOCKED)
    if not artifact_ok:
        reasons.append(RestoreWorkspacePreflightReasonCode.SOURCE_ARTIFACT_UNAVAILABLE)
    if not manifest_ok:
        reasons.append(RestoreWorkspacePreflightReasonCode.SOURCE_MANIFEST_UNAVAILABLE)
    if not target_parent_ok:
        reasons.append(RestoreWorkspacePreflightReasonCode.TARGET_PARENT_UNAVAILABLE)
    if not target_ok:
        reasons.append(RestoreWorkspacePreflightReasonCode.TARGET_INVALID)
    if not staging_clear:
        reasons.append(RestoreWorkspacePreflightReasonCode.STAGING_TARGET_CONFLICT)
    if not rollback_clear:
        reasons.append(RestoreWorkspacePreflightReasonCode.ROLLBACK_TARGET_CONFLICT)
    if not staging_ancestor_ok:
        reasons.append(RestoreWorkspacePreflightReasonCode.STAGING_ANCESTOR_UNAVAILABLE)
    if not rollback_ancestor_ok:
        reasons.append(RestoreWorkspacePreflightReasonCode.ROLLBACK_ANCESTOR_UNAVAILABLE)
    if not paths_distinct:
        reasons.append(RestoreWorkspacePreflightReasonCode.GOVERNED_PATH_CONFLICT)
    return tuple(reasons)
