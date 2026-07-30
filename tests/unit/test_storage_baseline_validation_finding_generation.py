"""Tests for deterministic reconciliation finding generation."""

from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceType,
)
from poe_backup_orchestrator.models.storage_baseline_validation import (
    ValidationFindingCategory,
    ValidationFindingSeverity,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    ContentIntegrityValidationFacts,
    InventoryValidationFacts,
    PreservationEvidenceReconciliationService,
    PreservationValidationFindingGenerationService,
)


def frozen_object(**values: object):
    return tuple(sorted(values.items()))


def inventory(
    *records: object,
    source_root_id: str = "root-1",
    declared_item_count: int | None = None,
) -> InventoryValidationFacts:
    return InventoryValidationFacts(
        schema_version="1.0",
        source_root_id=source_root_id,
        declared_item_count=(len(records) if declared_item_count is None else declared_item_count),
        records=tuple(records),  # type: ignore[arg-type]
        totals=frozen_object(item_count=len(records)),
    )


def integrity(
    *records: object,
    source_root_id: str = "root-1",
) -> ContentIntegrityValidationFacts:
    return ContentIntegrityValidationFacts(
        schema_version="1.0",
        source_root_id=source_root_id,
        evidence=tuple(records),  # type: ignore[arg-type]
        totals=frozen_object(candidate_file_count=len(records)),
    )


def generate(
    *,
    inventory_facts: InventoryValidationFacts,
    integrity_facts: ContentIntegrityValidationFacts,
):
    reconciliation = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory_facts,
        integrity_facts=integrity_facts,
    )
    return PreservationValidationFindingGenerationService().generate(
        reconciliation=reconciliation,
        inventory_evidence_path=Path("/evidence/inventory.jsonl"),
        integrity_evidence_path=Path("/evidence/integrity.jsonl"),
    )


def test_matching_reconciliation_produces_no_routine_findings() -> None:
    findings = generate(
        inventory_facts=inventory(
            frozen_object(item_id="a", relative_path="a.bin"),
        ),
        integrity_facts=integrity(
            frozen_object(item_id="a", relative_path="a.bin"),
        ),
    )
    assert findings == ()


def test_declared_inventory_count_mismatch_becomes_error_finding() -> None:
    findings = generate(
        inventory_facts=inventory(
            frozen_object(relative_path="a.bin"),
            declared_item_count=2,
        ),
        integrity_facts=integrity(
            frozen_object(relative_path="a.bin"),
        ),
    )
    finding = findings[0]
    assert finding.sequence == 1
    assert finding.category is ValidationFindingCategory.INVENTORY_RECONCILIATION_MISMATCH
    assert finding.severity is ValidationFindingSeverity.ERROR
    assert finding.expected == "2"
    assert finding.observed == "1"


def test_inventory_only_item_becomes_integrity_reconciliation_finding() -> None:
    finding = generate(
        inventory_facts=inventory(frozen_object(relative_path="a.bin")),
        integrity_facts=integrity(),
    )[0]
    assert finding.category is (ValidationFindingCategory.CONTENT_INTEGRITY_RECONCILIATION_MISMATCH)
    assert finding.evidence_type is (PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE)


def test_integrity_only_item_becomes_inventory_reconciliation_finding() -> None:
    finding = generate(
        inventory_facts=inventory(),
        integrity_facts=integrity(frozen_object(relative_path="a.bin")),
    )[0]
    assert finding.category is ValidationFindingCategory.INVENTORY_RECONCILIATION_MISMATCH
    assert finding.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE


def test_duplicate_paths_become_deterministic_duplicate_findings() -> None:
    findings = generate(
        inventory_facts=inventory(
            frozen_object(item_id="2", relative_path="dup.bin"),
            frozen_object(item_id="1", relative_path="dup.bin"),
        ),
        integrity_facts=integrity(
            frozen_object(item_id="2", relative_path="other.bin"),
            frozen_object(item_id="1", relative_path="other.bin"),
        ),
    )
    assert tuple(finding.category for finding in findings) == (
        ValidationFindingCategory.DUPLICATE_EVIDENCE,
        ValidationFindingCategory.DUPLICATE_EVIDENCE,
    )
    assert tuple(finding.sequence for finding in findings) == (1, 2)


def test_item_identity_disagreement_becomes_contradictory_evidence() -> None:
    finding = generate(
        inventory_facts=inventory(
            frozen_object(item_id="inventory-id", relative_path="a.bin"),
        ),
        integrity_facts=integrity(
            frozen_object(item_id="integrity-id", relative_path="a.bin"),
        ),
    )[0]
    assert finding.category is ValidationFindingCategory.CONTRADICTORY_EVIDENCE
    assert finding.severity is ValidationFindingSeverity.ERROR


def test_source_root_mismatch_becomes_critical_identity_finding() -> None:
    finding = generate(
        inventory_facts=inventory(source_root_id="root-a"),
        integrity_facts=integrity(source_root_id="root-b"),
    )[0]
    assert finding.category is ValidationFindingCategory.SOURCE_ROOT_IDENTITY_MISMATCH
    assert finding.severity is ValidationFindingSeverity.CRITICAL


def test_invalid_record_shape_becomes_critical_contradiction_finding() -> None:
    finding = generate(
        inventory_facts=inventory(
            frozen_object(item_id="missing-relative-path"),
        ),
        integrity_facts=integrity(),
    )[0]
    assert finding.category is ValidationFindingCategory.CONTRADICTORY_EVIDENCE
    assert finding.severity is ValidationFindingSeverity.CRITICAL


def test_findings_are_canonically_ordered_and_contiguously_sequenced() -> None:
    first = generate(
        inventory_facts=inventory(
            frozen_object(relative_path="z.bin"),
            frozen_object(relative_path="a.bin"),
            declared_item_count=3,
        ),
        integrity_facts=integrity(
            frozen_object(relative_path="x.bin"),
        ),
    )
    second = generate(
        inventory_facts=inventory(
            frozen_object(relative_path="a.bin"),
            frozen_object(relative_path="z.bin"),
            declared_item_count=3,
        ),
        integrity_facts=integrity(
            frozen_object(relative_path="x.bin"),
        ),
    )
    assert first == second
    assert tuple(finding.sequence for finding in first) == tuple(range(1, len(first) + 1))


def test_generator_requires_absolute_evidence_paths() -> None:
    reconciliation = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(),
        integrity_facts=integrity(),
    )
    with pytest.raises(ValueError, match="absolute"):
        PreservationValidationFindingGenerationService().generate(
            reconciliation=reconciliation,
            inventory_evidence_path=Path("inventory.jsonl"),
            integrity_evidence_path=Path("/evidence/integrity.jsonl"),
        )


def test_generator_exposes_no_acceptance_or_authority_fields() -> None:
    fields = set(PreservationValidationFindingGenerationService.__dataclass_fields__)
    assert "acceptance_recommendation" not in fields
    assert "acceptance_mode" not in fields
    assert "human_authorization" not in fields
    assert "migration_authority" not in fields
    assert "cleanup_authority" not in fields
