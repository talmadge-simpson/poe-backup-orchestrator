"""Tests for read-only filesystem discovery contracts and adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_discovery import (
    STORAGE_DISCOVERY_SCHEMA_VERSION,
    DiscoveredFilesystemEntry,
    DiscoveryEntryType,
    DiscoveryException,
    DiscoveryExceptionCode,
    DiscoveryPolicy,
    DiscoveryStatus,
    FilesystemDiscoveryRequest,
    FilesystemDiscoveryResult,
)
from poe_backup_orchestrator.services.storage_discovery import (
    LocalFilesystemDiscoveryAdapter,
)

NOW = datetime(2026, 7, 29, 15, 0, tzinfo=UTC)
LATER = datetime(2026, 7, 29, 15, 1, tzinfo=UTC)


class FixedClock:
    def __init__(self) -> None:
        self._values = iter((NOW, LATER))

    def __call__(self) -> datetime:
        return next(self._values)


def request(root: Path, *, policy: DiscoveryPolicy | None = None) -> FilesystemDiscoveryRequest:
    return FilesystemDiscoveryRequest(
        discovery_request_id="discovery-001",
        source_root_id="root-001",
        root_path=root,
        requested_at_utc=NOW,
        policy=policy or DiscoveryPolicy(),
    )


def test_request_requires_absolute_root() -> None:
    with pytest.raises(ValueError, match="absolute"):
        request(Path("relative/root"))


def test_policy_rejects_negative_max_depth() -> None:
    with pytest.raises(ValueError, match="zero or greater"):
        DiscoveryPolicy(max_depth=-1)


def test_file_entry_requires_size() -> None:
    with pytest.raises(ValueError, match="require size_bytes"):
        DiscoveredFilesystemEntry(
            source_root_id="root-001",
            relative_path=Path("file.txt"),
            entry_type=DiscoveryEntryType.FILE,
            size_bytes=None,
            modified_at_utc=NOW,
            mode=0o644,
            is_hidden=False,
        )


def test_non_file_entry_rejects_size() -> None:
    with pytest.raises(ValueError, match="only file entries"):
        DiscoveredFilesystemEntry(
            source_root_id="root-001",
            relative_path=Path("folder"),
            entry_type=DiscoveryEntryType.DIRECTORY,
            size_bytes=1,
            modified_at_utc=NOW,
            mode=0o755,
            is_hidden=False,
        )


def test_result_requires_deterministic_entry_order(tmp_path: Path) -> None:
    entries = (
        DiscoveredFilesystemEntry(
            source_root_id="root-001",
            relative_path=Path("z.txt"),
            entry_type=DiscoveryEntryType.FILE,
            size_bytes=1,
            modified_at_utc=NOW,
            mode=0o644,
            is_hidden=False,
        ),
        DiscoveredFilesystemEntry(
            source_root_id="root-001",
            relative_path=Path("a.txt"),
            entry_type=DiscoveryEntryType.FILE,
            size_bytes=1,
            modified_at_utc=NOW,
            mode=0o644,
            is_hidden=False,
        ),
    )

    with pytest.raises(ValueError, match="ordered"):
        FilesystemDiscoveryResult(
            schema_version=STORAGE_DISCOVERY_SCHEMA_VERSION,
            discovery_request_id="discovery-001",
            source_root_id="root-001",
            root_path=tmp_path,
            started_at_utc=NOW,
            completed_at_utc=LATER,
            status=DiscoveryStatus.COMPLETED,
            entries=entries,
            exceptions=(),
        )


def test_completed_result_rejects_exceptions(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot contain exceptions"):
        FilesystemDiscoveryResult(
            schema_version=STORAGE_DISCOVERY_SCHEMA_VERSION,
            discovery_request_id="discovery-001",
            source_root_id="root-001",
            root_path=tmp_path,
            started_at_utc=NOW,
            completed_at_utc=LATER,
            status=DiscoveryStatus.COMPLETED,
            entries=(),
            exceptions=(
                DiscoveryException(
                    code=DiscoveryExceptionCode.FILESYSTEM_ERROR,
                    relative_path=None,
                    detail="error",
                ),
            ),
        )


def test_missing_root_returns_failed_result(tmp_path: Path) -> None:
    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())

    result = adapter.discover(request(tmp_path / "missing"))

    assert result.status is DiscoveryStatus.FAILED
    assert result.entries == ()
    assert result.exceptions[0].code is DiscoveryExceptionCode.ROOT_NOT_FOUND


def test_file_root_returns_failed_result(tmp_path: Path) -> None:
    source_file = tmp_path / "source.txt"
    source_file.write_text("content", encoding="utf-8")
    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())

    result = adapter.discover(request(source_file))

    assert result.status is DiscoveryStatus.FAILED
    assert result.exceptions[0].code is DiscoveryExceptionCode.ROOT_NOT_DIRECTORY


def test_discovery_returns_sorted_relative_entries(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_text("z", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "child.txt").write_text("child", encoding="utf-8")

    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())
    result = adapter.discover(request(tmp_path))

    assert result.status is DiscoveryStatus.COMPLETED
    assert [entry.relative_path.as_posix() for entry in result.entries] == [
        "a.txt",
        "folder",
        "folder/child.txt",
        "z.txt",
    ]
    assert [entry.entry_type for entry in result.entries] == [
        DiscoveryEntryType.FILE,
        DiscoveryEntryType.DIRECTORY,
        DiscoveryEntryType.FILE,
        DiscoveryEntryType.FILE,
    ]


def test_discovery_can_exclude_hidden_entries(tmp_path: Path) -> None:
    (tmp_path / ".hidden").write_text("hidden", encoding="utf-8")
    (tmp_path / "visible").write_text("visible", encoding="utf-8")

    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())
    result = adapter.discover(request(tmp_path, policy=DiscoveryPolicy(include_hidden=False)))

    assert [entry.relative_path.as_posix() for entry in result.entries] == ["visible"]


def test_symlink_is_recorded_without_traversal(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    (target / "inside.txt").write_text("inside", encoding="utf-8")
    link = tmp_path / "link"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("Symbolic links are unavailable in this test environment")

    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())
    result = adapter.discover(request(tmp_path))

    entries = {entry.relative_path.as_posix(): entry.entry_type for entry in result.entries}
    assert entries["link"] is DiscoveryEntryType.SYMBOLIC_LINK
    assert "link/inside.txt" not in entries
    assert entries["target/inside.txt"] is DiscoveryEntryType.FILE


def test_max_depth_records_exception_and_stops_descent(tmp_path: Path) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    nested = folder / "nested"
    nested.mkdir()
    (nested / "file.txt").write_text("content", encoding="utf-8")

    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())
    result = adapter.discover(request(tmp_path, policy=DiscoveryPolicy(max_depth=0)))

    assert result.status is DiscoveryStatus.COMPLETED_WITH_EXCEPTIONS
    assert [entry.relative_path.as_posix() for entry in result.entries] == ["folder"]
    assert result.exceptions[0].code is DiscoveryExceptionCode.MAX_DEPTH_REACHED
    assert result.exceptions[0].relative_path == Path("folder")


def test_discovery_does_not_modify_source_content(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    original = b"preserve exactly"
    source.write_bytes(original)
    before_stat = source.stat()

    adapter = LocalFilesystemDiscoveryAdapter(clock=FixedClock())
    result = adapter.discover(request(tmp_path))

    after_stat = source.stat()
    assert result.status is DiscoveryStatus.COMPLETED
    assert source.read_bytes() == original
    assert after_stat.st_size == before_stat.st_size
    assert after_stat.st_mtime_ns == before_stat.st_mtime_ns
