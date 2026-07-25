"""Tests for Registry acquisition repository acceptance."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from poe_backup_orchestrator.exceptions import RegistryAcceptanceError
from poe_backup_orchestrator.services.registry_acceptance import (
    accept_registry_acquisition,
)
from poe_backup_orchestrator.services.registry_ingestion import (
    validate_registry_acquisition,
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _create_valid_acquisition(
    tmp_path: Path,
) -> tuple[Path, Path]:
    acquisition_root = tmp_path / "incoming"
    acquisition_root.mkdir()

    snapshot_path = acquisition_root / "poe-registry_20260725T160902Z.sqlite3"

    connection = sqlite3.connect(snapshot_path)
    connection.execute(
        "CREATE TABLE registry_assets (asset_id TEXT PRIMARY KEY, name TEXT NOT NULL)"
    )
    connection.execute(
        "INSERT INTO registry_assets(asset_id, name) VALUES (?, ?)",
        ("asset-001", "Test Asset"),
    )
    connection.commit()
    connection.close()

    manifest_path = acquisition_root / "poe-registry_20260725T160902Z.manifest.json"

    manifest = {
        "schema_version": "1.0",
        "acquisition_type": "windows_sqlite_snapshot",
        "asset_id": "poe-registry",
        "created_at": "2026-07-25T16:09:02Z",
        "source": {
            "hostname": "TEST-WINDOWS",
            "path": r"C:\POE\registry\runtime\POERegistry.db",
            "journal_mode": "wal",
        },
        "snapshot": {
            "filename": snapshot_path.name,
            "sha256": _sha256_file(snapshot_path),
            "size_bytes": snapshot_path.stat().st_size,
        },
        "verification": {
            "sqlite_integrity_check": "ok",
            "status": "PASS",
        },
        "publication": {
            "destination_root": r"P:\Incoming\Registry-Acquisition",
            "manifest_published_last": True,
        },
    }

    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    return manifest_path, snapshot_path


def test_accept_registry_acquisition_promotes_valid_artifact(
    tmp_path: Path,
) -> None:
    manifest_path, source_snapshot = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)
    result = accept_registry_acquisition(ingestion_result, destination_root)

    assert result.asset_id == "poe-registry"
    assert result.run_id == "20260725T160902Z"
    assert result.destination_directory == destination_root / "20260725T160902Z"
    assert result.snapshot_path.is_file()
    assert result.manifest_path.is_file()
    assert result.snapshot_path.read_bytes() == source_snapshot.read_bytes()
    assert _sha256_file(result.snapshot_path) == result.sha256
    assert result.snapshot_path.stat().st_size == result.size_bytes


def test_accept_registry_acquisition_preserves_source_files(
    tmp_path: Path,
) -> None:
    manifest_path, snapshot_path = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)
    accept_registry_acquisition(ingestion_result, destination_root)

    assert manifest_path.is_file()
    assert snapshot_path.is_file()


def test_accept_registry_acquisition_rejects_existing_run_directory(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()
    (destination_root / "20260725T160902Z").mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(RegistryAcceptanceError, match="destination already exists"):
        accept_registry_acquisition(ingestion_result, destination_root)


def test_accept_registry_acquisition_rejects_missing_destination_root(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _create_valid_acquisition(tmp_path)
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(RegistryAcceptanceError, match="does not exist"):
        accept_registry_acquisition(
            ingestion_result,
            tmp_path / "missing-repository",
        )


def test_accept_registry_acquisition_rejects_missing_source_snapshot(
    tmp_path: Path,
) -> None:
    manifest_path, snapshot_path = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)
    snapshot_path.unlink()

    with pytest.raises(RegistryAcceptanceError, match="snapshot no longer exists"):
        accept_registry_acquisition(ingestion_result, destination_root)


def test_accept_registry_acquisition_cleans_failed_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path, _ = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)

    def incorrect_hash(_: Path) -> str:
        return "0" * 64

    monkeypatch.setattr(
        "poe_backup_orchestrator.services.registry_acceptance._sha256_file",
        incorrect_hash,
    )

    with pytest.raises(RegistryAcceptanceError, match="SHA-256 verification failed"):
        accept_registry_acquisition(ingestion_result, destination_root)

    assert not (destination_root / "20260725T160902Z").exists()


def test_accept_registry_acquisition_leaves_no_partial_files(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)
    result = accept_registry_acquisition(ingestion_result, destination_root)

    assert not list(result.destination_directory.glob("*.partial"))


def test_accept_registry_acquisition_publishes_only_expected_files(
    tmp_path: Path,
) -> None:
    manifest_path, snapshot_path = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()

    ingestion_result = validate_registry_acquisition(manifest_path)
    result = accept_registry_acquisition(ingestion_result, destination_root)

    published_names = {path.name for path in result.destination_directory.iterdir()}

    assert published_names == {
        snapshot_path.name,
        manifest_path.name,
    }
