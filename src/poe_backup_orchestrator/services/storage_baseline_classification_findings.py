"""Deterministic Slice 6C-3 classification finding generation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_analysis import (
    AcceptedBaselineAnalysisEvidenceStatus,
    FrozenJsonArray,
    FrozenJsonObject,
    stable_accepted_baseline_analysis_context_id,
    stable_accepted_baseline_analysis_profile_id,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import PreservationEvidenceType
from poe_backup_orchestrator.models.storage_baseline_classification import (
    BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID,
    BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION,
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationObservation,
    AcceptedBaselineClassificationObservationSet,
    AcceptedBaselineClassificationState,
    stable_accepted_baseline_classification_observation_set_id,
    stable_accepted_baseline_classification_policy_id,
)
from poe_backup_orchestrator.models.storage_baseline_classification_findings import (
    STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION,
    STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
    AcceptedBaselineClassificationFinding,
    AcceptedBaselineClassificationFindingCategory,
    AcceptedBaselineClassificationFindingIdentity,
    AcceptedBaselineClassificationFindingPolicy,
    AcceptedBaselineClassificationFindingPolicyIdentity,
    AcceptedBaselineClassificationFindingResult,
    AcceptedBaselineClassificationFindingResultIdentity,
    AcceptedBaselineClassificationFindingRule,
    AcceptedBaselineClassificationFindingSeverity,
    AcceptedBaselineClassificationObservationReference,
    _finding_rules_overlap,
    _observation_reference_matches,
    stable_accepted_baseline_classification_finding_id,
    stable_accepted_baseline_classification_finding_policy_id,
    stable_accepted_baseline_classification_finding_result_id,
)

BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION: Final[str] = (
    "poe.storage.baseline-classification.finding-policy-behavior/1.0"
)
BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID: Final[str] = (
    "5fb9bef7fdbcf63b2bab8347e088a01fad9b35c2bb5f89ccee321f938f2fa9fa"
)

_BENIGN_CODES: Final[tuple[str, ...]] = (
    "benign_capture_captured",
    "benign_classified_unmapped",
    "benign_directory_integrity_not_applicable",
    "benign_integrity_verified",
    "benign_not_applicable",
)
_OPERATIONAL_EXCLUSIONS: Final[tuple[str, ...]] = (
    "approval",
    "blocking",
    "cache_state",
    "destination",
    "execution_host",
    "execution_timestamp",
    "filesystem_transport_path",
    "lock_state",
    "logging_detail",
    "memory_identity",
    "migration",
    "object_identity",
    "persistence_path",
    "publication_path",
    "readiness",
    "recommendation",
    "replay_state",
    "service_instance",
)


class AcceptedBaselineClassificationFindingError(RuntimeError):
    """Base error for deterministic classification finding generation."""


class AcceptedBaselineClassificationFindingInputError(AcceptedBaselineClassificationFindingError):
    """The predecessor observation set failed semantic validation."""


class AcceptedBaselineClassificationFindingPolicyError(AcceptedBaselineClassificationFindingError):
    """The configured finding policy is not architecture conformant."""


class AcceptedBaselineClassificationFindingEvaluationError(
    AcceptedBaselineClassificationFindingError
):
    """Structurally valid input could not be evaluated consistently."""


@dataclass(slots=True)
class AcceptedBaselineClassificationFindingService:
    """Generate non-authoritative findings from one immutable observation set."""

    policy: AcceptedBaselineClassificationFindingPolicy = field(
        default_factory=lambda: _default_policy()
    )

    def __post_init__(self) -> None:
        if not isinstance(self.policy, AcceptedBaselineClassificationFindingPolicy):
            raise ValueError("policy must be AcceptedBaselineClassificationFindingPolicy")
        _verify_policy(self.policy)

    def generate_findings(
        self,
        observation_set: AcceptedBaselineClassificationObservationSet,
    ) -> AcceptedBaselineClassificationFindingResult:
        """Return deterministic findings without rerunning predecessor services."""

        if not isinstance(observation_set, AcceptedBaselineClassificationObservationSet):
            raise AcceptedBaselineClassificationFindingInputError(
                "observation_set must be AcceptedBaselineClassificationObservationSet"
            )
        _verify_policy(self.policy)
        _verify_observation_set(observation_set)
        try:
            findings: list[AcceptedBaselineClassificationFinding] = []
            for observation in observation_set.observations:
                matches = tuple(rule for rule in self.policy.rules if _matches(rule, observation))
                if len(matches) > 1:
                    raise AcceptedBaselineClassificationFindingEvaluationError(
                        "more than one finding rule matched one observation"
                    )
                if not matches:
                    if observation.review_required and not _benign(observation, self.policy):
                        raise AcceptedBaselineClassificationFindingPolicyError(
                            "review-required observation is unsupported by finding policy"
                        )
                    if not _benign(observation, self.policy):
                        raise AcceptedBaselineClassificationFindingPolicyError(
                            "observation is unsupported by finding policy"
                        )
                    continue
                findings.append(
                    _build_finding(observation_set, self.policy, observation, matches[0])
                )
            ordered = tuple(sorted(findings, key=_finding_key))
            if len({_finding_key(item) for item in ordered}) != len(ordered):
                raise AcceptedBaselineClassificationFindingEvaluationError("duplicate finding key")
            result_id = stable_accepted_baseline_classification_finding_result_id(
                observation_set=observation_set,
                policy=self.policy,
                findings=ordered,
            )
            return AcceptedBaselineClassificationFindingResult(
                identity=AcceptedBaselineClassificationFindingResultIdentity(
                    STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
                    result_id,
                    observation_set.identity.classification_observation_set_id,
                    self.policy.identity.classification_finding_policy_id,
                ),
                observation_set=observation_set,
                policy=self.policy,
                findings=ordered,
            )
        except AcceptedBaselineClassificationFindingError:
            raise
        except (TypeError, ValueError) as exc:
            raise AcceptedBaselineClassificationFindingEvaluationError(
                "classification finding evaluation failed"
            ) from exc


def _build_finding(observation_set, policy, observation, rule):
    reference = AcceptedBaselineClassificationObservationReference(
        classification_observation_set_id=(
            observation_set.identity.classification_observation_set_id
        ),
        source_root_id=observation.subject.source_root_id,
        relative_path=observation.subject.relative_path,
        item_id=observation.subject.item_id,
        dimension=observation.dimension,
        observation_kind=observation.observation_kind,
        state=observation.state,
        selected_value=observation.selected_value,
        candidates=observation.candidates,
        applied_classification_rule_codes=observation.applied_rule_codes,
        rationale_codes=observation.rationale_codes,
        review_required=observation.review_required,
        review_rationale_codes=observation.review_rationale_codes,
        semantic_fact_references=observation.fact_references,
        contributing_finding_rule_codes=(rule.rule_code,),
    )
    if not _observation_reference_matches(reference, observation):
        raise AcceptedBaselineClassificationFindingEvaluationError(
            "observation reference does not resolve"
        )
    finding_id = stable_accepted_baseline_classification_finding_id(
        observation_reference=reference,
        finding_policy_id=policy.identity.classification_finding_policy_id,
        behavior_manifest_id=policy.identity.behavior_manifest_id,
        category=rule.category,
        severity=rule.severity,
        finding_code=rule.finding_code,
        rationale_codes=(rule.rationale_code,),
        contributing_finding_rule_codes=(rule.rule_code,),
    )
    return AcceptedBaselineClassificationFinding(
        identity=AcceptedBaselineClassificationFindingIdentity(
            STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION, finding_id
        ),
        category=rule.category,
        severity=rule.severity,
        finding_code=rule.finding_code,
        rationale_codes=(rule.rationale_code,),
        contributing_finding_rule_codes=(rule.rule_code,),
        observation_reference=reference,
    )


def _matches(rule, observation):
    return (
        observation.state in rule.accepted_states
        and (not rule.accepted_dimensions or observation.dimension in rule.accepted_dimensions)
        and (
            not rule.accepted_selected_values
            or observation.selected_value in rule.accepted_selected_values
        )
        and (rule.required_review is None or observation.review_required is rule.required_review)
    )


def _benign(
    observation: AcceptedBaselineClassificationObservation,
    policy: AcceptedBaselineClassificationFindingPolicy,
) -> bool:
    if observation.state is AcceptedBaselineClassificationState.NOT_APPLICABLE:
        return True
    if observation.state is not AcceptedBaselineClassificationState.CLASSIFIED:
        return False
    if observation.review_required:
        return False
    if (
        observation.dimension is AcceptedBaselineClassificationDimension.CAPTURE_STATE
        and observation.selected_value == "captured"
    ):
        return True
    if (
        observation.dimension is AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE
        and observation.selected_value == "verified"
    ):
        return True
    concerning_shape = any(
        rule.accepted_states == (AcceptedBaselineClassificationState.CLASSIFIED,)
        and (not rule.accepted_dimensions or observation.dimension in rule.accepted_dimensions)
        and (
            not rule.accepted_selected_values
            or observation.selected_value in rule.accepted_selected_values
        )
        for rule in policy.rules
    )
    return not concerning_shape


def _verify_policy(policy: AcceptedBaselineClassificationFindingPolicy) -> None:
    try:
        expected_categories = tuple(
            sorted(AcceptedBaselineClassificationFindingCategory, key=lambda item: item.value)
        )
        expected_severities = tuple(
            sorted(AcceptedBaselineClassificationFindingSeverity, key=lambda item: item.value)
        )
        if (
            policy.policy_version != "1.0"
            or policy.benign_no_finding_codes != _BENIGN_CODES
            or policy.category_vocabulary != expected_categories
            or policy.severity_vocabulary != expected_severities
            or policy.operational_exclusions != _OPERATIONAL_EXCLUSIONS
            or policy.behavior_manifest_version
            != BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION
            or policy.identity.behavior_manifest_id
            != BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID
        ):
            raise ValueError("unsupported finding-policy behavior")
        if hashlib.sha256(_canonical_bytes(_behavior_manifest(policy.rules))).hexdigest() != (
            BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID
        ):
            raise ValueError("finding-policy behavior manifest digest mismatch")
        if len(policy.rules) != 12 or len({rule.rule_code for rule in policy.rules}) != 12:
            raise ValueError("finding policy must contain exactly 12 unique rules")
        pairs = 0
        for index, left in enumerate(policy.rules):
            for right in policy.rules[index + 1 :]:
                pairs += 1
                if _finding_rules_overlap(left, right):
                    raise ValueError("finding-policy rule overlap")
        if pairs != 66:
            raise ValueError("finding policy pair-count mismatch")
        expected = stable_accepted_baseline_classification_finding_policy_id(
            policy_version=policy.policy_version,
            behavior_manifest_id=policy.identity.behavior_manifest_id,
            behavior_manifest_version=policy.behavior_manifest_version,
            rules=policy.rules,
            benign_no_finding_codes=policy.benign_no_finding_codes,
            category_vocabulary=policy.category_vocabulary,
            severity_vocabulary=policy.severity_vocabulary,
            operational_exclusions=policy.operational_exclusions,
        )
        if policy.identity.classification_finding_policy_id != expected:
            raise ValueError("finding-policy identity mismatch")
    except (TypeError, ValueError) as exc:
        raise AcceptedBaselineClassificationFindingPolicyError(
            "classification finding policy validation failed"
        ) from exc


def _verify_observation_set(observation_set) -> None:
    try:
        context = observation_set.analysis_context
        profile = context.profile
        profile_id = stable_accepted_baseline_analysis_profile_id(
            profile_version=profile.profile_version,
            resource_profile_version=profile.resource_profile_version,
            evidence_rules=profile.evidence_rules,
            missing_evidence_behavior=profile.missing_evidence_behavior,
            unsupported_evidence_behavior=profile.unsupported_evidence_behavior,
            adapter_registry_id=profile.adapter_registry_id,
            fact_projection_id=profile.fact_projection_id,
            maximum_inventory_evidence_bytes=profile.maximum_inventory_evidence_bytes,
            maximum_content_integrity_evidence_bytes=profile.maximum_content_integrity_evidence_bytes,
            maximum_inventory_items_per_root=profile.maximum_inventory_items_per_root,
            maximum_integrity_observations_per_root=profile.maximum_integrity_observations_per_root,
            maximum_aggregate_evidence_bytes=profile.maximum_aggregate_evidence_bytes,
            maximum_aggregate_projected_items=profile.maximum_aggregate_projected_items,
            maximum_inventory_ndjson_record_bytes=profile.maximum_inventory_ndjson_record_bytes,
            json_nesting_depth_limit=profile.json_nesting_depth_limit,
            deterministic_ordering=profile.deterministic_ordering,
        )
        if profile.identity.analysis_profile_id != profile_id:
            raise ValueError("analysis profile identity mismatch")
        evidence_by_id = {}
        for evidence in context.authenticated_evidence:
            if evidence.status is not AcceptedBaselineAnalysisEvidenceStatus.AUTHENTICATED:
                raise ValueError("context evidence is not authenticated")
            if evidence.semantic_facts is None or evidence.evidence_semantic_id is None:
                raise ValueError("authenticated evidence semantics are incomplete")
            digest = hashlib.sha256(_canonical_bytes(_thaw(evidence.semantic_facts))).hexdigest()
            if digest != evidence.evidence_semantic_id:
                raise ValueError("evidence semantic identity mismatch")
            if digest in evidence_by_id:
                raise ValueError("authenticated evidence semantic identity is duplicate")
            evidence_by_id[digest] = evidence
        context_id = stable_accepted_baseline_analysis_context_id(
            accepted_baseline_id=context.identity.accepted_baseline_id,
            profile=profile,
            authenticated_evidence=context.authenticated_evidence,
            lineage_only_evidence=context.lineage_only_evidence,
        )
        if context.identity.analysis_context_id != context_id:
            raise ValueError("analysis context identity mismatch")
        if context.identity.analysis_profile_id != profile.identity.analysis_profile_id:
            raise ValueError("analysis context profile lineage mismatch")
        if context.identity.accepted_baseline_id != (
            context.accepted_baseline.identity.accepted_baseline_id
        ):
            raise ValueError("accepted-baseline lineage mismatch")
        classification_policy = observation_set.policy
        if (
            classification_policy.identity.behavior_manifest_id
            != BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID
            or classification_policy.behavior_manifest_version
            != BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION
        ):
            raise AcceptedBaselineClassificationFindingPolicyError(
                "unsupported predecessor classification behavior"
            )
        classification_policy_id = stable_accepted_baseline_classification_policy_id(
            policy_version=classification_policy.policy_version,
            behavior_manifest_id=classification_policy.identity.behavior_manifest_id,
            behavior_manifest_version=classification_policy.behavior_manifest_version,
            supported_dimensions=classification_policy.supported_dimensions,
            value_domains=classification_policy.value_domains,
            rules=classification_policy.rules,
            state_resolution=classification_policy.state_resolution,
            conflict_semantics=classification_policy.conflict_semantics,
            review_semantics=classification_policy.review_semantics,
            ordering=classification_policy.ordering,
            operational_exclusions=classification_policy.operational_exclusions,
        )
        if classification_policy.identity.classification_policy_id != classification_policy_id:
            raise ValueError("classification policy identity mismatch")
        if observation_set.identity.classification_policy_id != (
            classification_policy.identity.classification_policy_id
        ):
            raise ValueError("observation-set policy lineage mismatch")
        observation_keys = tuple(_observation_key(item) for item in observation_set.observations)
        if observation_keys != tuple(sorted(observation_keys)) or len(observation_keys) != len(
            set(observation_keys)
        ):
            raise AcceptedBaselineClassificationFindingEvaluationError(
                "observation keys are duplicate or unordered"
            )
        for observation in observation_set.observations:
            try:
                replace(observation)
            except (TypeError, ValueError) as exc:
                raise AcceptedBaselineClassificationFindingEvaluationError(
                    "classification observation contains an impossible combination"
                ) from exc
            for fact in observation.fact_references:
                evidence = evidence_by_id.get(fact.evidence_semantic_id)
                if evidence is None or not _fact_reference_resolves(fact, evidence):
                    raise AcceptedBaselineClassificationFindingEvaluationError(
                        "observation fact reference does not resolve"
                    )
                if (
                    fact.source_root_id,
                    fact.relative_path,
                    fact.item_id,
                ) != (
                    observation.subject.source_root_id,
                    observation.subject.relative_path,
                    observation.subject.item_id,
                ):
                    raise AcceptedBaselineClassificationFindingEvaluationError(
                        "observation fact subject reference does not resolve"
                    )
        observation_set_id = stable_accepted_baseline_classification_observation_set_id(
            analysis_context_id=context.identity.analysis_context_id,
            accepted_baseline_id=context.identity.accepted_baseline_id,
            analysis_profile_id=context.identity.analysis_profile_id,
            policy=classification_policy,
            observations=observation_set.observations,
        )
        if observation_set.identity.classification_observation_set_id != observation_set_id:
            raise ValueError("classification observation-set identity mismatch")
        if observation_set.identity.analysis_context_id != context.identity.analysis_context_id:
            raise ValueError("observation-set context lineage mismatch")
        if observation_set.identity.analysis_profile_id != profile.identity.analysis_profile_id:
            raise ValueError("observation-set profile lineage mismatch")
        if observation_set.identity.accepted_baseline_id != context.identity.accepted_baseline_id:
            raise ValueError("observation-set accepted-baseline lineage mismatch")
    except AcceptedBaselineClassificationFindingError:
        raise
    except (TypeError, ValueError) as exc:
        raise AcceptedBaselineClassificationFindingInputError(
            "classification observation-set semantic validation failed"
        ) from exc


def _fact_reference_resolves(fact, evidence) -> bool:
    if (
        fact.evidence_type is not evidence.observation.evidence_type
        or fact.schema_name != evidence.schema_name
        or fact.schema_version != evidence.schema_version
        or fact.source_root_id != evidence.observation.source_root_id
        or evidence.semantic_facts is None
    ):
        return False
    facts = _thaw(evidence.semantic_facts)
    if fact.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        if not isinstance(facts, list) or not facts or not isinstance(facts[0], dict):
            return False
        if facts[0].get("source_root_id") != fact.source_root_id:
            return False
        rows = tuple(
            row
            for row in facts[1:]
            if isinstance(row, dict)
            and row.get("relative_path") == fact.relative_path
            and row.get("item_id") == fact.item_id
        )
        if len(rows) != 1:
            return False
        row = rows[0]
        if fact.field_path == "inventory.support_status":
            return "support_status" in row
        if fact.field_path == "inventory.item_type":
            return "item_type" in row
        if fact.field_path == "inventory.capture_status":
            return isinstance(row.get("record"), dict) and "capture_status" in row["record"]
        return False
    if fact.evidence_type is PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE:
        if not isinstance(facts, dict) or facts.get("source_root_id") != fact.source_root_id:
            return False
        rows = facts.get("evidence")
        if not isinstance(rows, list):
            return False
        matches = tuple(
            row
            for row in rows
            if isinstance(row, dict)
            and row.get("relative_path") == fact.relative_path
            and row.get("item_id") == fact.item_id
        )
        return (
            len(matches) == 1 and fact.field_path == "integrity.outcome" and "outcome" in matches[0]
        )
    return False


def _default_policy() -> AcceptedBaselineClassificationFindingPolicy:
    rules = _default_rules()
    categories = tuple(
        sorted(AcceptedBaselineClassificationFindingCategory, key=lambda item: item.value)
    )
    severities = tuple(
        sorted(AcceptedBaselineClassificationFindingSeverity, key=lambda item: item.value)
    )
    policy_id = stable_accepted_baseline_classification_finding_policy_id(
        policy_version="1.0",
        behavior_manifest_id=BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID,
        behavior_manifest_version=BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION,
        rules=rules,
        benign_no_finding_codes=_BENIGN_CODES,
        category_vocabulary=categories,
        severity_vocabulary=severities,
        operational_exclusions=_OPERATIONAL_EXCLUSIONS,
    )
    policy = AcceptedBaselineClassificationFindingPolicy(
        identity=AcceptedBaselineClassificationFindingPolicyIdentity(
            STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION,
            policy_id,
            BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID,
        ),
        policy_version="1.0",
        behavior_manifest_version=BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION,
        rules=rules,
        benign_no_finding_codes=_BENIGN_CODES,
        category_vocabulary=categories,
        severity_vocabulary=severities,
        operational_exclusions=_OPERATIONAL_EXCLUSIONS,
    )
    _verify_policy(policy)
    return policy


def _default_rules() -> tuple[AcceptedBaselineClassificationFindingRule, ...]:
    state = AcceptedBaselineClassificationState
    dimension = AcceptedBaselineClassificationDimension
    category = AcceptedBaselineClassificationFindingCategory
    severity = AcceptedBaselineClassificationFindingSeverity
    specifications = (
        (
            "finding-state-ambiguous",
            (state.AMBIGUOUS,),
            (),
            (),
            None,
            category.CLASSIFICATION_UNCERTAINTY,
            severity.WARNING,
            "classification_ambiguous",
            "ambiguous_classification_requires_attention",
        ),
        (
            "finding-capture-attention",
            (state.CLASSIFIED,),
            (dimension.CAPTURE_STATE,),
            ("excluded", "pending"),
            True,
            category.CAPTURE_CONDITION,
            severity.WARNING,
            "capture_requires_attention",
            "capture_state_requires_attention",
        ),
        (
            "finding-capture-failure",
            (state.CLASSIFIED,),
            (dimension.CAPTURE_STATE,),
            ("error", "inaccessible"),
            True,
            category.CAPTURE_CONDITION,
            severity.ERROR,
            "capture_failure_observed",
            "capture_failure_requires_attention",
        ),
        (
            "finding-integrity-failure",
            (state.CLASSIFIED,),
            (dimension.CONTENT_INTEGRITY_STATE,),
            (
                "digest_mismatch",
                "filesystem_error",
                "inaccessible",
                "missing",
                "not_regular_file",
                "size_mismatch",
                "source_changed",
            ),
            True,
            category.INTEGRITY_CONDITION,
            severity.ERROR,
            "integrity_failure_observed",
            "integrity_failure_requires_attention",
        ),
        (
            "finding-content-other",
            (state.CLASSIFIED,),
            (dimension.CONTENT_TYPE,),
            ("other",),
            True,
            category.CLASSIFICATION_REVIEW,
            severity.WARNING,
            "other_content_type_review",
            "other_content_type_requires_review",
        ),
        (
            "finding-content-unsupported",
            (state.CLASSIFIED,),
            (dimension.CONTENT_TYPE,),
            ("unsupported_object",),
            True,
            category.UNSUPPORTED_CLASSIFICATION,
            severity.WARNING,
            "unsupported_content_object",
            "unsupported_content_object_requires_attention",
        ),
        (
            "finding-inventory-unsupported",
            (state.CLASSIFIED,),
            (dimension.INVENTORY_SUPPORT_STATE,),
            ("unsupported",),
            True,
            category.UNSUPPORTED_CLASSIFICATION,
            severity.WARNING,
            "unsupported_inventory_record",
            "unsupported_inventory_record_requires_attention",
        ),
        (
            "finding-state-conflicting",
            (state.CONFLICTING,),
            (),
            (),
            None,
            category.CLASSIFICATION_CONFLICT,
            severity.ERROR,
            "classification_conflicting",
            "conflicting_classification_requires_attention",
        ),
        (
            "finding-state-insufficient",
            (state.INSUFFICIENT_EVIDENCE,),
            (),
            (),
            None,
            category.INSUFFICIENT_EVIDENCE,
            severity.ERROR,
            "classification_insufficient_evidence",
            "insufficient_classification_evidence",
        ),
        (
            "finding-state-unclassified",
            (state.UNCLASSIFIED,),
            (),
            (),
            None,
            category.POLICY_NONCOVERAGE,
            severity.WARNING,
            "classification_unclassified",
            "classification_policy_did_not_cover_observation",
        ),
        (
            "finding-state-unknown",
            (state.UNKNOWN,),
            (),
            (),
            None,
            category.CLASSIFICATION_UNCERTAINTY,
            severity.WARNING,
            "classification_unknown",
            "unknown_classification_requires_attention",
        ),
        (
            "finding-state-unsupported",
            (state.UNSUPPORTED,),
            (),
            (),
            None,
            category.UNSUPPORTED_CLASSIFICATION,
            severity.WARNING,
            "classification_unsupported",
            "unsupported_classification_requires_attention",
        ),
    )
    return tuple(AcceptedBaselineClassificationFindingRule(*item) for item in specifications)


def _behavior_manifest(rules):
    return {
        "category_vocabulary": [
            item.value
            for item in sorted(
                AcceptedBaselineClassificationFindingCategory, key=lambda item: item.value
            )
        ],
        "deduplication": (
            "duplicate finding keys fail; findings from distinct observations never merge"
        ),
        "finding_granularity": "one finding per concerning classification observation",
        "manifest_schema_version": BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION,
        "no_finding_mappings": [
            {"code": "benign_capture_captured", "condition": "capture_state classified captured"},
            {
                "code": "benign_classified_unmapped",
                "condition": (
                    "classified observation without an approved concerning selected-value rule"
                ),
            },
            {
                "code": "benign_directory_integrity_not_applicable",
                "condition": "content_integrity_state not_applicable for directory",
            },
            {
                "code": "benign_integrity_verified",
                "condition": "content_integrity_state classified verified",
            },
            {"code": "benign_not_applicable", "condition": "not_applicable observation"},
        ],
        "one_rule_per_observation": (
            "at most one rule may match; static overlap is invalid; runtime overlap fails"
        ),
        "operational_exclusions": list(_OPERATIONAL_EXCLUSIONS),
        "ordering": {
            "finding_rule_codes": "lexical",
            "findings": (
                "(source_root_id,relative_path,item_id,dimension,observation_kind,"
                "category,finding_code)"
            ),
            "policy_rules": "(accepted_state,dimension-or-empty,rule_code)",
            "rationale_codes": "lexical",
        },
        "overlap_failure": "accepted-baseline classification finding evaluation error",
        "policy_version": "1.0",
        "required_classification_behavior_id": BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID,
        "review_required_behavior": (
            "review_required does not create a second finding; unmatched review-required "
            "observations fail as unsupported behavior"
        ),
        "rules": [
            {
                "accepted_dimensions": [item.value for item in rule.accepted_dimensions],
                "accepted_selected_values": list(rule.accepted_selected_values),
                "accepted_states": [item.value for item in rule.accepted_states],
                "category": rule.category.value,
                "finding_code": rule.finding_code,
                "rationale_code": rule.rationale_code,
                "required_review": rule.required_review,
                "rule_code": rule.rule_code,
                "severity": rule.severity.value,
            }
            for rule in rules
        ],
        "severity_vocabulary": [
            item.value
            for item in sorted(
                AcceptedBaselineClassificationFindingSeverity, key=lambda item: item.value
            )
        ],
        "structural_condition_semantics": (
            "identity, lineage, model, reference, overlap, and evaluator defects are "
            "failures, not findings"
        ),
        "supported_input_classification_schema": "1.0",
    }


def _canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def _thaw(value):
    if isinstance(value, FrozenJsonObject):
        return {key: _thaw(item) for key, item in value.entries}
    if isinstance(value, FrozenJsonArray):
        return [_thaw(item) for item in value.values]
    return value


def _observation_key(item):
    return (
        item.subject.source_root_id,
        item.subject.relative_path,
        item.subject.item_id,
        item.dimension.value,
        item.observation_kind.value,
    )


def _finding_key(item):
    reference = item.observation_reference
    return (
        reference.source_root_id,
        reference.relative_path,
        reference.item_id,
        reference.dimension.value,
        reference.observation_kind.value,
        item.category.value,
        item.finding_code,
    )
