"""Application bootstrap support for the POE Backup Orchestrator."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from poe_backup_orchestrator.config import (
    OrchestratorConfig,
    load_configuration,
)
from poe_backup_orchestrator.utilities.logging import configure_logging

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApplicationContext:
    """Runtime dependencies and validated application state."""

    config_path: Path
    config: OrchestratorConfig


def bootstrap_application(config_path: Path) -> ApplicationContext:
    """Initialize logging, load configuration, and return application context."""
    configure_logging()

    LOGGER.info("Initializing POE Backup Orchestrator")
    LOGGER.info("Loading configuration from %s", config_path)

    config = load_configuration(config_path)

    LOGGER.info(
        "Configuration loaded for environment %s",
        config.application.environment,
    )

    return ApplicationContext(
        config_path=config_path,
        config=config,
    )
