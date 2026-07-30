"""Immutable preservation-baseline acceptance-evaluation contracts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_validation import (
    PreservationBaselineValidationResult,
    ValidationFindingCategory,
    ValidationFindingSeverity,
)

STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION: Final[str] = "1.0"

_EVALUATION_ID_PATTERN = re.compile(r"pba-[0-9a-f]{64}")
_SEVERITY_RANK: Final[dict[ValidationFindingSeverity, int]] = {
    ValidationFindingSeverity.INFORMATIONAL: 0,
    ValidationFindingSeverity.WARNING: 1,
    ValidationFindingSeverity.ERROR: 2,
    ValidationFindingSeverity.CRITICAL: 3,
}
_DISPOSITION_RANK: Final[dict[AcceptanceConditionDisposition, int]]


class AcceptanceMode(StrEnum):
    """Automated evaluation mode without governance authority."""

    STRICT = "strict"
    REVIEW_PERMITTED = "review_permitted"


class AcceptanceDecision(StrEnum):
    """Authority-neutral automated recommendation."""

    RECOMMEND_ACCEPTANCE = "recommend_acceptance"
    RECOMMEND_REVIEW = "recommend_review"
    RECOMMEND_REJECTION = "recommend_rejection"


class AcceptanceConditionDisposition(StrEnum):
    """Policy classification for one deterministic condition."""

    SATISFIED = "satisfied"
    REVIEW_REQUIRED = "review_required"
    BLOCKING = "blocking"


_DISPOSITION_RANK = {
    AcceptanceConditionDisposition.SATISFIED: 0,
    AcceptanceConditionDisposition.REVIEW_REQUIRED: 1,
    AcceptanceConditionDisposition.BLOCKING: 2,
}


def _normalize_required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_code(value: str, field_name: str) -> str:
    normalized = _normalize_required(value, field_name)
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


@dataclass(frozen=True, slots=True)
class AcceptanceCondition:
    """Compact policy conclusion referencing exact validation findings."""

    sequence: int
    condition_code: str
    disposition: AcceptanceConditionDisposition
    finding_categories: tuple[ValidationFindingCategory, ...]
    finding_sequences: tuple[int, ...]
    detail: str

    def __post_init__(self) -> None:
        if self.sequence <= 0:
            raise ValueError("sequence must be positive")

        condition_code = _normalize_code(self.condition_code, "condition_code")
        categories = tuple(self.finding_categories)
        sequences = tuple(self.finding_sequences)
        detail = _normalize_required(self.detail, "detail")

        if not categories:
            raise ValueError("finding_categories must not be empty")
        if categories != tuple(sorted(categories, key=lambda item: item.value)):
            raise ValueError("finding_categories must use canonical ordering")
        if len(set(categories)) != len(categories):
            raise ValueError("finding_categories must not contain duplicates")

        if not sequences:
            raise ValueError("finding_sequences must not be empty")
        if any(sequence <= 0 for sequence in sequences):
            raise ValueError("finding_sequences must contain positive values")
        if sequences != tuple(sorted(sequences)):
            raise ValueError("finding_sequences must use canonical ordering")
        if len(set(sequences)) != len(sequences):
            raise ValueError("finding_sequences must not contain duplicates")

        object.__setattr__(self, "condition_code", condition_code)
        object.__setattr__(self, "finding_categories", categories)
        object.__setattr__(self, "finding_sequences", sequences)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class AcceptancePolicyRule:
    """Explicit mapping from a validation category to policy semantics."""

    finding_category: ValidationFindingCategory
    minimum_severity: ValidationFindingSeverity
    strict_disposition: AcceptanceConditionDisposition
    review_permitted_disposition: AcceptanceConditionDisposition
    condition_code: str

    def __post_init__(self) -> None:
        condition_code = _normalize_code(self.condition_code, "condition_code")
        if (
            _DISPOSITION_RANK[self.strict_disposition]
            < _DISPOSITION_RANK[self.review_permitted_disposition]
        ):
            raise ValueError(
                "strict_disposition must not be less conservative than review_permitted_disposition"
            )
        object.__setattr__(self, "condition_code", condition_code)


@dataclass(frozen=True, slots=True)
class AcceptancePolicy:
    """Immutable and versioned acceptance-evaluation policy."""

    policy_id: str
    policy_version: str
    mode: AcceptanceMode
    rules: tuple[AcceptancePolicyRule, ...]
    unmapped_finding_disposition: AcceptanceConditionDisposition

    def __post_init__(self) -> None:
        policy_id = _normalize_code(self.policy_id, "policy_id")
        policy_version = _normalize_code(self.policy_version, "policy_version")
        rules = tuple(self.rules)
        categories = tuple(rule.finding_category.value for rule in rules)

        if categories != tuple(sorted(categories)):
            raise ValueError("rules must use canonical finding-category ordering")
        if len(set(categories)) != len(categories):
            raise ValueError("rules must not contain duplicate finding categories")
        if self.unmapped_finding_disposition is AcceptanceConditionDisposition.SATISFIED:
            raise ValueError("unmapped_finding_disposition must be conservative")

        object.__setattr__(self, "policy_id", policy_id)
        object.__setattr__(self, "policy_version", policy_version)
        object.__setattr__(self, "rules", rules)


@dataclass(frozen=True, slots=True)
class AcceptanceEvaluationIdentity:
    """Stable evaluation identity with exact validation and policy lineage."""

    schema_version: str
    evaluation_id: str
    validation_id: str
    candidate_id: str
    baseline_id: str
    policy_id: str
    policy_version: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION:
            raise ValueError("unsupported acceptance schema_version")
        if _EVALUATION_ID_PATTERN.fullmatch(self.evaluation_id) is None:
            raise ValueError("evaluation_id must use the governed pba identifier")

        for field_name in (
            "validation_id",
            "candidate_id",
            "baseline_id",
            "policy_id",
            "policy_version",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_code(getattr(self, field_name), field_name),
            )


def stable_preservation_baseline_acceptance_evaluation_id(
    *,
    validation_id: str,
    candidate_id: str,
    baseline_id: str,
    policy_id: str,
    policy_version: str,
    mode: AcceptanceMode,
    conditions: tuple[AcceptanceCondition, ...],
    decision: AcceptanceDecision,
    rationale_codes: tuple[str, ...],
) -> str:
    """Derive stable identity from canonical acceptance-evaluation semantics."""

    payload = {
        "schema_version": STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
        "validation_id": _normalize_code(validation_id, "validation_id"),
        "candidate_id": _normalize_code(candidate_id, "candidate_id"),
        "baseline_id": _normalize_code(baseline_id, "baseline_id"),
        "policy_id": _normalize_code(policy_id, "policy_id"),
        "policy_version": _normalize_code(policy_version, "policy_version"),
        "mode": mode.value,
        "conditions": [
            {
                "sequence": condition.sequence,
                "condition_code": condition.condition_code,
                "disposition": condition.disposition.value,
                "finding_categories": [category.value for category in condition.finding_categories],
                "finding_sequences": list(condition.finding_sequences),
                "detail": condition.detail,
            }
            for condition in conditions
        ],
        "decision": decision.value,
        "rationale_codes": [_normalize_code(code, "rationale_code") for code in rationale_codes],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return f"pba-{hashlib.sha256(encoded).hexdigest()}"


@dataclass(frozen=True, slots=True)
class PreservationBaselineAcceptanceRecommendation:
    """Immutable automated recommendation without governance authority."""

    identity: AcceptanceEvaluationIdentity
    validation_result: PreservationBaselineValidationResult
    mode: AcceptanceMode
    decision: AcceptanceDecision
    conditions: tuple[AcceptanceCondition, ...]
    rationale_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.validation_result, PreservationBaselineValidationResult):
            raise ValueError("validation_result must be PreservationBaselineValidationResult")

        conditions = tuple(self.conditions)
        rationale_codes = tuple(
            _normalize_code(code, "rationale_code") for code in self.rationale_codes
        )

        expected_sequences = tuple(range(1, len(conditions) + 1))
        if tuple(condition.sequence for condition in conditions) != expected_sequences:
            raise ValueError("condition sequences must be contiguous beginning with one")
        if len(set(rationale_codes)) != len(rationale_codes):
            raise ValueError("rationale_codes must not contain duplicates")
        if rationale_codes != tuple(sorted(rationale_codes)):
            raise ValueError("rationale_codes must use canonical ordering")
        if not rationale_codes:
            raise ValueError("rationale_codes must not be empty")

        validation_identity = self.validation_result.identity
        if self.identity.validation_id != validation_identity.validation_id:
            raise ValueError("evaluation validation identity does not match validation result")
        if self.identity.candidate_id != validation_identity.candidate_id:
            raise ValueError("evaluation candidate identity does not match validation result")
        if self.identity.baseline_id != validation_identity.baseline_id:
            raise ValueError("evaluation baseline identity does not match validation result")

        dispositions = {condition.disposition for condition in conditions}
        if self.decision is AcceptanceDecision.RECOMMEND_ACCEPTANCE:
            if AcceptanceConditionDisposition.BLOCKING in dispositions:
                raise ValueError("acceptance recommendation must not contain blocking conditions")
            if AcceptanceConditionDisposition.REVIEW_REQUIRED in dispositions:
                raise ValueError(
                    "acceptance recommendation must not contain review-required conditions"
                )
        elif self.decision is AcceptanceDecision.RECOMMEND_REVIEW:
            if AcceptanceConditionDisposition.BLOCKING in dispositions:
                raise ValueError("review recommendation must not contain blocking conditions")
            if AcceptanceConditionDisposition.REVIEW_REQUIRED not in dispositions:
                raise ValueError(
                    "review recommendation requires at least one review-required condition"
                )
        elif AcceptanceConditionDisposition.BLOCKING not in dispositions:
            raise ValueError("rejection recommendation requires at least one blocking condition")

        stable_id = stable_preservation_baseline_acceptance_evaluation_id(
            validation_id=validation_identity.validation_id,
            candidate_id=validation_identity.candidate_id,
            baseline_id=validation_identity.baseline_id,
            policy_id=self.identity.policy_id,
            policy_version=self.identity.policy_version,
            mode=self.mode,
            conditions=conditions,
            decision=self.decision,
            rationale_codes=rationale_codes,
        )
        if self.identity.evaluation_id != stable_id:
            raise ValueError("evaluation_id does not match semantic recommendation")

        referenced_sequences = {
            sequence for condition in conditions for sequence in condition.finding_sequences
        }
        available_sequences = {finding.sequence for finding in self.validation_result.findings}
        if not referenced_sequences.issubset(available_sequences):
            raise ValueError("conditions reference nonexistent validation findings")
        if available_sequences != referenced_sequences:
            raise ValueError("every validation finding must be accounted for")

        object.__setattr__(self, "conditions", conditions)
        object.__setattr__(self, "rationale_codes", rationale_codes)


def severity_meets_threshold(
    severity: ValidationFindingSeverity,
    minimum_severity: ValidationFindingSeverity,
) -> bool:
    """Compare validation severity using governed domain ordering."""

    return _SEVERITY_RANK[severity] >= _SEVERITY_RANK[minimum_severity]
