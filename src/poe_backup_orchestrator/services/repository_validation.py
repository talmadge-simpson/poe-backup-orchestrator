"""Backup repository validation service."""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Sequence
from typing import Any

from poe_backup_orchestrator.exceptions import RepositoryValidationError
from poe_backup_orchestrator.models import RepositoryValidationResult

DEFAULT_REPOSITORY_COMMAND = (
    "sudo",
    "-n",
    "/usr/local/sbin/poe-backup-repository",
    "--status",
)

_REPOSITORY_STATE_BLOCK = re.compile(
    r"===== REPOSITORY STATE =====\s*(\{.*?\})\s*===== CAPACITY =====",
    re.DOTALL,
)


def _extract_repository_state(output: str) -> dict[str, Any]:
    """Extract and decode the repository-state JSON object."""
    match = _REPOSITORY_STATE_BLOCK.search(output)

    if match is None:
        return {}

    try:
        decoded = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}

    return decoded if isinstance(decoded, dict) else {}


def validate_repository(
    command: Sequence[str] = DEFAULT_REPOSITORY_COMMAND,
) -> RepositoryValidationResult:
    """Execute the repository status command and interpret its result."""
    normalized_command = tuple(command)

    if not normalized_command:
        raise RepositoryValidationError("Repository validation command must not be empty.")

    try:
        completed_process = subprocess.run(
            normalized_command,
            capture_output=True,
            check=False,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RepositoryValidationError(
            f"Repository validation command not found: {normalized_command[0]}"
        ) from exc
    except OSError as exc:
        raise RepositoryValidationError(
            f"Unable to execute repository validation command: {exc}"
        ) from exc

    standard_output = completed_process.stdout.strip()
    standard_error = completed_process.stderr.strip()

    repository_state = _extract_repository_state(standard_output)

    mounted = (
        "/srv/poe-backup" in standard_output
        and "/dev/sdb1" in standard_output
        and "ext4" in standard_output
    )

    healthy = repository_state.get("health") == "Healthy"

    operational = (
        repository_state.get("state") == "OPERATIONAL_BASELINE"
        and repository_state.get("operational_baseline") is True
        and repository_state.get("promotion") == "Operational Baseline"
    )

    return RepositoryValidationResult(
        command=normalized_command,
        return_code=completed_process.returncode,
        mounted=mounted,
        healthy=healthy,
        operational=operational,
        standard_output=standard_output,
        standard_error=standard_error,
    )
