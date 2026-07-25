"""Tests for Registry acquisition repository acceptance."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

import pytest

from poe_backup_orchestrator.exceptions import (
    RegistryAcceptanceConflictError,
    RegistryAcceptanceError,
    RegistryAcceptanceInconsistentError,
)
from poe_backup_orchestrator.models.registry_acceptance import (
    RegistryAcceptanceStatus,
)
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


def _accept_once(
    tmp_path: Path,
) -> tuple[Path, Path, Path, object]:
    manifest_path, snapshot_path = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()
    ingestion_result = validate_registry_acquisition(manifest_path)
    result = accept_registry_acquisition(ingestion_result, destination_root)
    return manifest_path, snapshot_path, destination_root, result


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
    assert result.status is RegistryAcceptanceStatus.ACCEPTED
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


def test_accept_registry_acquisition_returns_idempotent_success_for_exact_duplicate(
    tmp_path: Path,
) -> None:
    manifest_path, _, destination_root, first_result = _accept_once(tmp_path)
    ingestion_result = validate_registry_acquisition(manifest_path)

    snapshot_mtime = first_result.snapshot_path.stat().st_mtime_ns
    manifest_mtime = first_result.manifest_path.stat().st_mtime_ns

    second_result = accept_registry_acquisition(
        ingestion_result,
        destination_root,
    )

    assert second_result.status is RegistryAcceptanceStatus.ALREADY_ACCEPTED
    assert second_result.asset_id == first_result.asset_id
    assert second_result.run_id == first_result.run_id
    assert second_result.destination_directory == first_result.destination_directory
    assert second_result.snapshot_path == first_result.snapshot_path
    assert second_result.manifest_path == first_result.manifest_path
    assert second_result.sha256 == first_result.sha256
    assert second_result.size_bytes == first_result.size_bytes
    assert second_result.snapshot_path.stat().st_mtime_ns == snapshot_mtime
    assert second_result.manifest_path.stat().st_mtime_ns == manifest_mtime


def test_accept_registry_acquisition_rejects_snapshot_content_conflict(
    tmp_path: Path,
) -> None:
    manifest_path, _, destination_root, result = _accept_once(tmp_path)
    result.snapshot_path.write_bytes(b"conflicting snapshot")
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(
        RegistryAcceptanceConflictError,
        match="snapshot size conflicts",
    ):
        accept_registry_acquisition(ingestion_result, destination_root)


def test_accept_registry_acquisition_rejects_same_size_snapshot_hash_conflict(
    tmp_path: Path,
) -> None:
    manifest_path, _, destination_root, result = _accept_once(tmp_path)
    original = result.snapshot_path.read_bytes()
    result.snapshot_path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(
        RegistryAcceptanceConflictError,
        match="snapshot SHA-256 conflicts",
    ):
        accept_registry_acquisition(ingestion_result, destination_root)


def test_accept_registry_acquisition_rejects_manifest_conflict(
    tmp_path: Path,
) -> None:
    manifest_path, _, destination_root, result = _accept_once(tmp_path)
    result.manifest_path.write_text("{}\n", encoding="utf-8")
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(
        RegistryAcceptanceConflictError,
        match="manifest conflicts",
    ):
        accept_registry_acquisition(ingestion_result, destination_root)


@pytest.mark.parametrize(
    "missing_name",
    [
        "poe-registry_20260725T160902Z.sqlite3",
        "poe-registry_20260725T160902Z.manifest.json",
    ],
)
def test_accept_registry_acquisition_rejects_incomplete_destination(
    tmp_path: Path,
    missing_name: str,
) -> None:
    manifest_path, _, destination_root, result = _accept_once(tmp_path)
    (result.destination_directory / missing_name).unlink()
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(
        RegistryAcceptanceInconsistentError,
        match="incomplete or polluted",
    ):
        accept_registry_acquisition(ingestion_result, destination_root)


@pytest.mark.parametrize(
    "unexpected_name",
    ["unexpected.txt", "snapshot.partial"],
)
def test_accept_registry_acquisition_rejects_polluted_destination(
    tmp_path: Path,
    unexpected_name: str,
) -> None:
    manifest_path, _, destination_root, result = _accept_once(tmp_path)
    (result.destination_directory / unexpected_name).write_text(
        "unexpected",
        encoding="utf-8",
    )
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(
        RegistryAcceptanceInconsistentError,
        match="incomplete or polluted",
    ):
        accept_registry_acquisition(ingestion_result, destination_root)


def test_accept_registry_acquisition_rejects_non_directory_destination(
    tmp_path: Path,
) -> None:
    manifest_path, _ = _create_valid_acquisition(tmp_path)
    destination_root = tmp_path / "repository"
    destination_root.mkdir()
    destination = destination_root / "20260725T160902Z"
    destination.write_text("not a directory", encoding="utf-8")
    ingestion_result = validate_registry_acquisition(manifest_path)

    with pytest.raises(
        RegistryAcceptanceInconsistentError,
        match="not a directory",
    ):
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

    with pytest.raises(
        RegistryAcceptanceError,
        match="snapshot no longer exists",
    ):
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

    with pytest.raises(
        RegistryAcceptanceError,
        match="SHA-256 verification failed",
    ):
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
