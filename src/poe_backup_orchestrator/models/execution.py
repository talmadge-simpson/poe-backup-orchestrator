"""Execution-state, outcome, failure, and result models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from poe_backup_orchestrator.models.evidence import EvidenceReference
from poe_backup_orchestrator.models.job import JobId, require_utc


class ExecutionState(StrEnum):
    """Lifecycle states for one Registry backup execution."""

    CREATED = "created"
    LOCK_ACQUISITION = "lock_acquisition"
    REPOSITORY_VALIDATION = "repository_validation"
    REGISTRY_ACQUISITION = "registry_acquisition"
    ACQUISITION_VALIDATION = "acquisition_validation"
    REGISTRY_ACCEPTANCE = "registry_acceptance"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionOutcome(StrEnum):
    """Final orchestration outcomes."""

    SUCCEEDED = "succeeded"
    SUCCEEDED_IDEMPOTENT = "succeeded_idempotent"
    FAILED = "failed"


class FailureCategory(StrEnum):
    """Stable categories for execution failures."""

    CONFIGURATION = "configuration"
    LOCK_UNAVAILABLE = "lock_unavailable"
    REPOSITORY_PRECONDITION = "repository_precondition"
    ACQUISITION = "acquisition"
    VALIDATION = "validation"
    ACCEPTANCE_CONFLICT = "acceptance_conflict"
    ACCEPTANCE = "acceptance"
    REPORTING = "reporting"
    CLEANUP = "cleanup"
    INTERNAL = "internal"


@dataclass(frozen=True, slots=True)
class ExecutionFailure:
    """Structured representation of an orchestration failure."""

    category: FailureCategory
    failed_state: ExecutionState
    error_type: str
    message: str
    retryable: bool
    exit_code: int

    def __post_init__(self) -> None:
        error_type = self.error_type.strip()
        message = self.message.strip()

        if not error_type:
            raise ValueError("error_type must not be empty")
        if not message:
            raise ValueError("failure message must not be empty")
        if self.exit_code <= 0:
            raise ValueError("failure exit_code must be greater than zero")
        if self.failed_state in {ExecutionState.COMPLETED, ExecutionState.FAILED}:
            raise ValueError("failed_state must identify the operational state that failed")

        object.__setattr__(self, "error_type", error_type)
        object.__setattr__(self, "message", message)


@dataclass(frozen=True, slots=True)
class RegistryBackupExecutionResult:
    """Immutable public result for one Registry backup execution.

    Component result fields intentionally accept service-specific result objects.
    Their concrete protocols will be normalized in Slice 3C.
    """

    job_id: JobId
    outcome: ExecutionOutcome
    started_at_utc: datetime
    completed_at_utc: datetime
    duration_ms: int
    final_state: ExecutionState
    repository: Any | None = None
    acquisition: Any | None = None
    validation: Any | None = None
    acceptance: Any | None = None
    report: Any | None = None
    evidence: tuple[EvidenceReference, ...] = ()
    warnings: tuple[str, ...] = ()
    failure: ExecutionFailure | None = None

    def __post_init__(self) -> None:
        require_utc(self.started_at_utc, field_name="started_at_utc")
        require_utc(self.completed_at_utc, field_name="completed_at_utc")

        if self.completed_at_utc < self.started_at_utc:
            raise ValueError("completed_at_utc must not precede started_at_utc")
        if self.duration_ms < 0:
            raise ValueError("duration_ms must not be negative")

        object.__setattr__(self, "evidence", tuple(self.evidence))
        object.__setattr__(self, "warnings", tuple(self.warnings))

        if self.outcome is ExecutionOutcome.FAILED:
            self._validate_failed_result()
        else:
            self._validate_successful_result()

    def _validate_successful_result(self) -> None:
        if self.final_state is not ExecutionState.COMPLETED:
            raise ValueError("successful result must have final_state COMPLETED")
        if self.failure is not None:
            raise ValueError("successful result must not include failure")
        if self.repository is None:
            raise ValueError("successful result must include repository result")
        if self.acquisition is None:
            raise ValueError("successful result must include acquisition result")
        if self.validation is None:
            raise ValueError("successful result must include validation result")
        if self.acceptance is None:
            raise ValueError("successful result must include acceptance result")

    def _validate_failed_result(self) -> None:
        if self.final_state is not ExecutionState.FAILED:
            raise ValueError("failed result must have final_state FAILED")
        if self.failure is None:
            raise ValueError("failed result must include failure")
