"""Typed configuration models for the POE Backup Orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ApplicationConfig:
    """Application identity and environment settings."""

    name: str
    environment: str


@dataclass(frozen=True)
class PathConfig:
    """Filesystem paths used by the orchestrator."""

    repository_root: Path
    staging_root: Path
    reports_root: Path
    logs_root: Path
    restore_tests_root: Path
    quarantine_root: Path


@dataclass(frozen=True)
class OrchestratorConfig:
    """Complete validated application configuration."""

    application: ApplicationConfig
    paths: PathConfig
