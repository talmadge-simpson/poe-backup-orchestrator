"Tests for end-to-end operational acceptance evidence."

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from poe_backup_orchestrator.models import (
    ExecutionOutcome,
    ExecutionState,
    JobId,
    RegistryAcceptanceResult,
    RegistryAcceptanceStatus,
    RegistryBackupExecutionResult,
    RegistryBackupRequest,
    RepositoryValidationResult,
)
from poe_backup_orchestrator.models.operational_report import (
    OperationalReportPublication,
)
from poe_backup_orchestrator.services.operational_acceptance import (
    ACCEPTANCE_FAILURE_EXIT_CODE,
    OperationalAcceptanceService,
)
from poe_backup_orchestrator.services.run_service import RegistryBackupRunResult

NOW = datetime(2026, 7, 26, 20, 0, tzinfo=UTC)


class FixedClock:
    def now_utc(self) -> datetime:
        return NOW


class StubRunService:
    def __init__(self, result: RegistryBackupRunResult, mutation=None) -> None:
        self.result = result
        self.mutation = mutation

    def execute(self, request: RegistryBackupRequest) -> RegistryBackupRunResult:
        if self.mutation is not None:
            self.mutation(request)
        return self.result


def valid_repository() -> RepositoryValidationResult:
    return RepositoryValidationResult(
        ("poe-backup-repository", "--status"),
        0,
        True,
        True,
        True,
        "Healthy\nOperational Baseline\nRepository is mounted",
        "",
    )


def build_run_result(tmp_path: Path) -> RegistryBackupRunResult:
    accepted = tmp_path / "accepted" / "20260726T200000Z"
    accepted.mkdir(parents=True)
    snapshot = accepted / "poeregistry.sqlite3"
    snapshot.write_bytes(b"accepted snapshot")
    manifest = accepted / "poeregistry.manifest.json"
    manifest.write_text("{}\n", encoding="utf-8")
    digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()

    acceptance = RegistryAcceptanceResult(
        "poeregistry",
        "20260726T200000Z",
        accepted,
        snapshot,
        manifest,
        digest,
        snapshot.stat().st_size,
        RegistryAcceptanceStatus.ACCEPTED,
    )
    execution = RegistryBackupExecutionResult(
        job_id=JobId("job-acceptance"),
        outcome=ExecutionOutcome.SUCCEEDED,
        started_at_utc=NOW,
        completed_at_utc=NOW,
        duration_ms=0,
        final_state=ExecutionState.COMPLETED,
        repository=valid_repository(),
        acquisition=cast(object, object()),
        validation=cast(object, object()),
        acceptance=acceptance,
    )

    reports = tmp_path / "reports"
    reports.mkdir()
    json_report = reports / "report.json"
    json_report.write_text(
        json.dumps(
            {
                "job_id": "job-acceptance",
                "outcome": "succeeded",
                "acceptance": {"destination_directory": str(accepted)},
            }
        ),
        encoding="utf-8",
    )
    text_report = reports / "report.txt"
    text_report.write_text("report\n", encoding="utf-8")

    return RegistryBackupRunResult(
        execution,
        cast(object, object()),
        OperationalReportPublication(json_report, text_report),
        "summary\n",
        0,
    )


def build_service(
    tmp_path: Path,
    source: Path,
    *,
    mutation=None,
    second_repository: RepositoryValidationResult | None = None,
) -> OperationalAcceptanceService:
    results = iter((valid_repository(), second_repository or valid_repository()))
    return OperationalAcceptanceService(
        run_service=cast(
            object,
            StubRunService(build_run_result(tmp_path), mutation=mutation),
        ),
        evidence_root=tmp_path / "evidence",
        clock=FixedClock(),
        repository_validator=lambda: next(results),
    )


def test_acceptance_passes_and_publishes_evidence(tmp_path: Path) -> None:
    source = tmp_path / "registry.sqlite3"
    source.write_bytes(b"registry source")

    result = build_service(tmp_path, source).execute(RegistryBackupRequest(source))

    assert result.evidence.passed
    assert result.evidence.exit_code == 0
    assert all(check.passed for check in result.evidence.checks)
    assert result.publication.json_path.is_file()
    assert result.publication.summary_path.is_file()
    decoded = json.loads(result.publication.json_path.read_text(encoding="utf-8"))
    assert decoded["status"] == "passed"


def test_acceptance_detects_source_mutation(tmp_path: Path) -> None:
    source = tmp_path / "registry.sqlite3"
    source.write_bytes(b"registry source")

    def mutate(request: RegistryBackupRequest) -> None:
        request.source_path.write_bytes(b"changed")

    result = build_service(
        tmp_path,
        source,
        mutation=mutate,
    ).execute(RegistryBackupRequest(source))

    assert not result.evidence.passed
    assert result.evidence.exit_code == ACCEPTANCE_FAILURE_EXIT_CODE
    assert any("Source was missing or changed" in issue for issue in result.evidence.issues)


def test_acceptance_detects_report_identity_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "registry.sqlite3"
    source.write_bytes(b"registry source")
    service = build_service(tmp_path, source)
    service.run_service.result.publication.json_path.write_text(
        '{"job_id":"wrong","outcome":"succeeded","acceptance":{}}\n',
        encoding="utf-8",
    )

    result = service.execute(RegistryBackupRequest(source))

    assert not result.evidence.passed
    assert any(
        check.name == "operational_report_identity" and not check.passed
        for check in result.evidence.checks
    )


def test_acceptance_detects_post_run_repository_failure(tmp_path: Path) -> None:
    source = tmp_path / "registry.sqlite3"
    source.write_bytes(b"registry source")
    invalid = RepositoryValidationResult(("status",), 1, False, False, False, "", "unavailable")

    result = build_service(
        tmp_path,
        source,
        second_repository=invalid,
    ).execute(RegistryBackupRequest(source))

    assert not result.evidence.passed
    assert any(
        check.name == "repository_valid_after_run" and not check.passed
        for check in result.evidence.checks
    )
