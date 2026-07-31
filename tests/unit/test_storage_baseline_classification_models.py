"""Model tests for Slice 6C-2 deterministic classification."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from poe_backup_orchestrator.models.storage_baseline_classification import (
    STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION,
    STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION,
    AcceptedBaselineClassificationCandidate,
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationObservation,
    AcceptedBaselineClassificationObservationKind,
    AcceptedBaselineClassificationPolicyIdentity,
    AcceptedBaselineClassificationPredicate,
    AcceptedBaselineClassificationState,
    AcceptedBaselineClassificationSubject,
    stable_accepted_baseline_classification_policy_id,
)
from poe_backup_orchestrator.services.storage_baseline_classification import (
    _default_policy,
)


def test_schema_versions_and_identity_formats() -> None:
    policy = _default_policy()
    assert STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION == "1.0"
    assert STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION == "1.0"
    assert policy.identity.classification_policy_id.startswith("pbcp-")
    assert len(policy.identity.classification_policy_id) == 69


def test_models_are_frozen_and_slotted() -> None:
    subject = AcceptedBaselineClassificationSubject("root", "path/file", "item", "file")
    with pytest.raises((FrozenInstanceError, AttributeError)):
        subject.item_id = "changed"  # type: ignore[misc]
    assert not hasattr(subject, "__dict__")


@pytest.mark.parametrize(
    ("operator", "values"),
    (("exact", ()), ("exact", ("a", "b")), ("member_of", ()), ("present", ("x",))),
)
def test_predicate_contract_rejects_invalid_arity(operator: str, values: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        AcceptedBaselineClassificationPredicate("inventory.item_type", operator, values)


def test_predicates_require_canonical_unique_values() -> None:
    with pytest.raises(ValueError, match="unique and lexically ordered"):
        AcceptedBaselineClassificationPredicate("field", "member_of", ("z", "a"))
    with pytest.raises(ValueError, match="unique and lexically ordered"):
        AcceptedBaselineClassificationPredicate("field", "member_of", ("a", "a"))


def test_exact_four_dimensions_and_eight_states() -> None:
    assert {item.value for item in AcceptedBaselineClassificationDimension} == {
        "content_type",
        "inventory_support_state",
        "capture_state",
        "content_integrity_state",
    }
    assert len(AcceptedBaselineClassificationState) == 8
    assert tuple(AcceptedBaselineClassificationObservationKind) == (
        AcceptedBaselineClassificationObservationKind.DESCRIPTIVE_OBSERVATION,
    )


def test_default_policy_has_exact_canonical_rule_surface() -> None:
    policy = _default_policy()
    keys = tuple((rule.dimension.value, rule.rule_code) for rule in policy.rules)
    assert len(policy.rules) == 23
    assert keys == tuple(sorted(keys))
    assert len({rule.rule_code for rule in policy.rules}) == 23


def test_policy_identity_is_stable_and_semantically_sensitive() -> None:
    policy = _default_policy()
    kwargs = dict(
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
    assert (
        stable_accepted_baseline_classification_policy_id(**kwargs)
        == policy.identity.classification_policy_id
    )
    kwargs["policy_version"] = "1.1"
    assert (
        stable_accepted_baseline_classification_policy_id(**kwargs)
        != policy.identity.classification_policy_id
    )


def test_policy_rejects_tampered_identity() -> None:
    policy = _default_policy()
    with pytest.raises(ValueError, match="does not match"):
        replace(
            policy,
            identity=AcceptedBaselineClassificationPolicyIdentity(
                "1.0", "pbcp-" + "0" * 64, policy.identity.behavior_manifest_id
            ),
        )


def test_subject_rejects_absolute_and_traversing_paths() -> None:
    for value in ("/absolute", "../escape", "a/../b", "a\\b"):
        with pytest.raises(ValueError):
            AcceptedBaselineClassificationSubject("root", value, "item", "file")


def test_candidate_preserves_sorted_unique_rule_lineage() -> None:
    candidate = AcceptedBaselineClassificationCandidate("file", ("a-rule", "b-rule"))
    assert candidate.rule_codes == ("a-rule", "b-rule")
    with pytest.raises(ValueError):
        AcceptedBaselineClassificationCandidate("file", ("b-rule", "a-rule"))


@pytest.mark.parametrize(
    "state",
    (
        AcceptedBaselineClassificationState.AMBIGUOUS,
        AcceptedBaselineClassificationState.CONFLICTING,
    ),
)
def test_ambiguity_and_conflict_preserve_all_candidates(state) -> None:
    subject = AcceptedBaselineClassificationSubject("root", "path/file", "item", "file")
    observation = AcceptedBaselineClassificationObservation(
        subject,
        AcceptedBaselineClassificationDimension.CONTENT_TYPE,
        AcceptedBaselineClassificationObservationKind.DESCRIPTIVE_OBSERVATION,
        state,
        (
            AcceptedBaselineClassificationCandidate("file", ("a-rule",)),
            AcceptedBaselineClassificationCandidate("other", ("b-rule",)),
        ),
        None,
        ("a-rule", "b-rule"),
        (),
        ("multiple_candidates",),
        True,
        ("classification_review_required",),
    )
    assert tuple(item.value for item in observation.candidates) == ("file", "other")
    assert observation.selected_value is None


def test_mutable_rule_structures_are_rejected_at_typed_boundary() -> None:
    with pytest.raises((TypeError, ValueError)):
        AcceptedBaselineClassificationPredicate("field", "exact", ["x"])  # type: ignore[arg-type]


def test_model_module_has_no_service_dependency() -> None:
    import poe_backup_orchestrator.models.storage_baseline_classification as module

    source_names = set(module.__dict__)
    assert "AcceptedBaselineClassificationService" not in source_names
