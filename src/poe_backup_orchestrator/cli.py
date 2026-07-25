"""Command-line interface for the POE Backup Orchestrator."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.bootstrap import bootstrap_application
from poe_backup_orchestrator.exceptions import OrchestratorError

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

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Backup Orchestrator command-line interface."""
    parser = build_parser()
    arguments = parser.parse_args(argv)

    if arguments.command is None:
        parser.print_help()
        return 0

    try:
        context = bootstrap_application(arguments.config)
    except OrchestratorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if arguments.command == "status":
        print("POE Backup Orchestrator")
        print(f"Version: {__version__}")
        print(f"Environment: {context.config.application.environment}")
        print(f"Repository: {context.config.paths.repository_root}")
        print("State: BOOTSTRAP_READY")
        return 0

    parser.error(f"Unsupported command: {arguments.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
