from dataclasses import FrozenInstanceError
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
    AcceptancePolicy,
    AcceptancePolicyRule,
    PreservationBaselineAcceptanceRecommendation,
    stable_preservation_baseline_acceptance_evaluation_id,
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


def _validation_result(
    findings: tuple[ValidationFinding, ...] = (),
) -> PreservationBaselineValidationResult:
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
    return PreservationBaselineValidationResult(
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


def _finding() -> ValidationFinding:
    return ValidationFinding(
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


def _condition(
    disposition: AcceptanceConditionDisposition,
) -> AcceptanceCondition:
    return AcceptanceCondition(
        sequence=1,
        condition_code="evidence_exceptions",
        disposition=disposition,
        finding_categories=(ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,),
        finding_sequences=(1,),
        detail="evidence exceptions require policy treatment",
    )


def test_acceptance_schema_and_policy_invariants() -> None:
    assert STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION == "1.0"

    rule = AcceptancePolicyRule(
        finding_category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
        minimum_severity=ValidationFindingSeverity.WARNING,
        strict_disposition=AcceptanceConditionDisposition.BLOCKING,
        review_permitted_disposition=AcceptanceConditionDisposition.REVIEW_REQUIRED,
        condition_code=" evidence_exceptions ",
    )
    policy = AcceptancePolicy(
        policy_id=" baseline-acceptance ",
        policy_version=" 1.0 ",
        mode=AcceptanceMode.STRICT,
        rules=(rule,),
        unmapped_finding_disposition=AcceptanceConditionDisposition.BLOCKING,
    )

    assert rule.condition_code == "evidence_exceptions"
    assert policy.policy_id == "baseline-acceptance"

    with pytest.raises(ValueError, match="duplicate"):
        AcceptancePolicy(
            policy_id="baseline-acceptance",
            policy_version="1.0",
            mode=AcceptanceMode.STRICT,
            rules=(rule, rule),
            unmapped_finding_disposition=AcceptanceConditionDisposition.BLOCKING,
        )

    with pytest.raises(ValueError, match="conservative"):
        AcceptancePolicy(
            policy_id="baseline-acceptance",
            policy_version="1.0",
            mode=AcceptanceMode.STRICT,
            rules=(rule,),
            unmapped_finding_disposition=AcceptanceConditionDisposition.SATISFIED,
        )


def test_rule_rejects_less_conservative_strict_disposition() -> None:
    with pytest.raises(ValueError, match="less conservative"):
        AcceptancePolicyRule(
            finding_category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
            minimum_severity=ValidationFindingSeverity.WARNING,
            strict_disposition=AcceptanceConditionDisposition.REVIEW_REQUIRED,
            review_permitted_disposition=AcceptanceConditionDisposition.BLOCKING,
            condition_code="evidence_exceptions",
        )


def test_condition_requires_canonical_unique_references() -> None:
    with pytest.raises(ValueError, match="canonical"):
        AcceptanceCondition(
            sequence=1,
            condition_code="mixed",
            disposition=AcceptanceConditionDisposition.BLOCKING,
            finding_categories=(
                ValidationFindingCategory.EVIDENCE_UNREADABLE,
                ValidationFindingCategory.EVIDENCE_MISSING,
            ),
            finding_sequences=(1, 2),
            detail="mixed",
        )

    with pytest.raises(ValueError, match="duplicates"):
        AcceptanceCondition(
            sequence=1,
            condition_code="duplicate",
            disposition=AcceptanceConditionDisposition.BLOCKING,
            finding_categories=(ValidationFindingCategory.EVIDENCE_MISSING,),
            finding_sequences=(1, 1),
            detail="duplicate",
        )


def test_stable_identity_changes_with_policy_and_decision() -> None:
    condition = _condition(AcceptanceConditionDisposition.BLOCKING)
    common = {
        "validation_id": "pbv-" + "a" * 64,
        "candidate_id": "pbc-" + "b" * 64,
        "baseline_id": "baseline-a",
        "policy_id": "baseline-acceptance",
        "mode": AcceptanceMode.STRICT,
        "conditions": (condition,),
        "rationale_codes": ("evidence_exceptions", "recommend_rejection"),
    }
    first = stable_preservation_baseline_acceptance_evaluation_id(
        **common,
        policy_version="1.0",
        decision=AcceptanceDecision.RECOMMEND_REJECTION,
    )
    second = stable_preservation_baseline_acceptance_evaluation_id(
        **common,
        policy_version="2.0",
        decision=AcceptanceDecision.RECOMMEND_REJECTION,
    )

    assert first.startswith("pba-")
    assert first != second


def test_recommendation_enforces_lineage_decision_and_immutability() -> None:
    finding = _finding()
    validation = _validation_result((finding,))
    condition = _condition(AcceptanceConditionDisposition.BLOCKING)
    rationale = ("evidence_exceptions", "recommend_rejection")
    evaluation_id = stable_preservation_baseline_acceptance_evaluation_id(
        validation_id=validation.identity.validation_id,
        candidate_id=validation.identity.candidate_id,
        baseline_id=validation.identity.baseline_id,
        policy_id="baseline-acceptance",
        policy_version="1.0",
        mode=AcceptanceMode.STRICT,
        conditions=(condition,),
        decision=AcceptanceDecision.RECOMMEND_REJECTION,
        rationale_codes=rationale,
    )
    recommendation = PreservationBaselineAcceptanceRecommendation(
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
        mode=AcceptanceMode.STRICT,
        decision=AcceptanceDecision.RECOMMEND_REJECTION,
        conditions=(condition,),
        rationale_codes=rationale,
    )

    with pytest.raises(FrozenInstanceError):
        recommendation.decision = AcceptanceDecision.RECOMMEND_ACCEPTANCE  # type: ignore[misc]

    with pytest.raises(ValueError, match="requires at least one blocking"):
        PreservationBaselineAcceptanceRecommendation(
            identity=recommendation.identity,
            validation_result=validation,
            mode=AcceptanceMode.STRICT,
            decision=AcceptanceDecision.RECOMMEND_REJECTION,
            conditions=(_condition(AcceptanceConditionDisposition.SATISFIED),),
            rationale_codes=rationale,
        )


def test_acceptance_models_expose_no_authority_fields() -> None:
    fields = set(PreservationBaselineAcceptanceRecommendation.__dataclass_fields__)
    prohibited = {
        "approval",
        "approver",
        "authorization",
        "signature",
        "exception_approval",
        "accepted_baseline",
        "migration_authority",
        "cleanup_authority",
        "published_at_utc",
    }

    assert fields.isdisjoint(prohibited)
