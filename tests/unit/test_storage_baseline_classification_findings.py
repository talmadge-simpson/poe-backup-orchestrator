"""Service and authority tests for Slice 6C-3 classification findings."""

from __future__ import annotations

import builtins
import hashlib
import importlib.util
import inspect
import itertools
from dataclasses import replace
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_analysis import (
    AcceptedBaselineAnalysisContextIdentity,
    AcceptedBaselineAnalysisProfileIdentity,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import PreservationEvidenceType
from poe_backup_orchestrator.models.storage_baseline_classification import (
    AcceptedBaselineClassificationCandidate,
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationObservationSet,
    AcceptedBaselineClassificationObservationSetIdentity,
    AcceptedBaselineClassificationPolicyIdentity,
    AcceptedBaselineClassificationState,
    AcceptedBaselineClassificationSubject,
    stable_accepted_baseline_classification_observation_set_id,
)
from poe_backup_orchestrator.models.storage_baseline_classification_findings import (
    AcceptedBaselineClassificationFindingCategory,
    AcceptedBaselineClassificationFindingIdentity,
    AcceptedBaselineClassificationFindingPolicy,
    AcceptedBaselineClassificationFindingPolicyIdentity,
    AcceptedBaselineClassificationFindingResult,
    AcceptedBaselineClassificationFindingResultIdentity,
    AcceptedBaselineClassificationFindingSeverity,
    _finding_rules_overlap,
    stable_accepted_baseline_classification_finding_id,
    stable_accepted_baseline_classification_finding_policy_id,
    stable_accepted_baseline_classification_finding_result_id,
)
from poe_backup_orchestrator.services.storage_baseline_classification import (
    AcceptedBaselineClassificationService,
)
from poe_backup_orchestrator.services.storage_baseline_classification_findings import (
    BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID,
    BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION,
    AcceptedBaselineClassificationFindingEvaluationError,
    AcceptedBaselineClassificationFindingInputError,
    AcceptedBaselineClassificationFindingPolicyError,
    AcceptedBaselineClassificationFindingService,
    _behavior_manifest,
    _canonical_bytes,
    _default_policy,
)


def _analysis_bundle(tmp_path):
    path = Path(__file__).with_name("test_storage_baseline_analysis.py")
    spec = importlib.util.spec_from_file_location("slice_6c1_finding_support", path)
    assert spec is not None and spec.loader is not None
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    return support._bundle(tmp_path)


@pytest.fixture
def observation_set(tmp_path):
    service, artifact, _ = _analysis_bundle(tmp_path)
    context = service.build_context(artifact)
    return AcceptedBaselineClassificationService().classify(context)


def _replace_observation(observation_set, index, observation):
    observations = list(observation_set.observations)
    observations[index] = observation
    observations = tuple(
        sorted(
            observations,
            key=lambda item: (
                item.subject.source_root_id,
                item.subject.relative_path,
                item.subject.item_id,
                item.dimension.value,
                item.observation_kind.value,
            ),
        )
    )
    context = observation_set.analysis_context.identity
    identity_value = stable_accepted_baseline_classification_observation_set_id(
        analysis_context_id=context.analysis_context_id,
        accepted_baseline_id=context.accepted_baseline_id,
        analysis_profile_id=context.analysis_profile_id,
        policy=observation_set.policy,
        observations=observations,
    )
    return AcceptedBaselineClassificationObservationSet(
        AcceptedBaselineClassificationObservationSetIdentity(
            observation_set.identity.schema_version,
            identity_value,
            context.analysis_context_id,
            context.accepted_baseline_id,
            context.analysis_profile_id,
            observation_set.policy.identity.classification_policy_id,
        ),
        observation_set.analysis_context,
        observation_set.policy,
        observations,
    )


def _by_dimension(observation_set, dimension):
    return next(
        (index, item)
        for index, item in enumerate(observation_set.observations)
        if item.dimension is dimension
    )


def _classified(observation, value, review=True):
    code = f"synthetic_{observation.dimension.value}_{value}"
    return replace(
        observation,
        state=AcceptedBaselineClassificationState.CLASSIFIED,
        candidates=(AcceptedBaselineClassificationCandidate(value, (code,)),),
        selected_value=value,
        applied_rule_codes=(code,),
        rationale_codes=("synthetic_rationale",),
        review_required=review,
        review_rationale_codes=("synthetic_review",) if review else (),
    )


def _reidentified_policy(policy, **changes):
    values = {
        "policy_version": policy.policy_version,
        "behavior_manifest_id": policy.identity.behavior_manifest_id,
        "behavior_manifest_version": policy.behavior_manifest_version,
        "rules": policy.rules,
        "benign_no_finding_codes": policy.benign_no_finding_codes,
        "category_vocabulary": policy.category_vocabulary,
        "severity_vocabulary": policy.severity_vocabulary,
        "operational_exclusions": policy.operational_exclusions,
    }
    values.update(changes)
    policy_id = stable_accepted_baseline_classification_finding_policy_id(**values)
    return AcceptedBaselineClassificationFindingPolicy(
        identity=AcceptedBaselineClassificationFindingPolicyIdentity(
            policy.identity.schema_version,
            policy_id,
            values["behavior_manifest_id"],
        ),
        policy_version=values["policy_version"],
        behavior_manifest_version=values["behavior_manifest_version"],
        rules=values["rules"],
        benign_no_finding_codes=values["benign_no_finding_codes"],
        category_vocabulary=values["category_vocabulary"],
        severity_vocabulary=values["severity_vocabulary"],
        operational_exclusions=values["operational_exclusions"],
    )


def test_manifest_digest_rule_counts_vocabularies_and_overlap() -> None:
    policy = _default_policy()
    digest = hashlib.sha256(_canonical_bytes(_behavior_manifest(policy.rules))).hexdigest()
    assert BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_VERSION == (
        "poe.storage.baseline-classification.finding-policy-behavior/1.0"
    )
    assert digest == BASELINE_CLASSIFICATION_FINDING_POLICY_BEHAVIOR_ID
    assert digest == "5fb9bef7fdbcf63b2bab8347e088a01fad9b35c2bb5f89ccee321f938f2fa9fa"
    assert len(policy.rules) == len({rule.rule_code for rule in policy.rules}) == 12
    assert (
        sum(
            rule.accepted_states == (AcceptedBaselineClassificationState.CLASSIFIED,)
            for rule in policy.rules
        )
        == 6
    )
    assert (
        sum(
            rule.accepted_states != (AcceptedBaselineClassificationState.CLASSIFIED,)
            for rule in policy.rules
        )
        == 6
    )
    pairs = tuple(itertools.combinations(policy.rules, 2))
    assert len(pairs) == 66
    assert not any(_finding_rules_overlap(left, right) for left, right in pairs)
    manifest = _behavior_manifest(policy.rules)
    assert len(manifest["no_finding_mappings"]) == 5
    assert manifest["severity_vocabulary"] == ["error", "warning"]
    assert len(manifest["category_vocabulary"]) == 8
    assert manifest["required_classification_behavior_id"] == (
        "bea4cfe1132683da9c06988bdd361d7ef53361b760e1b94da8f30abe8a71ace5"
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"policy_version": "1.1"},
        {"benign_no_finding_codes": _default_policy().benign_no_finding_codes + ("future_benign",)},
        {
            "operational_exclusions": _default_policy().operational_exclusions
            + ("transport_extension",)
        },
    ),
)
def test_self_consistent_noncanonical_policy_is_rejected(changes) -> None:
    altered = _reidentified_policy(_default_policy(), **changes)
    with pytest.raises(AcceptedBaselineClassificationFindingPolicyError):
        AcceptedBaselineClassificationFindingService(altered)


