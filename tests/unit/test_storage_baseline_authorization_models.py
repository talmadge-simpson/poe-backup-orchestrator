from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
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
    STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION,
    AuthorizationAuthority,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    PilotAuthorization,
    PreservationBaselineAuthorizationDecision,
    PreservationBaselineAuthorizationIdentity,
    stable_preservation_baseline_authorization_id,
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


def _recommendation(
    *,
    decision: AcceptanceDecision = AcceptanceDecision.RECOMMEND_ACCEPTANCE,
) -> PreservationBaselineAcceptanceRecommendation:
    reference = PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        source_root_id="root-a",
        schema_version="1.0",
        evidence_path=Path("/evidence/inventory.jsonl"),
        digest_path=Path("/evidence/inventory.jsonl.sha256"),
        sha256="a" * 64,
        byte_count=100,
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
            source_root_ids=("root-a",),
        ),
        observations=(
            EvidenceRequirementObservation(
                source_root_id="root-a",
                evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
                status=EvidenceRequirementStatus.PRESENT,
                evidence_reference=reference,
            ),
        ),
    )
    finding = ValidationFinding(
        sequence=1,
        category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
        severity=ValidationFindingSeverity.WARNING,
        source_root_id="root-a",
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        evidence_path=Path("/evidence/inventory.jsonl"),
        field_name="exception_count",
        expected="0",
        observed="1",
        detail="explicit exception remains visible",
    )
    findings = () if decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE else (finding,)
    validated = (
        ValidatedEvidenceReference(
            evidence_reference=reference,
            status=EvidenceValidationStatus.VERIFIED,
            calculated_sha256=reference.sha256,
            calculated_byte_count=reference.byte_count,
            sidecar_sha256=reference.sha256,
            resolved_schema_name="poe.storage.inventory-evidence",
            resolved_schema_version="1.0",
        ),
    )
    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-validation-v1",
        validated_evidence=validated,
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
        validated_evidence=validated,
        findings=findings,
    )
    if decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE:
        conditions = ()
        rationale_codes = ("no_validation_findings", "recommend_acceptance")
    elif decision is AcceptanceDecision.RECOMMEND_REVIEW:
        conditions = (
            AcceptanceCondition(
                sequence=1,
                condition_code="evidence_exception_review",
                disposition=AcceptanceConditionDisposition.REVIEW_REQUIRED,
                finding_categories=(ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,),
                finding_sequences=(1,),
                detail="review required",
            ),
        )
        rationale_codes = ("evidence_exception_review", "recommend_review")
    else:
        conditions = (
            AcceptanceCondition(
                sequence=1,
                condition_code="evidence_exception_blocking",
                disposition=AcceptanceConditionDisposition.BLOCKING,
                finding_categories=(ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,),
                finding_sequences=(1,),
                detail="blocking",
            ),
        )
        rationale_codes = ("evidence_exception_blocking", "recommend_rejection")

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


def _authority() -> AuthorizationAuthority:
    return AuthorizationAuthority(
        authority_id="talmadge-simpson",
        display_name="Talmadge Simpson",
        authority_role="System Owner",
        authority_basis="Designated preservation-governance authority",
        organization="Personal Executive Operating System",
    )


def test_schema_and_authority_normalization() -> None:
    assert STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION == "1.0"

    authority = AuthorizationAuthority(
        authority_id=" owner-1 ",
        display_name=" Owner One ",
        authority_role=" System Owner ",
        authority_basis=" Explicit designation ",
        organization=" POE ",
    )

    assert authority.authority_id == "owner-1"
    assert authority.display_name == "Owner One"
    assert authority.organization == "POE"

    with pytest.raises(ValueError, match="whitespace"):
        AuthorizationAuthority(
            authority_id="owner one",
            display_name="Owner One",
            authority_role="Owner",
            authority_basis="Designation",
        )


def test_scope_and_pilot_require_canonical_unique_values() -> None:
    with pytest.raises(ValueError, match="canonical"):
        AuthorizationScope(
            accepted_source_root_ids=("root-b", "root-a"),
            excluded_source_root_ids=(),
            scope_limitations=(),
        )

    with pytest.raises(ValueError, match="overlap"):
        AuthorizationScope(
            accepted_source_root_ids=("root-a",),
            excluded_source_root_ids=("root-a",),
            scope_limitations=(),
        )

    with pytest.raises(ValueError, match="must not be empty"):
        PilotAuthorization(purpose="test", limitations=())


