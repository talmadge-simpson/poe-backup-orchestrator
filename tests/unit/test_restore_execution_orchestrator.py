"""Tests for controlled restore execution orchestration."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from poe_backup_orchestrator.services import restore
from poe_backup_orchestrator.services.restore import RestoreExecutionOrchestrator


def _clock():
    start = datetime(2026, 7, 28, 15, 0, tzinfo=UTC)
    current = start
    while True:
        yield current
        current += timedelta(seconds=1)


def _build_orchestrator():
    plan = SimpleNamespace(plan_id="restore-plan-001")
    lock_path = Path("/tmp/restore-plan-001.lock")
    ownership = object()
    ownership_handle = SimpleNamespace(evidence=ownership, release=Mock())

    workspace_preflight_result = object()
    workspace_materialization_result = object()
    artifact_staging_result = object()
    staged_validation_result = object()
    application_validation_result = object()
    authoritative_preflight_result = object()
    rollback_capture_result = object()
    promotion_readiness_result = object()
    authoritative_promotion_result = object()
    post_promotion_verification_result = object()

    workspace_preflight = Mock()
    workspace_preflight.evaluate.return_value = workspace_preflight_result

    workspace_materialization = Mock()
    workspace_materialization.materialize.return_value = workspace_materialization_result

    artifact_staging = Mock()
    artifact_staging.stage.return_value = artifact_staging_result

    staged_validation = Mock()
    staged_validation.validate.return_value = staged_validation_result

    application_validation = Mock()
    application_validation.validate.return_value = application_validation_result

    authoritative_preflight = Mock()
    authoritative_preflight.preflight.return_value = authoritative_preflight_result

    rollback_capture = Mock()
    rollback_capture.capture.return_value = rollback_capture_result

    promotion_readiness = Mock()
    promotion_readiness.acquire_ownership.return_value = ownership_handle
    promotion_readiness.evaluate.return_value = promotion_readiness_result

    authoritative_promotion = Mock()
    authoritative_promotion.execute.return_value = authoritative_promotion_result

    post_promotion_verification = Mock()
    post_promotion_verification.verify.return_value = post_promotion_verification_result

    timestamps = _clock()
    clock = Mock(side_effect=lambda: next(timestamps))

    orchestrator = RestoreExecutionOrchestrator(
        workspace_preflight=workspace_preflight,
        workspace_materialization=workspace_materialization,
        artifact_staging=artifact_staging,
        staged_validation=staged_validation,
        application_validation=application_validation,
        authoritative_preflight=authoritative_preflight,
        rollback_capture=rollback_capture,
        promotion_readiness=promotion_readiness,
        authoritative_promotion=authoritative_promotion,
        post_promotion_verification=post_promotion_verification,
        clock=clock,
    )

    return SimpleNamespace(
        orchestrator=orchestrator,
        plan=plan,
        lock_path=lock_path,
        ownership=ownership,
        ownership_handle=ownership_handle,
        workspace_preflight=workspace_preflight,
        workspace_preflight_result=workspace_preflight_result,
        workspace_materialization=workspace_materialization,
        workspace_materialization_result=workspace_materialization_result,
        artifact_staging=artifact_staging,
        artifact_staging_result=artifact_staging_result,
        staged_validation=staged_validation,
        staged_validation_result=staged_validation_result,
        application_validation=application_validation,
        application_validation_result=application_validation_result,
        authoritative_preflight=authoritative_preflight,
        authoritative_preflight_result=authoritative_preflight_result,
        rollback_capture=rollback_capture,
        rollback_capture_result=rollback_capture_result,
        promotion_readiness=promotion_readiness,
        promotion_readiness_result=promotion_readiness_result,
        authoritative_promotion=authoritative_promotion,
        authoritative_promotion_result=authoritative_promotion_result,
        post_promotion_verification=post_promotion_verification,
        post_promotion_verification_result=post_promotion_verification_result,
        clock=clock,
    )


def test_execute_sequences_services_and_returns_completion_evidence():
    context = _build_orchestrator()

    result = context.orchestrator.execute(
        context.plan,
        lock_path=context.lock_path,
    )

    assert result is context.post_promotion_verification_result
    assert context.clock.call_count == 11

    context.promotion_readiness.acquire_ownership.assert_called_once_with(
        plan_id=context.plan.plan_id,
        lock_path=context.lock_path,
        acquired_at_utc=datetime(2026, 7, 28, 15, 0, tzinfo=UTC),
    )
    context.workspace_preflight.evaluate.assert_called_once_with(
        context.plan,
        evaluated_at_utc=datetime(2026, 7, 28, 15, 0, 1, tzinfo=UTC),
    )
    context.workspace_materialization.materialize.assert_called_once_with(
        context.plan,
        context.workspace_preflight_result,
        materialized_at_utc=datetime(2026, 7, 28, 15, 0, 2, tzinfo=UTC),
    )
    context.artifact_staging.stage.assert_called_once_with(
        context.plan,
        context.workspace_preflight_result,
        context.workspace_materialization_result,
        staged_at_utc=datetime(2026, 7, 28, 15, 0, 3, tzinfo=UTC),
    )
    context.staged_validation.validate.assert_called_once_with(
        context.plan,
        context.workspace_preflight_result,
        context.workspace_materialization_result,
        context.artifact_staging_result,
        validated_at_utc=datetime(2026, 7, 28, 15, 0, 4, tzinfo=UTC),
    )
    context.application_validation.validate.assert_called_once_with(
        context.plan,
        context.staged_validation_result,
        validated_at_utc=datetime(2026, 7, 28, 15, 0, 5, tzinfo=UTC),
    )
    context.authoritative_preflight.preflight.assert_called_once_with(
        context.plan,
        context.application_validation_result,
        preflight_at_utc=datetime(2026, 7, 28, 15, 0, 6, tzinfo=UTC),
    )
    context.rollback_capture.capture.assert_called_once_with(
        context.plan,
        context.authoritative_preflight_result,
        captured_at_utc=datetime(2026, 7, 28, 15, 0, 7, tzinfo=UTC),
    )
    context.promotion_readiness.evaluate.assert_called_once_with(
        context.plan,
        context.staged_validation_result,
        context.application_validation_result,
        context.authoritative_preflight_result,
        context.rollback_capture_result,
        context.ownership,
        evaluated_at_utc=datetime(2026, 7, 28, 15, 0, 8, tzinfo=UTC),
    )
    context.authoritative_promotion.execute.assert_called_once_with(
        context.plan,
        context.promotion_readiness_result,
        executed_at_utc=datetime(2026, 7, 28, 15, 0, 9, tzinfo=UTC),
    )
    context.post_promotion_verification.verify.assert_called_once_with(
        context.plan,
        context.authoritative_promotion_result,
        verified_at_utc=datetime(2026, 7, 28, 15, 0, 10, tzinfo=UTC),
    )
    context.ownership_handle.release.assert_called_once_with()


def test_execute_releases_ownership_when_a_service_fails():
    context = _build_orchestrator()
    failure = RuntimeError("staged validation failed")
    context.staged_validation.validate.side_effect = failure

    with pytest.raises(RuntimeError, match="staged validation failed"):
        context.orchestrator.execute(
            context.plan,
            lock_path=context.lock_path,
        )

    context.ownership_handle.release.assert_called_once_with()
    context.application_validation.validate.assert_not_called()
    context.authoritative_preflight.preflight.assert_not_called()
    context.rollback_capture.capture.assert_not_called()
    context.promotion_readiness.evaluate.assert_not_called()
    context.authoritative_promotion.execute.assert_not_called()
    context.post_promotion_verification.verify.assert_not_called()


def test_execute_does_not_release_when_ownership_acquisition_fails():
    context = _build_orchestrator()
    context.promotion_readiness.acquire_ownership.side_effect = RuntimeError(
        "ownership unavailable"
    )

    with pytest.raises(RuntimeError, match="ownership unavailable"):
        context.orchestrator.execute(
            context.plan,
            lock_path=context.lock_path,
        )

    context.ownership_handle.release.assert_not_called()
    context.workspace_preflight.evaluate.assert_not_called()


def test_restore_package_exports_execution_orchestrator():
    assert restore.RestoreExecutionOrchestrator is RestoreExecutionOrchestrator
