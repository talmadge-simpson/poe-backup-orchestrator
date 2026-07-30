from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
    AcceptanceCondition,
    AcceptanceConditionDisposition,
    AcceptanceDecision,
    AcceptanceEvaluationIdentity,
    AcceptanceMode,
    PreservationBaselineAcceptanceRecommendation,
    stable_preservation_baseline_acceptance_evaluation_id,
)
from poe_backup_orchestrator.models.storage_baseline_authorization import (
    AuthorizationAuthority,
    AuthorizationConditionDecision,
    AuthorizationConditionDisposition,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    PilotAuthorization,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
    EvidenceRequirementObservation,
    EvidenceRequirementStatus,
    PreservationBaselineCandidate,
    PreservationBaselineCandidateIdentity,
    PreservationBaselineCandidateScope,
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.models.storage_baseline_validation import (
    STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
    EvidenceValidationStatus,
    PreservationBaselineValidationIdentity,
    PreservationBaselineValidationResult,
    ValidatedEvidenceReference,
    ValidationFinding,
    ValidationFindingCategory,
    ValidationFindingSeverity,
    stable_preservation_baseline_validation_id,
)
from poe_backup_orchestrator.services.storage_baseline_authorization import (
    PreservationBaselineAuthorizationDecisionAssembler,
    PreservationBaselineAuthorizationError,
)


def recommendation(
    decision: AcceptanceDecision,
    *,
    roots: tuple[str, ...] = ("root-a",),
) -> PreservationBaselineAcceptanceRecommendation:
    observations = []
    validated = []
    for index, root in enumerate(roots):
        reference = PreservationEvidenceReference(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            source_root_id=root,
            schema_version="1.0",
            evidence_path=Path(f"/evidence/{root}.jsonl"),
            digest_path=Path(f"/evidence/{root}.jsonl.sha256"),
            sha256=chr(ord("a") + index) * 64,
            byte_count=100,
        )
        observations.append(
            EvidenceRequirementObservation(
                source_root_id=root,
                evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
                status=EvidenceRequirementStatus.PRESENT,
                evidence_reference=reference,
            )
        )
        validated.append(
            ValidatedEvidenceReference(
                evidence_reference=reference,
                status=EvidenceValidationStatus.VERIFIED,
                calculated_sha256=reference.sha256,
                calculated_byte_count=reference.byte_count,
                sidecar_sha256=reference.sha256,
                resolved_schema_name="poe.storage.inventory-evidence",
                resolved_schema_version="1.0",
            )
        )

    candidate = PreservationBaselineCandidate(
        identity=PreservationBaselineCandidateIdentity(
            schema_version=STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
            candidate_id="pbc-" + "b" * 64,
            baseline_id="baseline-a",
            created_at_utc=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
        ),
        scope=PreservationBaselineCandidateScope(
            baseline_id="baseline-a",
            source_root_ids=roots,
        ),
        observations=tuple(observations),
    )

    finding = ValidationFinding(
        sequence=1,
        category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
        severity=ValidationFindingSeverity.WARNING,
        source_root_id=roots[0],
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        evidence_path=Path(f"/evidence/{roots[0]}.jsonl"),
        field_name="exception_count",
        expected="0",
        observed="1",
        detail="explicit exception remains visible",
    )
    findings = () if decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE else (finding,)
    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-validation-v1",
        validated_evidence=tuple(validated),
        findings=findings,
    )
    validation = PreservationBaselineValidationResult(
        identity=PreservationBaselineValidationIdentity(
            schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
            validation_id=validation_id,
            candidate_id=candidate.identity.candidate_id,
            baseline_id=candidate.identity.baseline_id,
            validated_at_utc=datetime(2026, 7, 30, 15, 0, tzinfo=UTC),
        ),
        candidate=candidate,
        policy_profile_id="strict-validation-v1",
        validated_evidence=tuple(validated),
        findings=findings,
    )

    if decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE:
        conditions = ()
        rationale_codes = ("no_validation_findings", "recommend_acceptance")
    elif decision is AcceptanceDecision.RECOMMEND_REVIEW:
        conditions = (
            AcceptanceCondition(
                sequence=1,
                condition_code="exception_review",
                disposition=AcceptanceConditionDisposition.REVIEW_REQUIRED,
                finding_categories=(ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,),
                finding_sequences=(1,),
                detail="review required",
            ),
        )
        rationale_codes = ("exception_review", "recommend_review")
    else:
        conditions = (
            AcceptanceCondition(
                sequence=1,
                condition_code="blocking_exception",
                disposition=AcceptanceConditionDisposition.BLOCKING,
                finding_categories=(ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,),
                finding_sequences=(1,),
                detail="blocking",
            ),
        )
        rationale_codes = ("blocking_exception", "recommend_rejection")

    evaluation_id = stable_preservation_baseline_acceptance_evaluation_id(
        validation_id=validation.identity.validation_id,
        candidate_id=validation.identity.candidate_id,
        baseline_id=validation.identity.baseline_id,
        policy_id="baseline-acceptance",
        policy_version="1.0",
        mode=AcceptanceMode.REVIEW_PERMITTED,
        conditions=conditions,
        decision=decision,
        rationale_codes=rationale_codes,
    )
    return PreservationBaselineAcceptanceRecommendation(
        identity=AcceptanceEvaluationIdentity(
            schema_version=STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
            evaluation_id=evaluation_id,
            validation_id=validation.identity.validation_id,
            candidate_id=validation.identity.candidate_id,
            baseline_id=validation.identity.baseline_id,
            policy_id="baseline-acceptance",
            policy_version="1.0",
        ),
        validation_result=validation,
        mode=AcceptanceMode.REVIEW_PERMITTED,
        decision=decision,
        conditions=conditions,
        rationale_codes=rationale_codes,
    )


