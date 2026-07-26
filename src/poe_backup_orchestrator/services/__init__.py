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
from poe_backup_orchestrator.services.failure_mapping import (
    FailurePolicy,
    map_operational_failure,
)
from poe_backup_orchestrator.services.operational_reporting import (
    build_operational_report,
    publish_operational_report,
    render_operational_summary,
)
from poe_backup_orchestrator.services.orchestrator import (
    RegistryBackupOrchestrator,
    StateMachineFactory,
)
from poe_backup_orchestrator.services.registry_acceptance import (
    accept_registry_acquisition,
)
from poe_backup_orchestrator.services.registry_acquisition import (
    create_registry_acquisition,
)
from poe_backup_orchestrator.services.registry_ingestion import (
    validate_registry_acquisition,
)
from poe_backup_orchestrator.services.repository_validation import (
    DEFAULT_REPOSITORY_COMMAND,
    validate_repository,
)
from poe_backup_orchestrator.services.run_service import (
    REPORTING_FAILURE_EXIT_CODE,
    RegistryBackupRunResult,
    RegistryBackupRunService,
    RepositoryReadinessGuard,
    SecureJobIdGenerator,
    SystemUtcClock,
    build_registry_backup_run_service,
)
from poe_backup_orchestrator.services.sqlite_backup import create_sqlite_backup

__all__ = [
    "create_registry_acquisition",
    "build_registry_backup_run_service",
    "SystemUtcClock",
    "SecureJobIdGenerator",
    "RepositoryReadinessGuard",
    "RegistryBackupRunService",
    "RegistryBackupRunResult",
    "REPORTING_FAILURE_EXIT_CODE",
    "AcquisitionValidationAdapter",
    "AcquisitionValidationService",
    "DEFAULT_REPOSITORY_COMMAND",
    "ExecutionStateMachine",
    "ExecutionTransition",
    "map_operational_failure",
    "FailurePolicy",
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
    "build_operational_report",
    "publish_operational_report",
    "render_operational_summary",
    "validate_repository",
]
