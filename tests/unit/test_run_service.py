"""Tests for executable Registry backup composition."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import cast

import pytest

from poe_backup_orchestrator.exceptions import (
    OperationalReportingError,
    RepositoryValidationError,
)
from poe_backup_orchestrator.models import (
    ExecutionFailure,
    ExecutionOutcome,
    ExecutionState,
    FailureCategory,
    JobId,
    RegistryBackupExecutionResult,
    RegistryBackupRequest,
    RepositoryValidationResult,
)
from poe_backup_orchestrator.models.operational_report import (
    OperationalReportPublication,
)
from poe_backup_orchestrator.services import (
    RegistryBackupRunService,
    RepositoryReadinessGuard,
    SecureJobIdGenerator,
)
from poe_backup_orchestrator.services.adapters import RepositoryValidationAdapter

STARTED = datetime(2026, 7, 26, 18, 0, tzinfo=UTC)
COMPLETED = STARTED + timedelta(seconds=1)


class FixedClock:
    def now_utc(self) -> datetime:
        return COMPLETED + timedelta(milliseconds=1)


class StubOrchestrator:
    def __init__(self, result: RegistryBackupExecutionResult) -> None:
        self.result = result
        self.requests: list[RegistryBackupRequest] = []

    def execute(self, request: RegistryBackupRequest) -> RegistryBackupExecutionResult:
        self.requests.append(request)
        return self.result


def failed_execution() -> RegistryBackupExecutionResult:
    return RegistryBackupExecutionResult(
        job_id=JobId("job-failed"),
        outcome=ExecutionOutcome.FAILED,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=1000,
        final_state=ExecutionState.FAILED,
        failure=ExecutionFailure(
            FailureCategory.REPOSITORY_PRECONDITION,
            ExecutionState.REPOSITORY_VALIDATION,
            "RepositoryValidationError",
            "repository unavailable",
            False,
            20,
        ),
    )


def test_readiness_guard_rejects_invalid_repository() -> None:
    result = RepositoryValidationResult(
        ("status",),
        1,
        False,
        False,
        False,
        "",
        "unavailable",
    )
    adapter = RepositoryValidationAdapter(validator=lambda command: result)

    with pytest.raises(RepositoryValidationError):
        RepositoryReadinessGuard(adapter).validate()


def test_run_service_publishes_governed_failure_and_returns_mapped_exit(
    tmp_path: Path,
) -> None:
    execution = failed_execution()
    orchestrator = StubOrchestrator(execution)
    published = OperationalReportPublication(
        json_path=tmp_path / "report.json",
        summary_path=tmp_path / "report.txt",
    )

    service = RegistryBackupRunService(
        orchestrator=cast(object, orchestrator),
        reports_root=tmp_path,
        clock=FixedClock(),
        report_publisher=lambda report, *, reports_root: published,
    )

    result = service.execute(RegistryBackupRequest(Path("/source/registry.db")))

    assert result.exit_code == 20
    assert result.execution is execution
    assert result.publication is published
    assert "Outcome: failed" in result.summary


def test_run_service_maps_publication_error() -> None:
    execution = failed_execution()

    def failing_publisher(report, *, reports_root):
        del report, reports_root
        raise OSError("disk unavailable")

    service = RegistryBackupRunService(
        orchestrator=cast(object, StubOrchestrator(execution)),
        reports_root=Path("/reports"),
        clock=FixedClock(),
        report_publisher=failing_publisher,
    )

    with pytest.raises(OperationalReportingError, match="disk unavailable"):
        service.execute(RegistryBackupRequest(Path("/source/registry.db")))


def test_secure_job_id_is_filename_safe_and_unique() -> None:
    generator = SecureJobIdGenerator()

    first = generator.generate(STARTED)
    second = generator.generate(STARTED)

    assert str(first).startswith("20260726T180000000000Z-")
    assert "/" not in str(first)
    assert first != second
