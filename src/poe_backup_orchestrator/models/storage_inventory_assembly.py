"""Immutable inventory-assembly contracts and deterministic item identity."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from poe_backup_orchestrator.models.storage_baseline_manifest import (
    CaptureExceptionSummary,
    InventoryTotals,
)
from poe_backup_orchestrator.models.storage_inventory import (
    DirectoryInventoryRecord,
    FileInventoryRecord,
    InventoryItemIdentity,
    InventoryItemType,
)

type InventoryRecord = FileInventoryRecord | DirectoryInventoryRecord


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
