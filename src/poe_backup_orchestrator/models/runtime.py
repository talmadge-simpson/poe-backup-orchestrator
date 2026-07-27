"""Production runtime identity, path, and validation models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class RuntimeEnvironment(StrEnum):
    """Supported execution environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

    @classmethod
    def parse(cls, value: str) -> RuntimeEnvironment:
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            supported = ", ".join(item.value for item in cls)
            raise ValueError(
                f"unsupported runtime environment {value!r}; expected one of: {supported}"
            ) from exc


@dataclass(frozen=True, slots=True)
class RuntimeDescriptor:
    """Resolved runtime contract used by application bootstrap."""

    environment: RuntimeEnvironment
    config_path: Path
    state_root: Path
    log_root: Path
    service_account: str
    service_group: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "config_path", Path(self.config_path))
        object.__setattr__(self, "state_root", Path(self.state_root))
        object.__setattr__(self, "log_root", Path(self.log_root))
        account = self.service_account.strip()
        group = self.service_group.strip()
        if not account:
            raise ValueError("service_account must not be empty")
        if not group:
            raise ValueError("service_group must not be empty")
        object.__setattr__(self, "service_account", account)
        object.__setattr__(self, "service_group", group)


@dataclass(frozen=True, slots=True)
class RuntimeValidationCheck:
    """One deterministic runtime validation assertion."""

    name: str
    passed: bool
    detail: str

    def __post_init__(self) -> None:
        name = self.name.strip()
        detail = self.detail.strip()
        if not name:
            raise ValueError("runtime validation check name must not be empty")
        if not detail:
            raise ValueError("runtime validation check detail must not be empty")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "detail", detail)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class RuntimeValidationResult:
    """Complete runtime validation evidence."""

    descriptor: RuntimeDescriptor
    checks: tuple[RuntimeValidationCheck, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "checks", tuple(self.checks))

    @property
    def is_valid(self) -> bool:
        return bool(self.checks) and all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "environment": self.descriptor.environment.value,
            "config_path": str(self.descriptor.config_path),
            "state_root": str(self.descriptor.state_root),
            "log_root": str(self.descriptor.log_root),
            "service_account": self.descriptor.service_account,
            "service_group": self.descriptor.service_group,
            "is_valid": self.is_valid,
            "checks": [check.to_dict() for check in self.checks],
        }
