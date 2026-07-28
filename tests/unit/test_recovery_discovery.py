"""Tests for read-only governed recovery-point discovery."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from poe_backup_orchestrator.models import (
    RecoveryPointEligibility,
    RecoveryPointReasonCode,
)
from poe_backup_orchestrator.services.restore import (
    RecoveryPointDiscoveryError,
    discover_recovery_points,
    locate_recovery_point_packages,
)

EVALUATED_AT = datetime(2026, 7, 27, 18, 0, tzinfo=UTC)


def manifest_payload(
    *,
    asset_id: str = "poe-registry",
    created_at: str = "2026-07-27T17:00:00Z",
    filename: str = "poe-registry.sqlite3",
    verification_status: str = "PASS",
) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "acquisition_type": "windows_sqlite_snapshot",
        "asset_id": asset_id,
        "asset_type": "sqlite",
        "created_at": created_at,
        "source": "/srv/poe/registry/poe-registry.sqlite3",
        "snapshot": {
            "filename": filename,
            "size_bytes": 4096,
            "sha256": "a" * 64,
        },
        "verification": {
            "sqlite_integrity_check": "ok",
            "status": verification_status,
        },
        "publication": {
            "manifest_published_last": True,
        },
    }


def create_package(
    root: Path,
    package_name: str,
    *,
    payload: dict[str, Any] | None = None,
    manifest_text: str | None = None,
) -> Path:
    package = root / package_name
    package.mkdir()

    if payload is not None:
        (package / "manifest.json").write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
    elif manifest_text is not None:
        (package / "manifest.json").write_text(manifest_text, encoding="utf-8")

    return package


def test_locate_recovery_point_packages_returns_shallow_sorted_candidates(
    tmp_path: Path,
) -> None:
    create_package(tmp_path, "run-b")
    create_package(tmp_path, "run-a")
    (tmp_path / "not-a-package.txt").write_text("ignored", encoding="utf-8")
    (tmp_path / ".hidden").mkdir()
    (tmp_path / "run-c.partial").mkdir()
    (tmp_path / "run-d.tmp").mkdir()
    (tmp_path / "run-e.staging").mkdir()
    (tmp_path / "lost+found").mkdir()

    packages = locate_recovery_point_packages(tmp_path)

    assert tuple(path.name for path in packages) == ("run-a", "run-b")


def test_locate_recovery_point_packages_rejects_missing_root(tmp_path: Path) -> None:
    with pytest.raises(RecoveryPointDiscoveryError, match="does not exist"):
        locate_recovery_point_packages(tmp_path / "missing")


def test_locate_recovery_point_packages_rejects_file_root(tmp_path: Path) -> None:
    root = tmp_path / "root.txt"
    root.write_text("not a directory", encoding="utf-8")

    with pytest.raises(RecoveryPointDiscoveryError, match="not a directory"):
        locate_recovery_point_packages(root)


def test_discover_recovery_points_constructs_typed_unknown_point(
    tmp_path: Path,
) -> None:
    package = create_package(
        tmp_path,
        "backup-20260727T170000Z",
        payload=manifest_payload(),
    )

    points = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert len(points) == 1
    point = points[0]
    assert point.recovery_point_id == "backup-20260727T170000Z"
    assert point.package_path == package.resolve()
    assert point.manifest_path == package.resolve() / "manifest.json"
    assert point.artifact_path == package.resolve() / "poe-registry.sqlite3"
    assert point.source_backup_execution_id == "backup-20260727T170000Z"
    assert point.source_registry_id == "poe-registry"
    assert point.created_at_utc == datetime(2026, 7, 27, 17, 0, tzinfo=UTC)
    assert point.artifact_size_bytes == 4096
    assert point.artifact_sha256 == "a" * 64
    assert point.manifest_version == "1.0"
    assert point.verification_status == "PASS"
    assert point.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert point.eligibility.reason_codes == (RecoveryPointReasonCode.STATUS_UNDETERMINED,)


def test_discover_recovery_points_does_not_require_artifact_to_exist(
    tmp_path: Path,
) -> None:
    create_package(tmp_path, "backup-1", payload=manifest_payload())

    point = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )[0]

    assert point.artifact_path is not None
    assert not point.artifact_path.exists()
    assert point.eligibility.classification is RecoveryPointEligibility.UNKNOWN


def test_discover_recovery_points_retains_package_with_missing_manifest(
    tmp_path: Path,
) -> None:
    package = create_package(tmp_path, "backup-missing-manifest")

    point = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )[0]

    assert point.package_path == package.resolve()
    assert point.manifest_path == package.resolve() / "manifest.json"
    assert point.artifact_path is None
    assert point.source_registry_id is None
    assert point.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert point.eligibility.reason_codes == (RecoveryPointReasonCode.MANIFEST_MISSING,)


def test_discover_recovery_points_retains_package_with_invalid_manifest(
    tmp_path: Path,
) -> None:
    create_package(tmp_path, "backup-invalid-manifest", manifest_text="{invalid")

    point = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )[0]

    assert point.artifact_path is None
    assert point.eligibility.reason_codes == (RecoveryPointReasonCode.MANIFEST_INVALID,)
    assert point.eligibility.warnings


def test_discover_recovery_points_maps_unsupported_manifest_version(
    tmp_path: Path,
) -> None:
    payload = manifest_payload()
    payload["schema_version"] = "2.0"
    create_package(tmp_path, "backup-version-2", payload=payload)

    point = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )[0]

    assert point.eligibility.reason_codes == (RecoveryPointReasonCode.MANIFEST_VERSION_UNSUPPORTED,)


def test_discover_recovery_points_maps_invalid_checksum(
    tmp_path: Path,
) -> None:
    payload = manifest_payload()
    payload["snapshot"]["sha256"] = "invalid"
    create_package(tmp_path, "backup-invalid-checksum", payload=payload)

    point = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )[0]

    assert point.eligibility.reason_codes == (RecoveryPointReasonCode.CHECKSUM_INVALID,)


def test_discover_recovery_points_preserves_recorded_failed_verification(
    tmp_path: Path,
) -> None:
    create_package(
        tmp_path,
        "backup-failed-verification",
        payload=manifest_payload(verification_status="FAIL"),
    )

    point = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )[0]

    assert point.verification_status == "FAIL"
    assert point.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert point.eligibility.reason_codes == (RecoveryPointReasonCode.STATUS_UNDETERMINED,)


def test_discover_recovery_points_orders_newest_valid_first_and_unknown_last(
    tmp_path: Path,
) -> None:
    create_package(
        tmp_path,
        "backup-old",
        payload=manifest_payload(created_at="2026-07-25T17:00:00Z"),
    )
    create_package(
        tmp_path,
        "backup-new",
        payload=manifest_payload(created_at="2026-07-27T17:00:00Z"),
    )
    create_package(tmp_path, "backup-unknown")

    points = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert tuple(point.recovery_point_id for point in points) == (
        "backup-new",
        "backup-old",
        "backup-unknown",
    )


def test_discover_recovery_points_uses_identity_as_deterministic_tiebreaker(
    tmp_path: Path,
) -> None:
    create_package(tmp_path, "backup-b", payload=manifest_payload())
    create_package(tmp_path, "backup-a", payload=manifest_payload())

    points = discover_recovery_points(
        tmp_path,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert tuple(point.recovery_point_id for point in points) == (
        "backup-a",
        "backup-b",
    )


def test_discover_recovery_points_returns_empty_tuple_for_empty_root(
    tmp_path: Path,
) -> None:
    assert (
        discover_recovery_points(
            tmp_path,
            evaluated_at_utc=EVALUATED_AT,
        )
        == ()
    )


def test_discover_recovery_points_requires_utc_evaluation_timestamp(
    tmp_path: Path,
) -> None:
    create_package(tmp_path, "backup-1", payload=manifest_payload())

    with pytest.raises(ValueError, match="timezone-aware"):
        discover_recovery_points(
            tmp_path,
            evaluated_at_utc=datetime(2026, 7, 27, 18, 0),
        )


def test_locate_recovery_point_packages_translates_permission_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_resolve = Path.resolve

    def denied_resolve(path: Path, *args, **kwargs) -> Path:
        if path == tmp_path:
            raise PermissionError("permission denied")
        return original_resolve(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", denied_resolve)
    with pytest.raises(RecoveryPointDiscoveryError, match="unable to inspect"):
        locate_recovery_point_packages(tmp_path)


def test_discover_recovery_points_supports_legacy_manifest_filename(tmp_path: Path) -> None:
    package = create_package(tmp_path, "20260725T160902Z")
    legacy = package / "poe-registry_20260725T160902Z.manifest.json"
    legacy.write_text(
        json.dumps(
            manifest_payload(
                created_at="2026-07-25T16:09:02Z", filename="poe-registry_20260725T160902Z.sqlite3"
            ),
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    point = discover_recovery_points(tmp_path, evaluated_at_utc=EVALUATED_AT)[0]
    assert point.manifest_path == legacy.resolve()
    assert point.created_at_utc == datetime(2026, 7, 25, 16, 9, 2, tzinfo=UTC)
    assert point.verification_status == "PASS"


def test_discover_recovery_points_populates_structured_source_metadata(tmp_path: Path) -> None:
    payload = manifest_payload(
        asset_id="poeregistry",
        created_at="2026-07-26T18:07:57Z",
        filename="poeregistry_20260726T180757Z.sqlite3",
    )
    payload["source"] = {
        "path": (
            "/srv/poe-nas/Incoming/Registry-Acquisition/"
            "poe-registry/poe-registry_20260725T160902Z.sqlite3"
        )
    }
    create_package(tmp_path, "20260726T180757Z", payload=payload)
    point = discover_recovery_points(tmp_path, evaluated_at_utc=EVALUATED_AT)[0]
    assert point.created_at_utc == datetime(2026, 7, 26, 18, 7, 57, tzinfo=UTC)
    assert point.source_registry_id == "poeregistry"
    assert point.manifest_version == "1.0"
    assert point.verification_status == "PASS"
