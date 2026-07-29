"""Tests for deterministic source-content capture and SHA-256 certification."""

from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_manifest import (
    CaptureExceptionSummary,
    InventoryTotals,
)
from poe_backup_orchestrator.models.storage_content_capture import (
    ContentCaptureExceptionCode,
    FileContentCertification,
)
from poe_backup_orchestrator.models.storage_inventory import (
    DirectoryInventoryRecord,
    FileInventoryRecord,
    InventoryCaptureStatus,
    InventoryItemIdentity,
    InventoryItemType,
    InventoryMetadata,
)
from poe_backup_orchestrator.models.storage_inventory_assembly import (
    AssembledInventoryItem,
    InventoryAssemblyResult,
    stable_inventory_item_id,
)
from poe_backup_orchestrator.services.storage_content_capture import (
    ContentCapturePolicy,
    InventoryContentCaptureError,
    InventoryContentCaptureService,
)

T0 = datetime(2026, 7, 29, 15, 0, tzinfo=UTC)


class SequenceClock:
    def __init__(self) -> None:
        self._index = 0

    def __call__(self) -> datetime:
        value = T0 + timedelta(seconds=self._index)
        self._index += 1
        return value


def identity(path: str, item_type: InventoryItemType) -> InventoryItemIdentity:
    return InventoryItemIdentity(
        baseline_id="baseline-1",
        capture_session_id="capture-1",
        source_device_id="device-1",
        source_volume_id="volume-1",
        source_root_id="root-1",
        relative_path=Path(path),
        item_type=item_type,
    )


def metadata() -> InventoryMetadata:
    return InventoryMetadata(
        created_at_utc=None,
        modified_at_utc=T0,
        accessed_at_utc=None,
        owner=None,
        permissions="0640",
    )


def file_item(path: str, size: int) -> AssembledInventoryItem:
    record = FileInventoryRecord(
        identity=identity(path, InventoryItemType.FILE),
        size_bytes=size,
        sha256=None,
        metadata=metadata(),
        capture_status=InventoryCaptureStatus.PENDING,
    )
    return AssembledInventoryItem(
        item_id=stable_inventory_item_id(record.identity),
        record=record,
    )


def directory_item(path: str) -> AssembledInventoryItem:
    record = DirectoryInventoryRecord(
        identity=identity(path, InventoryItemType.DIRECTORY),
        metadata=metadata(),
        direct_file_count=0,
        direct_directory_count=0,
        descendant_file_count=0,
        descendant_directory_count=0,
        descendant_size_bytes=0,
        capture_status=InventoryCaptureStatus.PENDING,
    )
    return AssembledInventoryItem(
        item_id=stable_inventory_item_id(record.identity),
        record=record,
    )


def assembled(*items: AssembledInventoryItem) -> InventoryAssemblyResult:
    ordered = tuple(sorted(items, key=lambda item: item.record.identity.relative_path.as_posix()))
    file_count = sum(item.record.identity.item_type is InventoryItemType.FILE for item in ordered)
    directory_count = len(ordered) - file_count
    total_bytes = sum(
        item.record.size_bytes for item in ordered if isinstance(item.record, FileInventoryRecord)
    )
    return InventoryAssemblyResult(
        discovery_request_id="discovery-1",
        source_root_id="root-1",
        items=ordered,
        unsupported_items=(),
        totals=InventoryTotals(
            directory_count=directory_count,
            file_count=file_count,
            symbolic_link_count=0,
            junction_count=0,
            other_item_count=0,
            total_file_bytes=total_bytes,
            captured_count=0,
            excluded_count=0,
            inaccessible_count=0,
            error_count=0,
            pending_count=len(ordered),
        ),
        exception_summaries=tuple[CaptureExceptionSummary, ...](),
    )


def service(chunk_size: int = 4) -> InventoryContentCaptureService:
    return InventoryContentCaptureService(
        policy=ContentCapturePolicy(chunk_size_bytes=chunk_size),
        clock=SequenceClock(),
    )


def test_policy_rejects_nonpositive_chunk_size() -> None:
    with pytest.raises(ValueError, match="positive"):
        ContentCapturePolicy(chunk_size_bytes=0)


def test_capture_requires_absolute_root() -> None:
    with pytest.raises(InventoryContentCaptureError, match="absolute"):
        service().capture(root_path=Path("relative"), inventory=assembled())


def test_empty_file_is_certified(tmp_path: Path) -> None:
    (tmp_path / "empty.bin").write_bytes(b"")
    result = service().capture(
        root_path=tmp_path,
        inventory=assembled(file_item("empty.bin", 0)),
    )
    record = result.items[0].record
    assert isinstance(record, FileInventoryRecord)
    assert record.capture_status is InventoryCaptureStatus.CAPTURED
    assert record.sha256 == hashlib.sha256(b"").hexdigest()
    assert record.captured_at_utc is not None
    assert result.certifications[0].observed_byte_count == 0


def test_multi_chunk_file_is_certified(tmp_path: Path) -> None:
    payload = b"abcdefghijk"
    (tmp_path / "payload.bin").write_bytes(payload)
    result = service(chunk_size=3).capture(
        root_path=tmp_path,
        inventory=assembled(file_item("payload.bin", len(payload))),
    )
    assert result.certifications[0].sha256 == hashlib.sha256(payload).hexdigest()
    assert result.certifications[0].observed_byte_count == len(payload)


def test_capture_order_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "b.txt").write_bytes(b"b")
    result = service().capture(
        root_path=tmp_path,
        inventory=assembled(file_item("b.txt", 1), file_item("a.txt", 1)),
    )
    assert [item.relative_path.as_posix() for item in result.certifications] == [
        "a.txt",
        "b.txt",
    ]


