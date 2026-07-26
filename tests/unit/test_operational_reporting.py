"""Tests for operational reporting."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    EvidenceReference,
    EvidenceType,
    ExecutionFailure,
    ExecutionOutcome,
    ExecutionState,
    FailureCategory,
    JobId,
    RegistryAcceptanceResult,
    RegistryAcceptanceStatus,
    RegistryBackupExecutionResult,
    RegistryIngestionResult,
    RepositoryValidationResult,
    SqliteBackupResult,
)
from poe_backup_orchestrator.services import (
    build_operational_report,
    publish_operational_report,
    render_operational_summary,
)

STARTED = datetime(2026, 7, 26, 21, 0, tzinfo=UTC)
COMPLETED = STARTED + timedelta(seconds=2)
GENERATED = COMPLETED + timedelta(milliseconds=250)
DIGEST = "a" * 64


def stage_results():
    repository = RepositoryValidationResult(
        ("poe-backup-repository", "--status"), 0, True, True, True, "Healthy", ""
    )
    acquisition = SqliteBackupResult(
        "POERegistry",
        Path("/source/registry.db"),
        Path("/staging/registry.db"),
        Path("/staging/registry.manifest.json"),
        DIGEST,
        100,
        "ok",
        "2026-07-26T21:00:01Z",
    )
    validation = RegistryIngestionResult(
        "POERegistry",
        Path("/staging/registry.manifest.json"),
        Path("/staging/registry.db"),
        "2026-07-26T21:00:01Z",
        DIGEST,
        100,
        "ok",
    )
    acceptance = RegistryAcceptanceResult(
        "POERegistry",
        "run-1",
        Path("/repository/run-1"),
        Path("/repository/run-1/registry.db"),
        Path("/repository/run-1/registry.manifest.json"),
        DIGEST,
        100,
        RegistryAcceptanceStatus.ACCEPTED,
    )
    return repository, acquisition, validation, acceptance


def successful_result():
    repository, acquisition, validation, acceptance = stage_results()
    return RegistryBackupExecutionResult(
        job_id=JobId("job-slice-3f"),
        outcome=ExecutionOutcome.SUCCEEDED,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=2000,
        final_state=ExecutionState.COMPLETED,
        repository=repository,
        acquisition=acquisition,
        validation=validation,
        acceptance=acceptance,
        evidence=(
            EvidenceReference(
                EvidenceType.ACCEPTED_ARTIFACT,
                "Accepted Registry snapshot",
                acceptance.snapshot_path,
                DIGEST,
            ),
        ),
        warnings=("sample warning",),
    )


def test_success_report_and_summary():
    report = build_operational_report(successful_result(), generated_at_utc=GENERATED)
    data = report.to_dict()
    assert data["schema_version"] == "1.0"
    assert data["application_version"] == "0.1.0"
    assert data["acceptance"]["status"] == "ACCEPTED"
    assert data["failure"] is None
    summary = render_operational_summary(report)
    assert "Job ID: job-slice-3f" in summary
    assert "Accepted destination: /repository/run-1" in summary


def test_failed_report_preserves_prior_results():
    repository, acquisition, _, _ = stage_results()
    result = RegistryBackupExecutionResult(
        job_id=JobId("job-failed"),
        outcome=ExecutionOutcome.FAILED,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=2000,
        final_state=ExecutionState.FAILED,
        repository=repository,
        acquisition=acquisition,
        failure=ExecutionFailure(
            FailureCategory.VALIDATION,
            ExecutionState.ACQUISITION_VALIDATION,
            "RegistryIngestionError",
            "invalid",
            False,
            40,
        ),
    )
    data = build_operational_report(result, generated_at_utc=GENERATED).to_dict()
    assert data["repository"] is not None
    assert data["acquisition"] is not None
    assert data["validation"] is None
    assert data["failure"]["failed_state"] == "acquisition_validation"


def test_publish_is_deterministic_and_atomic(tmp_path: Path):
    report = build_operational_report(successful_result(), generated_at_utc=GENERATED)
    publication = publish_operational_report(report, reports_root=tmp_path / "reports")
    assert publication.json_path.name == "registry-backup-job-slice-3f.json"
    assert json.loads(publication.json_path.read_text()) == report.to_dict()
    assert publication.summary_path.read_text() == render_operational_summary(report)
    assert not list(publication.json_path.parent.glob("*.tmp"))


@pytest.mark.parametrize("job_id", ["../escape", "a/b", ".", ".."])
def test_unsafe_job_id_is_rejected(tmp_path: Path, job_id: str):
    source = successful_result()
    result = RegistryBackupExecutionResult(
        job_id=JobId(job_id),
        outcome=source.outcome,
        started_at_utc=source.started_at_utc,
        completed_at_utc=source.completed_at_utc,
        duration_ms=source.duration_ms,
        final_state=source.final_state,
        repository=source.repository,
        acquisition=source.acquisition,
        validation=source.validation,
        acceptance=source.acceptance,
    )
    report = build_operational_report(result, generated_at_utc=GENERATED)
    with pytest.raises(ValueError, match="not safe"):
        publish_operational_report(report, reports_root=tmp_path)


def test_unknown_stage_result_is_rejected():
    result = successful_result()
    object.__setattr__(result, "repository", object())
    with pytest.raises(TypeError, match="unsupported"):
        build_operational_report(result, generated_at_utc=GENERATED)


def test_report_contract_serializes_utc_failure_evidence_and_nulls():
    repository, acquisition, _, _ = stage_results()
    result = RegistryBackupExecutionResult(
        job_id=JobId("job-contract"),
        outcome=ExecutionOutcome.FAILED,
        started_at_utc=STARTED,
        completed_at_utc=COMPLETED,
        duration_ms=2000,
        final_state=ExecutionState.FAILED,
        repository=repository,
        acquisition=acquisition,
        failure=ExecutionFailure(
            FailureCategory.VALIDATION,
            ExecutionState.ACQUISITION_VALIDATION,
            "RegistryIngestionError",
            "validation failed",
            True,
            40,
        ),
        evidence=(
            EvidenceReference(
                EvidenceType.ACCEPTED_ARTIFACT,
                "Registry backup evidence",
                acquisition.backup_path,
                DIGEST,
            ),
        ),
        warnings=("operator review required",),
    )

    data = build_operational_report(result, generated_at_utc=GENERATED).to_dict()

    assert data["schema_name"] == "poe-backup-orchestrator.registry-backup-report"
    assert data["schema_version"] == "1.0"
    assert data["generated_at_utc"] == "2026-07-26T21:00:02.250000Z"
    assert data["started_at_utc"] == "2026-07-26T21:00:00Z"
    assert data["completed_at_utc"] == "2026-07-26T21:00:02Z"
    assert data["outcome"] == "failed"
    assert data["final_state"] == "failed"
    assert data["failure"] == {
        "category": "validation",
        "failed_state": "acquisition_validation",
        "error_type": "RegistryIngestionError",
        "message": "validation failed",
        "retryable": True,
        "exit_code": 40,
    }
    assert data["warnings"] == ["operator review required"]
    assert data["evidence"] == [
        {
            "evidence_type": "accepted_artifact",
            "description": "Registry backup evidence",
            "path": "/staging/registry.db",
            "sha256": DIGEST,
        }
    ]
    assert data["repository"] is not None
    assert data["acquisition"] is not None
    assert data["validation"] is None
    assert data["acceptance"] is None


def test_publication_failure_leaves_no_partial_report(tmp_path: Path, monkeypatch):
    report = build_operational_report(successful_result(), generated_at_utc=GENERATED)
    reports_root = tmp_path / "reports"
    real_replace = os.replace

    def fail_json_commit(source, destination):
        destination_path = Path(destination)
        if destination_path.suffix == ".json":
            raise OSError("simulated JSON commit failure")
        return real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_json_commit)

    with pytest.raises(OSError, match="simulated JSON commit failure"):
        publish_operational_report(report, reports_root=reports_root)

    assert not (reports_root / "registry-backup-job-slice-3f.json").exists()
    assert not (reports_root / "registry-backup-job-slice-3f.txt").exists()
    assert not list(reports_root.glob("*.tmp"))
    assert not list(reports_root.glob("*.bak"))


def test_failed_republication_restores_previous_report(tmp_path: Path, monkeypatch):
    original = build_operational_report(successful_result(), generated_at_utc=GENERATED)
    reports_root = tmp_path / "reports"
    publication = publish_operational_report(original, reports_root=reports_root)
    original_json = publication.json_path.read_text(encoding="utf-8")
    original_summary = publication.summary_path.read_text(encoding="utf-8")

    replacement = build_operational_report(
        successful_result(),
        generated_at_utc=GENERATED + timedelta(seconds=1),
        application_version="9.9.9",
    )
    real_replace = os.replace

    def fail_replacement_json_commit(source, destination):
        source_path = Path(source)
        destination_path = Path(destination)
        if source_path.suffix == ".tmp" and destination_path.suffix == ".json":
            raise OSError("simulated replacement failure")
        return real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_replacement_json_commit)

    with pytest.raises(OSError, match="simulated replacement failure"):
        publish_operational_report(replacement, reports_root=reports_root)

    assert publication.json_path.read_text(encoding="utf-8") == original_json
    assert publication.summary_path.read_text(encoding="utf-8") == original_summary
    assert not list(reports_root.glob("*.tmp"))
    assert not list(reports_root.glob("*.bak"))
