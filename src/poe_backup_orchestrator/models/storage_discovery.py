"""Read-only filesystem discovery contracts for storage consolidation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.job import require_utc

STORAGE_DISCOVERY_SCHEMA_VERSION: Final[str] = "1.0"


class DiscoveryEntryType(StrEnum):
    """Filesystem object type observed during read-only discovery."""

    DIRECTORY = "directory"
    FILE = "file"
    SYMBOLIC_LINK = "symbolic_link"
    OTHER = "other"


class DiscoveryStatus(StrEnum):
    """Overall outcome of one discovery request."""

    COMPLETED = "completed"
    COMPLETED_WITH_EXCEPTIONS = "completed_with_exceptions"
    FAILED = "failed"


class DiscoveryExceptionCode(StrEnum):
    """Stable classification for discovery exceptions."""

    ROOT_NOT_FOUND = "root_not_found"
    ROOT_NOT_DIRECTORY = "root_not_directory"
    PERMISSION_DENIED = "permission_denied"
    FILESYSTEM_ERROR = "filesystem_error"
    MAX_DEPTH_REACHED = "max_depth_reached"
    ENTRY_DISAPPEARED = "entry_disappeared"


@dataclass(frozen=True, slots=True)
class DiscoveryPolicy:
    """Read-only traversal policy for one source root."""

    include_hidden: bool = True
    follow_symbolic_links: bool = False
    max_depth: int | None = None

    def __post_init__(self) -> None:
        if self.max_depth is not None and self.max_depth < 0:
            raise ValueError("max_depth must be zero or greater")


@dataclass(frozen=True, slots=True)
class FilesystemDiscoveryRequest:
    """Request to inspect one declared source root without mutation."""

    discovery_request_id: str
    source_root_id: str
    root_path: Path
    requested_at_utc: datetime
    policy: DiscoveryPolicy = DiscoveryPolicy()

    def __post_init__(self) -> None:
        request_id = _normalize_identifier(
            self.discovery_request_id,
            "discovery_request_id",
        )
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        root_path = Path(self.root_path)
        if not root_path.is_absolute():
            raise ValueError("root_path must be absolute")
        require_utc(self.requested_at_utc, field_name="requested_at_utc")

        object.__setattr__(self, "discovery_request_id", request_id)
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "root_path", root_path)


@dataclass(frozen=True, slots=True)
class DiscoveredFilesystemEntry:
    """Normalized observation of one filesystem object."""

    source_root_id: str
    relative_path: Path
    entry_type: DiscoveryEntryType
    size_bytes: int | None
    modified_at_utc: datetime | None
    mode: int
    is_hidden: bool

    def __post_init__(self) -> None:
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        relative_path = Path(self.relative_path)
        if relative_path.is_absolute():
            raise ValueError("relative_path must be relative")
        if str(relative_path) in {"", "."}:
            raise ValueError("relative_path must identify an entry")
        if self.size_bytes is not None and self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        if self.modified_at_utc is not None:
            require_utc(self.modified_at_utc, field_name="modified_at_utc")
        if self.mode < 0:
            raise ValueError("mode must not be negative")

        if self.entry_type is DiscoveryEntryType.FILE and self.size_bytes is None:
            raise ValueError("file entries require size_bytes")
        if self.entry_type is not DiscoveryEntryType.FILE and self.size_bytes is not None:
            raise ValueError("only file entries may contain size_bytes")

        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "relative_path", relative_path)


@dataclass(frozen=True, slots=True)
class DiscoveryException:
    """Evidence describing one path that could not be fully discovered."""

    code: DiscoveryExceptionCode
    relative_path: Path | None
    detail: str

    def __post_init__(self) -> None:
        detail = self.detail.strip()
        if not detail:
            raise ValueError("detail must not be empty")
        if self.relative_path is not None:
            relative_path = Path(self.relative_path)
            if relative_path.is_absolute():
                raise ValueError("relative_path must be relative")
            object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class FilesystemDiscoveryResult:
    """Deterministically ordered result of one read-only discovery request."""

    schema_version: str
    discovery_request_id: str
    source_root_id: str
    root_path: Path
    started_at_utc: datetime
    completed_at_utc: datetime
    status: DiscoveryStatus
    entries: tuple[DiscoveredFilesystemEntry, ...]
    exceptions: tuple[DiscoveryException, ...]

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_DISCOVERY_SCHEMA_VERSION:
            raise ValueError("schema_version must match the supported discovery schema")

        discovery_request_id = _normalize_identifier(
            self.discovery_request_id,
            "discovery_request_id",
        )
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        root_path = Path(self.root_path)
        if not root_path.is_absolute():
            raise ValueError("root_path must be absolute")

        require_utc(self.started_at_utc, field_name="started_at_utc")
        require_utc(self.completed_at_utc, field_name="completed_at_utc")
        if self.completed_at_utc < self.started_at_utc:
            raise ValueError("completed_at_utc must not precede started_at_utc")

        entries = tuple(self.entries)
        exceptions = tuple(self.exceptions)

        entry_paths = [entry.relative_path.as_posix() for entry in entries]
        if entry_paths != sorted(entry_paths):
            raise ValueError("entries must be ordered by normalized relative path")
        if len(entry_paths) != len(set(entry_paths)):
            raise ValueError("entries must not contain duplicate relative paths")
        if any(entry.source_root_id != source_root_id for entry in entries):
            raise ValueError("every entry must reference the result source_root_id")

        if self.status is DiscoveryStatus.COMPLETED and exceptions:
            raise ValueError("completed results cannot contain exceptions")
        if self.status is DiscoveryStatus.COMPLETED_WITH_EXCEPTIONS and not exceptions:
            raise ValueError("completed_with_exceptions results require at least one exception")
        if self.status is DiscoveryStatus.FAILED and entries:
            raise ValueError("failed results cannot contain discovered entries")

        object.__setattr__(self, "discovery_request_id", discovery_request_id)
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "root_path", root_path)
        object.__setattr__(self, "entries", entries)
        object.__setattr__(self, "exceptions", exceptions)


def _normalize_identifier(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized
