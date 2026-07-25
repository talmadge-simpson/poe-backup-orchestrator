"""Consistent SQLite backup service."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.exceptions import SqliteBackupError
from poe_backup_orchestrator.models import SqliteBackupResult

_ASSET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def _validate_asset_id(asset_id: str) -> str:
    """Validate and normalize an asset identifier."""
    normalized = asset_id.strip().lower()

    if not _ASSET_ID_PATTERN.fullmatch(normalized):
        raise SqliteBackupError(
            "Asset ID must contain only lowercase letters, numbers, hyphens, and underscores."
        )

    return normalized


def create_sqlite_backup(
    source_path: Path,
    staging_root: Path,
    asset_id: str,
    *,
    created_at: datetime | None = None,
) -> SqliteBackupResult:
    """Create and verify a transactionally consistent SQLite backup."""
    source_path = source_path.expanduser().resolve()
    staging_root = staging_root.expanduser().resolve()
    normalized_asset_id = _validate_asset_id(asset_id)

    if not source_path.is_file():
        raise SqliteBackupError(f"SQLite source database not found: {source_path}")

    timestamp = created_at or datetime.now(UTC)
    timestamp_text = timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    filename_timestamp = timestamp.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")

    destination_directory = staging_root / "sqlite" / normalized_asset_id / filename_timestamp
    destination_directory.mkdir(parents=True, exist_ok=False)

    backup_path = destination_directory / (f"{normalized_asset_id}_{filename_timestamp}.sqlite3")
    partial_path = backup_path.with_suffix(".sqlite3.partial")
    manifest_path = destination_directory / "manifest.json"

    source_connection: sqlite3.Connection | None = None
    destination_connection: sqlite3.Connection | None = None

    try:
        source_uri = f"{source_path.as_uri()}?mode=ro"
        source_connection = sqlite3.connect(source_uri, uri=True)
        destination_connection = sqlite3.connect(partial_path)

        source_connection.backup(destination_connection)
        destination_connection.commit()

        integrity_row = destination_connection.execute("PRAGMA integrity_check").fetchone()

        integrity_check = str(integrity_row[0]) if integrity_row is not None else "unknown"

        if integrity_check.casefold() != "ok":
            raise SqliteBackupError(f"SQLite backup integrity check failed: {integrity_check}")

    except sqlite3.Error as exc:
        raise SqliteBackupError(f"SQLite backup failed: {exc}") from exc

    finally:
        if destination_connection is not None:
            destination_connection.close()

        if source_connection is not None:
            source_connection.close()

    partial_path.replace(backup_path)

    size_bytes = backup_path.stat().st_size
    sha256 = _sha256_file(backup_path)

    manifest = {
        "schema_version": "1.0",
        "asset_id": normalized_asset_id,
        "asset_type": "sqlite",
        "created_at": timestamp_text,
        "source": {
            "path": str(source_path),
        },
        "backup": {
            "path": str(backup_path),
            "filename": backup_path.name,
            "size_bytes": size_bytes,
            "sha256": sha256,
        },
        "verification": {
            "sqlite_integrity_check": integrity_check,
            "status": "PASS",
        },
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return SqliteBackupResult(
        asset_id=normalized_asset_id,
        source_path=source_path,
        backup_path=backup_path,
        manifest_path=manifest_path,
        sha256=sha256,
        size_bytes=size_bytes,
        integrity_check=integrity_check,
        created_at=timestamp_text,
    )
