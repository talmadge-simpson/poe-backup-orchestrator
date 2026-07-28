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
from poe_backup_orchestrator.models.operational_acceptance import (
    ACCEPTANCE_SCHEMA_NAME,
    ACCEPTANCE_SCHEMA_VERSION,
    AcceptanceCheck,
    FileEvidence,
    OperationalAcceptanceEvidence,
    OperationalAcceptancePublication,
    OperationalAcceptanceResult,
    OperationalAcceptanceStatus,
)
from poe_backup_orchestrator.models.operational_report import (
    REPORT_SCHEMA_NAME,
    REPORT_SCHEMA_VERSION,
    OperationalEvidenceReport,
    OperationalFailureReport,
    OperationalReport,
    OperationalReportPublication,
)
from poe_backup_orchestrator.models.recovery import (
    RecoveryPoint,
    RecoveryPointEligibility,
    RecoveryPointEligibilityResult,
    RecoveryPointReasonCode,
)
from poe_backup_orchestrator.models.recovery_manifest import (
    SUPPORTED_RECOVERY_ACQUISITION_TYPE,
    SUPPORTED_RECOVERY_MANIFEST_VERSION,
    RecoveryManifest,
    RecoveryManifestFaultCode,
    RecoveryManifestPublication,
    RecoveryManifestSnapshot,
    RecoveryManifestVerification,
)
from poe_backup_orchestrator.models.registry_acceptance import (
    RegistryAcceptanceResult,
    RegistryAcceptanceStatus,
)
from poe_backup_orchestrator.models.registry_ingestion import RegistryIngestionResult
from poe_backup_orchestrator.models.repository import RepositoryValidationResult
from poe_backup_orchestrator.models.restore_plan import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestoreConflict,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanRequest,
    RestorePlanValidation,
    RestoreWarning,
)
from poe_backup_orchestrator.models.restore_workspace import (
    RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightCheck,
    RestoreWorkspacePreflightReadiness,
    RestoreWorkspacePreflightReasonCode,
)
from poe_backup_orchestrator.models.restore_workspace_materialization import (
    RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION,
    RestoreWorkspaceDirectoryRecord,
    RestoreWorkspaceMaterialization,
    RestoreWorkspaceMaterializationReasonCode,
    RestoreWorkspaceMaterializationStatus,
)
from poe_backup_orchestrator.models.runtime import (
    RUNTIME_STATE_SCHEMA_VERSION,
    RuntimeDescriptor,
    RuntimeEnvironment,
    RuntimeExecutionStatus,
    RuntimeState,
    RuntimeValidationCheck,
    RuntimeValidationResult,
)
from poe_backup_orchestrator.models.sqlite_backup import SqliteBackupResult

__all__ = [
    "OperationalAcceptanceStatus",
    "OperationalAcceptanceResult",
    "OperationalAcceptancePublication",
    "OperationalAcceptanceEvidence",
    "FileEvidence",
    "AcceptanceCheck",
    "ACCEPTANCE_SCHEMA_VERSION",
    "ACCEPTANCE_SCHEMA_NAME",
    "RecoveryManifestVerification",
    "RecoveryManifestSnapshot",
    "RecoveryManifestPublication",
    "RecoveryManifestFaultCode",
    "RecoveryManifest",
    "SUPPORTED_RECOVERY_MANIFEST_VERSION",
    "SUPPORTED_RECOVERY_ACQUISITION_TYPE",
    "RecoveryPointReasonCode",
    "RecoveryPointEligibilityResult",
    "RecoveryPointEligibility",
    "RecoveryPoint",
    "RegistryAcceptanceResult",
    "RegistryAcceptanceStatus",
    "RegistryIngestionResult",
    "RepositoryValidationResult",
    "SqliteBackupResult",
    "RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION",
    "RestoreWorkspacePreflight",
    "RestoreWorkspacePreflightCheck",
    "RestoreWorkspacePreflightReadiness",
    "RestoreWorkspacePreflightReasonCode",
    "RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION",
    "RestoreWorkspaceDirectoryRecord",
    "RestoreWorkspaceMaterialization",
    "RestoreWorkspaceMaterializationReasonCode",
    "RestoreWorkspaceMaterializationStatus",
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
    "REPORT_SCHEMA_NAME",
    "REPORT_SCHEMA_VERSION",
    "OperationalEvidenceReport",
    "OperationalFailureReport",
    "OperationalReport",
    "OperationalReportPublication",
    "RUNTIME_STATE_SCHEMA_VERSION",
    "RuntimeExecutionStatus",
    "RuntimeState",
    "RegistryBackupRequest",
]

__all__ += [
    "RuntimeDescriptor",
    "RuntimeEnvironment",
    "RuntimeValidationCheck",
    "RuntimeValidationResult",
    "RESTORE_PLAN_POLICY_VERSION",
    "RESTORE_PLAN_SCHEMA_VERSION",
    "RestoreAction",
    "RestoreActionType",
    "RestoreConflict",
    "RestorePlan",
    "RestorePlanReadiness",
    "RestorePlanReasonCode",
    "RestorePlanRequest",
    "RestorePlanValidation",
    "RestoreWarning",
]
