"""Read-only loading and validation of governed Registry backup manifests."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.models.recovery_manifest import (
    SUPPORTED_RECOVERY_ACQUISITION_TYPE,
    SUPPORTED_RECOVERY_MANIFEST_VERSION,
    RecoveryManifest,
    RecoveryManifestFaultCode,
    RecoveryManifestPublication,
    RecoveryManifestSnapshot,
    RecoveryManifestVerification,
)


class RecoveryManifestError(ValueError):
    """Manifest loading or contract fault with a stable classification."""

    def __init__(
        self,
        fault_code: RecoveryManifestFaultCode,
        message: str,
        *,
        field_path: str | None = None,
    ) -> None:
        super().__init__(message)
        self.fault_code = fault_code
        self.field_path = field_path


def read_recovery_manifest(manifest_path: Path) -> RecoveryManifest:
    """Load one governed backup manifest without validating artifact contents."""

    path = Path(manifest_path).expanduser().resolve()
    payload = _load_json_object(path)

    schema_version = _required_string(payload, "schema_version")
    if schema_version != SUPPORTED_RECOVERY_MANIFEST_VERSION:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.VERSION_UNSUPPORTED,
            f"unsupported recovery manifest schema version: {schema_version}",
            field_path="schema_version",
        )

    acquisition_type = _required_string(payload, "acquisition_type")
    if acquisition_type != SUPPORTED_RECOVERY_ACQUISITION_TYPE:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.ACQUISITION_TYPE_UNSUPPORTED,
            f"unsupported recovery acquisition type: {acquisition_type}",
            field_path="acquisition_type",
        )

    asset_id = _required_string(payload, "asset_id")
    asset_type = _optional_string(payload, "asset_type")
    created_at_utc = _required_utc_timestamp(payload, "created_at")
    source_path = _optional_path(payload, "source")

    snapshot_payload = _required_mapping(payload, "snapshot")
    snapshot = _build_snapshot(snapshot_payload)

    verification_payload = _required_mapping(payload, "verification")
    verification = RecoveryManifestVerification(
        sqlite_integrity_check=_required_string(
            verification_payload,
            "sqlite_integrity_check",
            parent="verification",
        ),
        status=_required_string(
            verification_payload,
            "status",
            parent="verification",
        ),
    )

    publication_payload = _required_mapping(payload, "publication")
    publication = RecoveryManifestPublication(
        manifest_published_last=_required_bool(
            publication_payload,
            "manifest_published_last",
            parent="publication",
        )
    )

    return RecoveryManifest(
        schema_version=schema_version,
        acquisition_type=acquisition_type,
        asset_id=asset_id,
        asset_type=asset_type,
        created_at_utc=created_at_utc,
        source_path=source_path,
        snapshot=snapshot,
        verification=verification,
        publication=publication,
    )


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.NOT_FOUND,
            f"recovery manifest not found: {path}",
        )

    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.INVALID_JSON,
            f"invalid recovery manifest JSON: {exc}",
        ) from exc
    except OSError as exc:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.UNREADABLE,
            f"unable to read recovery manifest: {exc}",
        ) from exc

    if not isinstance(decoded, dict):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.ROOT_NOT_OBJECT,
            "recovery manifest must contain a JSON object",
        )
    return decoded


def _required_mapping(
    data: dict[str, Any],
    key: str,
    *,
    parent: str | None = None,
) -> dict[str, Any]:
    field_path = _field_path(parent, key)
    if key not in data:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING,
            f"required manifest object is missing: {field_path}",
            field_path=field_path,
        )
    value = data[key]
    if not isinstance(value, dict):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_TYPE_INVALID,
            f"manifest field must be an object: {field_path}",
            field_path=field_path,
        )
    return value


def _required_string(
    data: dict[str, Any],
    key: str,
    *,
    parent: str | None = None,
) -> str:
    field_path = _field_path(parent, key)
    if key not in data:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING,
            f"required manifest field is missing: {field_path}",
            field_path=field_path,
        )
    value = data[key]
    if not isinstance(value, str):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_TYPE_INVALID,
            f"manifest field must be a string: {field_path}",
            field_path=field_path,
        )
    normalized = value.strip()
    if not normalized:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_VALUE_INVALID,
            f"manifest field must not be empty: {field_path}",
            field_path=field_path,
        )
    return normalized


def _optional_string(data: dict[str, Any], key: str) -> str | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if not isinstance(value, str):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_TYPE_INVALID,
            f"manifest field must be a string when provided: {key}",
            field_path=key,
        )
    normalized = value.strip()
    if not normalized:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_VALUE_INVALID,
            f"manifest field must not be empty when provided: {key}",
            field_path=key,
        )
    return normalized


def _required_nonnegative_int(
    data: dict[str, Any],
    key: str,
    *,
    parent: str,
) -> int:
    field_path = _field_path(parent, key)
    if key not in data:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING,
            f"required manifest field is missing: {field_path}",
            field_path=field_path,
        )
    value = data[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_TYPE_INVALID,
            f"manifest field must be an integer: {field_path}",
            field_path=field_path,
        )
    if value < 0:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_VALUE_INVALID,
            f"manifest field must not be negative: {field_path}",
            field_path=field_path,
        )
    return value


def _required_bool(
    data: dict[str, Any],
    key: str,
    *,
    parent: str,
) -> bool:
    field_path = _field_path(parent, key)
    if key not in data:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING,
            f"required manifest field is missing: {field_path}",
            field_path=field_path,
        )
    value = data[key]
    if not isinstance(value, bool):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_TYPE_INVALID,
            f"manifest field must be a boolean: {field_path}",
            field_path=field_path,
        )
    return value


def _required_utc_timestamp(data: dict[str, Any], key: str) -> datetime:
    raw_value = _required_string(data, key)
    normalized = raw_value[:-1] + "+00:00" if raw_value.endswith("Z") else raw_value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.TIMESTAMP_INVALID,
            f"manifest timestamp is invalid: {key}",
            field_path=key,
        ) from exc

    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.TIMESTAMP_INVALID,
            f"manifest timestamp must be timezone-aware: {key}",
            field_path=key,
        )
    return parsed.astimezone(UTC)


def _optional_path(data: dict[str, Any], key: str) -> Path | None:
    value = _optional_string(data, key)
    return None if value is None else Path(value)


def _build_snapshot(data: dict[str, Any]) -> RecoveryManifestSnapshot:
    filename = _required_string(data, "filename", parent="snapshot")
    candidate = Path(filename)
    if candidate.name != filename or candidate.is_absolute():
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.SNAPSHOT_FILENAME_UNSAFE,
            "manifest snapshot filename must be a plain filename",
            field_path="snapshot.filename",
        )

    if "sha256" not in data:
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING,
            "required manifest field is missing: snapshot.sha256",
            field_path="snapshot.sha256",
        )

    raw_sha256 = data["sha256"]
    if not isinstance(raw_sha256, str):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.FIELD_TYPE_INVALID,
            "manifest field must be a string: snapshot.sha256",
            field_path="snapshot.sha256",
        )

    sha256 = raw_sha256.strip().lower()
    if len(sha256) != 64 or any(character not in "0123456789abcdef" for character in sha256):
        raise RecoveryManifestError(
            RecoveryManifestFaultCode.CHECKSUM_INVALID,
            "manifest snapshot sha256 must contain exactly 64 hexadecimal characters",
            field_path="snapshot.sha256",
        )

    return RecoveryManifestSnapshot(
        filename=filename,
        size_bytes=_required_nonnegative_int(
            data,
            "size_bytes",
            parent="snapshot",
        ),
        sha256=sha256,
    )


def _field_path(parent: str | None, key: str) -> str:
    return key if parent is None else f"{parent}.{key}"
