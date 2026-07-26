"""Tests for reusable Linux file-locking primitives."""

from __future__ import annotations

from pathlib import Path

import pytest

from poe_backup_orchestrator.utilities.locking import (
    LockContentionError,
    exclusive_file_lock,
)


def test_exclusive_file_lock_creates_parent_and_lock_file(tmp_path: Path) -> None:
    lock_path = tmp_path / "locks" / "repository.lock"

    with exclusive_file_lock(lock_path) as acquired_path:
        assert acquired_path == lock_path.resolve()
        assert lock_path.is_file()


def test_exclusive_file_lock_rejects_contention(tmp_path: Path) -> None:
    lock_path = tmp_path / "repository.lock"

    with exclusive_file_lock(lock_path):
        with pytest.raises(LockContentionError, match="already held"):
            with exclusive_file_lock(lock_path):
                pass


def test_exclusive_file_lock_releases_after_success(tmp_path: Path) -> None:
    lock_path = tmp_path / "repository.lock"

    with exclusive_file_lock(lock_path):
        pass

    with exclusive_file_lock(lock_path):
        pass


def test_exclusive_file_lock_releases_after_exception(tmp_path: Path) -> None:
    lock_path = tmp_path / "repository.lock"

    with pytest.raises(RuntimeError, match="forced failure"):
        with exclusive_file_lock(lock_path):
            raise RuntimeError("forced failure")

    with exclusive_file_lock(lock_path):
        pass


def test_exclusive_file_lock_reuses_stale_lock_file(tmp_path: Path) -> None:
    lock_path = tmp_path / "repository.lock"
    lock_path.write_text("stale metadata\n", encoding="utf-8")

    with exclusive_file_lock(lock_path):
        assert lock_path.is_file()


def test_exclusive_file_lock_isolates_distinct_lock_paths(tmp_path: Path) -> None:
    first_lock = tmp_path / "first.lock"
    second_lock = tmp_path / "second.lock"

    with exclusive_file_lock(first_lock):
        with exclusive_file_lock(second_lock):
            assert first_lock.is_file()
            assert second_lock.is_file()
