"""Production runtime identity, state, path, and validation models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from poe_backup_orchestrator.models.execution import ExecutionState
from poe_backup_orchestrator.models.job import require_utc

RUNTIME_STATE_SCHEMA_VERSION: Final[int] = 1


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


class RuntimeExecutionStatus(StrEnum):
    """Coarse process-level condition for one orchestration execution."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True, slots=True)
class RuntimeState:
    """Immutable persisted-state contract for one orchestration execution."""

    schema_version: int
    run_id: str
    status: RuntimeExecutionStatus
    execution_state: ExecutionState
    started_at_utc: datetime
    updated_at_utc: datetime
    pid: int
    hostname: str
    environment: RuntimeEnvironment

    def __post_init__(self) -> None:
        if self.schema_version != RUNTIME_STATE_SCHEMA_VERSION:
            raise ValueError(f"runtime state schema_version must be {RUNTIME_STATE_SCHEMA_VERSION}")

        run_id = self.run_id.strip()
        hostname = self.hostname.strip()

        if not run_id:
            raise ValueError("runtime state run_id must not be empty")
        if not hostname:
            raise ValueError("runtime state hostname must not be empty")
        if self.pid <= 0:
            raise ValueError("runtime state pid must be greater than zero")

        require_utc(self.started_at_utc, field_name="started_at_utc")
        require_utc(self.updated_at_utc, field_name="updated_at_utc")

        if self.updated_at_utc < self.started_at_utc:
            raise ValueError("updated_at_utc must not precede started_at_utc")

        self._validate_status_state_consistency()

        object.__setattr__(self, "run_id", run_id)
        object.__setattr__(self, "hostname", hostname)

    def _validate_status_state_consistency(self) -> None:
        terminal_states = {ExecutionState.COMPLETED, ExecutionState.FAILED}

        if (
            self.status is RuntimeExecutionStatus.RUNNING
            and self.execution_state in terminal_states
        ):
            raise ValueError("running runtime state must use a nonterminal execution state")

        if (
            self.status is RuntimeExecutionStatus.COMPLETED
            and self.execution_state is not ExecutionState.COMPLETED
        ):
            raise ValueError("completed runtime status requires execution state COMPLETED")

        if (
            self.status is RuntimeExecutionStatus.FAILED
            and self.execution_state is not ExecutionState.FAILED
        ):
            raise ValueError("failed runtime status requires execution state FAILED")

        if (
            self.status is RuntimeExecutionStatus.INTERRUPTED
            and self.execution_state in terminal_states
        ):
            raise ValueError(
                "interrupted runtime state must preserve a nonterminal execution state"
            )

    def to_dict(self) -> dict[str, object]:
        """Return the stable JSON-compatible runtime-state representation."""

        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "status": self.status.value,
            "execution_state": self.execution_state.value,
            "started_at_utc": _utc_isoformat(self.started_at_utc),
            "updated_at_utc": _utc_isoformat(self.updated_at_utc),
            "pid": self.pid,
            "hostname": self.hostname,
            "environment": self.environment.value,
        }


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


def _utc_isoformat(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
