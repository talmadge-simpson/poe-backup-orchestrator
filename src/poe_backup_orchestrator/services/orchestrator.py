"""Registry backup orchestration across successful and failed executions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from poe_backup_orchestrator.exceptions import OrchestratorError
from poe_backup_orchestrator.models import (
    Clock,
    ExecutionOutcome,
    ExecutionState,
    JobId,
    JobIdGenerator,
    RegistryBackupExecutionResult,
    RegistryBackupRequest,
)
from poe_backup_orchestrator.services.contracts import (
    AcquisitionValidationService,
    RegistryAcceptanceService,
    RegistryAcquisitionService,
    RepositoryValidationService,
)
from poe_backup_orchestrator.services.execution_state_machine import (
    ExecutionStateMachine,
)
from poe_backup_orchestrator.services.failure_mapping import (
    map_operational_failure,
)


class RuntimeLifecycle(Protocol):
    """Persist runtime ownership and accepted orchestration transitions."""

    def start(self, job_id: JobId, started_at_utc: datetime) -> object: ...

    def transition_to(self, execution_state: ExecutionState) -> object: ...


StateMachineFactory = Callable[[Clock], ExecutionStateMachine]


@dataclass(frozen=True, slots=True)
class RegistryBackupOrchestrator:
    """Coordinate one Registry backup execution."""

    repository_validation: RepositoryValidationService
    registry_acquisition: RegistryAcquisitionService
    acquisition_validation: AcquisitionValidationService
    registry_acceptance: RegistryAcceptanceService
    clock: Clock
    job_id_generator: JobIdGenerator
    state_machine_factory: StateMachineFactory = ExecutionStateMachine
    runtime_lifecycle: RuntimeLifecycle | None = None

    def execute(
        self,
        request: RegistryBackupRequest,
    ) -> RegistryBackupExecutionResult:
        """Execute the workflow and classify expected operational failures."""

        started_at_utc = request.requested_at_utc or self.clock.now_utc()
        job_id = request.job_id or self.job_id_generator.generate(started_at_utc)
        state_machine = self.state_machine_factory(self.clock)
        if self.runtime_lifecycle is not None:
            self.runtime_lifecycle.start(job_id, started_at_utc)

        repository_result: Any | None = None
        acquisition_result: Any | None = None
        validation_result: Any | None = None
        acceptance_result: Any | None = None

        try:
            self._transition_to(state_machine, ExecutionState.LOCK_ACQUISITION)

            self._transition_to(state_machine, ExecutionState.REPOSITORY_VALIDATION)
            repository_result = self.repository_validation.validate()

            self._transition_to(state_machine, ExecutionState.REGISTRY_ACQUISITION)
            acquisition_result = self.registry_acquisition.acquire()

            self._transition_to(state_machine, ExecutionState.ACQUISITION_VALIDATION)
            validation_result = self.acquisition_validation.validate(acquisition_result)

            self._transition_to(state_machine, ExecutionState.REGISTRY_ACCEPTANCE)
            acceptance_result = self.registry_acceptance.accept(validation_result)

            self._transition_to(state_machine, ExecutionState.REPORT_GENERATION)
            self._transition_to(state_machine, ExecutionState.COMPLETED)
        except OrchestratorError as error:
            return self._failed_result(
                error=error,
                failed_state=state_machine.current_state,
                state_machine=state_machine,
                job_id=job_id,
                started_at_utc=started_at_utc,
                repository_result=repository_result,
                acquisition_result=acquisition_result,
                validation_result=validation_result,
                acceptance_result=acceptance_result,
            )

        completed_at_utc = self.clock.now_utc()
        duration_ms = self._duration_ms(started_at_utc, completed_at_utc)

        return RegistryBackupExecutionResult(
            job_id=job_id,
            outcome=ExecutionOutcome.SUCCEEDED,
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
            duration_ms=duration_ms,
            final_state=state_machine.current_state,
            repository=repository_result,
            acquisition=acquisition_result,
            validation=validation_result,
            acceptance=acceptance_result,
        )

    def _transition_to(
        self,
        state_machine: ExecutionStateMachine,
        state: ExecutionState,
    ) -> None:
        """Apply a legal transition and then persist its runtime projection."""

        state_machine.transition_to(state)
        if self.runtime_lifecycle is not None:
            self.runtime_lifecycle.transition_to(state)

    def _failed_result(
        self,
        *,
        error: OrchestratorError,
        failed_state: ExecutionState,
        state_machine: ExecutionStateMachine,
        job_id: JobId,
        started_at_utc,
        repository_result: Any | None,
        acquisition_result: Any | None,
        validation_result: Any | None,
        acceptance_result: Any | None,
    ) -> RegistryBackupExecutionResult:
        failure = map_operational_failure(
            error,
            failed_state=failed_state,
        )
        self._transition_to(state_machine, ExecutionState.FAILED)

        completed_at_utc = self.clock.now_utc()
        duration_ms = self._duration_ms(started_at_utc, completed_at_utc)

        return RegistryBackupExecutionResult(
            job_id=job_id,
            outcome=ExecutionOutcome.FAILED,
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
            duration_ms=duration_ms,
            final_state=state_machine.current_state,
            repository=repository_result,
            acquisition=acquisition_result,
            validation=validation_result,
            acceptance=acceptance_result,
            failure=failure,
        )

    @staticmethod
    def _duration_ms(started_at_utc, completed_at_utc) -> int:
        return int((completed_at_utc - started_at_utc).total_seconds() * 1000)
