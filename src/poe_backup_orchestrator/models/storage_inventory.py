"""Immutable source-identity and inventory contracts for storage consolidation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.job import require_utc

STORAGE_INVENTORY_SCHEMA_VERSION: Final[str] = "1.0"
_SHA256_HEX_LENGTH: Final[int] = 64


class SourceDeviceType(StrEnum):
    """Supported source-device categories."""

    WINDOWS_DESKTOP = "windows_desktop"
    WINDOWS_LAPTOP = "windows_laptop"
    MACBOOK = "macbook"
    RASPBERRY_PI = "raspberry_pi"
    NAS = "nas"
    EXTERNAL_DRIVE = "external_drive"
    CLOUD_SYNC = "cloud_sync"
    OTHER = "other"


class SourceAccessibility(StrEnum):
    """Observed accessibility state for a source object."""

    ACCESSIBLE = "accessible"
    INACCESSIBLE = "inaccessible"
    PARTIALLY_ACCESSIBLE = "partially_accessible"
    UNKNOWN = "unknown"


class InventoryItemType(StrEnum):
    """Inventory object type."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMBOLIC_LINK = "symbolic_link"
    JUNCTION = "junction"
    OTHER = "other"


class InventoryCaptureStatus(StrEnum):
    """Terminal or intermediate capture status for an inventory object."""

    CAPTURED = "captured"
    EXCLUDED = "excluded"
    INACCESSIBLE = "inaccessible"
    ERROR = "error"
    PENDING = "pending"


@dataclass(frozen=True, slots=True)
class SourceDevice:
    """Stable identity for one physical, virtual, or synchronized source device."""

    source_device_id: str
    device_type: SourceDeviceType
    hostname: str
    operating_system: str
    registered_at_utc: datetime
    accessibility: SourceAccessibility
    description: str | None = None

    def __post_init__(self) -> None:
        source_device_id = _normalize_identifier(self.source_device_id, "source_device_id")
        hostname = _normalize_text(self.hostname, "hostname")
        operating_system = _normalize_text(self.operating_system, "operating_system")
        description = _normalize_optional_text(self.description, "description")
        require_utc(self.registered_at_utc, field_name="registered_at_utc")

        object.__setattr__(self, "source_device_id", source_device_id)
        object.__setattr__(self, "hostname", hostname)
        object.__setattr__(self, "operating_system", operating_system)
        object.__setattr__(self, "description", description)


@dataclass(frozen=True, slots=True)
class SourceVolume:
    """Stable identity for one source volume attached to a registered device."""

    source_volume_id: str
    source_device_id: str
    volume_label: str | None
    volume_identifier: str | None
    filesystem: str
    mount_point: Path
    capacity_bytes: int | None
    accessibility: SourceAccessibility
    observed_at_utc: datetime

    def __post_init__(self) -> None:
        source_volume_id = _normalize_identifier(self.source_volume_id, "source_volume_id")
        source_device_id = _normalize_identifier(self.source_device_id, "source_device_id")
        volume_label = _normalize_optional_text(self.volume_label, "volume_label")
        volume_identifier = _normalize_optional_text(
            self.volume_identifier,
            "volume_identifier",
        )
        filesystem = _normalize_text(self.filesystem, "filesystem")
        if self.capacity_bytes is not None and self.capacity_bytes < 0:
            raise ValueError("capacity_bytes must not be negative")
        require_utc(self.observed_at_utc, field_name="observed_at_utc")

        object.__setattr__(self, "source_volume_id", source_volume_id)
        object.__setattr__(self, "source_device_id", source_device_id)
        object.__setattr__(self, "volume_label", volume_label)
        object.__setattr__(self, "volume_identifier", volume_identifier)
        object.__setattr__(self, "filesystem", filesystem)
        object.__setattr__(self, "mount_point", Path(self.mount_point))


