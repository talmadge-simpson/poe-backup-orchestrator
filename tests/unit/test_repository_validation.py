"""Unit tests for repository validation."""

from __future__ import annotations

import subprocess

import pytest

from poe_backup_orchestrator.exceptions import RepositoryValidationError
from poe_backup_orchestrator.services.repository_validation import (
    DEFAULT_REPOSITORY_COMMAND,
    validate_repository,
)

VALID_STATUS_OUTPUT = """
2026-07-25T09:58:55-04:00 [PASS] Validated volume /dev/sdb1: ext4.
===== REPOSITORY MANAGER =====
Component: POE Backup Repository Manager
Version: 1.0.4

===== FILESYSTEM =====
TARGET          SOURCE    FSTYPE OPTIONS
/srv/poe-backup /dev/sdb1 ext4   rw,relatime

===== REPOSITORY STATE =====
{
    "subsystem": "POE Backup Repository",
    "version": "1.0.4",
    "state": "OPERATIONAL_BASELINE",
    "health": "Healthy",
    "promotion": "Operational Baseline",
    "last_validation": "2026-07-22T14:54:00-04:00",
    "operational_baseline": true
}

===== CAPACITY =====
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sdb1      ext4  3.6T  2.2M  3.6T   1% /srv/poe-backup
""".strip()


def test_default_command_uses_noninteractive_sudo() -> None:
    """Confirm automation uses the approved privileged command."""
    assert DEFAULT_REPOSITORY_COMMAND == (
        "sudo",
        "-n",
        "/usr/local/sbin/poe-backup-repository",
        "--status",
    )


def test_validate_repository_reports_valid_state(monkeypatch) -> None:
    """Confirm actual operational repository output passes validation."""

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=VALID_STATUS_OUTPUT,
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = validate_repository()

    assert result.return_code == 0
    assert result.mounted is True
    assert result.healthy is True
    assert result.operational is True
    assert result.is_valid is True


def test_validate_repository_reports_invalid_state(monkeypatch) -> None:
    """Confirm non-operational repository state fails validation."""

    invalid_output = VALID_STATUS_OUTPUT.replace(
        '"state": "OPERATIONAL_BASELINE"',
        '"state": "INITIALIZED_NOT_PROMOTED"',
    ).replace(
        '"operational_baseline": true',
        '"operational_baseline": false',
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=1,
            stdout=invalid_output,
            stderr="",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = validate_repository()

    assert result.return_code == 1
    assert result.operational is False
    assert result.is_valid is False


def test_validate_repository_rejects_missing_command(monkeypatch) -> None:
    """Confirm a missing repository command raises a controlled error."""

    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(
        RepositoryValidationError,
        match="Repository validation command not found",
    ):
        validate_repository()


def test_validate_repository_rejects_empty_command() -> None:
    """Confirm an empty validation command is rejected."""
    with pytest.raises(
        RepositoryValidationError,
        match="must not be empty",
    ):
        validate_repository(())