def authority() -> AuthorizationAuthority:
    return AuthorizationAuthority(
        authority_id="talmadge-simpson",
        display_name="Talmadge Simpson",
        authority_role="System Owner",
        authority_basis="Designated preservation-governance authority",
    )


def assemble(
    recommendation_value: PreservationBaselineAcceptanceRecommendation,
    *,
    outcome: AuthorizationDecisionOutcome,
    condition_decisions: tuple[AuthorizationConditionDecision, ...] = (),
    scope: AuthorizationScope | None = None,
    pilot: PilotAuthorization | None = None,
):
    roots = recommendation_value.validation_result.candidate.scope.source_root_ids
    if scope is None:
        scope = AuthorizationScope(
            accepted_source_root_ids=(
                () if outcome is AuthorizationDecisionOutcome.REJECT else roots
            ),
            excluded_source_root_ids=(
                roots if outcome is AuthorizationDecisionOutcome.REJECT else ()
            ),
            scope_limitations=(),
        )
    return PreservationBaselineAuthorizationDecisionAssembler().assemble(
        recommendation=recommendation_value,
        outcome=outcome,
        authority=authority(),
        decided_at_utc=datetime(2026, 7, 30, 18, 0, tzinfo=UTC),
        condition_decisions=condition_decisions,
        scope=scope,
        pilot=pilot,
        retention_obligations=("retain preservation evidence",),
        supersession_eligible=True,
        rationale="Explicit accountable decision.",
    )


def test_acceptance_recommendation_can_be_authorized_or_rejected() -> None:
    value = recommendation(AcceptanceDecision.RECOMMEND_ACCEPTANCE)

    authorized = assemble(value, outcome=AuthorizationDecisionOutcome.AUTHORIZE)
    rejected = assemble(value, outcome=AuthorizationDecisionOutcome.REJECT)

    assert authorized.outcome is AuthorizationDecisionOutcome.AUTHORIZE
    assert rejected.outcome is AuthorizationDecisionOutcome.REJECT
    assert authorized.identity.authorization_id != rejected.identity.authorization_id


