"""Command-line interface for the POE Backup Orchestrator."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.bootstrap import bootstrap_application
from poe_backup_orchestrator.exceptions import (
    OperationalReportingError,
    OrchestratorError,
    RepositoryValidationError,
)
from poe_backup_orchestrator.models import (
    RegistryBackupRequest,
    RestorePlan,
    RestorePlanRequest,
    RuntimeEnvironment,
)
from poe_backup_orchestrator.models.recovery import RecoveryPoint
from poe_backup_orchestrator.services import (
    REPORTING_FAILURE_EXIT_CODE,
    OperationalAcceptanceService,
    build_registry_backup_run_service,
    build_runtime_recovery_inspector,
    create_sqlite_backup,
    validate_repository,
)
from poe_backup_orchestrator.services.restore import (
    RecoveryPointDiscoveryError,
    RestorePlanningError,
    build_restore_plan,
    discover_recovery_points,
    evaluate_recovery_point,
)
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspection,
)

DEFAULT_CONFIG_PATH = Path("config/orchestrator.toml")
DEFAULT_REGISTRY_ASSET_ID = "poeregistry"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="poe-backup-orchestrator",
        description="Governed backup orchestration for the POE platform.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Explicit path to the orchestrator TOML configuration file.",
    )
    parser.add_argument(
        "--environment",
        choices=[item.value for item in RuntimeEnvironment],
        default=None,
        help="Explicit runtime environment; it must match the configuration.",
    )

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("status", help="Display the current orchestrator status.")
    subparsers.add_parser(
        "runtime-state",
        help="Inspect the authoritative orchestrator runtime state.",
    )
    subparsers.add_parser(
        "validate-repository",
        help="Validate the managed backup repository.",
    )

    sqlite_parser = subparsers.add_parser(
        "backup-sqlite",
        help="Create a consistent backup of a local SQLite database.",
    )
    sqlite_parser.add_argument("--source", required=True, type=Path)
    sqlite_parser.add_argument("--asset-id", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Execute the governed Registry backup workflow.",
    )
    run_parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Local path to the authoritative Registry SQLite database.",
    )
    run_parser.add_argument(
        "--asset-id",
        default=DEFAULT_REGISTRY_ASSET_ID,
        help=f"Stable Registry asset identifier (default: {DEFAULT_REGISTRY_ASSET_ID}).",
    )
    run_parser.add_argument(
        "--destination-root",
        type=Path,
        default=None,
        help=(
            "Accepted Registry destination root (default: <repository_root>/Registry/POERegistry)."
        ),
    )

    acceptance_parser = subparsers.add_parser(
        "acceptance-run",
        help="Execute and verify an end-to-end operational acceptance run.",
    )
    acceptance_parser.add_argument("--source", required=True, type=Path)
    acceptance_parser.add_argument(
        "--asset-id",
        default=DEFAULT_REGISTRY_ASSET_ID,
    )
    acceptance_parser.add_argument("--destination-root", type=Path, default=None)
    acceptance_parser.add_argument("--evidence-root", type=Path, default=None)

    restore_parser = subparsers.add_parser(
        "restore",
        help="Inspect governed Registry recovery points.",
    )
    restore_subparsers = restore_parser.add_subparsers(dest="restore_command")

    restore_list_parser = restore_subparsers.add_parser(
        "list",
        help="List discovered Registry recovery points.",
    )
    restore_list_parser.add_argument(
        "--destination-root",
        type=Path,
        default=None,
        help=(
            "Accepted Registry destination root (default: <repository_root>/Registry/POERegistry)."
        ),
    )

    restore_show_parser = restore_subparsers.add_parser(
        "show",
        help="Show one discovered Registry recovery point.",
    )
    restore_show_parser.add_argument("--backup-id", required=True)
    restore_show_parser.add_argument(
        "--destination-root",
        type=Path,
        default=None,
        help=(
            "Accepted Registry destination root (default: <repository_root>/Registry/POERegistry)."
        ),
    )

    restore_evaluate_parser = restore_subparsers.add_parser(
        "evaluate",
        help="Evaluate one Registry recovery point for restore eligibility.",
    )
    restore_evaluate_parser.add_argument("--backup-id", required=True)
    restore_evaluate_parser.add_argument(
        "--destination-root",
        type=Path,
        default=None,
        help=(
            "Accepted Registry destination root (default: <repository_root>/Registry/POERegistry)."
        ),
    )

    restore_plan_parser = restore_subparsers.add_parser(
        "plan",
        help="Construct a deterministic, non-executing Registry restore plan.",
    )
    restore_plan_parser.add_argument("--backup-id", required=True)
    restore_plan_parser.add_argument(
        "--target",
        required=True,
        type=Path,
        help="Authoritative Registry SQLite target path proposed for restoration.",
    )
    restore_plan_parser.add_argument(
        "--destination-root",
        type=Path,
        default=None,
        help=(
            "Accepted Registry destination root (default: <repository_root>/Registry/POERegistry)."
        ),
    )
    restore_plan_parser.add_argument(
        "--staging-root",
        type=Path,
        default=None,
        help=(
            "Governed restore planning staging root "
            "(default: <restore_tests_root>/Planning/Staging)."
        ),
    )
    restore_plan_parser.add_argument(
        "--rollback-root",
        type=Path,
        default=None,
        help=("Governed rollback planning root (default: <restore_tests_root>/Planning/Rollback)."),
    )
    restore_plan_parser.add_argument(
        "--eligibility-override",
        action="store_true",
        help="Record an operator request for governed eligibility override.",
    )
    restore_plan_parser.add_argument(
        "--operator-rationale",
        default=None,
        help="Required rationale when --eligibility-override is supplied.",
    )
    return parser


def _print_repository_validation() -> int:
    result = validate_repository()
    print("POE Backup Repository Validation")
    print(f"Command exit code: {result.return_code}")
    print(f"Mounted: {'PASS' if result.mounted else 'FAIL'}")
    print(f"Healthy: {'PASS' if result.healthy else 'FAIL'}")
    print(f"Operational: {'PASS' if result.operational else 'FAIL'}")
    print(f"Result: {'PASS' if result.is_valid else 'FAIL'}")

    if result.standard_output:
        print()
        print("Repository status output:")
        print(result.standard_output)
    if result.standard_error:
        print()
        print("Repository status error output:", file=sys.stderr)
        print(result.standard_error, file=sys.stderr)
    return 0 if result.is_valid else 1


def _require_valid_repository() -> None:
    result = validate_repository()
    if not result.is_valid:
        raise RepositoryValidationError(
            "Backup repository validation failed; backup was not started."
        )


def _print_runtime_state(inspection: RuntimeRecoveryInspection) -> None:
    # Render one stable, human-readable runtime-state inspection.

    print("POE Backup Orchestrator — Runtime State")
    print(f"Recovery outcome: {inspection.outcome.value}")
    print(f"State changed: {'yes' if inspection.state_changed else 'no'}")

    state = inspection.state
    if state is None:
        print("No runtime state present.")
        return

    print(f"Runtime status: {state.status.value}")
    print(f"Execution state: {state.execution_state.value}")
    print(f"Run ID: {state.run_id}")
    print(f"Hostname: {state.hostname}")
    print(f"PID: {state.pid}")
    print(f"Started (UTC): {state.started_at_utc.isoformat()}")
    print(f"Updated (UTC): {state.updated_at_utc.isoformat()}")
    print(f"Environment: {state.environment.value}")


def _restore_destination_root(arguments, repository_root: Path) -> Path:
    destination_root = arguments.destination_root
    if destination_root is not None:
        return destination_root
    return repository_root / "Registry" / "POERegistry"


def _restore_planning_staging_root(arguments, restore_tests_root: Path) -> Path:
    if arguments.staging_root is not None:
        return arguments.staging_root
    return restore_tests_root / "Planning" / "Staging"


def _restore_planning_rollback_root(arguments, restore_tests_root: Path) -> Path:
    if arguments.rollback_root is not None:
        return arguments.rollback_root
    return restore_tests_root / "Planning" / "Rollback"


def _find_recovery_point(
    recovery_points: tuple[RecoveryPoint, ...],
    backup_id: str,
) -> RecoveryPoint | None:
    return next(
        (point for point in recovery_points if point.recovery_point_id == backup_id),
        None,
    )


def _print_recovery_point_list(
    recovery_points: tuple[RecoveryPoint, ...],
    *,
    destination_root: Path,
) -> None:
    print("POE Backup Orchestrator — Recovery Point List")
    print(f"Destination root: {destination_root}")
    print(f"Recovery points discovered: {len(recovery_points)}")

    if not recovery_points:
        print("No recovery points found.")
        return

    for point in recovery_points:
        created = (
            point.created_at_utc.isoformat() if point.created_at_utc is not None else "unknown"
        )
        print(f"{point.recovery_point_id} | {created} | {point.eligibility.classification.value}")


def _print_recovery_point(
    point: RecoveryPoint,
    *,
    heading: str,
) -> None:
    created = point.created_at_utc.isoformat() if point.created_at_utc is not None else "unknown"
    print(f"POE Backup Orchestrator — {heading}")
    print(f"Recovery point: {point.recovery_point_id}")
    print(f"Created (UTC): {created}")
    print(f"Package: {point.package_path}")
    print(f"Manifest: {point.manifest_path or 'unknown'}")
    print(f"Artifact: {point.artifact_path or 'unknown'}")
    print(f"Registry ID: {point.source_registry_id or 'unknown'}")
    print(f"Manifest version: {point.manifest_version or 'unknown'}")
    print(f"Verification: {point.verification_status or 'unknown'}")
    print(f"Quarantined: {'yes' if point.quarantined else 'no'}")
    print(f"Eligibility: {point.eligibility.classification.value}")
    reasons = ", ".join(reason.value for reason in point.eligibility.reason_codes)
    print(f"Reason codes: {reasons}")
    override = "yes" if point.eligibility.override_required else "no"
    print(f"Override required: {override}")
    print(f"Policy version: {point.eligibility.policy_version}")
    for warning in point.eligibility.warnings:
        print(f"Warning: {warning}")


def _print_restore_plan(plan: RestorePlan) -> None:
    print("POE Backup Orchestrator — Restore Plan")
    print(f"Plan ID: {plan.plan_id}")
    print(f"Schema version: {plan.schema_version}")
    print(f"Policy version: {plan.policy_version}")
    print(f"Created (UTC): {plan.created_at_utc.isoformat()}")
    print(f"Recovery point: {plan.recovery_point_id}")
    print(f"Source artifact: {plan.source_artifact_path}")
    print(f"Source manifest: {plan.source_manifest_path}")
    print(f"Authoritative target: {plan.authoritative_target_path}")
    print(f"Staging target: {plan.staging_target_path}")
    print(f"Rollback artifact: {plan.rollback_artifact_path}")
    print(f"Readiness: {plan.validation.readiness.value}")
    reasons = ", ".join(reason.value for reason in plan.validation.reason_codes)
    print(f"Reason codes: {reasons}")
    print(f"Approval required: {'yes' if plan.validation.approval_required else 'no'}")
    print(f"Execution authorized: {'yes' if plan.execution_authorized else 'no'}")

    for warning in plan.validation.warnings:
        print(f"Warning [{warning.code}]: {warning.message}")
    for conflict in plan.validation.conflicts:
        print(
            f"Conflict [{conflict.code}]: {conflict.message} "
            f"(blocking={'yes' if conflict.blocking else 'no'}, "
            f"approval-resolvable={'yes' if conflict.approval_can_resolve else 'no'})"
        )

    print("Planned actions:")
    for action in plan.actions:
        print(f"  {action.ordinal}. {action.action_type.value}: {action.description}")
        if action.source_path is not None:
            print(f"     Source: {action.source_path}")
        if action.destination_path is not None:
            print(f"     Destination: {action.destination_path}")
        print(f"     Mutates state: {'yes' if action.mutates_state else 'no'}")
        print(f"     Approval required: {'yes' if action.approval_required else 'no'}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.command is None:
        parser.print_help()
        return 0

    try:
        requested_environment = (
            None
            if arguments.environment is None
            else RuntimeEnvironment.parse(arguments.environment)
        )
        context = bootstrap_application(
            arguments.config,
            environment=requested_environment,
        )

        if arguments.command == "status":
            print("POE Backup Orchestrator")
            print(f"Version: {__version__}")
            print(f"Environment: {context.config.application.environment.value}")
            print(f"Configuration: {context.config_path}")
            print(f"State root: {context.runtime.state_root}")
            print(f"Log root: {context.runtime.log_root}")
            print(f"Repository: {context.config.paths.repository_root}")
            print("State: BOOTSTRAP_READY")
            return 0

        if arguments.command == "runtime-state":
            inspector = build_runtime_recovery_inspector(
                state_root=context.runtime.state_root,
            )
            _print_runtime_state(inspector.inspect())
            return 0

        if arguments.command == "validate-repository":
            return _print_repository_validation()

        if arguments.command == "backup-sqlite":
            _require_valid_repository()
            result = create_sqlite_backup(
                source_path=arguments.source,
                staging_root=context.config.paths.staging_root,
                asset_id=arguments.asset_id,
            )
            print("POE SQLite Backup")
            print(f"Asset: {result.asset_id}")
            print(f"Source: {result.source_path}")
            print(f"Backup: {result.backup_path}")
            print(f"Manifest: {result.manifest_path}")
            print(f"Size: {result.size_bytes} bytes")
            print(f"SHA-256: {result.sha256}")
            print(f"SQLite integrity check: {result.integrity_check}")
            print("Result: PASS")
            return 0

        if arguments.command == "run":
            destination_root = arguments.destination_root
            if destination_root is None:
                destination_root = context.config.paths.repository_root / "Registry" / "POERegistry"

            service = build_registry_backup_run_service(
                source_path=arguments.source,
                staging_root=context.config.paths.staging_root,
                reports_root=context.config.paths.reports_root / "Backup-Orchestrator",
                destination_root=destination_root,
                asset_id=arguments.asset_id,
                state_root=context.runtime.state_root,
                environment=context.runtime.environment,
            )
            run_result = service.execute(RegistryBackupRequest(source_path=arguments.source))
            print(run_result.summary, end="")
            print(f"JSON report: {run_result.publication.json_path}")
            print(f"Text report: {run_result.publication.summary_path}")
            return run_result.exit_code

        if arguments.command == "acceptance-run":
            destination_root = arguments.destination_root
            if destination_root is None:
                destination_root = context.config.paths.repository_root / "Registry" / "POERegistry"
            evidence_root = arguments.evidence_root
            if evidence_root is None:
                evidence_root = (
                    context.config.paths.reports_root / "Backup-Orchestrator" / "Acceptance"
                )
            run_service = build_registry_backup_run_service(
                source_path=arguments.source,
                staging_root=context.config.paths.staging_root,
                reports_root=context.config.paths.reports_root / "Backup-Orchestrator",
                destination_root=destination_root,
                asset_id=arguments.asset_id,
                state_root=context.runtime.state_root,
                environment=context.runtime.environment,
            )
            acceptance_service = OperationalAcceptanceService(
                run_service=run_service,
                evidence_root=evidence_root,
                clock=run_service.clock,
                repository_validator=validate_repository,
            )
            result = acceptance_service.execute(RegistryBackupRequest(source_path=arguments.source))
            print(result.summary, end="")
            print(f"Acceptance JSON: {result.publication.json_path}")
            print(f"Acceptance text: {result.publication.summary_path}")
            return result.evidence.exit_code

        if arguments.command == "restore":
            if arguments.restore_command is None:
                restore_parser = next(
                    action
                    for action in parser._actions
                    if isinstance(action, argparse._SubParsersAction)
                ).choices["restore"]
                restore_parser.print_help()
                return 0

            destination_root = _restore_destination_root(
                arguments,
                context.config.paths.repository_root,
            )
            evaluated_at_utc = datetime.now(UTC)
            recovery_points = discover_recovery_points(
                destination_root,
                evaluated_at_utc=evaluated_at_utc,
            )

            if arguments.restore_command == "list":
                _print_recovery_point_list(
                    recovery_points,
                    destination_root=destination_root,
                )
                return 0

            point = _find_recovery_point(
                recovery_points,
                arguments.backup_id,
            )
            if point is None:
                print(
                    f"ERROR: Recovery point not found: {arguments.backup_id}",
                    file=sys.stderr,
                )
                return 1

            if arguments.restore_command == "show":
                _print_recovery_point(point, heading="Recovery Point")
                return 0

            if arguments.restore_command == "evaluate":
                evaluated = evaluate_recovery_point(
                    point,
                    evaluated_at_utc=evaluated_at_utc,
                )
                _print_recovery_point(
                    evaluated,
                    heading="Recovery Point Eligibility",
                )
                return 0

            if arguments.restore_command == "plan":
                if arguments.eligibility_override and not (
                    arguments.operator_rationale and arguments.operator_rationale.strip()
                ):
                    print(
                        "ERROR: --operator-rationale is required when "
                        "--eligibility-override is supplied.",
                        file=sys.stderr,
                    )
                    return 1

                evaluated = evaluate_recovery_point(
                    point,
                    evaluated_at_utc=evaluated_at_utc,
                )
                request = RestorePlanRequest(
                    recovery_point_id=evaluated.recovery_point_id,
                    authoritative_target_path=arguments.target,
                    staging_root=_restore_planning_staging_root(
                        arguments,
                        context.config.paths.restore_tests_root,
                    ),
                    rollback_root=_restore_planning_rollback_root(
                        arguments,
                        context.config.paths.restore_tests_root,
                    ),
                    eligibility_override_requested=arguments.eligibility_override,
                    operator_rationale=arguments.operator_rationale,
                )
                plan = build_restore_plan(
                    evaluated,
                    request,
                    created_at_utc=evaluated_at_utc,
                )
                _print_restore_plan(plan)
                return 0

    except (RecoveryPointDiscoveryError, RestorePlanningError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OperationalReportingError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return REPORTING_FAILURE_EXIT_CODE
    except OrchestratorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unsupported command: {arguments.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
