"""Typed results for Registry acquisition acceptance."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RegistryAcceptanceResult:
    """Result returned after successful repository promotion."""

    asset_id: str
    run_id: str
    destination_directory: Path
    snapshot_path: Path
    manifest_path: Path
    sha256: str
    size_bytes: int
