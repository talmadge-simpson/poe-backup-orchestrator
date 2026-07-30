from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    EvidenceRequirementStatus,
    PreservationEvidenceReference,
    PreservationEvidenceRequirement,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.models.storage_content_integrity import (
    STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
)
from poe_backup_orchestrator.models.storage_inventory import (
    STORAGE_INVENTORY_SCHEMA_VERSION,
    PreservationBaselineIdentity,
)
from poe_backup_orchestrator.services.storage_baseline_composition import (
    PreservationBaselineComposer,
    PreservationBaselineCompositionError,
)
from poe_backup_orchestrator.services.storage_content_integrity_persistence import (
    PersistedContentIntegrityEvidence,
)
from poe_backup_orchestrator.services.storage_inventory_persistence import (
    InventoryEvidencePublication,
)

NOW = datetime(2026, 7, 30, 13, 0, tzinfo=UTC)
DIGEST = "a" * 64


def _identity() -> PreservationBaselineIdentity:
    return PreservationBaselineIdentity(
        schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
        baseline_id="baseline-a",
        created_at_utc=NOW,
        status="draft",
        retained_until="indefinite",
    )


def _requirement(
    kind: PreservationEvidenceType,
    applicable: bool = True,
    detail: str | None = None,
) -> PreservationEvidenceRequirement:
    return PreservationEvidenceRequirement(
        source_root_id="root-a",
        evidence_type=kind,
        applicable=applicable,
        detail=detail,
    )


def _reference(
    kind: PreservationEvidenceType,
) -> PreservationEvidenceReference:
    return PreservationEvidenceReference(
        evidence_type=kind,
        source_root_id="root-a",
        schema_version="1.0",
        evidence_path=Path(f"/evidence/{kind.value}.json"),
        digest_path=Path(f"/evidence/{kind.value}.sha256"),
        sha256=DIGEST,
        byte_count=100,
    )


def test_inventory_adapter() -> None:
    publication = InventoryEvidencePublication(
        evidence_path=Path("/evidence/inventory.ndjson"),
        sha256_path=Path("/evidence/inventory.ndjson.sha256"),
        sha256=DIGEST,
        item_count=1,
        byte_count=123,
        idempotent_replay=False,
    )
    adapted = PreservationBaselineComposer.inventory_evidence_reference(
        source_root_id="root-a",
        publication=publication,
    )
    assert adapted.byte_count == 123


def test_integrity_adapter() -> None:
    publication = PersistedContentIntegrityEvidence(
        evidence_path=Path("/evidence/integrity.json"),
        digest_path=Path("/evidence/integrity.sha256"),
        byte_count=321,
        sha256=DIGEST,
    )
    adapted = PreservationBaselineComposer.content_integrity_evidence_reference(
        source_root_id="root-a",
        schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
        publication=publication,
    )
    assert adapted.byte_count == 321


def test_missing_creates_absent() -> None:
    candidate = PreservationBaselineComposer(clock=lambda: NOW).compose(
        baseline_identity=_identity(),
        source_root_ids=("root-a",),
        requirements=(_requirement(PreservationEvidenceType.INVENTORY_EVIDENCE),),
        evidence_references=(),
    )
    assert candidate.observations[0].status is EvidenceRequirementStatus.ABSENT


def test_nonapplicable_creates_observation() -> None:
    candidate = PreservationBaselineComposer(clock=lambda: NOW).compose(
        baseline_identity=_identity(),
        source_root_ids=("root-a",),
        requirements=(
            _requirement(
                PreservationEvidenceType.RECONCILIATION_EVIDENCE,
                applicable=False,
                detail="not produced",
            ),
        ),
        evidence_references=(),
    )
    assert candidate.observations[0].status is EvidenceRequirementStatus.NOT_APPLICABLE


def test_present_creates_present() -> None:
    candidate = PreservationBaselineComposer(clock=lambda: NOW).compose(
        baseline_identity=_identity(),
        source_root_ids=("root-a",),
        requirements=(_requirement(PreservationEvidenceType.INVENTORY_EVIDENCE),),
        evidence_references=(_reference(PreservationEvidenceType.INVENTORY_EVIDENCE),),
    )
    assert candidate.observations[0].status is EvidenceRequirementStatus.PRESENT


def test_duplicate_requirement_rejected() -> None:
    requirement = _requirement(PreservationEvidenceType.INVENTORY_EVIDENCE)
    with pytest.raises(
        PreservationBaselineCompositionError,
        match="duplicate",
    ):
        PreservationBaselineComposer(clock=lambda: NOW).compose(
            baseline_identity=_identity(),
            source_root_ids=("root-a",),
            requirements=(requirement, requirement),
            evidence_references=(),
        )


def test_reference_without_requirement_rejected() -> None:
    with pytest.raises(
        PreservationBaselineCompositionError,
        match="do not match",
    ):
        PreservationBaselineComposer(clock=lambda: NOW).compose(
            baseline_identity=_identity(),
            source_root_ids=("root-a",),
            requirements=(_requirement(PreservationEvidenceType.INVENTORY_EVIDENCE),),
            evidence_references=(_reference(PreservationEvidenceType.DISCOVERY_RESULT),),
        )


def test_identity_repeatable_across_creation_times() -> None:
    kwargs = {
        "baseline_identity": _identity(),
        "source_root_ids": ("root-a",),
        "requirements": (_requirement(PreservationEvidenceType.INVENTORY_EVIDENCE),),
        "evidence_references": (_reference(PreservationEvidenceType.INVENTORY_EVIDENCE),),
    }
    first = PreservationBaselineComposer(clock=lambda: NOW).compose(**kwargs)
    later = datetime(2026, 7, 30, 14, 0, tzinfo=UTC)
    second = PreservationBaselineComposer(clock=lambda: later).compose(**kwargs)
    assert first.identity.candidate_id == second.identity.candidate_id
