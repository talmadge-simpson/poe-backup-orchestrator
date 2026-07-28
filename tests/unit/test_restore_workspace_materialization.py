"""Tests for governed restore-workspace directory materialization."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanValidation,
    RestoreWorkspaceMaterializationReasonCode,
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightCheck,
    RestoreWorkspacePreflightReadiness,
    RestoreWorkspacePreflightReasonCode,
)
from poe_backup_orchestrator.services.restore import (
    RestoreWorkspaceMaterializationError,
    materialize_restore_workspace,
)

NOW = datetime(2026, 7, 28, 16, 0, tzinfo=UTC)


def plan(tmp_path: Path) -> RestorePlan:
    target = tmp_path / "authoritative" / "POERegistry.db"
    staging = tmp_path / "restore-tests" / "Planning" / "Staging" / "plan-1" / "registry.sqlite3"
    rollback = tmp_path / "restore-tests" / "Planning" / "Rollback" / "plan-1" / "POERegistry.db"
    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-1",
        created_at_utc=NOW,
        recovery_point_id="rp-1",
        source_artifact_path=tmp_path / "repository" / "registry.sqlite3",
        source_manifest_path=tmp_path / "repository" / "manifest.json",
        authoritative_target_path=target,
        staging_target_path=staging,
        rollback_artifact_path=rollback,
        actions=(
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect target.",
                destination_path=target,
            ),
        ),
        validation=RestorePlanValidation(
            readiness=RestorePlanReadiness.READY,
            reason_codes=(RestorePlanReasonCode.PLAN_READY,),
            warnings=(),
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=NOW,
        ),
        execution_authorized=False,
    )


def ready_preflight(restore_plan: RestorePlan) -> RestoreWorkspacePreflight:
    return RestoreWorkspacePreflight(
        schema_version=RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
        plan_id=restore_plan.plan_id,
        evaluated_at_utc=NOW,
        readiness=RestoreWorkspacePreflightReadiness.READY,
        reason_codes=(RestoreWorkspacePreflightReasonCode.PREFLIGHT_READY,),
        checks=(
            RestoreWorkspacePreflightCheck(
                ordinal=1,
                code="ready",
                passed=True,
                path=None,
                detail="Ready.",
            ),
        ),
        warnings=(),
        mutation_performed=False,
    )


def test_materialization_creates_only_workspace_directories(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)

    result = materialize_restore_workspace(
        restore_plan,
        ready_preflight(restore_plan),
        materialized_at_utc=NOW,
    )

    assert restore_plan.staging_target_path.parent.is_dir()
    assert restore_plan.rollback_artifact_path.parent.is_dir()
    assert not restore_plan.staging_target_path.exists()
    assert not restore_plan.rollback_artifact_path.exists()
    assert result.artifact_copied is False
    assert result.reason_codes == (
        RestoreWorkspaceMaterializationReasonCode.WORKSPACE_MATERIALIZED,
    )
    assert len(result.created_directories) == 2


def test_repeated_materialization_reuses_existing_directories(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    preflight = ready_preflight(restore_plan)

    materialize_restore_workspace(
        restore_plan,
        preflight,
        materialized_at_utc=NOW,
    )
    repeated = materialize_restore_workspace(
        restore_plan,
        preflight,
        materialized_at_utc=NOW,
    )

    assert repeated.reason_codes == (RestoreWorkspaceMaterializationReasonCode.WORKSPACE_REUSED,)
    assert repeated.created_directories == ()
    assert repeated.reused_directories == (
        restore_plan.staging_target_path.parent,
        restore_plan.rollback_artifact_path.parent,
    )


def test_blocked_preflight_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    blocked = RestoreWorkspacePreflight(
        schema_version=RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
        plan_id=restore_plan.plan_id,
        evaluated_at_utc=NOW,
        readiness=RestoreWorkspacePreflightReadiness.BLOCKED,
        reason_codes=(RestoreWorkspacePreflightReasonCode.PLAN_BLOCKED,),
        checks=(
            RestoreWorkspacePreflightCheck(
                ordinal=1,
                code="blocked",
                passed=False,
                path=None,
                detail="Blocked.",
            ),
        ),
        warnings=(),
        mutation_performed=False,
    )

    with pytest.raises(
        RestoreWorkspaceMaterializationError,
        match="preflight must be ready",
    ):
        materialize_restore_workspace(
            restore_plan,
            blocked,
            materialized_at_utc=NOW,
        )


def test_mismatched_plan_id_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    preflight = ready_preflight(restore_plan)
    mismatched = RestoreWorkspacePreflight(
        schema_version=preflight.schema_version,
        plan_id="another-plan",
        evaluated_at_utc=preflight.evaluated_at_utc,
        readiness=preflight.readiness,
        reason_codes=preflight.reason_codes,
        checks=preflight.checks,
        warnings=preflight.warnings,
        mutation_performed=False,
    )

    with pytest.raises(
        RestoreWorkspaceMaterializationError,
        match="plan_id does not match",
    ):
        materialize_restore_workspace(
            restore_plan,
            mismatched,
            materialized_at_utc=NOW,
        )


def test_existing_artifact_path_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    restore_plan.staging_target_path.parent.mkdir(parents=True)
    restore_plan.staging_target_path.write_bytes(b"existing")

    with pytest.raises(
        RestoreWorkspaceMaterializationError,
        match="staging artifact path already exists",
    ):
        materialize_restore_workspace(
            restore_plan,
            ready_preflight(restore_plan),
            materialized_at_utc=NOW,
        )


def test_non_utc_timestamp_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    non_utc = NOW.astimezone(timezone(timedelta(hours=-4)))

    with pytest.raises(
        RestoreWorkspaceMaterializationError,
        match="must use UTC",
    ):
        materialize_restore_workspace(
            restore_plan,
            ready_preflight(restore_plan),
            materialized_at_utc=non_utc,
        )


class FailingFilesystem:
    """Test double that fails while creating the rollback directory."""

    def __init__(self) -> None:
        self.existing: set[Path] = set()
        self.removed: list[Path] = []

    def exists(self, path: Path) -> bool:
        return path in self.existing

    def is_directory(self, path: Path) -> bool:
        return path in self.existing

    def create_directory(self, path: Path) -> tuple[Path, ...]:
        if "Rollback" in path.parts:
            raise OSError("simulated rollback-directory failure")
        self.existing.add(path)
        return (path,)

    def remove_directory_if_empty(self, path: Path) -> None:
        self.existing.remove(path)
        self.removed.append(path)


def test_partial_materialization_is_cleaned_up(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    filesystem = FailingFilesystem()

    with pytest.raises(
        RestoreWorkspaceMaterializationError,
        match="simulated rollback-directory failure",
    ):
        materialize_restore_workspace(
            restore_plan,
            ready_preflight(restore_plan),
            materialized_at_utc=NOW,
            filesystem=filesystem,
        )

    assert restore_plan.staging_target_path.parent in filesystem.removed
    assert filesystem.existing == set()


def test_materialization_contract_is_exported() -> None:
    from poe_backup_orchestrator.services import restore

    assert restore.materialize_restore_workspace is materialize_restore_workspace
