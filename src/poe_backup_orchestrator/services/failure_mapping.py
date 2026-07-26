"""Deterministic mapping of expected operational exceptions."""

from __future__ import annotations

from dataclasses import dataclass

from poe_backup_orchestrator.exceptions import (
    ConfigurationError,
    OrchestratorError,
    RegistryAcceptanceConflictError,
    RegistryAcceptanceError,
    RegistryAcceptanceInconsistentError,
    RegistryAcceptanceLockError,
    RegistryIngestionError,
    RepositoryValidationError,
    SqliteBackupError,
)
from poe_backup_orchestrator.models import (
    ExecutionFailure,
    ExecutionState,
    FailureCategory,
)


@dataclass(frozen=True, slots=True)
class FailurePolicy:
    """Stable policy applied to one classified operational exception."""

    category: FailureCategory
    retryable: bool
    exit_code: int


_FAILURE_POLICIES: tuple[tuple[type[OrchestratorError], FailurePolicy], ...] = (
    (
        RegistryAcceptanceLockError,
        FailurePolicy(
            category=FailureCategory.LOCK_UNAVAILABLE,
            retryable=True,
            exit_code=50,
        ),
    ),
    (
        RegistryAcceptanceConflictError,
        FailurePolicy(
            category=FailureCategory.ACCEPTANCE_CONFLICT,
            retryable=False,
            exit_code=51,
        ),
    ),
    (
        RegistryAcceptanceInconsistentError,
        FailurePolicy(
            category=FailureCategory.ACCEPTANCE,
            retryable=False,
            exit_code=52,
        ),
    ),
    (
        RepositoryValidationError,
        FailurePolicy(
            category=FailureCategory.REPOSITORY_PRECONDITION,
            retryable=False,
            exit_code=20,
        ),
    ),
    (
        SqliteBackupError,
        FailurePolicy(
            category=FailureCategory.ACQUISITION,
            retryable=True,
            exit_code=30,
        ),
    ),
    (
        RegistryIngestionError,
        FailurePolicy(
            category=FailureCategory.VALIDATION,
            retryable=False,
            exit_code=40,
        ),
    ),
    (
        RegistryAcceptanceError,
        FailurePolicy(
            category=FailureCategory.ACCEPTANCE,
            retryable=False,
            exit_code=53,
        ),
    ),
    (
        ConfigurationError,
        FailurePolicy(
            category=FailureCategory.CONFIGURATION,
            retryable=False,
            exit_code=10,
        ),
    ),
)


def map_operational_failure(
    error: OrchestratorError,
    *,
    failed_state: ExecutionState,
) -> ExecutionFailure:
    """Map one known operational exception to a structured failure."""

    for exception_type, policy in _FAILURE_POLICIES:
        if isinstance(error, exception_type):
            return ExecutionFailure(
                category=policy.category,
                failed_state=failed_state,
                error_type=type(error).__name__,
                message=str(error),
                retryable=policy.retryable,
                exit_code=policy.exit_code,
            )

    raise TypeError(f"no operational failure mapping for {type(error).__name__}")
