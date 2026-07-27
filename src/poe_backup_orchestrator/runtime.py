"""Runtime discovery and deterministic environment selection."""

from __future__ import annotations

from pathlib import Path

from poe_backup_orchestrator.models.runtime import RuntimeDescriptor, RuntimeEnvironment

DEVELOPMENT_CONFIG_PATH = Path("config/orchestrator.toml")
PRODUCTION_CONFIG_PATH = Path("/etc/poe/backup-orchestrator/orchestrator.toml")
DEVELOPMENT_STATE_ROOT = Path(".runtime/state")
DEVELOPMENT_LOG_ROOT = Path(".runtime/log")
PRODUCTION_STATE_ROOT = Path("/var/lib/poe/backup/orchestrator")
PRODUCTION_LOG_ROOT = Path("/var/log/poe/backup/orchestrator")


def discover_runtime(
    environment: RuntimeEnvironment,
    *,
    config_path: Path | None = None,
) -> RuntimeDescriptor:
    """Resolve one explicit environment into its authoritative descriptor."""
    if environment is RuntimeEnvironment.PRODUCTION:
        return RuntimeDescriptor(
            environment=environment,
            config_path=config_path or PRODUCTION_CONFIG_PATH,
            state_root=PRODUCTION_STATE_ROOT,
            log_root=PRODUCTION_LOG_ROOT,
            service_account="poe-backup",
            service_group="poe-backup",
        )

    return RuntimeDescriptor(
        environment=environment,
        config_path=config_path or DEVELOPMENT_CONFIG_PATH,
        state_root=DEVELOPMENT_STATE_ROOT,
        log_root=DEVELOPMENT_LOG_ROOT,
        service_account="talmadge",
        service_group="talmadge",
    )
