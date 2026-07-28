"""Deterministic and durable publication of restore execution evidence."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.models import RestoreExecutionRecord

_PLAN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


class RestoreExecutionRecordPublicationError(RuntimeError):
    """Base failure raised while publishing restore execution evidence."""


class RestoreExecutionRecordConflictError(RestoreExecutionRecordPublicationError):
    """Raised when an immutable execution-record path already differs."""


@dataclass(frozen=True, slots=True)
class RestoreExecutionRecordPublication:
    """Evidence describing one durable execution-record publication."""

    plan_id: str
    json_path: Path
    sha256: str
    bytes_written: int
    idempotent: bool


class RestoreExecutionRecordPublisher:
    """Publish completed restore execution records as immutable JSON."""

    def __init__(self, executions_root: Path) -> None:
        self.executions_root = Path(executions_root)

    def publish(
        self,
        record: RestoreExecutionRecord,
    ) -> RestoreExecutionRecordPublication:
        """Persist one completed execution record without overwriting evidence."""

        _validate_plan_id(record.plan_id)
        content = serialize_restore_execution_record(record)
        encoded = content.encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()

        self.executions_root.mkdir(parents=True, exist_ok=True, mode=0o770)
        destination = self.executions_root / f"restore-execution-{record.plan_id}.json"

        if destination.exists():
            return _resolve_existing(
                destination=destination,
                plan_id=record.plan_id,
                expected=encoded,
                digest=digest,
            )

        temporary_path = _stage_bytes(
            directory=self.executions_root,
            prefix=f".restore-execution-{record.plan_id}-",
            content=encoded,
        )
        try:
            try:
                os.link(temporary_path, destination)
            except FileExistsError:
                return _resolve_existing(
                    destination=destination,
                    plan_id=record.plan_id,
                    expected=encoded,
                    digest=digest,
                )
            except OSError as exc:
                raise RestoreExecutionRecordPublicationError(
                    f"failed to publish restore execution record: {destination}"
                ) from exc

            _fsync_directory(self.executions_root)
            return RestoreExecutionRecordPublication(
                plan_id=record.plan_id,
                json_path=destination,
                sha256=digest,
                bytes_written=len(encoded),
                idempotent=False,
            )
        finally:
            temporary_path.unlink(missing_ok=True)


def serialize_restore_execution_record(
    record: RestoreExecutionRecord,
) -> str:
    """Return deterministic UTF-8 JSON text for one execution record."""

    payload = _json_compatible(record)
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def _json_compatible(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _json_compatible(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise RestoreExecutionRecordPublicationError(
                "restore execution record contains a naive datetime"
            )
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return _json_compatible(value.value)
    if isinstance(value, Mapping):
        return {str(key): _json_compatible(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_compatible(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized = [_json_compatible(item) for item in value]
        return sorted(
            normalized,
            key=lambda item: json.dumps(item, sort_keys=True),
        )
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise RestoreExecutionRecordPublicationError(
        f"restore execution record contains unsupported value of type {type(value).__name__}"
    )


def _validate_plan_id(plan_id: str) -> None:
    if not _PLAN_ID_PATTERN.fullmatch(plan_id) or plan_id in {".", ".."}:
        raise RestoreExecutionRecordPublicationError(
            "plan_id is not safe for execution-record publication"
        )


def _stage_bytes(
    *,
    directory: Path,
    prefix: str,
    content: bytes,
) -> Path:
    descriptor = -1
    temporary_path: Path | None = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            dir=directory,
            prefix=prefix,
            suffix=".tmp",
        )
        temporary_path = Path(raw_path)
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        return temporary_path
    except OSError as exc:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise RestoreExecutionRecordPublicationError(
            "failed to stage restore execution record"
        ) from exc


def _resolve_existing(
    *,
    destination: Path,
    plan_id: str,
    expected: bytes,
    digest: str,
) -> RestoreExecutionRecordPublication:
    try:
        existing = destination.read_bytes()
    except OSError as exc:
        raise RestoreExecutionRecordPublicationError(
            f"failed to inspect existing restore execution record: {destination}"
        ) from exc

    if existing != expected:
        raise RestoreExecutionRecordConflictError(
            f"restore execution record path already contains different evidence: {destination}"
        )

    return RestoreExecutionRecordPublication(
        plan_id=plan_id,
        json_path=destination,
        sha256=digest,
        bytes_written=len(expected),
        idempotent=True,
    )


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
