"""Tests for deterministic, non-mutating restore-plan construction."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RecoveryPoint,
    RecoveryPointEligibility,
    RecoveryPointEligibilityResult,
    RecoveryPointReasonCode,
    RestoreActionType,
    RestorePlanReadiness,
    RestorePlanRequest,
)
from poe_backup_orchestrator.services.restore import (
    RestorePlanningError,
    RestorePlanningService,
    build_restore_plan,
)

CREATED_AT = datetime(2026, 7, 28, 15, 30, 12, 345678, tzinfo=UTC)


def eligibility(
    classification: RecoveryPointEligibility = RecoveryPointEligibility.ELIGIBLE,
    *,
    warnings: tuple[str, ...] = (),
    override_required: bool = False,
) -> RecoveryPointEligibilityResult:
    reason = {
        RecoveryPointEligibility.ELIGIBLE: RecoveryPointReasonCode.RECOVERY_POINT_ELIGIBLE,
        RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE: (
            RecoveryPointReasonCode.RECOVERY_POINT_EXPIRED
        ),
        RecoveryPointEligibility.INELIGIBLE: RecoveryPointReasonCode.ARTIFACT_MISSING,
        RecoveryPointEligibility.UNKNOWN: RecoveryPointReasonCode.STATUS_UNDETERMINED,
    }[classification]
    return RecoveryPointEligibilityResult(
        classification=classification,
        reason_codes=(reason,),
        warnings=warnings,
        override_required=override_required,
        evaluated_at_utc=CREATED_AT,
        policy_version="5A.4",
    )


def point(
    classification: RecoveryPointEligibility = RecoveryPointEligibility.ELIGIBLE,
    *,
    warnings: tuple[str, ...] = (),
) -> RecoveryPoint:
    return RecoveryPoint(
        recovery_point_id="rp-20260727T170000Z",
        package_path=Path("/repository/rp-20260727T170000Z"),
        artifact_path=Path("/repository/rp-20260727T170000Z/registry.sqlite3"),
        manifest_path=Path("/repository/rp-20260727T170000Z/manifest.json"),
        source_backup_execution_id="backup-20260727T170000Z",
        source_registry_id="poeregistry",
        created_at_utc=datetime(2026, 7, 27, 17, 0, tzinfo=UTC),
        artifact_size_bytes=4096,
        artifact_sha256="a" * 64,
        manifest_version="1.0",
        backup_status="completed",
        verification_status="PASS",
        quarantined=False,
        eligibility=eligibility(
            classification,
            warnings=warnings,
            override_required=(classification is RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE),
        ),
    )


def request(
    *,
    override: bool = False,
) -> RestorePlanRequest:
    return RestorePlanRequest(
        recovery_point_id="rp-20260727T170000Z",
        authoritative_target_path=Path("/srv/poe/registry/POERegistry.db"),
        staging_root=Path("/srv/poe-backup/Restore-Tests/staging"),
        rollback_root=Path("/srv/poe-backup/Restore-Tests/rollback"),
        eligibility_override_requested=override,
        operator_rationale="Approved recovery exception." if override else None,
    )


def test_eligible_point_produces_deterministic_ready_plan() -> None:
    first = build_restore_plan(point(), request(), created_at_utc=CREATED_AT)
    second = build_restore_plan(point(), request(), created_at_utc=CREATED_AT)

    assert first == second
    assert first.plan_id == ("restore-plan-rp-20260727T170000Z-20260728T153012345678Z")
    assert first.validation.readiness is RestorePlanReadiness.READY
    assert first.execution_authorized is False


def test_planner_composes_governed_paths_without_creating_them(
    tmp_path: Path,
) -> None:
    planning_request = RestorePlanRequest(
        recovery_point_id="rp-20260727T170000Z",
        authoritative_target_path=tmp_path / "authoritative" / "POERegistry.db",
        staging_root=tmp_path / "staging",
        rollback_root=tmp_path / "rollback",
    )

    plan = RestorePlanningService().plan(
        point(),
        planning_request,
        created_at_utc=CREATED_AT,
    )

    assert plan.staging_target_path == (tmp_path / "staging" / plan.plan_id / "registry.sqlite3")
    assert plan.rollback_artifact_path == (tmp_path / "rollback" / plan.plan_id / "POERegistry.db")
    assert not (tmp_path / "staging").exists()
    assert not (tmp_path / "rollback").exists()


def test_ready_plan_has_complete_future_action_sequence() -> None:
    plan = build_restore_plan(point(), request(), created_at_utc=CREATED_AT)

    assert tuple(action.action_type for action in plan.actions) == (
        RestoreActionType.INSPECT_TARGET,
        RestoreActionType.STAGE_RECOVERY_ARTIFACT,
        RestoreActionType.VERIFY_STAGED_CHECKSUM,
        RestoreActionType.VERIFY_STAGED_SQLITE_INTEGRITY,
        RestoreActionType.CREATE_ROLLBACK_ARTIFACT,
        RestoreActionType.VERIFY_ROLLBACK_ARTIFACT,
        RestoreActionType.PROMOTE_STAGED_ARTIFACT,
        RestoreActionType.VERIFY_AUTHORITATIVE_TARGET,
        RestoreActionType.PUBLISH_RESTORE_EVIDENCE,
    )
    assert tuple(action.ordinal for action in plan.actions) == tuple(range(1, 10))


def test_conditionally_eligible_point_requires_approval() -> None:
    plan = build_restore_plan(
        point(RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE),
        request(override=True),
        created_at_utc=CREATED_AT,
    )

    assert plan.validation.readiness is RestorePlanReadiness.APPROVAL_REQUIRED
    assert plan.validation.approval_required is True
    assert RestoreActionType.AWAIT_APPROVAL in {action.action_type for action in plan.actions}
    promotion = next(
        action
        for action in plan.actions
        if action.action_type is RestoreActionType.PROMOTE_STAGED_ARTIFACT
    )
    assert promotion.approval_required is True
    assert plan.execution_authorized is False


@pytest.mark.parametrize(
    "classification",
    [
        RecoveryPointEligibility.INELIGIBLE,
        RecoveryPointEligibility.UNKNOWN,
    ],
)
def test_nonviable_eligibility_produces_blocked_nonmutating_plan(
    classification: RecoveryPointEligibility,
) -> None:
    plan = build_restore_plan(
        point(classification),
        request(),
        created_at_utc=CREATED_AT,
    )

    assert plan.validation.readiness is RestorePlanReadiness.BLOCKED
    assert plan.validation.conflicts[0].blocking is True
    assert all(not action.mutates_state for action in plan.actions)
    assert tuple(action.action_type for action in plan.actions) == (
        RestoreActionType.INSPECT_TARGET,
    )


def test_eligibility_warnings_are_preserved_as_structured_warnings() -> None:
    plan = build_restore_plan(
        point(warnings=("Recovery point exceeds normal age policy.",)),
        request(),
        created_at_utc=CREATED_AT,
    )

    assert tuple(warning.message for warning in plan.validation.warnings) == (
        "Recovery point exceeds normal age policy.",
    )


def test_request_and_recovery_point_identifiers_must_match() -> None:
    mismatched = replace(request(), recovery_point_id="other-point")

    with pytest.raises(RestorePlanningError, match="does not match"):
        build_restore_plan(point(), mismatched, created_at_utc=CREATED_AT)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("artifact_path", "artifact path"),
        ("manifest_path", "manifest path"),
    ],
)
def test_required_recovery_metadata_is_enforced(
    field: str,
    message: str,
) -> None:
    incomplete = replace(point(), **{field: None})

    with pytest.raises(RestorePlanningError, match=message):
        build_restore_plan(incomplete, request(), created_at_utc=CREATED_AT)


def test_planning_timestamp_must_be_utc() -> None:
    non_utc = CREATED_AT.astimezone(timezone(timedelta(hours=-4)))

    with pytest.raises(RestorePlanningError, match="must use UTC"):
        build_restore_plan(point(), request(), created_at_utc=non_utc)


def test_service_contract_is_exported() -> None:
    from poe_backup_orchestrator.services import restore

    assert restore.RestorePlanningService is RestorePlanningService
    assert restore.RestorePlanningError is RestorePlanningError
    assert restore.build_restore_plan is build_restore_plan
