"""Tests for rollback artifact capture and validation."""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION,
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestoreAuthoritativeTargetObservation,
    RestoreAuthoritativeTargetPreflight,
    RestoreAuthoritativeTargetPreflightReasonCode,
    RestoreAuthoritativeTargetPreflightStatus,
    RestoreAuthoritativeTargetState,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanValidation,
    RestoreRollbackPlan,
)
from poe_backup_orchestrator.services.restore import (
    RestoreRollbackArtifactCaptureError,
    capture_rollback_artifact,
)

NOW = datetime(2026, 7, 28, 21, 0, tzinfo=UTC)


def _plan(tmp_path: Path, *, target_exists: bool) -> RestorePlan:
    source = tmp_path / "source.sqlite3"
    staged = tmp_path / "staging" / "registry.sqlite3"
    target = tmp_path / "authoritative" / "registry.sqlite3"
    rollback = tmp_path / "rollback" / "registry-before-restore.sqlite3"

    source.write_bytes(b"source")
    staged.parent.mkdir()
    staged.write_bytes(b"staged")
    target.parent.mkdir()
    rollback.parent.mkdir()
    if target_exists:
        target.write_bytes(b"authoritative-registry")

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-rollback-capture",
        created_at_utc=NOW,
        recovery_point_id="rp-rollback-capture",
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


def _preflight(
    plan: RestorePlan,
    *,
    required: bool,
) -> RestoreAuthoritativeTargetPreflight:
    if required:
        file_stat = plan.authoritative_target_path.stat()
        data = plan.authoritative_target_path.read_bytes()
        observation = RestoreAuthoritativeTargetObservation(
            path=plan.authoritative_target_path,
            size_bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
            mode=file_stat.st_mode & 0o7777,
            owner_uid=file_stat.st_uid,
            owner_gid=file_stat.st_gid,
            modified_at_utc=datetime.fromtimestamp(file_stat.st_mtime, tz=UTC),
        )
        state = RestoreAuthoritativeTargetState.REGULAR_FILE
        source_path = plan.authoritative_target_path
        reasons = (
            RestoreAuthoritativeTargetPreflightReasonCode.APPLICATION_VALIDATION_ACCEPTED,
            RestoreAuthoritativeTargetPreflightReasonCode.AUTHORITATIVE_TARGET_REGULAR_FILE,
            RestoreAuthoritativeTargetPreflightReasonCode.AUTHORITATIVE_TARGET_READABLE,
            RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_REQUIRED,
            RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_DESTINATION_AVAILABLE,
            RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_PARENT_READY,
            RestoreAuthoritativeTargetPreflightReasonCode.PREFLIGHT_READY,
        )
    else:
        observation = None
        state = RestoreAuthoritativeTargetState.ABSENT
        source_path = None
        reasons = (
            RestoreAuthoritativeTargetPreflightReasonCode.APPLICATION_VALIDATION_ACCEPTED,
            RestoreAuthoritativeTargetPreflightReasonCode.AUTHORITATIVE_TARGET_ABSENT,
            RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_NOT_REQUIRED,
            RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_DESTINATION_AVAILABLE,
            RestoreAuthoritativeTargetPreflightReasonCode.ROLLBACK_PARENT_READY,
            RestoreAuthoritativeTargetPreflightReasonCode.PREFLIGHT_READY,
        )

    return RestoreAuthoritativeTargetPreflight(
        schema_version=RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        preflight_at_utc=NOW,
        status=RestoreAuthoritativeTargetPreflightStatus.READY,
        reason_codes=reasons,
        authoritative_target_path=plan.authoritative_target_path,
        target_state=state,
        target_observation=observation,
        rollback_plan=RestoreRollbackPlan(
            required=required,
            source_path=source_path,
            destination_path=plan.rollback_artifact_path,
            destination_parent_ready=True,
            destination_available=True,
        ),
        staged_artifact_modified=False,
        authoritative_target_modified=False,
        rollback_artifact_created=False,
    )


