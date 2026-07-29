"""Immutable capture-session and preservation-baseline manifest contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from poe_backup_orchestrator.models.job import require_utc
from poe_backup_orchestrator.models.storage_inventory import (
    STORAGE_INVENTORY_SCHEMA_VERSION,
    PreservationBaselineIdentity,
    SourceDevice,
    SourceRoot,
    SourceVolume,
)

STORAGE_BASELINE_MANIFEST_SCHEMA_VERSION: Final[str] = "1.0"
_SHA256_HEX_LENGTH: Final[int] = 64


class CaptureSessionStatus(StrEnum):
    """Lifecycle state of one inventory capture session."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_EXCEPTIONS = "completed_with_exceptions"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BaselineManifestStatus(StrEnum):
    """Publication state of one preservation baseline manifest."""

    DRAFT = "draft"
    CERTIFIED = "certified"
    SUPERSEDED = "superseded"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class CaptureScope:
    """Declared source scope for one capture session."""

    source_device_ids: tuple[str, ...]
    source_volume_ids: tuple[str, ...]
    source_root_ids: tuple[str, ...]
    include_patterns: tuple[str, ...] = ()
    exclude_patterns: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "source_device_ids",
            _normalize_unique_identifiers(self.source_device_ids, "source_device_ids"),
        )
        object.__setattr__(
            self,
            "source_volume_ids",
            _normalize_unique_identifiers(self.source_volume_ids, "source_volume_ids"),
        )
        object.__setattr__(
            self,
            "source_root_ids",
            _normalize_unique_identifiers(self.source_root_ids, "source_root_ids"),
        )
        object.__setattr__(
            self,
            "include_patterns",
            _normalize_unique_text(self.include_patterns, "include_patterns"),
        )
        object.__setattr__(
            self,
            "exclude_patterns",
            _normalize_unique_text(self.exclude_patterns, "exclude_patterns"),
        )

        if not self.source_device_ids:
            raise ValueError("source_device_ids must not be empty")
        if not self.source_volume_ids:
            raise ValueError("source_volume_ids must not be empty")
        if not self.source_root_ids:
            raise ValueError("source_root_ids must not be empty")


@dataclass(frozen=True, slots=True)
class InventoryTotals:
    """Deterministic aggregate totals for one capture session."""

    directory_count: int
    file_count: int
    symbolic_link_count: int
    junction_count: int
    other_item_count: int
    total_file_bytes: int
    captured_count: int
    excluded_count: int
    inaccessible_count: int
    error_count: int
    pending_count: int

    def __post_init__(self) -> None:
        values = asdict(self)
        if any(value < 0 for value in values.values()):
            raise ValueError("inventory totals must not contain negative values")

        item_count = (
            self.directory_count
            + self.file_count
            + self.symbolic_link_count
            + self.junction_count
            + self.other_item_count
        )
        status_count = (
            self.captured_count
            + self.excluded_count
            + self.inaccessible_count
            + self.error_count
            + self.pending_count
        )
        if item_count != status_count:
            raise ValueError("inventory item totals must equal capture-status totals")

    @property
    def item_count(self) -> int:
        """Return the total number of inventoried objects."""

        return (
            self.directory_count
            + self.file_count
            + self.symbolic_link_count
            + self.junction_count
            + self.other_item_count
        )

    @property
    def exception_count(self) -> int:
        """Return the number of excluded, inaccessible, or failed objects."""

        return self.excluded_count + self.inaccessible_count + self.error_count


@dataclass(frozen=True, slots=True)
class CaptureExceptionSummary:
    """Aggregated evidence for one capture exception category."""

    category: str
    count: int
    example_paths: tuple[Path, ...] = ()
    detail: str | None = None

    def __post_init__(self) -> None:
        category = _normalize_text(self.category, "category")
        detail = _normalize_optional_text(self.detail, "detail")
        if self.count <= 0:
            raise ValueError("count must be greater than zero")

        normalized_paths: list[Path] = []
        seen: set[str] = set()
        for raw_path in self.example_paths:
            path = Path(raw_path)
            if path.is_absolute():
                raise ValueError("example_paths must be relative")
            if str(path) in {"", "."}:
                raise ValueError("example_paths must identify an item")
            key = path.as_posix()
            if key in seen:
                raise ValueError("example_paths must not contain duplicates")
            seen.add(key)
            normalized_paths.append(path)

        object.__setattr__(self, "category", category)
        object.__setattr__(self, "detail", detail)
        object.__setattr__(self, "example_paths", tuple(normalized_paths))


