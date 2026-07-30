# Tests for authenticated evidence deserialization and schema resolution.

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import ClassVar

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
    INVENTORY_EVIDENCE_SCHEMA_NAME,
    ContentIntegrityEvidenceAdapter,
    DeserializedPreservationEvidence,
    EvidenceDeserializationStatus,
    EvidenceLoadStatus,
    InventoryEvidenceAdapter,
    LoadedPreservationEvidence,
    PreservationEvidenceDeserializationService,
    ValidationAdapterRegistry,
)

INVENTORY_BYTES = (
    b'{"item_count":1,"record_kind":"inventory_header","schema_version":"1.0"}\n'
    b'{"item_type":"file","relative_path":"a.txt","support_status":"supported"}\n'
)
INTEGRITY_BYTES = b'{"evidence":[],"schema_version":"1.0","source_root_id":"root-1","totals":{}}\n'


def loaded(
    *,
    evidence_type: PreservationEvidenceType,
    content: bytes,
    schema_version: str = "1.0",
) -> LoadedPreservationEvidence:
    path = Path("/evidence/artifact")
    reference = PreservationEvidenceReference(
        evidence_type=evidence_type,
        source_root_id="root-1",
        schema_version=schema_version,
        evidence_path=path,
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


def service() -> PreservationEvidenceDeserializationService:
    return PreservationEvidenceDeserializationService(
        registry=ValidationAdapterRegistry(
            adapters=(InventoryEvidenceAdapter(), ContentIntegrityEvidenceAdapter())
        )
    )


def test_inventory_ndjson_is_deserialized_and_resolved() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=INVENTORY_BYTES,
        )
    )
    assert result.status is EvidenceDeserializationStatus.DESERIALIZED
    assert result.schema_name == INVENTORY_EVIDENCE_SCHEMA_NAME
    assert result.schema_version == "1.0"
    assert isinstance(result.adapter, InventoryEvidenceAdapter)
    assert isinstance(result.parsed_evidence, tuple)
    assert len(result.parsed_evidence) == 2


def test_content_integrity_json_is_deserialized_and_resolved() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            content=INTEGRITY_BYTES,
        )
    )
    assert result.status is EvidenceDeserializationStatus.DESERIALIZED
    assert result.schema_name == CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME
    assert result.schema_version == "1.0"
    assert isinstance(result.adapter, ContentIntegrityEvidenceAdapter)
    assert isinstance(result.parsed_evidence, tuple)


def test_parsed_json_is_recursively_immutable() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            content=INTEGRITY_BYTES,
        )
    )
    assert result.parsed_evidence == (
        ("evidence", ()),
        ("schema_version", "1.0"),
        ("source_root_id", "root-1"),
        ("totals", ()),
    )


def test_unauthenticated_input_is_rejected() -> None:
    verified = loaded(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        content=INVENTORY_BYTES,
    )
    unverified = replace(
        verified,
        status=EvidenceLoadStatus.EVIDENCE_MISSING,
        evidence_bytes=None,
        calculated_sha256=None,
        calculated_byte_count=None,
        sidecar_sha256=None,
        detail_code="missing",
    )
    result = service().deserialize(unverified)
    assert result.status is EvidenceDeserializationStatus.AUTHENTICATION_REQUIRED
    assert result.parsed_evidence is None
    assert result.adapter is None


def test_invalid_utf8_is_explicit() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=b"\xff",
        )
    )
    assert result.status is EvidenceDeserializationStatus.INVALID_UTF8
    assert result.detail_code == "evidence_not_utf8"


@pytest.mark.parametrize(
    ("evidence_type", "content"),
    [
        (PreservationEvidenceType.INVENTORY_EVIDENCE, b"{bad}\n"),
        (PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE, b"{bad}\n"),
    ],
)
def test_malformed_json_is_explicit(
    evidence_type: PreservationEvidenceType,
    content: bytes,
) -> None:
    result = service().deserialize(loaded(evidence_type=evidence_type, content=content))
    assert result.status is EvidenceDeserializationStatus.MALFORMED_SERIALIZATION


