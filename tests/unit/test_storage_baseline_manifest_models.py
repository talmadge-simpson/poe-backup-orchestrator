"""Tests for storage capture-session and baseline-manifest contracts."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_manifest import (
    STORAGE_BASELINE_MANIFEST_SCHEMA_VERSION,
    BaselineManifestStatus,
    CaptureExceptionSummary,
    CaptureScope,
    CaptureSession,
    CaptureSessionStatus,
    InventoryTotals,
    PreservationBaselineManifest,
)
from poe_backup_orchestrator.models.storage_inventory import (
    STORAGE_INVENTORY_SCHEMA_VERSION,
    PreservationBaselineIdentity,
    SourceAccessibility,
    SourceDevice,
    SourceDeviceType,
    SourceRoot,
    SourceVolume,
)

NOW = datetime(2026, 7, 29, 14, 0, tzinfo=UTC)
LATER = datetime(2026, 7, 29, 14, 30, tzinfo=UTC)


def scope() -> CaptureScope:
    return CaptureScope(
        source_device_ids=("windows-desktop",),
        source_volume_ids=("windows-c",),
        source_root_ids=("documents",),
        include_patterns=("**/*",),
        exclude_patterns=("AppData/Local/Temp/**",),
    )


def totals(
    *,
    captured: int = 2,
    excluded: int = 0,
    inaccessible: int = 0,
    errors: int = 0,
    pending: int = 0,
) -> InventoryTotals:
    return InventoryTotals(
        directory_count=1,
        file_count=captured + excluded + inaccessible + errors + pending - 1,
        symbolic_link_count=0,
        junction_count=0,
        other_item_count=0,
        total_file_bytes=100,
        captured_count=captured,
        excluded_count=excluded,
        inaccessible_count=inaccessible,
        error_count=errors,
        pending_count=pending,
    )


def baseline() -> PreservationBaselineIdentity:
    return PreservationBaselineIdentity(
        schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
        baseline_id="POE-STOR-MIG-BASELINE-20260729",
        created_at_utc=NOW,
        status="READ-ONLY",
        retained_until="MIGRATION_CLOSEOUT",
    )


def device() -> SourceDevice:
    return SourceDevice(
        source_device_id="windows-desktop",
        device_type=SourceDeviceType.WINDOWS_DESKTOP,
        hostname="DESKTOP",
        operating_system="Windows 11",
        registered_at_utc=NOW,
        accessibility=SourceAccessibility.ACCESSIBLE,
    )


def volume() -> SourceVolume:
    return SourceVolume(
        source_volume_id="windows-c",
        source_device_id="windows-desktop",
        volume_label="System",
        volume_identifier="volume-guid",
        filesystem="NTFS",
        mount_point=Path("C:/"),
        capacity_bytes=1_000_000,
        accessibility=SourceAccessibility.ACCESSIBLE,
        observed_at_utc=NOW,
    )


def root() -> SourceRoot:
    return SourceRoot(
        source_root_id="documents",
        source_volume_id="windows-c",
        root_path=Path("C:/Users/Talmadge/Documents"),
        declared_at_utc=NOW,
        accessibility=SourceAccessibility.ACCESSIBLE,
    )


def completed_session() -> CaptureSession:
    return CaptureSession(
        capture_session_id="capture-001",
        baseline_id=baseline().baseline_id,
        status=CaptureSessionStatus.COMPLETED,
        scope=scope(),
        started_at_utc=NOW,
        completed_at_utc=LATER,
        totals=totals(),
    )


def draft_manifest() -> PreservationBaselineManifest:
    return PreservationBaselineManifest(
        schema_version=STORAGE_BASELINE_MANIFEST_SCHEMA_VERSION,
        inventory_schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
        manifest_status=BaselineManifestStatus.DRAFT,
        baseline=baseline(),
        generated_at_utc=LATER,
        devices=(device(),),
        volumes=(volume(),),
        roots=(root(),),
        capture_sessions=(completed_session(),),
        inventory_evidence_path=Path(
            "/srv/poe-backup/Snapshots/Storage-Consolidation/inventory.ndjson"
        ),
    )


def test_capture_scope_rejects_duplicate_identity() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        CaptureScope(
            source_device_ids=("device", "device"),
            source_volume_ids=("volume",),
            source_root_ids=("root",),
        )


def test_inventory_totals_require_status_reconciliation() -> None:
    with pytest.raises(ValueError, match="must equal"):
        InventoryTotals(
            directory_count=1,
            file_count=1,
            symbolic_link_count=0,
            junction_count=0,
            other_item_count=0,
            total_file_bytes=10,
            captured_count=1,
            excluded_count=0,
            inaccessible_count=0,
            error_count=0,
            pending_count=0,
        )


def test_inventory_totals_expose_derived_counts() -> None:
    aggregate = totals(captured=1, excluded=1)

    assert aggregate.item_count == 2
    assert aggregate.exception_count == 1


def test_capture_exception_summary_requires_relative_paths() -> None:
    with pytest.raises(ValueError, match="relative"):
        CaptureExceptionSummary(
            category="permission",
            count=1,
            example_paths=(Path("/absolute/path"),),
        )


def test_planned_session_rejects_execution_timestamp() -> None:
    with pytest.raises(ValueError, match="planned"):
        CaptureSession(
            capture_session_id="capture-001",
            baseline_id=baseline().baseline_id,
            status=CaptureSessionStatus.PLANNED,
            scope=scope(),
            started_at_utc=NOW,
            completed_at_utc=None,
            totals=totals(captured=0, pending=2),
        )


def test_completed_session_rejects_exceptions() -> None:
    with pytest.raises(ValueError, match="cannot contain exceptions"):
        CaptureSession(
            capture_session_id="capture-001",
            baseline_id=baseline().baseline_id,
            status=CaptureSessionStatus.COMPLETED,
            scope=scope(),
            started_at_utc=NOW,
            completed_at_utc=LATER,
            totals=totals(captured=1, excluded=1),
        )


def test_completed_with_exceptions_requires_exception_total() -> None:
    with pytest.raises(ValueError, match="requires at least one"):
        CaptureSession(
            capture_session_id="capture-001",
            baseline_id=baseline().baseline_id,
            status=CaptureSessionStatus.COMPLETED_WITH_EXCEPTIONS,
            scope=scope(),
            started_at_utc=NOW,
            completed_at_utc=LATER,
            totals=totals(),
        )


def test_failed_session_requires_failure_detail() -> None:
    with pytest.raises(ValueError, match="failure_detail"):
        CaptureSession(
            capture_session_id="capture-001",
            baseline_id=baseline().baseline_id,
            status=CaptureSessionStatus.FAILED,
            scope=scope(),
            started_at_utc=NOW,
            completed_at_utc=LATER,
            totals=totals(captured=0, errors=2),
        )


def test_manifest_rejects_unknown_volume_device() -> None:
    invalid_volume = replace(volume(), source_device_id="unknown-device")

    with pytest.raises(ValueError, match="manifest device"):
        PreservationBaselineManifest(
            schema_version=STORAGE_BASELINE_MANIFEST_SCHEMA_VERSION,
            inventory_schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
            manifest_status=BaselineManifestStatus.DRAFT,
            baseline=baseline(),
            generated_at_utc=LATER,
            devices=(device(),),
            volumes=(invalid_volume,),
            roots=(root(),),
            capture_sessions=(completed_session(),),
            inventory_evidence_path=Path("/tmp/inventory.ndjson"),
        )


def test_manifest_rejects_relative_evidence_path() -> None:
    with pytest.raises(ValueError, match="must be absolute"):
        replace(draft_manifest(), inventory_evidence_path=Path("inventory.ndjson"))


def test_canonical_json_is_deterministic() -> None:
    manifest = draft_manifest()

    assert manifest.canonical_json() == manifest.canonical_json()
    assert manifest.calculate_sha256() == manifest.calculate_sha256()
    assert len(manifest.calculate_sha256()) == 64


def test_draft_manifest_rejects_integrity_digest() -> None:
    with pytest.raises(ValueError, match="only certified"):
        replace(draft_manifest(), manifest_sha256="a" * 64)


def test_certified_manifest_requires_digest() -> None:
    with pytest.raises(ValueError, match="require manifest_sha256"):
        replace(
            draft_manifest(),
            manifest_status=BaselineManifestStatus.CERTIFIED,
        )


def test_certified_manifest_accepts_matching_digest() -> None:
    draft = draft_manifest()
    digest = draft.certification_sha256()

    certified = replace(
        draft,
        manifest_status=BaselineManifestStatus.CERTIFIED,
        manifest_sha256=digest,
    )

    assert certified.manifest_sha256 == certified.calculate_sha256()


def test_certified_manifest_rejects_mismatched_digest() -> None:
    with pytest.raises(ValueError, match="does not match"):
        replace(
            draft_manifest(),
            manifest_status=BaselineManifestStatus.CERTIFIED,
            manifest_sha256="a" * 64,
        )
