"""Tests for orchestration runtime-state lifecycle persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from poe_backup_orchestrator.exceptions import RuntimeStateOwnershipError
from poe_backup_orchestrator.models import (
    ExecutionState,
    JobId,
    RuntimeEnvironment,
    RuntimeExecutionStatus,
)
from poe_backup_orchestrator.services.runtime_lifecycle import (
    RuntimeLifecycleCoordinator,
)
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspection,
    RuntimeRecoveryOutcome,
)
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore

STARTED = datetime(2026, 7, 27, 16, 0, tzinfo=UTC)
LOCKED = STARTED + timedelta(seconds=1)
COMPLETED = STARTED + timedelta(seconds=2)


@dataclass
class StubRecoveryInspector:
    inspection: RuntimeRecoveryInspection
    calls: int = 0

    def inspect(self) -> RuntimeRecoveryInspection:
        self.calls += 1
        return self.inspection


@dataclass(frozen=True)
class FixedHost:
    value: str = "ai-lab"

    def hostname(self) -> str:
        return self.value


class SequenceClock:
    def __init__(self, *values: datetime) -> None:
        self._values = iter(values)

    def now_utc(self) -> datetime:
        return next(self._values)


def coordinator(
    tmp_path: Path,
    *,
    outcome: RuntimeRecoveryOutcome = RuntimeRecoveryOutcome.NO_STATE,
    clock: SequenceClock | None = None,
) -> tuple[RuntimeLifecycleCoordinator, RuntimeStateStore, StubRecoveryInspector]:
    store = RuntimeStateStore(tmp_path)
    recovery = StubRecoveryInspector(RuntimeRecoveryInspection(outcome, None))
    lifecycle = RuntimeLifecycleCoordinator(
        store=store,
        recovery_inspector=recovery,  # type: ignore[arg-type]
        host_identity=FixedHost(),
        clock=clock or SequenceClock(LOCKED, COMPLETED),
        environment=RuntimeEnvironment.DEVELOPMENT,
        pid=4321,
    )
    return lifecycle, store, recovery


@pytest.mark.parametrize(
    "outcome",
    [
        RuntimeRecoveryOutcome.NO_STATE,
        RuntimeRecoveryOutcome.TERMINAL_STATE,
        RuntimeRecoveryOutcome.INTERRUPTED_EXECUTION,
    ],
)
def test_start_publishes_created_running_state(
    tmp_path: Path,
    outcome: RuntimeRecoveryOutcome,
) -> None:
    lifecycle, store, recovery = coordinator(tmp_path, outcome=outcome)

    state = lifecycle.start(JobId("job-lifecycle"), STARTED)

    assert recovery.calls == 1
    assert state.status is RuntimeExecutionStatus.RUNNING
    assert state.execution_state is ExecutionState.CREATED
    assert state.run_id == "job-lifecycle"
    assert state.started_at_utc == STARTED
    assert state.updated_at_utc == STARTED
    assert state.pid == 4321
    assert state.hostname == "ai-lab"
    assert state.environment is RuntimeEnvironment.DEVELOPMENT
    assert store.load() == state
    assert lifecycle.current_state == state


@pytest.mark.parametrize(
    "outcome",
    [
        RuntimeRecoveryOutcome.ACTIVE_EXECUTION,
        RuntimeRecoveryOutcome.AMBIGUOUS_OWNERSHIP,
    ],
)
def test_start_blocks_unsafe_ownership(
    tmp_path: Path,
    outcome: RuntimeRecoveryOutcome,
) -> None:
    lifecycle, store, _ = coordinator(tmp_path, outcome=outcome)

    with pytest.raises(RuntimeStateOwnershipError):
        lifecycle.start(JobId("job-blocked"), STARTED)

    assert store.load() is None
    assert lifecycle.current_state is None


def test_transition_persists_each_accepted_state(tmp_path: Path) -> None:
    lifecycle, store, _ = coordinator(tmp_path)
    lifecycle.start(JobId("job-lifecycle"), STARTED)

    locked = lifecycle.transition_to(ExecutionState.LOCK_ACQUISITION)
    completed = lifecycle.transition_to(ExecutionState.COMPLETED)

    assert locked.status is RuntimeExecutionStatus.RUNNING
    assert locked.execution_state is ExecutionState.LOCK_ACQUISITION
    assert locked.updated_at_utc == LOCKED
    assert completed.status is RuntimeExecutionStatus.COMPLETED
    assert completed.execution_state is ExecutionState.COMPLETED
    assert completed.updated_at_utc == COMPLETED
    assert store.load() == completed


def test_failed_transition_persists_failed_terminal_state(tmp_path: Path) -> None:
    lifecycle, store, _ = coordinator(tmp_path, clock=SequenceClock(LOCKED))
    lifecycle.start(JobId("job-lifecycle"), STARTED)

    failed = lifecycle.transition_to(ExecutionState.FAILED)

    assert failed.status is RuntimeExecutionStatus.FAILED
    assert failed.execution_state is ExecutionState.FAILED
    assert store.load() == failed


def test_transition_requires_started_lifecycle(tmp_path: Path) -> None:
    lifecycle, _, _ = coordinator(tmp_path)

    with pytest.raises(RuntimeError, match="not been started"):
        lifecycle.transition_to(ExecutionState.LOCK_ACQUISITION)


def test_service_exports_runtime_lifecycle() -> None:
    from poe_backup_orchestrator import services

    assert services.RuntimeLifecycleCoordinator is RuntimeLifecycleCoordinator
