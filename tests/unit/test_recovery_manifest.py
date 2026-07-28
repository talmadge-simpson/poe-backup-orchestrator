"""Tests for the governed restore manifest contract."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from poe_backup_orchestrator.models import (
    RecoveryManifestFaultCode,
)
from poe_backup_orchestrator.services.restore.manifest import (
    RecoveryManifestError,
    read_recovery_manifest,
)


def valid_manifest() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "acquisition_type": "windows_sqlite_snapshot",
        "asset_id": "poe-registry",
        "asset_type": "sqlite",
        "created_at": "2026-07-27T17:00:00Z",
        "source": "/srv/poe/registry/poe-registry.sqlite3",
        "snapshot": {
            "filename": "poe-registry_20260727T170000Z.sqlite3",
            "size_bytes": 4096,
            "sha256": "A" * 64,
        },
        "verification": {
            "sqlite_integrity_check": "ok",
            "status": "PASS",
        },
        "publication": {
            "manifest_published_last": True,
        },
    }


def write_manifest(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_read_recovery_manifest_returns_typed_contract(tmp_path: Path) -> None:
    manifest = read_recovery_manifest(write_manifest(tmp_path, valid_manifest()))

    assert manifest.schema_version == "1.0"
    assert manifest.acquisition_type == "windows_sqlite_snapshot"
    assert manifest.asset_id == "poe-registry"
    assert manifest.asset_type == "sqlite"
    assert manifest.created_at_utc == datetime(2026, 7, 27, 17, 0, tzinfo=UTC)
    assert manifest.snapshot.filename == "poe-registry_20260727T170000Z.sqlite3"
    assert manifest.snapshot.size_bytes == 4096
    assert manifest.snapshot.sha256 == "a" * 64
    assert manifest.verification.passed is True
    assert manifest.publication.manifest_published_last is True


def test_read_recovery_manifest_accepts_optional_asset_type_and_source(
    tmp_path: Path,
) -> None:
    payload = valid_manifest()
    payload.pop("asset_type")
    payload.pop("source")

    manifest = read_recovery_manifest(write_manifest(tmp_path, payload))

    assert manifest.asset_type is None
    assert manifest.source_path is None


def test_read_recovery_manifest_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(tmp_path / "missing.json")

    assert captured.value.fault_code is RecoveryManifestFaultCode.NOT_FOUND


def test_read_recovery_manifest_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(path)

    assert captured.value.fault_code is RecoveryManifestFaultCode.INVALID_JSON


def test_read_recovery_manifest_rejects_non_object_root(tmp_path: Path) -> None:
    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, []))

    assert captured.value.fault_code is RecoveryManifestFaultCode.ROOT_NOT_OBJECT


@pytest.mark.parametrize(
    ("field", "fault_code"),
    [
        ("schema_version", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
        ("acquisition_type", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
        ("asset_id", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
        ("created_at", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
        ("snapshot", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
        ("verification", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
        ("publication", RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING),
    ],
)
def test_read_recovery_manifest_rejects_missing_required_top_level_fields(
    tmp_path: Path,
    field: str,
    fault_code: RecoveryManifestFaultCode,
) -> None:
    payload = valid_manifest()
    payload.pop(field)

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.fault_code is fault_code
    assert captured.value.field_path == field


def test_read_recovery_manifest_rejects_unsupported_version(tmp_path: Path) -> None:
    payload = valid_manifest()
    payload["schema_version"] = "2.0"

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.fault_code is RecoveryManifestFaultCode.VERSION_UNSUPPORTED
    assert captured.value.field_path == "schema_version"


def test_read_recovery_manifest_rejects_unsupported_acquisition_type(
    tmp_path: Path,
) -> None:
    payload = valid_manifest()
    payload["acquisition_type"] = "unknown"

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.fault_code is RecoveryManifestFaultCode.ACQUISITION_TYPE_UNSUPPORTED


@pytest.mark.parametrize(
    "filename",
    [
        "../outside.sqlite3",
        "nested/registry.sqlite3",
        "/absolute/registry.sqlite3",
    ],
)
def test_read_recovery_manifest_rejects_unsafe_snapshot_filename(
    tmp_path: Path,
    filename: str,
) -> None:
    payload = valid_manifest()
    payload["snapshot"]["filename"] = filename

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.fault_code is RecoveryManifestFaultCode.SNAPSHOT_FILENAME_UNSAFE
    assert captured.value.field_path == "snapshot.filename"


@pytest.mark.parametrize("digest", ["", "a" * 63, "a" * 65, "g" * 64])
def test_read_recovery_manifest_rejects_invalid_checksum(
    tmp_path: Path,
    digest: str,
) -> None:
    payload = valid_manifest()
    payload["snapshot"]["sha256"] = digest

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.fault_code is RecoveryManifestFaultCode.CHECKSUM_INVALID


@pytest.mark.parametrize("value", [-1, "4096", True])
def test_read_recovery_manifest_rejects_invalid_snapshot_size(
    tmp_path: Path,
    value: object,
) -> None:
    payload = valid_manifest()
    payload["snapshot"]["size_bytes"] = value

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.field_path == "snapshot.size_bytes"


@pytest.mark.parametrize(
    "created_at",
    [
        "not-a-timestamp",
        "2026-07-27T17:00:00",
    ],
)
def test_read_recovery_manifest_rejects_invalid_timestamp(
    tmp_path: Path,
    created_at: str,
) -> None:
    payload = valid_manifest()
    payload["created_at"] = created_at

    with pytest.raises(RecoveryManifestError) as captured:
        read_recovery_manifest(write_manifest(tmp_path, payload))

    assert captured.value.fault_code is RecoveryManifestFaultCode.TIMESTAMP_INVALID


def test_read_recovery_manifest_preserves_recorded_failed_verification(
    tmp_path: Path,
) -> None:
    payload = valid_manifest()
    payload["verification"]["status"] = "FAIL"

    manifest = read_recovery_manifest(write_manifest(tmp_path, payload))

    assert manifest.verification.status == "FAIL"
    assert manifest.verification.passed is False


def test_read_recovery_manifest_preserves_manifest_last_false(
    tmp_path: Path,
) -> None:
    payload = valid_manifest()
    payload["publication"]["manifest_published_last"] = False

    manifest = read_recovery_manifest(write_manifest(tmp_path, payload))

    assert manifest.publication.manifest_published_last is False


def test_read_recovery_manifest_accepts_structured_source_path(tmp_path: Path) -> None:
    payload = valid_manifest()
    payload["source"] = {
        "hostname": "DSKTOP-WIN-000",
        "path": r"C:\POE\registry\runtime\POERegistry.db",
    }
    manifest = read_recovery_manifest(write_manifest(tmp_path, payload))
    assert manifest.source_path == Path(r"C:\POE\registry\runtime\POERegistry.db")
