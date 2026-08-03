"""Model tests for Slice 6C-3 classification findings."""

from __future__ import annotations

import itertools
from dataclasses import FrozenInstanceError, replace

import pytest

from poe_backup_orchestrator.models.storage_baseline_classification import (
    AcceptedBaselineClassificationDimension,
    AcceptedBaselineClassificationState,
)
from poe_backup_orchestrator.models.storage_baseline_classification_findings import (
    STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION,
    STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
    AcceptedBaselineClassificationFindingCategory,
    AcceptedBaselineClassificationFindingIdentity,
    AcceptedBaselineClassificationFindingPolicy,
    AcceptedBaselineClassificationFindingPolicyIdentity,
    AcceptedBaselineClassificationFindingResultIdentity,
    AcceptedBaselineClassificationFindingRule,
    AcceptedBaselineClassificationFindingSeverity,
    _finding_rules_overlap,
    stable_accepted_baseline_classification_finding_policy_id,
)
from poe_backup_orchestrator.services.storage_baseline_classification_findings import (
    _default_policy,
)


def _policy_id(policy, **changes):
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
    return stable_accepted_baseline_classification_finding_policy_id(**values)


def test_schema_versions_identity_formats_and_exact_vocabularies() -> None:
    policy = _default_policy()
    assert STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION == "1.0"
    assert STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION == "1.0"
    assert policy.identity.classification_finding_policy_id.startswith("pbcfp-")
    assert len(policy.identity.classification_finding_policy_id) == 70
    assert {item.name for item in AcceptedBaselineClassificationFindingCategory} == {
        "POLICY_NONCOVERAGE",
        "CLASSIFICATION_UNCERTAINTY",
        "CLASSIFICATION_CONFLICT",
        "INSUFFICIENT_EVIDENCE",
        "UNSUPPORTED_CLASSIFICATION",
        "CLASSIFICATION_REVIEW",
        "CAPTURE_CONDITION",
        "INTEGRITY_CONDITION",
    }
    assert {item.name for item in AcceptedBaselineClassificationFindingSeverity} == {
        "WARNING",
        "ERROR",
    }


def test_identity_models_reject_wrong_types_and_malformed_predecessor_id() -> None:
    policy = _default_policy()
    with pytest.raises(ValueError):
        AcceptedBaselineClassificationFindingPolicyIdentity(
            STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION,
            policy.identity.classification_finding_policy_id,
            None,  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError):
        AcceptedBaselineClassificationFindingIdentity(
            STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
            None,  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="pbcos with a digest"):
        AcceptedBaselineClassificationFindingResultIdentity(
            STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION,
            "pbcfr-" + "0" * 64,
            "pbcos-not-a-digest",
            policy.identity.classification_finding_policy_id,
        )


def test_models_are_frozen_slotted_and_service_independent() -> None:
    rule = _default_policy().rules[0]
    with pytest.raises((FrozenInstanceError, AttributeError)):
        rule.rule_code = "changed"  # type: ignore[misc]
    assert not hasattr(rule, "__dict__")
    import poe_backup_orchestrator.models.storage_baseline_classification_findings as module

    assert "AcceptedBaselineClassificationFindingService" not in module.__dict__


def test_default_policy_has_exact_rule_reconciliation() -> None:
    rules = _default_policy().rules
    assert len(rules) == 12
    assert len({rule.rule_code for rule in rules}) == 12
    assert (
        sum(
            rule.accepted_states != (AcceptedBaselineClassificationState.CLASSIFIED,)
            for rule in rules
        )
        == 6
    )
    assert (
        sum(
            rule.accepted_states == (AcceptedBaselineClassificationState.CLASSIFIED,)
            for rule in rules
        )
        == 6
    )
    keys = tuple(
        (
            rule.accepted_states[0].value,
            rule.accepted_dimensions[0].value if rule.accepted_dimensions else "",
            rule.rule_code,
        )
        for rule in rules
    )
    assert keys == tuple(sorted(keys))


def test_all_66_rule_pairs_are_non_overlapping() -> None:
    pairs = tuple(itertools.combinations(_default_policy().rules, 2))
    assert len(pairs) == 66
    assert not [
        (left.rule_code, right.rule_code)
        for left, right in pairs
        if _finding_rules_overlap(left, right)
    ]


