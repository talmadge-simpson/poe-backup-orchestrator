"""Atomic filesystem persistence for the current orchestrator runtime state."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.exceptions import (
    RuntimeStateCorruptionError,
    RuntimeStatePersistenceError,
    RuntimeStateSchemaError,
)
from poe_backup_orchestrator.models import (
    RUNTIME_STATE_SCHEMA_VERSION,
    ExecutionState,
    RuntimeEnvironment,
    RuntimeExecutionStatus,
    RuntimeState,
)

RUNTIME_STATE_FILENAME = "runtime-state.json"
_REQUIRED_FIELDS = frozenset(
    {
        "schema_version",
        "run_id",
        "status",
        "execution_state",
        "started_at_utc",
        "updated_at_utc",
        "pid",
        "hostname",
        "environment",
    }
)


class RuntimeStateStore:
    """Load, atomically save, and clear the authoritative runtime-state record."""

    def __init__(self, state_root: Path) -> None:
        self.state_root = Path(state_root)
        self.path = self.state_root / RUNTIME_STATE_FILENAME

    def load(self) -> RuntimeState | None:
        """Load persisted runtime state, returning None when no record exists."""
        try:
            raw = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise RuntimeStatePersistenceError(
                f"Unable to read runtime state from {self.path}: {exc}"
            ) from exc

        try:
            document = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeStateCorruptionError(
                f"Runtime-state file contains malformed JSON: {self.path}"
            ) from exc

        return _decode_runtime_state(document, source=self.path)

    def save(self, state: RuntimeState) -> None:
        """Atomically replace the authoritative runtime-state record."""
        if not isinstance(state, RuntimeState):
            raise TypeError("state must be a RuntimeState instance")

        try:
            self.state_root.mkdir(parents=True, exist_ok=True)
            content = json.dumps(state.to_dict(), indent=2, sort_keys=True, ensure_ascii=False)
            _atomic_write_text(self.path, content + "\n")
        except OSError as exc:
            raise RuntimeStatePersistenceError(
                f"Unable to persist runtime state to {self.path}: {exc}"
            ) from exc

    def clear(self) -> None:
        """Remove the current runtime-state record; absence is not an error."""
        try:
            self.path.unlink(missing_ok=True)
            if self.state_root.exists():
                _fsync_directory(self.state_root)
        except OSError as exc:
            raise RuntimeStatePersistenceError(
                f"Unable to clear runtime state at {self.path}: {exc}"
            ) from exc


def _decode_runtime_state(document: Any, *, source: Path) -> RuntimeState:
    if not isinstance(document, dict):
        raise RuntimeStateCorruptionError(f"Runtime-state document must be a JSON object: {source}")

    keys = set(document)
    missing = sorted(_REQUIRED_FIELDS - keys)
    unexpected = sorted(keys - _REQUIRED_FIELDS)
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected fields: {', '.join(unexpected)}")
        raise RuntimeStateCorruptionError(
            f"Invalid runtime-state structure in {source}: {'; '.join(details)}"
        )

    schema_version = document["schema_version"]
    if type(schema_version) is not int:
        raise RuntimeStateCorruptionError(
            f"Runtime-state schema_version must be an integer: {source}"
        )
    if schema_version != RUNTIME_STATE_SCHEMA_VERSION:
        raise RuntimeStateSchemaError(
            f"Unsupported runtime-state schema version {schema_version}; "
            f"expected {RUNTIME_STATE_SCHEMA_VERSION}"
        )

    try:
        return RuntimeState(
            schema_version=schema_version,
            run_id=_require_string(document, "run_id"),
            status=RuntimeExecutionStatus(_require_string(document, "status")),
            execution_state=ExecutionState(_require_string(document, "execution_state")),
            started_at_utc=_parse_timestamp(
                _require_string(document, "started_at_utc"),
                field_name="started_at_utc",
            ),
            updated_at_utc=_parse_timestamp(
                _require_string(document, "updated_at_utc"),
                field_name="updated_at_utc",
            ),
            pid=_require_integer(document, "pid"),
            hostname=_require_string(document, "hostname"),
            environment=RuntimeEnvironment(_require_string(document, "environment")),
        )
    except RuntimeStateCorruptionError:
        raise
    except (TypeError, ValueError) as exc:
        raise RuntimeStateCorruptionError(
            f"Invalid runtime-state content in {source}: {exc}"
        ) from exc


def _require_string(document: dict[str, Any], field_name: str) -> str:
    value = document[field_name]
    if not isinstance(value, str):
        raise RuntimeStateCorruptionError(f"Runtime-state field {field_name!r} must be a string")
    return value


def _require_integer(document: dict[str, Any], field_name: str) -> int:
    value = document[field_name]
    if type(value) is not int:
        raise RuntimeStateCorruptionError(f"Runtime-state field {field_name!r} must be an integer")
    return value


def _parse_timestamp(value: str, *, field_name: str) -> datetime:
    if not value.endswith("Z"):
        raise RuntimeStateCorruptionError(
            f"Runtime-state field {field_name!r} must use UTC Z notation"
        )
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise RuntimeStateCorruptionError(
            f"Runtime-state field {field_name!r} is not a valid timestamp"
        ) from exc


def _atomic_write_text(destination: Path, content: str) -> None:
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary_path = Path(raw_path)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
        _fsync_directory(destination.parent)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