def test_default_generation_is_deterministic_and_preserves_predecessor(observation_set) -> None:
    service = AcceptedBaselineClassificationFindingService()
    first = service.generate_findings(observation_set)
    second = service.generate_findings(observation_set)
    assert first == second
    assert first.observation_set is observation_set
    assert first.policy is service.policy
    assert first.identity.classification_finding_result_id.startswith("pbcfr-")
    assert len(first.findings) == 1
    finding = first.findings[0]
    assert finding.finding_code == "capture_requires_attention"
    assert finding.identity.classification_finding_id.startswith("pbcf-")
    assert finding.observation_reference.selected_value == "pending"
    assert finding.observation_reference.semantic_fact_references


def test_result_order_lineage_identity_sensitivity_and_nonmutation(observation_set) -> None:
    before = observation_set.observations
    result = AcceptedBaselineClassificationFindingService().generate_findings(observation_set)
    assert observation_set.observations == before
    keys = tuple(
        (
            item.observation_reference.source_root_id,
            item.observation_reference.relative_path,
            item.observation_reference.item_id,
            item.observation_reference.dimension.value,
            item.observation_reference.observation_kind.value,
            item.category.value,
            item.finding_code,
        )
        for item in result.findings
    )
    assert keys == tuple(sorted(keys))
    for finding in result.findings:
        reference = finding.observation_reference
        source = next(
            item
            for item in observation_set.observations
            if (
                item.subject.source_root_id,
                item.subject.relative_path,
                item.subject.item_id,
                item.dimension,
                item.observation_kind,
            )
            == (
                reference.source_root_id,
                reference.relative_path,
                reference.item_id,
                reference.dimension,
                reference.observation_kind,
            )
        )
        assert reference.selected_value == source.selected_value
        assert reference.candidates == source.candidates
        assert reference.semantic_fact_references == source.fact_references
    with pytest.raises(ValueError, match="unique and canonically ordered"):
        AcceptedBaselineClassificationFindingResult(
            result.identity,
            result.observation_set,
            result.policy,
            result.findings + result.findings,
        )
    changed_finding = replace(result.findings[0], finding_code="changed_finding")
    with pytest.raises(ValueError, match="finding semantics"):
        AcceptedBaselineClassificationFindingResult(
            result.identity,
            result.observation_set,
            result.policy,
            (changed_finding,),
        )
    changed_id = stable_accepted_baseline_classification_finding_id(
        observation_reference=changed_finding.observation_reference,
        finding_policy_id=result.policy.identity.classification_finding_policy_id,
        behavior_manifest_id=result.policy.identity.behavior_manifest_id,
        category=changed_finding.category,
        severity=changed_finding.severity,
        finding_code=changed_finding.finding_code,
        rationale_codes=changed_finding.rationale_codes,
        contributing_finding_rule_codes=changed_finding.contributing_finding_rule_codes,
    )
    self_consistent_finding = replace(
        changed_finding,
        identity=AcceptedBaselineClassificationFindingIdentity(
            changed_finding.identity.schema_version, changed_id
        ),
    )
    changed_result_id = stable_accepted_baseline_classification_finding_result_id(
        observation_set=result.observation_set,
        policy=result.policy,
        findings=(self_consistent_finding,),
    )
    self_consistent_result_identity = AcceptedBaselineClassificationFindingResultIdentity(
        result.identity.schema_version,
        changed_result_id,
        result.identity.classification_observation_set_id,
        result.identity.classification_finding_policy_id,
    )
    with pytest.raises(ValueError, match="finding semantics"):
        AcceptedBaselineClassificationFindingResult(
            self_consistent_result_identity,
            result.observation_set,
            result.policy,
            (self_consistent_finding,),
        )
    omitted_result_id = stable_accepted_baseline_classification_finding_result_id(
        observation_set=result.observation_set,
        policy=result.policy,
        findings=(),
    )
    omitted_identity = AcceptedBaselineClassificationFindingResultIdentity(
        result.identity.schema_version,
        omitted_result_id,
        result.identity.classification_observation_set_id,
        result.identity.classification_finding_policy_id,
    )
    with pytest.raises(ValueError, match="completely represent"):
        AcceptedBaselineClassificationFindingResult(
            omitted_identity,
            result.observation_set,
            result.policy,
            (),
        )
    with pytest.raises(ValueError, match="closed finding-category"):
        replace(result.findings[0], category="readiness")
    with pytest.raises(ValueError, match="closed finding-severity"):
        replace(result.findings[0], severity="blocking")
    with pytest.raises(ValueError, match="identity must be"):
        replace(result, identity=None)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="must contain classification findings"):
        replace(result, findings=(None,))  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("classification_observation_set_id", "pbcos-not-a-digest", "pbcos with a digest"),
        ("relative_path", "/absolute/path", "safe POSIX relative path"),
        ("relative_path", "../traversal", "safe POSIX relative path"),
        ("dimension", "content_type", "closed classification-dimension"),
        ("observation_kind", "item", "closed classification-observation"),
        ("state", "unknown", "closed classification-state"),
        ("review_required", 1, "review_required must be bool"),
    ),
)
def test_observation_reference_rejects_invalid_boundary_values(
    observation_set, field, value, message
) -> None:
    result = AcceptedBaselineClassificationFindingService().generate_findings(observation_set)
    with pytest.raises(ValueError, match=message):
        replace(result.findings[0].observation_reference, **{field: value})


