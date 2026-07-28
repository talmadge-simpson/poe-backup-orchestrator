from poe_backup_orchestrator.models import RegistryApplicationValidationPolicy
from poe_backup_orchestrator.services.restore.authoritative_promotion import (
    RestoreAuthoritativePromotionService,
)
from poe_backup_orchestrator.services.restore.authoritative_target_preflight import (
    RestoreAuthoritativeTargetPreflightService,
)
from poe_backup_orchestrator.services.restore.execution_orchestrator import (
    RestoreExecutionOrchestrator,
)
from poe_backup_orchestrator.services.restore.materialization import (
    LocalWorkspaceFilesystemOperator,
    RestoreWorkspaceMaterializationService,
)
from poe_backup_orchestrator.services.restore.post_promotion_verification import (
    RestorePostPromotionVerificationService,
)
from poe_backup_orchestrator.services.restore.preflight import (
    LocalWorkspacePathProbe,
    RestoreWorkspacePreflightService,
)
from poe_backup_orchestrator.services.restore.promotion_readiness import (
    RestorePromotionReadinessService,
)
from poe_backup_orchestrator.services.restore.registry_application_validation import (
    RestoreRegistryApplicationValidationService,
)
from poe_backup_orchestrator.services.restore.rollback_artifact_capture import (
    RestoreRollbackArtifactCaptureService,
)
from poe_backup_orchestrator.services.restore.staged_validation import (
    LocalArtifactIntegrityOperator,
    RestoreStagedArtifactValidationService,
)
from poe_backup_orchestrator.services.restore.staging import (
    LocalArtifactFilesystemOperator,
    RestoreArtifactStagingService,
)


def build_restore_execution_orchestrator(
    *,
    validation_policy: RegistryApplicationValidationPolicy,
) -> RestoreExecutionOrchestrator:
    return RestoreExecutionOrchestrator(
        workspace_preflight=RestoreWorkspacePreflightService(path_probe=LocalWorkspacePathProbe()),
        workspace_materialization=RestoreWorkspaceMaterializationService(
            filesystem=LocalWorkspaceFilesystemOperator()
        ),
        artifact_staging=RestoreArtifactStagingService(
            filesystem=LocalArtifactFilesystemOperator()
        ),
        staged_validation=RestoreStagedArtifactValidationService(
            integrity=LocalArtifactIntegrityOperator()
        ),
        application_validation=RestoreRegistryApplicationValidationService(
            policy=validation_policy
        ),
        authoritative_preflight=RestoreAuthoritativeTargetPreflightService(),
        rollback_capture=RestoreRollbackArtifactCaptureService(),
        promotion_readiness=RestorePromotionReadinessService(),
        authoritative_promotion=RestoreAuthoritativePromotionService(),
        post_promotion_verification=RestorePostPromotionVerificationService(),
    )