@dataclass(frozen=True, slots=True)
class CaptureSession:
    """Immutable execution-level record for one inventory capture."""

    capture_session_id: str
    baseline_id: str
    status: CaptureSessionStatus
    scope: CaptureScope
    started_at_utc: datetime | None
    completed_at_utc: datetime | None
    totals: InventoryTotals
    exceptions: tuple[CaptureExceptionSummary, ...] = ()
    failure_detail: str | None = None

    def __post_init__(self) -> None:
        capture_session_id = _normalize_identifier(
            self.capture_session_id,
            "capture_session_id",
        )
        baseline_id = _normalize_identifier(self.baseline_id, "baseline_id")
        failure_detail = _normalize_optional_text(
            self.failure_detail,
            "failure_detail",
        )

        if self.started_at_utc is not None:
            require_utc(self.started_at_utc, field_name="started_at_utc")
        if self.completed_at_utc is not None:
            require_utc(self.completed_at_utc, field_name="completed_at_utc")
        if (
            self.started_at_utc is not None
            and self.completed_at_utc is not None
            and self.completed_at_utc < self.started_at_utc
        ):
            raise ValueError("completed_at_utc must not precede started_at_utc")

        terminal_statuses = {
            CaptureSessionStatus.COMPLETED,
            CaptureSessionStatus.COMPLETED_WITH_EXCEPTIONS,
            CaptureSessionStatus.FAILED,
            CaptureSessionStatus.CANCELLED,
        }
        if self.status in terminal_statuses and self.completed_at_utc is None:
            raise ValueError("terminal capture sessions require completed_at_utc")
        if self.status is CaptureSessionStatus.RUNNING and self.started_at_utc is None:
            raise ValueError("running capture sessions require started_at_utc")
        if self.status is CaptureSessionStatus.PLANNED and (
            self.started_at_utc is not None or self.completed_at_utc is not None
        ):
            raise ValueError("planned capture sessions cannot contain execution timestamps")
        if self.status is CaptureSessionStatus.COMPLETED and (
            self.totals.exception_count != 0 or self.totals.pending_count != 0
        ):
            raise ValueError(
                "completed capture sessions cannot contain exceptions or pending items"
            )
        if self.status is CaptureSessionStatus.COMPLETED_WITH_EXCEPTIONS and (
            self.totals.exception_count == 0
        ):
            raise ValueError("completed_with_exceptions requires at least one capture exception")
        if self.status is CaptureSessionStatus.FAILED and failure_detail is None:
            raise ValueError("failed capture sessions require failure_detail")
        if self.status is not CaptureSessionStatus.FAILED and failure_detail is not None:
            raise ValueError("failure_detail is only valid for failed capture sessions")
        if sum(exception.count for exception in self.exceptions) > self.totals.exception_count:
            raise ValueError("exception summary counts cannot exceed aggregate exception totals")

        object.__setattr__(self, "capture_session_id", capture_session_id)
        object.__setattr__(self, "baseline_id", baseline_id)
        object.__setattr__(self, "failure_detail", failure_detail)
        object.__setattr__(self, "exceptions", tuple(self.exceptions))