@pytest.mark.parametrize(
    ("state", "category", "severity", "code"),
    (
        (
            AcceptedBaselineClassificationState.UNCLASSIFIED,
            "policy_noncoverage",
            "warning",
            "classification_unclassified",
        ),
        (
            AcceptedBaselineClassificationState.UNKNOWN,
            "classification_uncertainty",
            "warning",
            "classification_unknown",
        ),
        (
            AcceptedBaselineClassificationState.UNSUPPORTED,
            "unsupported_classification",
            "warning",
            "classification_unsupported",
        ),
    ),
)
def test_state_wide_single_candidate_free_mappings(
    observation_set, state, category, severity, code
) -> None:
    index, original = _by_dimension(
        observation_set, AcceptedBaselineClassificationDimension.CONTENT_TYPE
    )
    changed = replace(original, state=state, candidates=(), selected_value=None)
    result = AcceptedBaselineClassificationFindingService().generate_findings(
        _replace_observation(observation_set, index, changed)
    )
    finding = next(item for item in result.findings if item.finding_code == code)
    assert finding.category.value == category
    assert finding.severity.value == severity


@pytest.mark.parametrize(
    ("state", "category", "severity", "code"),
    (
        (
            AcceptedBaselineClassificationState.AMBIGUOUS,
            "classification_uncertainty",
            "warning",
            "classification_ambiguous",
        ),
        (
            AcceptedBaselineClassificationState.CONFLICTING,
            "classification_conflict",
            "error",
            "classification_conflicting",
        ),
    ),
)
def test_ambiguous_and_conflicting_mappings(
    observation_set, state, category, severity, code
) -> None:
    index, original = _by_dimension(
        observation_set, AcceptedBaselineClassificationDimension.CONTENT_TYPE
    )
    changed = replace(
        original,
        state=state,
        candidates=(
            AcceptedBaselineClassificationCandidate("file", ("candidate_a",)),
            AcceptedBaselineClassificationCandidate("other", ("candidate_b",)),
        ),
        selected_value=None,
        applied_rule_codes=("candidate_a", "candidate_b"),
    )
    result = AcceptedBaselineClassificationFindingService().generate_findings(
        _replace_observation(observation_set, index, changed)
    )
    finding = next(item for item in result.findings if item.finding_code == code)
    assert finding.category.value == category
    assert finding.severity.value == severity
    assert len(finding.observation_reference.candidates) == 2


