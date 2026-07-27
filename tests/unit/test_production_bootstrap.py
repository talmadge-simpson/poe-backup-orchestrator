"""Tests for production-aware application bootstrap."""

from pathlib import Path

import pytest

from poe_backup_orchestrator.bootstrap import bootstrap_application
from poe_backup_orchestrator.exceptions import BootstrapError
from poe_backup_orchestrator.models.runtime import RuntimeEnvironment


def write_config(path: Path, environment: str) -> None:
    path.write_text(
        f"""
[application]
name = "poe-backup-orchestrator"
environment = "{environment}"

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


def test_bootstrap_uses_configured_test_runtime(tmp_path: Path) -> None:
    config = tmp_path / "orchestrator.toml"
    write_config(config, "test")
    context = bootstrap_application(config)
    assert context.runtime.environment is RuntimeEnvironment.TEST
    assert context.runtime_validation is None


def test_bootstrap_rejects_requested_environment_mismatch(tmp_path: Path) -> None:
    config = tmp_path / "orchestrator.toml"
    write_config(config, "development")
    with pytest.raises(BootstrapError, match="does not match"):
        bootstrap_application(
            config,
            environment=RuntimeEnvironment.PRODUCTION,
            validate_production_runtime=False,
        )
