from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    AcceptanceConditionDisposition,
    AcceptanceDecision,
    AcceptanceMode,
    AcceptancePolicy,
    AcceptancePolicyRule,
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
from poe_backup_orchestrator.services.storage_baseline_acceptance import (
    PreservationBaselineAcceptanceEvaluationError,
    PreservationBaselineAcceptanceEvaluator,
)


def finding(
    sequence: int,
    *,
    category: ValidationFindingCategory,
    severity: ValidationFindingSeverity,
) -> ValidationFinding:
    return ValidationFinding(
        sequence=sequence,
        category=category,
        severity=severity,
        source_root_id="root-a",
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        evidence_path=Path("/evidence/inventory.jsonl"),
        field_name=None,
        expected=None,
        observed=None,
        detail=f"{category.value} observed",
    )


def validation_result(
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


def policy(mode: AcceptanceMode = AcceptanceMode.STRICT) -> AcceptancePolicy:
    return AcceptancePolicy(
        policy_id="baseline-acceptance",
        policy_version="1.0",
        mode=mode,
        rules=(
            AcceptancePolicyRule(
                finding_category=ValidationFindingCategory.CONTRADICTORY_EVIDENCE,
                minimum_severity=ValidationFindingSeverity.ERROR,
                strict_disposition=AcceptanceConditionDisposition.BLOCKING,
                review_permitted_disposition=AcceptanceConditionDisposition.BLOCKING,
                condition_code="evidence_contradiction",
            ),
            AcceptancePolicyRule(
                finding_category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
                minimum_severity=ValidationFindingSeverity.WARNING,
                strict_disposition=AcceptanceConditionDisposition.BLOCKING,
                review_permitted_disposition=AcceptanceConditionDisposition.REVIEW_REQUIRED,
                condition_code="evidence_exception_review",
            ),
            AcceptancePolicyRule(
                finding_category=ValidationFindingCategory.SOURCE_CHANGE_OBSERVED,
                minimum_severity=ValidationFindingSeverity.ERROR,
                strict_disposition=AcceptanceConditionDisposition.BLOCKING,
                review_permitted_disposition=AcceptanceConditionDisposition.BLOCKING,
                condition_code="source_change",
            ),
        ),
        unmapped_finding_disposition=AcceptanceConditionDisposition.BLOCKING,
    )


def evaluate(
    findings: tuple[ValidationFinding, ...] = (),
    *,
    mode: AcceptanceMode = AcceptanceMode.STRICT,
):
    return PreservationBaselineAcceptanceEvaluator().evaluate(
        validation_result=validation_result(findings),
        policy=policy(mode),
    )


def test_empty_findings_recommend_acceptance() -> None:
    recommendation = evaluate()

    assert recommendation.decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE
    assert recommendation.conditions == ()
    assert recommendation.rationale_codes == (
        "no_validation_findings",
        "recommend_acceptance",
    )


def test_below_threshold_finding_is_explicitly_satisfied() -> None:
    recommendation = evaluate(
        (
            finding(
                1,
                category=ValidationFindingCategory.CONTRADICTORY_EVIDENCE,
                severity=ValidationFindingSeverity.WARNING,
            ),
        )
    )

    assert recommendation.decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE
    assert recommendation.conditions[0].disposition is AcceptanceConditionDisposition.SATISFIED
    assert recommendation.conditions[0].finding_sequences == (1,)


def test_strict_and_review_modes_apply_category_specific_policy() -> None:
    findings = (
        finding(
            1,
            category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
            severity=ValidationFindingSeverity.WARNING,
        ),
    )

    strict = evaluate(findings)
    review = evaluate(findings, mode=AcceptanceMode.REVIEW_PERMITTED)

    assert strict.decision is AcceptanceDecision.RECOMMEND_REJECTION
    assert review.decision is AcceptanceDecision.RECOMMEND_REVIEW
    assert strict.identity.evaluation_id != review.identity.evaluation_id


def test_blocking_precedes_review() -> None:
    recommendation = evaluate(
        (
            finding(
                1,
                category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
                severity=ValidationFindingSeverity.WARNING,
            ),
            finding(
                2,
                category=ValidationFindingCategory.CONTRADICTORY_EVIDENCE,
                severity=ValidationFindingSeverity.ERROR,
            ),
        ),
        mode=AcceptanceMode.REVIEW_PERMITTED,
    )

    assert recommendation.decision is AcceptanceDecision.RECOMMEND_REJECTION
    assert tuple(condition.disposition for condition in recommendation.conditions) == (
        AcceptanceConditionDisposition.BLOCKING,
        AcceptanceConditionDisposition.REVIEW_REQUIRED,
    )


def test_shared_condition_code_groups_findings_deterministically() -> None:
    grouped_policy = AcceptancePolicy(
        policy_id="grouped",
        policy_version="1.0",
        mode=AcceptanceMode.STRICT,
        rules=(
            AcceptancePolicyRule(
                finding_category=ValidationFindingCategory.EVIDENCE_MISSING,
                minimum_severity=ValidationFindingSeverity.WARNING,
                strict_disposition=AcceptanceConditionDisposition.BLOCKING,
                review_permitted_disposition=AcceptanceConditionDisposition.BLOCKING,
                condition_code="evidence_availability",
            ),
            AcceptancePolicyRule(
                finding_category=ValidationFindingCategory.EVIDENCE_UNREADABLE,
                minimum_severity=ValidationFindingSeverity.WARNING,
                strict_disposition=AcceptanceConditionDisposition.BLOCKING,
                review_permitted_disposition=AcceptanceConditionDisposition.BLOCKING,
                condition_code="evidence_availability",
            ),
        ),
        unmapped_finding_disposition=AcceptanceConditionDisposition.BLOCKING,
    )
    result = validation_result(
        (
            finding(
                1,
                category=ValidationFindingCategory.EVIDENCE_UNREADABLE,
                severity=ValidationFindingSeverity.ERROR,
            ),
            finding(
                2,
                category=ValidationFindingCategory.EVIDENCE_MISSING,
                severity=ValidationFindingSeverity.ERROR,
            ),
        )
    )

    recommendation = PreservationBaselineAcceptanceEvaluator().evaluate(
        validation_result=result,
        policy=grouped_policy,
    )

    assert len(recommendation.conditions) == 1
    assert recommendation.conditions[0].finding_categories == (
        ValidationFindingCategory.EVIDENCE_MISSING,
        ValidationFindingCategory.EVIDENCE_UNREADABLE,
    )
    assert recommendation.conditions[0].finding_sequences == (1, 2)


def test_unmapped_findings_fail_conservatively_and_remain_explicit() -> None:
    recommendation = evaluate(
        (
            finding(
                1,
                category=ValidationFindingCategory.CAPTURE_INCOMPLETE,
                severity=ValidationFindingSeverity.INFORMATIONAL,
            ),
        )
    )

    assert recommendation.decision is AcceptanceDecision.RECOMMEND_REJECTION
    assert recommendation.conditions[0].condition_code == "unmapped_validation_finding"
    assert "unmapped_validation_finding" in recommendation.rationale_codes


def test_repeated_evaluation_is_equal_and_inputs_remain_immutable() -> None:
    result = validation_result(
        (
            finding(
                1,
                category=ValidationFindingCategory.SOURCE_CHANGE_OBSERVED,
                severity=ValidationFindingSeverity.ERROR,
            ),
        )
    )
    acceptance_policy = policy()
    evaluator = PreservationBaselineAcceptanceEvaluator()

    first = evaluator.evaluate(
        validation_result=result,
        policy=acceptance_policy,
    )
    second = evaluator.evaluate(
        validation_result=result,
        policy=acceptance_policy,
    )

    assert first == second
    with pytest.raises(FrozenInstanceError):
        acceptance_policy.policy_version = "2.0"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("validation_result", object(), "validation_result must"),
        ("policy", object(), "policy must"),
    ],
)
def test_evaluator_rejects_invalid_inputs(
    field: str,
    value: object,
    message: str,
) -> None:
    arguments = {
        "validation_result": validation_result(),
        "policy": policy(),
    }
    arguments[field] = value

    with pytest.raises(PreservationBaselineAcceptanceEvaluationError, match=message):
        PreservationBaselineAcceptanceEvaluator().evaluate(**arguments)


def test_evaluator_surface_has_no_authority_or_side_effect_methods() -> None:
    public_names = {
        name for name in dir(PreservationBaselineAcceptanceEvaluator) if not name.startswith("_")
    }

    assert public_names == {"evaluate"}
