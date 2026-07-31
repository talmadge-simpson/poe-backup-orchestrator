"""Immutable contracts for deterministic accepted-baseline classification."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_analysis import (
    AcceptedBaselineAnalysisContext,
    FrozenJsonArray,
    FrozenJsonObject,
    FrozenJsonValue,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceType,
)

STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION: Final[str] = "1.0"
STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION: Final[str] = "1.0"
BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION: Final[str] = (
    "poe.storage.baseline-classification.policy-behavior/1.0"
)
BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID: Final[str] = (
    "bea4cfe1132683da9c06988bdd361d7ef53361b760e1b94da8f30abe8a71ace5"
)

_POLICY_ID = re.compile(r"pbcp-[0-9a-f]{64}")
_OBSERVATION_SET_ID = re.compile(r"pbcos-[0-9a-f]{64}")
_SHA256 = re.compile(r"[0-9a-f]{64}")
_RULE_CODE = re.compile(r"[a-z0-9]+(?:[-_][a-z0-9]+)*")
_OPERATORS: Final[frozenset[str]] = frozenset({"exact", "member_of", "present", "absent"})


class AcceptedBaselineClassificationDimension(StrEnum):
    """The four approved Slice 6C-2 descriptive dimensions."""

    CONTENT_TYPE = "content_type"
    INVENTORY_SUPPORT_STATE = "inventory_support_state"
    CAPTURE_STATE = "capture_state"
    CONTENT_INTEGRITY_STATE = "content_integrity_state"


class AcceptedBaselineClassificationObservationKind(StrEnum):
    """Authority-neutral output kind for Slice 6C-2."""

    DESCRIPTIVE_OBSERVATION = "descriptive_observation"


class AcceptedBaselineClassificationState(StrEnum):
    """Explicit deterministic classification state."""

    CLASSIFIED = "classified"
    UNCLASSIFIED = "unclassified"
    UNKNOWN = "unknown"
    AMBIGUOUS = "ambiguous"
    CONFLICTING = "conflicting"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNSUPPORTED = "unsupported"
    NOT_APPLICABLE = "not_applicable"


_VALUE_DOMAINS: Final[dict[AcceptedBaselineClassificationDimension, tuple[str, ...]]] = {
    AcceptedBaselineClassificationDimension.CONTENT_TYPE: (
        "directory",
        "file",
        "other",
        "unsupported_object",
    ),
    AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE: (
        "supported",
        "unsupported",
    ),
    AcceptedBaselineClassificationDimension.CAPTURE_STATE: (
        "captured",
        "error",
        "excluded",
        "inaccessible",
        "not_applicable",
        "pending",
    ),
    AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE: (
        "digest_mismatch",
        "filesystem_error",
        "inaccessible",
        "insufficient_evidence",
        "missing",
        "not_applicable",
        "not_regular_file",
        "size_mismatch",
        "source_changed",
        "verified",
    ),
}


def _required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _code(value: str, field_name: str) -> str:
    normalized = _required(value, field_name)
    if _RULE_CODE.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must be a lowercase machine code")
    return normalized


def _sha256(value: str, field_name: str) -> str:
    normalized = value.strip()
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must contain 64 lowercase hexadecimal characters")
    return normalized


def _ordered_codes(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise ValueError(f"{field_name} must be an immutable tuple")
    result = tuple(_code(value, field_name) for value in values)
    if result != tuple(sorted(result)) or len(result) != len(set(result)):
        raise ValueError(f"{field_name} must be unique and lexically ordered")
    return result


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationPolicyIdentity:
    """Stable identity of one immutable classification policy."""

    schema_version: str
    classification_policy_id: str
    behavior_manifest_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION:
            raise ValueError("unsupported classification-policy schema_version")
        if _POLICY_ID.fullmatch(self.classification_policy_id) is None:
            raise ValueError("classification_policy_id must use the governed pbcp identifier")
        object.__setattr__(
            self,
            "behavior_manifest_id",
            _sha256(self.behavior_manifest_id, "behavior_manifest_id"),
        )


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationObservationSetIdentity:
    """Stable identity and predecessor keys for one observation set."""

    schema_version: str
    classification_observation_set_id: str
    analysis_context_id: str
    accepted_baseline_id: str
    analysis_profile_id: str
    classification_policy_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION:
            raise ValueError("unsupported classification schema_version")
        if _OBSERVATION_SET_ID.fullmatch(self.classification_observation_set_id) is None:
            raise ValueError(
                "classification_observation_set_id must use the governed pbcos identifier"
            )
        if not self.analysis_context_id.startswith("pbac-"):
            raise ValueError("analysis_context_id must use the governed pbac identifier")
        if not self.analysis_profile_id.startswith("pbaip-"):
            raise ValueError("analysis_profile_id must use the governed pbaip identifier")
        if _POLICY_ID.fullmatch(self.classification_policy_id) is None:
            raise ValueError("classification_policy_id must use the governed pbcp identifier")
        object.__setattr__(
            self,
            "accepted_baseline_id",
            _required(self.accepted_baseline_id, "accepted_baseline_id"),
        )


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineClassificationSubject:
    """One inventory-item subject without an absolute or inferred path."""

    source_root_id: str
    relative_path: str
    item_id: str
    item_type: str

    def __post_init__(self) -> None:
        source_root_id = _required(self.source_root_id, "source_root_id")
        relative_path = _required(self.relative_path, "relative_path")
        item_id = _required(self.item_id, "item_id")
        item_type = _required(self.item_type, "item_type")
        parts = relative_path.split("/")
        if (
            relative_path.startswith("/")
            or "\\" in relative_path
            or any(part in {"", ".", ".."} for part in parts)
        ):
            raise ValueError("relative_path must be an exact safe POSIX relative path")
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "item_type", item_type)


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineClassificationFactReference:
    """Compact semantic fact attribution for one observation."""

    evidence_semantic_id: str
    evidence_type: PreservationEvidenceType
    schema_name: str
    schema_version: str
    source_root_id: str
    item_id: str
    relative_path: str
    field_path: str
    applied_rule_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evidence_semantic_id",
            _sha256(self.evidence_semantic_id, "evidence_semantic_id"),
        )
        for field_name in (
            "schema_name",
            "schema_version",
            "source_root_id",
            "item_id",
            "field_path",
        ):
            object.__setattr__(self, field_name, _required(getattr(self, field_name), field_name))
        relative_path = _required(self.relative_path, "relative_path")
        if relative_path.startswith("/") or "\\" in relative_path:
            raise ValueError("fact relative_path must be POSIX relative")
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(
            self,
            "applied_rule_codes",
            _ordered_codes(self.applied_rule_codes, "applied_rule_codes"),
        )


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineClassificationCandidate:
    """One retained candidate and its complete rule provenance."""

    value: str
    rule_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _required(self.value, "candidate value"))
        rules = _ordered_codes(self.rule_codes, "candidate rule_codes")
        if not rules:
            raise ValueError("candidate rule_codes must not be empty")
        object.__setattr__(self, "rule_codes", rules)


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineClassificationPredicate:
    """One typed fixed predicate; rules combine predicates by conjunction."""

    field_path: str
    operator: str
    values: tuple[str, ...]

    def __post_init__(self) -> None:
        field_path = _required(self.field_path, "field_path")
        operator = _required(self.operator, "operator")
        if not isinstance(self.values, tuple):
            raise ValueError("predicate values must be an immutable tuple")
        values = tuple(_required(value, "predicate value") for value in self.values)
        if operator not in _OPERATORS:
            raise ValueError("unsupported classification predicate operator")
        if operator == "exact" and len(values) != 1:
            raise ValueError("EXACT requires exactly one value")
        if operator == "member_of" and not values:
            raise ValueError("MEMBER_OF requires at least one value")
        if operator in {"present", "absent"} and values:
            raise ValueError("PRESENT and ABSENT require no values")
        if values != tuple(sorted(values)) or len(values) != len(set(values)):
            raise ValueError("predicate values must be unique and lexically ordered")
        object.__setattr__(self, "field_path", field_path)
        object.__setattr__(self, "operator", operator)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineClassificationRule:
    """One deterministic architecture-owned classification rule."""

    dimension: AcceptedBaselineClassificationDimension
    rule_code: str
    predicates: tuple[AcceptedBaselineClassificationPredicate, ...]
    observation_kind: AcceptedBaselineClassificationObservationKind
    candidate_value: str | None
    result_state: AcceptedBaselineClassificationState
    review_required: bool
    rationale_code: str
    review_rationale_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        rule_code = _code(self.rule_code, "rule_code")
        if not isinstance(self.predicates, tuple):
            raise ValueError("rule predicates must be an immutable tuple")
        predicates = tuple(self.predicates)
        keys = tuple((item.field_path, item.operator, item.values) for item in predicates)
        if not predicates or keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("rule predicates must be unique and canonically ordered")
        candidate = (
            None
            if self.candidate_value is None
            else _required(self.candidate_value, "candidate_value")
        )
        if candidate is not None and candidate not in _VALUE_DOMAINS[self.dimension]:
            raise ValueError("candidate_value is outside the dimension value domain")
        if (
            self.result_state is AcceptedBaselineClassificationState.CLASSIFIED
            and candidate is None
        ):
            raise ValueError("CLASSIFIED rules require a candidate_value")
        if (
            self.result_state
            in {
                AcceptedBaselineClassificationState.UNSUPPORTED,
                AcceptedBaselineClassificationState.UNCLASSIFIED,
                AcceptedBaselineClassificationState.UNKNOWN,
            }
            and candidate is not None
        ):
            raise ValueError("the rule state does not permit a candidate_value")
        rationale = _code(self.rationale_code, "rationale_code")
        review_codes = _ordered_codes(self.review_rationale_codes, "review_rationale_codes")
        if self.review_required != bool(review_codes):
            raise ValueError("review_required must agree with review_rationale_codes")
        object.__setattr__(self, "rule_code", rule_code)
        object.__setattr__(self, "predicates", predicates)
        object.__setattr__(self, "candidate_value", candidate)
        object.__setattr__(self, "rationale_code", rationale)
        object.__setattr__(self, "review_rationale_codes", review_codes)


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationPolicy:
    """Immutable semantic policy for deterministic classification."""

    identity: AcceptedBaselineClassificationPolicyIdentity
    policy_version: str
    behavior_manifest_version: str
    supported_dimensions: tuple[AcceptedBaselineClassificationDimension, ...]
    value_domains: tuple[tuple[AcceptedBaselineClassificationDimension, tuple[str, ...]], ...]
    rules: tuple[AcceptedBaselineClassificationRule, ...]
    state_resolution: FrozenJsonObject
    conflict_semantics: FrozenJsonObject
    review_semantics: FrozenJsonObject
    ordering: FrozenJsonObject
    operational_exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, tuple)
            for value in (
                self.supported_dimensions,
                self.value_domains,
                self.rules,
                self.operational_exclusions,
            )
        ):
            raise ValueError("policy collection fields must be immutable tuples")
        policy_version = _required(self.policy_version, "policy_version")
        behavior_version = _required(self.behavior_manifest_version, "behavior_manifest_version")
        dimensions = tuple(self.supported_dimensions)
        expected_dimensions = tuple(
            sorted(AcceptedBaselineClassificationDimension, key=lambda item: item.value)
        )
        if dimensions != expected_dimensions:
            raise ValueError("supported_dimensions must contain exactly four ordered dimensions")
        domains = tuple(self.value_domains)
        expected_domains = tuple((dimension, _VALUE_DOMAINS[dimension]) for dimension in dimensions)
        if domains != expected_domains:
            raise ValueError("value_domains must match the approved closed vocabularies")
        rules = tuple(self.rules)
        keys = tuple((rule.dimension.value, rule.rule_code) for rule in rules)
        if len(rules) != 23:
            raise ValueError("classification policy must contain exactly 23 rules")
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("rules must be unique and canonically ordered")
        exclusions = tuple(self.operational_exclusions)
        if exclusions != tuple(sorted(exclusions)) or len(exclusions) != len(set(exclusions)):
            raise ValueError("operational_exclusions must be unique and ordered")
        expected_id = stable_accepted_baseline_classification_policy_id(
            policy_version=policy_version,
            behavior_manifest_id=self.identity.behavior_manifest_id,
            behavior_manifest_version=behavior_version,
            supported_dimensions=dimensions,
            value_domains=domains,
            rules=rules,
            state_resolution=self.state_resolution,
            conflict_semantics=self.conflict_semantics,
            review_semantics=self.review_semantics,
            ordering=self.ordering,
            operational_exclusions=exclusions,
        )
        if self.identity.classification_policy_id != expected_id:
            raise ValueError("classification_policy_id does not match policy semantics")
        object.__setattr__(self, "policy_version", policy_version)
        object.__setattr__(self, "behavior_manifest_version", behavior_version)
        object.__setattr__(self, "supported_dimensions", dimensions)
        object.__setattr__(self, "value_domains", domains)
        object.__setattr__(self, "rules", rules)
        object.__setattr__(self, "operational_exclusions", exclusions)


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationObservation:
    """One deterministic descriptive observation for one subject dimension."""

    subject: AcceptedBaselineClassificationSubject
    dimension: AcceptedBaselineClassificationDimension
    observation_kind: AcceptedBaselineClassificationObservationKind
    state: AcceptedBaselineClassificationState
    candidates: tuple[AcceptedBaselineClassificationCandidate, ...]
    selected_value: str | None
    applied_rule_codes: tuple[str, ...]
    fact_references: tuple[AcceptedBaselineClassificationFactReference, ...]
    rationale_codes: tuple[str, ...]
    review_required: bool
    review_rationale_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if any(
            not isinstance(value, tuple)
            for value in (
                self.candidates,
                self.applied_rule_codes,
                self.fact_references,
                self.rationale_codes,
                self.review_rationale_codes,
            )
        ):
            raise ValueError("observation collection fields must be immutable tuples")
        candidates = tuple(self.candidates)
        candidate_keys = tuple((item.value, item.rule_codes) for item in candidates)
        if candidate_keys != tuple(sorted(candidate_keys)) or len(candidate_keys) != len(
            set(candidate_keys)
        ):
            raise ValueError("candidates must be unique and canonically ordered")
        selected = (
            None
            if self.selected_value is None
            else _required(self.selected_value, "selected_value")
        )
        if selected is not None and selected not in _VALUE_DOMAINS[self.dimension]:
            raise ValueError("selected_value is outside the dimension value domain")
        if self.state is AcceptedBaselineClassificationState.CLASSIFIED:
            if len(candidates) != 1 or selected != candidates[0].value:
                raise ValueError("CLASSIFIED requires exactly one selected candidate")
        elif self.state is AcceptedBaselineClassificationState.INSUFFICIENT_EVIDENCE:
            if len(candidates) != 1 or selected != "insufficient_evidence":
                raise ValueError("INSUFFICIENT_EVIDENCE requires its one explicit selected value")
        elif self.state is AcceptedBaselineClassificationState.NOT_APPLICABLE:
            if len(candidates) != 1 or selected != "not_applicable":
                raise ValueError("NOT_APPLICABLE requires its one explicit selected value")
        elif self.state in {
            AcceptedBaselineClassificationState.AMBIGUOUS,
            AcceptedBaselineClassificationState.CONFLICTING,
        }:
            if len(candidates) < 2 or selected is not None:
                raise ValueError("AMBIGUOUS and CONFLICTING require multiple unselected candidates")
        elif selected is not None or candidates:
            raise ValueError("the classification state does not permit selected candidates")
        applied = _ordered_codes(self.applied_rule_codes, "applied_rule_codes")
        facts = tuple(self.fact_references)
        fact_keys = tuple(_fact_reference_key(item) for item in facts)
        if fact_keys != tuple(sorted(fact_keys)) or len(fact_keys) != len(set(fact_keys)):
            raise ValueError("fact_references must be unique and canonically ordered")
        rationales = _ordered_codes(self.rationale_codes, "rationale_codes")
        review_codes = _ordered_codes(self.review_rationale_codes, "review_rationale_codes")
        if self.review_required != bool(review_codes):
            raise ValueError("review_required must agree with review_rationale_codes")
        object.__setattr__(self, "candidates", candidates)
        object.__setattr__(self, "selected_value", selected)
        object.__setattr__(self, "applied_rule_codes", applied)
        object.__setattr__(self, "fact_references", facts)
        object.__setattr__(self, "rationale_codes", rationales)
        object.__setattr__(self, "review_rationale_codes", review_codes)


@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationObservationSet:
    """Complete deterministic classification observations for one context/policy."""

    identity: AcceptedBaselineClassificationObservationSetIdentity
    analysis_context: AcceptedBaselineAnalysisContext
    policy: AcceptedBaselineClassificationPolicy
    observations: tuple[AcceptedBaselineClassificationObservation, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.analysis_context, AcceptedBaselineAnalysisContext):
            raise ValueError("analysis_context must be AcceptedBaselineAnalysisContext")
        if not isinstance(self.policy, AcceptedBaselineClassificationPolicy):
            raise ValueError("policy must be AcceptedBaselineClassificationPolicy")
        if not isinstance(self.observations, tuple):
            raise ValueError("observations must be an immutable tuple")
        observations = tuple(self.observations)
        if not observations:
            raise ValueError("observations must not be empty")
        keys = tuple(_observation_key(item) for item in observations)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("observations must be unique and canonically ordered")
        context_identity = self.analysis_context.identity
        if self.identity.analysis_context_id != context_identity.analysis_context_id:
            raise ValueError("observation-set context identity does not match")
        if self.identity.accepted_baseline_id != context_identity.accepted_baseline_id:
            raise ValueError("observation-set accepted-baseline identity does not match")
        if self.identity.analysis_profile_id != context_identity.analysis_profile_id:
            raise ValueError("observation-set profile identity does not match")
        if self.identity.classification_policy_id != self.policy.identity.classification_policy_id:
            raise ValueError("observation-set policy identity does not match")
        expected = stable_accepted_baseline_classification_observation_set_id(
            analysis_context_id=context_identity.analysis_context_id,
            accepted_baseline_id=context_identity.accepted_baseline_id,
            analysis_profile_id=context_identity.analysis_profile_id,
            policy=self.policy,
            observations=observations,
        )
        if self.identity.classification_observation_set_id != expected:
            raise ValueError("classification_observation_set_id does not match semantics")
        object.__setattr__(self, "observations", observations)


def stable_accepted_baseline_classification_policy_id(
    *,
    policy_version: str,
    behavior_manifest_id: str,
    behavior_manifest_version: str,
    supported_dimensions: tuple[AcceptedBaselineClassificationDimension, ...],
    value_domains: tuple[tuple[AcceptedBaselineClassificationDimension, tuple[str, ...]], ...],
    rules: tuple[AcceptedBaselineClassificationRule, ...],
    state_resolution: FrozenJsonObject,
    conflict_semantics: FrozenJsonObject,
    review_semantics: FrozenJsonObject,
    ordering: FrozenJsonObject,
    operational_exclusions: tuple[str, ...],
) -> str:
    payload = {
        "schema_version": STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION,
        "policy_version": policy_version,
        "behavior_manifest_id": behavior_manifest_id,
        "behavior_manifest_version": behavior_manifest_version,
        "supported_dimensions": [item.value for item in supported_dimensions],
        "value_domains": [
            {"dimension": dimension.value, "values": list(values)}
            for dimension, values in value_domains
        ],
        "rules": [_rule_payload(rule) for rule in rules],
        "state_resolution": _frozen_object_value(state_resolution),
        "conflict_semantics": _frozen_object_value(conflict_semantics),
        "review_semantics": _frozen_object_value(review_semantics),
        "ordering": _frozen_object_value(ordering),
        "operational_exclusions": list(operational_exclusions),
    }
    return f"pbcp-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def stable_accepted_baseline_classification_observation_set_id(
    *,
    analysis_context_id: str,
    accepted_baseline_id: str,
    analysis_profile_id: str,
    policy: AcceptedBaselineClassificationPolicy,
    observations: tuple[AcceptedBaselineClassificationObservation, ...],
) -> str:
    payload = {
        "schema_version": STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION,
        "analysis_context_id": analysis_context_id,
        "accepted_baseline_id": accepted_baseline_id,
        "analysis_profile_id": analysis_profile_id,
        "classification_policy_id": policy.identity.classification_policy_id,
        "policy_version": policy.policy_version,
        "behavior_manifest_id": policy.identity.behavior_manifest_id,
        "observations": [_observation_payload(item) for item in observations],
    }
    return f"pbcos-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def _rule_payload(rule: AcceptedBaselineClassificationRule) -> dict[str, object]:
    return {
        "rule_code": rule.rule_code,
        "dimension": rule.dimension.value,
        "predicates": [
            {
                "field_path": item.field_path,
                "operator": item.operator,
                "values": list(item.values),
            }
            for item in rule.predicates
        ],
        "observation_kind": rule.observation_kind.value,
        "candidate_value": rule.candidate_value,
        "result_state": rule.result_state.value,
        "review_required": rule.review_required,
        "rationale_code": rule.rationale_code,
        "review_rationale_codes": list(rule.review_rationale_codes),
    }


def _observation_payload(
    item: AcceptedBaselineClassificationObservation,
) -> dict[str, object]:
    return {
        "subject": {
            "source_root_id": item.subject.source_root_id,
            "relative_path": item.subject.relative_path,
            "item_id": item.subject.item_id,
            "item_type": item.subject.item_type,
        },
        "dimension": item.dimension.value,
        "observation_kind": item.observation_kind.value,
        "state": item.state.value,
        "candidates": [
            {"value": candidate.value, "rule_codes": list(candidate.rule_codes)}
            for candidate in item.candidates
        ],
        "selected_value": item.selected_value,
        "applied_rule_codes": list(item.applied_rule_codes),
        "fact_references": [
            {
                "evidence_semantic_id": fact.evidence_semantic_id,
                "evidence_type": fact.evidence_type.value,
                "schema_name": fact.schema_name,
                "schema_version": fact.schema_version,
                "source_root_id": fact.source_root_id,
                "item_id": fact.item_id,
                "relative_path": fact.relative_path,
                "field_path": fact.field_path,
                "applied_rule_codes": list(fact.applied_rule_codes),
            }
            for fact in item.fact_references
        ],
        "rationale_codes": list(item.rationale_codes),
        "review_required": item.review_required,
        "review_rationale_codes": list(item.review_rationale_codes),
    }


def _observation_key(
    item: AcceptedBaselineClassificationObservation,
) -> tuple[str, str, str, str, str]:
    return (
        item.subject.source_root_id,
        item.subject.relative_path,
        item.subject.item_id,
        item.dimension.value,
        item.observation_kind.value,
    )


def _fact_reference_key(
    item: AcceptedBaselineClassificationFactReference,
) -> tuple[str, str, str, str, str]:
    return (
        item.evidence_semantic_id,
        item.source_root_id,
        item.relative_path,
        item.item_id,
        item.field_path,
    )


def _frozen_object_value(value: FrozenJsonObject) -> dict[str, object]:
    return {key: _frozen_value(item) for key, item in value.entries}


def _frozen_value(value: FrozenJsonValue) -> object:
    if isinstance(value, FrozenJsonObject):
        return _frozen_object_value(value)
    if isinstance(value, FrozenJsonArray):
        return [_frozen_value(item) for item in value.values]
    return value
