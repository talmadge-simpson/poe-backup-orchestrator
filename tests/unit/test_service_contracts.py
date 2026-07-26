"""Tests for normalized orchestration service contracts and adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from poe_backup_orchestrator.exceptions import (
    RegistryAcceptanceError,
    RegistryIngestionError,
    RepositoryValidationError,
    SqliteBackupError,
)
from poe_backup_orchestrator.models import (
    RegistryAcceptanceResult,
    RegistryIngestionResult,
    RepositoryValidationResult,
    SqliteBackupResult,
)
from poe_backup_orchestrator.services import (
    AcquisitionValidationAdapter,
    AcquisitionValidationService,
    RegistryAcceptanceAdapter,
    RegistryAcceptanceService,
    RegistryAcquisitionAdapter,
    RegistryAcquisitionService,
    RepositoryValidationAdapter,
    RepositoryValidationService,
)

NOW = datetime(2026, 7, 26, 16, 0, tzinfo=UTC)


class FixedClock:
    """Clock returning a deterministic timestamp."""

    def now_utc(self) -> datetime:
        return NOW


class FakeRepositoryService:
    """Structurally valid repository service."""

    def validate(self) -> RepositoryValidationResult:
        return cast(RepositoryValidationResult, object())


class FakeAcquisitionService:
    """Structurally valid acquisition service."""

    def acquire(self) -> SqliteBackupResult:
        return cast(SqliteBackupResult, object())


class FakeValidationService:
    """Structurally valid acquisition-validation service."""

    def validate(self, acquisition: SqliteBackupResult) -> RegistryIngestionResult:
        del acquisition
        return cast(RegistryIngestionResult, object())


class FakeAcceptanceService:
    """Structurally valid acceptance service."""

    def accept(
        self,
        validation: RegistryIngestionResult,
    ) -> RegistryAcceptanceResult:
        del validation
        return cast(RegistryAcceptanceResult, object())


@pytest.mark.parametrize(
    ("instance", "contract"),
    [
        (FakeRepositoryService(), RepositoryValidationService),
        (FakeAcquisitionService(), RegistryAcquisitionService),
        (FakeValidationService(), AcquisitionValidationService),
        (FakeAcceptanceService(), RegistryAcceptanceService),
    ],
)
def test_fake_implementations_satisfy_runtime_contracts(
    instance: object,
    contract: type[object],
) -> None:
    assert isinstance(instance, contract)


def test_repository_adapter_delegates_bound_command() -> None:
    expected = cast(RepositoryValidationResult, object())
    calls: list[tuple[str, ...]] = []

    def validator(command) -> RepositoryValidationResult:
        calls.append(tuple(command))
        return expected

    adapter = RepositoryValidationAdapter(
        command=("repository-status", "--json"),
        validator=validator,
    )

    assert isinstance(adapter, RepositoryValidationService)
    assert adapter.validate() is expected
    assert calls == [("repository-status", "--json")]


def test_repository_adapter_propagates_domain_exception() -> None:
    expected = RepositoryValidationError("repository unavailable")

    def validator(command) -> RepositoryValidationResult:
        del command
        raise expected

    adapter = RepositoryValidationAdapter(validator=validator)

    with pytest.raises(RepositoryValidationError) as raised:
        adapter.validate()

    assert raised.value is expected


def test_acquisition_adapter_delegates_bound_dependencies() -> None:
    expected = cast(SqliteBackupResult, object())
    received: dict[str, object] = {}

    def creator(**kwargs) -> SqliteBackupResult:
        received.update(kwargs)
        return expected

    adapter = RegistryAcquisitionAdapter(
        source_path=Path("/source/registry.db"),
        staging_root=Path("/staging"),
        asset_id="poe-registry",
        clock=FixedClock(),
        creator=creator,
    )

    assert isinstance(adapter, RegistryAcquisitionService)
    assert adapter.acquire() is expected
    assert received == {
        "source_path": Path("/source/registry.db"),
        "staging_root": Path("/staging"),
        "asset_id": "poe-registry",
        "created_at": NOW,
    }


def test_acquisition_adapter_propagates_domain_exception() -> None:
    expected = SqliteBackupError("acquisition failed")

    def creator(**kwargs) -> SqliteBackupResult:
        del kwargs
        raise expected

    adapter = RegistryAcquisitionAdapter(
        source_path=Path("/source/registry.db"),
        staging_root=Path("/staging"),
        asset_id="poe-registry",
        clock=FixedClock(),
        creator=creator,
    )

    with pytest.raises(SqliteBackupError) as raised:
        adapter.acquire()

    assert raised.value is expected


@dataclass(frozen=True)
class AcquisitionStub:
    manifest_path: Path


def test_validation_adapter_extracts_manifest_path() -> None:
    expected = cast(RegistryIngestionResult, object())
    manifest_path = Path("/staging/run/registry.manifest.json")
    received: list[Path] = []

    def validator(path: Path) -> RegistryIngestionResult:
        received.append(path)
        return expected

    adapter = AcquisitionValidationAdapter(validator=validator)
    acquisition = cast(SqliteBackupResult, AcquisitionStub(manifest_path))

    assert isinstance(adapter, AcquisitionValidationService)
    assert adapter.validate(acquisition) is expected
    assert received == [manifest_path]


def test_validation_adapter_propagates_domain_exception() -> None:
    expected = RegistryIngestionError("validation failed")

    def validator(path: Path) -> RegistryIngestionResult:
        del path
        raise expected

    adapter = AcquisitionValidationAdapter(validator=validator)
    acquisition = cast(
        SqliteBackupResult,
        AcquisitionStub(Path("/staging/registry.manifest.json")),
    )

    with pytest.raises(RegistryIngestionError) as raised:
        adapter.validate(acquisition)

    assert raised.value is expected


def test_acceptance_adapter_delegates_bound_destination() -> None:
    expected = cast(RegistryAcceptanceResult, object())
    validation = cast(RegistryIngestionResult, object())
    destination_root = Path("/repository/Registry/POERegistry")
    received: list[tuple[RegistryIngestionResult, Path]] = []

    def acceptor(
        result: RegistryIngestionResult,
        destination: Path,
    ) -> RegistryAcceptanceResult:
        received.append((result, destination))
        return expected

    adapter = RegistryAcceptanceAdapter(
        destination_root=destination_root,
        acceptor=acceptor,
    )

    assert isinstance(adapter, RegistryAcceptanceService)
    assert adapter.accept(validation) is expected
    assert received == [(validation, destination_root)]


def test_acceptance_adapter_propagates_domain_exception() -> None:
    expected = RegistryAcceptanceError("acceptance failed")
    validation = cast(RegistryIngestionResult, object())

    def acceptor(
        result: RegistryIngestionResult,
        destination: Path,
    ) -> RegistryAcceptanceResult:
        del result, destination
        raise expected

    adapter = RegistryAcceptanceAdapter(
        destination_root=Path("/repository/Registry/POERegistry"),
        acceptor=acceptor,
    )

    with pytest.raises(RegistryAcceptanceError) as raised:
        adapter.accept(validation)

    assert raised.value is expected
