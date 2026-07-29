"""Tests for durable restore execution-record publication."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import cast

import pytest

from poe_backup_orchestrator.models import RestoreExecutionRecord
from poe_backup_orchestrator.services.restore.execution_record_persistence import (
    RestoreExecutionRecordConflictError,
    RestoreExecutionRecordPublicationError,
    RestoreExecutionRecordPublisher,
    serialize_restore_execution_record,
)


class ExampleStatus(Enum):
    COMPLETE = "complete"


@dataclass(frozen=True)
class NestedEvidence:
    observed_at_utc: datetime
    path: Path
    status: ExampleStatus
    checks: tuple[str, ...]


@dataclass(frozen=True)
class ExampleRecord:
    schema_version: str
    plan_id: str
    started_at_utc: datetime
    completed_at_utc: datetime
    lock_path: Path
    evidence: NestedEvidence
    restore_completed: bool


def record(*, plan_id: str = "plan-5e3") -> RestoreExecutionRecord:
    value = ExampleRecord(
        schema_version="1.0",
        plan_id=plan_id,
        started_at_utc=datetime(2026, 7, 28, 16, 0, tzinfo=UTC),
        completed_at_utc=datetime(2026, 7, 28, 16, 5, tzinfo=UTC),
        lock_path=Path("/var/lib/poe/restore.lock"),
        evidence=NestedEvidence(
            observed_at_utc=datetime(
                2026,
                7,
                28,
                12,
                1,
                tzinfo=UTC,
            ),
            path=Path("/srv/poe-backup/Registry/POERegistry"),
            status=ExampleStatus.COMPLETE,
            checks=("sha256", "sqlite"),
        ),
        restore_completed=True,
    )
    return cast(RestoreExecutionRecord, value)


def test_serialization_is_deterministic_and_json_safe() -> None:
    first = serialize_restore_execution_record(record())
    second = serialize_restore_execution_record(record())

    assert first == second
    assert first.endswith("\n")

    payload = json.loads(first)
    assert payload["plan_id"] == "plan-5e3"
    assert payload["started_at_utc"] == "2026-07-28T16:00:00Z"
    assert payload["evidence"]["observed_at_utc"] == "2026-07-28T12:01:00Z"
    assert payload["evidence"]["path"] == ("/srv/poe-backup/Registry/POERegistry")
    assert payload["evidence"]["status"] == "complete"
    assert payload["evidence"]["checks"] == ["sha256", "sqlite"]


def test_publish_creates_immutable_json_and_evidence(tmp_path: Path) -> None:
    executions_root = tmp_path / "Restore" / "Executions"
    publisher = RestoreExecutionRecordPublisher(executions_root)

    publication = publisher.publish(record())

    expected = executions_root / "restore-execution-plan-5e3.json"
    content = expected.read_bytes()

    assert publication.plan_id == "plan-5e3"
    assert publication.json_path == expected
    assert publication.sha256 == hashlib.sha256(content).hexdigest()
    sidecar = Path(f"{expected}.sha256")
    assert sidecar.is_file()
    assert sidecar.read_text(encoding="utf-8") == (f"{publication.sha256}  {expected.name}\n")
    assert publication.bytes_written == len(content)
    assert publication.idempotent is False
    assert expected.stat().st_mode & 0o777 == 0o600
    assert not list(executions_root.glob("*.tmp"))


def test_republishing_identical_record_is_idempotent(tmp_path: Path) -> None:
    publisher = RestoreExecutionRecordPublisher(tmp_path)

    first = publisher.publish(record())
    second = publisher.publish(record())

    assert first.json_path == second.json_path
    assert first.sha256 == second.sha256
    assert second.idempotent is True
    assert len(list(tmp_path.glob("restore-execution-*.json"))) == 1
    assert len(list(tmp_path.glob("restore-execution-*.json.sha256"))) == 1


def test_existing_different_record_is_conflict(tmp_path: Path) -> None:
    destination = tmp_path / "restore-execution-plan-5e3.json"
    destination.write_text('{"different":true}\n', encoding="utf-8")
    publisher = RestoreExecutionRecordPublisher(tmp_path)

    with pytest.raises(
        RestoreExecutionRecordConflictError,
        match="different evidence",
    ):
        publisher.publish(record())

    assert destination.read_text(encoding="utf-8") == '{"different":true}\n'
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize(
    "plan_id",
    ("../escape", "nested/path", "", ".", "..", r"nested\path"),
)
def test_unsafe_plan_id_is_rejected(
    tmp_path: Path,
    plan_id: str,
) -> None:
    publisher = RestoreExecutionRecordPublisher(tmp_path)

    with pytest.raises(
        RestoreExecutionRecordPublicationError,
        match="plan_id",
    ):
        publisher.publish(record(plan_id=plan_id))

    assert not list(tmp_path.glob("restore-execution-*.json"))
    assert not list(tmp_path.glob("*.tmp"))


def test_naive_datetime_is_rejected() -> None:
    value = ExampleRecord(
        schema_version="1.0",
        plan_id="plan-naive",
        started_at_utc=datetime(2026, 7, 28, 16, 0),
        completed_at_utc=datetime(2026, 7, 28, 16, 5, tzinfo=UTC),
        lock_path=Path("/tmp/restore.lock"),
        evidence=NestedEvidence(
            observed_at_utc=datetime(2026, 7, 28, 16, 1, tzinfo=UTC),
            path=Path("/tmp/evidence"),
            status=ExampleStatus.COMPLETE,
            checks=(),
        ),
        restore_completed=True,
    )

    with pytest.raises(
        RestoreExecutionRecordPublicationError,
        match="naive datetime",
    ):
        serialize_restore_execution_record(cast(RestoreExecutionRecord, value))


def test_link_race_with_identical_record_is_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = RestoreExecutionRecordPublisher(tmp_path)
    expected = serialize_restore_execution_record(record()).encode("utf-8")
    destination = tmp_path / "restore-execution-plan-5e3.json"
    real_link = os.link

    def racing_link(source: Path, target: Path) -> None:
        destination.write_bytes(expected)
        raise FileExistsError(target)

    monkeypatch.setattr(os, "link", racing_link)
    publication = publisher.publish(record())
    monkeypatch.setattr(os, "link", real_link)

    assert publication.idempotent is True
    assert destination.read_bytes() == expected
    assert not list(tmp_path.glob("*.tmp"))


def test_link_failure_removes_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    publisher = RestoreExecutionRecordPublisher(tmp_path)

    def fail_link(source: Path, target: Path) -> None:
        del source, target
        raise OSError("simulated link failure")

    monkeypatch.setattr(os, "link", fail_link)

    with pytest.raises(
        RestoreExecutionRecordPublicationError,
        match="failed to publish",
    ):
        publisher.publish(record())

    assert not list(tmp_path.glob("*.tmp"))
    assert not list(tmp_path.glob("*.json"))
