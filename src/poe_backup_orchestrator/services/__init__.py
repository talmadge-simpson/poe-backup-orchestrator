"""Application services for the POE Backup Orchestrator."""

from poe_backup_orchestrator.services.adapters import (
    AcquisitionValidationAdapter,
    RegistryAcceptanceAdapter,
    RegistryAcquisitionAdapter,
    RepositoryValidationAdapter,
)
from poe_backup_orchestrator.services.contracts import (
    AcquisitionValidationService,
    RegistryAcceptanceService,
    RegistryAcquisitionService,
    RepositoryValidationService,
)
from poe_backup_orchestrator.services.execution_state_machine import (
    ExecutionStateMachine,
    ExecutionTransition,
    InvalidExecutionTransitionError,
)
from poe_backup_orchestrator.services.orchestrator import (
    RegistryBackupOrchestrator,
    StateMachineFactory,
)
from poe_backup_orchestrator.services.registry_acceptance import (
    accept_registry_acquisition,
)
from poe_backup_orchestrator.services.registry_ingestion import (
    validate_registry_acquisition,
)
from poe_backup_orchestrator.services.repository_validation import (
    DEFAULT_REPOSITORY_COMMAND,
    validate_repository,
)
from poe_backup_orchestrator.services.sqlite_backup import create_sqlite_backup

__all__ = [
    "AcquisitionValidationAdapter",
    "AcquisitionValidationService",
    "DEFAULT_REPOSITORY_COMMAND",
    "ExecutionStateMachine",
    "ExecutionTransition",
    "InvalidExecutionTransitionError",
    "RegistryAcceptanceAdapter",
    "RegistryAcceptanceService",
    "RegistryAcquisitionAdapter",
    "RegistryAcquisitionService",
    "RepositoryValidationAdapter",
    "RepositoryValidationService",
    "StateMachineFactory",
    "RegistryBackupOrchestrator",
    "accept_registry_acquisition",
    "create_sqlite_backup",
    "validate_registry_acquisition",
    "validate_repository",
]