def test_insufficient_evidence_mapping(observation_set) -> None:
    index, original = _by_dimension(
        observation_set, AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE
    )
    changed = replace(
        original,
        state=AcceptedBaselineClassificationState.INSUFFICIENT_EVIDENCE,
        candidates=(
            AcceptedBaselineClassificationCandidate(
                "insufficient_evidence", ("integrity_missing_link",)
            ),
        ),
        selected_value="insufficient_evidence",
        applied_rule_codes=("integrity_missing_link",),
        review_required=True,
        review_rationale_codes=("integrity_linkage_missing",),
    )
    result = AcceptedBaselineClassificationFindingService().generate_findings(
        _replace_observation(observation_set, index, changed)
    )
    finding = next(
        item
        for item in result.findings
        if item.finding_code == "classification_insufficient_evidence"
    )
    assert finding.category is AcceptedBaselineClassificationFindingCategory.INSUFFICIENT_EVIDENCE
    assert finding.severity is AcceptedBaselineClassificationFindingSeverity.ERROR


@pytest.mark.parametrize(
    ("dimension", "value", "finding_code"),
    (
        (
            AcceptedBaselineClassificationDimension.CONTENT_TYPE,
            "other",
            "other_content_type_review",
        ),
        (
            AcceptedBaselineClassificationDimension.CONTENT_TYPE,
            "unsupported_object",
            "unsupported_content_object",
        ),
        (
            AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE,
            "unsupported",
            "unsupported_inventory_record",
        ),
        (
            AcceptedBaselineClassificationDimension.CAPTURE_STATE,
            "excluded",
            "capture_requires_attention",
        ),
        (
            AcceptedBaselineClassificationDimension.CAPTURE_STATE,
            "pending",
            "capture_requires_attention",
        ),
        (
            AcceptedBaselineClassificationDimension.CAPTURE_STATE,
            "error",
            "capture_failure_observed",
        ),
        (
            AcceptedBaselineClassificationDimension.CAPTURE_STATE,
            "inaccessible",
            "capture_failure_observed",
        ),
    ),
)
def test_each_classified_review_mapping(observation_set, dimension, value, finding_code) -> None:
    index, original = _by_dimension(observation_set, dimension)
    changed = _classified(original, value)
    result = AcceptedBaselineClassificationFindingService().generate_findings(
        _replace_observation(observation_set, index, changed)
    )
    assert any(item.finding_code == finding_code for item in result.findings)