def test_not_required_emits_evidence_without_copy(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    staged_before = plan.staging_target_path.read_bytes()

    result = capture_rollback_artifact(
        plan,
        _preflight(plan, required=False),
        captured_at_utc=NOW,
    )

    assert result.status.value == "not_required"
    assert result.capture_required is False
    assert result.copied_bytes == 0
    assert not plan.rollback_artifact_path.exists()
    assert not plan.authoritative_target_path.exists()
    assert plan.staging_target_path.read_bytes() == staged_before


def test_required_capture_copies_and_validates_bytes(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    source_before = plan.authoritative_target_path.read_bytes()
    staged_before = plan.staging_target_path.read_bytes()
    os.chmod(plan.authoritative_target_path, 0o640)

    preflight = _preflight(plan, required=True)
    result = capture_rollback_artifact(
        plan,
        preflight,
        captured_at_utc=NOW,
        copy_chunk_size=4,
    )

    assert result.status.value == "captured"
    assert result.capture_required is True
    assert result.copied_bytes == len(source_before)
    assert result.checksum_matched is True
    assert result.source_remained_stable is True
    assert result.mode_preserved is True
    assert plan.rollback_artifact_path.read_bytes() == source_before
    assert plan.authoritative_target_path.read_bytes() == source_before
    assert plan.staging_target_path.read_bytes() == staged_before
    assert (
        plan.rollback_artifact_path.stat().st_mode & 0o7777
        == plan.authoritative_target_path.stat().st_mode & 0o7777
    )


def test_existing_destination_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    preflight = _preflight(plan, required=True)
    plan.rollback_artifact_path.write_bytes(b"existing")

    with pytest.raises(
        RestoreRollbackArtifactCaptureError,
        match="rollback destination already exists",
    ):
        capture_rollback_artifact(
            plan,
            preflight,
            captured_at_utc=NOW,
        )

    assert plan.rollback_artifact_path.read_bytes() == b"existing"


def test_source_drift_after_preflight_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    preflight = _preflight(plan, required=True)
    plan.authoritative_target_path.write_bytes(b"changed-after-preflight")

    with pytest.raises(
        RestoreRollbackArtifactCaptureError,
        match="changed after preflight",
    ):
        capture_rollback_artifact(
            plan,
            preflight,
            captured_at_utc=NOW,
        )

    assert not plan.rollback_artifact_path.exists()


def test_plan_id_mismatch_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    preflight = _preflight(plan, required=True)
    mismatch = RestoreAuthoritativeTargetPreflight(
        schema_version=preflight.schema_version,
        plan_id="other-plan",
        preflight_at_utc=preflight.preflight_at_utc,
        status=preflight.status,
        reason_codes=preflight.reason_codes,
        authoritative_target_path=preflight.authoritative_target_path,
        target_state=preflight.target_state,
        target_observation=preflight.target_observation,
        rollback_plan=preflight.rollback_plan,
        staged_artifact_modified=False,
        authoritative_target_modified=False,
        rollback_artifact_created=False,
    )

    with pytest.raises(
        RestoreRollbackArtifactCaptureError,
        match="plan_id does not match",
    ):
        capture_rollback_artifact(
            plan,
            mismatch,
            captured_at_utc=NOW,
        )


def test_non_utc_timestamp_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    local_time = datetime.fromisoformat("2026-07-28T21:00:00-04:00")

    with pytest.raises(
        RestoreRollbackArtifactCaptureError,
        match="must use UTC",
    ):
        capture_rollback_artifact(
            plan,
            _preflight(plan, required=True),
            captured_at_utc=local_time,
        )


def test_unrequired_capture_rejects_unexpected_destination(
    tmp_path: Path,
) -> None:
    plan = _plan(tmp_path, target_exists=False)
    plan.rollback_artifact_path.write_bytes(b"unexpected")

    with pytest.raises(
        RestoreRollbackArtifactCaptureError,
        match="although capture is not required",
    ):
        capture_rollback_artifact(
            plan,
            _preflight(plan, required=False),
            captured_at_utc=NOW,
        )
