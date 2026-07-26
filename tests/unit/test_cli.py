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


def test_validate_repository_command_reports_success(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Confirm repository validation success is exposed through the CLI."""
    from poe_backup_orchestrator.models import RepositoryValidationResult

    config_path = tmp_path / "orchestrator.toml"
    write_test_config(config_path)

    result = RepositoryValidationResult(
        command=("poe-backup-repository", "--status"),
        return_code=0,
        mounted=True,
        healthy=True,
        operational=True,
        standard_output="Operational Baseline\nHealthy\nRepository is mounted",
        standard_error="",
    )

    monkeypatch.setattr(
        "poe_backup_orchestrator.cli.validate_repository",
        lambda: result,
    )

    exit_code = main(
        [
            "--config",
            str(config_path),
            "validate-repository",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Mounted: PASS" in captured.out
    assert "Healthy: PASS" in captured.out
    assert "Operational: PASS" in captured.out
    assert "Result: PASS" in captured.out


def test_validate_repository_command_reports_failure(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Confirm repository validation failure returns a nonzero exit code."""
    from poe_backup_orchestrator.models import RepositoryValidationResult

    config_path = tmp_path / "orchestrator.toml"
    write_test_config(config_path)

    result = RepositoryValidationResult(
        command=("poe-backup-repository", "--status"),
        return_code=1,
        mounted=False,
        healthy=False,
        operational=False,
        standard_output="Repository unavailable",
        standard_error="",
    )

    monkeypatch.setattr(
        "poe_backup_orchestrator.cli.validate_repository",
        lambda: result,
    )

    exit_code = main(
        [
            "--config",
            str(config_path),
            "validate-repository",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Result: FAIL" in captured.out


def test_run_command_delegates_to_run_service(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Confirm CLI forwards runtime paths and prints published evidence."""
    from dataclasses import dataclass

    from poe_backup_orchestrator.models.operational_report import (
        OperationalReportPublication,
    )

    config_path = tmp_path / "orchestrator.toml"
    write_test_config(config_path)
    source = tmp_path / "registry.sqlite3"
    source.touch()
    received = {}

    @dataclass
    class FakeRunResult:
        summary: str
        publication: OperationalReportPublication
        exit_code: int

    class FakeService:
        def execute(self, request):
            received["request"] = request
            return FakeRunResult(
                summary="POE Backup Orchestrator — Registry Backup Report\nOutcome: succeeded\n",
                publication=OperationalReportPublication(
                    json_path=Path("/reports/report.json"),
                    summary_path=Path("/reports/report.txt"),
                ),
                exit_code=0,
            )

    def fake_builder(**kwargs):
        received.update(kwargs)
        return FakeService()

    monkeypatch.setattr(
        "poe_backup_orchestrator.cli.build_registry_backup_run_service",
        fake_builder,
    )

    exit_code = main(
        [
            "--config",
            str(config_path),
            "run",
            "--source",
            str(source),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert received["source_path"] == source
    assert received["staging_root"] == Path("/tmp/staging")
    assert received["reports_root"] == Path("/tmp/reports/Backup-Orchestrator")
    assert received["destination_root"] == Path("/tmp/repository/Registry/POERegistry")
    assert received["asset_id"] == "poeregistry"
    assert received["request"].source_path == source
    assert "Outcome: succeeded" in captured.out
    assert "JSON report: /reports/report.json" in captured.out
    assert "Text report: /reports/report.txt" in captured.out


def test_run_command_returns_reporting_failure_exit_code(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    """Confirm report publication failure returns the stable CLI exit code."""
    from poe_backup_orchestrator.exceptions import OperationalReportingError

    config_path = tmp_path / "orchestrator.toml"
    write_test_config(config_path)
    source = tmp_path / "registry.sqlite3"
    source.touch()

    class FakeService:
        def execute(self, request):
            del request
            raise OperationalReportingError("publication failed")

    monkeypatch.setattr(
        "poe_backup_orchestrator.cli.build_registry_backup_run_service",
        lambda **kwargs: FakeService(),
    )

    exit_code = main(
        [
            "--config",
            str(config_path),
            "run",
            "--source",
            str(source),
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 60
    assert "publication failed" in captured.err