@pytest.mark.parametrize(
    "value",
    (
        "source_changed",
        "size_mismatch",
        "digest_mismatch",
        "missing",
        "inaccessible",
        "not_regular_file",
        "filesystem_error",
    ),
)
def test_each_integrity_failure_mapping(observation_set, value) -> None:
    index, original = _by_dimension(
        observation_set, AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE
    )
    changed = _classified(original, value)
    result = AcceptedBaselineClassificationFindingService().generate_findings(
        _replace_observation(observation_set, index, changed)
    )
    finding = next(
        item for item in result.findings if item.finding_code == "integrity_failure_observed"
    )
    assert finding.severity is AcceptedBaselineClassificationFindingSeverity.ERROR


@pytest.mark.parametrize(
    ("dimension", "value"),
    (
        (AcceptedBaselineClassificationDimension.CONTENT_TYPE, "file"),
        (AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE, "supported"),
        (AcceptedBaselineClassificationDimension.CAPTURE_STATE, "captured"),
        (AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE, "verified"),
    ),
)
def test_benign_classified_mappings_emit_no_finding_for_that_observation(
    observation_set, dimension, value
) -> None:
    index, original = _by_dimension(observation_set, dimension)
    changed = _classified(original, value, review=False)
    changed_set = _replace_observation(observation_set, index, changed)
    result = AcceptedBaselineClassificationFindingService().generate_findings(changed_set)
    key = (
        changed.subject.source_root_id,
        changed.subject.relative_path,
        changed.subject.item_id,
        dimension,
    )
    assert not any(
        (
            item.observation_reference.source_root_id,
            item.observation_reference.relative_path,
            item.observation_reference.item_id,
            item.observation_reference.dimension,
        )
        == key
        for item in result.findings
    )


def test_not_applicable_is_benign(observation_set) -> None:
    index, original = _by_dimension(
        observation_set, AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE
    )
    changed = replace(
        original,
        state=AcceptedBaselineClassificationState.NOT_APPLICABLE,
        candidates=(
            AcceptedBaselineClassificationCandidate("not_applicable", ("not_applicable",)),
        ),
        selected_value="not_applicable",
        applied_rule_codes=("not_applicable",),
        review_required=False,
        review_rationale_codes=(),
    )
    result = AcceptedBaselineClassificationFindingService().generate_findings(
        _replace_observation(observation_set, index, changed)
    )
    assert all(
        item.observation_reference.dimension is not changed.dimension for item in result.findings
    )


