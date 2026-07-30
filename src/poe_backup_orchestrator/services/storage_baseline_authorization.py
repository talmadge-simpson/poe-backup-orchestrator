"""Side-effect-free preservation-baseline authorization decision assembly."""

from __future__ import annotations

from datetime import datetime

from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    PreservationBaselineAcceptanceRecommendation,
)
from poe_backup_orchestrator.models.storage_baseline_authorization import (
    STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION,
    AuthorizationAuthority,
    AuthorizationConditionDecision,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    PilotAuthorization,
    PreservationBaselineAuthorizationDecision,
    PreservationBaselineAuthorizationIdentity,
    stable_preservation_baseline_authorization_id,
)


class PreservationBaselineAuthorizationError(Exception):
    """Raised when a valid authorization decision cannot be assembled."""


class PreservationBaselineAuthorizationDecisionAssembler:
    """Construct one immutable accountable decision without persistence."""

    def assemble(
        self,
        *,
        recommendation: PreservationBaselineAcceptanceRecommendation,
        outcome: AuthorizationDecisionOutcome,
        authority: AuthorizationAuthority,
        decided_at_utc: datetime,
        condition_decisions: tuple[AuthorizationConditionDecision, ...],
        scope: AuthorizationScope,
        pilot: PilotAuthorization | None,
        retention_obligations: tuple[str, ...],
        supersession_eligible: bool,
        rationale: str,
    ) -> PreservationBaselineAuthorizationDecision:
        if not isinstance(
            recommendation,
            PreservationBaselineAcceptanceRecommendation,
        ):
            raise PreservationBaselineAuthorizationError(
                "recommendation must be PreservationBaselineAcceptanceRecommendation"
            )
        if not isinstance(outcome, AuthorizationDecisionOutcome):
            raise PreservationBaselineAuthorizationError(
                "outcome must be AuthorizationDecisionOutcome"
            )
        if not isinstance(authority, AuthorizationAuthority):
            raise PreservationBaselineAuthorizationError("authority must be AuthorizationAuthority")
        if not isinstance(condition_decisions, tuple):
            raise PreservationBaselineAuthorizationError(
                "condition_decisions must be an immutable tuple"
            )
        if not isinstance(scope, AuthorizationScope):
            raise PreservationBaselineAuthorizationError("scope must be AuthorizationScope")
        if pilot is not None and not isinstance(pilot, PilotAuthorization):
            raise PreservationBaselineAuthorizationError(
                "pilot must be PilotAuthorization when present"
            )
        if not isinstance(retention_obligations, tuple):
            raise PreservationBaselineAuthorizationError(
                "retention_obligations must be an immutable tuple"
            )

        canonical_condition_decisions = tuple(
            sorted(
                condition_decisions,
                key=lambda item: item.condition_sequence,
            )
        )
        canonical_retention_obligations = tuple(sorted(retention_obligations))
        recommendation_identity = recommendation.identity

        authorization_id = stable_preservation_baseline_authorization_id(
            evaluation_id=recommendation_identity.evaluation_id,
            validation_id=recommendation_identity.validation_id,
            candidate_id=recommendation_identity.candidate_id,
            baseline_id=recommendation_identity.baseline_id,
            outcome=outcome,
            authority=authority,
            condition_decisions=canonical_condition_decisions,
            scope=scope,
            pilot=pilot,
            retention_obligations=canonical_retention_obligations,
            supersession_eligible=supersession_eligible,
            rationale=rationale,
        )

        try:
            return PreservationBaselineAuthorizationDecision(
                identity=PreservationBaselineAuthorizationIdentity(
                    schema_version=STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION,
                    authorization_id=authorization_id,
                    evaluation_id=recommendation_identity.evaluation_id,
                    validation_id=recommendation_identity.validation_id,
                    candidate_id=recommendation_identity.candidate_id,
                    baseline_id=recommendation_identity.baseline_id,
                ),
                recommendation=recommendation,
                outcome=outcome,
                authority=authority,
                decided_at_utc=decided_at_utc,
                condition_decisions=canonical_condition_decisions,
                scope=scope,
                pilot=pilot,
                retention_obligations=canonical_retention_obligations,
                supersession_eligible=supersession_eligible,
                rationale=rationale,
            )
        except ValueError as exc:
            raise PreservationBaselineAuthorizationError(
                f"authorization decision assembly failed: {exc}"
            ) from exc
