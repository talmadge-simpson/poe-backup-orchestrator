"""Thin adapters binding orchestration dependencies to existing services."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from poe_backup_orchestrator.models import (
    Clock,
    RegistryAcceptanceResult,
    RegistryIngestionResult,
    RepositoryValidationResult,
    SqliteBackupResult,
)
from poe_backup_orchestrator.services.registry_acceptance import (
    accept_registry_acquisition,
)
from poe_backup_orchestrator.services.registry_ingestion import (
    validate_registry_acquisition,
)
from poe_backup_orchestrator.services.repository_validation import (
    DEFAULT_REPOSITORY_COMMAND,
    validate_repository,
)
from poe_backup_orchestrator.services.sqlite_backup import create_sqlite_backup

RepositoryValidator = Callable[[Sequence[str]], RepositoryValidationResult]
AcquisitionCreator = Callable[..., SqliteBackupResult]
AcquisitionValidator = Callable[[Path], RegistryIngestionResult]
AcquisitionAcceptor = Callable[
    [RegistryIngestionResult, Path],
    RegistryAcceptanceResult,
]


@dataclass(frozen=True, slots=True)
class RepositoryValidationAdapter:
    """Bind the approved repository command to repository validation."""

    command: Sequence[str] = DEFAULT_REPOSITORY_COMMAND
    validator: RepositoryValidator = validate_repository

    def validate(self) -> RepositoryValidationResult:
        """Delegate repository validation without changing its result."""

        return self.validator(self.command)


@dataclass(frozen=True, slots=True)
class RegistryAcquisitionAdapter:
    """Bind source, staging, identity, and time dependencies to acquisition."""

    source_path: Path
    staging_root: Path
    asset_id: str
    clock: Clock
    creator: AcquisitionCreator = create_sqlite_backup

    def acquire(self) -> SqliteBackupResult:
        """Delegate Registry acquisition without changing its result."""

        return self.creator(
            source_path=self.source_path,
            staging_root=self.staging_root,
            asset_id=self.asset_id,
            created_at=self.clock.now_utc(),
        )


@dataclass(frozen=True, slots=True)
class AcquisitionValidationAdapter:
    """Adapt an acquisition result to manifest-based validation."""

    validator: AcquisitionValidator = validate_registry_acquisition

    def validate(self, acquisition: SqliteBackupResult) -> RegistryIngestionResult:
        """Validate the manifest produced by the acquisition stage."""

        return self.validator(acquisition.manifest_path)


@dataclass(frozen=True, slots=True)
class RegistryAcceptanceAdapter:
    """Bind the repository destination to Registry acceptance."""

    destination_root: Path
    acceptor: AcquisitionAcceptor = accept_registry_acquisition

    def accept(
        self,
        validation: RegistryIngestionResult,
    ) -> RegistryAcceptanceResult:
        """Delegate Registry acceptance without changing its result."""

        return self.acceptor(validation, self.destination_root)
