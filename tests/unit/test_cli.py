"""Unit tests for the Backup Orchestrator command-line interface."""

from pathlib import Path

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.cli import main


def write_test_config(path: Path) -> None:
    """Write a valid test configuration file."""
    path.write_text(
        """
[application]
name = "poe-backup-orchestrator"
environment = "test"

[paths]
repository_root = "/tmp/repository"
staging_root = "/tmp/staging"
reports_root = "/tmp/reports"
logs_root = "/tmp/logs"
restore_tests_root = "/tmp/restore-tests"
quarantine_root = "/tmp/quarantine"
""".strip(),
        encoding="utf-8",
    )


def test_version_is_initial_baseline() -> None:
    """Confirm the initial application version."""
    assert __version__ == "0.1.0"


def test_status_command_reports_bootstrap_state(
    tmp_path: Path,
    capsys,
) -> None:
    """Confirm status loads configuration and reports bootstrap readiness."""
    config_path = tmp_path / "orchestrator.toml"
    write_test_config(config_path)

    exit_code = main(
        [
            "--config",
            str(config_path),
            "status",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "POE Backup Orchestrator" in captured.out
    assert "Version: 0.1.0" in captured.out
    assert "Environment: test" in captured.out
    assert "Repository: /tmp/repository" in captured.out
    assert "State: BOOTSTRAP_READY" in captured.out


def test_status_returns_error_for_missing_configuration(
    tmp_path: Path,
    capsys,
) -> None:
    """Confirm a missing configuration produces a controlled error."""
    missing_path = tmp_path / "missing.toml"

    exit_code = main(
        [
            "--config",
            str(missing_path),
            "status",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Configuration file not found" in captured.err
