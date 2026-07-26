"""Deterministic lifecycle state machine for Registry backup execution."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Final

from poe_backup_orchestrator.models import Clock, ExecutionState
from poe_backup_orchestrator.models.job import require_utc


@dataclass(frozen=True, slots=True)
class ExecutionTransition:
    """One accepted transition between orchestration lifecycle states."""

    previous_state: ExecutionState
    new_state: ExecutionState
    occurred_at_utc: datetime

    def __post_init__(self) -> None:
        require_utc(self.occurred_at_utc, field_name="occurred_at_utc")


class InvalidExecutionTransitionError(ValueError):
    """Raised when an execution lifecycle transition is not permitted."""

    def __init__(
        self,
        previous_state: ExecutionState,
        requested_state: ExecutionState,
    ) -> None:
        self.previous_state = previous_state
        self.requested_state = requested_state
        super().__init__(
            f"invalid execution transition: {previous_state.value} -> {requested_state.value}"
        )


_SUCCESS_TRANSITIONS: Final[dict[ExecutionState, ExecutionState]] = {
    ExecutionState.CREATED: ExecutionState.LOCK_ACQUISITION,
    ExecutionState.LOCK_ACQUISITION: ExecutionState.REPOSITORY_VALIDATION,
    ExecutionState.REPOSITORY_VALIDATION: ExecutionState.REGISTRY_ACQUISITION,
    ExecutionState.REGISTRY_ACQUISITION: ExecutionState.ACQUISITION_VALIDATION,
    ExecutionState.ACQUISITION_VALIDATION: ExecutionState.REGISTRY_ACCEPTANCE,
    ExecutionState.REGISTRY_ACCEPTANCE: ExecutionState.REPORT_GENERATION,
    ExecutionState.REPORT_GENERATION: ExecutionState.COMPLETED,
}

SUCCESS_TRANSITIONS: Final[Mapping[ExecutionState, ExecutionState]] = MappingProxyType(
    _SUCCESS_TRANSITIONS
)

_TERMINAL_STATES: Final[frozenset[ExecutionState]] = frozenset(
    {
        ExecutionState.COMPLETED,
        ExecutionState.FAILED,
    }
)


class ExecutionStateMachine:
    """Authoritative execution lifecycle controller."""

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._current_state = ExecutionState.CREATED
        self._history: list[ExecutionTransition] = []

    @property
    def current_state(self) -> ExecutionState:
        """Return the current lifecycle state."""

        return self._current_state

    @property
    def history(self) -> tuple[ExecutionTransition, ...]:
        """Return an immutable snapshot of accepted transitions."""

        return tuple(self._history)

    def can_transition_to(self, state: ExecutionState) -> bool:
        """Return whether the requested transition is currently legal."""

        if self._current_state in _TERMINAL_STATES:
            return False

        if state is ExecutionState.FAILED:
            return True

        return SUCCESS_TRANSITIONS.get(self._current_state) is state

    def transition_to(self, state: ExecutionState) -> ExecutionTransition:
        """Apply and record a legal lifecycle transition."""

        previous_state = self._current_state

        if not self.can_transition_to(state):
            raise InvalidExecutionTransitionError(previous_state, state)

        occurred_at_utc = self._clock.now_utc()
        require_utc(occurred_at_utc, field_name="clock.now_utc()")

        transition = ExecutionTransition(
            previous_state=previous_state,
            new_state=state,
            occurred_at_utc=occurred_at_utc,
        )

        self._current_state = state
        self._history.append(transition)
        return transition
