"""Deterministic, non-mutating restore-plan construction."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RecoveryPoint,
    RecoveryPointEligibility,
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


class RestorePlanningError(ValueError):
    """Raised when supplied restore-planning inputs are internally inconsistent."""


class RestorePlanningService:
    """Construct immutable restore plans without observing or mutating live state."""

    def plan(
        self,
        recovery_point: RecoveryPoint,
        request: RestorePlanRequest,
        *,
        created_at_utc: datetime,
    ) -> RestorePlan:
        """Return a deterministic plan for the supplied recovery point and request."""

        _require_utc(created_at_utc)

        if recovery_point.recovery_point_id != request.recovery_point_id:
            raise RestorePlanningError(
                "request recovery_point_id does not match the supplied recovery point"
            )
        if recovery_point.artifact_path is None:
            raise RestorePlanningError("recovery point does not declare an artifact path")
        if recovery_point.manifest_path is None:
            raise RestorePlanningError("recovery point does not declare a manifest path")

        plan_id = _plan_id(recovery_point.recovery_point_id, created_at_utc)
        artifact_name = recovery_point.artifact_path.name
        target_name = request.authoritative_target_path.name

        if not artifact_name:
            raise RestorePlanningError("recovery artifact path must name a file")
        if not target_name:
            raise RestorePlanningError("authoritative target path must name a file")

        staging_target = request.staging_root / plan_id / artifact_name
        rollback_artifact = request.rollback_root / plan_id / target_name
        validation = _validation_for(
            recovery_point,
            request,
            evaluated_at_utc=created_at_utc,
        )
        actions = _actions_for(
            recovery_point.artifact_path,
            request.authoritative_target_path,
            staging_target,
            rollback_artifact,
            validation,
        )

        return RestorePlan(
            schema_version=RESTORE_PLAN_SCHEMA_VERSION,
            policy_version=RESTORE_PLAN_POLICY_VERSION,
            plan_id=plan_id,
            created_at_utc=created_at_utc,
            recovery_point_id=recovery_point.recovery_point_id,
            source_artifact_path=recovery_point.artifact_path,
            source_manifest_path=recovery_point.manifest_path,
            authoritative_target_path=request.authoritative_target_path,
            staging_target_path=staging_target,
            rollback_artifact_path=rollback_artifact,
            actions=actions,
            validation=validation,
            execution_authorized=False,
        )


def build_restore_plan(
    recovery_point: RecoveryPoint,
    request: RestorePlanRequest,
    *,
    created_at_utc: datetime,
) -> RestorePlan:
    """Convenience function for deterministic restore-plan construction."""

    return RestorePlanningService().plan(
        recovery_point,
        request,
        created_at_utc=created_at_utc,
    )


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RestorePlanningError("created_at_utc must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise RestorePlanningError("created_at_utc must use UTC")


def _plan_id(recovery_point_id: str, created_at_utc: datetime) -> str:
    timestamp = created_at_utc.strftime("%Y%m%dT%H%M%S%fZ")
    return f"restore-plan-{recovery_point_id}-{timestamp}"


def _validation_for(
    recovery_point: RecoveryPoint,
    request: RestorePlanRequest,
    *,
    evaluated_at_utc: datetime,
) -> RestorePlanValidation:
    eligibility = recovery_point.eligibility
    warnings = tuple(
        RestoreWarning(
            code=f"eligibility_warning_{index}",
            message=message,
        )
        for index, message in enumerate(eligibility.warnings, start=1)
    )

    if eligibility.classification is RecoveryPointEligibility.ELIGIBLE:
        if request.eligibility_override_requested:
            warnings += (
                RestoreWarning(
                    code="eligibility_override_not_required",
                    message=(
                        "An eligibility override was requested for a recovery point "
                        "already classified as eligible."
                    ),
                ),
            )
        return RestorePlanValidation(
            readiness=RestorePlanReadiness.READY,
            reason_codes=(RestorePlanReasonCode.PLAN_READY,),
            warnings=warnings,
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=evaluated_at_utc,
        )

    if eligibility.classification is RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE:
        conflict = RestoreConflict(
            code="eligibility_override_required",
            message=(
                "The selected recovery point is conditionally eligible and requires "
                "governed approval before restore execution."
            ),
            blocking=False,
            approval_can_resolve=True,
        )
        return RestorePlanValidation(
            readiness=RestorePlanReadiness.APPROVAL_REQUIRED,
            reason_codes=(RestorePlanReasonCode.ELIGIBILITY_OVERRIDE_REQUIRED,),
            warnings=warnings,
            conflicts=(conflict,),
            approval_required=True,
            evaluated_at_utc=evaluated_at_utc,
        )

    if eligibility.classification is RecoveryPointEligibility.INELIGIBLE:
        conflict = RestoreConflict(
            code="recovery_point_ineligible",
            message="The selected recovery point is ineligible for restore.",
        )
    else:
        conflict = RestoreConflict(
            code="recovery_point_eligibility_unknown",
            message="The selected recovery point has unknown restore eligibility.",
        )

    return RestorePlanValidation(
        readiness=RestorePlanReadiness.BLOCKED,
        reason_codes=(RestorePlanReasonCode.TARGET_STATE_CONFLICT,),
        warnings=warnings,
        conflicts=(conflict,),
        approval_required=False,
        evaluated_at_utc=evaluated_at_utc,
    )


def _actions_for(
    source_artifact: Path,
    authoritative_target: Path,
    staging_target: Path,
    rollback_artifact: Path,
    validation: RestorePlanValidation,
) -> tuple[RestoreAction, ...]:
    if validation.readiness is RestorePlanReadiness.BLOCKED:
        return (
            RestoreAction(
                ordinal=1,
                action_type=RestoreActionType.INSPECT_TARGET,
                description=(
                    "Inspect the authoritative Registry target only after planning "
                    "conflicts are resolved."
                ),
                destination_path=authoritative_target,
            ),
        )

    actions: list[RestoreAction] = [
        RestoreAction(
            ordinal=1,
            action_type=RestoreActionType.INSPECT_TARGET,
            description="Inspect the authoritative Registry target.",
            destination_path=authoritative_target,
        ),
        RestoreAction(
            ordinal=2,
            action_type=RestoreActionType.STAGE_RECOVERY_ARTIFACT,
            description="Stage the selected recovery artifact.",
            source_path=source_artifact,
            destination_path=staging_target,
            mutates_state=True,
        ),
        RestoreAction(
            ordinal=3,
            action_type=RestoreActionType.VERIFY_STAGED_CHECKSUM,
            description="Verify the staged artifact checksum.",
            source_path=staging_target,
        ),
        RestoreAction(
            ordinal=4,
            action_type=RestoreActionType.VERIFY_STAGED_SQLITE_INTEGRITY,
            description="Verify SQLite integrity of the staged artifact.",
            source_path=staging_target,
        ),
        RestoreAction(
            ordinal=5,
            action_type=RestoreActionType.CREATE_ROLLBACK_ARTIFACT,
            description="Create a rollback artifact from the authoritative target.",
            source_path=authoritative_target,
            destination_path=rollback_artifact,
            mutates_state=True,
        ),
        RestoreAction(
            ordinal=6,
            action_type=RestoreActionType.VERIFY_ROLLBACK_ARTIFACT,
            description="Verify the rollback artifact.",
            source_path=rollback_artifact,
        ),
    ]

    if validation.approval_required:
        actions.append(
            RestoreAction(
                ordinal=len(actions) + 1,
                action_type=RestoreActionType.AWAIT_APPROVAL,
                description="Await governed approval before promotion.",
                approval_required=True,
            )
        )

    actions.extend(
        (
            RestoreAction(
                ordinal=len(actions) + 1,
                action_type=RestoreActionType.PROMOTE_STAGED_ARTIFACT,
                description="Promote the staged artifact to the authoritative target.",
                source_path=staging_target,
                destination_path=authoritative_target,
                mutates_state=True,
                approval_required=validation.approval_required,
            ),
            RestoreAction(
                ordinal=len(actions) + 2,
                action_type=RestoreActionType.VERIFY_AUTHORITATIVE_TARGET,
                description="Verify the restored authoritative Registry target.",
                source_path=authoritative_target,
            ),
            RestoreAction(
                ordinal=len(actions) + 3,
                action_type=RestoreActionType.PUBLISH_RESTORE_EVIDENCE,
                description="Publish governed restore evidence.",
                mutates_state=True,
            ),
        )
    )
    return tuple(actions)
