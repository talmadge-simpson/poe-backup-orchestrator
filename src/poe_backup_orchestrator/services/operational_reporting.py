"""Operational report projection, rendering, and atomic persistence."""

from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.models import (
    EvidenceReference,
    RegistryAcceptanceResult,
    RegistryBackupExecutionResult,
    RegistryIngestionResult,
    RepositoryValidationResult,
    SqliteBackupResult,
)
from poe_backup_orchestrator.models.operational_report import (
    REPORT_SCHEMA_NAME,
    REPORT_SCHEMA_VERSION,
    OperationalEvidenceReport,
    OperationalFailureReport,
    OperationalReport,
    OperationalReportPublication,
)
from poe_backup_orchestrator.utilities.json_serialization import deterministic_json

_SAFE_JOB_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def build_operational_report(
    result: RegistryBackupExecutionResult,
    *,
    generated_at_utc: datetime,
    application_version: str = __version__,
) -> OperationalReport:
    failure = result.failure
    failure_report = (
        None
        if failure is None
        else OperationalFailureReport(
            category=failure.category.value,
            failed_state=failure.failed_state.value,
            error_type=failure.error_type,
            message=failure.message,
            retryable=failure.retryable,
            exit_code=failure.exit_code,
        )
    )
    return OperationalReport(
        schema_name=REPORT_SCHEMA_NAME,
        schema_version=REPORT_SCHEMA_VERSION,
        application_version=application_version,
        generated_at_utc=generated_at_utc,
        job_id=str(result.job_id),
        outcome=result.outcome.value,
        started_at_utc=result.started_at_utc,
        completed_at_utc=result.completed_at_utc,
        duration_ms=result.duration_ms,
        final_state=result.final_state.value,
        failure=failure_report,
        warnings=result.warnings,
        evidence=tuple(_serialize_evidence(item) for item in result.evidence),
        repository=_serialize_stage_result(result.repository),
        acquisition=_serialize_stage_result(result.acquisition),
        validation=_serialize_stage_result(result.validation),
        acceptance=_serialize_stage_result(result.acceptance),
    )


def render_operational_summary(report: OperationalReport) -> str:
    lines = [
        "POE Backup Orchestrator — Registry Backup Report",
        f"Job ID: {report.job_id}",
        f"Outcome: {report.outcome}",
        f"Final state: {report.final_state}",
        f"Started: {_utc_isoformat(report.started_at_utc)}",
        f"Completed: {_utc_isoformat(report.completed_at_utc)}",
        f"Duration: {report.duration_ms} ms",
        f"Completed stages: {_completed_stages(report)}",
    ]
    if report.acceptance is not None:
        lines.append(f"Accepted destination: {report.acceptance['destination_directory']}")
    if report.failure is not None:
        lines.extend(
            [
                "Failure:",
                f"  Category: {report.failure.category}",
                f"  Failed state: {report.failure.failed_state}",
                f"  Type: {report.failure.error_type}",
                f"  Message: {report.failure.message}",
                f"  Retryable: {'yes' if report.failure.retryable else 'no'}",
                f"  Exit code: {report.failure.exit_code}",
            ]
        )
    if report.warnings:
        lines.append("Warnings:")
        lines.extend(f"  - {warning}" for warning in report.warnings)
    if report.evidence:
        lines.append("Evidence:")
        for item in report.evidence:
            location = f" — {item.path}" if item.path is not None else ""
            lines.append(f"  - {item.evidence_type}: {item.description}{location}")
    return "\n".join(lines) + "\n"


