"""Immutable contracts for deterministic classification finding generation."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_classification import (
    AcceptedBaselineClassificationCandidate,
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationFactReference,
    AcceptedBaselineClassificationObservation,
    AcceptedBaselineClassificationObservationKind,
    AcceptedBaselineClassificationObservationSet,
    AcceptedBaselineClassificationState,
)

STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION: Final[str] = "1.0"
STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION: Final[str] = "1.0"

_POLICY_ID = re.compile(r"pbcfp-[0-9a-f]{64}")
_FINDING_ID = re.compile(r"pbcf-[0-9a-f]{64}")
_RESULT_ID = re.compile(r"pbcfr-[0-9a-f]{64}")
_OBSERVATION_SET_ID = re.compile(r"pbcos-[0-9a-f]{64}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_CODE = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")


class AcceptedBaselineClassificationFindingCategory(StrEnum):
    """The eight approved Slice 6C-3 finding categories."""

    POLICY_NONCOVERAGE = "policy_noncoverage"
    CLASSIFICATION_UNCERTAINTY = "classification_uncertainty"
    CLASSIFICATION_CONFLICT = "classification_conflict"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNSUPPORTED_CLASSIFICATION = "unsupported_classification"
    CLASSIFICATION_REVIEW = "classification_review"
    CAPTURE_CONDITION = "capture_condition"
    INTEGRITY_CONDITION = "integrity_condition"


class AcceptedBaselineClassificationFindingSeverity(StrEnum):
    """Descriptive, non-authoritative finding severity."""

    WARNING = "warning"
    ERROR = "error"


def _required(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _code(value: str, name: str) -> str:
    normalized = _required(value, name)
    if _CODE.fullmatch(normalized) is None:
        raise ValueError(f"{name} must be a lowercase machine code")
    return normalized


def _digest(value: str, name: str) -> str:
    normalized = _required(value, name)
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{name} must contain 64 lowercase hexadecimal characters")
    return normalized


def _ordered_codes(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise ValueError(f"{name} must be an immutable tuple")
    result = tuple(_code(value, name) for value in values)
    if result != tuple(sorted(result)) or len(result) != len(set(result)):
        raise ValueError(f"{name} must be unique and lexically ordered")
    return result


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFindingPolicyIdentity:
    """Stable identity for one immutable finding policy."""

    schema_version: str
    classification_finding_policy_id: str
    behavior_manifest_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported finding-policy schema_version")
        if not isinstance(self.classification_finding_policy_id, str) or (
            _POLICY_ID.fullmatch(self.classification_finding_policy_id) is None
        ):
            raise ValueError("classification_finding_policy_id must use pbcfp")
        object.__setattr__(
            self,
            "behavior_manifest_id",
            _digest(self.behavior_manifest_id, "behavior_manifest_id"),
        )


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFindingIdentity:
    """Stable semantic identity for one finding."""

    schema_version: str
    classification_finding_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION:
            raise ValueError("unsupported finding schema_version")
        if not isinstance(self.classification_finding_id, str) or (
            _FINDING_ID.fullmatch(self.classification_finding_id) is None
        ):
            raise ValueError("classification_finding_id must use pbcf")


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFindingResultIdentity:
    """Stable semantic identity and predecessor keys for one finding result."""

    schema_version: str
    classification_finding_result_id: str
    classification_observation_set_id: str
    classification_finding_policy_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION:
            raise ValueError("unsupported finding-result schema_version")
        if not isinstance(self.classification_finding_result_id, str) or (
            _RESULT_ID.fullmatch(self.classification_finding_result_id) is None
        ):
            raise ValueError("classification_finding_result_id must use pbcfr")
        if not isinstance(self.classification_observation_set_id, str) or (
            _OBSERVATION_SET_ID.fullmatch(self.classification_observation_set_id) is None
        ):
            raise ValueError("classification_observation_set_id must use pbcos with a digest")
        if not isinstance(self.classification_finding_policy_id, str) or (
            _POLICY_ID.fullmatch(self.classification_finding_policy_id) is None
        ):
            raise ValueError("classification_finding_policy_id must use pbcfp")


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineClassificationFindingRule:
    """One exact-conjunction finding rule."""

    rule_code: str
    accepted_states: tuple[AcceptedBaselineClassificationState, ...]
    accepted_dimensions: tuple[AcceptedBaselineClassificationDimension, ...]
    accepted_selected_values: tuple[str, ...]
    required_review: bool | None
    category: AcceptedBaselineClassificationFindingCategory
    severity: AcceptedBaselineClassificationFindingSeverity
    finding_code: str
    rationale_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.category, AcceptedBaselineClassificationFindingCategory):
            raise ValueError("category must use the closed finding-category vocabulary")
        if not isinstance(self.severity, AcceptedBaselineClassificationFindingSeverity):
            raise ValueError("severity must use the closed finding-severity vocabulary")
        object.__setattr__(self, "rule_code", _code(self.rule_code, "rule_code"))
        for name in ("accepted_states", "accepted_dimensions", "accepted_selected_values"):
            if not isinstance(getattr(self, name), tuple):
                raise ValueError(f"{name} must be an immutable tuple")
        states = tuple(self.accepted_states)
        if any(not isinstance(item, AcceptedBaselineClassificationState) for item in states):
            raise ValueError("accepted_states must use the closed classification-state vocabulary")
        if not states or states != tuple(sorted(states, key=lambda item: item.value)):
            raise ValueError("accepted_states must be nonempty and canonically ordered")
        if len(states) != len(set(states)):
            raise ValueError("accepted_states must be unique")
        dimensions = tuple(self.accepted_dimensions)
        if any(
            not isinstance(item, AcceptedBaselineClassificationDimension) for item in dimensions
        ):
            raise ValueError(
                "accepted_dimensions must use the closed classification-dimension vocabulary"
            )
        if dimensions != tuple(sorted(dimensions, key=lambda item: item.value)) or len(
            dimensions
        ) != len(set(dimensions)):
            raise ValueError("accepted_dimensions must be unique and canonically ordered")
        values = tuple(
            _required(value, "accepted_selected_value") for value in self.accepted_selected_values
        )
        if values != tuple(sorted(values)) or len(values) != len(set(values)):
            raise ValueError("accepted_selected_values must be unique and lexically ordered")
        if self.required_review not in (True, False, None):
            raise ValueError("required_review must be True, False, or None")
        object.__setattr__(self, "finding_code", _code(self.finding_code, "finding_code"))
        object.__setattr__(self, "rationale_code", _code(self.rationale_code, "rationale_code"))
        object.__setattr__(self, "accepted_states", states)
        object.__setattr__(self, "accepted_dimensions", dimensions)
        object.__setattr__(self, "accepted_selected_values", values)


def _domains_intersect(left: tuple[object, ...], right: tuple[object, ...]) -> bool:
    return not left or not right or bool(set(left).intersection(right))


def _finding_rules_overlap(
    left: AcceptedBaselineClassificationFindingRule,
    right: AcceptedBaselineClassificationFindingRule,
) -> bool:
    """Return whether two exact rule domains contain a common observation shape."""

    return (
        _domains_intersect(left.accepted_states, right.accepted_states)
        and _domains_intersect(left.accepted_dimensions, right.accepted_dimensions)
        and _domains_intersect(left.accepted_selected_values, right.accepted_selected_values)
        and (
            left.required_review is None
            or right.required_review is None
            or left.required_review == right.required_review
        )
    )


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFindingPolicy:
    """Complete immutable policy for deterministic finding generation."""

    identity: AcceptedBaselineClassificationFindingPolicyIdentity
    policy_version: str
    behavior_manifest_version: str
    rules: tuple[AcceptedBaselineClassificationFindingRule, ...]
    benign_no_finding_codes: tuple[str, ...]
    category_vocabulary: tuple[AcceptedBaselineClassificationFindingCategory, ...]
    severity_vocabulary: tuple[AcceptedBaselineClassificationFindingSeverity, ...]
    operational_exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.identity, AcceptedBaselineClassificationFindingPolicyIdentity):
            raise ValueError("identity must be AcceptedBaselineClassificationFindingPolicyIdentity")
        for name in (
            "rules",
            "benign_no_finding_codes",
            "category_vocabulary",
            "severity_vocabulary",
            "operational_exclusions",
        ):
            if not isinstance(getattr(self, name), tuple):
                raise ValueError(f"{name} must be an immutable tuple")
        policy_version = _required(self.policy_version, "policy_version")
        behavior_version = _required(self.behavior_manifest_version, "behavior_manifest_version")
        rules = tuple(self.rules)
        if any(not isinstance(rule, AcceptedBaselineClassificationFindingRule) for rule in rules):
            raise ValueError("rules must contain classification finding rules")
        keys = tuple(_finding_rule_key(rule) for rule in rules)
        if len(rules) != 12:
            raise ValueError("finding policy must contain exactly 12 rules")
        if keys != tuple(sorted(keys)) or len({rule.rule_code for rule in rules}) != len(rules):
            raise ValueError("finding rules must be unique and canonically ordered")
        for index, left in enumerate(rules):
            for right in rules[index + 1 :]:
                if _finding_rules_overlap(left, right):
                    raise ValueError("finding policy rules must be pairwise non-overlapping")
        benign = _ordered_codes(self.benign_no_finding_codes, "benign_no_finding_codes")
        categories = tuple(self.category_vocabulary)
        expected_categories = tuple(
            sorted(AcceptedBaselineClassificationFindingCategory, key=lambda item: item.value)
        )
        if categories != expected_categories:
            raise ValueError("category_vocabulary must contain exactly eight ordered values")
        severities = tuple(self.severity_vocabulary)
        expected_severities = tuple(
            sorted(AcceptedBaselineClassificationFindingSeverity, key=lambda item: item.value)
        )
        if severities != expected_severities:
            raise ValueError("severity_vocabulary must contain exactly two ordered values")
        exclusions = _ordered_codes(self.operational_exclusions, "operational_exclusions")
        expected = stable_accepted_baseline_classification_finding_policy_id(
            policy_version=policy_version,
            behavior_manifest_id=self.identity.behavior_manifest_id,
            behavior_manifest_version=behavior_version,
            rules=rules,
            benign_no_finding_codes=benign,
            category_vocabulary=categories,
            severity_vocabulary=severities,
            operational_exclusions=exclusions,
        )
        if self.identity.classification_finding_policy_id != expected:
            raise ValueError("classification_finding_policy_id does not match semantics")
        object.__setattr__(self, "policy_version", policy_version)
        object.__setattr__(self, "behavior_manifest_version", behavior_version)
        object.__setattr__(self, "rules", rules)
        object.__setattr__(self, "benign_no_finding_codes", benign)
        object.__setattr__(self, "category_vocabulary", categories)
        object.__setattr__(self, "severity_vocabulary", severities)
        object.__setattr__(self, "operational_exclusions", exclusions)


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationObservationReference:
    """Compact immutable reference to exactly one predecessor observation."""

    classification_observation_set_id: str
    source_root_id: str
    relative_path: str
    item_id: str
    dimension: AcceptedBaselineClassificationDimension
    observation_kind: AcceptedBaselineClassificationObservationKind
    state: AcceptedBaselineClassificationState
    selected_value: str | None
    candidates: tuple[AcceptedBaselineClassificationCandidate, ...]
    applied_classification_rule_codes: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    review_required: bool
    review_rationale_codes: tuple[str, ...]
    semantic_fact_references: tuple[AcceptedBaselineClassificationFactReference, ...]
    contributing_finding_rule_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.classification_observation_set_id, str) or (
            _OBSERVATION_SET_ID.fullmatch(self.classification_observation_set_id) is None
        ):
            raise ValueError("classification_observation_set_id must use pbcos with a digest")
        if not isinstance(self.dimension, AcceptedBaselineClassificationDimension):
            raise ValueError("dimension must use the closed classification-dimension vocabulary")
        if not isinstance(self.observation_kind, AcceptedBaselineClassificationObservationKind):
            raise ValueError(
                "observation_kind must use the closed classification-observation vocabulary"
            )
        if not isinstance(self.state, AcceptedBaselineClassificationState):
            raise ValueError("state must use the closed classification-state vocabulary")
        if not isinstance(self.review_required, bool):
            raise ValueError("review_required must be bool")
        for name in ("source_root_id", "relative_path", "item_id"):
            object.__setattr__(self, name, _required(getattr(self, name), name))
        if self.selected_value is not None and not isinstance(self.selected_value, str):
            raise ValueError("selected_value must be a string or None")
        parts = self.relative_path.split("/")
        if (
            self.relative_path.startswith("/")
            or "\\" in self.relative_path
            or any(part in {"", ".", ".."} for part in parts)
        ):
            raise ValueError("relative_path must be an exact safe POSIX relative path")
        for name in (
            "candidates",
            "applied_classification_rule_codes",
            "rationale_codes",
            "review_rationale_codes",
            "semantic_fact_references",
            "contributing_finding_rule_codes",
        ):
            if not isinstance(getattr(self, name), tuple):
                raise ValueError(f"{name} must be an immutable tuple")
        object.__setattr__(
            self,
            "applied_classification_rule_codes",
            _ordered_codes(
                self.applied_classification_rule_codes,
                "applied_classification_rule_codes",
            ),
        )
        candidates = tuple(self.candidates)
        if any(
            not isinstance(item, AcceptedBaselineClassificationCandidate) for item in candidates
        ):
            raise ValueError("candidates must contain classification candidates")
        candidate_keys = tuple((item.value, item.rule_codes) for item in candidates)
        if candidate_keys != tuple(sorted(candidate_keys)) or len(candidate_keys) != len(
            set(candidate_keys)
        ):
            raise ValueError("candidates must preserve canonical unique order")
        object.__setattr__(self, "candidates", candidates)
        object.__setattr__(
            self, "rationale_codes", _ordered_codes(self.rationale_codes, "rationale_codes")
        )
        review_codes = _ordered_codes(self.review_rationale_codes, "review_rationale_codes")
        if self.review_required != bool(review_codes):
            raise ValueError("review_required must agree with review_rationale_codes")
        object.__setattr__(self, "review_rationale_codes", review_codes)
        facts = tuple(self.semantic_fact_references)
        if any(not isinstance(item, AcceptedBaselineClassificationFactReference) for item in facts):
            raise ValueError("semantic_fact_references must contain classification fact references")
        if facts != tuple(sorted(facts)) or len(facts) != len(set(facts)):
            raise ValueError("semantic_fact_references must preserve canonical unique order")
        object.__setattr__(self, "semantic_fact_references", facts)
        object.__setattr__(
            self,
            "contributing_finding_rule_codes",
            _ordered_codes(
                self.contributing_finding_rule_codes,
                "contributing_finding_rule_codes",
            ),
        )


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFinding:
    """One deterministic non-authoritative finding."""

    identity: AcceptedBaselineClassificationFindingIdentity
    category: AcceptedBaselineClassificationFindingCategory
    severity: AcceptedBaselineClassificationFindingSeverity
    finding_code: str
    rationale_codes: tuple[str, ...]
    contributing_finding_rule_codes: tuple[str, ...]
    observation_reference: AcceptedBaselineClassificationObservationReference

    def __post_init__(self) -> None:
        if not isinstance(self.identity, AcceptedBaselineClassificationFindingIdentity):
            raise ValueError("identity must be AcceptedBaselineClassificationFindingIdentity")
        if not isinstance(
            self.observation_reference, AcceptedBaselineClassificationObservationReference
        ):
            raise ValueError(
                "observation_reference must be AcceptedBaselineClassificationObservationReference"
            )
        if not isinstance(self.category, AcceptedBaselineClassificationFindingCategory):
            raise ValueError("category must use the closed finding-category vocabulary")
        if not isinstance(self.severity, AcceptedBaselineClassificationFindingSeverity):
            raise ValueError("severity must use the closed finding-severity vocabulary")
        object.__setattr__(self, "finding_code", _code(self.finding_code, "finding_code"))
        rationales = _ordered_codes(self.rationale_codes, "rationale_codes")
        rule_codes = _ordered_codes(
            self.contributing_finding_rule_codes, "contributing_finding_rule_codes"
        )
        if not rationales or not rule_codes:
            raise ValueError("finding rationale and rule provenance must not be empty")
        if rule_codes != self.observation_reference.contributing_finding_rule_codes:
            raise ValueError("finding rule provenance must agree with observation reference")
        object.__setattr__(self, "rationale_codes", rationales)
        object.__setattr__(self, "contributing_finding_rule_codes", rule_codes)


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFindingResult:
    """Complete deterministic findings for one observation-set/policy pair."""

    identity: AcceptedBaselineClassificationFindingResultIdentity
    observation_set: AcceptedBaselineClassificationObservationSet
    policy: AcceptedBaselineClassificationFindingPolicy
    findings: tuple[AcceptedBaselineClassificationFinding, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.identity, AcceptedBaselineClassificationFindingResultIdentity):
            raise ValueError("identity must be AcceptedBaselineClassificationFindingResultIdentity")
        if not isinstance(self.observation_set, AcceptedBaselineClassificationObservationSet):
            raise ValueError("observation_set must be AcceptedBaselineClassificationObservationSet")
        if not isinstance(self.policy, AcceptedBaselineClassificationFindingPolicy):
            raise ValueError("policy must be AcceptedBaselineClassificationFindingPolicy")
        if not isinstance(self.findings, tuple):
            raise ValueError("findings must be an immutable tuple")
        findings = tuple(self.findings)
        if any(not isinstance(item, AcceptedBaselineClassificationFinding) for item in findings):
            raise ValueError("findings must contain classification findings")
        keys = tuple(_finding_key(item) for item in findings)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("findings must be unique and canonically ordered")
        expected_sources = []
        for observation in self.observation_set.observations:
            matches = tuple(
                rule
                for rule in self.policy.rules
                if _finding_rule_matches_observation(rule, observation)
            )
            if len(matches) > 1:
                raise ValueError("observation matches more than one finding policy rule")
            if matches:
                expected_sources.append(
                    (
                        observation.subject.source_root_id,
                        observation.subject.relative_path,
                        observation.subject.item_id,
                        observation.dimension,
                        observation.observation_kind,
                        matches[0].rule_code,
                    )
                )
        actual_sources = [
            (
                finding.observation_reference.source_root_id,
                finding.observation_reference.relative_path,
                finding.observation_reference.item_id,
                finding.observation_reference.dimension,
                finding.observation_reference.observation_kind,
                finding.contributing_finding_rule_codes[0],
            )
            for finding in findings
        ]
        if tuple(actual_sources) != tuple(expected_sources):
            raise ValueError("findings must completely represent every policy-matched observation")
        if self.identity.classification_observation_set_id != (
            self.observation_set.identity.classification_observation_set_id
        ):
            raise ValueError("finding-result observation-set identity does not match")
        if self.identity.classification_finding_policy_id != (
            self.policy.identity.classification_finding_policy_id
        ):
            raise ValueError("finding-result policy identity does not match")
        for finding in findings:
            reference = finding.observation_reference
            if reference.classification_observation_set_id != (
                self.observation_set.identity.classification_observation_set_id
            ):
                raise ValueError("finding observation-set reference does not match")
            resolved = tuple(
                observation
                for observation in self.observation_set.observations
                if (
                    observation.subject.source_root_id == reference.source_root_id
                    and observation.subject.relative_path == reference.relative_path
                    and observation.subject.item_id == reference.item_id
                    and observation.dimension is reference.dimension
                    and observation.observation_kind is reference.observation_kind
                )
            )
            if len(resolved) != 1 or not _observation_reference_matches(reference, resolved[0]):
                raise ValueError("finding observation reference does not resolve")
            matching_rules = tuple(
                rule
                for rule in self.policy.rules
                if rule.rule_code in finding.contributing_finding_rule_codes
                and _finding_rule_matches_reference(rule, reference)
            )
            if len(matching_rules) != 1:
                raise ValueError("finding does not resolve to exactly one policy rule")
            rule = matching_rules[0]
            if (
                finding.contributing_finding_rule_codes != (rule.rule_code,)
                or finding.category is not rule.category
                or finding.severity is not rule.severity
                or finding.finding_code != rule.finding_code
                or finding.rationale_codes != (rule.rationale_code,)
            ):
                raise ValueError("finding semantics do not match the resolved policy rule")
            expected_finding_id = stable_accepted_baseline_classification_finding_id(
                observation_reference=finding.observation_reference,
                finding_policy_id=self.policy.identity.classification_finding_policy_id,
                behavior_manifest_id=self.policy.identity.behavior_manifest_id,
                category=finding.category,
                severity=finding.severity,
                finding_code=finding.finding_code,
                rationale_codes=finding.rationale_codes,
                contributing_finding_rule_codes=finding.contributing_finding_rule_codes,
            )
            if finding.identity.classification_finding_id != expected_finding_id:
                raise ValueError("classification_finding_id does not match semantics")
        expected_result = stable_accepted_baseline_classification_finding_result_id(
            observation_set=self.observation_set,
            policy=self.policy,
            findings=findings,
        )
        if self.identity.classification_finding_result_id != expected_result:
            raise ValueError("classification_finding_result_id does not match semantics")
        object.__setattr__(self, "findings", findings)


def stable_accepted_baseline_classification_finding_policy_id(
    *,
    policy_version: str,
    behavior_manifest_id: str,
    behavior_manifest_version: str,
    rules: tuple[AcceptedBaselineClassificationFindingRule, ...],
    benign_no_finding_codes: tuple[str, ...],
    category_vocabulary: tuple[AcceptedBaselineClassificationFindingCategory, ...],
    severity_vocabulary: tuple[AcceptedBaselineClassificationFindingSeverity, ...],
    operational_exclusions: tuple[str, ...],
) -> str:
    payload = {
        "schema_version": STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION,
        "policy_version": policy_version,
        "behavior_manifest_id": behavior_manifest_id,
        "behavior_manifest_version": behavior_manifest_version,
        "rules": [_rule_payload(rule) for rule in rules],
        "benign_no_finding_codes": list(benign_no_finding_codes),
        "category_vocabulary": [item.value for item in category_vocabulary],
        "severity_vocabulary": [item.value for item in severity_vocabulary],
        "operational_exclusions": list(operational_exclusions),
    }
    return f"pbcfp-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def stable_accepted_baseline_classification_finding_id(
    *,
    observation_reference: AcceptedBaselineClassificationObservationReference,
    finding_policy_id: str,
    behavior_manifest_id: str,
    category: AcceptedBaselineClassificationFindingCategory,
    severity: AcceptedBaselineClassificationFindingSeverity,
    finding_code: str,
    rationale_codes: tuple[str, ...],
    contributing_finding_rule_codes: tuple[str, ...],
) -> str:
    payload = {
        "schema_version": STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
        "classification_finding_policy_id": finding_policy_id,
        "behavior_manifest_id": behavior_manifest_id,
        "observation_reference": _observation_reference_payload(observation_reference),
        "category": category.value,
        "severity": severity.value,
        "finding_code": finding_code,
        "rationale_codes": list(rationale_codes),
        "contributing_finding_rule_codes": list(contributing_finding_rule_codes),
    }
    return f"pbcf-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def stable_accepted_baseline_classification_finding_result_id(
    *,
    observation_set: AcceptedBaselineClassificationObservationSet,
    policy: AcceptedBaselineClassificationFindingPolicy,
    findings: tuple[AcceptedBaselineClassificationFinding, ...],
) -> str:
    context = observation_set.analysis_context.identity
    payload = {
        "schema_version": STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
        "classification_observation_set_id": (
            observation_set.identity.classification_observation_set_id
        ),
        "analysis_context_id": context.analysis_context_id,
        "accepted_baseline_id": context.accepted_baseline_id,
        "analysis_profile_id": context.analysis_profile_id,
        "classification_policy_id": observation_set.policy.identity.classification_policy_id,
        "classification_behavior_id": observation_set.policy.identity.behavior_manifest_id,
        "classification_finding_policy_id": policy.identity.classification_finding_policy_id,
        "finding_policy_version": policy.policy_version,
        "finding_behavior_id": policy.identity.behavior_manifest_id,
        "findings": [_finding_payload(item) for item in findings],
    }
    return f"pbcfr-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def _finding_rule_key(rule: AcceptedBaselineClassificationFindingRule) -> tuple[str, str, str]:
    return (
        rule.accepted_states[0].value,
        rule.accepted_dimensions[0].value if rule.accepted_dimensions else "",
        rule.rule_code,
    )


def _finding_rule_matches_reference(
    rule: AcceptedBaselineClassificationFindingRule,
    reference: AcceptedBaselineClassificationObservationReference,
) -> bool:
    return (
        reference.state in rule.accepted_states
        and (not rule.accepted_dimensions or reference.dimension in rule.accepted_dimensions)
        and (
            not rule.accepted_selected_values
            or reference.selected_value in rule.accepted_selected_values
        )
        and (rule.required_review is None or reference.review_required is rule.required_review)
    )


def _finding_rule_matches_observation(
    rule: AcceptedBaselineClassificationFindingRule,
    observation: AcceptedBaselineClassificationObservation,
) -> bool:
    return (
        observation.state in rule.accepted_states
        and (not rule.accepted_dimensions or observation.dimension in rule.accepted_dimensions)
        and (
            not rule.accepted_selected_values
            or observation.selected_value in rule.accepted_selected_values
        )
        and (rule.required_review is None or observation.review_required is rule.required_review)
    )


def _finding_key(
    finding: AcceptedBaselineClassificationFinding,
) -> tuple[str, str, str, str, str, str, str]:
    reference = finding.observation_reference
    return (
        reference.source_root_id,
        reference.relative_path,
        reference.item_id,
        reference.dimension.value,
        reference.observation_kind.value,
        finding.category.value,
        finding.finding_code,
    )


def _rule_payload(rule: AcceptedBaselineClassificationFindingRule) -> dict[str, object]:
    return {
        "rule_code": rule.rule_code,
        "accepted_states": [item.value for item in rule.accepted_states],
        "accepted_dimensions": [item.value for item in rule.accepted_dimensions],
        "accepted_selected_values": list(rule.accepted_selected_values),
        "required_review": rule.required_review,
        "category": rule.category.value,
        "severity": rule.severity.value,
        "finding_code": rule.finding_code,
        "rationale_code": rule.rationale_code,
    }


def _observation_reference_payload(
    reference: AcceptedBaselineClassificationObservationReference,
) -> dict[str, object]:
    return {
        "classification_observation_set_id": reference.classification_observation_set_id,
        "source_root_id": reference.source_root_id,
        "relative_path": reference.relative_path,
        "item_id": reference.item_id,
        "dimension": reference.dimension.value,
        "observation_kind": reference.observation_kind.value,
        "state": reference.state.value,
        "selected_value": reference.selected_value,
        "candidates": [
            {"value": item.value, "rule_codes": list(item.rule_codes)}
            for item in reference.candidates
        ],
        "applied_classification_rule_codes": list(reference.applied_classification_rule_codes),
        "rationale_codes": list(reference.rationale_codes),
        "review_required": reference.review_required,
        "review_rationale_codes": list(reference.review_rationale_codes),
        "semantic_fact_references": [
            {
                "evidence_semantic_id": item.evidence_semantic_id,
                "evidence_type": item.evidence_type.value,
                "schema_name": item.schema_name,
                "schema_version": item.schema_version,
                "source_root_id": item.source_root_id,
                "item_id": item.item_id,
                "relative_path": item.relative_path,
                "field_path": item.field_path,
                "applied_rule_codes": list(item.applied_rule_codes),
            }
            for item in reference.semantic_fact_references
        ],
        "contributing_finding_rule_codes": list(reference.contributing_finding_rule_codes),
    }


def _finding_payload(finding: AcceptedBaselineClassificationFinding) -> dict[str, object]:
    return {
        "classification_finding_id": finding.identity.classification_finding_id,
        "category": finding.category.value,
        "severity": finding.severity.value,
        "finding_code": finding.finding_code,
        "rationale_codes": list(finding.rationale_codes),
        "contributing_finding_rule_codes": list(finding.contributing_finding_rule_codes),
        "observation_reference": _observation_reference_payload(finding.observation_reference),
    }


def _observation_reference_matches(
    reference: AcceptedBaselineClassificationObservationReference,
    observation: AcceptedBaselineClassificationObservation,
) -> bool:
    """Return whether a compact reference exactly reproduces one observation."""

    return (
        reference.source_root_id == observation.subject.source_root_id
        and reference.relative_path == observation.subject.relative_path
        and reference.item_id == observation.subject.item_id
        and reference.dimension is observation.dimension
        and reference.observation_kind is observation.observation_kind
        and reference.state is observation.state
        and reference.selected_value == observation.selected_value
        and reference.candidates == observation.candidates
        and reference.applied_classification_rule_codes == observation.applied_rule_codes
        and reference.rationale_codes == observation.rationale_codes
        and reference.review_required == observation.review_required
        and reference.review_rationale_codes == observation.review_rationale_codes
        and reference.semantic_fact_references == observation.fact_references
    )
