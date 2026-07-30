"""Tests for deterministic preservation-evidence reconciliation facts."""

from dataclasses import FrozenInstanceError

import pytest

from poe_backup_orchestrator.services.storage_baseline_validation import (
    ContentIntegrityValidationFacts,
    EvidenceReconciliationStatus,
    InventoryValidationFacts,
    PreservationEvidenceReconciliationService,
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
        declared_item_count=len(records) if declared_item_count is None else declared_item_count,
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


def test_reconciliation_matches_by_canonical_relative_path() -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(
            frozen_object(item_id="inv-b", relative_path="b.bin"),
            frozen_object(item_id="inv-a", relative_path="a.bin"),
        ),
        integrity_facts=integrity(
            frozen_object(item_id="int-a", relative_path="a.bin"),
            frozen_object(item_id="int-c", relative_path="c.bin"),
        ),
    )

    assert result.status is EvidenceReconciliationStatus.RECONCILED
    assert tuple(item.relative_path for item in result.matched) == ("a.bin",)
    assert result.matched[0].inventory_item_id == "inv-a"
    assert result.matched[0].integrity_item_id == "int-a"
    assert tuple(item.relative_path for item in result.inventory_only) == ("b.bin",)
    assert tuple(item.relative_path for item in result.integrity_only) == ("c.bin",)


def test_reconciliation_retains_count_observations_without_judgment() -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(
            frozen_object(relative_path="a.bin"),
            declared_item_count=7,
        ),
        integrity_facts=integrity(
            frozen_object(relative_path="a.bin"),
        ),
    )

    assert result.counts is not None
    assert result.counts.inventory_declared_item_count == 7
    assert result.counts.inventory_observed_record_count == 1
    assert result.counts.integrity_observed_record_count == 1
    assert not hasattr(result, "findings")
    assert not hasattr(result, "severity")
    assert not hasattr(result, "acceptance_recommendation")


def test_duplicate_paths_are_retained_and_excluded_from_unique_matching() -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(
            frozen_object(item_id="one", relative_path="dup.bin"),
            frozen_object(item_id="two", relative_path="dup.bin"),
            frozen_object(item_id="unique", relative_path="unique.bin"),
        ),
        integrity_facts=integrity(
            frozen_object(item_id="int-dup", relative_path="dup.bin"),
            frozen_object(item_id="int-unique", relative_path="unique.bin"),
        ),
    )

    assert result.duplicate_inventory_paths == ("dup.bin",)
    assert result.duplicate_integrity_paths == ()
    assert tuple(item.relative_path for item in result.matched) == ("unique.bin",)
    assert tuple(item.relative_path for item in result.integrity_only) == ("dup.bin",)
    assert result.counts is not None
    assert result.counts.duplicate_inventory_path_count == 1


def test_source_root_mismatch_returns_explicit_nonsemantic_status() -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(
            frozen_object(relative_path="a.bin"),
            source_root_id="root-a",
        ),
        integrity_facts=integrity(
            frozen_object(relative_path="a.bin"),
            source_root_id="root-b",
        ),
    )

    assert result.status is EvidenceReconciliationStatus.SOURCE_ROOT_MISMATCH
    assert result.detail_code == "source_root_ids_do_not_match"
    assert result.counts is None
    assert result.matched == ()


@pytest.mark.parametrize(
    "bad_record",
    [
        frozen_object(item_id="missing-path"),
        frozen_object(relative_path=123),
        frozen_object(item_id=123, relative_path="a.bin"),
    ],
)
def test_invalid_reconciliation_record_shapes_fail_explicitly(
    bad_record: object,
) -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(bad_record),
        integrity_facts=integrity(),
    )

    assert result.status is EvidenceReconciliationStatus.RECONCILIATION_FAILED
    assert result.detail_code == "reconciliation_record_shape_invalid"
    assert result.counts is None


def test_reconciliation_is_deterministic_and_non_mutating() -> None:
    inventory_facts = inventory(
        frozen_object(item_id="b", relative_path="b.bin"),
        frozen_object(item_id="a", relative_path="a.bin"),
    )
    integrity_facts = integrity(
        frozen_object(item_id="a", relative_path="a.bin"),
        frozen_object(item_id="b", relative_path="b.bin"),
    )
    service = PreservationEvidenceReconciliationService()

    first = service.reconcile(
        inventory_facts=inventory_facts,
        integrity_facts=integrity_facts,
    )
    second = service.reconcile(
        inventory_facts=inventory_facts,
        integrity_facts=integrity_facts,
    )

    assert first == second
    assert first.inventory_facts is inventory_facts
    assert first.integrity_facts is integrity_facts


def test_reconciliation_result_is_frozen() -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(frozen_object(relative_path="a.bin")),
        integrity_facts=integrity(frozen_object(relative_path="a.bin")),
    )

    with pytest.raises(FrozenInstanceError):
        result.status = EvidenceReconciliationStatus.RECONCILIATION_FAILED  # type: ignore[misc]


def test_item_identifier_disagreement_is_observed_not_classified() -> None:
    result = PreservationEvidenceReconciliationService().reconcile(
        inventory_facts=inventory(
            frozen_object(item_id="inventory-id", relative_path="a.bin"),
        ),
        integrity_facts=integrity(
            frozen_object(item_id="integrity-id", relative_path="a.bin"),
        ),
    )

    assert result.matched[0].inventory_item_id == "inventory-id"
    assert result.matched[0].integrity_item_id == "integrity-id"
    assert result.status is EvidenceReconciliationStatus.RECONCILED