def test_wrong_input_and_tampered_predecessor_fail_closed(observation_set) -> None:
    service = AcceptedBaselineClassificationFindingService()
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        service.generate_findings({})  # type: ignore[arg-type]
    object.__setattr__(
        observation_set.identity,
        "classification_observation_set_id",
        "pbcos-" + "0" * 64,
    )
    with pytest.raises(AcceptedBaselineClassificationFindingInputError) as error:
        service.generate_findings(observation_set)
    assert error.value.__cause__ is not None


def test_tampered_profile_context_and_evidence_identities_fail(observation_set) -> None:
    service = AcceptedBaselineClassificationFindingService()
    context = observation_set.analysis_context
    original_profile = context.profile.identity
    object.__setattr__(
        context.profile,
        "identity",
        AcceptedBaselineAnalysisProfileIdentity(
            original_profile.schema_version,
            "pbaip-" + "0" * 64,
        ),
    )
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        service.generate_findings(observation_set)


def test_tampered_context_identity_fails(observation_set) -> None:
    context = observation_set.analysis_context
    identity = context.identity
    object.__setattr__(
        context,
        "identity",
        AcceptedBaselineAnalysisContextIdentity(
            identity.schema_version,
            "pbac-" + "0" * 64,
            identity.accepted_baseline_id,
            identity.analysis_profile_id,
        ),
    )
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_tampered_classification_policy_and_behavior_fail(observation_set) -> None:
    policy = observation_set.policy
    identity = policy.identity
    object.__setattr__(
        policy,
        "identity",
        AcceptedBaselineClassificationPolicyIdentity(
            identity.schema_version,
            "pbcp-" + "0" * 64,
            identity.behavior_manifest_id,
        ),
    )
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_tampered_classification_behavior_fails(observation_set) -> None:
    policy = observation_set.policy
    identity = policy.identity
    object.__setattr__(
        policy,
        "identity",
        AcceptedBaselineClassificationPolicyIdentity(
            identity.schema_version,
            identity.classification_policy_id,
            "0" * 64,
        ),
    )
    with pytest.raises(AcceptedBaselineClassificationFindingPolicyError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_context_profile_lineage_mismatch_fails(observation_set) -> None:
    context = observation_set.analysis_context
    identity = context.identity
    object.__setattr__(
        context,
        "identity",
        AcceptedBaselineAnalysisContextIdentity(
            identity.schema_version,
            identity.analysis_context_id,
            identity.accepted_baseline_id,
            "pbaip-" + "0" * 64,
        ),
    )
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_observation_set_policy_lineage_mismatch_fails(observation_set) -> None:
    identity = observation_set.identity
    object.__setattr__(
        observation_set,
        "identity",
        AcceptedBaselineClassificationObservationSetIdentity(
            identity.schema_version,
            identity.classification_observation_set_id,
            identity.analysis_context_id,
            identity.accepted_baseline_id,
            identity.analysis_profile_id,
            "pbcp-" + "0" * 64,
        ),
    )
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_duplicate_observation_and_unresolved_fact_reference_fail(observation_set) -> None:
    original = observation_set.observations
    object.__setattr__(observation_set, "observations", original + (original[0],))
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_unresolved_fact_reference_fails(observation_set) -> None:
    observation = next(
        item
        for item in observation_set.observations
        if any(
            fact.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
            for fact in item.fact_references
        )
    )
    fact = next(
        item
        for item in observation.fact_references
        if item.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
    )
    object.__setattr__(fact, "evidence_semantic_id", "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("evidence_type", PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE),
        ("schema_name", "tampered_schema"),
        ("schema_version", "999"),
        ("source_root_id", "tampered-root"),
        ("item_id", "tampered-item"),
        ("relative_path", "tampered/path"),
        ("field_path", "inventory.nonexistent"),
    ),
)
def test_tampered_fact_reference_components_fail_resolution(observation_set, field, value) -> None:
    observation = next(
        item
        for item in observation_set.observations
        if any(
            fact.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
            for fact in item.fact_references
        )
    )
    fact = next(
        item
        for item in observation.fact_references
        if item.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
    )
    object.__setattr__(fact, field, value)
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_cross_subject_fact_reference_substitution_fails(observation_set) -> None:
    left_index, observation = next(
        (index, item)
        for index, item in enumerate(observation_set.observations)
        if any(
            fact.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
            for fact in item.fact_references
        )
    )
    substituted_subject = AcceptedBaselineClassificationSubject(
        observation.subject.source_root_id,
        "different/item",
        "different-item-id",
        observation.subject.item_type,
    )
    substituted = replace(observation, subject=substituted_subject)
    changed_set = _replace_observation(observation_set, left_index, substituted)
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError):
        AcceptedBaselineClassificationFindingService().generate_findings(changed_set)