@dataclass(frozen=True, slots=True)
class SourceRoot:
    """Declared inventory root within one registered source volume."""

    source_root_id: str
    source_volume_id: str
    root_path: Path
    declared_at_utc: datetime
    accessibility: SourceAccessibility
    description: str | None = None

    def __post_init__(self) -> None:
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        source_volume_id = _normalize_identifier(self.source_volume_id, "source_volume_id")
        description = _normalize_optional_text(self.description, "description")
        require_utc(self.declared_at_utc, field_name="declared_at_utc")

        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "source_volume_id", source_volume_id)
        object.__setattr__(self, "root_path", Path(self.root_path))
        object.__setattr__(self, "description", description)


@dataclass(frozen=True, slots=True)
class InventoryItemIdentity:
    """Common immutable identity shared by all inventory records."""

    baseline_id: str
    capture_session_id: str
    source_device_id: str
    source_volume_id: str
    source_root_id: str
    relative_path: Path
    item_type: InventoryItemType

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "baseline_id",
            _normalize_identifier(self.baseline_id, "baseline_id"),
        )
        object.__setattr__(
            self,
            "capture_session_id",
            _normalize_identifier(self.capture_session_id, "capture_session_id"),
        )
        object.__setattr__(
            self,
            "source_device_id",
            _normalize_identifier(self.source_device_id, "source_device_id"),
        )
        object.__setattr__(
            self,
            "source_volume_id",
            _normalize_identifier(self.source_volume_id, "source_volume_id"),
        )
        object.__setattr__(
            self,
            "source_root_id",
            _normalize_identifier(self.source_root_id, "source_root_id"),
        )

        relative_path = Path(self.relative_path)
        if relative_path.is_absolute():
            raise ValueError("relative_path must not be absolute")
        if str(relative_path) in {"", "."}:
            raise ValueError("relative_path must identify an item below the source root")
        object.__setattr__(self, "relative_path", relative_path)


@dataclass(frozen=True, slots=True)
class InventoryMetadata:
    """Portable metadata observations for one inventory object."""

    created_at_utc: datetime | None
    modified_at_utc: datetime | None
    accessed_at_utc: datetime | None
    owner: str | None
    permissions: str | None

    def __post_init__(self) -> None:
        for field_name in ("created_at_utc", "modified_at_utc", "accessed_at_utc"):
            value = getattr(self, field_name)
            if value is not None:
                require_utc(value, field_name=field_name)

        object.__setattr__(self, "owner", _normalize_optional_text(self.owner, "owner"))
        object.__setattr__(
            self,
            "permissions",
            _normalize_optional_text(self.permissions, "permissions"),
        )


@dataclass(frozen=True, slots=True)
class FileInventoryRecord:
    """Immutable inventory record for one regular file."""

    identity: InventoryItemIdentity
    size_bytes: int
    sha256: str | None
    metadata: InventoryMetadata
    capture_status: InventoryCaptureStatus
    exclusion_reason: str | None = None
    error_detail: str | None = None
    captured_at_utc: datetime | None = None

    def __post_init__(self) -> None:
        if self.identity.item_type is not InventoryItemType.FILE:
            raise ValueError("file inventory identity must use item_type FILE")
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")

        sha256 = _normalize_optional_sha256(self.sha256)
        exclusion_reason = _normalize_optional_text(
            self.exclusion_reason,
            "exclusion_reason",
        )
        error_detail = _normalize_optional_text(self.error_detail, "error_detail")
        if self.captured_at_utc is not None:
            require_utc(self.captured_at_utc, field_name="captured_at_utc")

        if self.capture_status is InventoryCaptureStatus.CAPTURED and sha256 is None:
            raise ValueError("captured file inventory records require sha256")
        if self.capture_status is InventoryCaptureStatus.EXCLUDED and exclusion_reason is None:
            raise ValueError("excluded file inventory records require exclusion_reason")
        if (
            self.capture_status
            in {
                InventoryCaptureStatus.ERROR,
                InventoryCaptureStatus.INACCESSIBLE,
            }
            and error_detail is None
        ):
            raise ValueError("error and inaccessible file records require error_detail")
        if self.capture_status is InventoryCaptureStatus.PENDING and (
            sha256 is not None
            or exclusion_reason is not None
            or error_detail is not None
            or self.captured_at_utc is not None
        ):
            raise ValueError("pending file records cannot contain terminal capture evidence")
        if (
            self.capture_status is not InventoryCaptureStatus.CAPTURED
            and self.captured_at_utc is not None
        ):
            raise ValueError("only captured file records may contain captured_at_utc")

        object.__setattr__(self, "sha256", sha256)
        object.__setattr__(self, "exclusion_reason", exclusion_reason)
        object.__setattr__(self, "error_detail", error_detail)


