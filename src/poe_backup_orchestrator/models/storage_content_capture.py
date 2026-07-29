"""Immutable source-content capture and certification contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.job import require_utc
from poe_backup_orchestrator.models.storage_baseline_manifest import InventoryTotals
from poe_backup_orchestrator.models.storage_inventory_assembly import (
    AssembledInventoryItem,
    UnsupportedInventoryItem,
)

STORAGE_CONTENT_CAPTURE_SCHEMA_VERSION: Final[str] = "1.0"
_SHA256_HEX_LENGTH: Final[int] = 64


class ContentCaptureExceptionCode(StrEnum):
    """Stable classification for source-content capture exceptions."""

    FILE_NOT_FOUND = "file_not_found"
    PERMISSION_DENIED = "permission_denied"
    NOT_REGULAR_FILE = "not_regular_file"
    BYTE_COUNT_MISMATCH = "byte_count_mismatch"
    FILESYSTEM_ERROR = "filesystem_error"


@dataclass(frozen=True, slots=True)
class ContentCaptureException:
    """Explicit evidence describing one unsuccessful file capture."""

    code: ContentCaptureExceptionCode
    item_id: str
    relative_path: Path
    detail: str

    def __post_init__(self) -> None:
        item_id = _normalize_identifier(self.item_id, "item_id")
        relative_path = Path(self.relative_path)
        detail = self.detail.strip()
        if relative_path.is_absolute() or str(relative_path) in {"", "."}:
            raise ValueError("relative_path must identify an item below the source root")
        if not detail:
            raise ValueError("detail must not be empty")
        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class FileContentCertification:
    """Cryptographic and temporal evidence for one captured regular file."""

    item_id: str
    relative_path: Path
    expected_byte_count: int
    observed_byte_count: int
    sha256: str
    started_at_utc: datetime
    completed_at_utc: datetime

    def __post_init__(self) -> None:
        item_id = _normalize_identifier(self.item_id, "item_id")
        relative_path = Path(self.relative_path)
        sha256 = self.sha256.strip().lower()
        if relative_path.is_absolute() or str(relative_path) in {"", "."}:
            raise ValueError("relative_path must identify an item below the source root")
        if self.expected_byte_count < 0 or self.observed_byte_count < 0:
            raise ValueError("byte counts must not be negative")
        if self.expected_byte_count != self.observed_byte_count:
            raise ValueError("certification byte counts must match")
        if len(sha256) != _SHA256_HEX_LENGTH or any(
            character not in "0123456789abcdef" for character in sha256
        ):
            raise ValueError("sha256 must contain exactly 64 lowercase hexadecimal characters")
        require_utc(self.started_at_utc, field_name="started_at_utc")
        require_utc(self.completed_at_utc, field_name="completed_at_utc")
        if self.completed_at_utc < self.started_at_utc:
            raise ValueError("completed_at_utc must not precede started_at_utc")
        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "sha256", sha256)


@dataclass(frozen=True, slots=True)
class InventoryContentCaptureResult:
    """Immutable inventory update after deterministic source-content capture."""

    schema_version: str
    source_root_id: str
    root_path: Path
    started_at_utc: datetime
    completed_at_utc: datetime
    items: tuple[AssembledInventoryItem, ...]
    unsupported_items: tuple[UnsupportedInventoryItem, ...]
    certifications: tuple[FileContentCertification, ...]
    exceptions: tuple[ContentCaptureException, ...]
    totals: InventoryTotals

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_CONTENT_CAPTURE_SCHEMA_VERSION:
            raise ValueError("schema_version must match the supported capture schema")
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        root_path = Path(self.root_path)
        if not root_path.is_absolute():
            raise ValueError("root_path must be absolute")
        require_utc(self.started_at_utc, field_name="started_at_utc")
        require_utc(self.completed_at_utc, field_name="completed_at_utc")
        if self.completed_at_utc < self.started_at_utc:
            raise ValueError("completed_at_utc must not precede started_at_utc")

        items = tuple(self.items)
        unsupported_items = tuple(self.unsupported_items)
        certifications = tuple(self.certifications)
        exceptions = tuple(self.exceptions)
        item_paths = [item.record.identity.relative_path.as_posix() for item in items]
        unsupported_paths = [item.relative_path.as_posix() for item in unsupported_items]
        certification_paths = [item.relative_path.as_posix() for item in certifications]
        exception_paths = [item.relative_path.as_posix() for item in exceptions]
        if item_paths != sorted(item_paths):
            raise ValueError("inventory items must be ordered by relative path")
        if unsupported_paths != sorted(unsupported_paths):
            raise ValueError("unsupported items must be ordered by relative path")
        if certification_paths != sorted(certification_paths):
            raise ValueError("certifications must be ordered by relative path")
        if exception_paths != sorted(exception_paths):
            raise ValueError("exceptions must be ordered by relative path")

        supported_ids = {item.item_id for item in items}
        certification_ids = {item.item_id for item in certifications}
        exception_ids = {item.item_id for item in exceptions}
        if not certification_ids.issubset(supported_ids):
            raise ValueError("every certification must reference a supported inventory item")
        if not exception_ids.issubset(supported_ids):
            raise ValueError("every exception must reference a supported inventory item")
        if certification_ids & exception_ids:
            raise ValueError("an item cannot be both certified and exceptional")
        if any(item.record.identity.source_root_id != source_root_id for item in items):
            raise ValueError("every inventory item must reference source_root_id")

        expected_item_count = len(items) + len(unsupported_items)
        if self.totals.item_count != expected_item_count:
            raise ValueError("capture totals must reconcile item count")
        if self.totals.captured_count != len(certifications):
            raise ValueError("captured_count must reconcile certifications")
        if self.totals.exception_count != len(exceptions):
            raise ValueError("exception totals must reconcile capture exceptions")

        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "root_path", root_path)
        object.__setattr__(self, "items", items)
        object.__setattr__(self, "unsupported_items", unsupported_items)
        object.__setattr__(self, "certifications", certifications)
        object.__setattr__(self, "exceptions", exceptions)


def _normalize_identifier(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized
