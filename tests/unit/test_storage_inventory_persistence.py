"""Tests for deterministic storage inventory serialization and persistence."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_discovery import (
    STORAGE_DISCOVERY_SCHEMA_VERSION,
    DiscoveredFilesystemEntry,
    DiscoveryEntryType,
    DiscoveryStatus,
    FilesystemDiscoveryResult,
)
from poe_backup_orchestrator.services.storage_inventory_assembly import (
    DiscoveryInventoryAssembler,
    InventoryAssemblyContext,
)
from poe_backup_orchestrator.services.storage_inventory_persistence import (
    STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION,
    InventoryEvidenceConflictError,
    InventoryEvidencePersistenceError,
    InventoryEvidenceSerializer,
    InventoryEvidenceStore,
)

NOW = datetime(2026, 7, 29, 17, 0, tzinfo=UTC)
LATER = datetime(2026, 7, 29, 17, 1, tzinfo=UTC)


def assembled_result():
    discovery = FilesystemDiscoveryResult(
        schema_version=STORAGE_DISCOVERY_SCHEMA_VERSION,
        discovery_request_id="discovery-001",
        source_root_id="documents",
        root_path=Path("/source/documents"),
        started_at_utc=NOW,
        completed_at_utc=LATER,
        status=DiscoveryStatus.COMPLETED,
        entries=(
            DiscoveredFilesystemEntry(
                source_root_id="documents",
                relative_path=Path("a.txt"),
                entry_type=DiscoveryEntryType.FILE,
                size_bytes=10,
                modified_at_utc=NOW,
                mode=0o644,
                is_hidden=False,
            ),
            DiscoveredFilesystemEntry(
                source_root_id="documents",
                relative_path=Path("folder"),
                entry_type=DiscoveryEntryType.DIRECTORY,
                size_bytes=None,
                modified_at_utc=NOW,
                mode=0o755,
                is_hidden=False,
            ),
            DiscoveredFilesystemEntry(
                source_root_id="documents",
                relative_path=Path("link"),
                entry_type=DiscoveryEntryType.SYMBOLIC_LINK,
                size_bytes=None,
                modified_at_utc=NOW,
                mode=0o777,
                is_hidden=False,
            ),
        ),
        exceptions=(),
    )
    return DiscoveryInventoryAssembler().assemble(
        context=InventoryAssemblyContext(
            baseline_id="POE-STOR-MIG-BASELINE-20260729",
            capture_session_id="capture-001",
            source_device_id="windows-desktop",
            source_volume_id="windows-c",
            source_root_id="documents",
        ),
        discovery=discovery,
    )


def decoded_lines(content: bytes) -> list[dict[str, object]]:
    return [json.loads(line) for line in content.decode().splitlines()]


def test_serialization_is_deterministic() -> None:
    serializer = InventoryEvidenceSerializer()
    result = assembled_result()

    assert serializer.serialize(result) == serializer.serialize(result)
    assert serializer.calculate_sha256(result) == serializer.calculate_sha256(result)


def test_serialization_is_newline_terminated_ndjson() -> None:
    content = InventoryEvidenceSerializer().serialize(assembled_result())

    assert content.endswith(b"\n")
    assert len(content.decode().splitlines()) == 4


def test_header_contains_schema_identity_and_reconciled_totals() -> None:
    header = decoded_lines(InventoryEvidenceSerializer().serialize(assembled_result()))[0]

    assert header["record_kind"] == "inventory_header"
    assert header["schema_version"] == STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION
    assert header["discovery_request_id"] == "discovery-001"
    assert header["source_root_id"] == "documents"
    assert header["item_count"] == 3
    assert header["totals"]["pending_count"] == 3


def test_items_are_serialized_in_relative_path_order() -> None:
    records = decoded_lines(InventoryEvidenceSerializer().serialize(assembled_result()))[1:]

    assert [record["relative_path"] for record in records] == [
        "a.txt",
        "folder",
        "link",
    ]


def test_supported_file_record_preserves_identity_and_metadata() -> None:
    record = decoded_lines(InventoryEvidenceSerializer().serialize(assembled_result()))[1]

    assert record["support_status"] == "supported"
    assert record["item_type"] == "file"
    assert record["record"]["identity"]["baseline_id"] == "POE-STOR-MIG-BASELINE-20260729"
    assert record["record"]["identity"]["relative_path"] == "a.txt"
    assert record["record"]["metadata"]["modified_at_utc"] == NOW.isoformat()
    assert record["record"]["capture_status"] == "pending"


def test_unsupported_item_remains_explicit_evidence() -> None:
    record = decoded_lines(InventoryEvidenceSerializer().serialize(assembled_result()))[-1]

    assert record["support_status"] == "unsupported"
    assert record["item_type"] == "symbolic_link"
    assert record["relative_path"] == "link"
    assert "does not define a dedicated record contract" in record["detail"]


def test_digest_covers_exact_serialized_bytes() -> None:
    serializer = InventoryEvidenceSerializer()
    content = serializer.serialize(assembled_result())

    assert serializer.calculate_sha256(assembled_result()) == hashlib.sha256(content).hexdigest()


def test_publish_requires_absolute_evidence_path(tmp_path: Path) -> None:
    with pytest.raises(InventoryEvidencePersistenceError, match="absolute"):
        InventoryEvidenceStore().publish(
            result=assembled_result(),
            evidence_path=Path("relative/inventory.ndjson"),
        )


def test_publish_creates_evidence_and_digest_sidecar(tmp_path: Path) -> None:
    evidence = tmp_path / "baseline" / "inventory.ndjson"

    publication = InventoryEvidenceStore().publish(
        result=assembled_result(),
        evidence_path=evidence,
    )

    assert publication.evidence_path == evidence
    assert publication.sha256_path == evidence.with_name("inventory.ndjson.sha256")
    assert publication.idempotent_replay is False
    assert evidence.is_file()
    assert publication.sha256_path.is_file()
    assert hashlib.sha256(evidence.read_bytes()).hexdigest() == publication.sha256
    assert (
        publication.sha256_path.read_text(encoding="utf-8")
        == f"{publication.sha256}  inventory.ndjson\n"
    )


def test_published_files_use_restricted_mode(tmp_path: Path) -> None:
    evidence = tmp_path / "inventory.ndjson"

    publication = InventoryEvidenceStore().publish(
        result=assembled_result(),
        evidence_path=evidence,
    )

    assert evidence.stat().st_mode & 0o777 == 0o640
    assert publication.sha256_path.stat().st_mode & 0o777 == 0o640


def test_identical_republication_is_idempotent(tmp_path: Path) -> None:
    evidence = tmp_path / "inventory.ndjson"
    store = InventoryEvidenceStore()

    first = store.publish(result=assembled_result(), evidence_path=evidence)
    second = store.publish(result=assembled_result(), evidence_path=evidence)

    assert first.idempotent_replay is False
    assert second.idempotent_replay is True
    assert first.sha256 == second.sha256
    assert first.byte_count == second.byte_count


def test_conflicting_existing_evidence_is_rejected(tmp_path: Path) -> None:
    evidence = tmp_path / "inventory.ndjson"
    store = InventoryEvidenceStore()
    store.publish(result=assembled_result(), evidence_path=evidence)
    evidence.write_text("contradictory\n", encoding="utf-8")

    with pytest.raises(InventoryEvidenceConflictError, match="differs"):
        store.publish(result=assembled_result(), evidence_path=evidence)


def test_incomplete_existing_publication_is_rejected(tmp_path: Path) -> None:
    evidence = tmp_path / "inventory.ndjson"
    evidence.write_text("orphaned\n", encoding="utf-8")

    with pytest.raises(InventoryEvidenceConflictError, match="incomplete"):
        InventoryEvidenceStore().publish(
            result=assembled_result(),
            evidence_path=evidence,
        )


def test_publication_cleans_temporary_files(tmp_path: Path) -> None:
    evidence = tmp_path / "inventory.ndjson"

    InventoryEvidenceStore().publish(
        result=assembled_result(),
        evidence_path=evidence,
    )

    assert list(tmp_path.glob("*.tmp")) == []
    assert list(tmp_path.glob(".*.tmp")) == []


def test_serialization_and_persistence_do_not_touch_source_content(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_bytes(b"preserve exactly")
    before = source.stat()
    evidence = tmp_path / "evidence" / "inventory.ndjson"

    InventoryEvidenceStore().publish(
        result=assembled_result(),
        evidence_path=evidence,
    )

    after = source.stat()
    assert source.read_bytes() == b"preserve exactly"
    assert after.st_size == before.st_size
    assert after.st_mtime_ns == before.st_mtime_ns
