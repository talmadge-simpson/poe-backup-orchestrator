"""Tests for deterministic discovery-to-inventory assembly."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_discovery import (
    STORAGE_DISCOVERY_SCHEMA_VERSION,
    DiscoveredFilesystemEntry,
    DiscoveryEntryType,
    DiscoveryException,
    DiscoveryExceptionCode,
    DiscoveryStatus,
    FilesystemDiscoveryResult,
)
from poe_backup_orchestrator.models.storage_inventory import (
    DirectoryInventoryRecord,
    FileInventoryRecord,
    InventoryCaptureStatus,
    InventoryItemType,
)
from poe_backup_orchestrator.services.storage_inventory_assembly import (
    DiscoveryInventoryAssembler,
    InventoryAssemblyContext,
    InventoryAssemblyError,
    stable_inventory_item_id,
)

NOW = datetime(2026, 7, 29, 16, 0, tzinfo=UTC)
LATER = datetime(2026, 7, 29, 16, 1, tzinfo=UTC)


def context() -> InventoryAssemblyContext:
    return InventoryAssemblyContext(
        baseline_id="POE-STOR-MIG-BASELINE-20260729",
        capture_session_id="capture-001",
        source_device_id="windows-desktop",
        source_volume_id="windows-c",
        source_root_id="documents",
    )


def entry(
    relative_path: str,
    entry_type: DiscoveryEntryType,
    *,
    size_bytes: int | None = None,
    mode: int = 0o644,
) -> DiscoveredFilesystemEntry:
    return DiscoveredFilesystemEntry(
        source_root_id="documents",
        relative_path=Path(relative_path),
        entry_type=entry_type,
        size_bytes=size_bytes,
        modified_at_utc=NOW,
        mode=mode,
        is_hidden=False,
    )


def discovery(
    entries: tuple[DiscoveredFilesystemEntry, ...],
    *,
    status: DiscoveryStatus = DiscoveryStatus.COMPLETED,
    exceptions: tuple[DiscoveryException, ...] = (),
) -> FilesystemDiscoveryResult:
    return FilesystemDiscoveryResult(
        schema_version=STORAGE_DISCOVERY_SCHEMA_VERSION,
        discovery_request_id="discovery-001",
        source_root_id="documents",
        root_path=Path("/source/documents"),
        started_at_utc=NOW,
        completed_at_utc=LATER,
        status=status,
        entries=entries,
        exceptions=exceptions,
    )


def test_context_normalizes_identifiers() -> None:
    value = InventoryAssemblyContext(
        baseline_id=" baseline ",
        capture_session_id=" capture ",
        source_device_id=" device ",
        source_volume_id=" volume ",
        source_root_id=" root ",
    )

    assert value.baseline_id == "baseline"
    assert value.capture_session_id == "capture"


def test_failed_discovery_cannot_be_assembled() -> None:
    failed = discovery(
        (),
        status=DiscoveryStatus.FAILED,
        exceptions=(
            DiscoveryException(
                code=DiscoveryExceptionCode.ROOT_NOT_FOUND,
                relative_path=None,
                detail="missing",
            ),
        ),
    )

    with pytest.raises(InventoryAssemblyError, match="failed discovery"):
        DiscoveryInventoryAssembler().assemble(
            context=context(),
            discovery=failed,
        )


def test_source_root_must_match_context() -> None:
    result = replace(discovery(()), source_root_id="other-root")

    with pytest.raises(InventoryAssemblyError, match="source_root_id"):
        DiscoveryInventoryAssembler().assemble(
            context=context(),
            discovery=result,
        )


def test_file_entry_maps_to_pending_inventory_record() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery((entry("file.txt", DiscoveryEntryType.FILE, size_bytes=12),)),
    )

    record = result.records[0]
    assert isinstance(record, FileInventoryRecord)
    assert record.identity.relative_path == Path("file.txt")
    assert record.identity.item_type is InventoryItemType.FILE
    assert record.size_bytes == 12
    assert record.sha256 is None
    assert record.capture_status is InventoryCaptureStatus.PENDING
    assert record.metadata.permissions == "0644"


def test_directory_metrics_are_derived_from_descendants() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery(
            (
                entry("folder", DiscoveryEntryType.DIRECTORY, mode=0o755),
                entry(
                    "folder/direct.txt",
                    DiscoveryEntryType.FILE,
                    size_bytes=10,
                ),
                entry(
                    "folder/nested",
                    DiscoveryEntryType.DIRECTORY,
                    mode=0o755,
                ),
                entry(
                    "folder/nested/deep.txt",
                    DiscoveryEntryType.FILE,
                    size_bytes=20,
                ),
            )
        ),
    )

    folder = next(
        record for record in result.records if record.identity.relative_path == Path("folder")
    )
    assert isinstance(folder, DirectoryInventoryRecord)
    assert folder.direct_file_count == 1
    assert folder.direct_directory_count == 1
    assert folder.descendant_file_count == 2
    assert folder.descendant_directory_count == 1
    assert folder.descendant_size_bytes == 30
    assert folder.capture_status is InventoryCaptureStatus.PENDING


def test_nested_directory_has_own_reconciled_metrics() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery(
            (
                entry("folder", DiscoveryEntryType.DIRECTORY, mode=0o755),
                entry("folder/nested", DiscoveryEntryType.DIRECTORY, mode=0o755),
                entry(
                    "folder/nested/deep.txt",
                    DiscoveryEntryType.FILE,
                    size_bytes=20,
                ),
            )
        ),
    )

    nested = next(
        record
        for record in result.records
        if record.identity.relative_path == Path("folder/nested")
    )
    assert isinstance(nested, DirectoryInventoryRecord)
    assert nested.direct_file_count == 1
    assert nested.direct_directory_count == 0
    assert nested.descendant_file_count == 1
    assert nested.descendant_directory_count == 0
    assert nested.descendant_size_bytes == 20


def test_stable_item_identifier_is_repeatable() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery((entry("file.txt", DiscoveryEntryType.FILE, size_bytes=12),)),
    )

    item = result.items[0]
    assert item.item_id == stable_inventory_item_id(item.record.identity)
    assert item.item_id.startswith("inventory-")
    assert len(item.item_id) == len("inventory-") + 64


def test_stable_item_identifier_changes_with_path() -> None:
    assembler = DiscoveryInventoryAssembler()
    first = assembler.assemble(
        context=context(),
        discovery=discovery((entry("a.txt", DiscoveryEntryType.FILE, size_bytes=1),)),
    )
    second = assembler.assemble(
        context=context(),
        discovery=discovery((entry("b.txt", DiscoveryEntryType.FILE, size_bytes=1),)),
    )

    assert first.items[0].item_id != second.items[0].item_id


def test_symbolic_link_is_retained_as_unsupported_evidence() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery(
            (
                entry(
                    "link",
                    DiscoveryEntryType.SYMBOLIC_LINK,
                    mode=0o777,
                ),
            )
        ),
    )

    assert result.records == ()
    assert len(result.unsupported_items) == 1
    assert result.unsupported_items[0].relative_path == Path("link")
    assert result.unsupported_items[0].item_type is InventoryItemType.SYMBOLIC_LINK
    assert result.totals.symbolic_link_count == 1
    assert result.totals.pending_count == 1


def test_totals_reconcile_types_statuses_and_bytes() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery(
            (
                entry("a.txt", DiscoveryEntryType.FILE, size_bytes=10),
                entry("b.txt", DiscoveryEntryType.FILE, size_bytes=20),
                entry("folder", DiscoveryEntryType.DIRECTORY, mode=0o755),
                entry("link", DiscoveryEntryType.SYMBOLIC_LINK, mode=0o777),
                entry("socket", DiscoveryEntryType.OTHER, mode=0o600),
            )
        ),
    )

    assert result.totals.directory_count == 1
    assert result.totals.file_count == 2
    assert result.totals.symbolic_link_count == 1
    assert result.totals.other_item_count == 1
    assert result.totals.total_file_bytes == 30
    assert result.totals.item_count == 5
    assert result.totals.pending_count == 5


def test_discovery_exceptions_are_grouped_deterministically() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery(
            (entry("folder", DiscoveryEntryType.DIRECTORY, mode=0o755),),
            status=DiscoveryStatus.COMPLETED_WITH_EXCEPTIONS,
            exceptions=(
                DiscoveryException(
                    code=DiscoveryExceptionCode.PERMISSION_DENIED,
                    relative_path=Path("folder/private"),
                    detail="denied B",
                ),
                DiscoveryException(
                    code=DiscoveryExceptionCode.PERMISSION_DENIED,
                    relative_path=Path("folder/hidden"),
                    detail="denied A",
                ),
            ),
        ),
    )

    assert len(result.exception_summaries) == 1
    summary = result.exception_summaries[0]
    assert summary.category == "permission_denied"
    assert summary.count == 2
    assert summary.example_paths == (
        Path("folder/hidden"),
        Path("folder/private"),
    )
    assert summary.detail == "denied A | denied B"


def test_output_paths_are_deterministic() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery(
            (
                entry("a.txt", DiscoveryEntryType.FILE, size_bytes=1),
                entry("folder", DiscoveryEntryType.DIRECTORY, mode=0o755),
                entry("link", DiscoveryEntryType.SYMBOLIC_LINK, mode=0o777),
                entry("z.txt", DiscoveryEntryType.FILE, size_bytes=1),
            )
        ),
    )

    paths = [
        (
            item.record.identity.relative_path.as_posix()
            if hasattr(item, "record")
            else item.relative_path.as_posix()
        )
        for item in result.ordered_items
    ]
    assert paths == sorted(paths)


def test_inventory_identity_propagates_source_hierarchy() -> None:
    result = DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery((entry("file.txt", DiscoveryEntryType.FILE, size_bytes=1),)),
    )

    identity = result.records[0].identity
    assert identity.baseline_id == "POE-STOR-MIG-BASELINE-20260729"
    assert identity.capture_session_id == "capture-001"
    assert identity.source_device_id == "windows-desktop"
    assert identity.source_volume_id == "windows-c"
    assert identity.source_root_id == "documents"


def test_assembly_is_in_memory_and_does_not_touch_source(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_bytes(b"unchanged")
    before = source.stat()

    DiscoveryInventoryAssembler().assemble(
        context=context(),
        discovery=discovery((entry("source.txt", DiscoveryEntryType.FILE, size_bytes=9),)),
    )

    after = source.stat()
    assert source.read_bytes() == b"unchanged"
    assert after.st_size == before.st_size
    assert after.st_mtime_ns == before.st_mtime_ns
