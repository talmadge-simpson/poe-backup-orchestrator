"""Deterministic preservation-baseline acceptance policy evaluation."""

from __future__ import annotations

from collections import defaultdict

from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
    AcceptanceCondition,
    AcceptanceConditionDisposition,
    AcceptanceDecision,
    AcceptanceEvaluationIdentity,
    AcceptanceMode,
    AcceptancePolicy,
    PreservationBaselineAcceptanceRecommendation,
    severity_meets_threshold,
    stable_preservation_baseline_acceptance_evaluation_id,
)
from poe_backup_orchestrator.models.storage_baseline_validation import (
    PreservationBaselineValidationResult,
    ValidationFinding,
)


class PreservationBaselineAcceptanceEvaluationError(Exception):
    """Raised when deterministic acceptance evaluation cannot be produced."""


_DISPOSITION_ORDER = {
    AcceptanceConditionDisposition.BLOCKING: 0,
    AcceptanceConditionDisposition.REVIEW_REQUIRED: 1,
    AcceptanceConditionDisposition.SATISFIED: 2,
}


class PreservationBaselineAcceptanceEvaluator:
    """Apply one explicit immutable policy to one immutable validation result."""

    def evaluate(
        self,
        *,
        validation_result: PreservationBaselineValidationResult,
        policy: AcceptancePolicy,
    ) -> PreservationBaselineAcceptanceRecommendation:
        if not isinstance(validation_result, PreservationBaselineValidationResult):
            raise PreservationBaselineAcceptanceEvaluationError(
                "validation_result must be PreservationBaselineValidationResult"
            )
        if not isinstance(policy, AcceptancePolicy):
            raise PreservationBaselineAcceptanceEvaluationError("policy must be AcceptancePolicy")

        rules = {rule.finding_category: rule for rule in policy.rules}
        grouped: dict[
            tuple[AcceptanceConditionDisposition, str],
            list[ValidationFinding],
        ] = defaultdict(list)
        unmapped_present = False

        for finding in validation_result.findings:
            rule = rules.get(finding.category)
            if rule is None:
                disposition = policy.unmapped_finding_disposition
                condition_code = "unmapped_validation_finding"
                unmapped_present = True
            else:
                if severity_meets_threshold(finding.severity, rule.minimum_severity):
                    disposition = (
                        rule.strict_disposition
                        if policy.mode is AcceptanceMode.STRICT
                        else rule.review_permitted_disposition
                    )
                else:
                    disposition = AcceptanceConditionDisposition.SATISFIED
                condition_code = rule.condition_code

            grouped[(disposition, condition_code)].append(finding)

        ordered_groups = sorted(
            grouped.items(),
            key=lambda item: (
                _DISPOSITION_ORDER[item[0][0]],
                item[0][1],
                tuple(sorted({finding.category.value for finding in item[1]})),
                tuple(finding.sequence for finding in item[1]),
            ),
        )

        conditions = tuple(
            AcceptanceCondition(
                sequence=index,
                condition_code=condition_code,
                disposition=disposition,
                finding_categories=tuple(
                    sorted(
                        {finding.category for finding in findings},
                        key=lambda category: category.value,
                    )
                ),
                finding_sequences=tuple(sorted(finding.sequence for finding in findings)),
                detail=_condition_detail(
                    condition_code=condition_code,
                    disposition=disposition,
                    findings=findings,
                ),
            )
            for index, ((disposition, condition_code), findings) in enumerate(
                ordered_groups,
                start=1,
            )
        )

        decision = _decision_for(conditions)
        rationale_codes = _rationale_codes(
            conditions=conditions,
            decision=decision,
            unmapped_present=unmapped_present,
        )
        identity = validation_result.identity
        evaluation_id = stable_preservation_baseline_acceptance_evaluation_id(
            validation_id=identity.validation_id,
            candidate_id=identity.candidate_id,
            baseline_id=identity.baseline_id,
            policy_id=policy.policy_id,
            policy_version=policy.policy_version,
            mode=policy.mode,
            conditions=conditions,
            decision=decision,
            rationale_codes=rationale_codes,
        )

        try:
            return PreservationBaselineAcceptanceRecommendation(
                identity=AcceptanceEvaluationIdentity(
                    schema_version=STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
                    evaluation_id=evaluation_id,
                    validation_id=identity.validation_id,
                    candidate_id=identity.candidate_id,
                    baseline_id=identity.baseline_id,
                    policy_id=policy.policy_id,
                    policy_version=policy.policy_version,
                ),
                validation_result=validation_result,
                mode=policy.mode,
                decision=decision,
                conditions=conditions,
                rationale_codes=rationale_codes,
            )
        except ValueError as exc:
            raise PreservationBaselineAcceptanceEvaluationError(
                "acceptance recommendation invariants failed"
            ) from exc


def _decision_for(
    conditions: tuple[AcceptanceCondition, ...],
) -> AcceptanceDecision:
    dispositions = {condition.disposition for condition in conditions}
    if AcceptanceConditionDisposition.BLOCKING in dispositions:
        return AcceptanceDecision.RECOMMEND_REJECTION
    if AcceptanceConditionDisposition.REVIEW_REQUIRED in dispositions:
        return AcceptanceDecision.RECOMMEND_REVIEW
    return AcceptanceDecision.RECOMMEND_ACCEPTANCE


def _rationale_codes(
    *,
    conditions: tuple[AcceptanceCondition, ...],
    decision: AcceptanceDecision,
    unmapped_present: bool,
) -> tuple[str, ...]:
    codes = {
        condition.condition_code
        for condition in conditions
        if condition.disposition is not AcceptanceConditionDisposition.SATISFIED
    }
    if unmapped_present:
        codes.add("unmapped_validation_finding")
    if not codes:
        codes.add("no_validation_findings" if not conditions else "all_policy_conditions_satisfied")
    codes.add(decision.value)
    return tuple(sorted(codes))


def _condition_detail(
    *,
    condition_code: str,
    disposition: AcceptanceConditionDisposition,
    findings: list[ValidationFinding],
) -> str:
    categories = ", ".join(
        category.value
        for category in sorted(
            {finding.category for finding in findings},
            key=lambda category: category.value,
        )
    )
    return (
        f"{condition_code} classified {len(findings)} validation finding(s) "
        f"as {disposition.value}: {categories}"
    )
