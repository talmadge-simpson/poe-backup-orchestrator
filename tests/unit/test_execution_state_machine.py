"""Tests for the orchestration execution state machine."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from poe_backup_orchestrator.models import ExecutionState
from poe_backup_orchestrator.services.execution_state_machine import (
    ExecutionStateMachine,
    ExecutionTransition,
    InvalidExecutionTransitionError,
)

NOW = datetime(2026, 7, 26, 15, 0, tzinfo=UTC)


class FixedClock:
    """Clock returning one deterministic timestamp."""

    def __init__(self, now: datetime = NOW) -> None:
        self._now = now

    def now_utc(self) -> datetime:
        return self._now


class AdvancingClock:
    """Clock advancing by one second on each call."""

    def __init__(self, now: datetime = NOW) -> None:
        self._now = now

    def now_utc(self) -> datetime:
        current = self._now
        self._now += timedelta(seconds=1)
        return current


SUCCESSFUL_LIFECYCLE = (
    ExecutionState.LOCK_ACQUISITION,
    ExecutionState.REPOSITORY_VALIDATION,
    ExecutionState.REGISTRY_ACQUISITION,
    ExecutionState.ACQUISITION_VALIDATION,
    ExecutionState.REGISTRY_ACCEPTANCE,
    ExecutionState.REPORT_GENERATION,
    ExecutionState.COMPLETED,
)

NONTERMINAL_STATES = (
    ExecutionState.CREATED,
    ExecutionState.LOCK_ACQUISITION,
    ExecutionState.REPOSITORY_VALIDATION,
    ExecutionState.REGISTRY_ACQUISITION,
    ExecutionState.ACQUISITION_VALIDATION,
    ExecutionState.REGISTRY_ACCEPTANCE,
    ExecutionState.REPORT_GENERATION,
)


def machine_at(state: ExecutionState) -> ExecutionStateMachine:
    machine = ExecutionStateMachine(FixedClock())
    for next_state in SUCCESSFUL_LIFECYCLE:
        if machine.current_state is state:
            break
        machine.transition_to(next_state)
    assert machine.current_state is state
    return machine


def test_new_state_machine_starts_created_with_empty_history() -> None:
    machine = ExecutionStateMachine(FixedClock())

    assert machine.current_state is ExecutionState.CREATED
    assert machine.history == ()


@pytest.mark.parametrize(
    ("previous_state", "next_state"),
    [
        (ExecutionState.CREATED, ExecutionState.LOCK_ACQUISITION),
        (
            ExecutionState.LOCK_ACQUISITION,
            ExecutionState.REPOSITORY_VALIDATION,
        ),
        (
            ExecutionState.REPOSITORY_VALIDATION,
            ExecutionState.REGISTRY_ACQUISITION,
        ),
        (
            ExecutionState.REGISTRY_ACQUISITION,
            ExecutionState.ACQUISITION_VALIDATION,
        ),
        (
            ExecutionState.ACQUISITION_VALIDATION,
            ExecutionState.REGISTRY_ACCEPTANCE,
        ),
        (
            ExecutionState.REGISTRY_ACCEPTANCE,
            ExecutionState.REPORT_GENERATION,
        ),
        (
            ExecutionState.REPORT_GENERATION,
            ExecutionState.COMPLETED,
        ),
    ],
)
def test_each_success_transition_is_legal(
    previous_state: ExecutionState,
    next_state: ExecutionState,
) -> None:
    machine = machine_at(previous_state)

    assert machine.can_transition_to(next_state)

    transition = machine.transition_to(next_state)

    assert transition.previous_state is previous_state
    assert transition.new_state is next_state
    assert transition.occurred_at_utc == NOW
    assert machine.current_state is next_state


def test_complete_successful_lifecycle_records_ordered_history() -> None:
    machine = ExecutionStateMachine(AdvancingClock())

    transitions = [machine.transition_to(state) for state in SUCCESSFUL_LIFECYCLE]

    assert machine.current_state is ExecutionState.COMPLETED
    assert tuple(item.new_state for item in transitions) == SUCCESSFUL_LIFECYCLE
    assert machine.history == tuple(transitions)
    assert tuple(item.occurred_at_utc for item in transitions) == tuple(
        NOW + timedelta(seconds=index) for index in range(len(SUCCESSFUL_LIFECYCLE))
    )


@pytest.mark.parametrize("state", NONTERMINAL_STATES)
def test_failure_is_legal_from_every_nonterminal_state(
    state: ExecutionState,
) -> None:
    machine = machine_at(state)

    assert machine.can_transition_to(ExecutionState.FAILED)

    transition = machine.transition_to(ExecutionState.FAILED)

    assert transition.previous_state is state
    assert transition.new_state is ExecutionState.FAILED
    assert machine.current_state is ExecutionState.FAILED


@pytest.mark.parametrize(
    ("current_state", "requested_state"),
    [
        (ExecutionState.CREATED, ExecutionState.REPOSITORY_VALIDATION),
        (
            ExecutionState.LOCK_ACQUISITION,
            ExecutionState.REGISTRY_ACQUISITION,
        ),
        (
            ExecutionState.REPOSITORY_VALIDATION,
            ExecutionState.ACQUISITION_VALIDATION,
        ),
        (
            ExecutionState.REGISTRY_ACQUISITION,
            ExecutionState.REGISTRY_ACCEPTANCE,
        ),
        (
            ExecutionState.ACQUISITION_VALIDATION,
            ExecutionState.REPORT_GENERATION,
        ),
        (
            ExecutionState.REGISTRY_ACCEPTANCE,
            ExecutionState.COMPLETED,
        ),
    ],
)
def test_skipped_stages_are_rejected(
    current_state: ExecutionState,
    requested_state: ExecutionState,
) -> None:
    machine = machine_at(current_state)
    prior_history = machine.history

    with pytest.raises(InvalidExecutionTransitionError) as raised:
        machine.transition_to(requested_state)

    assert raised.value.previous_state is current_state
    assert raised.value.requested_state is requested_state
    assert machine.current_state is current_state
    assert machine.history == prior_history


@pytest.mark.parametrize("state", NONTERMINAL_STATES)
def test_self_transitions_are_rejected(state: ExecutionState) -> None:
    machine = machine_at(state)
    prior_history = machine.history

    assert not machine.can_transition_to(state)

    with pytest.raises(InvalidExecutionTransitionError):
        machine.transition_to(state)

    assert machine.current_state is state
    assert machine.history == prior_history


def test_backward_transition_is_rejected() -> None:
    machine = machine_at(ExecutionState.REGISTRY_ACQUISITION)
    prior_history = machine.history

    with pytest.raises(InvalidExecutionTransitionError):
        machine.transition_to(ExecutionState.REPOSITORY_VALIDATION)

    assert machine.current_state is ExecutionState.REGISTRY_ACQUISITION
    assert machine.history == prior_history


@pytest.mark.parametrize(
    ("terminal_state", "requested_state"),
    [
        (ExecutionState.COMPLETED, ExecutionState.FAILED),
        (ExecutionState.COMPLETED, ExecutionState.COMPLETED),
        (ExecutionState.FAILED, ExecutionState.COMPLETED),
        (ExecutionState.FAILED, ExecutionState.FAILED),
    ],
)
def test_terminal_states_reject_all_transitions(
    terminal_state: ExecutionState,
    requested_state: ExecutionState,
) -> None:
    if terminal_state is ExecutionState.COMPLETED:
        machine = machine_at(ExecutionState.COMPLETED)
    else:
        machine = ExecutionStateMachine(FixedClock())
        machine.transition_to(ExecutionState.FAILED)

    prior_history = machine.history

    assert not machine.can_transition_to(requested_state)

    with pytest.raises(InvalidExecutionTransitionError):
        machine.transition_to(requested_state)

    assert machine.current_state is terminal_state
    assert machine.history == prior_history


def test_transition_is_immutable() -> None:
    transition = ExecutionTransition(
        previous_state=ExecutionState.CREATED,
        new_state=ExecutionState.LOCK_ACQUISITION,
        occurred_at_utc=NOW,
    )

    with pytest.raises(FrozenInstanceError):
        transition.new_state = ExecutionState.FAILED  # type: ignore[misc]


def test_history_is_an_immutable_snapshot() -> None:
    machine = ExecutionStateMachine(FixedClock())
    first_snapshot = machine.history

    machine.transition_to(ExecutionState.LOCK_ACQUISITION)
    second_snapshot = machine.history

    assert first_snapshot == ()
    assert len(second_snapshot) == 1
    assert isinstance(second_snapshot, tuple)


def test_transition_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ExecutionTransition(
            previous_state=ExecutionState.CREATED,
            new_state=ExecutionState.LOCK_ACQUISITION,
            occurred_at_utc=datetime(2026, 7, 26, 15, 0),
        )


def test_transition_rejects_non_utc_timestamp() -> None:
    non_utc = datetime(
        2026,
        7,
        26,
        11,
        0,
        tzinfo=timezone(timedelta(hours=-4)),
    )

    with pytest.raises(ValueError, match="normalized to UTC"):
        ExecutionTransition(
            previous_state=ExecutionState.CREATED,
            new_state=ExecutionState.LOCK_ACQUISITION,
            occurred_at_utc=non_utc,
        )


def test_state_machine_rejects_non_utc_clock_value_without_mutation() -> None:
    non_utc = datetime(
        2026,
        7,
        26,
        11,
        0,
        tzinfo=timezone(timedelta(hours=-4)),
    )
    machine = ExecutionStateMachine(FixedClock(non_utc))

    with pytest.raises(ValueError, match="normalized to UTC"):
        machine.transition_to(ExecutionState.LOCK_ACQUISITION)

    assert machine.current_state is ExecutionState.CREATED
    assert machine.history == ()
