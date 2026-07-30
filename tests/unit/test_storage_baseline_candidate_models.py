from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
    EvidenceRequirementObservation,
    EvidenceRequirementStatus,
    PreservationBaselineCandidateIdentity,
    PreservationBaselineCandidateScope,
    PreservationEvidenceReference,
    PreservationEvidenceRequirement,
    PreservationEvidenceType,
    stable_preservation_baseline_candidate_id,
)

NOW = datetime(2026, 7, 30, 13, 0, tzinfo=UTC)
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def _reference(
    path: str = "/evidence/a.json",
    digest: str = DIGEST_A,
    size: int = 100,
) -> PreservationEvidenceReference:
    return PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        source_root_id="root-a",
        schema_version="1.0",
        evidence_path=Path(path),
        digest_path=Path(f"{path}.sha256"),
        sha256=digest,
        byte_count=size,
    )


def _observation(
    reference: PreservationEvidenceReference | None = None,
) -> EvidenceRequirementObservation:
    reference = reference or _reference()
    return EvidenceRequirementObservation(
        source_root_id="root-a",
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        status=EvidenceRequirementStatus.PRESENT,
        evidence_reference=reference,
    )


def test_reference_requires_absolute_path() -> None:
    with pytest.raises(ValueError, match="evidence_path must be absolute"):
        _reference("relative.json")


def test_reference_rejects_negative_byte_count() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        _reference(size=-1)


def test_present_requires_reference() -> None:
    with pytest.raises(ValueError, match="requires evidence_reference"):
        EvidenceRequirementObservation(
            source_root_id="root-a",
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            status=EvidenceRequirementStatus.PRESENT,
            evidence_reference=None,
        )


def test_nonapplicable_requirement_requires_detail() -> None:
    with pytest.raises(ValueError, match="requires detail"):
        PreservationEvidenceRequirement(
            source_root_id="root-a",
            evidence_type=PreservationEvidenceType.DISCOVERY_RESULT,
            applicable=False,
        )


def test_scope_rejects_unordered_roots() -> None:
    with pytest.raises(ValueError, match="deterministic"):
        PreservationBaselineCandidateScope(
            baseline_id="baseline-a",
            source_root_ids=("root-b", "root-a"),
        )


def test_identity_requires_utc() -> None:
    with pytest.raises(ValueError, match="UTC"):
        PreservationBaselineCandidateIdentity(
            schema_version=STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
            candidate_id=f"pbc-{DIGEST_A}",
            baseline_id="baseline-a",
            created_at_utc=datetime(2026, 7, 30, 13, 0),
        )


def test_scope_is_immutable() -> None:
    scope = PreservationBaselineCandidateScope(
        "baseline-a",
        ("root-a",),
    )
    with pytest.raises(FrozenInstanceError):
        scope.baseline_id = "changed"  # type: ignore[misc]


def test_candidate_id_is_path_independent() -> None:
    first = stable_preservation_baseline_candidate_id(
        baseline_id="baseline-a",
        source_root_ids=("root-a",),
        observations=(_observation(_reference("/first/a.json")),),
    )
    second = stable_preservation_baseline_candidate_id(
        baseline_id="baseline-a",
        source_root_ids=("root-a",),
        observations=(_observation(_reference("/second/a.json")),),
    )
    assert first == second


def test_candidate_id_changes_with_digest() -> None:
    first = stable_preservation_baseline_candidate_id(
        baseline_id="baseline-a",
        source_root_ids=("root-a",),
        observations=(_observation(_reference(digest=DIGEST_A)),),
    )
    second = stable_preservation_baseline_candidate_id(
        baseline_id="baseline-a",
        source_root_ids=("root-a",),
        observations=(_observation(_reference(digest=DIGEST_B)),),
    )
    assert first != second
