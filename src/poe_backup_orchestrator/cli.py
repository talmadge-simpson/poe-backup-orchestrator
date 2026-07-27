"""Command-line interface for the POE Backup Orchestrator."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.bootstrap import bootstrap_application
from poe_backup_orchestrator.exceptions import (
    OperationalReportingError,
    OrchestratorError,
    RepositoryValidationError,
)
from poe_backup_orchestrator.models import RegistryBackupRequest, RuntimeEnvironment
from poe_backup_orchestrator.services import (
    REPORTING_FAILURE_EXIT_CODE,
    OperationalAcceptanceService,
    build_registry_backup_run_service,
    create_sqlite_backup,
    validate_repository,
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
