"""Tests for immutable Slice 6C-1 analytical-intake contracts."""

from __future__ import annotations

import dataclasses
import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_analysis import (
    BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID,
    BASELINE_ANALYSIS_FACT_PROJECTION_ID,
    STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION,
    STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION,
    AcceptedBaselineAnalysisEvidence,
    AcceptedBaselineAnalysisEvidenceStatus,
    FrozenJsonArray,
    FrozenJsonObject,
    stable_accepted_baseline_analysis_context_id,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    EvidenceRequirementObservation,
    EvidenceRequirementStatus,
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.services.storage_baseline_analysis import (
    AcceptedBaselineAnalysisIntakeService,
    _canonical_frozen_bytes,
)


def test_schema_versions_and_behavior_identities_are_exact() -> None:
    assert STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION == "1.0"
    assert STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION == "1.0"
    assert BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID == (
        "f8d9caf9c32ff3da38b901efb001faf4f31cd131a567f2e2acfc0abaf06825d2"
    )
    assert BASELINE_ANALYSIS_FACT_PROJECTION_ID == (
        "00c4f0f475908c11ebc8f42aec8d4b4dd9b39f5fdfa3dbcd56fdde4feebfdaec"
    )


def test_default_profile_has_approved_identity_and_resource_envelope() -> None:
    profile = AcceptedBaselineAnalysisIntakeService().profile

    assert profile.identity.analysis_profile_id == (
        "pbaip-f46394209d6cd23846874ec56d4cfee861ff826108c1444fe7088ca346c7d2ee"
    )
    assert profile.maximum_inventory_evidence_bytes == 40_000_000
    assert profile.maximum_content_integrity_evidence_bytes == 40_000_000
    assert profile.maximum_inventory_items_per_root == 25_000
    assert profile.maximum_integrity_observations_per_root == 25_000
    assert profile.maximum_aggregate_evidence_bytes == 80_000_000
    assert profile.maximum_aggregate_projected_items == 50_000
    assert profile.maximum_inventory_ndjson_record_bytes == 1_647
    assert profile.json_nesting_depth_limit is None


def test_profile_models_are_frozen_slotted_and_service_independent() -> None:
    profile = AcceptedBaselineAnalysisIntakeService().profile

    assert profile.__slots__
    with pytest.raises(dataclasses.FrozenInstanceError):
        profile.profile_version = "changed"  # type: ignore[misc]
    assert "services" not in Path(
        __import__(
            "poe_backup_orchestrator.models.storage_baseline_analysis",
            fromlist=["__file__"],
        ).__file__
    ).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "change",
    (
        {"maximum_inventory_evidence_bytes": 39_999_999},
        {"maximum_inventory_items_per_root": 24_999},
        {"resource_profile_version": "poe.storage.baseline-analysis.resource-profile/2.0"},
        {"fact_projection_id": "1" * 64},
    ),
)
def test_profile_identity_is_sensitive_to_every_semantic_change(change: dict[str, object]) -> None:
    profile = AcceptedBaselineAnalysisIntakeService().profile

    with pytest.raises(ValueError, match="analysis_profile_id"):
        replace(profile, **change)


def test_profile_rejects_invalid_limits_and_rule_order() -> None:
    profile = AcceptedBaselineAnalysisIntakeService().profile

    with pytest.raises(ValueError, match="greater than zero"):
        replace(profile, maximum_aggregate_evidence_bytes=0)
    with pytest.raises(ValueError, match="canonically ordered"):
        replace(profile, evidence_rules=tuple(reversed(profile.evidence_rules)))


def test_lineage_only_evidence_rejects_operational_or_semantic_payload() -> None:
    observation = EvidenceRequirementObservation(
        source_root_id="root-a",
        evidence_type=PreservationEvidenceType.BASELINE_MANIFEST,
        status=EvidenceRequirementStatus.NOT_APPLICABLE,
        evidence_reference=None,
        detail="Lineage retained without opening.",
    )
    with pytest.raises(ValueError, match="lineage-only"):
        AcceptedBaselineAnalysisEvidence(
            observation=observation,
            status=AcceptedBaselineAnalysisEvidenceStatus.LINEAGE_ONLY,
            schema_name="forbidden",
            schema_version=None,
            evidence_semantic_id=None,
            fact_projection_id=None,
            semantic_facts=None,
        )


def _semantic_evidence(value):
    reference = PreservationEvidenceReference(
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        "root-a",
        "1.0",
        Path("/tmp/evidence.ndjson"),
        Path("/tmp/evidence.ndjson.sha256"),
        "a" * 64,
        1,
    )
    observation = EvidenceRequirementObservation(
        "root-a",
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        EvidenceRequirementStatus.PRESENT,
        reference,
    )
    return AcceptedBaselineAnalysisEvidence(
        observation=observation,
        status=AcceptedBaselineAnalysisEvidenceStatus.AUTHENTICATED,
        schema_name="poe.storage.inventory-evidence",
        schema_version="1.0",
        evidence_semantic_id=hashlib.sha256(_canonical_frozen_bytes(value)).hexdigest(),
        fact_projection_id=BASELINE_ANALYSIS_FACT_PROJECTION_ID,
        semantic_facts=value,
        artifact_path=reference.evidence_path,
        sidecar_path=reference.digest_path,
        transport_sha256="a" * 64,
        verified_byte_count=1,
        artifact_link_count=1,
        sidecar_link_count=1,
    )


def test_frozen_empty_object_and_array_preserve_distinct_json_semantics() -> None:
    empty_object = FrozenJsonObject(())
    empty_array = FrozenJsonArray(())

    assert empty_object != empty_array
    assert _canonical_frozen_bytes(empty_object) == b"{}"
    assert _canonical_frozen_bytes(empty_array) == b"[]"
    assert (
        _semantic_evidence(empty_object).evidence_semantic_id
        != _semantic_evidence(empty_array).evidence_semantic_id
    )


def test_nested_empty_objects_and_arrays_change_context_identity() -> None:
    object_value = FrozenJsonObject((("nested", FrozenJsonArray((FrozenJsonObject(()),))),))
    array_value = FrozenJsonObject((("nested", FrozenJsonArray((FrozenJsonArray(()),))),))
    object_evidence = _semantic_evidence(object_value)
    array_evidence = _semantic_evidence(array_value)
    profile = AcceptedBaselineAnalysisIntakeService().profile

    object_context = stable_accepted_baseline_analysis_context_id(
        accepted_baseline_id="pab-" + "b" * 64,
        profile=profile,
        authenticated_evidence=(object_evidence,),
        lineage_only_evidence=(),
    )
    array_context = stable_accepted_baseline_analysis_context_id(
        accepted_baseline_id="pab-" + "b" * 64,
        profile=profile,
        authenticated_evidence=(array_evidence,),
        lineage_only_evidence=(),
    )

    assert object_context != array_context


@pytest.mark.parametrize("mutable", ({}, [], {"nested": []}, [dict()]))
def test_semantic_facts_reject_mutable_json_values(mutable: object) -> None:
    with pytest.raises(ValueError, match="recursively immutable"):
        _semantic_evidence(mutable)
