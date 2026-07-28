"""Tests for authoritative target preflight and rollback planning."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RESTORE_REGISTRY_APPLICATION_VALIDATION_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanValidation,
    RestoreRegistryApplicationValidation,
    RestoreRegistryApplicationValidationReasonCode,
    RestoreRegistryApplicationValidationStatus,
)
from poe_backup_orchestrator.services.restore import (
    RestoreAuthoritativeTargetPreflightError,
    preflight_authoritative_target,
)

NOW = datetime(2026, 7, 28, 20, 0, tzinfo=UTC)


def _plan(tmp_path: Path, *, target_exists: bool) -> RestorePlan:
    source = tmp_path / "source.sqlite3"
    staged = tmp_path / "staging" / "registry.sqlite3"
    target = tmp_path / "authoritative" / "registry.sqlite3"
    rollback = tmp_path / "rollback" / "registry-before-restore.sqlite3"

    source.write_bytes(b"source-registry")
    staged.parent.mkdir()
    staged.write_bytes(b"staged-registry")
    target.parent.mkdir()
    rollback.parent.mkdir()
    if target_exists:
        target.write_bytes(b"authoritative-registry")

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-authoritative-preflight",
        created_at_utc=NOW,
        recovery_point_id="rp-authoritative-preflight",
        source_artifact_path=source,
        source_manifest_path=tmp_path / "manifest.json",
        authoritative_target_path=target,
        staging_target_path=staged,
        rollback_artifact_path=rollback,
        actions=(
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect authoritative target.",
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


def _application_validation(
    plan: RestorePlan,
) -> RestoreRegistryApplicationValidation:
    return RestoreRegistryApplicationValidation(
        schema_version=RESTORE_REGISTRY_APPLICATION_VALIDATION_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        validated_at_utc=NOW,
        status=RestoreRegistryApplicationValidationStatus.VALID,
        reason_codes=(
            RestoreRegistryApplicationValidationReasonCode.REQUIRED_TABLES_PRESENT,
            RestoreRegistryApplicationValidationReasonCode.REQUIRED_COLUMNS_PRESENT,
            RestoreRegistryApplicationValidationReasonCode.REQUIRED_METADATA_VALID,
            RestoreRegistryApplicationValidationReasonCode.ROW_COUNTS_VALID,
            RestoreRegistryApplicationValidationReasonCode.REGISTRY_APPLICATION_VALID,
        ),
        policy_id="test-policy",
        policy_version="1.0",
        staged_path=plan.staging_target_path,
        discovered_tables=("assets",),
        discovered_columns=(("assets", ("asset_id",)),),
        metadata_observations=(),
        row_count_observations=(("assets", 1),),
        staged_artifact_modified=False,
        authoritative_target_modified=False,
    )


def test_absent_target_requires_no_rollback(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)

    result = preflight_authoritative_target(
        plan,
        _application_validation(plan),
        preflight_at_utc=NOW,
    )

    assert result.target_state.value == "absent"
    assert result.target_observation is None
    assert result.rollback_plan.required is False
    assert result.rollback_plan.source_path is None
    assert result.rollback_plan.destination_path == plan.rollback_artifact_path
    assert not plan.authoritative_target_path.exists()
    assert not plan.rollback_artifact_path.exists()


def test_regular_target_requires_rollback_and_is_observed(
    tmp_path: Path,
) -> None:
    plan = _plan(tmp_path, target_exists=True)
    before = plan.authoritative_target_path.read_bytes()

    result = preflight_authoritative_target(
        plan,
        _application_validation(plan),
        preflight_at_utc=NOW,
        digest_chunk_size=4,
    )

    observation = result.target_observation
    assert observation is not None
    assert observation.size_bytes == len(before)
    assert observation.sha256 == hashlib.sha256(before).hexdigest()
    assert result.rollback_plan.required is True
    assert result.rollback_plan.source_path == plan.authoritative_target_path
    assert plan.authoritative_target_path.read_bytes() == before
    assert not plan.rollback_artifact_path.exists()


def test_existing_rollback_destination_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    plan.rollback_artifact_path.write_bytes(b"existing")

    with pytest.raises(
        RestoreAuthoritativeTargetPreflightError,
        match="rollback destination already exists",
    ):
        preflight_authoritative_target(
            plan,
            _application_validation(plan),
            preflight_at_utc=NOW,
        )


def test_missing_rollback_parent_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    plan.rollback_artifact_path.parent.rmdir()

    with pytest.raises(
        RestoreAuthoritativeTargetPreflightError,
        match="rollback destination parent does not exist",
    ):
        preflight_authoritative_target(
            plan,
            _application_validation(plan),
            preflight_at_utc=NOW,
        )


def test_non_regular_target_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    plan.authoritative_target_path.mkdir()

    with pytest.raises(
        RestoreAuthoritativeTargetPreflightError,
        match="not a regular file",
    ):
        preflight_authoritative_target(
            plan,
            _application_validation(plan),
            preflight_at_utc=NOW,
        )


def test_application_validation_plan_mismatch_is_rejected(
    tmp_path: Path,
) -> None:
    plan = _plan(tmp_path, target_exists=False)
    evidence = _application_validation(plan)
    mismatch = RestoreRegistryApplicationValidation(
        schema_version=evidence.schema_version,
        plan_id="other-plan",
        validated_at_utc=evidence.validated_at_utc,
        status=evidence.status,
        reason_codes=evidence.reason_codes,
        policy_id=evidence.policy_id,
        policy_version=evidence.policy_version,
        staged_path=evidence.staged_path,
        discovered_tables=evidence.discovered_tables,
        discovered_columns=evidence.discovered_columns,
        metadata_observations=evidence.metadata_observations,
        row_count_observations=evidence.row_count_observations,
        staged_artifact_modified=False,
        authoritative_target_modified=False,
    )

    with pytest.raises(
        RestoreAuthoritativeTargetPreflightError,
        match="plan_id does not match",
    ):
        preflight_authoritative_target(
            plan,
            mismatch,
            preflight_at_utc=NOW,
        )


def test_non_utc_timestamp_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    local_time = datetime.fromisoformat("2026-07-28T20:00:00-04:00")

    with pytest.raises(
        RestoreAuthoritativeTargetPreflightError,
        match="must use UTC",
    ):
        preflight_authoritative_target(
            plan,
            _application_validation(plan),
            preflight_at_utc=local_time,
        )


def test_path_collision_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    plan.rollback_artifact_path.symlink_to(plan.authoritative_target_path)

    with pytest.raises(
        RestoreAuthoritativeTargetPreflightError,
        match="rollback destination collides",
    ):
        preflight_authoritative_target(
            plan,
            _application_validation(plan),
            preflight_at_utc=NOW,
        )
