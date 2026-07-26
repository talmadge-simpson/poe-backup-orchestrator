"""Orchestration-facing service contracts."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from poe_backup_orchestrator.models import (
    RegistryAcceptanceResult,
    RegistryIngestionResult,
    RepositoryValidationResult,
    SqliteBackupResult,
)


@runtime_checkable
class RepositoryValidationService(Protocol):
    """Validate readiness of the managed backup repository."""

    def validate(self) -> RepositoryValidationResult:
        """Return the repository readiness result."""


@runtime_checkable
class RegistryAcquisitionService(Protocol):
    """Create a consistent Registry acquisition artifact."""

    def acquire(self) -> SqliteBackupResult:
        """Return the created Registry acquisition result."""


@runtime_checkable
class AcquisitionValidationService(Protocol):
    """Validate a created Registry acquisition."""

    def validate(self, acquisition: SqliteBackupResult) -> RegistryIngestionResult:
        """Return validated acquisition evidence."""


@runtime_checkable
class RegistryAcceptanceService(Protocol):
    """Promote a validated Registry acquisition into the repository."""

    def accept(
        self,
        validation: RegistryIngestionResult,
    ) -> RegistryAcceptanceResult:
        """Return the repository acceptance result."""
