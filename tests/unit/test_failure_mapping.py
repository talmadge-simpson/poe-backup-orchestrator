"""Tests for operational exception classification."""

from __future__ import annotations

import pytest

from poe_backup_orchestrator.exceptions import (
    BootstrapError,
    ConfigurationError,
    RegistryAcceptanceConflictError,
    RegistryAcceptanceError,
    RegistryAcceptanceInconsistentError,
    RegistryAcceptanceLockError,
    RegistryIngestionError,
    RepositoryValidationError,
    SqliteBackupError,
)
from poe_backup_orchestrator.models import ExecutionState, FailureCategory
from poe_backup_orchestrator.services import map_operational_failure


@pytest.mark.parametrize(
    (
        "error",
        "failed_state",
        "category",
        "retryable",
        "exit_code",
    ),
    [
        (
            ConfigurationError("configuration invalid"),
            ExecutionState.CREATED,
            FailureCategory.CONFIGURATION,
            False,
            10,
        ),
        (
            RepositoryValidationError("repository unavailable"),
            ExecutionState.REPOSITORY_VALIDATION,
            FailureCategory.REPOSITORY_PRECONDITION,
            False,
            20,
        ),
        (
            SqliteBackupError("backup failed"),
            ExecutionState.REGISTRY_ACQUISITION,
            FailureCategory.ACQUISITION,
            True,
            30,
        ),
        (
            RegistryIngestionError("validation failed"),
            ExecutionState.ACQUISITION_VALIDATION,
            FailureCategory.VALIDATION,
            False,
            40,
        ),
        (
            RegistryAcceptanceLockError("acceptance lock unavailable"),
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.LOCK_UNAVAILABLE,
            True,
            50,
        ),
        (
            RegistryAcceptanceConflictError("acceptance conflict"),
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.ACCEPTANCE_CONFLICT,
            False,
            51,
        ),
        (
            RegistryAcceptanceInconsistentError("destination inconsistent"),
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.ACCEPTANCE,
            False,
            52,
        ),
        (
            RegistryAcceptanceError("acceptance failed"),
            ExecutionState.REGISTRY_ACCEPTANCE,
            FailureCategory.ACCEPTANCE,
            False,
            53,
        ),
    ],
)
def test_map_operational_failure(
    error,
    failed_state,
    category,
    retryable,
    exit_code,
) -> None:
    failure = map_operational_failure(
        error,
        failed_state=failed_state,
    )

    assert failure.category is category
    assert failure.failed_state is failed_state
    assert failure.error_type == type(error).__name__
    assert failure.message == str(error)
    assert failure.retryable is retryable
    assert failure.exit_code == exit_code


def test_specific_acceptance_mapping_precedes_base_mapping() -> None:
    failure = map_operational_failure(
        RegistryAcceptanceConflictError("conflict"),
        failed_state=ExecutionState.REGISTRY_ACCEPTANCE,
    )

    assert failure.category is FailureCategory.ACCEPTANCE_CONFLICT
    assert failure.exit_code == 51


def test_unmapped_orchestrator_error_is_rejected() -> None:
    error = BootstrapError("bootstrap failed")

    with pytest.raises(TypeError, match="BootstrapError"):
        map_operational_failure(
            error,
            failed_state=ExecutionState.CREATED,
        )
