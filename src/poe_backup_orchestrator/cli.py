"""Command-line interface for the POE Backup Orchestrator."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from poe_backup_orchestrator import __version__


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

    if arguments.command == "status":
        print("POE Backup Orchestrator")
        print(f"Version: {__version__}")
        print("State: DEVELOPMENT_BASELINE")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
