"""Tests for atomic persistent runtime-state storage."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

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
from poe_backup_orchestrator.services.runtime_state_store import (
    RUNTIME_STATE_FILENAME,
    RuntimeStateStore,
)

STARTED = datetime(2026, 7, 27, 15, 0, tzinfo=UTC)
UPDATED = datetime(2026, 7, 27, 15, 0, 1, tzinfo=UTC)


def runtime_state(*, run_id: str = "job-runtime-store") -> RuntimeState:
    return RuntimeState(
        schema_version=RUNTIME_STATE_SCHEMA_VERSION,
        run_id=run_id,
        status=RuntimeExecutionStatus.RUNNING,
        execution_state=ExecutionState.REPOSITORY_VALIDATION,
        started_at_utc=STARTED,
        updated_at_utc=UPDATED,
        pid=4321,
        hostname="ai-lab",
        environment=RuntimeEnvironment.DEVELOPMENT,
    )


def write_document(store: RuntimeStateStore, document: object) -> None:
    store.state_root.mkdir(parents=True, exist_ok=True)
    store.path.write_text(json.dumps(document), encoding="utf-8")


def test_store_uses_authoritative_filename(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path / "state")
    assert store.path == tmp_path / "state" / RUNTIME_STATE_FILENAME


def test_load_returns_none_when_file_is_absent(tmp_path: Path) -> None:
    assert RuntimeStateStore(tmp_path / "state").load() is None


def test_save_load_round_trip_and_create_root(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path / "nested" / "state")
    expected = runtime_state()
    store.save(expected)
    assert store.load() == expected


def test_save_writes_deterministic_utf8_json(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    state = runtime_state(run_id="job-café")
    store.save(state)
    content = store.path.read_text(encoding="utf-8")
    assert content.endswith("\n")
    assert "\\u00e9" not in content
    assert json.loads(content) == state.to_dict()


def test_save_atomically_overwrites_previous_state(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    store.save(runtime_state(run_id="first"))
    replacement = runtime_state(run_id="second")
    store.save(replacement)
    assert store.load() == replacement
    assert not list(tmp_path.glob("*.tmp"))


def test_save_rejects_non_runtime_state(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="RuntimeState"):
        RuntimeStateStore(tmp_path).save(object())  # type: ignore[arg-type]


def test_clear_is_effective_and_idempotent(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    store.save(runtime_state())
    store.clear()
    store.clear()
    assert store.load() is None


def test_load_rejects_malformed_json(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    tmp_path.mkdir(exist_ok=True)
    store.path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(RuntimeStateCorruptionError, match="malformed JSON"):
        store.load()


@pytest.mark.parametrize("document", [[], "text", 42, None])
def test_load_rejects_non_object_json(tmp_path: Path, document: object) -> None:
    store = RuntimeStateStore(tmp_path)
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match="JSON object"):
        store.load()


def test_load_rejects_missing_and_unexpected_fields(tmp_path: Path) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    del document["hostname"]
    document["extra"] = True
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match="missing fields: hostname"):
        store.load()


@pytest.mark.parametrize("version", [0, 2, 99])
def test_load_rejects_unsupported_schema(tmp_path: Path, version: int) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    document["schema_version"] = version
    write_document(store, document)
    with pytest.raises(RuntimeStateSchemaError, match="Unsupported"):
        store.load()


@pytest.mark.parametrize("version", ["1", 1.0, True, None])
def test_load_rejects_noninteger_schema(tmp_path: Path, version: object) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    document["schema_version"] = version
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match="must be an integer"):
        store.load()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("run_id", 123),
        ("status", 123),
        ("execution_state", 123),
        ("started_at_utc", 123),
        ("updated_at_utc", 123),
        ("hostname", 123),
        ("environment", 123),
    ],
)
def test_load_rejects_nonstring_fields(tmp_path: Path, field: str, value: object) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    document[field] = value
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match="must be a string"):
        store.load()


@pytest.mark.parametrize("pid", ["4321", 1.0, True, None])
def test_load_rejects_noninteger_pid(tmp_path: Path, pid: object) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    document["pid"] = pid
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match="must be an integer"):
        store.load()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("status", "unknown"),
        ("execution_state", "unknown"),
        ("environment", "unknown"),
        ("run_id", " "),
        ("hostname", " "),
        ("pid", 0),
    ],
)
def test_load_wraps_invalid_domain_content(tmp_path: Path, field: str, value: object) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    document[field] = value
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match="Invalid runtime-state content"):
        store.load()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("started_at_utc", "2026-07-27T15:00:00+00:00"),
        ("updated_at_utc", "not-a-timeZ"),
    ],
)
def test_load_rejects_invalid_timestamp_encoding(tmp_path: Path, field: str, value: str) -> None:
    store = RuntimeStateStore(tmp_path)
    document = runtime_state().to_dict()
    document[field] = value
    write_document(store, document)
    with pytest.raises(RuntimeStateCorruptionError, match=field):
        store.load()


def test_failed_replacement_preserves_previous_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = RuntimeStateStore(tmp_path)
    original = runtime_state(run_id="original")
    store.save(original)
    real_replace = os.replace

    def fail_replace(source: object, destination: object) -> None:
        if Path(destination) == store.path:
            raise OSError("simulated replacement failure")
        real_replace(source, destination)

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(RuntimeStatePersistenceError, match="simulated replacement failure"):
        store.save(runtime_state(run_id="replacement"))
    assert store.load() == original
    assert not list(tmp_path.glob("*.tmp"))


def test_load_wraps_read_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = RuntimeStateStore(tmp_path)

    def fail_read(*args: object, **kwargs: object) -> str:
        raise PermissionError("simulated read failure")

    monkeypatch.setattr(Path, "read_text", fail_read)
    with pytest.raises(RuntimeStatePersistenceError, match="simulated read failure"):
        store.load()


def test_clear_wraps_filesystem_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = RuntimeStateStore(tmp_path)
    store.save(runtime_state())

    def fail_unlink(*args: object, **kwargs: object) -> None:
        raise PermissionError("simulated clear failure")

    monkeypatch.setattr(Path, "unlink", fail_unlink)
    with pytest.raises(RuntimeStatePersistenceError, match="simulated clear failure"):
        store.clear()


def test_service_exports_runtime_state_store() -> None:
    from poe_backup_orchestrator import services

    assert services.RUNTIME_STATE_FILENAME == RUNTIME_STATE_FILENAME
    assert services.RuntimeStateStore is RuntimeStateStore
