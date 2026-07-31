"""Deterministic classification of authenticated accepted-baseline semantics."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_analysis import (
    AcceptedBaselineAnalysisContext,
    AcceptedBaselineAnalysisEvidence,
    AcceptedBaselineAnalysisEvidenceStatus,
    FrozenJsonArray,
    FrozenJsonObject,
    FrozenJsonValue,
    stable_accepted_baseline_analysis_context_id,
    stable_accepted_baseline_analysis_profile_id,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceType,
)
from poe_backup_orchestrator.models.storage_baseline_classification import (
    BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID,
    BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION,
    STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION,
    STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION,
    AcceptedBaselineClassificationCandidate,
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationFactReference,
    AcceptedBaselineClassificationObservation,
    AcceptedBaselineClassificationObservationKind,
    AcceptedBaselineClassificationObservationSet,
    AcceptedBaselineClassificationObservationSetIdentity,
    AcceptedBaselineClassificationPolicy,
    AcceptedBaselineClassificationPolicyIdentity,
    AcceptedBaselineClassificationPredicate,
    AcceptedBaselineClassificationRule,
    AcceptedBaselineClassificationState,
    AcceptedBaselineClassificationSubject,
    stable_accepted_baseline_classification_observation_set_id,
    stable_accepted_baseline_classification_policy_id,
)

_KIND: Final = AcceptedBaselineClassificationObservationKind.DESCRIPTIVE_OBSERVATION
_DIMENSIONS: Final = tuple(
    sorted(AcceptedBaselineClassificationDimension, key=lambda item: item.value)
)
_VALUE_DOMAINS: Final = (
    (
        AcceptedBaselineClassificationDimension.CAPTURE_STATE,
        ("captured", "error", "excluded", "inaccessible", "not_applicable", "pending"),
    ),
    (
        AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE,
        (
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
    ),
    (
        AcceptedBaselineClassificationDimension.CONTENT_TYPE,
        ("directory", "file", "other", "unsupported_object"),
    ),
    (AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE, ("supported", "unsupported")),
)
_OPERATIONAL_EXCLUSIONS: Final = (
    "cache_state",
    "execution_host",
    "execution_timestamp",
    "filesystem_transport_path",
    "lock_state",
    "logging_detail",
    "memory_identity",
    "object_identity",
    "persistence_path",
    "publication_path",
    "replay_state",
    "service_instance",
)


class AcceptedBaselineClassificationError(RuntimeError):
    """Base failure for deterministic accepted-baseline classification."""


class AcceptedBaselineClassificationContextError(AcceptedBaselineClassificationError):
    """The supplied analytical context failed semantic validation."""


class AcceptedBaselineClassificationPolicyError(AcceptedBaselineClassificationError):
    """The configured classification policy is not architecture conformant."""


class AcceptedBaselineClassificationEvaluationError(AcceptedBaselineClassificationError):
    """Structurally valid inputs could not be evaluated consistently."""


@dataclass(slots=True)
class AcceptedBaselineClassificationService:
    """Apply one immutable architecture-approved policy to one context."""

    policy: AcceptedBaselineClassificationPolicy = field(default_factory=lambda: _default_policy())

    def __post_init__(self) -> None:
        if not isinstance(self.policy, AcceptedBaselineClassificationPolicy):
            raise ValueError("policy must be AcceptedBaselineClassificationPolicy")
        _verify_policy(self.policy)

    def classify(
        self,
        context: AcceptedBaselineAnalysisContext,
    ) -> AcceptedBaselineClassificationObservationSet:
        """Return deterministic descriptive observations without external access."""

        if not isinstance(context, AcceptedBaselineAnalysisContext):
            raise AcceptedBaselineClassificationContextError(
                "context must be AcceptedBaselineAnalysisContext"
            )
        _verify_policy(self.policy)
        _verify_context(context)
        try:
            subjects, inventory, integrity = _derive_subjects(context)
            observations = tuple(
                sorted(
                    (
                        _evaluate(subject, dimension, inventory, integrity, self.policy)
                        for subject in subjects
                        for dimension in _DIMENSIONS
                    ),
                    key=_observation_key,
                )
            )
            identity_value = stable_accepted_baseline_classification_observation_set_id(
                analysis_context_id=context.identity.analysis_context_id,
                accepted_baseline_id=context.identity.accepted_baseline_id,
                analysis_profile_id=context.identity.analysis_profile_id,
                policy=self.policy,
                observations=observations,
            )
            return AcceptedBaselineClassificationObservationSet(
                identity=AcceptedBaselineClassificationObservationSetIdentity(
                    STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION,
                    identity_value,
                    context.identity.analysis_context_id,
                    context.identity.accepted_baseline_id,
                    context.identity.analysis_profile_id,
                    self.policy.identity.classification_policy_id,
                ),
                analysis_context=context,
                policy=self.policy,
                observations=observations,
            )
        except AcceptedBaselineClassificationError:
            raise
        except (TypeError, ValueError) as exc:
            raise AcceptedBaselineClassificationEvaluationError(
                "classification evaluation failed"
            ) from exc


def _verify_context(context: AcceptedBaselineAnalysisContext) -> None:
    profile = context.profile
    try:
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
        for evidence in context.authenticated_evidence:
            if evidence.status is not AcceptedBaselineAnalysisEvidenceStatus.AUTHENTICATED:
                raise ValueError("context contains unauthenticated analytical evidence")
            if evidence.semantic_facts is None or evidence.evidence_semantic_id is None:
                raise ValueError("authenticated evidence has incomplete semantics")
            digest = hashlib.sha256(_canonical_frozen_bytes(evidence.semantic_facts)).hexdigest()
            if digest != evidence.evidence_semantic_id:
                raise ValueError("authenticated evidence semantic identity mismatch")
        context_id = stable_accepted_baseline_analysis_context_id(
            accepted_baseline_id=context.identity.accepted_baseline_id,
            profile=profile,
            authenticated_evidence=context.authenticated_evidence,
            lineage_only_evidence=context.lineage_only_evidence,
        )
        if context.identity.analysis_context_id != context_id:
            raise ValueError("analysis context identity mismatch")
        if (
            context.identity.accepted_baseline_id
            != context.accepted_baseline.identity.accepted_baseline_id
        ):
            raise ValueError("accepted-baseline lineage mismatch")
    except (TypeError, ValueError) as exc:
        raise AcceptedBaselineClassificationContextError(
            "analysis context semantic validation failed"
        ) from exc


def _derive_subjects(context: AcceptedBaselineAnalysisContext):
    inventory_records: dict[
        tuple[str, str, str], tuple[AcceptedBaselineAnalysisEvidence, dict[str, FrozenJsonValue]]
    ] = {}
    integrity_records: dict[
        tuple[str, str, str], tuple[AcceptedBaselineAnalysisEvidence, dict[str, FrozenJsonValue]]
    ] = {}
    for evidence in context.authenticated_evidence:
        facts = evidence.semantic_facts
        assert facts is not None
        root = evidence.observation.source_root_id
        if evidence.observation.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
            rows = _array(facts, "inventory facts")
            if not rows or _object(rows[0], "inventory header").get("source_root_id") != root:
                raise AcceptedBaselineClassificationEvaluationError(
                    "inventory source-root lineage is contradictory"
                )
            for value in rows[1:]:
                record = _object(value, "inventory item")
                key = (root, _string(record, "relative_path"), _string(record, "item_id"))
                if key in inventory_records:
                    raise AcceptedBaselineClassificationEvaluationError(
                        "duplicate inventory subject"
                    )
                if record.get("support_status") == "supported":
                    payload = _object(record["record"], "inventory record payload")
                    identity = _object(payload["identity"], "inventory identity")
                    if (
                        identity.get("source_root_id") != root
                        or identity.get("relative_path") != key[1]
                        or identity.get("item_type") != record.get("item_type")
                    ):
                        raise AcceptedBaselineClassificationEvaluationError(
                            "inventory item lineage is contradictory"
                        )
                inventory_records[key] = (evidence, record)
        elif (
            evidence.observation.evidence_type
            is PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE
        ):
            document = _object(facts, "integrity document")
            if document.get("source_root_id") != root:
                raise AcceptedBaselineClassificationEvaluationError(
                    "integrity source-root lineage is contradictory"
                )
            for value in _array(document["evidence"], "integrity evidence"):
                record = _object(value, "integrity item")
                key = (root, _string(record, "relative_path"), _string(record, "item_id"))
                if key in integrity_records:
                    raise AcceptedBaselineClassificationEvaluationError(
                        "duplicate integrity linkage"
                    )
                integrity_records[key] = (evidence, record)
    if any(key not in inventory_records for key in integrity_records):
        raise AcceptedBaselineClassificationEvaluationError(
            "integrity linkage does not identify an inventory subject"
        )
    subjects = tuple(
        AcceptedBaselineClassificationSubject(root, path, item_id, _string(record, "item_type"))
        for (root, path, item_id), (_, record) in sorted(inventory_records.items())
    )
    return subjects, inventory_records, integrity_records


def _evaluate(subject, dimension, inventory, integrity, policy):
    key = (subject.source_root_id, subject.relative_path, subject.item_id)
    inventory_evidence, inventory_record = inventory[key]
    facts: dict[str, str] = {
        "inventory.support_status": _string(inventory_record, "support_status"),
        "inventory.item_type": _string(inventory_record, "item_type"),
    }
    sources = {
        "inventory.support_status": inventory_evidence,
        "inventory.item_type": inventory_evidence,
    }
    if facts["inventory.support_status"] == "supported":
        payload = _object(inventory_record["record"], "inventory record payload")
        capture = payload.get("capture_status")
        if isinstance(capture, str):
            facts["inventory.capture_status"] = capture
            sources["inventory.capture_status"] = inventory_evidence
    linked = integrity.get(key)
    if linked is not None:
        integrity_evidence, integrity_record = linked
        facts["integrity.outcome"] = _string(integrity_record, "outcome")
        sources["integrity.outcome"] = integrity_evidence

    matches = [
        rule
        for rule in policy.rules
        if rule.dimension is dimension and all(_matches(item, facts) for item in rule.predicates)
    ]
    if not matches:
        return _uncertain_observation(subject, dimension, facts, sources)
    candidate_rules: dict[str, list[str]] = {}
    for rule in matches:
        if rule.candidate_value is not None:
            candidate_rules.setdefault(rule.candidate_value, []).append(rule.rule_code)
    candidates = tuple(
        AcceptedBaselineClassificationCandidate(value, tuple(sorted(codes)))
        for value, codes in sorted(candidate_rules.items())
    )
    states = {rule.result_state for rule in matches}
    if len(candidates) > 1:
        state = AcceptedBaselineClassificationState.CONFLICTING
        selected = None
    elif len(states) == 1:
        state = next(iter(states))
        selected = (
            candidates[0].value
            if candidates
            and state
            in {
                AcceptedBaselineClassificationState.CLASSIFIED,
                AcceptedBaselineClassificationState.INSUFFICIENT_EVIDENCE,
                AcceptedBaselineClassificationState.NOT_APPLICABLE,
            }
            else None
        )
    else:
        raise AcceptedBaselineClassificationEvaluationError(
            "matching rules yield impossible states"
        )
    rule_codes = tuple(sorted(rule.rule_code for rule in matches))
    used_paths = tuple(sorted({p.field_path for rule in matches for p in rule.predicates}))
    references = tuple(
        sorted(
            (
                _fact_reference(subject, path, sources[path], rule_codes)
                for path in used_paths
                if path in sources
            ),
            key=lambda item: (
                item.evidence_semantic_id,
                item.source_root_id,
                item.relative_path,
                item.item_id,
                item.field_path,
            ),
        )
    )
    review_codes = tuple(sorted({code for rule in matches for code in rule.review_rationale_codes}))
    rationales = tuple(sorted({rule.rationale_code for rule in matches}))
    return AcceptedBaselineClassificationObservation(
        subject,
        dimension,
        _KIND,
        state,
        candidates,
        selected,
        rule_codes,
        references,
        rationales,
        bool(review_codes),
        review_codes,
    )


def _uncertain_observation(subject, dimension, facts, sources):
    relevant = {
        AcceptedBaselineClassificationDimension.CONTENT_TYPE: "inventory.item_type",
        AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE: "inventory.support_status",
        AcceptedBaselineClassificationDimension.CAPTURE_STATE: "inventory.capture_status",
        AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE: "integrity.outcome",
    }[dimension]
    if relevant not in facts:
        state = AcceptedBaselineClassificationState.INSUFFICIENT_EVIDENCE
        rationale = "required_fact_missing"
    elif facts[relevant] == "unknown":
        state = AcceptedBaselineClassificationState.UNKNOWN
        rationale = "governed_unknown_value"
    else:
        state = AcceptedBaselineClassificationState.UNSUPPORTED
        rationale = "unsupported_source_value"
    refs = (
        ()
        if relevant not in sources
        else (_fact_reference(subject, relevant, sources[relevant], ()),)
    )
    return AcceptedBaselineClassificationObservation(
        subject,
        dimension,
        _KIND,
        state,
        (),
        None,
        (),
        refs,
        (rationale,),
        True,
        ("classification_review_required",),
    )


def _matches(predicate, facts):
    present = predicate.field_path in facts
    if predicate.operator == "present":
        return present
    if predicate.operator == "absent":
        return not present
    if not present:
        return False
    if predicate.operator == "exact":
        return facts[predicate.field_path] == predicate.values[0]
    return facts[predicate.field_path] in predicate.values


def _fact_reference(subject, field_path, evidence, rule_codes):
    assert evidence.evidence_semantic_id and evidence.schema_name and evidence.schema_version
    return AcceptedBaselineClassificationFactReference(
        evidence.evidence_semantic_id,
        evidence.observation.evidence_type,
        evidence.schema_name,
        evidence.schema_version,
        subject.source_root_id,
        subject.item_id,
        subject.relative_path,
        field_path,
        rule_codes,
    )


def _default_policy() -> AcceptedBaselineClassificationPolicy:
    rules = _default_rules()
    state_resolution = _freeze_object(
        {
            "explicit_unknown": "unknown",
            "missing_required_fact": "insufficient_evidence",
            "no_matching_supported_rule": "unclassified",
            "not_applicable": "not_applicable",
            "unsupported_source_value": "unsupported",
        }
    )
    conflict = _freeze_object(
        {
            "ambiguous": "different compatible candidates are retained without selection",
            "conflicting": "different mutually exclusive candidates are retained without selection",
            "same_value": "combine unique rule and fact provenance",
        }
    )
    review = _freeze_object(
        {
            "classified_failure_or_nonterminal_state": "review required",
            "classified_verified_or_captured_state": "review not indicated",
            "not_applicable": "review not indicated",
            "uncertainty_conflict_or_unsupported": "review required",
        }
    )
    ordering = _freeze_object(
        {
            "candidates": "(value,rule_codes)",
            "fact_references": "(evidence_semantic_id,subject_id,field_path)",
            "observations": "(source_root_id,relative_path,item_id,dimension,kind)",
            "rationale_codes": "lexical",
            "review_rationale_codes": "lexical",
            "rule_codes": "lexical",
            "rules": "(dimension,rule_code)",
            "subjects": "(source_root_id,relative_path,item_id)",
        }
    )
    policy_id = stable_accepted_baseline_classification_policy_id(
        policy_version="1.0",
        behavior_manifest_id=BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID,
        behavior_manifest_version=BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION,
        supported_dimensions=_DIMENSIONS,
        value_domains=_VALUE_DOMAINS,
        rules=rules,
        state_resolution=state_resolution,
        conflict_semantics=conflict,
        review_semantics=review,
        ordering=ordering,
        operational_exclusions=_OPERATIONAL_EXCLUSIONS,
    )
    policy = AcceptedBaselineClassificationPolicy(
        AcceptedBaselineClassificationPolicyIdentity(
            STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION,
            policy_id,
            BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID,
        ),
        "1.0",
        BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION,
        _DIMENSIONS,
        _VALUE_DOMAINS,
        rules,
        state_resolution,
        conflict,
        review,
        ordering,
        _OPERATIONAL_EXCLUSIONS,
    )
    _verify_policy(policy)
    return policy


def _default_rules() -> tuple[AcceptedBaselineClassificationRule, ...]:
    specifications = (
        (
            "capture-captured",
            "capture_state",
            (
                ("inventory.capture_status", "exact", ("captured",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "captured",
            "classified",
            False,
            "capture_status_preserved",
        ),
        (
            "capture-error",
            "capture_state",
            (
                ("inventory.capture_status", "exact", ("error",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "error",
            "classified",
            True,
            "capture_error_review",
        ),
        (
            "capture-excluded",
            "capture_state",
            (
                ("inventory.capture_status", "exact", ("excluded",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "excluded",
            "classified",
            True,
            "capture_excluded_review",
        ),
        (
            "capture-inaccessible",
            "capture_state",
            (
                ("inventory.capture_status", "exact", ("inaccessible",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "inaccessible",
            "classified",
            True,
            "capture_inaccessible_review",
        ),
        (
            "capture-pending",
            "capture_state",
            (
                ("inventory.capture_status", "exact", ("pending",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "pending",
            "classified",
            True,
            "capture_pending_review",
        ),
        (
            "capture-unsupported",
            "capture_state",
            (("inventory.support_status", "exact", ("unsupported",)),),
            None,
            "unsupported",
            True,
            "capture_state_unsupported",
        ),
        (
            "content-type-directory",
            "content_type",
            (
                ("inventory.item_type", "exact", ("directory",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "directory",
            "classified",
            False,
            "evidence_declares_directory",
        ),
        (
            "content-type-file",
            "content_type",
            (
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "file",
            "classified",
            False,
            "evidence_declares_file",
        ),
        (
            "content-type-other",
            "content_type",
            (
                ("inventory.item_type", "member_of", ("junction", "other", "symbolic_link")),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "other",
            "classified",
            True,
            "supported_other_object",
        ),
        (
            "content-type-unsupported",
            "content_type",
            (("inventory.support_status", "exact", ("unsupported",)),),
            "unsupported_object",
            "classified",
            True,
            "unsupported_inventory_object",
        ),
        (
            "integrity-digest-mismatch",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("digest_mismatch",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "digest_mismatch",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-directory-na",
            "content_integrity_state",
            (
                ("inventory.item_type", "exact", ("directory",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "not_applicable",
            "not_applicable",
            False,
            "integrity_not_applicable_directory",
        ),
        (
            "integrity-filesystem-error",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("filesystem_error",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "filesystem_error",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-inaccessible",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("inaccessible",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "inaccessible",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-missing",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("missing",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "missing",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-missing-link",
            "content_integrity_state",
            (
                ("integrity.outcome", "absent", ()),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "insufficient_evidence",
            "insufficient_evidence",
            True,
            "integrity_linkage_missing",
        ),
        (
            "integrity-not-regular",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("not_regular_file",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "not_regular_file",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-size-mismatch",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("size_mismatch",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "size_mismatch",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-source-changed",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("source_changed",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "source_changed",
            "classified",
            True,
            "integrity_failure_review",
        ),
        (
            "integrity-unsupported",
            "content_integrity_state",
            (("inventory.support_status", "exact", ("unsupported",)),),
            None,
            "unsupported",
            True,
            "integrity_state_unsupported",
        ),
        (
            "integrity-verified",
            "content_integrity_state",
            (
                ("integrity.outcome", "exact", ("verified",)),
                ("inventory.item_type", "exact", ("file",)),
                ("inventory.support_status", "exact", ("supported",)),
            ),
            "verified",
            "classified",
            False,
            "integrity_outcome_preserved",
        ),
        (
            "inventory-support-supported",
            "inventory_support_state",
            (("inventory.support_status", "exact", ("supported",)),),
            "supported",
            "classified",
            False,
            "inventory_record_supported",
        ),
        (
            "inventory-support-unsupported",
            "inventory_support_state",
            (("inventory.support_status", "exact", ("unsupported",)),),
            "unsupported",
            "classified",
            True,
            "inventory_record_unsupported",
        ),
    )
    rules = []
    for code, dimension, predicates, candidate, state, review, rationale in specifications:
        review_codes = (rationale,) if review else ()
        rules.append(
            AcceptedBaselineClassificationRule(
                AcceptedBaselineClassificationDimension(dimension),
                code,
                tuple(AcceptedBaselineClassificationPredicate(*item) for item in predicates),
                _KIND,
                candidate,
                AcceptedBaselineClassificationState(state),
                review,
                rationale,
                review_codes,
            )
        )
    return tuple(sorted(rules, key=lambda item: (item.dimension.value, item.rule_code)))


def _verify_policy(policy: AcceptedBaselineClassificationPolicy) -> None:
    try:
        if (
            policy.identity.behavior_manifest_id != BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID
            or policy.behavior_manifest_version != BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION
        ):
            raise ValueError("unsupported classification-policy behavior")
        digest = hashlib.sha256(_canonical_bytes(_behavior_manifest(policy.rules))).hexdigest()
        if digest != BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID:
            raise ValueError("policy behavior manifest digest mismatch")
        expected = stable_accepted_baseline_classification_policy_id(
            policy_version=policy.policy_version,
            behavior_manifest_id=policy.identity.behavior_manifest_id,
            behavior_manifest_version=policy.behavior_manifest_version,
            supported_dimensions=policy.supported_dimensions,
            value_domains=policy.value_domains,
            rules=policy.rules,
            state_resolution=policy.state_resolution,
            conflict_semantics=policy.conflict_semantics,
            review_semantics=policy.review_semantics,
            ordering=policy.ordering,
            operational_exclusions=policy.operational_exclusions,
        )
        if policy.identity.classification_policy_id != expected:
            raise ValueError("classification policy identity mismatch")
    except (TypeError, ValueError) as exc:
        raise AcceptedBaselineClassificationPolicyError(
            "classification policy validation failed"
        ) from exc


def _behavior_manifest(rules):
    return {
        "conflict_semantics": {
            "ambiguous": "different compatible candidates are retained without selection",
            "conflicting": "different mutually exclusive candidates are retained without selection",
            "same_value": "combine unique rule and fact provenance",
        },
        "dimensions": {dimension.value: list(values) for dimension, values in _VALUE_DOMAINS},
        "manifest_schema_version": BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_VERSION,
        "normalization": "none",
        "observation_kind": "descriptive_observation",
        "operational_exclusions": list(_OPERATIONAL_EXCLUSIONS),
        "ordering": {
            "candidates": "(value,rule_codes)",
            "fact_references": "(evidence_semantic_id,subject_id,field_path)",
            "observations": "(source_root_id,relative_path,item_id,dimension,kind)",
            "rationale_codes": "lexical",
            "review_rationale_codes": "lexical",
            "rule_codes": "lexical",
            "rules": "(dimension,rule_code)",
            "subjects": "(source_root_id,relative_path,item_id)",
        },
        "policy_version": "1.0",
        "predicate_semantics": {
            "absent": "field path does not resolve",
            "conjunction": "all ordered predicates must match",
            "exact": "resolved scalar equals the one declared value without normalization",
            "member_of": "resolved scalar equals one declared value without normalization",
            "present": "field path resolves",
        },
        "review_semantics": {
            "classified_failure_or_nonterminal_state": "review required",
            "classified_verified_or_captured_state": "review not indicated",
            "not_applicable": "review not indicated",
            "uncertainty_conflict_or_unsupported": "review required",
        },
        "rules": [
            {
                "candidate": rule.candidate_value,
                "dimension": rule.dimension.value,
                "kind": rule.observation_kind.value,
                "predicates": [
                    {
                        "field_path": item.field_path,
                        "operator": item.operator,
                        "values": list(item.values),
                    }
                    for item in rule.predicates
                ],
                "rationale_code": rule.rationale_code,
                "result_state": rule.result_state.value,
                "review_rationale_codes": list(rule.review_rationale_codes),
                "review_required": rule.review_required,
                "rule_code": rule.rule_code,
            }
            for rule in rules
        ],
        "source_field_bindings": {
            "integrity.outcome": "content_integrity_evidence.evidence[].outcome",
            "inventory.capture_status": "inventory_evidence.records[].record.capture_status",
            "inventory.item_type": "inventory_evidence.records[].item_type",
            "inventory.support_status": "inventory_evidence.records[].support_status",
        },
        "source_field_paths": [
            "integrity.outcome",
            "inventory.capture_status",
            "inventory.item_type",
            "inventory.support_status",
        ],
        "state_resolution": {
            "explicit_unknown": "unknown",
            "missing_required_fact": "insufficient_evidence",
            "no_matching_supported_rule": "unclassified",
            "not_applicable": "not_applicable",
            "unsupported_source_value": "unsupported",
        },
    }


def _freeze_object(value):
    return FrozenJsonObject(tuple((key, item) for key, item in sorted(value.items())))


def _canonical_bytes(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def _canonical_frozen_bytes(value):
    return _canonical_bytes(_thaw(value))


def _thaw(value):
    if isinstance(value, FrozenJsonObject):
        return {key: _thaw(item) for key, item in value.entries}
    if isinstance(value, FrozenJsonArray):
        return [_thaw(item) for item in value.values]
    return value


def _object(value, description):
    if not isinstance(value, FrozenJsonObject):
        raise AcceptedBaselineClassificationEvaluationError(f"{description} must be an object")
    return dict(value.entries)


def _array(value, description):
    if not isinstance(value, FrozenJsonArray):
        raise AcceptedBaselineClassificationEvaluationError(f"{description} must be an array")
    return value.values


def _string(value, key):
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise AcceptedBaselineClassificationEvaluationError(f"{key} must be a string")
    return item


def _observation_key(item):
    return (
        item.subject.source_root_id,
        item.subject.relative_path,
        item.subject.item_id,
        item.dimension.value,
        item.observation_kind.value,
    )
