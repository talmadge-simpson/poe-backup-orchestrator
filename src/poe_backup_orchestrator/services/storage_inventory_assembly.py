"""Deterministic transformation of discovery evidence into inventory records."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from poe_backup_orchestrator.models.storage_baseline_manifest import (
    CaptureExceptionSummary,
    InventoryTotals,
)
from poe_backup_orchestrator.models.storage_discovery import (
    DiscoveredFilesystemEntry,
    DiscoveryEntryType,
    DiscoveryException,
    DiscoveryStatus,
    FilesystemDiscoveryResult,
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
    InventoryAssemblyContext,
    InventoryAssemblyResult,
    InventoryRecord,
    UnsupportedInventoryItem,
    stable_inventory_item_id,
)


class InventoryAssemblyError(RuntimeError):
    """Raised when discovery evidence cannot be assembled deterministically."""


class DiscoveryInventoryAssembler:
    """Transform one completed discovery result into pending inventory evidence."""

    def assemble(
        self,
        *,
        context: InventoryAssemblyContext,
        discovery: FilesystemDiscoveryResult,
    ) -> InventoryAssemblyResult:
        """Assemble deterministic inventory records without source mutation."""

        if discovery.status is DiscoveryStatus.FAILED:
            raise InventoryAssemblyError(
                "failed discovery results cannot be assembled into inventory"
            )
        if discovery.source_root_id != context.source_root_id:
            raise InventoryAssemblyError("discovery source_root_id does not match assembly context")

        entry_paths = [entry.relative_path.as_posix() for entry in discovery.entries]
        if len(entry_paths) != len(set(entry_paths)):
            raise InventoryAssemblyError("discovery result contains duplicate relative paths")

        directory_metrics = _calculate_directory_metrics(discovery.entries)
        assembled: list[AssembledInventoryItem] = []
        unsupported: list[UnsupportedInventoryItem] = []

        for entry in discovery.entries:
            identity = _identity_for_entry(context=context, entry=entry)
            item_id = stable_inventory_item_id(identity)

            if entry.entry_type is DiscoveryEntryType.FILE:
                record: InventoryRecord = FileInventoryRecord(
                    identity=identity,
                    size_bytes=_require_file_size(entry),
                    sha256=None,
                    metadata=_metadata_for_entry(entry),
                    capture_status=InventoryCaptureStatus.PENDING,
                )
                assembled.append(
                    AssembledInventoryItem(
                        item_id=item_id,
                        record=record,
                    )
                )
                continue

            if entry.entry_type is DiscoveryEntryType.DIRECTORY:
                metrics = directory_metrics[entry.relative_path.as_posix()]
                record = DirectoryInventoryRecord(
                    identity=identity,
                    metadata=_metadata_for_entry(entry),
                    direct_file_count=metrics.direct_file_count,
                    direct_directory_count=metrics.direct_directory_count,
                    descendant_file_count=metrics.descendant_file_count,
                    descendant_directory_count=metrics.descendant_directory_count,
                    descendant_size_bytes=metrics.descendant_size_bytes,
                    capture_status=InventoryCaptureStatus.PENDING,
                )
                assembled.append(
                    AssembledInventoryItem(
                        item_id=item_id,
                        record=record,
                    )
                )
                continue

            unsupported.append(
                UnsupportedInventoryItem(
                    item_id=item_id,
                    relative_path=entry.relative_path,
                    item_type=identity.item_type,
                    detail=(
                        "The current inventory schema does not define a dedicated "
                        f"record contract for {identity.item_type.value} objects."
                    ),
                )
            )

        combined = sorted(
            [*assembled, *unsupported],
            key=_assembled_relative_path,
        )
        assembled = [item for item in combined if isinstance(item, AssembledInventoryItem)]
        unsupported = [item for item in combined if isinstance(item, UnsupportedInventoryItem)]

        totals = _build_totals(discovery.entries)
        exception_summaries = _summarize_discovery_exceptions(discovery.exceptions)

        result = InventoryAssemblyResult(
            discovery_request_id=discovery.discovery_request_id,
            source_root_id=discovery.source_root_id,
            items=tuple(assembled),
            unsupported_items=tuple(unsupported),
            totals=totals,
            exception_summaries=exception_summaries,
        )

        if result.totals.item_count != len(discovery.entries):
            raise InventoryAssemblyError(
                "assembled inventory count does not reconcile discovery entries"
            )
        return result


@dataclass(frozen=True, slots=True)
class _DirectoryMetrics:
    direct_file_count: int
    direct_directory_count: int
    descendant_file_count: int
    descendant_directory_count: int
    descendant_size_bytes: int


def _calculate_directory_metrics(
    entries: tuple[DiscoveredFilesystemEntry, ...],
) -> dict[str, _DirectoryMetrics]:
    directories = {
        entry.relative_path.as_posix(): entry
        for entry in entries
        if entry.entry_type is DiscoveryEntryType.DIRECTORY
    }
    result: dict[str, _DirectoryMetrics] = {}

    for directory_path in directories:
        directory = Path(directory_path)
        direct_files = 0
        direct_directories = 0
        descendant_files = 0
        descendant_directories = 0
        descendant_size_bytes = 0

        for candidate in entries:
            candidate_path = candidate.relative_path
            if candidate_path == directory:
                continue
            try:
                remainder = candidate_path.relative_to(directory)
            except ValueError:
                continue

            is_direct_child = len(remainder.parts) == 1
            if candidate.entry_type is DiscoveryEntryType.FILE:
                descendant_files += 1
                descendant_size_bytes += _require_file_size(candidate)
                if is_direct_child:
                    direct_files += 1
            elif candidate.entry_type is DiscoveryEntryType.DIRECTORY:
                descendant_directories += 1
                if is_direct_child:
                    direct_directories += 1

        result[directory_path] = _DirectoryMetrics(
            direct_file_count=direct_files,
            direct_directory_count=direct_directories,
            descendant_file_count=descendant_files,
            descendant_directory_count=descendant_directories,
            descendant_size_bytes=descendant_size_bytes,
        )

    return result


def _identity_for_entry(
    *,
    context: InventoryAssemblyContext,
    entry: DiscoveredFilesystemEntry,
) -> InventoryItemIdentity:
    return InventoryItemIdentity(
        baseline_id=context.baseline_id,
        capture_session_id=context.capture_session_id,
        source_device_id=context.source_device_id,
        source_volume_id=context.source_volume_id,
        source_root_id=context.source_root_id,
        relative_path=entry.relative_path,
        item_type=_inventory_item_type(entry.entry_type),
    )


def _inventory_item_type(entry_type: DiscoveryEntryType) -> InventoryItemType:
    mapping = {
        DiscoveryEntryType.FILE: InventoryItemType.FILE,
        DiscoveryEntryType.DIRECTORY: InventoryItemType.DIRECTORY,
        DiscoveryEntryType.SYMBOLIC_LINK: InventoryItemType.SYMBOLIC_LINK,
        DiscoveryEntryType.OTHER: InventoryItemType.OTHER,
    }
    return mapping[entry_type]


def _metadata_for_entry(entry: DiscoveredFilesystemEntry) -> InventoryMetadata:
    return InventoryMetadata(
        created_at_utc=None,
        modified_at_utc=entry.modified_at_utc,
        accessed_at_utc=None,
        owner=None,
        permissions=f"{entry.mode:04o}",
    )


def _require_file_size(entry: DiscoveredFilesystemEntry) -> int:
    if entry.size_bytes is None:
        raise InventoryAssemblyError(
            f"file discovery entry lacks size evidence: {entry.relative_path}"
        )
    return entry.size_bytes


def _build_totals(
    entries: tuple[DiscoveredFilesystemEntry, ...],
) -> InventoryTotals:
    directory_count = sum(entry.entry_type is DiscoveryEntryType.DIRECTORY for entry in entries)
    file_count = sum(entry.entry_type is DiscoveryEntryType.FILE for entry in entries)
    symbolic_link_count = sum(
        entry.entry_type is DiscoveryEntryType.SYMBOLIC_LINK for entry in entries
    )
    other_item_count = sum(entry.entry_type is DiscoveryEntryType.OTHER for entry in entries)
    total_file_bytes = sum(
        _require_file_size(entry)
        for entry in entries
        if entry.entry_type is DiscoveryEntryType.FILE
    )
    item_count = len(entries)

    return InventoryTotals(
        directory_count=directory_count,
        file_count=file_count,
        symbolic_link_count=symbolic_link_count,
        junction_count=0,
        other_item_count=other_item_count,
        total_file_bytes=total_file_bytes,
        captured_count=0,
        excluded_count=0,
        inaccessible_count=0,
        error_count=0,
        pending_count=item_count,
    )


def _summarize_discovery_exceptions(
    exceptions: tuple[DiscoveryException, ...],
) -> tuple[CaptureExceptionSummary, ...]:
    grouped: dict[str, list[DiscoveryException]] = {}
    for exception in exceptions:
        grouped.setdefault(exception.code.value, []).append(exception)

    summaries: list[CaptureExceptionSummary] = []
    for category in sorted(grouped):
        category_exceptions = grouped[category]
        example_paths = tuple(
            sorted(
                {
                    exception.relative_path
                    for exception in category_exceptions
                    if exception.relative_path is not None
                },
                key=lambda path: path.as_posix(),
            )
        )
        details = sorted({exception.detail for exception in category_exceptions})
        summaries.append(
            CaptureExceptionSummary(
                category=category,
                count=len(category_exceptions),
                example_paths=example_paths[:5],
                detail=" | ".join(details),
            )
        )
    return tuple(summaries)


def _assembled_relative_path(
    item: AssembledInventoryItem | UnsupportedInventoryItem,
) -> str:
    if isinstance(item, AssembledInventoryItem):
        return item.record.identity.relative_path.as_posix()
    return item.relative_path.as_posix()
