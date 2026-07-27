"""Unit tests for the orchestrator configuration loader."""

from pathlib import Path

import pytest

from poe_backup_orchestrator.config import load_configuration
from poe_backup_orchestrator.exceptions import ConfigurationError
from poe_backup_orchestrator.models.runtime import RuntimeEnvironment


def test_load_configuration_returns_typed_model(tmp_path: Path) -> None:
    """Confirm a valid TOML file is converted to typed configuration."""
    config_path = tmp_path / "orchestrator.toml"
    config_path.write_text(
        """
[application]
name = "poe-backup-orchestrator"
environment = "test"

[paths]
repository_root = "/srv/test"
staging_root = "/srv/test/Staging"
reports_root = "/srv/test/Reports"
logs_root = "/srv/test/Logs"
restore_tests_root = "/srv/test/Restore-Tests"
quarantine_root = "/srv/test/Quarantine"
""".strip(),
        encoding="utf-8",
    )

    config = load_configuration(config_path)

    assert config.application.name == "poe-backup-orchestrator"
    assert config.application.environment is RuntimeEnvironment.TEST
    assert config.paths.repository_root == Path("/srv/test")


def test_load_configuration_rejects_missing_file(tmp_path: Path) -> None:
    """Confirm a missing configuration file is rejected."""
    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        load_configuration(tmp_path / "missing.toml")


def test_load_configuration_rejects_missing_section(tmp_path: Path) -> None:
    """Confirm required configuration sections are enforced."""
    config_path = tmp_path / "orchestrator.toml"
    config_path.write_text(
        """
[application]
name = "poe-backup-orchestrator"
environment = "test"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigurationError,
        match="Missing or invalid configuration section: paths",
    ):
        load_configuration(config_path)
