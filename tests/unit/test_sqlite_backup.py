"""Unit tests for consistent SQLite backup creation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.exceptions import SqliteBackupError
from poe_backup_orchestrator.services.sqlite_backup import (
    create_sqlite_backup,
)


def create_source_database(path: Path) -> None:
    """Create a small valid SQLite source database."""
    connection = sqlite3.connect(path)

    try:
        connection.execute("CREATE TABLE assets (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        connection.execute(
            "INSERT INTO assets (name) VALUES (?)",
            ("POE Registry",),
        )
        connection.commit()
    finally:
        connection.close()


def sha256_file(path: Path) -> str:
    """Calculate a test file digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_create_sqlite_backup_creates_verified_artifacts(
    tmp_path: Path,
) -> None:
    """Confirm backup, manifest, hash, and integrity evidence are created."""
    source_path = tmp_path / "source.db"
    staging_root = tmp_path / "staging"
    create_source_database(source_path)

    result = create_sqlite_backup(
        source_path=source_path,
        staging_root=staging_root,
        asset_id="poe-registry",
        created_at=datetime(2026, 7, 25, 14, 30, tzinfo=UTC),
    )

    assert result.backup_path.is_file()
    assert result.manifest_path.is_file()
    assert result.integrity_check == "ok"
    assert result.sha256 == sha256_file(result.backup_path)
    assert result.size_bytes == result.backup_path.stat().st_size

    backup_connection = sqlite3.connect(result.backup_path)

    try:
        row = backup_connection.execute("SELECT name FROM assets WHERE id = 1").fetchone()
    finally:
        backup_connection.close()

    assert row == ("POE Registry",)

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert manifest["asset_id"] == "poe-registry"
    assert manifest["backup"]["sha256"] == result.sha256
    assert manifest["verification"]["status"] == "PASS"
    assert manifest["verification"]["sqlite_integrity_check"] == "ok"


def test_create_sqlite_backup_rejects_missing_source(
    tmp_path: Path,
) -> None:
    """Confirm a missing source database is rejected."""
    with pytest.raises(
        SqliteBackupError,
        match="SQLite source database not found",
    ):
        create_sqlite_backup(
            source_path=tmp_path / "missing.db",
            staging_root=tmp_path / "staging",
            asset_id="poe-registry",
        )


def test_create_sqlite_backup_rejects_invalid_asset_id(
    tmp_path: Path,
) -> None:
    """Confirm unsafe artifact identifiers are rejected."""
    source_path = tmp_path / "source.db"
    create_source_database(source_path)

    with pytest.raises(
        SqliteBackupError,
        match="Asset ID must contain",
    ):
        create_sqlite_backup(
            source_path=source_path,
            staging_root=tmp_path / "staging",
            asset_id="../registry",
        )


def test_create_sqlite_backup_rejects_existing_run_directory(
    tmp_path: Path,
) -> None:
    """Confirm timestamp collisions cannot overwrite prior evidence."""
    source_path = tmp_path / "source.db"
    staging_root = tmp_path / "staging"
    created_at = datetime(2026, 7, 25, 14, 30, tzinfo=UTC)
    create_source_database(source_path)

    create_sqlite_backup(
        source_path=source_path,
        staging_root=staging_root,
        asset_id="poe-registry",
        created_at=created_at,
    )

    with pytest.raises(FileExistsError):
        create_sqlite_backup(
            source_path=source_path,
            staging_root=staging_root,
            asset_id="poe-registry",
            created_at=created_at,
        )