def test_impossible_observation_state_fails(observation_set) -> None:
    observation = next(
        item
        for item in observation_set.observations
        if item.state is AcceptedBaselineClassificationState.CLASSIFIED
    )
    object.__setattr__(observation, "selected_value", None)
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_tampered_authenticated_evidence_identity_fails(observation_set) -> None:
    evidence = observation_set.analysis_context.authenticated_evidence[0]
    object.__setattr__(evidence, "evidence_semantic_id", "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationFindingInputError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_evaluator_failure_preserves_cause(monkeypatch, observation_set) -> None:
    import poe_backup_orchestrator.services.storage_baseline_classification_findings as module

    def fail(*args, **kwargs):
        raise ValueError("synthetic evaluator defect")

    monkeypatch.setattr(module, "_build_finding", fail)
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError) as error:
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)
    assert isinstance(error.value.__cause__, ValueError)


def test_uncovered_review_required_observation_fails_policy(observation_set) -> None:
    index, original = _by_dimension(
        observation_set, AcceptedBaselineClassificationDimension.CONTENT_TYPE
    )
    changed = _classified(original, "file", review=True)
    with pytest.raises(AcceptedBaselineClassificationFindingPolicyError):
        AcceptedBaselineClassificationFindingService().generate_findings(
            _replace_observation(observation_set, index, changed)
        )


def test_runtime_multiple_match_fails_without_priority(monkeypatch, observation_set) -> None:
    import poe_backup_orchestrator.services.storage_baseline_classification_findings as module

    monkeypatch.setattr(module, "_matches", lambda rule, observation: True)
    with pytest.raises(AcceptedBaselineClassificationFindingEvaluationError):
        AcceptedBaselineClassificationFindingService().generate_findings(observation_set)


def test_service_has_no_forbidden_runtime_dependencies_or_private_exports() -> None:
    import poe_backup_orchestrator.services as public_services
    import poe_backup_orchestrator.services.storage_baseline_classification_findings as module

    source = inspect.getsource(module)
    for prohibited in (
        "import os",
        "import pathlib",
        "import subprocess",
        "import socket",
        "open(",
        "AcceptedBaselineClassificationService(",
        "AcceptedBaselineAnalysisIntakeService",
        "database",
        "requests",
        "openai",
        "boto",
        "argparse",
        "typer",
        "click",
    ):
        assert prohibited not in source
    assert "_default_policy" not in public_services.__all__
    assert "_behavior_manifest" not in public_services.__all__
    signature = inspect.signature(AcceptedBaselineClassificationFindingService.generate_findings)
    assert tuple(signature.parameters) == ("self", "observation_set")


def test_generation_neither_reopens_files_nor_reruns_classification(
    monkeypatch, observation_set
) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("forbidden predecessor or filesystem access")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(AcceptedBaselineClassificationService, "classify", forbidden)
    before = observation_set
    result = AcceptedBaselineClassificationFindingService().generate_findings(observation_set)
    assert result.observation_set is before
