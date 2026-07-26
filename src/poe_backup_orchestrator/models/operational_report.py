"""Canonical operational report models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.models.job import require_utc

REPORT_SCHEMA_NAME = "poe-backup-orchestrator.registry-backup-report"
REPORT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class OperationalFailureReport:
    category: str
    failed_state: str
    error_type: str
    message: str
    retryable: bool
    exit_code: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "failed_state": self.failed_state,
            "error_type": self.error_type,
            "message": self.message,
            "retryable": self.retryable,
            "exit_code": self.exit_code,
        }


@dataclass(frozen=True, slots=True)
class OperationalEvidenceReport:
    evidence_type: str
    description: str
    path: str | None
    sha256: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_type": self.evidence_type,
            "description": self.description,
            "path": self.path,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class OperationalReport:
    schema_name: str
    schema_version: str
    application_version: str
    generated_at_utc: datetime
    job_id: str
    outcome: str
    started_at_utc: datetime
    completed_at_utc: datetime
    duration_ms: int
    final_state: str
    failure: OperationalFailureReport | None
    warnings: tuple[str, ...]
    evidence: tuple[OperationalEvidenceReport, ...]
    repository: dict[str, Any] | None
    acquisition: dict[str, Any] | None
    validation: dict[str, Any] | None
    acceptance: dict[str, Any] | None

    def __post_init__(self) -> None:
        require_utc(self.generated_at_utc, field_name="generated_at_utc")
        require_utc(self.started_at_utc, field_name="started_at_utc")
        require_utc(self.completed_at_utc, field_name="completed_at_utc")
        if self.duration_ms < 0:
            raise ValueError("duration_ms must not be negative")
        object.__setattr__(self, "warnings", tuple(self.warnings))
        object.__setattr__(self, "evidence", tuple(self.evidence))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "application_version": self.application_version,
            "generated_at_utc": _utc_isoformat(self.generated_at_utc),
            "job_id": self.job_id,
            "outcome": self.outcome,
            "started_at_utc": _utc_isoformat(self.started_at_utc),
            "completed_at_utc": _utc_isoformat(self.completed_at_utc),
            "duration_ms": self.duration_ms,
            "final_state": self.final_state,
            "failure": None if self.failure is None else self.failure.to_dict(),
            "warnings": list(self.warnings),
            "evidence": [item.to_dict() for item in self.evidence],
            "repository": self.repository,
            "acquisition": self.acquisition,
            "validation": self.validation,
            "acceptance": self.acceptance,
        }


@dataclass(frozen=True, slots=True)
class OperationalReportPublication:
    json_path: Path
    summary_path: Path


def _utc_isoformat(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