@dataclass(frozen=True, slots=True)
class DirectoryInventoryRecord:
    """Immutable inventory record for one directory."""

    identity: InventoryItemIdentity
    metadata: InventoryMetadata
    direct_file_count: int
    direct_directory_count: int
    descendant_file_count: int
    descendant_directory_count: int
    descendant_size_bytes: int
    capture_status: InventoryCaptureStatus
    exclusion_reason: str | None = None
    error_detail: str | None = None

    def __post_init__(self) -> None:
        if self.identity.item_type is not InventoryItemType.DIRECTORY:
            raise ValueError("directory inventory identity must use item_type DIRECTORY")

        counts = (
            self.direct_file_count,
            self.direct_directory_count,
            self.descendant_file_count,
            self.descendant_directory_count,
            self.descendant_size_bytes,
        )
        if any(value < 0 for value in counts):
            raise ValueError("directory counts and byte totals must not be negative")
        if self.direct_file_count > self.descendant_file_count:
            raise ValueError("direct_file_count cannot exceed descendant_file_count")
        if self.direct_directory_count > self.descendant_directory_count:
            raise ValueError("direct_directory_count cannot exceed descendant_directory_count")

        exclusion_reason = _normalize_optional_text(
            self.exclusion_reason,
            "exclusion_reason",
        )
        error_detail = _normalize_optional_text(self.error_detail, "error_detail")

        if self.capture_status is InventoryCaptureStatus.EXCLUDED and exclusion_reason is None:
            raise ValueError("excluded directory records require exclusion_reason")
        if (
            self.capture_status
            in {
                InventoryCaptureStatus.ERROR,
                InventoryCaptureStatus.INACCESSIBLE,
            }
            and error_detail is None
        ):
            raise ValueError("error and inaccessible directory records require error_detail")

        object.__setattr__(self, "exclusion_reason", exclusion_reason)
        object.__setattr__(self, "error_detail", error_detail)


@dataclass(frozen=True, slots=True)
class PreservationBaselineIdentity:
    """Immutable identity and lifecycle state for one preservation baseline."""

    schema_version: str
    baseline_id: str
    created_at_utc: datetime
    status: str
    retained_until: str

    def __post_init__(self) -> None:
        schema_version = _normalize_text(self.schema_version, "schema_version")
        if schema_version != STORAGE_INVENTORY_SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {STORAGE_INVENTORY_SCHEMA_VERSION}")
        baseline_id = _normalize_identifier(self.baseline_id, "baseline_id")
        status = _normalize_text(self.status, "status")
        retained_until = _normalize_text(self.retained_until, "retained_until")
        require_utc(self.created_at_utc, field_name="created_at_utc")

        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "baseline_id", baseline_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "retained_until", retained_until)


def _normalize_identifier(value: str, field_name: str) -> str:
    normalized = _normalize_text(value, field_name)
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


def _normalize_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return _normalize_text(value, field_name)


def _normalize_optional_sha256(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if len(normalized) != _SHA256_HEX_LENGTH or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError("sha256 must contain exactly 64 hexadecimal characters")
    return normalized
