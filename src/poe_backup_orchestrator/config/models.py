"""Typed configuration models for the POE Backup Orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from poe_backup_orchestrator.models.runtime import RuntimeEnvironment


@dataclass(frozen=True)
class ApplicationConfig:
    name: str
    environment: RuntimeEnvironment


@dataclass(frozen=True)
class PathConfig:
    repository_root: Path
    staging_root: Path
    reports_root: Path
    logs_root: Path
    restore_tests_root: Path
    quarantine_root: Path


@dataclass(frozen=True)
class OrchestratorConfig:
    application: ApplicationConfig
    paths: PathConfig
