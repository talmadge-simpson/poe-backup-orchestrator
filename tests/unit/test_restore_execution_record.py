"""Tests for immutable restore execution aggregation."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_EXECUTION_RECORD_SCHEMA_VERSION,
    RestoreExecutionRecord,
)


def _build_record(**overrides):
    plan_id = "restore-plan-001"
    started_at = datetime(2026, 7, 28, 15, 0, tzinfo=UTC)
    completed_at = started_at + timedelta(seconds=10)

    values = {
        "schema_version": RESTORE_EXECUTION_RECORD_SCHEMA_VERSION,
        "plan_id": plan_id,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "lock_path": Path("/tmp/restore-plan-001.lock"),
        "plan": SimpleNamespace(plan_id=plan_id),
        "workspace_preflight": SimpleNamespace(plan_id=plan_id),
        "workspace_materialization": SimpleNamespace(plan_id=plan_id),
        "artifact_staging": SimpleNamespace(plan_id=plan_id),
        "staged_validation": SimpleNamespace(plan_id=plan_id),
        "application_validation": SimpleNamespace(plan_id=plan_id),
        "authoritative_preflight": SimpleNamespace(plan_id=plan_id),
        "rollback_capture": SimpleNamespace(plan_id=plan_id),
        "promotion_readiness": SimpleNamespace(plan_id=plan_id),
        "authoritative_promotion": SimpleNamespace(plan_id=plan_id),
        "post_promotion_verification": SimpleNamespace(
            plan_id=plan_id,
            verified_at_utc=completed_at,
            restore_completed=True,
        ),
        "restore_completed": True,
    }
    values.update(overrides)
    return RestoreExecutionRecord(**values)


def test_execution_record_accepts_complete_coherent_evidence():
    record = _build_record()

    assert record.restore_completed is True
    assert record.plan_id == "restore-plan-001"


def test_execution_record_rejects_plan_identity_mismatch():
    with pytest.raises(ValueError, match="restore plan plan_id"):
        _build_record(plan=SimpleNamespace(plan_id="different-plan"))


def test_execution_record_rejects_evidence_identity_mismatch():
    with pytest.raises(ValueError, match="restore evidence plan_id"):
        _build_record(rollback_capture=SimpleNamespace(plan_id="different-plan"))


def test_execution_record_rejects_incomplete_verification():
    completed_at = datetime(2026, 7, 28, 15, 0, 10, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="post-promotion verification must declare restore completion",
    ):
        _build_record(
            post_promotion_verification=SimpleNamespace(
                plan_id="restore-plan-001",
                verified_at_utc=completed_at,
                restore_completed=False,
            )
        )


def test_execution_record_rejects_completion_time_mismatch():
    with pytest.raises(ValueError, match="completed_at_utc must match"):
        _build_record(completed_at_utc=datetime(2026, 7, 28, 15, 0, 11, tzinfo=UTC))


def test_execution_record_is_immutable():
    record = _build_record()

    with pytest.raises(FrozenInstanceError):
        record.plan_id = "different-plan"
