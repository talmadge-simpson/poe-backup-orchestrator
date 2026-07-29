"""Canonical atomic persistence for content-integrity evidence."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from poe_backup_orchestrator.models.storage_content_integrity import (
    ContentIntegrityVerificationResult,
)


class ContentIntegrityPersistenceError(RuntimeError):
    """Raised when integrity evidence cannot be persisted atomically."""


@dataclass(frozen=True, slots=True)
class PersistedContentIntegrityEvidence:
    """Published integrity-evidence artifact and its independent digest."""

    evidence_path: Path
    digest_path: Path
    byte_count: int
    sha256: str


class ContentIntegrityEvidencePersistence:
    """Persist canonical JSON and a SHA-256 sidecar using atomic replacement."""

    EVIDENCE_FILENAME = "content-integrity-evidence.json"
    DIGEST_FILENAME = "content-integrity-evidence.sha256"

    def persist(
        self,
        *,
        destination_directory: Path,
        result: ContentIntegrityVerificationResult,
    ) -> PersistedContentIntegrityEvidence:
        destination = Path(destination_directory)
        destination.mkdir(parents=True, exist_ok=True)
        if not destination.is_dir():
            raise ContentIntegrityPersistenceError(
                "destination_directory must identify a directory"
            )

        payload = _canonical_json_bytes(result)
        digest = hashlib.sha256(payload).hexdigest()
        evidence_path = destination / self.EVIDENCE_FILENAME
        digest_path = destination / self.DIGEST_FILENAME

        try:
            _atomic_write(evidence_path, payload)
            _atomic_write(digest_path, f"{digest}\n".encode("ascii"))
        except OSError as error:
            raise ContentIntegrityPersistenceError(
                f"failed to persist integrity evidence: {error}"
            ) from error

        return PersistedContentIntegrityEvidence(
            evidence_path=evidence_path,
            digest_path=digest_path,
            byte_count=len(payload),
            sha256=digest,
        )


def _canonical_json_bytes(result: ContentIntegrityVerificationResult) -> bytes:
    document = _json_value(asdict(result))
    return (
        json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    return value


def _atomic_write(path: Path, payload: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
