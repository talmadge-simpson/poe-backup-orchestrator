"""Tests for persistent runtime-state domain models."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from poe_backup_orchestrator.models import (
    RUNTIME_STATE_SCHEMA_VERSION,
    ExecutionState,
    RuntimeEnvironment,
    RuntimeExecutionStatus,
    RuntimeState,
)

STARTED = datetime(2026, 7, 27, 14, 0, tzinfo=UTC)
UPDATED = datetime(2026, 7, 27, 14, 0, 1, tzinfo=UTC)


def runtime_state(
    *,
    schema_version: int = RUNTIME_STATE_SCHEMA_VERSION,
    run_id: str = "job-20260727T140000Z",
    status: RuntimeExecutionStatus = RuntimeExecutionStatus.RUNNING,
    execution_state: ExecutionState = ExecutionState.REPOSITORY_VALIDATION,
    started_at_utc: datetime = STARTED,
    updated_at_utc: datetime = UPDATED,
    pid: int = 1234,
    hostname: str = "ai-lab",
    environment: RuntimeEnvironment = RuntimeEnvironment.DEVELOPMENT,
) -> RuntimeState:
    return RuntimeState(
        schema_version=schema_version,
        run_id=run_id,
        status=status,
        execution_state=execution_state,
        started_at_utc=started_at_utc,
        updated_at_utc=updated_at_utc,
        pid=pid,
        hostname=hostname,
        environment=environment,
    )


def test_runtime_execution_status_has_stable_values() -> None:
    assert RuntimeExecutionStatus.RUNNING.value == "running"
    assert RuntimeExecutionStatus.COMPLETED.value == "completed"
    assert RuntimeExecutionStatus.FAILED.value == "failed"
    assert RuntimeExecutionStatus.INTERRUPTED.value == "interrupted"


def test_runtime_state_accepts_valid_running_state() -> None:
    state = runtime_state()

    assert state.status is RuntimeExecutionStatus.RUNNING
    assert state.execution_state is ExecutionState.REPOSITORY_VALIDATION


def test_runtime_state_accepts_valid_completed_state() -> None:
    state = runtime_state(
        status=RuntimeExecutionStatus.COMPLETED,
        execution_state=ExecutionState.COMPLETED,
    )

    assert state.execution_state is ExecutionState.COMPLETED


def test_runtime_state_accepts_valid_failed_state() -> None:
    state = runtime_state(
        status=RuntimeExecutionStatus.FAILED,
        execution_state=ExecutionState.FAILED,
    )

    assert state.execution_state is ExecutionState.FAILED


def test_runtime_state_accepts_valid_interrupted_state() -> None:
    state = runtime_state(
        status=RuntimeExecutionStatus.INTERRUPTED,
        execution_state=ExecutionState.REGISTRY_ACQUISITION,
    )

    assert state.execution_state is ExecutionState.REGISTRY_ACQUISITION


def test_runtime_state_normalizes_identity_strings() -> None:
    state = runtime_state(run_id="  job-123  ", hostname="  ai-lab  ")

    assert state.run_id == "job-123"
    assert state.hostname == "ai-lab"


@pytest.mark.parametrize("run_id", ["", "   "])
def test_runtime_state_rejects_blank_run_id(run_id: str) -> None:
    with pytest.raises(ValueError, match="run_id"):
        runtime_state(run_id=run_id)


@pytest.mark.parametrize("hostname", ["", "   "])
def test_runtime_state_rejects_blank_hostname(hostname: str) -> None:
    with pytest.raises(ValueError, match="hostname"):
        runtime_state(hostname=hostname)


@pytest.mark.parametrize("pid", [0, -1])
def test_runtime_state_rejects_nonpositive_pid(pid: int) -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        runtime_state(pid=pid)


def test_runtime_state_rejects_unsupported_schema_version() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        runtime_state(schema_version=2)


@pytest.mark.parametrize(
    "timestamp",
    [
        datetime(2026, 7, 27, 14, 0),
        datetime(
            2026,
            7,
            27,
            10,
            0,
            tzinfo=timezone(timedelta(hours=-4)),
        ),
    ],
)
def test_runtime_state_rejects_non_utc_start_timestamp(timestamp: datetime) -> None:
    with pytest.raises(ValueError, match="UTC|timezone-aware"):
        runtime_state(started_at_utc=timestamp)


@pytest.mark.parametrize(
    "timestamp",
    [
        datetime(2026, 7, 27, 14, 0),
        datetime(
            2026,
            7,
            27,
            10,
            0,
            tzinfo=timezone(timedelta(hours=-4)),
        ),
    ],
)
def test_runtime_state_rejects_non_utc_update_timestamp(timestamp: datetime) -> None:
    with pytest.raises(ValueError, match="UTC|timezone-aware"):
        runtime_state(updated_at_utc=timestamp)


def test_runtime_state_rejects_update_before_start() -> None:
    with pytest.raises(ValueError, match="must not precede"):
        runtime_state(
            started_at_utc=UPDATED,
            updated_at_utc=STARTED,
        )


@pytest.mark.parametrize(
    "execution_state",
    [ExecutionState.COMPLETED, ExecutionState.FAILED],
)
def test_running_runtime_state_rejects_terminal_execution_state(
    execution_state: ExecutionState,
) -> None:
    with pytest.raises(ValueError, match="nonterminal"):
        runtime_state(execution_state=execution_state)


@pytest.mark.parametrize(
    "execution_state",
    [
        ExecutionState.CREATED,
        ExecutionState.REPORT_GENERATION,
        ExecutionState.FAILED,
    ],
)
def test_completed_runtime_status_requires_completed_execution_state(
    execution_state: ExecutionState,
) -> None:
    with pytest.raises(ValueError, match="requires execution state COMPLETED"):
        runtime_state(
            status=RuntimeExecutionStatus.COMPLETED,
            execution_state=execution_state,
        )


@pytest.mark.parametrize(
    "execution_state",
    [
        ExecutionState.CREATED,
        ExecutionState.REPORT_GENERATION,
        ExecutionState.COMPLETED,
    ],
)
def test_failed_runtime_status_requires_failed_execution_state(
    execution_state: ExecutionState,
) -> None:
    with pytest.raises(ValueError, match="requires execution state FAILED"):
        runtime_state(
            status=RuntimeExecutionStatus.FAILED,
            execution_state=execution_state,
        )


@pytest.mark.parametrize(
    "execution_state",
    [ExecutionState.COMPLETED, ExecutionState.FAILED],
)
def test_interrupted_runtime_state_rejects_terminal_execution_state(
    execution_state: ExecutionState,
) -> None:
    with pytest.raises(ValueError, match="preserve a nonterminal"):
        runtime_state(
            status=RuntimeExecutionStatus.INTERRUPTED,
            execution_state=execution_state,
        )


def test_runtime_state_serializes_to_stable_json_compatible_mapping() -> None:
    state = runtime_state()

    assert state.to_dict() == {
        "schema_version": 1,
        "run_id": "job-20260727T140000Z",
        "status": "running",
        "execution_state": "repository_validation",
        "started_at_utc": "2026-07-27T14:00:00Z",
        "updated_at_utc": "2026-07-27T14:00:01Z",
        "pid": 1234,
        "hostname": "ai-lab",
        "environment": "development",
    }


def test_runtime_state_is_immutable() -> None:
    state = runtime_state()

    with pytest.raises(FrozenInstanceError):
        state.pid = 4321  # type: ignore[misc]


def test_runtime_models_are_exported_from_package() -> None:
    from poe_backup_orchestrator import models

    assert models.RUNTIME_STATE_SCHEMA_VERSION == 1
    assert models.RuntimeExecutionStatus is RuntimeExecutionStatus
    assert models.RuntimeState is RuntimeState