def test_stable_identity_excludes_timestamp() -> None:
    recommendation = _recommendation()
    authority = _authority()
    scope = AuthorizationScope(
        accepted_source_root_ids=("root-a",),
        excluded_source_root_ids=(),
        scope_limitations=(),
    )
    first = stable_preservation_baseline_authorization_id(
        evaluation_id=recommendation.identity.evaluation_id,
        validation_id=recommendation.identity.validation_id,
        candidate_id=recommendation.identity.candidate_id,
        baseline_id=recommendation.identity.baseline_id,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        authority=authority,
        condition_decisions=(),
        scope=scope,
        pilot=None,
        retention_obligations=("retain source evidence",),
        supersession_eligible=True,
        rationale="Evidence is complete.",
    )
    second = stable_preservation_baseline_authorization_id(
        evaluation_id=recommendation.identity.evaluation_id,
        validation_id=recommendation.identity.validation_id,
        candidate_id=recommendation.identity.candidate_id,
        baseline_id=recommendation.identity.baseline_id,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        authority=authority,
        condition_decisions=(),
        scope=scope,
        pilot=None,
        retention_obligations=("retain source evidence",),
        supersession_eligible=True,
        rationale="Evidence is complete.",
    )

    assert first == second
    assert first.startswith("pbd-")


def test_authorization_decision_enforces_utc_lineage_and_immutability() -> None:
    recommendation = _recommendation()
    authority = _authority()
    scope = AuthorizationScope(
        accepted_source_root_ids=("root-a",),
        excluded_source_root_ids=(),
        scope_limitations=(),
    )
    authorization_id = stable_preservation_baseline_authorization_id(
        evaluation_id=recommendation.identity.evaluation_id,
        validation_id=recommendation.identity.validation_id,
        candidate_id=recommendation.identity.candidate_id,
        baseline_id=recommendation.identity.baseline_id,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        authority=authority,
        condition_decisions=(),
        scope=scope,
        pilot=None,
        retention_obligations=(),
        supersession_eligible=True,
        rationale="Authorized.",
    )
    decision = PreservationBaselineAuthorizationDecision(
        identity=PreservationBaselineAuthorizationIdentity(
            schema_version=STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION,
            authorization_id=authorization_id,
            evaluation_id=recommendation.identity.evaluation_id,
            validation_id=recommendation.identity.validation_id,
            candidate_id=recommendation.identity.candidate_id,
            baseline_id=recommendation.identity.baseline_id,
        ),
        recommendation=recommendation,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        authority=authority,
        decided_at_utc=datetime(2026, 7, 30, 18, 0, tzinfo=UTC),
        condition_decisions=(),
        scope=scope,
        pilot=None,
        retention_obligations=(),
        supersession_eligible=True,
        rationale="Authorized.",
    )

    with pytest.raises(FrozenInstanceError):
        decision.outcome = AuthorizationDecisionOutcome.REJECT  # type: ignore[misc]

    with pytest.raises(ValueError, match="UTC"):
        PreservationBaselineAuthorizationDecision(
            identity=decision.identity,
            recommendation=recommendation,
            outcome=AuthorizationDecisionOutcome.AUTHORIZE,
            authority=authority,
            decided_at_utc=datetime(
                2026,
                7,
                30,
                18,
                0,
                tzinfo=UTC,
            ).astimezone(timezone(timedelta(hours=1))),
            condition_decisions=(),
            scope=scope,
            pilot=None,
            retention_obligations=(),
            supersession_eligible=True,
            rationale="Authorized.",
        )


def test_authorization_models_expose_no_later_authority_fields() -> None:
    fields = set(PreservationBaselineAuthorizationDecision.__dataclass_fields__)
    prohibited = {
        "persistence_path",
        "publication_path",
        "accepted_baseline",
        "migration_authority",
        "cleanup_authority",
        "client_redirection",
        "credential",
        "token",
        "signature",
    }

    assert fields.isdisjoint(prohibited)
