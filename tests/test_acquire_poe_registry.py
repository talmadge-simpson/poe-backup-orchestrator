"""Tests for the Windows POE Registry acquisition utility."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "windows" / "acquire_poe_registry.py"
)

SPEC = importlib.util.spec_from_file_location(
    "acquire_poe_registry",
    SCRIPT_PATH,
)
assert SPEC is not None
assert SPEC.loader is not None

MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def create_sqlite_database(path: Path) -> None:
    """Create a small valid SQLite database for acquisition tests."""
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE registry_items (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO registry_items (name) VALUES (?)",
            [("alpha",), ("beta",), ("gamma",)],
        )
        connection.commit()


def test_sha256_file_matches_hashlib(tmp_path: Path) -> None:
    """The helper should return the correct hexadecimal SHA-256 digest."""
    source = tmp_path / "payload.bin"
    payload = b"POE Backup Orchestrator\n"
    source.write_bytes(payload)

    assert MODULE.sha256_file(source) == hashlib.sha256(payload).hexdigest()


@pytest.mark.parametrize(
    ("supplied", "expected"),
    [
        ("poe-registry", "poe-registry"),
        (" POE-REGISTRY ", "poe-registry"),
        ("registry_01", "registry_01"),
    ],
)
def test_validate_asset_id_accepts_valid_values(
    supplied: str,
    expected: str,
) -> None:
    """Valid asset identifiers should be normalized and returned."""
    assert MODULE.validate_asset_id(supplied) == expected


@pytest.mark.parametrize(
    "asset_id",
    [
        "",
        "-registry",
        "_registry",
        "registry data",
        "registry.json",
        "registry\\data",
    ],
)
def test_validate_asset_id_rejects_invalid_values(asset_id: str) -> None:
    """Invalid identifiers should raise AcquisitionError."""
    with pytest.raises(MODULE.AcquisitionError):
        MODULE.validate_asset_id(asset_id)


def test_create_local_snapshot_creates_verified_copy(tmp_path: Path) -> None:
    """The SQLite Online Backup API should create a usable snapshot."""
    source = tmp_path / "source.sqlite3"
    snapshot = tmp_path / "snapshot.sqlite3"
    create_sqlite_database(source)

    integrity = MODULE.create_local_snapshot(source, snapshot)

    assert integrity == "ok"
    assert snapshot.is_file()

    with sqlite3.connect(snapshot) as connection:
        rows = connection.execute("SELECT name FROM registry_items ORDER BY id").fetchall()
        check = connection.execute("PRAGMA integrity_check").fetchone()[0]

    assert rows == [("alpha",), ("beta",), ("gamma",)]
    assert check == "ok"


def test_publish_file_replaces_partial_with_final_file(
    tmp_path: Path,
) -> None:
    """Publication should leave a final file and no partial artifact."""
    local = tmp_path / "local.txt"
    final = tmp_path / "published.txt"
    partial = tmp_path / "published.txt.partial"

    local.write_text("verified payload\n", encoding="utf-8")

    MODULE.publish_file(local, final)

    assert final.read_text(encoding="utf-8") == "verified payload\n"
    assert not partial.exists()


def test_acquire_registry_publishes_snapshot_and_manifest(
    tmp_path: Path,
) -> None:
    """A complete acquisition should publish consistent artifacts."""
    source = tmp_path / "POERegistry.db"
    destination = tmp_path / "incoming"
    destination.mkdir()
    create_sqlite_database(source)

    snapshot, manifest_path, manifest = MODULE.acquire_registry(
        source_path=source,
        destination_root=destination,
        asset_id="poe-registry",
    )

    assert snapshot.is_file()
    assert manifest_path.is_file()
    assert snapshot.parent == destination / "poe-registry"
    assert manifest_path.parent == snapshot.parent

    stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert stored_manifest == manifest
    assert manifest["schema_version"] == "1.0"
    assert manifest["asset_id"] == "poe-registry"
    assert manifest["verification"]["status"] == "PASS"
    assert manifest["verification"]["sqlite_integrity_check"] == "ok"
    assert manifest["snapshot"]["filename"] == snapshot.name
    assert manifest["snapshot"]["size_bytes"] == snapshot.stat().st_size
    assert manifest["snapshot"]["sha256"] == MODULE.sha256_file(snapshot)
    assert manifest["publication"]["manifest_published_last"] is True

    with sqlite3.connect(snapshot) as connection:
        row_count = connection.execute("SELECT COUNT(*) FROM registry_items").fetchone()[0]

    assert row_count == 3
    assert not list(snapshot.parent.glob("*.partial"))


def test_acquire_registry_rejects_missing_source(tmp_path: Path) -> None:
    """A missing source database should fail before publication."""
    destination = tmp_path / "incoming"
    destination.mkdir()

    with pytest.raises(
        MODULE.AcquisitionError,
        match="Registry database not found",
    ):
        MODULE.acquire_registry(
            source_path=tmp_path / "missing.db",
            destination_root=destination,
            asset_id="poe-registry",
        )


def test_acquire_registry_rejects_missing_destination(
    tmp_path: Path,
) -> None:
    """A missing destination directory should fail before acquisition."""
    source = tmp_path / "POERegistry.db"
    create_sqlite_database(source)

    with pytest.raises(
        MODULE.AcquisitionError,
        match="Acquisition destination not found",
    ):
        MODULE.acquire_registry(
            source_path=source,
            destination_root=tmp_path / "missing",
            asset_id="poe-registry",
        )
