"""Unit tests for the Backup Orchestrator command-line interface."""

from poe_backup_orchestrator import __version__
from poe_backup_orchestrator.cli import main


def test_version_is_initial_baseline() -> None:
    """Confirm the initial application version."""
    assert __version__ == "0.1.0"


def test_status_command_reports_development_baseline(capsys) -> None:
    """Confirm the status command produces the expected baseline output."""
    exit_code = main(["status"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "POE Backup Orchestrator" in captured.out
    assert "Version: 0.1.0" in captured.out
    assert "State: DEVELOPMENT_BASELINE" in captured.out
