"""Tests for the Slice 5B-1 restore plan domain contract."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestoreConflict,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanRequest,
    RestorePlanValidation,
    RestoreWarning,
)

TIMESTAMP = datetime(2026, 7, 28, 14, 0, tzinfo=UTC)


def validation(
    *,
    readiness: RestorePlanReadiness = RestorePlanReadiness.READY,
    conflicts: tuple[RestoreConflict, ...] = (),
    approval_required: bool = False,
) -> RestorePlanValidation:
    return RestorePlanValidation(
        readiness=readiness,
        reason_codes=(RestorePlanReasonCode.PLAN_READY,),
        warnings=(),
        conflicts=conflicts,
        approval_required=approval_required,
        evaluated_at_utc=TIMESTAMP,
    )


def actions() -> tuple[RestoreAction, ...]:
    return (
        RestoreAction(
            ordinal=1,
            action_type=RestoreActionType.INSPECT_TARGET,
            description="Inspect authoritative Registry target.",
        ),
        RestoreAction(
            ordinal=2,
            action_type=RestoreActionType.STAGE_RECOVERY_ARTIFACT,
            description="Stage the selected recovery artifact.",
            source_path=Path("/repository/recovery.sqlite3"),
            destination_path=Path("/staging/recovery.sqlite3"),
            mutates_state=True,
        ),
    )


def plan(**overrides) -> RestorePlan:
    values = {
        "schema_version": RESTORE_PLAN_SCHEMA_VERSION,
        "policy_version": RESTORE_PLAN_POLICY_VERSION,
        "plan_id": "restore-plan-20260728T140000Z",
        "created_at_utc": TIMESTAMP,
        "recovery_point_id": "20260726T180757Z",
        "source_artifact_path": Path("/repository/recovery.sqlite3"),
        "source_manifest_path": Path("/repository/manifest.json"),
        "authoritative_target_path": Path("/srv/poe/registry.sqlite3"),
        "staging_target_path": Path("/restore-tests/staging/registry.sqlite3"),
        "rollback_artifact_path": Path("/restore-tests/rollback/registry.sqlite3"),
        "actions": actions(),
        "validation": validation(),
    }
    values.update(overrides)
    return RestorePlan(**values)


def test_restore_plan_request_captures_planning_only_intent() -> None:
    request = RestorePlanRequest(
        recovery_point_id="20260726T180757Z",
        authoritative_target_path=Path("/srv/poe/registry.sqlite3"),
        staging_root=Path("/restore-tests/staging"),
        rollback_root=Path("/restore-tests/rollback"),
    )
    assert request.eligibility_override_requested is False
    assert request.operator_rationale is None


def test_override_request_requires_operator_rationale() -> None:
    with pytest.raises(ValueError, match="operator_rationale is required"):
        RestorePlanRequest(
            recovery_point_id="20260726T180757Z",
            authoritative_target_path=Path("/srv/poe/registry.sqlite3"),
            staging_root=Path("/restore-tests/staging"),
            rollback_root=Path("/restore-tests/rollback"),
            eligibility_override_requested=True,
        )


def test_restore_action_requires_positive_ordinal() -> None:
    with pytest.raises(ValueError, match="ordinal must be positive"):
        RestoreAction(
            ordinal=0,
            action_type=RestoreActionType.INSPECT_TARGET,
            description="Inspect target.",
        )


def test_ready_validation_rejects_blocking_conflict() -> None:
    conflict = RestoreConflict(code="target_busy", message="Target is busy.")
    with pytest.raises(ValueError, match="ready plan cannot contain"):
        validation(conflicts=(conflict,))


def test_blocked_validation_requires_blocking_conflict() -> None:
    with pytest.raises(ValueError, match="blocked plan requires"):
        validation(readiness=RestorePlanReadiness.BLOCKED)


def test_approval_required_classification_requires_flag() -> None:
    with pytest.raises(ValueError, match="must require approval"):
        validation(readiness=RestorePlanReadiness.APPROVAL_REQUIRED)


def test_validation_rejects_duplicate_warning_codes() -> None:
    warning = RestoreWarning(code="legacy_manifest", message="Legacy manifest.")
    with pytest.raises(ValueError, match="warning codes must be unique"):
        RestorePlanValidation(
            readiness=RestorePlanReadiness.UNKNOWN,
            reason_codes=(RestorePlanReasonCode.VALIDATION_NOT_PERFORMED,),
            warnings=(warning, warning),
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=TIMESTAMP,
        )


def test_validation_requires_utc_timestamp() -> None:
    non_utc = TIMESTAMP.astimezone(timezone(timedelta(hours=-4)))
    with pytest.raises(ValueError, match="must use UTC"):
        RestorePlanValidation(
            readiness=RestorePlanReadiness.UNKNOWN,
            reason_codes=(RestorePlanReasonCode.VALIDATION_NOT_PERFORMED,),
            warnings=(),
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=non_utc,
        )


def test_restore_plan_requires_contiguous_action_ordinals() -> None:
    invalid_actions = (
        RestoreAction(1, RestoreActionType.INSPECT_TARGET, "Inspect target."),
        RestoreAction(3, RestoreActionType.AWAIT_APPROVAL, "Await approval."),
    )
    with pytest.raises(ValueError, match="contiguous"):
        plan(actions=invalid_actions)


def test_restore_plan_requires_distinct_governed_paths() -> None:
    target = Path("/srv/poe/registry.sqlite3")
    with pytest.raises(ValueError, match="must be distinct"):
        plan(staging_target_path=target)


def test_restore_plan_cannot_authorize_execution() -> None:
    with pytest.raises(ValueError, match="cannot authorize execution"):
        plan(execution_authorized=True)


def test_restore_plan_is_immutable() -> None:
    restore_plan = plan()
    with pytest.raises(FrozenInstanceError):
        restore_plan.plan_id = "changed"


def test_restore_plan_contract_exports_expected_versions() -> None:
    assert RESTORE_PLAN_SCHEMA_VERSION == "1.0"
    assert RESTORE_PLAN_POLICY_VERSION == "5B.1"
