"""Tests for Registry acquisition ingestion validation."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any

import pytest

from poe_backup_orchestrator.exceptions import RegistryIngestionError
from poe_backup_orchestrator.services.registry_ingestion import (
    validate_registry_acquisition,
)


def _create_acquisition(tmp_path: Path) -> tuple[Path, Path]:
    acquisition_root = tmp_path / "poe-registry"
    acquisition_root.mkdir()

    snapshot_path = acquisition_root / "poe-registry_20260725T160902Z.sqlite3"
    connection = sqlite3.connect(snapshot_path)
    connection.execute("CREATE TABLE example (id INTEGER PRIMARY KEY, value TEXT)")
    connection.execute("INSERT INTO example (value) VALUES ('verified')")
    connection.commit()
    connection.close()

    sha256 = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()

    manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "acquisition_type": "windows_sqlite_snapshot",
        "asset_id": "poe-registry",
        "created_at": "2026-07-25T16:09:02Z",
        "publication": {
            "destination_root": r"P:\Incoming\Registry-Acquisition",
            "manifest_published_last": True,
        },
        "snapshot": {
            "filename": snapshot_path.name,
            "sha256": sha256,
            "size_bytes": snapshot_path.stat().st_size,
        },
        "source": {
            "hostname": "DSKTOP-WIN-000",
            "journal_mode": "wal",
            "path": r"C:\POE\registry\runtime\POERegistry.db",
        },
        "verification": {
            "sqlite_integrity_check": "ok",
            "status": "PASS",
        },
    }

    manifest_path = acquisition_root / "poe-registry_20260725T160902Z.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return manifest_path, snapshot_path


def _read_manifest(manifest_path: Path) -> dict[str, Any]:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def _write_manifest(manifest_path: Path, manifest: dict[str, Any]) -> None:
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def test_validate_registry_acquisition_accepts_valid_artifact(tmp_path: Path) -> None:
    manifest_path, snapshot_path = _create_acquisition(tmp_path)

    result = validate_registry_acquisition(manifest_path)

    assert result.asset_id == "poe-registry"
    assert result.manifest_path == manifest_path.resolve()
    assert result.snapshot_path == snapshot_path.resolve()
    assert result.sha256 == hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    assert result.size_bytes == snapshot_path.stat().st_size
    assert result.integrity_check == "ok"
    assert result.created_at == "2026-07-25T16:09:02Z"


def test_validate_registry_acquisition_rejects_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(RegistryIngestionError, match="manifest not found"):
        validate_registry_acquisition(tmp_path / "missing.manifest.json")


def test_validate_registry_acquisition_rejects_invalid_json(tmp_path: Path) -> None:
    manifest_path = tmp_path / "invalid.manifest.json"
    manifest_path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(RegistryIngestionError, match="Invalid.*JSON"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_unsupported_schema(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["schema_version"] = "2.0"
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="schema version"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_wrong_type(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["acquisition_type"] = "unknown"
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="acquisition type"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_path_traversal(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["snapshot"]["filename"] = "../outside.sqlite3"
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="plain filename"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_missing_snapshot(tmp_path: Path) -> None:
    manifest_path, snapshot_path = _create_acquisition(tmp_path)
    snapshot_path.unlink()

    with pytest.raises(RegistryIngestionError, match="snapshot not found"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_size_mismatch(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["snapshot"]["size_bytes"] = 1
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="size mismatch"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_hash_mismatch(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["snapshot"]["sha256"] = "0" * 64
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="SHA-256 mismatch"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_failed_manifest_status(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["verification"]["status"] = "FAIL"
    _write_manifest(manifest_path, manifest)

    with pytest.raises(
        RegistryIngestionError,
        match="successful acquisition verification",
    ):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_missing_manifest_last_flag(tmp_path: Path) -> None:
    manifest_path, _ = _create_acquisition(tmp_path)
    manifest = _read_manifest(manifest_path)
    manifest["publication"]["manifest_published_last"] = False
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="manifest-last publication"):
        validate_registry_acquisition(manifest_path)


def test_validate_registry_acquisition_rejects_corrupt_sqlite(tmp_path: Path) -> None:
    manifest_path, snapshot_path = _create_acquisition(tmp_path)
    snapshot_path.write_bytes(b"not a sqlite database")

    manifest = _read_manifest(manifest_path)
    manifest["snapshot"]["size_bytes"] = snapshot_path.stat().st_size
    manifest["snapshot"]["sha256"] = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    _write_manifest(manifest_path, manifest)

    with pytest.raises(RegistryIngestionError, match="SQLite verification failed"):
        validate_registry_acquisition(manifest_path)
