"""Tests for runtime validation behavior."""

from pathlib import Path

import pytest

from poe_backup_orchestrator.exceptions import BootstrapError
from poe_backup_orchestrator.models.runtime import RuntimeDescriptor, RuntimeEnvironment
from poe_backup_orchestrator.services.runtime_validation import (
    require_valid_runtime,
    validate_runtime,
)


def test_validate_runtime_proves_filesystem_capability(tmp_path: Path) -> None:
    config = tmp_path / "orchestrator.toml"
    config.write_text("[application]\n", encoding="utf-8")
    state = tmp_path / "state"
    logs = tmp_path / "logs"
    repository = tmp_path / "repository"
    state.mkdir()
    logs.mkdir()
    repository.mkdir()

    descriptor = RuntimeDescriptor(
        RuntimeEnvironment.TEST,
        config,
        state,
        logs,
        "root",
        "root",
    )
    result = validate_runtime(descriptor, repository_paths=(repository,))

    assert result.is_valid
    assert not list(state.glob(".poe-runtime-validation-*"))
    assert not list(logs.glob(".poe-runtime-validation-*"))


def test_require_valid_runtime_raises_controlled_error(tmp_path: Path) -> None:
    descriptor = RuntimeDescriptor(
        RuntimeEnvironment.TEST,
        tmp_path / "missing.toml",
        tmp_path / "missing-state",
        tmp_path / "missing-log",
        "root",
        "root",
    )
    with pytest.raises(BootstrapError, match="Runtime validation failed"):
        require_valid_runtime(validate_runtime(descriptor))
