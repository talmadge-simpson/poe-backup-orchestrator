"""Domain models for the POE Backup Orchestrator."""

from poe_backup_orchestrator.models.evidence import EvidenceReference, EvidenceType
from poe_backup_orchestrator.models.execution import (
    ExecutionFailure,
    ExecutionOutcome,
    ExecutionState,
    FailureCategory,
    RegistryBackupExecutionResult,
)
from poe_backup_orchestrator.models.job import (
    Clock,
    JobId,
    JobIdGenerator,
    RegistryBackupRequest,
)
from poe_backup_orchestrator.models.registry_acceptance import (
    RegistryAcceptanceResult,
    RegistryAcceptanceStatus,
)
from poe_backup_orchestrator.models.registry_ingestion import RegistryIngestionResult
from poe_backup_orchestrator.models.repository import RepositoryValidationResult
from poe_backup_orchestrator.models.sqlite_backup import SqliteBackupResult

__all__ = [
    "RegistryAcceptanceResult",
    "RegistryAcceptanceStatus",
    "RegistryIngestionResult",
    "RepositoryValidationResult",
    "SqliteBackupResult",
]

__all__ += [
    "Clock",
    "EvidenceReference",
    "EvidenceType",
    "ExecutionFailure",
    "ExecutionOutcome",
    "ExecutionState",
    "FailureCategory",
    "JobId",
    "JobIdGenerator",
    "RegistryBackupExecutionResult",
    "RegistryBackupRequest",
]
