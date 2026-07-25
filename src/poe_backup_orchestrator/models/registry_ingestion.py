"""Registry acquisition ingestion models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RegistryIngestionResult:
    """Verified result for a Windows Registry acquisition artifact."""

    asset_id: str
    manifest_path: Path
    snapshot_path: Path
    created_at: str
    sha256: str
    size_bytes: int
    integrity_check: str
