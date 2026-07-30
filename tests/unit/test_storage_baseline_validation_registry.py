from dataclasses import FrozenInstanceError
from typing import ClassVar

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceType,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    PreservationBaselineValidationError,
    ValidationAdapterRegistry,
)


class InventoryAdapter:
    evidence_type: ClassVar[PreservationEvidenceType] = PreservationEvidenceType.INVENTORY_EVIDENCE
    schema_name: ClassVar[str] = "poe.storage.inventory-evidence"
    supported_versions: ClassVar[tuple[str, ...]] = ("1.0",)

    def parse(self, evidence_bytes: bytes) -> object:
        return evidence_bytes

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        return parsed_evidence


class IntegrityAdapter:
    evidence_type: ClassVar[PreservationEvidenceType] = (
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE
    )
    schema_name: ClassVar[str] = "poe.storage.content-integrity-evidence"
    supported_versions: ClassVar[tuple[str, ...]] = ("1.0",)

    def parse(self, evidence_bytes: bytes) -> object:
        return evidence_bytes

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        return parsed_evidence


def test_registry_canonicalizes_registration_order() -> None:
    registry = ValidationAdapterRegistry(
        adapters=(InventoryAdapter(), IntegrityAdapter()),
    )
    reversed_registry = ValidationAdapterRegistry(
        adapters=(IntegrityAdapter(), InventoryAdapter()),
    )

    assert tuple(adapter.evidence_type for adapter in registry.adapters) == tuple(
        adapter.evidence_type for adapter in reversed_registry.adapters
    )


def test_registry_resolves_exact_key() -> None:
    adapter = InventoryAdapter()
    registry = ValidationAdapterRegistry(adapters=(adapter,))

    assert (
        registry.resolve(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            schema_name="poe.storage.inventory-evidence",
            schema_version="1.0",
        )
        is adapter
    )


def test_registry_rejects_duplicate_or_ambiguous_key() -> None:
    with pytest.raises(
        PreservationBaselineValidationError,
        match="duplicate or ambiguous",
    ):
        ValidationAdapterRegistry(
            adapters=(InventoryAdapter(), InventoryAdapter()),
        )


def test_registry_rejects_unknown_schema_or_version() -> None:
    registry = ValidationAdapterRegistry(adapters=(InventoryAdapter(),))

    with pytest.raises(PreservationBaselineValidationError, match="no unique"):
        registry.resolve(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            schema_name="unknown",
            schema_version="1.0",
        )

    with pytest.raises(PreservationBaselineValidationError, match="no unique"):
        registry.resolve(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            schema_name="poe.storage.inventory-evidence",
            schema_version="2.0",
        )


def test_registry_is_immutable() -> None:
    registry = ValidationAdapterRegistry(adapters=(InventoryAdapter(),))

    with pytest.raises(FrozenInstanceError):
        registry.adapters = ()  # type: ignore[misc]
