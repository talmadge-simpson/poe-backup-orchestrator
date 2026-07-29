"""Tests for independent source-content integrity verification."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_manifest import InventoryTotals
from poe_backup_orchestrator.models.storage_content_capture import (
    STORAGE_CONTENT_CAPTURE_SCHEMA_VERSION,
    FileContentCertification,
    InventoryContentCaptureResult,
)
from poe_backup_orchestrator.models.storage_content_integrity import ContentIntegrityOutcome
from poe_backup_orchestrator.models.storage_inventory import (
    FileInventoryRecord,
    InventoryCaptureStatus,
    InventoryItemIdentity,
    InventoryItemType,
    InventoryMetadata,
)
from poe_backup_orchestrator.models.storage_inventory_assembly import (
    AssembledInventoryItem,
    stable_inventory_item_id,
)
from poe_backup_orchestrator.services.storage_content_integrity import (
    ContentIntegrityVerificationError,
    ContentIntegrityVerificationPolicy,
    ContentIntegrityVerifier,
)

T0 = datetime(2026, 7, 29, 16, 0, tzinfo=UTC)


class Clock:
    def __init__(self) -> None:
        self.value = T0

    def __call__(self) -> datetime:
        current = self.value
        self.value += timedelta(microseconds=1)
        return current


def identity(path: str) -> InventoryItemIdentity:
    return InventoryItemIdentity(
        baseline_id="baseline-1",
        capture_session_id="capture-1",
        source_device_id="device-1",
        source_volume_id="volume-1",
        source_root_id="root-1",
        relative_path=Path(path),
        item_type=InventoryItemType.FILE,
    )


def metadata() -> InventoryMetadata:
    return InventoryMetadata(
        created_at_utc=None,
        modified_at_utc=T0,
        accessed_at_utc=None,
        owner=None,
        permissions="0640",
    )


def certification(path: str, content: bytes) -> FileContentCertification:
    item_identity = identity(path)
    return FileContentCertification(
        item_id=stable_inventory_item_id(item_identity),
        relative_path=Path(path),
        expected_byte_count=len(content),
        observed_byte_count=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        started_at_utc=T0,
        completed_at_utc=T0,
    )


def captured_item(cert: FileContentCertification) -> AssembledInventoryItem:
    record = FileInventoryRecord(
        identity=identity(cert.relative_path.as_posix()),
        size_bytes=cert.expected_byte_count,
        sha256=cert.sha256,
        metadata=metadata(),
        capture_status=InventoryCaptureStatus.CAPTURED,
        captured_at_utc=T0,
    )
    return AssembledInventoryItem(item_id=cert.item_id, record=record)


def capture_result(
    root: Path,
    certifications: tuple[FileContentCertification, ...],
) -> InventoryContentCaptureResult:
    ordered = tuple(sorted(certifications, key=lambda item: item.relative_path.as_posix()))
    items = tuple(captured_item(item) for item in ordered)
    return InventoryContentCaptureResult(
        schema_version=STORAGE_CONTENT_CAPTURE_SCHEMA_VERSION,
        source_root_id="root-1",
        root_path=root,
        started_at_utc=T0,
        completed_at_utc=T0,
        items=items,
        unsupported_items=(),
        certifications=ordered,
        exceptions=(),
        totals=InventoryTotals(
            directory_count=0,
            file_count=len(items),
            symbolic_link_count=0,
            junction_count=0,
            other_item_count=0,
            total_file_bytes=sum(item.expected_byte_count for item in ordered),
            captured_count=len(items),
            excluded_count=0,
            inaccessible_count=0,
            error_count=0,
            pending_count=0,
        ),
    )


def verifier() -> ContentIntegrityVerifier:
    return ContentIntegrityVerifier(
        policy=ContentIntegrityVerificationPolicy(chunk_size_bytes=2),
        clock=Clock(),
    )


def test_verifies_empty_and_multichunk_files(tmp_path: Path) -> None:
    (tmp_path / "a.bin").write_bytes(b"")
    (tmp_path / "b.bin").write_bytes(b"abcdef")
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(
            tmp_path,
            (certification("a.bin", b""), certification("b.bin", b"abcdef")),
        ),
    )
    assert [item.outcome for item in result.evidence] == [
        ContentIntegrityOutcome.VERIFIED,
        ContentIntegrityOutcome.VERIFIED,
    ]
    assert result.totals.verified_count == 2
    assert result.totals.total_observed_bytes == 6


def test_detects_same_size_digest_mismatch(tmp_path: Path) -> None:
    (tmp_path / "a.bin").write_bytes(b"xyz")
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(tmp_path, (certification("a.bin", b"abc"),)),
    )
    assert result.evidence[0].outcome is ContentIntegrityOutcome.DIGEST_MISMATCH


def test_detects_size_mismatch(tmp_path: Path) -> None:
    (tmp_path / "a.bin").write_bytes(b"abcd")
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(tmp_path, (certification("a.bin", b"abc"),)),
    )
    assert result.evidence[0].outcome is ContentIntegrityOutcome.SIZE_MISMATCH


def test_missing_file_is_explicit_evidence(tmp_path: Path) -> None:
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(tmp_path, (certification("missing.bin", b"x"),)),
    )
    assert result.evidence[0].outcome is ContentIntegrityOutcome.MISSING
    assert result.evidence[0].detail


def test_directory_is_not_regular_file(tmp_path: Path) -> None:
    (tmp_path / "folder").mkdir()
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(tmp_path, (certification("folder", b"x"),)),
    )
    assert result.evidence[0].outcome is ContentIntegrityOutcome.NOT_REGULAR_FILE


def test_symlink_is_not_followed(tmp_path: Path) -> None:
    target = tmp_path / "target.bin"
    target.write_bytes(b"x")
    link = tmp_path / "link.bin"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symbolic links are not available")
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(tmp_path, (certification("link.bin", b"x"),)),
    )
    assert result.evidence[0].outcome is ContentIntegrityOutcome.NOT_REGULAR_FILE


def test_evidence_is_deterministically_sorted(tmp_path: Path) -> None:
    (tmp_path / "a.bin").write_bytes(b"a")
    (tmp_path / "z.bin").write_bytes(b"z")
    result = verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(
            tmp_path,
            (certification("z.bin", b"z"), certification("a.bin", b"a")),
        ),
    )
    assert [item.relative_path.as_posix() for item in result.evidence] == [
        "a.bin",
        "z.bin",
    ]


def test_root_must_match_capture_result(tmp_path: Path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    with pytest.raises(ContentIntegrityVerificationError, match="match"):
        verifier().verify(root_path=other, capture_result=capture_result(tmp_path, ()))


def test_verification_does_not_modify_source(tmp_path: Path) -> None:
    path = tmp_path / "a.bin"
    path.write_bytes(b"source")
    before_bytes = path.read_bytes()
    before_stat = path.stat()
    verifier().verify(
        root_path=tmp_path,
        capture_result=capture_result(tmp_path, (certification("a.bin", b"source"),)),
    )
    after_stat = path.stat()
    assert path.read_bytes() == before_bytes
    assert after_stat.st_size == before_stat.st_size
    assert after_stat.st_mtime_ns == before_stat.st_mtime_ns