def test_same_state_dimension_intersecting_value_rules_overlap() -> None:
    left = AcceptedBaselineClassificationFindingRule(
        "left",
        (AcceptedBaselineClassificationState.CLASSIFIED,),
        (AcceptedBaselineClassificationDimension.CONTENT_TYPE,),
        ("other",),
        True,
        AcceptedBaselineClassificationFindingCategory.CLASSIFICATION_REVIEW,
        AcceptedBaselineClassificationFindingSeverity.WARNING,
        "left_finding",
        "left_rationale",
    )
    right = replace(left, rule_code="right", finding_code="right_finding")
    assert _finding_rules_overlap(left, right)


def test_policy_rejects_static_overlap() -> None:
    policy = _default_policy()
    rules = list(policy.rules)
    rules[1] = replace(rules[1], accepted_states=rules[0].accepted_states)
    rules = sorted(
        rules,
        key=lambda rule: (
            rule.accepted_states[0].value,
            rule.accepted_dimensions[0].value if rule.accepted_dimensions else "",
            rule.rule_code,
        ),
    )
    with pytest.raises(ValueError, match="overlapping"):
        replace(policy, rules=tuple(rules))


def test_rule_rejects_mutable_and_noncanonical_structures() -> None:
    rule = _default_policy().rules[0]
    with pytest.raises(ValueError, match="immutable"):
        replace(rule, accepted_states=[AcceptedBaselineClassificationState.UNKNOWN])  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="ordered"):
        replace(
            _default_policy().rules[1],
            accepted_selected_values=("pending", "excluded"),
        )
    with pytest.raises(ValueError):
        replace(rule, rule_code=None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("field", "value"),
    (("category", "readiness"), ("severity", "blocking")),
)
def test_rule_rejects_values_outside_closed_finding_vocabularies(field, value) -> None:
    with pytest.raises(ValueError, match="closed finding"):
        replace(_default_policy().rules[0], **{field: value})


@pytest.mark.parametrize(
    ("field", "value"),
    (("accepted_states", ("unknown",)), ("accepted_dimensions", ("content_type",))),
)
def test_rule_rejects_values_outside_predecessor_vocabularies(field, value) -> None:
    with pytest.raises(ValueError, match="closed classification"):
        replace(_default_policy().rules[0], **{field: value})


def test_policy_identity_is_stable_and_sensitive_to_every_semantic_collection() -> None:
    policy = _default_policy()
    assert _policy_id(policy) == policy.identity.classification_finding_policy_id
    assert _policy_id(policy, policy_version="1.1") != _policy_id(policy)
    assert _policy_id(
        policy,
        benign_no_finding_codes=policy.benign_no_finding_codes + ("future_benign",),
    ) != _policy_id(policy)
    assert _policy_id(
        policy,
        operational_exclusions=policy.operational_exclusions + ("transport_extension",),
    ) != _policy_id(policy)


def test_policy_rejects_mutable_collections() -> None:
    policy = _default_policy()
    with pytest.raises(ValueError, match="immutable"):
        AcceptedBaselineClassificationFindingPolicy(
            policy.identity,
            policy.policy_version,
            policy.behavior_manifest_version,
            list(policy.rules),  # type: ignore[arg-type]
            policy.benign_no_finding_codes,
            policy.category_vocabulary,
            policy.severity_vocabulary,
            policy.operational_exclusions,
        )
    with pytest.raises(ValueError, match="identity must be"):
        replace(policy, identity=None)  # type: ignore[arg-type]


def test_public_models_have_no_later_authority_fields() -> None:
    forbidden = {
        "blocking",
        "readiness",
        "recommendation",
        "action",
        "approval",
        "destination",
        "migration",
        "cleanup",
        "persistence",
        "publication",
        "certification",
    }
    import poe_backup_orchestrator.models.storage_baseline_classification_findings as module

    for name in module.__dict__:
        value = module.__dict__[name]
        fields = getattr(value, "__dataclass_fields__", {})
        assert forbidden.isdisjoint(fields)
