"""Tests for the Registry backup orchestrator skeleton."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest

from poe_backup_orchestrator.models import (
    ExecutionOutcome,
    ExecutionState,
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
    job_id=JobId("job-slice-3d"),
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
    """Record repository validation calls."""

    def __init__(
        self,
        events: list[str],
        result: RepositoryValidationResult,
        error: Exception | None = None,
    ) -> None:
        self.events = events
        self.result = result
        self.error = error

    def validate(self) -> RepositoryValidationResult:
        self.events.append("repository")
        if self.error is not None:
            raise self.error
        return self.result


class AcquisitionService:
    """Record Registry acquisition calls."""

    def __init__(
        self,
        events: list[str],
        result: SqliteBackupResult,
        error: Exception | None = None,
    ) -> None:
        self.events = events
        self.result = result
        self.error = error

    def acquire(self) -> SqliteBackupResult:
        self.events.append("acquisition")
        if self.error is not None:
            raise self.error
        return self.result


class ValidationService:
    """Record acquisition validation calls and inputs."""

    def __init__(
        self,
        events: list[str],
        result: RegistryIngestionResult,
        error: Exception | None = None,
    ) -> None:
        self.events = events
        self.result = result
        self.error = error
        self.received: list[SqliteBackupResult] = []

    def validate(
        self,
        acquisition: SqliteBackupResult,
    ) -> RegistryIngestionResult:
        self.events.append("validation")
        self.received.append(acquisition)
        if self.error is not None:
            raise self.error
        return self.result


class AcceptanceService:
    """Record Registry acceptance calls and inputs."""

    def __init__(
        self,
        events: list[str],
        result: RegistryAcceptanceResult,
        error: Exception | None = None,
    ) -> None:
        self.events = events
        self.result = result
        self.error = error
        self.received: list[RegistryIngestionResult] = []

    def accept(
        self,
        validation: RegistryIngestionResult,
    ) -> RegistryAcceptanceResult:
        self.events.append("acceptance")
        self.received.append(validation)
        if self.error is not None:
            raise self.error
        return self.result


def stage_results() -> tuple[
    RepositoryValidationResult,
    SqliteBackupResult,
    RegistryIngestionResult,
    RegistryAcceptanceResult,
]:
    return (
        cast(RepositoryValidationResult, object()),
        cast(SqliteBackupResult, object()),
        cast(RegistryIngestionResult, object()),
        cast(RegistryAcceptanceResult, object()),
    )


def orchestration_clock() -> SequenceClock:
    transition_times = [STARTED + timedelta(milliseconds=index * 100) for index in range(7)]
    return SequenceClock(*transition_times, COMPLETED)


def build_orchestrator(
    *,
    events: list[str],
    repository_error: Exception | None = None,
    acquisition_error: Exception | None = None,
    validation_error: Exception | None = None,
    acceptance_error: Exception | None = None,
    clock: SequenceClock | None = None,
    generator: FixedJobIdGenerator | None = None,
    machine_sink: list[ExecutionStateMachine] | None = None,
) -> tuple[
    RegistryBackupOrchestrator,
    RepositoryValidationResult,
    SqliteBackupResult,
    RegistryIngestionResult,
    RegistryAcceptanceResult,
    ValidationService,
    AcceptanceService,
]:
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

    def state_machine_factory(
        supplied_clock,
    ) -> ExecutionStateMachine:
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
    events: list[str] = []
    machines: list[ExecutionStateMachine] = []
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
    assert len(machines) == 1
    assert tuple(item.new_state for item in machines[0].history) == (
        ExecutionState.LOCK_ACQUISITION,
        ExecutionState.REPOSITORY_VALIDATION,
        ExecutionState.REGISTRY_ACQUISITION,
        ExecutionState.ACQUISITION_VALIDATION,
        ExecutionState.REGISTRY_ACCEPTANCE,
        ExecutionState.REPORT_GENERATION,
        ExecutionState.COMPLETED,
    )


def test_execute_generates_job_id_when_request_omits_one() -> None:
    events: list[str] = []
    generator = FixedJobIdGenerator(JobId("generated-slice-3d"))
    request = RegistryBackupRequest(
        source_path=Path("/source/registry.db"),
        requested_at_utc=STARTED,
    )
    orchestrator, *_ = build_orchestrator(
        events=events,
        generator=generator,
    )

    result = orchestrator.execute(request)

    assert result.job_id == JobId("generated-slice-3d")
    assert generator.calls == [STARTED]


def test_execute_uses_clock_for_start_when_request_omits_timestamp() -> None:
    events: list[str] = []
    transition_times = [STARTED + timedelta(milliseconds=index * 100) for index in range(7)]
    clock = SequenceClock(STARTED, *transition_times, COMPLETED)
    generator = FixedJobIdGenerator()
    request = RegistryBackupRequest(
        source_path=Path("/source/registry.db"),
        job_id=JobId("job-clock-start"),
    )
    orchestrator, *_ = build_orchestrator(
        events=events,
        clock=clock,
        generator=generator,
    )

    result = orchestrator.execute(request)

    assert result.started_at_utc == STARTED
    assert result.completed_at_utc == COMPLETED
    assert result.duration_ms == 2000
    assert generator.calls == []


@pytest.mark.parametrize(
    (
        "error_field",
        "expected_events",
        "expected_state",
    ),
    [
        (
            "repository_error",
            ["repository"],
            ExecutionState.REPOSITORY_VALIDATION,
        ),
        (
            "acquisition_error",
            ["repository", "acquisition"],
            ExecutionState.REGISTRY_ACQUISITION,
        ),
        (
            "validation_error",
            ["repository", "acquisition", "validation"],
            ExecutionState.ACQUISITION_VALIDATION,
        ),
        (
            "acceptance_error",
            ["repository", "acquisition", "validation", "acceptance"],
            ExecutionState.REGISTRY_ACCEPTANCE,
        ),
    ],
)
def test_execute_short_circuits_and_preserves_original_exception(
    error_field: str,
    expected_events: list[str],
    expected_state: ExecutionState,
) -> None:
    events: list[str] = []
    machines: list[ExecutionStateMachine] = []
    expected = RuntimeError(f"{error_field} failure")
    kwargs: dict[str, Exception] = {error_field: expected}
    orchestrator, *_ = build_orchestrator(
        events=events,
        machine_sink=machines,
        **kwargs,
    )

    with pytest.raises(RuntimeError) as raised:
        orchestrator.execute(REQUEST)

    assert raised.value is expected
    assert events == expected_events
    assert len(machines) == 1
    assert machines[0].current_state is expected_state


def test_execute_propagates_state_machine_failure_unchanged() -> None:
    events: list[str] = []
    expected = RuntimeError("state machine unavailable")

    def failing_factory(clock) -> ExecutionStateMachine:
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
        state_machine_factory=cast(
            Callable,
            failing_factory,
        ),
    )

    with pytest.raises(RuntimeError) as raised:
        orchestrator.execute(REQUEST)

    assert raised.value is expected
    assert events == []
