"End-to-end operational acceptance and durable evidence publication."

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.exceptions import OperationalReportingError
from poe_backup_orchestrator.models import (
    RegistryBackupRequest,
    RepositoryValidationResult,
)
from poe_backup_orchestrator.models.operational_acceptance import (
    ACCEPTANCE_SCHEMA_NAME,
    ACCEPTANCE_SCHEMA_VERSION,
    AcceptanceCheck,
    FileEvidence,
    OperationalAcceptanceEvidence,
    OperationalAcceptancePublication,
    OperationalAcceptanceResult,
    OperationalAcceptanceStatus,
)
from poe_backup_orchestrator.services.run_service import RegistryBackupRunService
from poe_backup_orchestrator.utilities.json_serialization import deterministic_json

ACCEPTANCE_FAILURE_EXIT_CODE = 70


class UtcClock(Protocol):
    def now_utc(self) -> datetime: ...


class RepositoryValidator(Protocol):
    def __call__(self) -> RepositoryValidationResult: ...


@dataclass(frozen=True, slots=True)
class OperationalAcceptanceService:
    "Execute a governed run and prove its externally visible invariants."

    run_service: RegistryBackupRunService
    evidence_root: Path
    clock: UtcClock
    repository_validator: RepositoryValidator

    def execute(self, request: RegistryBackupRequest) -> OperationalAcceptanceResult:
        source_path = request.source_path.expanduser().resolve()
        source_before = _inspect_file(source_path)
        repository_before = self.repository_validator()
        run_result = self.run_service.execute(request)

        checks: list[AcceptanceCheck] = []
        issues: list[str] = []
        source_after = _optional_file_evidence(source_path)

        _record(
            checks,
            issues,
            "governed_run_succeeded",
            run_result.exit_code == 0,
            f"Governed run exit code: {run_result.exit_code}.",
        )
        _record(
            checks,
            issues,
            "source_preserved",
            source_after == source_before,
            (
                "Source remained present and byte-identical."
                if source_after == source_before
                else "Source was missing or changed during acceptance."
            ),
        )

        execution = run_result.execution
        acceptance = execution.acceptance
        accepted_snapshot = (
            None if acceptance is None else _optional_file_evidence(acceptance.snapshot_path)
        )
        accepted_manifest = (
            None if acceptance is None else _optional_file_evidence(acceptance.manifest_path)
        )

        _record(
            checks,
            issues,
            "accepted_snapshot_present",
            accepted_snapshot is not None,
            "Accepted snapshot exists." if accepted_snapshot else "Accepted snapshot missing.",
        )
        _record(
            checks,
            issues,
            "accepted_manifest_present",
            accepted_manifest is not None,
            "Accepted manifest exists." if accepted_manifest else "Accepted manifest missing.",
        )

        identity_matches = (
            acceptance is not None
            and accepted_snapshot is not None
            and accepted_snapshot.size_bytes == acceptance.size_bytes
            and accepted_snapshot.sha256 == acceptance.sha256
        )
        _record(
            checks,
            issues,
            "accepted_snapshot_identity",
            identity_matches,
            (
                "Accepted snapshot size and SHA-256 match."
                if identity_matches
                else "Accepted snapshot size or SHA-256 mismatch."
            ),
        )

        operational_json = _optional_file_evidence(run_result.publication.json_path)
        operational_text = _optional_file_evidence(run_result.publication.summary_path)
        reports_present = operational_json is not None and operational_text is not None
        _record(
            checks,
            issues,
            "operational_reports_present",
            reports_present,
            (
                "Operational JSON and text reports exist."
                if reports_present
                else "One or more operational reports are missing."
            ),
        )

        report_matches = _verify_operational_report(
            run_result.publication.json_path,
            job_id=str(execution.job_id),
            accepted_destination=(
                None if acceptance is None else str(acceptance.destination_directory)
            ),
        )
        _record(
            checks,
            issues,
            "operational_report_identity",
            report_matches,
            (
                "Operational report matches job and accepted destination."
                if report_matches
                else "Operational report identity mismatch."
            ),
        )

        repository_after = self.repository_validator()
        _record(
            checks,
            issues,
            "repository_valid_after_run",
            repository_after.is_valid,
            (
                "Repository validates after execution."
                if repository_after.is_valid
                else "Repository validation failed after execution."
            ),
        )

        passed = all(check.passed for check in checks)
        evidence = OperationalAcceptanceEvidence(
            schema_name=ACCEPTANCE_SCHEMA_NAME,
            schema_version=ACCEPTANCE_SCHEMA_VERSION,
            application_version=__version__,
            generated_at_utc=self.clock.now_utc(),
            job_id=str(execution.job_id),
            status=(
                OperationalAcceptanceStatus.PASSED if passed else OperationalAcceptanceStatus.FAILED
            ),
            exit_code=0 if passed else ACCEPTANCE_FAILURE_EXIT_CODE,
            source_before=source_before,
            source_after=source_after,
            accepted_snapshot=accepted_snapshot,
            accepted_manifest=accepted_manifest,
            operational_json_report=operational_json,
            operational_text_report=operational_text,
            repository_before=_repository_projection(repository_before),
            repository_after=_repository_projection(repository_after),
            checks=tuple(checks),
            issues=tuple(issues),
        )
        summary = render_operational_acceptance_summary(evidence)

        try:
            publication = publish_operational_acceptance(
                evidence,
                summary=summary,
                evidence_root=self.evidence_root,
            )
        except (OSError, ValueError) as exc:
            raise OperationalReportingError(
                f"Operational acceptance evidence publication failed: {exc}"
            ) from exc

        return OperationalAcceptanceResult(evidence, publication, summary)