def publish_operational_report(
    report: OperationalReport, *, reports_root: Path
) -> OperationalReportPublication:
    safe_job_id = _validated_filename_job_id(report.job_id)
    root = Path(reports_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"registry-backup-{safe_job_id}.json"
    summary_path = root / f"registry-backup-{safe_job_id}.txt"

    staged_json = _stage_text(json_path, deterministic_json(report.to_dict()))
    staged_summary = _stage_text(summary_path, render_operational_summary(report))
    _publish_report_pair(
        staged_json=staged_json,
        json_path=json_path,
        staged_summary=staged_summary,
        summary_path=summary_path,
    )
    return OperationalReportPublication(json_path=json_path, summary_path=summary_path)


def _serialize_evidence(item: EvidenceReference) -> OperationalEvidenceReport:
    return OperationalEvidenceReport(
        evidence_type=item.evidence_type.value,
        description=item.description,
        path=None if item.path is None else str(item.path),
        sha256=item.sha256,
    )


def _serialize_stage_result(value: object | None) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, RepositoryValidationResult):
        return {
            "command": list(value.command),
            "return_code": value.return_code,
            "mounted": value.mounted,
            "healthy": value.healthy,
            "operational": value.operational,
            "standard_output": value.standard_output,
            "standard_error": value.standard_error,
            "is_valid": value.is_valid,
        }
    if isinstance(value, SqliteBackupResult):
        return {
            "asset_id": value.asset_id,
            "source_path": str(value.source_path),
            "backup_path": str(value.backup_path),
            "manifest_path": str(value.manifest_path),
            "sha256": value.sha256,
            "size_bytes": value.size_bytes,
            "integrity_check": value.integrity_check,
            "created_at": value.created_at,
        }
    if isinstance(value, RegistryIngestionResult):
        return {
            "asset_id": value.asset_id,
            "manifest_path": str(value.manifest_path),
            "snapshot_path": str(value.snapshot_path),
            "created_at": value.created_at,
            "sha256": value.sha256,
            "size_bytes": value.size_bytes,
            "integrity_check": value.integrity_check,
        }
    if isinstance(value, RegistryAcceptanceResult):
        return {
            "asset_id": value.asset_id,
            "run_id": value.run_id,
            "destination_directory": str(value.destination_directory),
            "snapshot_path": str(value.snapshot_path),
            "manifest_path": str(value.manifest_path),
            "sha256": value.sha256,
            "size_bytes": value.size_bytes,
            "status": value.status.value,
        }
    raise TypeError(f"unsupported operational report stage result: {type(value).__name__}")


def _validated_filename_job_id(value: str) -> str:
    if not _SAFE_JOB_ID.fullmatch(value) or value in {".", ".."}:
        raise ValueError("job ID is not safe for operational report filenames")
    return value


def _completed_stages(report: OperationalReport) -> str:
    names = [
        name
        for name, value in (
            ("repository_validation", report.repository),
            ("registry_acquisition", report.acquisition),
            ("acquisition_validation", report.validation),
            ("registry_acceptance", report.acceptance),
        )
        if value is not None
    ]
    return ", ".join(names) if names else "none"


def _stage_text(destination: Path, content: str) -> Path:
    temporary_path = None
    descriptor = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp"
        )
        temporary_path = Path(raw_path)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        staged_path = temporary_path
        temporary_path = None
        return staged_path
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _publish_report_pair(
    *,
    staged_json: Path,
    json_path: Path,
    staged_summary: Path,
    summary_path: Path,
) -> None:
    backup_json = _reserve_backup_path(json_path) if json_path.exists() else None
    backup_summary = _reserve_backup_path(summary_path) if summary_path.exists() else None
    published_summary = False
    published_json = False

    try:
        if backup_json is not None:
            os.replace(json_path, backup_json)
        if backup_summary is not None:
            os.replace(summary_path, backup_summary)

        os.replace(staged_summary, summary_path)
        published_summary = True
        os.replace(staged_json, json_path)
        published_json = True
    except Exception:
        if published_json:
            json_path.unlink(missing_ok=True)
        if published_summary:
            summary_path.unlink(missing_ok=True)

        if backup_summary is not None and backup_summary.exists():
            os.replace(backup_summary, summary_path)
        if backup_json is not None and backup_json.exists():
            os.replace(backup_json, json_path)
        raise
    finally:
        staged_json.unlink(missing_ok=True)
        staged_summary.unlink(missing_ok=True)
        if backup_json is not None:
            backup_json.unlink(missing_ok=True)
        if backup_summary is not None:
            backup_summary.unlink(missing_ok=True)


def _reserve_backup_path(destination: Path) -> Path:
    descriptor, raw_path = tempfile.mkstemp(
        dir=destination.parent, prefix=f".{destination.name}.", suffix=".bak"
    )
    os.close(descriptor)
    backup_path = Path(raw_path)
    backup_path.unlink()
    return backup_path


def _utc_isoformat(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
