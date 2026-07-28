"""Compose certified restore services into one controlled execution workflow."""

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models import (
    RESTORE_EXECUTION_RECORD_SCHEMA_VERSION,
    RestoreExecutionRecord,
    RestorePlan,
)
from poe_backup_orchestrator.services.restore.authoritative_promotion import (
    RestoreAuthoritativePromotionService,
)
from poe_backup_orchestrator.services.restore.authoritative_target_preflight import (
    RestoreAuthoritativeTargetPreflightService,
)
from poe_backup_orchestrator.services.restore.materialization import (
    RestoreWorkspaceMaterializationService,
)
from poe_backup_orchestrator.services.restore.post_promotion_verification import (
    RestorePostPromotionVerificationService,
)
from poe_backup_orchestrator.services.restore.preflight import (
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
    RestoreStagedArtifactValidationService,
)
from poe_backup_orchestrator.services.restore.staging import (
    RestoreArtifactStagingService,
)


def _utc_now() -> datetime:
    return datetime.now(UTC)


class RestoreExecutionOrchestrator:
    """Sequence one governed restore execution across certified services."""

    def __init__(
        self,
        *,
        workspace_preflight: RestoreWorkspacePreflightService,
        workspace_materialization: RestoreWorkspaceMaterializationService,
        artifact_staging: RestoreArtifactStagingService,
        staged_validation: RestoreStagedArtifactValidationService,
        application_validation: RestoreRegistryApplicationValidationService,
        authoritative_preflight: RestoreAuthoritativeTargetPreflightService,
        rollback_capture: RestoreRollbackArtifactCaptureService,
        promotion_readiness: RestorePromotionReadinessService,
        authoritative_promotion: RestoreAuthoritativePromotionService,
        post_promotion_verification: RestorePostPromotionVerificationService,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._workspace_preflight = workspace_preflight
        self._workspace_materialization = workspace_materialization
        self._artifact_staging = artifact_staging
        self._staged_validation = staged_validation
        self._application_validation = application_validation
        self._authoritative_preflight = authoritative_preflight
        self._rollback_capture = rollback_capture
        self._promotion_readiness = promotion_readiness
        self._authoritative_promotion = authoritative_promotion
        self._post_promotion_verification = post_promotion_verification
        self._clock = clock

    def execute(
        self,
        plan: RestorePlan,
        *,
        lock_path: Path,
    ) -> RestoreExecutionRecord:
        """Execute one authorized restore plan and return aggregate evidence."""

        started_at_utc = self._clock()
        ownership_handle = self._promotion_readiness.acquire_ownership(
            plan_id=plan.plan_id,
            lock_path=lock_path,
            acquired_at_utc=started_at_utc,
        )

        try:
            workspace_preflight = self._workspace_preflight.evaluate(
                plan,
                evaluated_at_utc=self._clock(),
            )
            workspace_materialization = self._workspace_materialization.materialize(
                plan,
                workspace_preflight,
                materialized_at_utc=self._clock(),
            )
            artifact_staging = self._artifact_staging.stage(
                plan,
                workspace_preflight,
                workspace_materialization,
                staged_at_utc=self._clock(),
            )
            staged_validation = self._staged_validation.validate(
                plan,
                workspace_preflight,
                workspace_materialization,
                artifact_staging,
                validated_at_utc=self._clock(),
            )
            application_validation = self._application_validation.validate(
                plan,
                staged_validation,
                validated_at_utc=self._clock(),
            )
            authoritative_preflight = self._authoritative_preflight.preflight(
                plan,
                application_validation,
                preflight_at_utc=self._clock(),
            )
            rollback_capture = self._rollback_capture.capture(
                plan,
                authoritative_preflight,
                captured_at_utc=self._clock(),
            )
            promotion_readiness = self._promotion_readiness.evaluate(
                plan,
                staged_validation,
                application_validation,
                authoritative_preflight,
                rollback_capture,
                ownership_handle.evidence,
                evaluated_at_utc=self._clock(),
            )
            authoritative_promotion = self._authoritative_promotion.execute(
                plan,
                promotion_readiness,
                executed_at_utc=self._clock(),
            )
            post_promotion_verification = self._post_promotion_verification.verify(
                plan,
                authoritative_promotion,
                verified_at_utc=self._clock(),
            )
            return RestoreExecutionRecord(
                schema_version=RESTORE_EXECUTION_RECORD_SCHEMA_VERSION,
                plan_id=plan.plan_id,
                started_at_utc=started_at_utc,
                completed_at_utc=post_promotion_verification.verified_at_utc,
                lock_path=lock_path,
                plan=plan,
                workspace_preflight=workspace_preflight,
                workspace_materialization=workspace_materialization,
                artifact_staging=artifact_staging,
                staged_validation=staged_validation,
                application_validation=application_validation,
                authoritative_preflight=authoritative_preflight,
                rollback_capture=rollback_capture,
                promotion_readiness=promotion_readiness,
                authoritative_promotion=authoritative_promotion,
                post_promotion_verification=post_promotion_verification,
                restore_completed=True,
            )
        finally:
            ownership_handle.release()
