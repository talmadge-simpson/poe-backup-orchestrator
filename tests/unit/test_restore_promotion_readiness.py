"""Tests for restore execution ownership and promotion readiness."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION,
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RESTORE_REGISTRY_APPLICATION_VALIDATION_SCHEMA_VERSION,
    RESTORE_ROLLBACK_ARTIFACT_CAPTURE_SCHEMA_VERSION,
    RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION,
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
    RestoreRegistryApplicationValidation,
    RestoreRegistryApplicationValidationReasonCode,
    RestoreRegistryApplicationValidationStatus,
    RestoreRollbackArtifactCapture,
    RestoreRollbackArtifactCaptureReasonCode,
    RestoreRollbackArtifactCaptureStatus,
    RestoreRollbackArtifactObservation,
    RestoreRollbackPlan,
    RestoreStagedArtifactValidation,
    RestoreStagedArtifactValidationReasonCode,
    RestoreStagedArtifactValidationStatus,
)
from poe_backup_orchestrator.services.restore import (
    RestorePromotionReadinessError,
    RestorePromotionReadinessService,
)

NOW = datetime(2026, 7, 28, 22, 0, tzinfo=UTC)


def _plan(tmp_path: Path, *, target_exists: bool) -> RestorePlan:
    source = tmp_path / "source.sqlite3"
    staged = tmp_path / "staging" / "registry.sqlite3"
    target = tmp_path / "authoritative" / "registry.sqlite3"
    rollback = tmp_path / "rollback" / "registry-before-restore.sqlite3"

    source.write_bytes(b"staged-registry")
    staged.parent.mkdir()
    staged.write_bytes(b"staged-registry")
    target.parent.mkdir()
    rollback.parent.mkdir()
    if target_exists:
        target.write_bytes(b"authoritative-registry")

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-promotion-readiness",
        created_at_utc=NOW,
        recovery_point_id="rp-promotion-readiness",
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


def _staged_validation(plan: RestorePlan) -> RestoreStagedArtifactValidation:
    source_data = plan.source_artifact_path.read_bytes()
    staged_data = plan.staging_target_path.read_bytes()
    return RestoreStagedArtifactValidation(
        schema_version=RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        validated_at_utc=NOW,
        status=RestoreStagedArtifactValidationStatus.VALID,
        reason_codes=(
            RestoreStagedArtifactValidationReasonCode.BYTE_COUNTS_MATCH,
            RestoreStagedArtifactValidationReasonCode.SHA256_MATCH,
            RestoreStagedArtifactValidationReasonCode.SQLITE_QUICK_CHECK_OK,
            RestoreStagedArtifactValidationReasonCode.SQLITE_INTEGRITY_CHECK_OK,
            RestoreStagedArtifactValidationReasonCode.STAGED_ARTIFACT_VALID,
        ),
        source_path=plan.source_artifact_path,
        staged_path=plan.staging_target_path,
        source_size_bytes=len(source_data),
        staged_size_bytes=len(staged_data),
        source_sha256=hashlib.sha256(source_data).hexdigest(),
        staged_sha256=hashlib.sha256(staged_data).hexdigest(),
        sqlite_opened_read_only=True,
        quick_check_results=("ok",),
        integrity_check_results=("ok",),
        authoritative_target_modified=False,
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


def _preflight(
    plan: RestorePlan,
    *,
    target_exists: bool,
) -> RestoreAuthoritativeTargetPreflight:
    if target_exists:
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
        required = True
        source = plan.authoritative_target_path
    else:
        observation = None
        state = RestoreAuthoritativeTargetState.ABSENT
        required = False
        source = None

    return RestoreAuthoritativeTargetPreflight(
        schema_version=RESTORE_AUTHORITATIVE_TARGET_PREFLIGHT_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        preflight_at_utc=NOW,
        status=RestoreAuthoritativeTargetPreflightStatus.READY,
        reason_codes=(
            RestoreAuthoritativeTargetPreflightReasonCode.APPLICATION_VALIDATION_ACCEPTED,
            RestoreAuthoritativeTargetPreflightReasonCode.PREFLIGHT_READY,
        ),
        authoritative_target_path=plan.authoritative_target_path,
        target_state=state,
        target_observation=observation,
        rollback_plan=RestoreRollbackPlan(
            required=required,
            source_path=source,
            destination_path=plan.rollback_artifact_path,
            destination_parent_ready=True,
            destination_available=True,
        ),
        staged_artifact_modified=False,
        authoritative_target_modified=False,
        rollback_artifact_created=False,
    )


def _capture(
    plan: RestorePlan,
    *,
    required: bool,
) -> RestoreRollbackArtifactCapture:
    if required:
        source_data = plan.authoritative_target_path.read_bytes()
        plan.rollback_artifact_path.write_bytes(source_data)
        file_stat = plan.rollback_artifact_path.stat()
        rollback_observation = RestoreRollbackArtifactObservation(
            path=plan.rollback_artifact_path,
            size_bytes=len(source_data),
            sha256=hashlib.sha256(source_data).hexdigest(),
            mode=file_stat.st_mode & 0o7777,
            modified_at_utc=datetime.fromtimestamp(file_stat.st_mtime, tz=UTC),
        )
        source_stat = plan.authoritative_target_path.stat()
        source_observation = RestoreAuthoritativeTargetObservation(
            path=plan.authoritative_target_path,
            size_bytes=len(source_data),
            sha256=hashlib.sha256(source_data).hexdigest(),
            mode=source_stat.st_mode & 0o7777,
            owner_uid=source_stat.st_uid,
            owner_gid=source_stat.st_gid,
            modified_at_utc=datetime.fromtimestamp(source_stat.st_mtime, tz=UTC),
        )
        status = RestoreRollbackArtifactCaptureStatus.CAPTURED
        source_path = plan.authoritative_target_path
        copied_bytes = len(source_data)
    else:
        rollback_observation = None
        source_observation = None
        status = RestoreRollbackArtifactCaptureStatus.NOT_REQUIRED
        source_path = None
        copied_bytes = 0

    return RestoreRollbackArtifactCapture(
        schema_version=RESTORE_ROLLBACK_ARTIFACT_CAPTURE_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        captured_at_utc=NOW,
        status=status,
        reason_codes=(
            RestoreRollbackArtifactCaptureReasonCode.PREFLIGHT_ACCEPTED,
            RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_CAPTURE_COMPLETE
            if required
            else RestoreRollbackArtifactCaptureReasonCode.ROLLBACK_NOT_REQUIRED,
        ),
        capture_required=required,
        source_path=source_path,
        destination_path=plan.rollback_artifact_path,
        source_observation=source_observation,
        rollback_observation=rollback_observation,
        copied_bytes=copied_bytes,
        checksum_matched=True,
        source_remained_stable=True,
        mode_preserved=True,
        staged_artifact_modified=False,
        authoritative_target_modified=False,
    )


def test_exclusive_ownership_blocks_concurrent_owner(tmp_path: Path) -> None:
    service = RestorePromotionReadinessService()
    lock_path = tmp_path / "restore.lock"

    first = service.acquire_ownership(
        plan_id="plan-1",
        lock_path=lock_path,
        acquired_at_utc=NOW,
    )
    try:
        with pytest.raises(
            RestorePromotionReadinessError,
            match="already held",
        ):
            service.acquire_ownership(
                plan_id="plan-2",
                lock_path=lock_path,
                acquired_at_utc=NOW,
            )
    finally:
        first.release()

    assert not lock_path.exists()


def test_ready_with_required_rollback(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    preflight = _preflight(plan, target_exists=True)
    capture = _capture(plan, required=True)
    service = RestorePromotionReadinessService(digest_chunk_size=4)
    lock_path = tmp_path / "restore.lock"

    with service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=lock_path,
        acquired_at_utc=NOW,
    ) as ownership:
        result = service.evaluate(
            plan,
            _staged_validation(plan),
            _application_validation(plan),
            preflight,
            capture,
            ownership.evidence,
            evaluated_at_utc=NOW,
        )
        assert result.status.value == "ready"
        assert result.authoritative_observation is not None
        assert result.rollback_observation is not None
        assert result.promotion_performed is False

    assert not lock_path.exists()


def test_ready_when_target_and_rollback_are_absent(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    preflight = _preflight(plan, target_exists=False)
    capture = _capture(plan, required=False)
    service = RestorePromotionReadinessService()
    lock_path = tmp_path / "restore.lock"

    with service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=lock_path,
        acquired_at_utc=NOW,
    ) as ownership:
        result = service.evaluate(
            plan,
            _staged_validation(plan),
            _application_validation(plan),
            preflight,
            capture,
            ownership.evidence,
            evaluated_at_utc=NOW,
        )

    assert result.authoritative_observation is None
    assert result.rollback_observation is None


def test_staged_artifact_drift_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    staged_validation = _staged_validation(plan)
    preflight = _preflight(plan, target_exists=False)
    capture = _capture(plan, required=False)
    plan.staging_target_path.write_bytes(b"changed-after-validation")
    service = RestorePromotionReadinessService()
    lock_path = tmp_path / "restore.lock"

    with service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=lock_path,
        acquired_at_utc=NOW,
    ) as ownership:
        with pytest.raises(
            RestorePromotionReadinessError,
            match="changed after validation",
        ):
            service.evaluate(
                plan,
                staged_validation,
                _application_validation(plan),
                preflight,
                capture,
                ownership.evidence,
                evaluated_at_utc=NOW,
            )


def test_authoritative_drift_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    preflight = _preflight(plan, target_exists=True)
    capture = _capture(plan, required=True)
    plan.authoritative_target_path.write_bytes(b"changed")
    service = RestorePromotionReadinessService()
    lock_path = tmp_path / "restore.lock"

    with service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=lock_path,
        acquired_at_utc=NOW,
    ) as ownership:
        with pytest.raises(
            RestorePromotionReadinessError,
            match="changed after preflight",
        ):
            service.evaluate(
                plan,
                _staged_validation(plan),
                _application_validation(plan),
                preflight,
                capture,
                ownership.evidence,
                evaluated_at_utc=NOW,
            )


def test_rollback_drift_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    preflight = _preflight(plan, target_exists=True)
    capture = _capture(plan, required=True)
    plan.rollback_artifact_path.write_bytes(b"changed")
    service = RestorePromotionReadinessService()
    lock_path = tmp_path / "restore.lock"

    with service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=lock_path,
        acquired_at_utc=NOW,
    ) as ownership:
        with pytest.raises(
            RestorePromotionReadinessError,
            match="changed after capture",
        ):
            service.evaluate(
                plan,
                _staged_validation(plan),
                _application_validation(plan),
                preflight,
                capture,
                ownership.evidence,
                evaluated_at_utc=NOW,
            )


def test_unexpected_rollback_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    preflight = _preflight(plan, target_exists=False)
    capture = _capture(plan, required=False)
    plan.rollback_artifact_path.write_bytes(b"unexpected")
    service = RestorePromotionReadinessService()
    lock_path = tmp_path / "restore.lock"

    with service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=lock_path,
        acquired_at_utc=NOW,
    ) as ownership:
        with pytest.raises(
            RestorePromotionReadinessError,
            match="unexpected rollback artifact exists",
        ):
            service.evaluate(
                plan,
                _staged_validation(plan),
                _application_validation(plan),
                preflight,
                capture,
                ownership.evidence,
                evaluated_at_utc=NOW,
            )


def test_missing_lock_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    preflight = _preflight(plan, target_exists=False)
    capture = _capture(plan, required=False)
    service = RestorePromotionReadinessService()
    handle = service.acquire_ownership(
        plan_id=plan.plan_id,
        lock_path=tmp_path / "restore.lock",
        acquired_at_utc=NOW,
    )
    evidence = handle.evidence
    handle.release()

    with pytest.raises(
        RestorePromotionReadinessError,
        match="lock is not present",
    ):
        service.evaluate(
            plan,
            _staged_validation(plan),
            _application_validation(plan),
            preflight,
            capture,
            evidence,
            evaluated_at_utc=NOW,
        )
