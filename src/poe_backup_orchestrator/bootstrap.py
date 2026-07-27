"""Application bootstrap support for the POE Backup Orchestrator."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from poe_backup_orchestrator.config import OrchestratorConfig, load_configuration
from poe_backup_orchestrator.exceptions import BootstrapError
from poe_backup_orchestrator.models.runtime import (
    RuntimeDescriptor,
    RuntimeEnvironment,
    RuntimeValidationResult,
)
from poe_backup_orchestrator.runtime import discover_runtime
from poe_backup_orchestrator.services.runtime_validation import (
    require_valid_runtime,
    validate_runtime,
)
from poe_backup_orchestrator.utilities.logging import configure_logging

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ApplicationContext:
    config_path: Path
    config: OrchestratorConfig
    runtime: RuntimeDescriptor
    runtime_validation: RuntimeValidationResult | None = None


def bootstrap_application(
    config_path: Path | None = None,
    *,
    environment: RuntimeEnvironment | None = None,
    validate_production_runtime: bool = True,
) -> ApplicationContext:
    """Discover runtime, load configuration, and validate production bootstrap."""
    configure_logging()
    selected_environment = environment or RuntimeEnvironment.DEVELOPMENT
    provisional_runtime = discover_runtime(selected_environment, config_path=config_path)

    LOGGER.info("Initializing POE Backup Orchestrator")
    LOGGER.info("Loading configuration from %s", provisional_runtime.config_path)
    config = load_configuration(provisional_runtime.config_path)

    if environment is not None and config.application.environment is not environment:
        raise BootstrapError(
            "Requested runtime environment "
            f"{environment.value!r} does not match configuration environment "
            f"{config.application.environment.value!r}."
        )

    runtime = discover_runtime(
        config.application.environment,
        config_path=provisional_runtime.config_path,
    )
    runtime_validation = None

    if (
        config.application.environment is RuntimeEnvironment.PRODUCTION
        and validate_production_runtime
    ):
        runtime_validation = validate_runtime(
            runtime,
            repository_paths=(
                config.paths.staging_root,
                config.paths.reports_root,
                config.paths.logs_root,
                config.paths.restore_tests_root,
                config.paths.quarantine_root,
            ),
        )
        require_valid_runtime(runtime_validation)

    return ApplicationContext(
        config_path=runtime.config_path,
        config=config,
        runtime=runtime,
        runtime_validation=runtime_validation,
    )
