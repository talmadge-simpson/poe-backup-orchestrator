"""Service and authority-boundary tests for Slice 6C-2."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
from dataclasses import replace
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_analysis import (
    AcceptedBaselineAnalysisContextIdentity,
    FrozenJsonArray,
    FrozenJsonObject,
    stable_accepted_baseline_analysis_context_id,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import PreservationEvidenceType
from poe_backup_orchestrator.models.storage_baseline_classification import (
    BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID,
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationState,
)
from poe_backup_orchestrator.services import storage_baseline_classification as module
from poe_backup_orchestrator.services.storage_baseline_analysis import _freeze_json
from poe_backup_orchestrator.services.storage_baseline_classification import (
    AcceptedBaselineClassificationContextError,
    AcceptedBaselineClassificationEvaluationError,
    AcceptedBaselineClassificationPolicyError,
    AcceptedBaselineClassificationService,
    _behavior_manifest,
    _canonical_bytes,
    _default_policy,
)


def _analysis_bundle(tmp_path):
    path = Path(__file__).with_name("test_storage_baseline_analysis.py")
    spec = importlib.util.spec_from_file_location("slice_6c1_test_support", path)
    assert spec is not None and spec.loader is not None
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    return support._bundle(tmp_path)


def _thaw(value):
    if isinstance(value, FrozenJsonObject):
        return {key: _thaw(item) for key, item in value.entries}
    if isinstance(value, FrozenJsonArray):
        return [_thaw(item) for item in value.values]
    return value


def _with_evidence_change(context, evidence_type, change):
    records = []
    for evidence in context.authenticated_evidence:
        if evidence.observation.evidence_type is evidence_type:
            value = _thaw(evidence.semantic_facts)
            change(value)
            frozen = _freeze_json(value)
            digest = hashlib.sha256(_canonical_bytes(value)).hexdigest()
            evidence = replace(evidence, semantic_facts=frozen, evidence_semantic_id=digest)
        records.append(evidence)
    authenticated = tuple(records)
    context_id = stable_accepted_baseline_analysis_context_id(
        accepted_baseline_id=context.identity.accepted_baseline_id,
        profile=context.profile,
        authenticated_evidence=authenticated,
        lineage_only_evidence=context.lineage_only_evidence,
    )
    return replace(
        context,
        identity=AcceptedBaselineAnalysisContextIdentity(
            context.identity.schema_version,
            context_id,
            context.identity.accepted_baseline_id,
            context.identity.analysis_profile_id,
        ),
        authenticated_evidence=authenticated,
    )


@pytest.fixture
def context(tmp_path):
    service, artifact, _ = _analysis_bundle(tmp_path)
    return service.build_context(artifact)


def test_manifest_digest_and_exact_rule_count() -> None:
    policy = _default_policy()
    digest = hashlib.sha256(_canonical_bytes(_behavior_manifest(policy.rules))).hexdigest()
    assert digest == BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID
    assert digest == "bea4cfe1132683da9c06988bdd361d7ef53361b760e1b94da8f30abe8a71ace5"
    assert len(policy.rules) == 23


def test_default_classification_is_deterministic_and_complete(context) -> None:
    service = AcceptedBaselineClassificationService()
    first = service.classify(context)
    second = service.classify(context)
    assert first == second
    assert first.analysis_context is context
    assert first.policy is service.policy
    assert first.identity.classification_observation_set_id.startswith("pbcos-")
    assert len(first.observations) == 4
    assert {item.dimension for item in first.observations} == set(
        AcceptedBaselineClassificationDimension
    )


def test_file_dimensions_preserve_source_values(context) -> None:
    result = AcceptedBaselineClassificationService().classify(context)
    by_dimension = {item.dimension: item for item in result.observations}
    assert (
        by_dimension[AcceptedBaselineClassificationDimension.CONTENT_TYPE].selected_value == "file"
    )
    assert (
        by_dimension[AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE].selected_value
        == "supported"
    )
    assert (
        by_dimension[AcceptedBaselineClassificationDimension.CAPTURE_STATE].selected_value
        == "pending"
    )
    assert (
        by_dimension[AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE].selected_value
        == "verified"
    )
    assert all(item.fact_references for item in result.observations)


def test_directory_subject_has_not_applicable_integrity(context) -> None:
    def make_directory(value):
        value[1]["item_type"] = "directory"
        value[1]["record"]["identity"]["item_type"] = "directory"

    changed = _with_evidence_change(
        context, PreservationEvidenceType.INVENTORY_EVIDENCE, make_directory
    )
    observations = {
        item.dimension: item
        for item in AcceptedBaselineClassificationService().classify(changed).observations
    }
    assert (
        observations[AcceptedBaselineClassificationDimension.CONTENT_TYPE].selected_value
        == "directory"
    )
    integrity = observations[AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE]
    assert integrity.state is AcceptedBaselineClassificationState.NOT_APPLICABLE
    assert integrity.selected_value == "not_applicable"


def test_unsupported_subject_remains_explicitly_unsupported(context) -> None:
    def make_unsupported(value):
        envelope = value[1]
        envelope["support_status"] = "unsupported"
        envelope["item_type"] = "symbolic_link"
        envelope["detail"] = "synthetic unsupported item"
        del envelope["record"]

    changed = _with_evidence_change(
        context, PreservationEvidenceType.INVENTORY_EVIDENCE, make_unsupported
    )
    observations = {
        item.dimension: item
        for item in AcceptedBaselineClassificationService().classify(changed).observations
    }
    assert (
        observations[AcceptedBaselineClassificationDimension.CONTENT_TYPE].selected_value
        == "unsupported_object"
    )
    assert (
        observations[AcceptedBaselineClassificationDimension.INVENTORY_SUPPORT_STATE].selected_value
        == "unsupported"
    )
    assert (
        observations[AcceptedBaselineClassificationDimension.CAPTURE_STATE].state
        is AcceptedBaselineClassificationState.UNSUPPORTED
    )
    assert (
        observations[AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE].state
        is AcceptedBaselineClassificationState.UNSUPPORTED
    )


@pytest.mark.parametrize("capture", ("captured", "error", "excluded", "inaccessible", "pending"))
def test_every_approved_capture_status_is_preserved(context, capture: str) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        lambda value: value[1]["record"].__setitem__("capture_status", capture),
    )
    observation = next(
        item
        for item in AcceptedBaselineClassificationService().classify(changed).observations
        if item.dimension is AcceptedBaselineClassificationDimension.CAPTURE_STATE
    )
    assert observation.selected_value == capture


@pytest.mark.parametrize(
    "outcome",
    (
        "verified",
        "source_changed",
        "size_mismatch",
        "digest_mismatch",
        "missing",
        "inaccessible",
        "not_regular_file",
        "filesystem_error",
    ),
)
def test_every_approved_integrity_outcome_is_preserved(context, outcome: str) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        lambda value: value["evidence"][0].__setitem__("outcome", outcome),
    )
    observation = next(
        item
        for item in AcceptedBaselineClassificationService().classify(changed).observations
        if item.dimension is AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE
    )
    assert observation.selected_value == outcome


def test_missing_integrity_linkage_is_explicit_insufficiency(context) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        lambda value: value.__setitem__("evidence", []),
    )
    observation = next(
        item
        for item in AcceptedBaselineClassificationService().classify(changed).observations
        if item.dimension is AcceptedBaselineClassificationDimension.CONTENT_INTEGRITY_STATE
    )
    assert observation.state is AcceptedBaselineClassificationState.INSUFFICIENT_EVIDENCE
    assert observation.selected_value == "insufficient_evidence"


def test_unsupported_source_value_is_explicit_not_defaulted(context) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        lambda value: value[1]["record"].__setitem__("capture_status", "unknown-to-policy"),
    )
    observation = next(
        item
        for item in AcceptedBaselineClassificationService().classify(changed).observations
        if item.dimension is AcceptedBaselineClassificationDimension.CAPTURE_STATE
    )
    assert observation.state is AcceptedBaselineClassificationState.UNSUPPORTED
    assert observation.selected_value is None


def test_duplicate_subject_fails_closed(context) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        lambda value: value.append(dict(value[1])),
    )
    with pytest.raises(AcceptedBaselineClassificationEvaluationError, match="duplicate inventory"):
        AcceptedBaselineClassificationService().classify(changed)


def test_duplicate_integrity_linkage_fails_closed(context) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        lambda value: value["evidence"].append(dict(value["evidence"][0])),
    )
    with pytest.raises(AcceptedBaselineClassificationEvaluationError, match="duplicate integrity"):
        AcceptedBaselineClassificationService().classify(changed)


def test_nested_source_root_contradiction_fails_closed(context) -> None:
    changed = _with_evidence_change(
        context,
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        lambda value: value[0].__setitem__("source_root_id", "other-root"),
    )
    with pytest.raises(AcceptedBaselineClassificationEvaluationError, match="source-root"):
        AcceptedBaselineClassificationService().classify(changed)


def test_review_is_orthogonal_not_a_dimension(context) -> None:
    result = AcceptedBaselineClassificationService().classify(context)
    pending = next(
        item
        for item in result.observations
        if item.dimension is AcceptedBaselineClassificationDimension.CAPTURE_STATE
    )
    assert pending.state is AcceptedBaselineClassificationState.CLASSIFIED
    assert pending.review_required
    assert "policy_review_signal" not in {
        item.value for item in AcceptedBaselineClassificationDimension
    }


def test_wrong_input_type_is_rejected() -> None:
    with pytest.raises(AcceptedBaselineClassificationContextError):
        AcceptedBaselineClassificationService().classify({})  # type: ignore[arg-type]


def test_tampered_context_identity_is_rejected(context) -> None:
    object.__setattr__(context.identity, "analysis_context_id", "pbac-" + "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationContextError) as caught:
        AcceptedBaselineClassificationService().classify(context)
    assert caught.value.__cause__ is not None


def test_tampered_profile_identity_is_rejected(context) -> None:
    object.__setattr__(context.profile.identity, "analysis_profile_id", "pbaip-" + "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationContextError):
        AcceptedBaselineClassificationService().classify(context)


def test_tampered_evidence_semantic_identity_is_rejected(context) -> None:
    object.__setattr__(context.authenticated_evidence[0], "evidence_semantic_id", "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationContextError):
        AcceptedBaselineClassificationService().classify(context)


def test_invalid_policy_behavior_is_rejected(monkeypatch) -> None:
    monkeypatch.setattr(module, "BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID", "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationPolicyError):
        AcceptedBaselineClassificationService()


def test_policy_is_revalidated_on_every_evaluation(context) -> None:
    service = AcceptedBaselineClassificationService()
    object.__setattr__(service.policy.identity, "classification_policy_id", "pbcp-" + "0" * 64)
    with pytest.raises(AcceptedBaselineClassificationPolicyError):
        service.classify(context)


def test_observations_have_canonical_order_and_rule_lineage(context) -> None:
    result = AcceptedBaselineClassificationService().classify(context)
    keys = tuple(
        (
            item.subject.source_root_id,
            item.subject.relative_path,
            item.subject.item_id,
            item.dimension.value,
            item.observation_kind.value,
        )
        for item in result.observations
    )
    assert keys == tuple(sorted(keys))
    assert all(
        tuple(sorted(item.applied_rule_codes)) == item.applied_rule_codes
        for item in result.observations
    )


def test_input_is_not_mutated(context) -> None:
    before = repr(context)
    AcceptedBaselineClassificationService().classify(context)
    assert repr(context) == before


def test_service_signature_has_one_public_method_input() -> None:
    signature = inspect.signature(AcceptedBaselineClassificationService.classify)
    assert tuple(signature.parameters) == ("self", "context")


def test_service_has_no_filesystem_or_later_authority_surface() -> None:
    source = inspect.getsource(module)
    prohibited = (
        "import os",
        "pathlib",
        "open(",
        "subprocess",
        "socket",
        "requests",
        "database",
        "migration",
        "cleanup",
        "supersession",
        "destination",
        "classification_finding",
        "publish(",
        "persist(",
    )
    assert not any(token in source.lower() for token in prohibited)
    assert not any(name.startswith("_") and "authenticator" in name for name in module.__dict__)


def test_no_private_helpers_are_package_exports() -> None:
    import poe_backup_orchestrator.services as services

    assert "_default_policy" not in services.__all__
    assert "_behavior_manifest" not in services.__all__


def test_context_semantic_revalidation_does_not_read_files(context, monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("filesystem access is prohibited")

    monkeypatch.setattr("builtins.open", forbidden)
    assert AcceptedBaselineClassificationService().classify(context).observations


def test_manifest_is_canonical_json_and_runtime_reproducible() -> None:
    payload = _behavior_manifest(_default_policy().rules)
    encoded = _canonical_bytes(payload)
    assert b"\n" not in encoded
    assert json.loads(encoded) == payload
    assert hashlib.sha256(encoded).hexdigest() == BASELINE_CLASSIFICATION_POLICY_BEHAVIOR_ID
