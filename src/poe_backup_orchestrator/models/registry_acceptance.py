"""Typed results for Registry acquisition acceptance."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class RegistryAcceptanceStatus(StrEnum):
    """Successful Registry acceptance outcomes."""

    ACCEPTED = "ACCEPTED"
    ALREADY_ACCEPTED = "ALREADY_ACCEPTED"


@dataclass(frozen=True, slots=True)
class RegistryAcceptanceResult:
    """Result returned after successful repository acceptance."""

    asset_id: str
    run_id: str
    destination_directory: Path
    snapshot_path: Path
    manifest_path: Path
    sha256: str
    size_bytes: int
    status: RegistryAcceptanceStatus
