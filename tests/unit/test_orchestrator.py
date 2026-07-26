"""Tests for successful and failed Registry backup orchestration."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest

from poe_backup_orchestrator.exceptions import (
    RegistryAcceptanceConflictError,
    RegistryAcceptanceError,
    RegistryAcceptanceInconsistentError,
    RegistryAcceptanceLockError,
    RegistryIngestionError,
    RepositoryValidationError,
    SqliteBackupError,
)
from poe_backup_orchestrator.models import (
    ExecutionOutcome,
    ExecutionState,
    FailureCategory,
    JobId,
    RegistryAcceptanceResult,
    RegistryBackupRequest,
    RegistryIngestionResult,
    RepositoryValidationResult,
    SqliteBackupResult,
)
from poe_backup_orchestrator.services import (
    ExecutionStateMachine,
    RegistryBackupOrchestrator,
)

STARTED = datetime(2026, 7, 26, 17, 0, tzinfo=UTC)
COMPLETED = STARTED + timedelta(seconds=2)
REQUEST = RegistryBackupRequest(
    source_path=Path("/source/registry.db"),
    job_id=JobId("job-slice-3e"),
    requested_at_utc=STARTED,
)


class SequenceClock:
    """Return supplied UTC values in order."""

    def __init__(self, *values: datetime) -> None:
        self._values = iter(values)

    def now_utc(self) -> datetime:
        return next(self._values)


class FixedJobIdGenerator:
    """Return a deterministic job identifier."""

    def __init__(self, job_id: JobId | None = None) -> None:
        if job_id is None:
            job_id = JobId("generated-job")

        self.job_id = job_id
        self.calls: list[datetime] = []

    def generate(self, now_utc: datetime) -> JobId:
        self.calls.append(now_utc)
        return self.job_id


class RepositoryService:
    def __init__(self, events, result, error=None) -> None:
        self.events = events
        self.result = result
        self.error = error

    def validate(self):
        self.events.append("repository")
        if self.error is not None:
            raise self.error
        return self.result


class AcquisitionService:
    def __init__(self, events, result, error=None) -> None:
        self.events = events
        self.result = result
        self.error = error

    def acquire(self):
        self.events.append("acquisition")
        if self.error is not None:
            raise self.error
        return self.result


class ValidationService:
    def __init__(self, events, result, error=None) -> None:
        self.events = events
        self.result = result
        self.error = error
        self.received = []

    def validate(self, acquisition):
        self.events.append("validation")
        self.received.append(acquisition)
        if self.error is not None:
            raise self.error
        return self.result


class AcceptanceService:
    def __init__(self, events, result, error=None) -> None:
        self.events = events
        self.result = result
        self.error = error
        self.received = []

    def accept(self, validation):
        self.events.append("acceptance")
        self.received.append(validation)
        if self.error is not None:
            raise self.error
        return self.result


def stage_results():
    return (
        cast(RepositoryValidationResult, object()),
        cast(SqliteBackupResult, object()),
        cast(RegistryIngestionResult, object()),
        cast(RegistryAcceptanceResult, object()),
    )


def orchestration_clock(*, failure: bool = False) -> SequenceClock:
    transition_count = 7 if not failure else 6
    transition_times = [
        STARTED + timedelta(milliseconds=index * 100) for index in range(transition_count)
    ]
    return SequenceClock(*transition_times, COMPLETED)


def build_orchestrator(
    *,
    events,
    repository_error=None,
    acquisition_error=None,
    validation_error=None,
    acceptance_error=None,
    clock=None,
    generator=None,
    machine_sink=None,
):
    repository, acquisition, validation, acceptance = stage_results()
    validation_service = ValidationService(
        events,
        validation,
        validation_error,
    )
    acceptance_service = AcceptanceService(
        events,
        acceptance,
        acceptance_error,
    )

    def state_machine_factory(supplied_clock):
        machine = ExecutionStateMachine(supplied_clock)
        if machine_sink is not None:
            machine_sink.append(machine)
        return machine

    orchestrator = RegistryBackupOrchestrator(
        repository_validation=RepositoryService(
            events,
            repository,
            repository_error,
        ),
        registry_acquisition=AcquisitionService(
            events,
            acquisition,
            acquisition_error,
        ),
        acquisition_validation=validation_service,
        registry_acceptance=acceptance_service,
        clock=clock or orchestration_clock(),
        job_id_generator=generator or FixedJobIdGenerator(),
        state_machine_factory=state_machine_factory,
    )
    return (
        orchestrator,
        repository,
        acquisition,
        validation,
        acceptance,
        validation_service,
        acceptance_service,
    )


def test_execute_coordinates_complete_success_path() -> None:
    events = []
    machines = []
    (
        orchestrator,
        repository,
        acquisition,
        validation,
        acceptance,
        validation_service,
        acceptance_service,
    ) = build_orchestrator(events=events, machine_sink=machines)

    result = orchestrator.execute(REQUEST)

    assert events == [
        "repository",
        "acquisition",
        "validation",
        "acceptance",
    ]
    assert validation_service.received == [acquisition]
    assert acceptance_service.received == [validation]
    assert result.job_id == REQUEST.job_id
    assert result.outcome is ExecutionOutcome.SUCCEEDED
    assert result.started_at_utc == STARTED
    assert result.completed_at_utc == COMPLETED
    assert result.duration_ms == 2000
    assert result.final_state is ExecutionState.COMPLETED
    assert result.repository is repository
    assert result.acquisition is acquisition
    assert result.validation is validation
    assert result.acceptance is acceptance
    assert result.failure is None
    assert tuple(item.new_state for item in machines[0].history) == (
        ExecutionState.LOCK_ACQUISITION,
        ExecutionState.REPOSITORY_VALIDATION,
        ExecutionState.REGISTRY_ACQUISITION,
        ExecutionState.ACQUISITION_VALIDATION,
        ExecutionState.REGISTRY_ACCEPTANCE,
        ExecutionState.REPORT_GENERATION,
        ExecutionState.COMPLETED,
    )


@pytest.mark.parametrize(
    (
        "error_field",
        "error",
        "expected_events",
        "failed_state",
        "category",
        "expected_components",
    ),
    [
        (
            "repository_error",
            RepositoryValidationError("repository unavailable"),
            ["repository"],
            ExecutionState.REPOSITORY_VALIDATION,
            FailureCategory.REPOSITORY_PRECONDITION,
            (False, False, False, False),
        ),
        (
            "acquisition_error",
            SqliteBackupError("acquisition failed"),
            ["repository", "acquisition"],
            ExecutionState.REGISTRY_ACQUISITION,
            FailureCategory.ACQUISITION,
            (True, False, False, False),
        ),
        (
            "validation_error",
            RegistryIngestionError("validation failed"),
            ["repository", "acquisition", "validation"],
            ExecutionState.ACQUISITION_VALIDATION,
            FailureCategory.VALIDATION,
            (True, True, False, False),
        ),
        (
            "acceptance_error",
            RegistryAcceptanceError("acceptance failed"),
            ["repository", "acquisition", "validation", "acceptance"],
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.ACCEPTANCE,
            (True, True, True, False),
        ),
        (
            "acceptance_error",
            RegistryAcceptanceLockError("lock unavailable"),
            ["repository", "acquisition", "validation", "acceptance"],
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.LOCK_UNAVAILABLE,
            (True, True, True, False),
        ),
        (
            "acceptance_error",
            RegistryAcceptanceConflictError("conflict"),
            ["repository", "acquisition", "validation", "acceptance"],
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.ACCEPTANCE_CONFLICT,
            (True, True, True, False),
        ),
        (
            "acceptance_error",
            RegistryAcceptanceInconsistentError("inconsistent"),
            ["repository", "acquisition", "validation", "acceptance"],
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.ACCEPTANCE,
            (True, True, True, False),
        ),
    ],
)
def test_execute_returns_typed_failed_result(
    error_field,
    error,
    expected_events,
    failed_state,
    category,
    expected_components,
) -> None:
    events = []
    machines = []
    kwargs = {error_field: error}
    orchestrator, *_ = build_orchestrator(
        events=events,
        machine_sink=machines,
        clock=orchestration_clock(failure=True),
        **kwargs,
    )

    result = orchestrator.execute(REQUEST)

    assert events == expected_events
    assert result.outcome is ExecutionOutcome.FAILED
    assert result.final_state is ExecutionState.FAILED
    assert result.failure is not None
    assert result.failure.category is category
    assert result.failure.failed_state is failed_state
    assert result.failure.error_type == type(error).__name__
    assert result.failure.message == str(error)
    assert result.failure.exit_code > 0
    assert result.completed_at_utc >= result.started_at_utc
    assert result.duration_ms >= 0
    components = (
        result.repository is not None,
        result.acquisition is not None,
        result.validation is not None,
        result.acceptance is not None,
    )
    assert components == expected_components
    assert machines[0].current_state is ExecutionState.FAILED
    assert machines[0].history[-1].new_state is ExecutionState.FAILED


def test_unknown_exception_propagates_unchanged() -> None:
    events = []
    expected = RuntimeError("programmer defect")
    orchestrator, *_ = build_orchestrator(
        events=events,
        repository_error=expected,
    )

    with pytest.raises(RuntimeError) as raised:
        orchestrator.execute(REQUEST)

    assert raised.value is expected
    assert events == ["repository"]


def test_state_machine_factory_failure_propagates_unchanged() -> None:
    events = []
    expected = RuntimeError("state machine unavailable")

    def failing_factory(clock):
        del clock
        raise expected

    repository, acquisition, validation, acceptance = stage_results()
    orchestrator = RegistryBackupOrchestrator(
        repository_validation=RepositoryService(events, repository),
        registry_acquisition=AcquisitionService(events, acquisition),
        acquisition_validation=ValidationService(events, validation),
        registry_acceptance=AcceptanceService(events, acceptance),
        clock=orchestration_clock(),
        job_id_generator=FixedJobIdGenerator(),
        state_machine_factory=cast(Callable, failing_factory),
    )

    with pytest.raises(RuntimeError) as raised:
        orchestrator.execute(REQUEST)

    assert raised.value is expected
    assert events == []
