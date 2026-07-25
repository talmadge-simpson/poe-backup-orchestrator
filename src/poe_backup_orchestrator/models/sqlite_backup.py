"""SQLite backup result models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SqliteBackupResult:
    """Evidence returned after a successful consistent SQLite backup."""

    asset_id: str
    source_path: Path
    backup_path: Path
    manifest_path: Path
    sha256: str
    size_bytes: int
    integrity_check: str
    created_at: str
