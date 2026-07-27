"""Tests for deterministic runtime-state recovery inspection."""

from __future__ import annotations

import errno
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.execution import ExecutionState
from poe_backup_orchestrator.models.runtime import (
    RUNTIME_STATE_SCHEMA_VERSION,
    RuntimeEnvironment,
    RuntimeExecutionStatus,
    RuntimeState,
)
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspector,
    RuntimeRecoveryOutcome,
    SystemHostIdentity,
    SystemProcessLiveness,
)
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore

STARTED = datetime(2026, 7, 27, 15, 0, tzinfo=UTC)
UPDATED = datetime(2026, 7, 27, 15, 5, tzinfo=UTC)
INSPECTED = datetime(2026, 7, 27, 15, 10, tzinfo=UTC)


@dataclass(frozen=True)
class FixedHost:
    value: str

    def hostname(self) -> str:
        return self.value


@dataclass(frozen=True)
class FixedProcess:
    alive: bool

    def is_alive(self, pid: int) -> bool:
        assert pid == 4321
        return self.alive


@dataclass(frozen=True)
class FixedClock:
    value: datetime

    def now_utc(self) -> datetime:
        return self.value


def runtime_state(
    *,
    status: RuntimeExecutionStatus = RuntimeExecutionStatus.RUNNING,
    execution_state: ExecutionState = ExecutionState.REPOSITORY_VALIDATION,
    hostname: str = "ai-lab",
) -> RuntimeState:
    return RuntimeState(
        schema_version=RUNTIME_STATE_SCHEMA_VERSION,
        run_id="job-recovery",
        status=status,
        execution_state=execution_state,
        started_at_utc=STARTED,
        updated_at_utc=UPDATED,
        pid=4321,
        hostname=hostname,
        environment=RuntimeEnvironment.DEVELOPMENT,
    )


def inspector(
    store: RuntimeStateStore,
    *,
    hostname: str = "ai-lab",
    alive: bool = True,
) -> RuntimeRecoveryInspector:
    return RuntimeRecoveryInspector(
        store=store,
        host_identity=FixedHost(hostname),
        process_liveness=FixedProcess(alive),
        clock=FixedClock(INSPECTED),
    )


def test_no_state_returns_no_state(tmp_path: Path) -> None:
    result = inspector(RuntimeStateStore(tmp_path)).inspect()
    assert result.outcome is RuntimeRecoveryOutcome.NO_STATE
    assert result.state is None
    assert not result.state_changed


@pytest.mark.parametrize(
    ("status", "execution_state"),
    [
        (RuntimeExecutionStatus.COMPLETED, ExecutionState.COMPLETED),
        (RuntimeExecutionStatus.FAILED, ExecutionState.FAILED),
        (RuntimeExecutionStatus.INTERRUPTED, ExecutionState.REPOSITORY_VALIDATION),
    ],
)
def test_terminal_state_is_observable_without_mutation(
    tmp_path: Path,
    status: RuntimeExecutionStatus,
    execution_state: ExecutionState,
) -> None:
    store = RuntimeStateStore(tmp_path)
    expected = runtime_state(status=status, execution_state=execution_state)
    store.save(expected)
    result = inspector(store, alive=False).inspect()
    assert result.outcome is RuntimeRecoveryOutcome.TERMINAL_STATE
    assert result.state == expected
    assert not result.state_changed
    assert store.load() == expected


def test_same_host_live_pid_is_active(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    expected = runtime_state()
    store.save(expected)
    result = inspector(store, alive=True).inspect()
    assert result.outcome is RuntimeRecoveryOutcome.ACTIVE_EXECUTION
    assert result.state == expected
    assert not result.state_changed


def test_different_host_is_ambiguous_and_not_mutated(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    expected = runtime_state(hostname="other-host")
    store.save(expected)
    result = inspector(store, hostname="ai-lab", alive=False).inspect()
    assert result.outcome is RuntimeRecoveryOutcome.AMBIGUOUS_OWNERSHIP
    assert result.state == expected
    assert not result.state_changed
    assert store.load() == expected


def test_dead_same_host_owner_is_persisted_as_interrupted(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    original = runtime_state()
    store.save(original)
    result = inspector(store, alive=False).inspect()
    assert result.outcome is RuntimeRecoveryOutcome.INTERRUPTED_EXECUTION
    assert result.state is not None
    assert result.state.status is RuntimeExecutionStatus.INTERRUPTED
    assert result.state.execution_state is original.execution_state
    assert result.state.started_at_utc == original.started_at_utc
    assert result.state.updated_at_utc == INSPECTED
    assert result.state_changed
    assert store.load() == result.state


def test_blank_current_hostname_is_rejected(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    store.save(runtime_state())
    with pytest.raises(ValueError, match="hostname"):
        inspector(store, hostname=" ", alive=False).inspect()


def test_reinspection_of_interrupted_state_is_terminal(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    store.save(runtime_state())
    first = inspector(store, alive=False).inspect()
    second = inspector(store, alive=True).inspect()
    assert first.outcome is RuntimeRecoveryOutcome.INTERRUPTED_EXECUTION
    assert second.outcome is RuntimeRecoveryOutcome.TERMINAL_STATE
    assert second.state == first.state


def test_system_host_identity_returns_nonblank_hostname() -> None:
    assert SystemHostIdentity().hostname().strip()


def test_system_process_liveness_rejects_nonpositive_pid() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        SystemProcessLiveness().is_alive(0)


def test_system_process_liveness_reports_current_process_alive() -> None:
    assert SystemProcessLiveness().is_alive(os.getpid())


def test_system_process_liveness_maps_missing_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_process(pid: int, signal: int) -> None:
        raise ProcessLookupError(errno.ESRCH, "missing")

    monkeypatch.setattr(os, "kill", missing_process)
    assert not SystemProcessLiveness().is_alive(4321)


def test_system_process_liveness_treats_permission_denial_as_alive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def denied_process(pid: int, signal: int) -> None:
        raise PermissionError(errno.EPERM, "denied")

    monkeypatch.setattr(os, "kill", denied_process)
    assert SystemProcessLiveness().is_alive(4321)


def test_system_process_liveness_propagates_unexpected_os_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected(pid: int, signal: int) -> None:
        raise OSError(errno.EIO, "unexpected")

    monkeypatch.setattr(os, "kill", unexpected)
    with pytest.raises(OSError, match="unexpected"):
        SystemProcessLiveness().is_alive(4321)


def test_service_exports_recovery_contract() -> None:
    from poe_backup_orchestrator import services

    assert services.RuntimeRecoveryInspector is RuntimeRecoveryInspector
    assert services.RuntimeRecoveryOutcome is RuntimeRecoveryOutcome
    assert services.SystemHostIdentity is SystemHostIdentity
    assert services.SystemProcessLiveness is SystemProcessLiveness
