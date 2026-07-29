"""Deterministic transformation of discovery evidence into inventory records."""

from __future__ import annotations

import hashlib
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

type InventoryRecord = FileInventoryRecord | DirectoryInventoryRecord


class InventoryAssemblyError(RuntimeError):
    """Raised when discovery evidence cannot be assembled deterministically."""


@dataclass(frozen=True, slots=True)
class InventoryAssemblyContext:
    """Source hierarchy and capture identity applied to every assembled item."""

    baseline_id: str
    capture_session_id: str
    source_device_id: str
    source_volume_id: str
    source_root_id: str

    def __post_init__(self) -> None:
        for field_name in (
            "baseline_id",
            "capture_session_id",
            "source_device_id",
            "source_volume_id",
            "source_root_id",
        ):
            normalized = _normalize_identifier(getattr(self, field_name), field_name)
            object.__setattr__(self, field_name, normalized)


@dataclass(frozen=True, slots=True)
class AssembledInventoryItem:
    """One inventory record paired with its stable deterministic item identifier."""

    item_id: str
    record: InventoryRecord

    def __post_init__(self) -> None:
        item_id = _normalize_identifier(self.item_id, "item_id")
        expected = stable_inventory_item_id(self.record.identity)
        if item_id != expected:
            raise ValueError("item_id must match the inventory identity")
        object.__setattr__(self, "item_id", item_id)


@dataclass(frozen=True, slots=True)
class UnsupportedInventoryItem:
    """Discovery object retained as evidence when no inventory record exists yet."""

    item_id: str
    relative_path: Path
    item_type: InventoryItemType
    detail: str

    def __post_init__(self) -> None:
        item_id = _normalize_identifier(self.item_id, "item_id")
        relative_path = Path(self.relative_path)
        detail = self.detail.strip()
        if relative_path.is_absolute() or str(relative_path) in {"", "."}:
            raise ValueError("relative_path must identify an item below the source root")
        if self.item_type not in {
            InventoryItemType.SYMBOLIC_LINK,
            InventoryItemType.OTHER,
        }:
            raise ValueError("unsupported items must be symbolic links or other objects")
        if not detail:
            raise ValueError("detail must not be empty")

        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class InventoryAssemblyResult:
    """Deterministic in-memory inventory assembly and reconciliation evidence."""

    discovery_request_id: str
    source_root_id: str
    items: tuple[AssembledInventoryItem, ...]
    unsupported_items: tuple[UnsupportedInventoryItem, ...]
    totals: InventoryTotals
    exception_summaries: tuple[CaptureExceptionSummary, ...]

    def __post_init__(self) -> None:
        discovery_request_id = _normalize_identifier(
            self.discovery_request_id,
            "discovery_request_id",
        )
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        items = tuple(self.items)
        unsupported_items = tuple(self.unsupported_items)
        exception_summaries = tuple(self.exception_summaries)

        item_paths = [item.record.identity.relative_path.as_posix() for item in items]
        unsupported_paths = [item.relative_path.as_posix() for item in unsupported_items]
        if item_paths != sorted(item_paths):
            raise ValueError("inventory records must be ordered by relative path")
        if unsupported_paths != sorted(unsupported_paths):
            raise ValueError("unsupported items must be ordered by relative path")

        all_paths = item_paths + unsupported_paths
        if len(all_paths) != len(set(all_paths)):
            raise ValueError("assembled items must not contain duplicate paths")

        item_ids = [item.item_id for item in items]
        item_ids.extend(item.item_id for item in unsupported_items)
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("assembled items must not contain duplicate item identifiers")

        if any(item.record.identity.source_root_id != source_root_id for item in items):
            raise ValueError("every inventory record must reference source_root_id")

        expected_total = len(items) + len(unsupported_items)
        if self.totals.item_count != expected_total:
            raise ValueError("inventory totals must reconcile assembled item count")
        if self.totals.pending_count != expected_total:
            raise ValueError("newly assembled inventory items must all be pending")

        object.__setattr__(self, "discovery_request_id", discovery_request_id)
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "items", items)
        object.__setattr__(self, "unsupported_items", unsupported_items)
        object.__setattr__(self, "exception_summaries", exception_summaries)

    @property
    def records(self) -> tuple[InventoryRecord, ...]:
        """Return assembled file and directory records in deterministic order."""

        return tuple(item.record for item in self.items)

    @property
    def ordered_items(
        self,
    ) -> tuple[AssembledInventoryItem | UnsupportedInventoryItem, ...]:
        """Return all assembled evidence in deterministic relative-path order."""

        return tuple(
            sorted(
                (*self.items, *self.unsupported_items),
                key=_assembled_relative_path,
            )
        )


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


def stable_inventory_item_id(identity: InventoryItemIdentity) -> str:
    """Return a deterministic identifier derived solely from governed identity."""

    canonical = "\0".join(
        (
            identity.baseline_id,
            identity.capture_session_id,
            identity.source_device_id,
            identity.source_volume_id,
            identity.source_root_id,
            identity.relative_path.as_posix(),
            identity.item_type.value,
        )
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"inventory-{digest}"


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


def _normalize_identifier(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized
