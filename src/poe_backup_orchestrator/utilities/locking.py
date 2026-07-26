"""Reusable non-blocking Linux file-locking primitives."""

from __future__ import annotations

import fcntl
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class LockingError(Exception):
    """Base exception for reusable file-locking failures."""


class LockContentionError(LockingError):
    """Raised when an exclusive non-blocking lock is already held."""


@contextmanager
def exclusive_file_lock(lock_path: Path) -> Iterator[Path]:
    """Acquire an exclusive, non-blocking advisory lock.

    The lock file may persist after use. Active ownership is determined by the
    kernel-managed advisory lock, not by the existence of the file itself.
    """

    lock_path = lock_path.resolve()
    lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o770)

    try:
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o660)
    except OSError as exc:
        raise LockingError(f"Unable to open lock file {lock_path}: {exc}") from exc

    acquired = False
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            acquired = True
        except BlockingIOError as exc:
            raise LockContentionError(f"Lock is already held: {lock_path}") from exc
        except OSError as exc:
            raise LockingError(f"Unable to acquire lock {lock_path}: {exc}") from exc

        yield lock_path
    finally:
        if acquired:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            except OSError:
                pass
        os.close(descriptor)
