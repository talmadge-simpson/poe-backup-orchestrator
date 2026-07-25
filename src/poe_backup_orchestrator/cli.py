"""Command-line interface for the POE Backup Orchestrator."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.bootstrap import bootstrap_application
from poe_backup_orchestrator.exceptions import OrchestratorError
from poe_backup_orchestrator.services import validate_repository

DEFAULT_CONFIG_PATH = Path("config/orchestrator.toml")


def build_parser() -> argparse.ArgumentParser:
    """Create and return the command-line argument parser."""
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
        default=DEFAULT_CONFIG_PATH,
        help=(f"Path to the orchestrator TOML configuration file (default: {DEFAULT_CONFIG_PATH})"),
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "status",
        help="Display the current orchestrator status.",
    )

    subparsers.add_parser(
        "validate-repository",
        help="Validate the managed backup repository.",
    )

    return parser


def _print_repository_validation() -> int:
    """Validate the repository and print a structured result."""
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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Backup Orchestrator command-line interface."""
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.command is None:
        parser.print_help()
        return 0

    try:
        context = bootstrap_application(arguments.config)

        if arguments.command == "status":
            print("POE Backup Orchestrator")
            print(f"Version: {__version__}")
            print(f"Environment: {context.config.application.environment}")
            print(f"Repository: {context.config.paths.repository_root}")
            print("State: BOOTSTRAP_READY")
            return 0

        if arguments.command == "validate-repository":
            return _print_repository_validation()

    except OrchestratorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    parser.error(f"Unsupported command: {arguments.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
