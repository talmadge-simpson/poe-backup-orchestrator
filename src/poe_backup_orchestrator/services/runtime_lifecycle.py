"""Runtime-state lifecycle coordination for one orchestrated execution."""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from datetime import datetime

from poe_backup_orchestrator.exceptions import RuntimeStateOwnershipError
from poe_backup_orchestrator.models import (
    RUNTIME_STATE_SCHEMA_VERSION,
    ExecutionState,
    JobId,
    RuntimeEnvironment,
    RuntimeExecutionStatus,
    RuntimeState,
)
from poe_backup_orchestrator.services.runtime_recovery import (
    HostIdentity,
    RuntimeRecoveryInspector,
    RuntimeRecoveryOutcome,
    UtcClock,
)
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore


@dataclass(slots=True)
class RuntimeLifecycleCoordinator:
    """Persist runtime ownership and every accepted execution transition."""

    store: RuntimeStateStore
    recovery_inspector: RuntimeRecoveryInspector
    host_identity: HostIdentity
    clock: UtcClock
    environment: RuntimeEnvironment
    pid: int = os.getpid()
    _state: RuntimeState | None = None

    @property
    def current_state(self) -> RuntimeState | None:
        """Return the most recently persisted state for this execution."""

        return self._state

    def start(self, job_id: JobId, started_at_utc: datetime) -> RuntimeState:
        """Inspect prior ownership and publish the new CREATED runtime record."""

        inspection = self.recovery_inspector.inspect()
        if inspection.outcome is RuntimeRecoveryOutcome.ACTIVE_EXECUTION:
            raise RuntimeStateOwnershipError(
                "An active Backup Orchestrator execution already owns runtime state"
                + _owner_suffix(inspection.state)
            )
        if inspection.outcome is RuntimeRecoveryOutcome.AMBIGUOUS_OWNERSHIP:
            raise RuntimeStateOwnershipError(
                "Runtime-state ownership belongs to a different host"
                + _owner_suffix(inspection.state)
            )

        hostname = self.host_identity.hostname().strip()
        if not hostname:
            raise ValueError("current hostname must not be blank")
        if self.pid <= 0:
            raise ValueError("pid must be greater than zero")

        state = RuntimeState(
            schema_version=RUNTIME_STATE_SCHEMA_VERSION,
            run_id=str(job_id),
            status=RuntimeExecutionStatus.RUNNING,
            execution_state=ExecutionState.CREATED,
            started_at_utc=started_at_utc,
            updated_at_utc=started_at_utc,
            pid=self.pid,
            hostname=hostname,
            environment=self.environment,
        )
        self.store.save(state)
        self._state = state
        return state

    def transition_to(self, execution_state: ExecutionState) -> RuntimeState:
        """Persist one state-machine-approved execution transition."""

        current = self._require_started()
        updated = replace(
            current,
            status=_status_for(execution_state),
            execution_state=execution_state,
            updated_at_utc=self.clock.now_utc(),
        )
        self.store.save(updated)
        self._state = updated
        return updated

    def _require_started(self) -> RuntimeState:
        if self._state is None:
            raise RuntimeError("runtime lifecycle has not been started")
        return self._state


def _status_for(execution_state: ExecutionState) -> RuntimeExecutionStatus:
    if execution_state is ExecutionState.COMPLETED:
        return RuntimeExecutionStatus.COMPLETED
    if execution_state is ExecutionState.FAILED:
        return RuntimeExecutionStatus.FAILED
    return RuntimeExecutionStatus.RUNNING


def _owner_suffix(state: RuntimeState | None) -> str:
    if state is None:
        return ""
    return (
        f": run_id={state.run_id}, hostname={state.hostname}, "
        f"pid={state.pid}, execution_state={state.execution_state.value}"
    )
