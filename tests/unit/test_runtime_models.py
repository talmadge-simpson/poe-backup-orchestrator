"""Tests for runtime domain models."""

from pathlib import Path

import pytest

from poe_backup_orchestrator.models.runtime import (
    RuntimeDescriptor,
    RuntimeEnvironment,
    RuntimeValidationCheck,
    RuntimeValidationResult,
)


def test_runtime_environment_parses_supported_values() -> None:
    assert RuntimeEnvironment.parse(" Production ") is RuntimeEnvironment.PRODUCTION
    assert RuntimeEnvironment.parse("development") is RuntimeEnvironment.DEVELOPMENT
    assert RuntimeEnvironment.parse("test") is RuntimeEnvironment.TEST


def test_runtime_environment_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="unsupported runtime environment"):
        RuntimeEnvironment.parse("staging")


def test_runtime_descriptor_normalizes_paths() -> None:
    descriptor = RuntimeDescriptor(
        RuntimeEnvironment.DEVELOPMENT,
        "config/orchestrator.toml",
        ".runtime/state",
        ".runtime/log",
        "talmadge",
        "talmadge",
    )
    assert descriptor.config_path == Path("config/orchestrator.toml")
    assert descriptor.state_root == Path(".runtime/state")


def test_runtime_validation_result_requires_all_checks_to_pass() -> None:
    descriptor = RuntimeDescriptor(
        RuntimeEnvironment.TEST,
        "/tmp/config",
        "/tmp/state",
        "/tmp/log",
        "test",
        "test",
    )
    result = RuntimeValidationResult(
        descriptor,
        (
            RuntimeValidationCheck("one", True, "passed"),
            RuntimeValidationCheck("two", False, "failed"),
        ),
    )
    assert not result.is_valid
