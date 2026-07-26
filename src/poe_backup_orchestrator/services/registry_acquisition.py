"""Registry-specific acquisition built on the consistent SQLite backup service."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from poe_backup_orchestrator.models import SqliteBackupResult
from poe_backup_orchestrator.services.sqlite_backup import create_sqlite_backup


def create_registry_acquisition(
    source_path: Path,
    staging_root: Path,
    asset_id: str,
    *,
    created_at: datetime | None = None,
) -> SqliteBackupResult:
    """Create a SQLite snapshot and publish the Registry acquisition manifest."""

    result = create_sqlite_backup(
        source_path=source_path,
        staging_root=staging_root,
        asset_id=asset_id,
        created_at=created_at,
    )

    manifest = {
        "schema_version": "1.0",
        "acquisition_type": "windows_sqlite_snapshot",
        "asset_id": result.asset_id,
        "created_at": result.created_at,
        "source": {
            "path": str(result.source_path),
        },
        "snapshot": {
            "filename": result.backup_path.name,
            "size_bytes": result.size_bytes,
            "sha256": result.sha256,
        },
        "verification": {
            "sqlite_integrity_check": result.integrity_check,
            "status": "PASS",
        },
        "publication": {
            "manifest_published_last": True,
        },
    }

    _atomic_write_json(result.manifest_path, manifest)
    return result


def _atomic_write_json(destination: Path, value: dict[str, object]) -> None:
    descriptor: int | None = None
    temporary_path: Path | None = None

    try:
        descriptor, raw_path = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(raw_path)

        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = None
            json.dump(value, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())

        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
