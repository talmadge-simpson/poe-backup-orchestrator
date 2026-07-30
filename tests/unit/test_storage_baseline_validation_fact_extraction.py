"""Tests for immutable adapter-driven preservation validation facts."""

from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import ClassVar

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
    ContentIntegrityEvidenceAdapter,
    ContentIntegrityValidationFacts,
    EvidenceFactExtractionStatus,
    EvidenceLoadStatus,
    InventoryEvidenceAdapter,
    InventoryValidationFacts,
    LoadedPreservationEvidence,
    PreservationEvidenceDeserializationService,
    PreservationEvidenceFactExtractionService,
    ValidationAdapterRegistry,
)

INVENTORY_BYTES = (
    b'{"item_count":2,"record_kind":"inventory_header","schema_version":"1.0",'
    b'"source_root_id":"root-1","totals":{"pending_count":2}}\n'
    b'{"record_kind":"inventory_item","relative_path":"a.txt","support_status":"supported"}\n'
    b'{"record_kind":"inventory_item","relative_path":"link","support_status":"unsupported"}\n'
)
INTEGRITY_BYTES = (
    b'{"evidence":[{"item_id":"item-a","outcome":"verified","relative_path":"a.txt"}],'
    b'"schema_version":"1.0","source_root_id":"root-1",'
    b'"totals":{"candidate_file_count":1,"verified_count":1}}\n'
)


def loaded(evidence_type: PreservationEvidenceType, content: bytes) -> LoadedPreservationEvidence:
    reference = PreservationEvidenceReference(
        evidence_type=evidence_type,
        source_root_id="root-1",
        schema_version="1.0",
        evidence_path=Path("/evidence/artifact"),
        digest_path=Path("/evidence/artifact.sha256"),
        sha256=hashlib.sha256(content).hexdigest(),
        byte_count=len(content),
    )
    return LoadedPreservationEvidence(
        reference=reference,
        status=EvidenceLoadStatus.VERIFIED,
        evidence_bytes=content,
        calculated_sha256=reference.sha256,
        calculated_byte_count=len(content),
        sidecar_sha256=reference.sha256,
    )


def deserialize(adapter: object, evidence_type: PreservationEvidenceType, content: bytes):
    service = PreservationEvidenceDeserializationService(
        ValidationAdapterRegistry(adapters=(adapter,))  # type: ignore[arg-type]
    )
    return service.deserialize(loaded(evidence_type, content))


def test_inventory_facts_are_typed_and_immutable() -> None:
    deserialized = deserialize(
        InventoryEvidenceAdapter(),
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        INVENTORY_BYTES,
    )
    result = PreservationEvidenceFactExtractionService().extract(deserialized)
    assert result.status is EvidenceFactExtractionStatus.EXTRACTED
    assert isinstance(result.facts, InventoryValidationFacts)
    assert result.facts.source_root_id == "root-1"
    assert result.facts.declared_item_count == 2
    assert len(result.facts.records) == 2
    assert result.facts.totals == (("pending_count", 2),)
    with pytest.raises(FrozenInstanceError):
        result.facts.declared_item_count = 3  # type: ignore[misc]


def test_integrity_facts_are_typed_and_immutable() -> None:
    deserialized = deserialize(
        ContentIntegrityEvidenceAdapter(),
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        INTEGRITY_BYTES,
    )
    result = PreservationEvidenceFactExtractionService().extract(deserialized)
    assert result.status is EvidenceFactExtractionStatus.EXTRACTED
    assert isinstance(result.facts, ContentIntegrityValidationFacts)
    assert result.facts.source_root_id == "root-1"
    assert len(result.facts.evidence) == 1
    assert result.facts.totals == (
        ("candidate_file_count", 1),
        ("verified_count", 1),
    )


def test_fact_extraction_requires_deserialized_evidence() -> None:
    deserialized = deserialize(
        InventoryEvidenceAdapter(),
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        b"{bad}\n",
    )
    result = PreservationEvidenceFactExtractionService().extract(deserialized)
    assert result.status is EvidenceFactExtractionStatus.DESERIALIZATION_REQUIRED
    assert result.facts is None
    assert result.detail_code == "evidence_not_deserialized"


class FailingAdapter:
    evidence_type: ClassVar[PreservationEvidenceType] = (
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE
    )
    schema_name: ClassVar[str] = CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME
    supported_versions: ClassVar[tuple[str, ...]] = ("1.0",)

    def parse(self, evidence_bytes: bytes) -> object:
        return ()

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        raise ValueError("deliberate failure")


def test_adapter_failure_is_isolated() -> None:
    deserialized = deserialize(
        FailingAdapter(),
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        INTEGRITY_BYTES,
    )
    result = PreservationEvidenceFactExtractionService().extract(deserialized)
    assert result.status is EvidenceFactExtractionStatus.EXTRACTION_FAILED
    assert result.facts is None
    assert result.detail_code == "adapter_fact_extraction_failed"


def test_extraction_is_deterministic_and_non_mutating() -> None:
    deserialized = deserialize(
        InventoryEvidenceAdapter(),
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        INVENTORY_BYTES,
    )
    before = deserialized.parsed_evidence
    service = PreservationEvidenceFactExtractionService()
    assert service.extract(deserialized) == service.extract(deserialized)
    assert deserialized.parsed_evidence == before


@pytest.mark.parametrize(
    "content",
    [
        (
            b'{"item_count":1,"record_kind":"inventory_header","schema_version":"1.0",'
            b'"totals":{}}\n{"record_kind":"inventory_item"}\n'
        ),
        (
            b'{"item_count":"one","record_kind":"inventory_header","schema_version":"1.0",'
            b'"source_root_id":"root-1","totals":{}}\n{"record_kind":"inventory_item"}\n'
        ),
    ],
)
def test_invalid_fact_shapes_fail_explicitly(content: bytes) -> None:
    deserialized = deserialize(
        InventoryEvidenceAdapter(),
        PreservationEvidenceType.INVENTORY_EVIDENCE,
        content,
    )
    result = PreservationEvidenceFactExtractionService().extract(deserialized)
    assert result.status is EvidenceFactExtractionStatus.EXTRACTION_FAILED
    assert result.detail_code == "adapter_fact_extraction_failed"
