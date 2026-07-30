from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    EvidenceLoadStatus,
    FilesystemPreservationEvidenceLoader,
    LoadedPreservationEvidence,
)

PAYLOAD = b'{"schema_version":"1.0"}\n'


def reference_for(
    path: Path, *, digest_path: Path | None = None, payload: bytes = PAYLOAD
) -> PreservationEvidenceReference:
    return PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        source_root_id="root-1",
        schema_version="1.0",
        evidence_path=path,
        digest_path=digest_path or path.with_name(f"{path.name}.sha256"),
        sha256=hashlib.sha256(payload).hexdigest(),
        byte_count=len(payload),
    )


def publish(path: Path, *, style: str = "digest_only") -> PreservationEvidenceReference:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(PAYLOAD)
    reference = reference_for(path)
    content = (
        f"{reference.sha256}\n" if style == "digest_only" else f"{reference.sha256}  {path.name}\n"
    )
    reference.digest_path.write_text(content, encoding="ascii")
    return reference


def test_accepts_digest_only_sidecar(tmp_path: Path) -> None:
    reference = publish(tmp_path / "integrity.json")
    loaded = FilesystemPreservationEvidenceLoader().load(reference)
    assert loaded.status is EvidenceLoadStatus.VERIFIED
    assert loaded.evidence_bytes == PAYLOAD
    assert loaded.calculated_byte_count == len(PAYLOAD)
    assert loaded.calculated_sha256 == reference.sha256
    assert loaded.sidecar_sha256 == reference.sha256


def test_accepts_sha256sum_sidecar(tmp_path: Path) -> None:
    reference = publish(tmp_path / "inventory.ndjson", style="sha256sum")
    assert (
        FilesystemPreservationEvidenceLoader().load(reference).status is EvidenceLoadStatus.VERIFIED
    )


def test_exact_path_no_inference(tmp_path: Path) -> None:
    publish(tmp_path / "inventory.ndjson", style="sha256sum")
    reference = reference_for(tmp_path / "explicit.ndjson")
    assert (
        FilesystemPreservationEvidenceLoader().load(reference).status
        is EvidenceLoadStatus.EVIDENCE_MISSING
    )


def test_directory_evidence_rejected(tmp_path: Path) -> None:
    path = tmp_path / "evidence"
    path.mkdir()
    assert (
        FilesystemPreservationEvidenceLoader().load(reference_for(path)).status
        is EvidenceLoadStatus.EVIDENCE_NOT_REGULAR_FILE
    )


def test_byte_count_mismatch(tmp_path: Path) -> None:
    reference = replace(publish(tmp_path / "evidence.json"), byte_count=len(PAYLOAD) + 1)
    loaded = FilesystemPreservationEvidenceLoader(chunk_size_bytes=3).load(reference)
    assert loaded.status is EvidenceLoadStatus.EVIDENCE_SIZE_MISMATCH
    assert loaded.calculated_byte_count == len(PAYLOAD)
    assert loaded.evidence_bytes is None


def test_reference_digest_mismatch(tmp_path: Path) -> None:
    reference = replace(publish(tmp_path / "evidence.json"), sha256="0" * 64)
    loaded = FilesystemPreservationEvidenceLoader().load(reference)
    assert loaded.status is EvidenceLoadStatus.EVIDENCE_DIGEST_MISMATCH
    assert loaded.sidecar_sha256 is None


def test_missing_sidecar(tmp_path: Path) -> None:
    path = tmp_path / "evidence.json"
    path.write_bytes(PAYLOAD)
    loaded = FilesystemPreservationEvidenceLoader().load(reference_for(path))
    assert loaded.status is EvidenceLoadStatus.DIGEST_SIDECAR_MISSING


def test_directory_sidecar_rejected(tmp_path: Path) -> None:
    path = tmp_path / "evidence.json"
    path.write_bytes(PAYLOAD)
    digest = tmp_path / "digest"
    digest.mkdir()
    loaded = FilesystemPreservationEvidenceLoader().load(reference_for(path, digest_path=digest))
    assert loaded.status is EvidenceLoadStatus.DIGEST_SIDECAR_NOT_REGULAR_FILE


@pytest.mark.parametrize(
    "content", ["", "bad\n", f"{'a' * 63}\n", f"{'A' * 64}\n", f"{'a' * 64} file\n"]
)
def test_malformed_sidecar(tmp_path: Path, content: str) -> None:
    path = tmp_path / "evidence.json"
    path.write_bytes(PAYLOAD)
    reference = reference_for(path)
    reference.digest_path.write_text(content, encoding="ascii")
    assert (
        FilesystemPreservationEvidenceLoader().load(reference).status
        is EvidenceLoadStatus.DIGEST_SIDECAR_MALFORMED
    )


def test_sidecar_filename_mismatch(tmp_path: Path) -> None:
    reference = publish(tmp_path / "evidence.json", style="sha256sum")
    reference.digest_path.write_text(f"{reference.sha256}  other.json\n", encoding="ascii")
    loaded = FilesystemPreservationEvidenceLoader().load(reference)
    assert loaded.status is EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH
    assert loaded.detail_code == "digest_sidecar_filename_mismatch"


def test_sidecar_digest_mismatch(tmp_path: Path) -> None:
    reference = publish(tmp_path / "evidence.json")
    reference.digest_path.write_text(f"{'0' * 64}\n", encoding="ascii")
    loaded = FilesystemPreservationEvidenceLoader().load(reference)
    assert loaded.status is EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH
    assert loaded.sidecar_sha256 == "0" * 64


def test_loader_does_not_modify_files(tmp_path: Path) -> None:
    reference = publish(tmp_path / "inventory.ndjson", style="sha256sum")
    evidence_before = reference.evidence_path.read_bytes()
    sidecar_before = reference.digest_path.read_bytes()
    FilesystemPreservationEvidenceLoader(chunk_size_bytes=2).load(reference)
    assert reference.evidence_path.read_bytes() == evidence_before
    assert reference.digest_path.read_bytes() == sidecar_before


def test_results_are_deterministic(tmp_path: Path) -> None:
    reference = publish(tmp_path / "evidence.json")
    loader = FilesystemPreservationEvidenceLoader(chunk_size_bytes=4)
    assert loader.load(reference) == loader.load(reference)


def test_invalid_chunk_size() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        FilesystemPreservationEvidenceLoader(chunk_size_bytes=0)


def test_unverified_result_cannot_expose_bytes(tmp_path: Path) -> None:
    reference = reference_for(tmp_path / "missing.json")
    with pytest.raises(ValueError, match="must not expose evidence_bytes"):
        LoadedPreservationEvidence(
            reference, EvidenceLoadStatus.EVIDENCE_MISSING, b"bad", None, None, None, "missing"
        )
