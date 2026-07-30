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
from poe_backup_orchestrator.services.operational_acceptance import (
    ACCEPTANCE_FAILURE_EXIT_CODE,
    OperationalAcceptanceService,
    publish_operational_acceptance,
    render_operational_acceptance_summary,
)
from poe_backup_orchestrator.services.operational_reporting import (
    build_operational_report,
    publish_operational_report,
    render_operational_summary,
)
from poe_backup_orchestrator.services.orchestrator import (
    RegistryBackupOrchestrator,
    RuntimeLifecycle,
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
from poe_backup_orchestrator.services.runtime_composition import (
    build_runtime_recovery_inspector,
)
from poe_backup_orchestrator.services.runtime_lifecycle import (
    RuntimeLifecycleCoordinator,
)
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspection,
    RuntimeRecoveryInspector,
    RuntimeRecoveryOutcome,
    SystemHostIdentity,
    SystemProcessLiveness,
)
from poe_backup_orchestrator.services.runtime_state_store import (
    RUNTIME_STATE_FILENAME,
    RuntimeStateStore,
)
from poe_backup_orchestrator.services.runtime_validation import (
    require_valid_runtime,
    validate_runtime,
)
from poe_backup_orchestrator.services.sqlite_backup import create_sqlite_backup
from poe_backup_orchestrator.services.storage_baseline_composition import (
    PreservationBaselineComposer,
    PreservationBaselineCompositionError,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
    INVENTORY_EVIDENCE_SCHEMA_NAME,
    ContentIntegrityEvidenceAdapter,
    ContentIntegrityValidationFacts,
    DeserializedPreservationEvidence,
    EvidenceDeserializationStatus,
    EvidenceFactExtractionStatus,
    EvidenceLoadStatus,
    ExtractedPreservationEvidenceFacts,
    FilesystemPreservationEvidenceLoader,
    InventoryEvidenceAdapter,
    InventoryValidationFacts,
    LoadedPreservationEvidence,
    PreservationBaselineValidationError,
    PreservationEvidenceAdapter,
    PreservationEvidenceDeserializationService,
    PreservationEvidenceFactExtractionService,
    PreservationEvidenceLoader,
    ValidationAdapterRegistry,
)
from poe_backup_orchestrator.services.storage_content_capture import (
    ContentCapturePolicy,
    InventoryContentCaptureError,
    InventoryContentCaptureService,
)
from poe_backup_orchestrator.services.storage_content_integrity import (
    ContentIntegrityVerificationError,
    ContentIntegrityVerificationPolicy,
    ContentIntegrityVerifier,
)
from poe_backup_orchestrator.services.storage_content_integrity_persistence import (
    ContentIntegrityEvidencePersistence,
    ContentIntegrityPersistenceError,
    PersistedContentIntegrityEvidence,
)
from poe_backup_orchestrator.services.storage_discovery import (
    FilesystemDiscoveryAdapter,
    LocalFilesystemDiscoveryAdapter,
)
from poe_backup_orchestrator.services.storage_inventory_assembly import (
    AssembledInventoryItem,
    DiscoveryInventoryAssembler,
    InventoryAssemblyContext,
    InventoryAssemblyError,
    InventoryAssemblyResult,
    UnsupportedInventoryItem,
    stable_inventory_item_id,
)
from poe_backup_orchestrator.services.storage_inventory_persistence import (
    INVENTORY_EVIDENCE_LOCK_FILENAME,
    STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION,
    InventoryEvidenceConflictError,
    InventoryEvidenceLockError,
    InventoryEvidencePersistenceError,
    InventoryEvidencePublication,
    InventoryEvidenceSerializer,
    InventoryEvidenceStore,
)

__all__ = [
    "build_runtime_recovery_inspector",
    "RuntimeLifecycleCoordinator",
    "RuntimeLifecycle",
    "SystemProcessLiveness",
    "SystemHostIdentity",
    "RuntimeRecoveryOutcome",
    "RuntimeRecoveryInspector",
    "RuntimeRecoveryInspection",
    "RuntimeStateStore",
    "RUNTIME_STATE_FILENAME",
    "render_operational_acceptance_summary",
    "publish_operational_acceptance",
    "OperationalAcceptanceService",
    "ACCEPTANCE_FAILURE_EXIT_CODE",
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
    "INVENTORY_EVIDENCE_LOCK_FILENAME",
    "STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION",
    "InventoryEvidenceConflictError",
    "InventoryEvidenceLockError",
    "InventoryEvidencePersistenceError",
    "InventoryEvidencePublication",
    "InventoryEvidenceSerializer",
    "InventoryEvidenceStore",
    "ContentCapturePolicy",
    "InventoryContentCaptureError",
    "InventoryContentCaptureService",
    "FilesystemDiscoveryAdapter",
    "LocalFilesystemDiscoveryAdapter",
    "AssembledInventoryItem",
    "DiscoveryInventoryAssembler",
    "InventoryAssemblyContext",
    "InventoryAssemblyError",
    "InventoryAssemblyResult",
    "UnsupportedInventoryItem",
    "stable_inventory_item_id",
    "ContentIntegrityVerificationError",
    "ContentIntegrityVerificationPolicy",
    "ContentIntegrityVerifier",
    "PreservationEvidenceFactExtractionService",
    "ExtractedPreservationEvidenceFacts",
    "EvidenceFactExtractionStatus",
    "ContentIntegrityValidationFacts",
    "InventoryValidationFacts",
    "PreservationEvidenceDeserializationService",
    "InventoryEvidenceAdapter",
    "EvidenceDeserializationStatus",
    "DeserializedPreservationEvidence",
    "ContentIntegrityEvidenceAdapter",
    "INVENTORY_EVIDENCE_SCHEMA_NAME",
    "CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME",
    "EvidenceLoadStatus",
    "FilesystemPreservationEvidenceLoader",
    "LoadedPreservationEvidence",
    "ContentIntegrityEvidencePersistence",
    "ContentIntegrityPersistenceError",
    "PersistedContentIntegrityEvidence",
]

__all__ += [
    "require_valid_runtime",
    "validate_runtime",
]

__all__ += [
    "PreservationBaselineComposer",
    "PreservationBaselineCompositionError",
]

__all__ += [
    "PreservationBaselineValidationError",
    "PreservationEvidenceAdapter",
    "PreservationEvidenceLoader",
    "ValidationAdapterRegistry",
]
