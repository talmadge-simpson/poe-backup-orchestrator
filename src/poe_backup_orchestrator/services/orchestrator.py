"""Success-path orchestration for one Registry backup execution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from poe_backup_orchestrator.models import (
    Clock,
    ExecutionOutcome,
    ExecutionState,
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

StateMachineFactory = Callable[[Clock], ExecutionStateMachine]


@dataclass(frozen=True, slots=True)
class RegistryBackupOrchestrator:
    """Coordinate the normalized Registry backup services in lifecycle order."""

    repository_validation: RepositoryValidationService
    registry_acquisition: RegistryAcquisitionService
    acquisition_validation: AcquisitionValidationService
    registry_acceptance: RegistryAcceptanceService
    clock: Clock
    job_id_generator: JobIdGenerator
    state_machine_factory: StateMachineFactory = ExecutionStateMachine

    def execute(
        self,
        request: RegistryBackupRequest,
    ) -> RegistryBackupExecutionResult:
        """Execute the complete success path or propagate the original failure."""

        started_at_utc = request.requested_at_utc or self.clock.now_utc()
        job_id = request.job_id or self.job_id_generator.generate(started_at_utc)
        state_machine = self.state_machine_factory(self.clock)

        state_machine.transition_to(ExecutionState.LOCK_ACQUISITION)

        state_machine.transition_to(ExecutionState.REPOSITORY_VALIDATION)
        repository_result = self.repository_validation.validate()

        state_machine.transition_to(ExecutionState.REGISTRY_ACQUISITION)
        acquisition_result = self.registry_acquisition.acquire()

        state_machine.transition_to(ExecutionState.ACQUISITION_VALIDATION)
        validation_result = self.acquisition_validation.validate(acquisition_result)

        state_machine.transition_to(ExecutionState.REGISTRY_ACCEPTANCE)
        acceptance_result = self.registry_acceptance.accept(validation_result)

        state_machine.transition_to(ExecutionState.REPORT_GENERATION)
        state_machine.transition_to(ExecutionState.COMPLETED)

        completed_at_utc = self.clock.now_utc()
        duration_ms = int((completed_at_utc - started_at_utc).total_seconds() * 1000)

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
