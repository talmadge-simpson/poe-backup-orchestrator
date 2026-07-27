"""Deterministic inspection and classification of persisted runtime state."""

from __future__ import annotations

import errno
import os
import socket
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from poe_backup_orchestrator.models.runtime import RuntimeExecutionStatus, RuntimeState
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore


class RuntimeRecoveryOutcome(StrEnum):
    """Stable outcomes produced by runtime-state recovery inspection."""

    NO_STATE = "no_state"
    TERMINAL_STATE = "terminal_state"
    ACTIVE_EXECUTION = "active_execution"
    INTERRUPTED_EXECUTION = "interrupted_execution"
    AMBIGUOUS_OWNERSHIP = "ambiguous_ownership"


class HostIdentity(Protocol):
    def hostname(self) -> str: ...


class ProcessLiveness(Protocol):
    def is_alive(self, pid: int) -> bool: ...


class UtcClock(Protocol):
    def now_utc(self) -> datetime: ...


@dataclass(frozen=True, slots=True)
class RuntimeRecoveryInspection:
    """Immutable result of inspecting persisted runtime ownership."""

    outcome: RuntimeRecoveryOutcome
    state: RuntimeState | None
    state_changed: bool = False


@dataclass(frozen=True, slots=True)
class SystemHostIdentity:
    def hostname(self) -> str:
        return socket.gethostname()


@dataclass(frozen=True, slots=True)
class SystemProcessLiveness:
    def is_alive(self, pid: int) -> bool:
        if pid <= 0:
            raise ValueError("pid must be greater than zero")
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        except OSError as exc:
            if exc.errno == errno.ESRCH:
                return False
            if exc.errno == errno.EPERM:
                return True
            raise
        return True


@dataclass(frozen=True, slots=True)
class RuntimeRecoveryInspector:
    """Inspect and conservatively classify the authoritative runtime state."""

    store: RuntimeStateStore
    host_identity: HostIdentity
    process_liveness: ProcessLiveness
    clock: UtcClock

    def inspect(self) -> RuntimeRecoveryInspection:
        state = self.store.load()
        if state is None:
            return RuntimeRecoveryInspection(RuntimeRecoveryOutcome.NO_STATE, None)

        if state.status is not RuntimeExecutionStatus.RUNNING:
            return RuntimeRecoveryInspection(RuntimeRecoveryOutcome.TERMINAL_STATE, state)

        current_hostname = self.host_identity.hostname().strip()
        if not current_hostname:
            raise ValueError("current hostname must not be blank")

        if state.hostname != current_hostname:
            return RuntimeRecoveryInspection(
                RuntimeRecoveryOutcome.AMBIGUOUS_OWNERSHIP,
                state,
            )

        if self.process_liveness.is_alive(state.pid):
            return RuntimeRecoveryInspection(
                RuntimeRecoveryOutcome.ACTIVE_EXECUTION,
                state,
            )

        interrupted = replace(
            state,
            status=RuntimeExecutionStatus.INTERRUPTED,
            updated_at_utc=self.clock.now_utc(),
        )
        self.store.save(interrupted)
        return RuntimeRecoveryInspection(
            RuntimeRecoveryOutcome.INTERRUPTED_EXECUTION,
            interrupted,
            state_changed=True,
        )