@dataclass(frozen=True, slots=True)
class PreservationBaselineManifest:
    """Deterministic manifest for one preservation baseline."""

    schema_version: str
    inventory_schema_version: str
    manifest_status: BaselineManifestStatus
    baseline: PreservationBaselineIdentity
    generated_at_utc: datetime
    devices: tuple[SourceDevice, ...]
    volumes: tuple[SourceVolume, ...]
    roots: tuple[SourceRoot, ...]
    capture_sessions: tuple[CaptureSession, ...]
    inventory_evidence_path: Path
    manifest_sha256: str | None = None

    def __post_init__(self) -> None:
        schema_version = _normalize_text(self.schema_version, "schema_version")
        inventory_schema_version = _normalize_text(
            self.inventory_schema_version,
            "inventory_schema_version",
        )
        if schema_version != STORAGE_BASELINE_MANIFEST_SCHEMA_VERSION:
            raise ValueError("schema_version must match the supported baseline manifest schema")
        if inventory_schema_version != STORAGE_INVENTORY_SCHEMA_VERSION:
            raise ValueError("inventory_schema_version must match the supported inventory schema")
        require_utc(self.generated_at_utc, field_name="generated_at_utc")

        devices = _tuple_with_unique_attr(self.devices, "source_device_id", "devices")
        volumes = _tuple_with_unique_attr(self.volumes, "source_volume_id", "volumes")
        roots = _tuple_with_unique_attr(self.roots, "source_root_id", "roots")
        sessions = _tuple_with_unique_attr(
            self.capture_sessions,
            "capture_session_id",
            "capture_sessions",
        )

        if not devices:
            raise ValueError("devices must not be empty")
        if not volumes:
            raise ValueError("volumes must not be empty")
        if not roots:
            raise ValueError("roots must not be empty")
        if not sessions:
            raise ValueError("capture_sessions must not be empty")

        device_ids = {device.source_device_id for device in devices}
        volume_ids = {volume.source_volume_id for volume in volumes}
        root_ids = {root.source_root_id for root in roots}

        for volume in volumes:
            if volume.source_device_id not in device_ids:
                raise ValueError("every volume must reference a manifest device")
        for root in roots:
            if root.source_volume_id not in volume_ids:
                raise ValueError("every root must reference a manifest volume")
        for session in sessions:
            if session.baseline_id != self.baseline.baseline_id:
                raise ValueError("every capture session must reference the manifest baseline")
            if not set(session.scope.source_device_ids).issubset(device_ids):
                raise ValueError("capture scope references an unknown device")
            if not set(session.scope.source_volume_ids).issubset(volume_ids):
                raise ValueError("capture scope references an unknown volume")
            if not set(session.scope.source_root_ids).issubset(root_ids):
                raise ValueError("capture scope references an unknown root")

        evidence_path = Path(self.inventory_evidence_path)
        if not evidence_path.is_absolute():
            raise ValueError("inventory_evidence_path must be absolute")

        manifest_sha256 = _normalize_optional_sha256(self.manifest_sha256)
        if self.manifest_status is BaselineManifestStatus.CERTIFIED:
            if manifest_sha256 is None:
                raise ValueError("certified manifests require manifest_sha256")
            if any(
                session.status
                not in {
                    CaptureSessionStatus.COMPLETED,
                    CaptureSessionStatus.COMPLETED_WITH_EXCEPTIONS,
                }
                for session in sessions
            ):
                raise ValueError("certified manifests require terminal successful capture sessions")
            expected_sha256 = self.certification_sha256()
            if manifest_sha256 != expected_sha256:
                raise ValueError("manifest_sha256 does not match canonical manifest content")
        elif manifest_sha256 is not None:
            raise ValueError("only certified manifests may contain manifest_sha256")

        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "inventory_schema_version", inventory_schema_version)
        object.__setattr__(self, "devices", devices)
        object.__setattr__(self, "volumes", volumes)
        object.__setattr__(self, "roots", roots)
        object.__setattr__(self, "capture_sessions", sessions)
        object.__setattr__(self, "inventory_evidence_path", evidence_path)
        object.__setattr__(self, "manifest_sha256", manifest_sha256)

    def canonical_payload(
        self,
        *,
        manifest_status: BaselineManifestStatus | None = None,
    ) -> dict[str, Any]:
        """Return canonical manifest content excluding its integrity digest."""

        effective_status = manifest_status or self.manifest_status
        return {
            "schema_version": self.schema_version,
            "inventory_schema_version": self.inventory_schema_version,
            "manifest_status": effective_status.value,
            "baseline": _to_primitive(self.baseline),
            "generated_at_utc": self.generated_at_utc.isoformat(),
            "devices": [_to_primitive(device) for device in self.devices],
            "volumes": [_to_primitive(volume) for volume in self.volumes],
            "roots": [_to_primitive(root) for root in self.roots],
            "capture_sessions": [_to_primitive(session) for session in self.capture_sessions],
            "inventory_evidence_path": str(self.inventory_evidence_path),
        }

    def canonical_json(
        self,
        *,
        manifest_status: BaselineManifestStatus | None = None,
    ) -> str:
        """Return deterministic UTF-8 JSON suitable for integrity hashing."""

        return json.dumps(
            self.canonical_payload(manifest_status=manifest_status),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    def calculate_sha256(
        self,
        *,
        manifest_status: BaselineManifestStatus | None = None,
    ) -> str:
        """Calculate a SHA-256 digest of canonical manifest content."""

        canonical_json = self.canonical_json(manifest_status=manifest_status)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def certification_sha256(self) -> str:
        """Calculate the digest for the manifest's certified representation."""

        return self.calculate_sha256(
            manifest_status=BaselineManifestStatus.CERTIFIED,
        )


def _to_primitive(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {
            field_name: _to_primitive(getattr(value, field_name))
            for field_name in value.__dataclass_fields__
        }
    return value


def _tuple_with_unique_attr(
    values: tuple[Any, ...],
    attribute_name: str,
    field_name: str,
) -> tuple[Any, ...]:
    normalized = tuple(values)
    identities = [getattr(value, attribute_name) for value in normalized]
    if len(identities) != len(set(identities)):
        raise ValueError(f"{field_name} must not contain duplicate identities")
    return normalized


def _normalize_unique_identifiers(
    values: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    normalized = tuple(_normalize_identifier(value, field_name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field_name} must not contain duplicates")
    return normalized


def _normalize_unique_text(
    values: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    normalized = tuple(_normalize_text(value, field_name) for value in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{field_name} must not contain duplicates")
    return normalized


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
        raise ValueError("manifest_sha256 must contain exactly 64 hexadecimal characters")
    return normalized
