"""Typed contract for governed Registry backup manifests used by restore discovery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.job import require_utc

SUPPORTED_RECOVERY_MANIFEST_VERSION: Final[str] = "1.0"
SUPPORTED_RECOVERY_ACQUISITION_TYPE: Final[str] = "windows_sqlite_snapshot"
_SHA256_HEX_LENGTH: Final[int] = 64


class RecoveryManifestFaultCode(StrEnum):
    """Stable fault classifications emitted while interpreting a manifest."""

    NOT_FOUND = "not_found"
    UNREADABLE = "unreadable"
    INVALID_JSON = "invalid_json"
    ROOT_NOT_OBJECT = "root_not_object"
    REQUIRED_FIELD_MISSING = "required_field_missing"
    FIELD_TYPE_INVALID = "field_type_invalid"
    FIELD_VALUE_INVALID = "field_value_invalid"
    VERSION_UNSUPPORTED = "version_unsupported"
    ACQUISITION_TYPE_UNSUPPORTED = "acquisition_type_unsupported"
    SNAPSHOT_FILENAME_UNSAFE = "snapshot_filename_unsafe"
    CHECKSUM_INVALID = "checksum_invalid"
    TIMESTAMP_INVALID = "timestamp_invalid"


@dataclass(frozen=True, slots=True)
class RecoveryManifestSnapshot:
    """Artifact metadata declared by one governed Registry backup manifest."""

    filename: str
    size_bytes: int
    sha256: str

    def __post_init__(self) -> None:
        filename = self.filename.strip()
        if not filename:
            raise ValueError("snapshot filename must not be empty")

        candidate = Path(filename)
        if candidate.name != filename or candidate.is_absolute():
            raise ValueError("snapshot filename must be a plain filename")

        if self.size_bytes < 0:
            raise ValueError("snapshot size_bytes must not be negative")

        sha256 = self.sha256.strip().lower()
        if len(sha256) != _SHA256_HEX_LENGTH or any(
            character not in "0123456789abcdef" for character in sha256
        ):
            raise ValueError("snapshot sha256 must contain exactly 64 hexadecimal characters")

        object.__setattr__(self, "filename", filename)
        object.__setattr__(self, "sha256", sha256)


@dataclass(frozen=True, slots=True)
class RecoveryManifestVerification:
    """Recorded acquisition verification declared by the source manifest."""

    sqlite_integrity_check: str
    status: str

    def __post_init__(self) -> None:
        integrity = self.sqlite_integrity_check.strip()
        status = self.status.strip()
        if not integrity:
            raise ValueError("sqlite_integrity_check must not be empty")
        if not status:
            raise ValueError("verification status must not be empty")
        object.__setattr__(self, "sqlite_integrity_check", integrity)
        object.__setattr__(self, "status", status)

    @property
    def passed(self) -> bool:
        """Return whether the source manifest records successful verification."""

        return self.sqlite_integrity_check.casefold() == "ok" and self.status.casefold() == "pass"


@dataclass(frozen=True, slots=True)
class RecoveryManifestPublication:
    """Publication guarantees declared by the source manifest."""

    manifest_published_last: bool


@dataclass(frozen=True, slots=True)
class RecoveryManifest:
    """Immutable typed interpretation of one governed Registry backup manifest."""

    schema_version: str
    acquisition_type: str
    asset_id: str
    asset_type: str | None
    created_at_utc: datetime
    source_path: Path | None
    snapshot: RecoveryManifestSnapshot
    verification: RecoveryManifestVerification
    publication: RecoveryManifestPublication

    def __post_init__(self) -> None:
        schema_version = self.schema_version.strip()
        acquisition_type = self.acquisition_type.strip()
        asset_id = self.asset_id.strip()
        asset_type = None if self.asset_type is None else self.asset_type.strip()

        if not schema_version:
            raise ValueError("schema_version must not be empty")
        if not acquisition_type:
            raise ValueError("acquisition_type must not be empty")
        if not asset_id:
            raise ValueError("asset_id must not be empty")
        if asset_type == "":
            raise ValueError("asset_type must not be empty when provided")

        require_utc(self.created_at_utc, field_name="created_at_utc")

        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "acquisition_type", acquisition_type)
        object.__setattr__(self, "asset_id", asset_id)
        object.__setattr__(self, "asset_type", asset_type)
        if self.source_path is not None:
            object.__setattr__(self, "source_path", Path(self.source_path))
