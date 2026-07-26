"""Tests for Registry-specific SQLite acquisition publication."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.services import (
    create_registry_acquisition,
    validate_registry_acquisition,
)


def test_registry_acquisition_emits_ingestion_compatible_manifest(
    tmp_path: Path,
) -> None:
    source = tmp_path / "registry.sqlite3"
    connection = sqlite3.connect(source)
    connection.execute("CREATE TABLE assets (id INTEGER PRIMARY KEY, name TEXT)")
    connection.execute("INSERT INTO assets (name) VALUES ('sample')")
    connection.commit()
    connection.close()

    created_at = datetime(2026, 7, 26, 18, 0, tzinfo=UTC)
    result = create_registry_acquisition(
        source_path=source,
        staging_root=tmp_path / "staging",
        asset_id="poeregistry",
        created_at=created_at,
    )

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1.0"
    assert manifest["acquisition_type"] == "windows_sqlite_snapshot"
    assert manifest["snapshot"]["filename"] == result.backup_path.name
    assert manifest["snapshot"]["sha256"] == result.sha256
    assert manifest["publication"]["manifest_published_last"] is True

    validation = validate_registry_acquisition(result.manifest_path)
    assert validation.snapshot_path == result.backup_path
    assert validation.sha256 == result.sha256
    assert validation.integrity_check == "ok"
