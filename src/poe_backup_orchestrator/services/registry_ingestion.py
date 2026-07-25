"""Read-only validation service for Windows Registry acquisition artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.exceptions import RegistryIngestionError
from poe_backup_orchestrator.models import RegistryIngestionResult

_ASSET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a required manifest mapping."""
    value = data.get(key)

    if not isinstance(value, dict):
        raise RegistryIngestionError(f"Missing or invalid manifest object: {key}")

    return value


def _required_string(data: dict[str, Any], key: str, section: str) -> str:
    """Return a required non-empty manifest string."""
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise RegistryIngestionError(f"Missing or invalid manifest value: {section}.{key}")

    return value.strip()


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    """Load and validate the top-level JSON manifest object."""
    if not manifest_path.is_file():
        raise RegistryIngestionError(f"Registry acquisition manifest not found: {manifest_path}")

    try:
        decoded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegistryIngestionError(f"Invalid Registry acquisition manifest JSON: {exc}") from exc
    except OSError as exc:
        raise RegistryIngestionError(
            f"Unable to read Registry acquisition manifest: {exc}"
        ) from exc

    if not isinstance(decoded, dict):
        raise RegistryIngestionError("Registry acquisition manifest must contain a JSON object.")

    return decoded


def _resolve_snapshot(manifest_path: Path, filename: str) -> Path:
    """Resolve a snapshot filename without allowing path traversal."""
    candidate = Path(filename)

    if candidate.name != filename or candidate.is_absolute():
        raise RegistryIngestionError("Manifest snapshot filename must be a plain filename.")

    snapshot_path = manifest_path.parent / candidate

    if not snapshot_path.is_file():
        raise RegistryIngestionError(f"Registry acquisition snapshot not found: {snapshot_path}")

    return snapshot_path


def _verify_sqlite_integrity(snapshot_path: Path) -> str:
    """Run SQLite integrity_check against the acquisition snapshot."""
    connection: sqlite3.Connection | None = None

    try:
        connection = sqlite3.connect(
            f"{snapshot_path.as_uri()}?mode=ro",
            uri=True,
        )
        row = connection.execute("PRAGMA integrity_check").fetchone()
    except sqlite3.Error as exc:
        raise RegistryIngestionError(
            f"Registry acquisition SQLite verification failed: {exc}"
        ) from exc
    finally:
        if connection is not None:
            connection.close()

    integrity_check = str(row[0]) if row is not None else "unknown"

    if integrity_check.casefold() != "ok":
        raise RegistryIngestionError(
            f"Registry acquisition integrity check failed: {integrity_check}"
        )

    return integrity_check


def validate_registry_acquisition(
    manifest_path: Path,
) -> RegistryIngestionResult:
    """Validate a published Windows Registry acquisition without modifying it."""
    manifest_path = manifest_path.expanduser().resolve()
    manifest = _load_manifest(manifest_path)

    schema_version = _required_string(manifest, "schema_version", "manifest")
    acquisition_type = _required_string(manifest, "acquisition_type", "manifest")
    asset_id = _required_string(manifest, "asset_id", "manifest")
    created_at = _required_string(manifest, "created_at", "manifest")

    if schema_version != "1.0":
        raise RegistryIngestionError(
            f"Unsupported Registry acquisition schema version: {schema_version}"
        )

    if acquisition_type != "windows_sqlite_snapshot":
        raise RegistryIngestionError(f"Unsupported Registry acquisition type: {acquisition_type}")

    if not _ASSET_ID_PATTERN.fullmatch(asset_id):
        raise RegistryIngestionError("Manifest asset ID contains unsupported characters.")

    snapshot = _required_mapping(manifest, "snapshot")
    filename = _required_string(snapshot, "filename", "snapshot")
    expected_sha256 = _required_string(snapshot, "sha256", "snapshot")
    expected_size = snapshot.get("size_bytes")

    if not _SHA256_PATTERN.fullmatch(expected_sha256):
        raise RegistryIngestionError(
            "Manifest snapshot SHA-256 must be 64 lowercase hexadecimal characters."
        )

    if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
        raise RegistryIngestionError("Manifest snapshot size_bytes must be a non-negative integer.")

    verification = _required_mapping(manifest, "verification")
    manifest_integrity = _required_string(verification, "sqlite_integrity_check", "verification")
    manifest_status = _required_string(verification, "status", "verification")

    if manifest_integrity.casefold() != "ok" or manifest_status != "PASS":
        raise RegistryIngestionError(
            "Manifest does not declare a successful acquisition verification."
        )

    publication = _required_mapping(manifest, "publication")

    if publication.get("manifest_published_last") is not True:
        raise RegistryIngestionError("Manifest does not confirm manifest-last publication.")

    snapshot_path = _resolve_snapshot(manifest_path, filename)
    actual_size = snapshot_path.stat().st_size

    if actual_size != expected_size:
        raise RegistryIngestionError(
            "Registry acquisition size mismatch: "
            f"expected {expected_size}, calculated {actual_size}."
        )

    actual_sha256 = _sha256_file(snapshot_path)

    if actual_sha256 != expected_sha256:
        raise RegistryIngestionError(
            "Registry acquisition SHA-256 mismatch: "
            f"expected {expected_sha256}, calculated {actual_sha256}."
        )

    integrity_check = _verify_sqlite_integrity(snapshot_path)

    return RegistryIngestionResult(
        asset_id=asset_id,
        manifest_path=manifest_path,
        snapshot_path=snapshot_path,
        created_at=created_at,
        sha256=actual_sha256,
        size_bytes=actual_size,
        integrity_check=integrity_check,
    )