def test_inventory_requires_object_records() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=b'["not","an","object"]\n',
        )
    )
    assert result.status is EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE
    assert result.detail_code == "inventory_record_not_object"


def test_inventory_requires_header_first() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=b'{"record_kind":"inventory_item","schema_version":"1.0"}\n',
        )
    )
    assert result.status is EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE
    assert result.detail_code == "inventory_header_missing"


def test_content_integrity_requires_root_object() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            content=b"[]\n",
        )
    )
    assert result.status is EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE
    assert result.detail_code == "content_integrity_document_not_object"


@pytest.mark.parametrize(
    ("evidence_type", "content", "detail"),
    [
        (
            PreservationEvidenceType.INVENTORY_EVIDENCE,
            b'{"record_kind":"inventory_header"}\n',
            "inventory_schema_version_missing",
        ),
        (
            PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            b'{"evidence":[]}\n',
            "content_integrity_schema_version_missing",
        ),
    ],
)
def test_schema_version_is_required(
    evidence_type: PreservationEvidenceType,
    content: bytes,
    detail: str,
) -> None:
    result = service().deserialize(loaded(evidence_type=evidence_type, content=content))
    assert result.status is EvidenceDeserializationStatus.SCHEMA_IDENTITY_MISSING
    assert result.detail_code == detail


def test_payload_schema_must_match_reference_schema() -> None:
    result = service().deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=INVENTORY_BYTES,
            schema_version="2.0",
        )
    )
    assert result.status is EvidenceDeserializationStatus.SCHEMA_IDENTITY_MISMATCH
    assert result.schema_version == "1.0"
    assert result.adapter is None


def test_unknown_adapter_is_explicit() -> None:
    deserializer = PreservationEvidenceDeserializationService(
        registry=ValidationAdapterRegistry(adapters=(ContentIntegrityEvidenceAdapter(),))
    )
    result = deserializer.deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=INVENTORY_BYTES,
        )
    )
    assert result.status is EvidenceDeserializationStatus.ADAPTER_NOT_FOUND
    assert result.detail_code == "schema_adapter_not_found"


class FailingInventoryAdapter:
    evidence_type: ClassVar[PreservationEvidenceType] = PreservationEvidenceType.INVENTORY_EVIDENCE
    schema_name: ClassVar[str] = INVENTORY_EVIDENCE_SCHEMA_NAME
    supported_versions: ClassVar[tuple[str, ...]] = ("1.0",)

    def parse(self, evidence_bytes: bytes) -> object:
        raise ValueError("deliberate parse failure")

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        return parsed_evidence


def test_adapter_parse_failure_is_isolated() -> None:
    deserializer = PreservationEvidenceDeserializationService(
        registry=ValidationAdapterRegistry(adapters=(FailingInventoryAdapter(),))
    )
    result = deserializer.deserialize(
        loaded(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            content=INVENTORY_BYTES,
        )
    )
    assert result.status is EvidenceDeserializationStatus.ADAPTER_PARSE_FAILED
    assert result.parsed_evidence is None
    assert result.adapter is None


def test_deserialization_is_deterministic() -> None:
    input_evidence = loaded(
        evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        content=INTEGRITY_BYTES,
    )
    deserializer = service()
    assert deserializer.deserialize(input_evidence) == deserializer.deserialize(input_evidence)


def test_deserializer_does_not_mutate_authenticated_bytes() -> None:
    input_evidence = loaded(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        content=INVENTORY_BYTES,
    )
    before = input_evidence.evidence_bytes
    service().deserialize(input_evidence)
    assert input_evidence.evidence_bytes == before


def test_failed_result_cannot_expose_parsed_evidence() -> None:
    input_evidence = loaded(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        content=INVENTORY_BYTES,
    )
    with pytest.raises(ValueError, match="must not expose parsed evidence"):
        DeserializedPreservationEvidence(
            loaded_evidence=input_evidence,
            status=EvidenceDeserializationStatus.ADAPTER_NOT_FOUND,
            schema_name=INVENTORY_EVIDENCE_SCHEMA_NAME,
            schema_version="1.0",
            parsed_evidence=json.loads('{"bad":true}'),
            adapter=None,
            detail_code="schema_adapter_not_found",
        )
