"""Executable composition service for one Registry backup run."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from poe_backup_orchestrator.exceptions import (
    OperationalReportingError,
    RepositoryValidationError,
)
from poe_backup_orchestrator.models import (
    Clock,
    JobId,
    JobIdGenerator,
    RegistryBackupExecutionResult,
    RegistryBackupRequest,
    RepositoryValidationResult,
)
from poe_backup_orchestrator.models.operational_report import (
    OperationalReport,
    OperationalReportPublication,
)
from poe_backup_orchestrator.models.runtime import RuntimeEnvironment
from poe_backup_orchestrator.services.adapters import (
    AcquisitionValidationAdapter,
    RegistryAcceptanceAdapter,
    RegistryAcquisitionAdapter,
    RepositoryValidationAdapter,
)
from poe_backup_orchestrator.services.operational_reporting import (
    build_operational_report,
    publish_operational_report,
    render_operational_summary,
)
from poe_backup_orchestrator.services.orchestrator import RegistryBackupOrchestrator
from poe_backup_orchestrator.services.runtime_lifecycle import (
    RuntimeLifecycleCoordinator,
)
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspector,
    SystemHostIdentity,
    SystemProcessLiveness,
)
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore

REPORTING_FAILURE_EXIT_CODE = 60


class ReportBuilder(Protocol):
    def __call__(
        self,
        result: RegistryBackupExecutionResult,
        *,
        generated_at_utc: datetime,
    ) -> OperationalReport: ...


class ReportPublisher(Protocol):
    def __call__(
        self,
        report: OperationalReport,
        *,
        reports_root: Path,
    ) -> OperationalReportPublication: ...


class ReportRenderer(Protocol):
    def __call__(self, report: OperationalReport) -> str: ...


@dataclass(frozen=True, slots=True)
class SystemUtcClock:
    """Provide current timezone-aware UTC timestamps."""

    def now_utc(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class SecureJobIdGenerator:
    """Generate sortable, collision-resistant job identifiers."""

    def generate(self, now_utc: datetime) -> JobId:
        timestamp = now_utc.astimezone(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        return JobId(f"{timestamp}-{secrets.token_hex(6)}")


@dataclass(frozen=True, slots=True)
class RepositoryReadinessGuard:
    """Convert an invalid repository result into a governed failure."""

    validator: RepositoryValidationAdapter

    def validate(self) -> RepositoryValidationResult:
        result = self.validator.validate()
        if not result.is_valid:
            raise RepositoryValidationError(
                "Backup repository validation failed; orchestration was not started."
            )
        return result


@dataclass(frozen=True, slots=True)
class RegistryBackupRunResult:
    """Published outcome returned to the CLI boundary."""

    execution: RegistryBackupExecutionResult
    report: OperationalReport
    publication: OperationalReportPublication
    summary: str
    exit_code: int


@dataclass(frozen=True, slots=True)
class RegistryBackupRunService:
    """Compose orchestration, reporting, publication, and exit-code selection."""

    orchestrator: RegistryBackupOrchestrator
    reports_root: Path
    clock: Clock
    report_builder: ReportBuilder = build_operational_report
    report_publisher: ReportPublisher = publish_operational_report
    report_renderer: ReportRenderer = render_operational_summary

    def execute(self, request: RegistryBackupRequest) -> RegistryBackupRunResult:
        execution = self.orchestrator.execute(request)
        report = self.report_builder(
            execution,
            generated_at_utc=self.clock.now_utc(),
        )

        try:
            publication = self.report_publisher(
                report,
                reports_root=self.reports_root,
            )
        except (OSError, ValueError) as exc:
            raise OperationalReportingError(
                f"Operational report publication failed: {exc}"
            ) from exc

        exit_code = 0
        if execution.failure is not None:
            exit_code = execution.failure.exit_code

        return RegistryBackupRunResult(
            execution=execution,
            report=report,
            publication=publication,
            summary=self.report_renderer(report),
            exit_code=exit_code,
        )


def build_registry_backup_run_service(
    *,
    source_path: Path,
    staging_root: Path,
    reports_root: Path,
    destination_root: Path,
    asset_id: str,
    state_root: Path,
    environment: RuntimeEnvironment,
    clock: Clock | None = None,
    job_id_generator: JobIdGenerator | None = None,
) -> RegistryBackupRunService:
    """Build the production dependency graph for one Registry backup run."""

    runtime_clock = clock or SystemUtcClock()
    runtime_job_id_generator = job_id_generator or SecureJobIdGenerator()
    runtime_store = RuntimeStateStore(state_root)
    host_identity = SystemHostIdentity()
    recovery_inspector = RuntimeRecoveryInspector(
        store=runtime_store,
        host_identity=host_identity,
        process_liveness=SystemProcessLiveness(),
        clock=runtime_clock,
    )
    runtime_lifecycle = RuntimeLifecycleCoordinator(
        store=runtime_store,
        recovery_inspector=recovery_inspector,
        host_identity=host_identity,
        clock=runtime_clock,
        environment=environment,
    )

    orchestrator = RegistryBackupOrchestrator(
        repository_validation=RepositoryReadinessGuard(RepositoryValidationAdapter()),
        registry_acquisition=RegistryAcquisitionAdapter(
            source_path=source_path,
            staging_root=staging_root,
            asset_id=asset_id,
            clock=runtime_clock,
        ),
        acquisition_validation=AcquisitionValidationAdapter(),
        registry_acceptance=RegistryAcceptanceAdapter(
            destination_root=destination_root,
        ),
        clock=runtime_clock,
        job_id_generator=runtime_job_id_generator,
        runtime_lifecycle=runtime_lifecycle,
    )

    return RegistryBackupRunService(
        orchestrator=orchestrator,
        reports_root=reports_root,
        clock=runtime_clock,
    )