def render_operational_acceptance_summary(
    evidence: OperationalAcceptanceEvidence,
) -> str:
    lines = [
        "POE Backup Orchestrator — Operational Acceptance",
        f"Job ID: {evidence.job_id}",
        f"Status: {evidence.status.value}",
        f"Exit code: {evidence.exit_code}",
        f"Generated: {evidence.generated_at_utc.isoformat().replace('+00:00', 'Z')}",
        "Checks:",
    ]
    for check in evidence.checks:
        state = "PASS" if check.passed else "FAIL"
        lines.append(f"  [{state}] {check.name}: {check.detail}")
    if evidence.issues:
        lines.append("Issues:")
        lines.extend(f"  - {issue}" for issue in evidence.issues)
    return "\n".join(lines) + "\n"


def publish_operational_acceptance(
    evidence: OperationalAcceptanceEvidence,
    *,
    summary: str,
    evidence_root: Path,
) -> OperationalAcceptancePublication:
    root = Path(evidence_root)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"registry-backup-acceptance-{evidence.job_id}.json"
    summary_path = root / f"registry-backup-acceptance-{evidence.job_id}.txt"
    staged_json = _stage_text(json_path, deterministic_json(evidence.to_dict()))
    staged_summary = _stage_text(summary_path, summary)
    _publish_pair(staged_json, json_path, staged_summary, summary_path)
    return OperationalAcceptancePublication(json_path, summary_path)


def _record(
    checks: list[AcceptanceCheck],
    issues: list[str],
    name: str,
    passed: bool,
    detail: str,
) -> None:
    checks.append(AcceptanceCheck(name, passed, detail))
    if not passed:
        issues.append(detail)


def _inspect_file(path: Path) -> FileEvidence:
    if not path.is_file():
        raise ValueError(f"acceptance source file not found: {path}")
    return FileEvidence(path, path.stat().st_size, _sha256_file(path))


def _optional_file_evidence(path: Path) -> FileEvidence | None:
    try:
        return _inspect_file(Path(path).resolve())
    except (OSError, ValueError):
        return None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_operational_report(
    path: Path,
    *,
    job_id: str,
    accepted_destination: str | None,
) -> bool:
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(decoded, dict):
        return False
    if decoded.get("job_id") != job_id or decoded.get("outcome") != "succeeded":
        return False
    acceptance = decoded.get("acceptance")
    return (
        isinstance(acceptance, dict)
        and acceptance.get("destination_directory") == accepted_destination
    )


def _repository_projection(result: RepositoryValidationResult) -> dict[str, object]:
    return {
        "command": list(result.command),
        "return_code": result.return_code,
        "mounted": result.mounted,
        "healthy": result.healthy,
        "operational": result.operational,
        "is_valid": result.is_valid,
        "standard_output": result.standard_output,
        "standard_error": result.standard_error,
    }


def _stage_text(destination: Path, content: str) -> Path:
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(raw_path)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        staged = temporary_path
        temporary_path = None
        return staged
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _publish_pair(
    staged_json: Path,
    json_path: Path,
    staged_summary: Path,
    summary_path: Path,
) -> None:
    backup_json = _reserve_backup_path(json_path) if json_path.exists() else None
    backup_summary = _reserve_backup_path(summary_path) if summary_path.exists() else None
    published_json = False
    published_summary = False
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
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".bak",
    )
    os.close(descriptor)
    backup_path = Path(raw_path)
    backup_path.unlink()
    return backup_path
