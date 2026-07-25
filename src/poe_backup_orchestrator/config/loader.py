"""TOML configuration loader for the POE Backup Orchestrator."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.config.models import (
    ApplicationConfig,
    OrchestratorConfig,
    PathConfig,
)
from poe_backup_orchestrator.exceptions import ConfigurationError


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    """Return a required nested configuration mapping."""
    value = data.get(key)

    if not isinstance(value, dict):
        raise ConfigurationError(f"Missing or invalid configuration section: {key}")

    return value


def _required_string(data: dict[str, Any], key: str, section: str) -> str:
    """Return a required non-empty string value."""
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Missing or invalid configuration value: {section}.{key}")

    return value.strip()


def load_configuration(path: Path) -> OrchestratorConfig:
    """Load and validate orchestrator configuration from a TOML file."""
    if not path.is_file():
        raise ConfigurationError(f"Configuration file not found: {path}")

    try:
        with path.open("rb") as configuration_file:
            raw_config = tomllib.load(configuration_file)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationError(f"Invalid TOML configuration in {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigurationError(f"Unable to read configuration file {path}: {exc}") from exc

    application_data = _required_mapping(raw_config, "application")
    paths_data = _required_mapping(raw_config, "paths")

    application = ApplicationConfig(
        name=_required_string(application_data, "name", "application"),
        environment=_required_string(
            application_data,
            "environment",
            "application",
        ),
    )

    paths = PathConfig(
        repository_root=Path(_required_string(paths_data, "repository_root", "paths")),
        staging_root=Path(_required_string(paths_data, "staging_root", "paths")),
        reports_root=Path(_required_string(paths_data, "reports_root", "paths")),
        logs_root=Path(_required_string(paths_data, "logs_root", "paths")),
        restore_tests_root=Path(_required_string(paths_data, "restore_tests_root", "paths")),
        quarantine_root=Path(_required_string(paths_data, "quarantine_root", "paths")),
    )

    return OrchestratorConfig(
        application=application,
        paths=paths,
    )
