"Immutable operational-acceptance evidence models."

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.models.job import require_utc

ACCEPTANCE_SCHEMA_NAME = "poe-backup-orchestrator.registry-backup-acceptance"
ACCEPTANCE_SCHEMA_VERSION = "1.0"


class OperationalAcceptanceStatus(StrEnum):
    "Final status of one operational-acceptance execution."

    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class AcceptanceCheck:
    "One named acceptance assertion."

    name: str
    passed: bool
    detail: str

    def __post_init__(self) -> None:
        name = self.name.strip()
        detail = self.detail.strip()
        if not name:
            raise ValueError("acceptance check name must not be empty")
        if not detail:
            raise ValueError("acceptance check detail must not be empty")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "detail", detail)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class FileEvidence:
    "Recorded identity of one evidence file."

    path: Path
    size_bytes: int
    sha256: str

    def __post_init__(self) -> None:
        if self.size_bytes < 0:
            raise ValueError("file evidence size_bytes must not be negative")
        if len(self.sha256) != 64:
            raise ValueError("file evidence sha256 must contain 64 characters")

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class OperationalAcceptanceEvidence:
    "Canonical evidence for one operational-acceptance execution."

    schema_name: str
    schema_version: str
    application_version: str
    generated_at_utc: datetime
    job_id: str
    status: OperationalAcceptanceStatus
    exit_code: int
    source_before: FileEvidence
    source_after: FileEvidence | None
    accepted_snapshot: FileEvidence | None
    accepted_manifest: FileEvidence | None
    operational_json_report: FileEvidence | None
    operational_text_report: FileEvidence | None
    repository_before: dict[str, Any]
    repository_after: dict[str, Any]
    checks: tuple[AcceptanceCheck, ...]
    issues: tuple[str, ...]

    def __post_init__(self) -> None:
        require_utc(self.generated_at_utc, field_name="generated_at_utc")
        if self.exit_code < 0:
            raise ValueError("acceptance exit_code must not be negative")
        object.__setattr__(self, "checks", tuple(self.checks))
        object.__setattr__(self, "issues", tuple(self.issues))

    @property
    def passed(self) -> bool:
        return self.status is OperationalAcceptanceStatus.PASSED

    def to_dict(self) -> dict[str, Any]:
        def optional(value: FileEvidence | None) -> dict[str, Any] | None:
            return None if value is None else value.to_dict()

        return {
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "application_version": self.application_version,
            "generated_at_utc": self.generated_at_utc.isoformat().replace("+00:00", "Z"),
            "job_id": self.job_id,
            "status": self.status.value,
            "exit_code": self.exit_code,
            "source_before": self.source_before.to_dict(),
            "source_after": optional(self.source_after),
            "accepted_snapshot": optional(self.accepted_snapshot),
            "accepted_manifest": optional(self.accepted_manifest),
            "operational_json_report": optional(self.operational_json_report),
            "operational_text_report": optional(self.operational_text_report),
            "repository_before": self.repository_before,
            "repository_after": self.repository_after,
            "checks": [check.to_dict() for check in self.checks],
            "issues": list(self.issues),
        }


@dataclass(frozen=True, slots=True)
class OperationalAcceptancePublication:
    "Published acceptance evidence paths."

    json_path: Path
    summary_path: Path


@dataclass(frozen=True, slots=True)
class OperationalAcceptanceResult:
    "Public result returned to the CLI."

    evidence: OperationalAcceptanceEvidence
    publication: OperationalAcceptancePublication
    summary: str