def test_directory_remains_pending_and_is_not_read(tmp_path: Path) -> None:
    (tmp_path / "folder").mkdir()
    item = directory_item("folder")
    result = service().capture(root_path=tmp_path, inventory=assembled(item))
    assert result.items[0] is item
    assert result.items[0].record.capture_status is InventoryCaptureStatus.PENDING
    assert result.certifications == ()
    assert result.totals.pending_count == 1


def test_successful_capture_is_immutable(tmp_path: Path) -> None:
    payload = b"immutable"
    (tmp_path / "source.bin").write_bytes(payload)
    original = file_item("source.bin", len(payload))
    result = service().capture(root_path=tmp_path, inventory=assembled(original))
    assert original.record.capture_status is InventoryCaptureStatus.PENDING
    assert original.record.sha256 is None
    assert result.items[0] is not original
    with pytest.raises(FrozenInstanceError):
        result.certifications[0].sha256 = "a" * 64  # type: ignore[misc]


def test_missing_file_becomes_inaccessible(tmp_path: Path) -> None:
    result = service().capture(
        root_path=tmp_path,
        inventory=assembled(file_item("missing.bin", 10)),
    )
    record = result.items[0].record
    assert record.capture_status is InventoryCaptureStatus.INACCESSIBLE
    assert record.sha256 is None
    assert record.error_detail
    assert result.exceptions[0].code is ContentCaptureExceptionCode.FILE_NOT_FOUND
    assert result.totals.inaccessible_count == 1


def test_byte_count_mismatch_becomes_error(tmp_path: Path) -> None:
    (tmp_path / "changed.bin").write_bytes(b"changed")
    result = service().capture(
        root_path=tmp_path,
        inventory=assembled(file_item("changed.bin", 2)),
    )
    record = result.items[0].record
    assert record.capture_status is InventoryCaptureStatus.ERROR
    assert record.sha256 is None
    assert result.exceptions[0].code is ContentCaptureExceptionCode.BYTE_COUNT_MISMATCH
    assert result.totals.error_count == 1


def test_symbolic_link_is_not_followed(tmp_path: Path) -> None:
    target = tmp_path / "target.bin"
    target.write_bytes(b"target")
    link = tmp_path / "link.bin"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symbolic links unavailable")
    result = service().capture(
        root_path=tmp_path,
        inventory=assembled(file_item("link.bin", len(b"target"))),
    )
    assert result.items[0].record.capture_status is InventoryCaptureStatus.ERROR
    assert result.exceptions[0].code is ContentCaptureExceptionCode.NOT_REGULAR_FILE


def test_source_bytes_remain_unchanged(tmp_path: Path) -> None:
    payload = b"preserve exactly"
    source = tmp_path / "source.bin"
    source.write_bytes(payload)
    service().capture(
        root_path=tmp_path,
        inventory=assembled(file_item("source.bin", len(payload))),
    )
    assert source.read_bytes() == payload


def test_capture_rejects_nonpending_file(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    source.write_bytes(b"x")
    pending = file_item("source.bin", 1)
    record = pending.record
    assert isinstance(record, FileInventoryRecord)
    captured_record = FileInventoryRecord(
        identity=record.identity,
        size_bytes=1,
        sha256=hashlib.sha256(b"x").hexdigest(),
        metadata=record.metadata,
        capture_status=InventoryCaptureStatus.CAPTURED,
        captured_at_utc=T0,
    )
    captured = AssembledInventoryItem(item_id=pending.item_id, record=captured_record)
    with pytest.raises(InventoryContentCaptureError, match="only pending"):
        service().capture(root_path=tmp_path, inventory=assembled(captured))


def test_totals_reconcile_mixed_outcomes(tmp_path: Path) -> None:
    (tmp_path / "good.bin").write_bytes(b"good")
    (tmp_path / "changed.bin").write_bytes(b"changed")
    inventory = assembled(
        directory_item("folder"),
        file_item("good.bin", 4),
        file_item("changed.bin", 1),
        file_item("missing.bin", 3),
    )
    result = service().capture(root_path=tmp_path, inventory=inventory)
    assert result.totals.item_count == 4
    assert result.totals.captured_count == 1
    assert result.totals.error_count == 1
    assert result.totals.inaccessible_count == 1
    assert result.totals.pending_count == 1
    assert result.totals.exception_count == 2


def test_certification_rejects_mismatched_byte_counts() -> None:
    with pytest.raises(ValueError, match="must match"):
        FileContentCertification(
            item_id="inventory-1",
            relative_path=Path("file.bin"),
            expected_byte_count=1,
            observed_byte_count=2,
            sha256="a" * 64,
            started_at_utc=T0,
            completed_at_utc=T0,
        )


def test_file_inventory_rejects_timestamp_on_pending_record() -> None:
    with pytest.raises(ValueError, match="pending"):
        FileInventoryRecord(
            identity=identity("file.bin", InventoryItemType.FILE),
            size_bytes=1,
            sha256=None,
            metadata=metadata(),
            capture_status=InventoryCaptureStatus.PENDING,
            captured_at_utc=T0,
        )


def test_file_inventory_rejects_timestamp_on_error_record() -> None:
    with pytest.raises(ValueError, match="only captured"):
        FileInventoryRecord(
            identity=identity("file.bin", InventoryItemType.FILE),
            size_bytes=1,
            sha256=None,
            metadata=metadata(),
            capture_status=InventoryCaptureStatus.ERROR,
            error_detail="failed",
            captured_at_utc=T0,
        )