def test_review_recommendation_requires_all_conditions_approved() -> None:
    value = recommendation(AcceptanceDecision.RECOMMEND_REVIEW)
    approval = AuthorizationConditionDecision(
        condition_sequence=1,
        condition_code="exception_review",
        disposition=AuthorizationConditionDisposition.APPROVED,
        rationale="Exception is acceptable and retained.",
    )

    decision = assemble(
        value,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS,
        condition_decisions=(approval,),
    )

    assert decision.condition_decisions == (approval,)

    with pytest.raises(
        PreservationBaselineAuthorizationError,
        match="every review-required condition",
    ):
        assemble(
            value,
            outcome=AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS,
        )


def test_rejection_recommendation_can_only_be_rejected() -> None:
    value = recommendation(AcceptanceDecision.RECOMMEND_REJECTION)

    with pytest.raises(
        PreservationBaselineAuthorizationError,
        match="incompatible",
    ):
        assemble(
            value,
            outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        )

    rejected = assemble(value, outcome=AuthorizationDecisionOutcome.REJECT)
    assert rejected.outcome is AuthorizationDecisionOutcome.REJECT


def test_partial_scope_requires_nonempty_proper_subset() -> None:
    value = recommendation(
        AcceptanceDecision.RECOMMEND_ACCEPTANCE,
        roots=("root-a", "root-b"),
    )
    decision = assemble(
        value,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE,
        scope=AuthorizationScope(
            accepted_source_root_ids=("root-a",),
            excluded_source_root_ids=("root-b",),
            scope_limitations=("root-b remains pending",),
        ),
    )

    assert decision.scope.accepted_source_root_ids == ("root-a",)


def test_pilot_authorization_requires_pilot_metadata() -> None:
    value = recommendation(AcceptanceDecision.RECOMMEND_ACCEPTANCE)

    with pytest.raises(
        PreservationBaselineAuthorizationError,
        match="pilot metadata",
    ):
        assemble(value, outcome=AuthorizationDecisionOutcome.AUTHORIZE_PILOT)

    decision = assemble(
        value,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE_PILOT,
        pilot=PilotAuthorization(
            purpose="Validate downstream classification design",
            limitations=("no migration authority",),
        ),
    )
    assert decision.pilot is not None


def test_condition_code_mismatch_is_rejected() -> None:
    value = recommendation(AcceptanceDecision.RECOMMEND_REVIEW)
    invalid = AuthorizationConditionDecision(
        condition_sequence=1,
        condition_code="wrong-code",
        disposition=AuthorizationConditionDisposition.APPROVED,
        rationale="Approved.",
    )

    with pytest.raises(
        PreservationBaselineAuthorizationError,
        match="code does not match",
    ):
        assemble(
            value,
            outcome=AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS,
            condition_decisions=(invalid,),
        )


def test_timestamp_does_not_change_semantic_identity() -> None:
    value = recommendation(AcceptanceDecision.RECOMMEND_ACCEPTANCE)
    assembler = PreservationBaselineAuthorizationDecisionAssembler()
    common = {
        "recommendation": value,
        "outcome": AuthorizationDecisionOutcome.AUTHORIZE,
        "authority": authority(),
        "condition_decisions": (),
        "scope": AuthorizationScope(
            accepted_source_root_ids=("root-a",),
            excluded_source_root_ids=(),
            scope_limitations=(),
        ),
        "pilot": None,
        "retention_obligations": (),
        "supersession_eligible": True,
        "rationale": "Authorized.",
    }

    first = assembler.assemble(
        **common,
        decided_at_utc=datetime(2026, 7, 30, 18, 0, tzinfo=UTC),
    )
    second = assembler.assemble(
        **common,
        decided_at_utc=datetime(2026, 7, 30, 19, 0, tzinfo=UTC),
    )

    assert first.identity.authorization_id == second.identity.authorization_id
    assert first.decided_at_utc != second.decided_at_utc


def test_assembler_surface_is_side_effect_free() -> None:
    public_names = {
        name
        for name in dir(PreservationBaselineAuthorizationDecisionAssembler)
        if not name.startswith("_")
    }

    assert public_names == {"assemble"}
