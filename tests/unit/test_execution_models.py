"""Tests for orchestration execution models."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from poe_backup_orchestrator.models import (
    EvidenceReference,
    EvidenceType,
    ExecutionFailure,
    ExecutionOutcome,
    ExecutionState,
    FailureCategory,
    JobId,
    RegistryBackupExecutionResult,
)

STARTED = datetime(2026, 7, 26, 14, 0, tzinfo=UTC)
COMPLETED = datetime(2026, 7, 26, 14, 0, 1, tzinfo=UTC)


def successful_result(
    *,
    outcome: ExecutionOutcome = ExecutionOutcome.SUCCEEDED,
) -> RegistryBackupExecutionResult:
    return RegistryBackupExecutionResult(
        job_id=JobId("job-123"),
        outcome=outcome,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=1000,
        final_state=ExecutionState.COMPLETED,
        repository=object(),
        acquisition=object(),
        validation=object(),
        acceptance=object(),
    )


def failure() -> ExecutionFailure:
    return ExecutionFailure(
        category=FailureCategory.VALIDATION,
        failed_state=ExecutionState.ACQUISITION_VALIDATION,
        error_type="RegistryValidationError",
        message="Registry validation failed",
        retryable=False,
        exit_code=30,
    )


def test_successful_result_accepts_complete_contract() -> None:
    result = successful_result()

    assert result.outcome is ExecutionOutcome.SUCCEEDED
    assert result.final_state is ExecutionState.COMPLETED
    assert result.failure is None


def test_idempotent_result_is_successful() -> None:
    result = successful_result(outcome=ExecutionOutcome.SUCCEEDED_IDEMPOTENT)

    assert result.outcome is ExecutionOutcome.SUCCEEDED_IDEMPOTENT
    assert result.failure is None


def test_failed_result_preserves_prior_component_results() -> None:
    result = RegistryBackupExecutionResult(
        job_id=JobId("job-123"),
        outcome=ExecutionOutcome.FAILED,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=1000,
        final_state=ExecutionState.FAILED,
        repository=object(),
        acquisition=object(),
        failure=failure(),
    )

    assert result.repository is not None
    assert result.acquisition is not None
    assert result.validation is None
    assert result.failure is not None


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("repository", None),
        ("acquisition", None),
        ("validation", None),
        ("acceptance", None),
    ],
)
def test_successful_result_requires_mandatory_component_results(
    field_name: str,
    value: None,
) -> None:
    values = {
        "repository": object(),
        "acquisition": object(),
        "validation": object(),
        "acceptance": object(),
    }
    values[field_name] = value

    with pytest.raises(ValueError, match=field_name):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.SUCCEEDED,
            started_at_utc=STARTED,
            completed_at_utc=COMPLETED,
            duration_ms=1000,
            final_state=ExecutionState.COMPLETED,
            **values,
        )


def test_successful_result_rejects_failure_object() -> None:
    with pytest.raises(ValueError, match="must not include failure"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.SUCCEEDED,
            started_at_utc=STARTED,
            completed_at_utc=COMPLETED,
            duration_ms=1000,
            final_state=ExecutionState.COMPLETED,
            repository=object(),
            acquisition=object(),
            validation=object(),
            acceptance=object(),
            failure=failure(),
        )


def test_failed_result_requires_failure_object() -> None:
    with pytest.raises(ValueError, match="must include failure"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.FAILED,
            started_at_utc=STARTED,
            completed_at_utc=COMPLETED,
            duration_ms=1000,
            final_state=ExecutionState.FAILED,
        )


def test_successful_result_requires_completed_state() -> None:
    with pytest.raises(ValueError, match="COMPLETED"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.SUCCEEDED,
            started_at_utc=STARTED,
            completed_at_utc=COMPLETED,
            duration_ms=1000,
            final_state=ExecutionState.REPORT_GENERATION,
            repository=object(),
            acquisition=object(),
            validation=object(),
            acceptance=object(),
        )


def test_failed_result_requires_failed_state() -> None:
    with pytest.raises(ValueError, match="FAILED"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.FAILED,
            started_at_utc=STARTED,
            completed_at_utc=COMPLETED,
            duration_ms=1000,
            final_state=ExecutionState.ACQUISITION_VALIDATION,
            failure=failure(),
        )


def test_result_rejects_negative_duration() -> None:
    with pytest.raises(ValueError, match="duration_ms"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.FAILED,
            started_at_utc=STARTED,
            completed_at_utc=COMPLETED,
            duration_ms=-1,
            final_state=ExecutionState.FAILED,
            failure=failure(),
        )


def test_result_rejects_completion_before_start() -> None:
    with pytest.raises(ValueError, match="must not precede"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.FAILED,
            started_at_utc=COMPLETED,
            completed_at_utc=STARTED,
            duration_ms=0,
            final_state=ExecutionState.FAILED,
            failure=failure(),
        )


def test_result_rejects_non_utc_timestamp() -> None:
    non_utc = datetime(
        2026,
        7,
        26,
        10,
        0,
        tzinfo=timezone(timedelta(hours=-4)),
    )

    with pytest.raises(ValueError, match="normalized to UTC"):
        RegistryBackupExecutionResult(
            job_id=JobId("job-123"),
            outcome=ExecutionOutcome.FAILED,
            started_at_utc=non_utc,
            completed_at_utc=COMPLETED,
            duration_ms=0,
            final_state=ExecutionState.FAILED,
            failure=failure(),
        )


def test_result_normalizes_collections_to_tuples() -> None:
    evidence = [
        EvidenceReference(
            evidence_type=EvidenceType.LOG,
            description="Execution log",
        )
    ]

    result = RegistryBackupExecutionResult(
        job_id=JobId("job-123"),
        outcome=ExecutionOutcome.FAILED,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=1000,
        final_state=ExecutionState.FAILED,
        evidence=evidence,  # type: ignore[arg-type]
        warnings=["warning"],  # type: ignore[arg-type]
        failure=failure(),
    )

    assert isinstance(result.evidence, tuple)
    assert isinstance(result.warnings, tuple)


def test_result_is_immutable() -> None:
    result = successful_result()

    with pytest.raises(FrozenInstanceError):
        result.duration_ms = 500  # type: ignore[misc]


def test_execution_enums_have_stable_string_values() -> None:
    assert ExecutionState.REPOSITORY_VALIDATION.value == "repository_validation"
    assert ExecutionOutcome.SUCCEEDED_IDEMPOTENT.value == "succeeded_idempotent"
    assert FailureCategory.ACCEPTANCE_CONFLICT.value == "acceptance_conflict"


def test_execution_failure_rejects_terminal_failed_state() -> None:
    with pytest.raises(ValueError, match="operational state"):
        ExecutionFailure(
            category=FailureCategory.INTERNAL,
            failed_state=ExecutionState.FAILED,
            error_type="UnexpectedError",
            message="Unexpected failure",
            retryable=False,
            exit_code=99,
        )


def test_execution_failure_rejects_nonpositive_exit_code() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        ExecutionFailure(
            category=FailureCategory.INTERNAL,
            failed_state=ExecutionState.REPORT_GENERATION,
            error_type="UnexpectedError",
            message="Unexpected failure",
            retryable=False,
            exit_code=0,
        )
