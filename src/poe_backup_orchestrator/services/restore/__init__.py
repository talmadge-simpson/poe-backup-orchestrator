"""Restore-domain services for governed Registry recovery."""

from poe_backup_orchestrator.services.restore.authoritative_promotion import (
    RestoreAuthoritativePromotionError,
    RestoreAuthoritativePromotionService,
)
from poe_backup_orchestrator.services.restore.authoritative_target_preflight import (
    RestoreAuthoritativeTargetPreflightError,
    RestoreAuthoritativeTargetPreflightService,
    preflight_authoritative_target,
)
from poe_backup_orchestrator.services.restore.discovery import (
    DEFAULT_DISCOVERY_POLICY_VERSION,
    DEFAULT_RECOVERY_MANIFEST_FILENAME,
    RecoveryPointDiscoveryError,
    discover_recovery_points,
    locate_recovery_point_packages,
)
from poe_backup_orchestrator.services.restore.eligibility import (
    DEFAULT_ELIGIBILITY_POLICY_VERSION,
    evaluate_recovery_point,
    evaluate_recovery_points,
)
from poe_backup_orchestrator.services.restore.execution_orchestrator import (
    RestoreExecutionOrchestrator,
)
from poe_backup_orchestrator.services.restore.manifest import (
    RecoveryManifestError,
    read_recovery_manifest,
)
from poe_backup_orchestrator.services.restore.materialization import (
    LocalWorkspaceFilesystemOperator,
    RestoreWorkspaceMaterializationError,
    RestoreWorkspaceMaterializationService,
    WorkspaceFilesystemOperator,
    materialize_restore_workspace,
)
from poe_backup_orchestrator.services.restore.planning import (
    RestorePlanningError,
    RestorePlanningService,
    build_restore_plan,
)
from poe_backup_orchestrator.services.restore.post_promotion_verification import (
    RestorePostPromotionVerificationError,
    RestorePostPromotionVerificationService,
)
from poe_backup_orchestrator.services.restore.preflight import (
    LocalWorkspacePathProbe,
    RestoreWorkspacePreflightError,
    RestoreWorkspacePreflightService,
    WorkspacePathProbe,
    preflight_restore_workspace,
)
from poe_backup_orchestrator.services.restore.promotion_readiness import (
    RestoreExecutionOwnershipHandle,
    RestorePromotionReadinessError,
    RestorePromotionReadinessService,
)
from poe_backup_orchestrator.services.restore.registry_application_validation import (
    RestoreRegistryApplicationValidationError,
    RestoreRegistryApplicationValidationService,
    validate_staged_registry_application,
)
from poe_backup_orchestrator.services.restore.rollback_artifact_capture import (
    RestoreRollbackArtifactCaptureError,
    RestoreRollbackArtifactCaptureService,
    capture_rollback_artifact,
)
from poe_backup_orchestrator.services.restore.staged_validation import (
    ArtifactIntegrityOperator,
    LocalArtifactIntegrityOperator,
    RestoreStagedArtifactValidationError,
    RestoreStagedArtifactValidationService,
    validate_staged_restore_artifact,
)
from poe_backup_orchestrator.services.restore.staging import (
    ArtifactFilesystemOperator,
    LocalArtifactFilesystemOperator,
    RestoreArtifactStagingError,
    RestoreArtifactStagingService,
    stage_restore_artifact,
)

__all__ = [
    "RestoreExecutionOrchestrator",
    "DEFAULT_ELIGIBILITY_POLICY_VERSION",
    "evaluate_recovery_point",
    "evaluate_recovery_points",
    "DEFAULT_DISCOVERY_POLICY_VERSION",
    "DEFAULT_RECOVERY_MANIFEST_FILENAME",
    "RecoveryManifestError",
    "RecoveryPointDiscoveryError",
    "discover_recovery_points",
    "locate_recovery_point_packages",
    "read_recovery_manifest",
    "RestorePlanningError",
    "RestorePlanningService",
    "build_restore_plan",
    "LocalWorkspacePathProbe",
    "RestoreWorkspacePreflightError",
    "RestoreWorkspacePreflightService",
    "WorkspacePathProbe",
    "preflight_restore_workspace",
    "LocalWorkspaceFilesystemOperator",
    "RestoreWorkspaceMaterializationError",
    "RestoreWorkspaceMaterializationService",
    "WorkspaceFilesystemOperator",
    "materialize_restore_workspace",
    "ArtifactFilesystemOperator",
    "LocalArtifactFilesystemOperator",
    "RestoreArtifactStagingError",
    "RestoreArtifactStagingService",
    "stage_restore_artifact",
    "ArtifactIntegrityOperator",
    "LocalArtifactIntegrityOperator",
    "RestoreStagedArtifactValidationError",
    "RestoreStagedArtifactValidationService",
    "validate_staged_restore_artifact",
    "RestoreRegistryApplicationValidationError",
    "RestoreRegistryApplicationValidationService",
    "validate_staged_registry_application",
    "RestoreAuthoritativeTargetPreflightError",
    "RestoreAuthoritativeTargetPreflightService",
    "preflight_authoritative_target",
    "RestoreRollbackArtifactCaptureError",
    "RestoreRollbackArtifactCaptureService",
    "capture_rollback_artifact",
    "RestoreExecutionOwnershipHandle",
    "RestorePromotionReadinessError",
    "RestorePromotionReadinessService",
    "RestoreAuthoritativePromotionError",
    "RestoreAuthoritativePromotionService",
    "RestorePostPromotionVerificationError",
    "RestorePostPromotionVerificationService",
]
