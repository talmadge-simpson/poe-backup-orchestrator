"""Tests for deterministic runtime discovery."""

from pathlib import Path

from poe_backup_orchestrator.models.runtime import RuntimeEnvironment
from poe_backup_orchestrator.runtime import (
    PRODUCTION_CONFIG_PATH,
    PRODUCTION_LOG_ROOT,
    PRODUCTION_STATE_ROOT,
    discover_runtime,
)


def test_discover_production_runtime_uses_authoritative_paths() -> None:
    descriptor = discover_runtime(RuntimeEnvironment.PRODUCTION)
    assert descriptor.config_path == PRODUCTION_CONFIG_PATH
    assert descriptor.state_root == PRODUCTION_STATE_ROOT
    assert descriptor.log_root == PRODUCTION_LOG_ROOT
    assert descriptor.service_account == "poe-backup"


def test_discover_runtime_honors_explicit_config_path() -> None:
    descriptor = discover_runtime(
        RuntimeEnvironment.DEVELOPMENT,
        config_path=Path("/tmp/orchestrator.toml"),
    )
    assert descriptor.config_path == Path("/tmp/orchestrator.toml")
