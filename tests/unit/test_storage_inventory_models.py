"""Tests for immutable storage source-identity and inventory contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_inventory import (
    STORAGE_INVENTORY_SCHEMA_VERSION,
    DirectoryInventoryRecord,
    FileInventoryRecord,
    InventoryCaptureStatus,
    InventoryItemIdentity,
    InventoryItemType,
    InventoryMetadata,
    PreservationBaselineIdentity,
    SourceAccessibility,
    SourceDevice,
    SourceDeviceType,
    SourceRoot,
    SourceVolume,
)

NOW = datetime(2026, 7, 29, 12, 0, tzinfo=UTC)
SHA256 = "a" * 64


def metadata() -> InventoryMetadata:
    return InventoryMetadata(
        created_at_utc=NOW,
        modified_at_utc=NOW,
        accessed_at_utc=None,
        owner="talmadge",
        permissions="0644",
    )


def file_identity() -> InventoryItemIdentity:
    return InventoryItemIdentity(
        baseline_id="POE-STOR-MIG-BASELINE-20260729",
        capture_session_id="capture-001",
        source_device_id="windows-desktop",
        source_volume_id="windows-c",
        source_root_id="documents",
        relative_path=Path("Projects/example.txt"),
        item_type=InventoryItemType.FILE,
    )


def directory_identity() -> InventoryItemIdentity:
    return InventoryItemIdentity(
        baseline_id="POE-STOR-MIG-BASELINE-20260729",
        capture_session_id="capture-001",
        source_device_id="windows-desktop",
        source_volume_id="windows-c",
        source_root_id="documents",
        relative_path=Path("Projects"),
        item_type=InventoryItemType.DIRECTORY,
    )


def test_source_device_normalizes_text() -> None:
    device = SourceDevice(
        source_device_id=" windows-desktop ",
        device_type=SourceDeviceType.WINDOWS_DESKTOP,
        hostname=" DESKTOP ",
        operating_system=" Windows 11 ",
        registered_at_utc=NOW,
        accessibility=SourceAccessibility.ACCESSIBLE,
        description=" Primary workstation ",
    )

    assert device.source_device_id == "windows-desktop"
    assert device.hostname == "DESKTOP"
    assert device.operating_system == "Windows 11"
    assert device.description == "Primary workstation"


def test_source_device_rejects_non_utc_timestamp() -> None:
    with pytest.raises(ValueError, match="registered_at_utc"):
        SourceDevice(
            source_device_id="windows-desktop",
            device_type=SourceDeviceType.WINDOWS_DESKTOP,
            hostname="DESKTOP",
            operating_system="Windows 11",
            registered_at_utc=datetime(2026, 7, 29, 12, 0),
            accessibility=SourceAccessibility.ACCESSIBLE,
        )


def test_source_volume_rejects_negative_capacity() -> None:
    with pytest.raises(ValueError, match="capacity_bytes"):
        SourceVolume(
            source_volume_id="windows-c",
            source_device_id="windows-desktop",
            volume_label="System",
            volume_identifier="volume-guid",
            filesystem="NTFS",
            mount_point=Path("C:/"),
            capacity_bytes=-1,
            accessibility=SourceAccessibility.ACCESSIBLE,
            observed_at_utc=NOW,
        )


def test_source_root_converts_path() -> None:
    root = SourceRoot(
        source_root_id="documents",
        source_volume_id="windows-c",
        root_path="C:/Users/Talmadge/Documents",
        declared_at_utc=NOW,
        accessibility=SourceAccessibility.ACCESSIBLE,
    )

    assert isinstance(root.root_path, Path)


def test_inventory_identity_rejects_absolute_relative_path() -> None:
    with pytest.raises(ValueError, match="relative_path must not be absolute"):
        InventoryItemIdentity(
            baseline_id="baseline",
            capture_session_id="capture",
            source_device_id="device",
            source_volume_id="volume",
            source_root_id="root",
            relative_path=Path("/absolute/file.txt"),
            item_type=InventoryItemType.FILE,
        )


def test_captured_file_requires_sha256() -> None:
    with pytest.raises(ValueError, match="require sha256"):
        FileInventoryRecord(
            identity=file_identity(),
            size_bytes=10,
            sha256=None,
            metadata=metadata(),
            capture_status=InventoryCaptureStatus.CAPTURED,
        )


def test_captured_file_normalizes_sha256() -> None:
    record = FileInventoryRecord(
        identity=file_identity(),
        size_bytes=10,
        sha256=SHA256.upper(),
        metadata=metadata(),
        capture_status=InventoryCaptureStatus.CAPTURED,
    )

    assert record.sha256 == SHA256


def test_excluded_file_requires_reason() -> None:
    with pytest.raises(ValueError, match="exclusion_reason"):
        FileInventoryRecord(
            identity=file_identity(),
            size_bytes=10,
            sha256=None,
            metadata=metadata(),
            capture_status=InventoryCaptureStatus.EXCLUDED,
        )


def test_inaccessible_file_requires_error_detail() -> None:
    with pytest.raises(ValueError, match="error_detail"):
        FileInventoryRecord(
            identity=file_identity(),
            size_bytes=10,
            sha256=None,
            metadata=metadata(),
            capture_status=InventoryCaptureStatus.INACCESSIBLE,
        )


def test_pending_file_rejects_terminal_evidence() -> None:
    with pytest.raises(ValueError, match="terminal capture evidence"):
        FileInventoryRecord(
            identity=file_identity(),
            size_bytes=10,
            sha256=SHA256,
            metadata=metadata(),
            capture_status=InventoryCaptureStatus.PENDING,
        )


def test_directory_rejects_direct_count_larger_than_descendant_count() -> None:
    with pytest.raises(ValueError, match="direct_file_count"):
        DirectoryInventoryRecord(
            identity=directory_identity(),
            metadata=metadata(),
            direct_file_count=2,
            direct_directory_count=0,
            descendant_file_count=1,
            descendant_directory_count=0,
            descendant_size_bytes=10,
            capture_status=InventoryCaptureStatus.CAPTURED,
        )


def test_directory_requires_directory_identity() -> None:
    with pytest.raises(ValueError, match="item_type DIRECTORY"):
        DirectoryInventoryRecord(
            identity=file_identity(),
            metadata=metadata(),
            direct_file_count=0,
            direct_directory_count=0,
            descendant_file_count=0,
            descendant_directory_count=0,
            descendant_size_bytes=0,
            capture_status=InventoryCaptureStatus.CAPTURED,
        )


def test_preservation_baseline_identity_accepts_governed_contract() -> None:
    baseline = PreservationBaselineIdentity(
        schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
        baseline_id="POE-STOR-MIG-BASELINE-20260729",
        created_at_utc=NOW,
        status="READ-ONLY",
        retained_until="MIGRATION_CLOSEOUT",
    )

    assert baseline.status == "READ-ONLY"
    assert baseline.retained_until == "MIGRATION_CLOSEOUT"


def test_preservation_baseline_rejects_wrong_schema_version() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        PreservationBaselineIdentity(
            schema_version="2.0",
            baseline_id="baseline",
            created_at_utc=NOW,
            status="READ-ONLY",
            retained_until="MIGRATION_CLOSEOUT",
        )
