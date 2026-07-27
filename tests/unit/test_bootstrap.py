"""Unit tests for application bootstrap."""

from pathlib import Path

from poe_backup_orchestrator.bootstrap import bootstrap_application
from poe_backup_orchestrator.models.runtime import RuntimeEnvironment


def test_bootstrap_returns_application_context(tmp_path: Path) -> None:
    """Confirm bootstrap returns validated runtime context."""
    config_path = tmp_path / "orchestrator.toml"
    config_path.write_text(
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

    context = bootstrap_application(config_path)

    assert context.config_path == config_path
    assert context.config.application.environment is RuntimeEnvironment.TEST
    assert context.config.paths.repository_root == Path("/tmp/repository")
