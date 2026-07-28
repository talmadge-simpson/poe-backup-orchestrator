"""Tests for read-only governed restore-workspace preflight."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanValidation,
    RestoreWorkspacePreflightReadiness,
    RestoreWorkspacePreflightReasonCode,
)
from poe_backup_orchestrator.services.restore import (
    RestoreWorkspacePreflightError,
    preflight_restore_workspace,
)

NOW = datetime(2026, 7, 28, 15, 0, tzinfo=UTC)


def plan(tmp_path: Path, *, blocked: bool = False) -> RestorePlan:
    source = tmp_path / "repository" / "registry.sqlite3"
    manifest = tmp_path / "repository" / "manifest.json"
    target = tmp_path / "authoritative" / "POERegistry.db"
    staging = tmp_path / "restore-tests" / "Planning" / "Staging" / "plan-1" / "registry.sqlite3"
    rollback = tmp_path / "restore-tests" / "Planning" / "Rollback" / "plan-1" / "POERegistry.db"

    source.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    (tmp_path / "restore-tests").mkdir()
    source.write_bytes(b"registry")
    manifest.write_text("{}", encoding="utf-8")

    if blocked:
        readiness = RestorePlanReadiness.BLOCKED
        validation = RestorePlanValidation(
            readiness=readiness,
            reason_codes=(RestorePlanReasonCode.TARGET_STATE_CONFLICT,),
            warnings=(),
            conflicts=(
                __import__(
                    "poe_backup_orchestrator.models",
                    fromlist=["RestoreConflict"],
                ).RestoreConflict("blocked", "Blocked plan."),
            ),
            approval_required=False,
            evaluated_at_utc=NOW,
        )
        actions = (
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect target.",
                destination_path=target,
            ),
        )
    else:
        validation = RestorePlanValidation(
            readiness=RestorePlanReadiness.READY,
            reason_codes=(RestorePlanReasonCode.PLAN_READY,),
            warnings=(),
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=NOW,
        )
        actions = (
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect target.",
                destination_path=target,
            ),
        )

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-1",
        created_at_utc=NOW,
        recovery_point_id="rp-1",
        source_artifact_path=source,
        source_manifest_path=manifest,
        authoritative_target_path=target,
        staging_target_path=staging,
        rollback_artifact_path=rollback,
        actions=actions,
        validation=validation,
        execution_authorized=False,
    )


def test_preflight_ready_when_all_environmental_checks_pass(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)

    result = preflight_restore_workspace(
        restore_plan,
        evaluated_at_utc=NOW,
    )

    assert result.readiness is RestoreWorkspacePreflightReadiness.READY
    assert result.reason_codes == (RestoreWorkspacePreflightReasonCode.PREFLIGHT_READY,)
    assert all(check.passed for check in result.checks)
    assert tuple(check.ordinal for check in result.checks) == tuple(range(1, 11))
    assert result.mutation_performed is False
    assert not restore_plan.staging_target_path.exists()
    assert not restore_plan.rollback_artifact_path.exists()


def test_missing_source_artifact_blocks_preflight(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    restore_plan.source_artifact_path.unlink()

    result = preflight_restore_workspace(
        restore_plan,
        evaluated_at_utc=NOW,
    )

    assert result.readiness is RestoreWorkspacePreflightReadiness.BLOCKED
    assert RestoreWorkspacePreflightReasonCode.SOURCE_ARTIFACT_UNAVAILABLE in result.reason_codes


def test_existing_staging_and_rollback_targets_are_conflicts(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    restore_plan.staging_target_path.parent.mkdir(parents=True)
    restore_plan.rollback_artifact_path.parent.mkdir(parents=True)
    restore_plan.staging_target_path.write_bytes(b"existing")
    restore_plan.rollback_artifact_path.write_bytes(b"existing")

    result = preflight_restore_workspace(
        restore_plan,
        evaluated_at_utc=NOW,
    )

    assert result.readiness is RestoreWorkspacePreflightReadiness.BLOCKED
    assert RestoreWorkspacePreflightReasonCode.STAGING_TARGET_CONFLICT in result.reason_codes
    assert RestoreWorkspacePreflightReasonCode.ROLLBACK_TARGET_CONFLICT in result.reason_codes


def test_blocked_restore_plan_remains_blocked(tmp_path: Path) -> None:
    result = preflight_restore_workspace(
        plan(tmp_path, blocked=True),
        evaluated_at_utc=NOW,
    )

    assert result.readiness is RestoreWorkspacePreflightReadiness.BLOCKED
    assert RestoreWorkspacePreflightReasonCode.PLAN_BLOCKED in result.reason_codes


def test_preflight_is_deterministic_for_unchanged_environment(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)

    first = preflight_restore_workspace(restore_plan, evaluated_at_utc=NOW)
    second = preflight_restore_workspace(restore_plan, evaluated_at_utc=NOW)

    assert first == second


def test_non_utc_timestamp_is_rejected(tmp_path: Path) -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=-4)))

    with pytest.raises(RestoreWorkspacePreflightError, match="must use UTC"):
        preflight_restore_workspace(
            plan(tmp_path),
            evaluated_at_utc=non_utc,
        )


def test_service_contract_is_exported() -> None:
    from poe_backup_orchestrator.services import restore

    assert restore.preflight_restore_workspace is preflight_restore_workspace
