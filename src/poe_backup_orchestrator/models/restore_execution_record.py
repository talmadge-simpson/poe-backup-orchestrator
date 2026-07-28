"""Immutable aggregate evidence for one completed governed restore execution."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from poe_backup_orchestrator.models.restore_artifact_staging import (
    RestoreArtifactStaging,
)
from poe_backup_orchestrator.models.restore_authoritative_promotion import (
    RestoreAuthoritativePromotion,
)
from poe_backup_orchestrator.models.restore_authoritative_target_preflight import (
    RestoreAuthoritativeTargetPreflight,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_post_promotion_verification import (
    RestorePostPromotionVerification,
)
from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestorePromotionReadiness,
)
from poe_backup_orchestrator.models.restore_registry_application_validation import (
    RestoreRegistryApplicationValidation,
)
from poe_backup_orchestrator.models.restore_rollback_artifact_capture import (
    RestoreRollbackArtifactCapture,
)
from poe_backup_orchestrator.models.restore_staged_artifact_validation import (
    RestoreStagedArtifactValidation,
)
from poe_backup_orchestrator.models.restore_workspace import (
    RestoreWorkspacePreflight,
)
from poe_backup_orchestrator.models.restore_workspace_materialization import (
    RestoreWorkspaceMaterialization,
)

RESTORE_EXECUTION_RECORD_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class RestoreExecutionRecord:
    """Complete immutable evidence chain for one successful restore execution."""

    schema_version: str
    plan_id: str
    started_at_utc: datetime
    completed_at_utc: datetime
    lock_path: Path
    plan: RestorePlan
    workspace_preflight: RestoreWorkspacePreflight
    workspace_materialization: RestoreWorkspaceMaterialization
    artifact_staging: RestoreArtifactStaging
    staged_validation: RestoreStagedArtifactValidation
    application_validation: RestoreRegistryApplicationValidation
    authoritative_preflight: RestoreAuthoritativeTargetPreflight
    rollback_capture: RestoreRollbackArtifactCapture
    promotion_readiness: RestorePromotionReadiness
    authoritative_promotion: RestoreAuthoritativePromotion
    post_promotion_verification: RestorePostPromotionVerification
    restore_completed: bool

    def __post_init__(self) -> None:
        if self.schema_version != RESTORE_EXECUTION_RECORD_SCHEMA_VERSION:
            raise ValueError("unsupported restore execution record schema version")
        if not self.plan_id:
            raise ValueError("plan_id must not be empty")
        if self.lock_path == Path():
            raise ValueError("lock_path must not be empty")
        if self.completed_at_utc < self.started_at_utc:
            raise ValueError("completed_at_utc must not precede started_at_utc")
        if self.plan.plan_id != self.plan_id:
            raise ValueError("restore plan plan_id does not match execution record")

        evidence = (
            self.workspace_preflight,
            self.workspace_materialization,
            self.artifact_staging,
            self.staged_validation,
            self.application_validation,
            self.authoritative_preflight,
            self.rollback_capture,
            self.promotion_readiness,
            self.authoritative_promotion,
            self.post_promotion_verification,
        )
        if any(item.plan_id != self.plan_id for item in evidence):
            raise ValueError("restore evidence plan_id does not match execution record")

        if self.completed_at_utc != self.post_promotion_verification.verified_at_utc:
            raise ValueError("completed_at_utc must match post-promotion verification time")
        if not self.post_promotion_verification.restore_completed:
            raise ValueError("post-promotion verification must declare restore completion")
        if not self.restore_completed:
            raise ValueError("completed execution record must declare completion")
