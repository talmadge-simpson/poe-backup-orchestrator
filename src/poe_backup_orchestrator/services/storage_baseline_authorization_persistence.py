"""Canonical immutable persistence for preservation-baseline authorization evidence."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from dataclasses import dataclass, fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final

from poe_backup_orchestrator.models.storage_baseline_authorization import (
    PreservationBaselineAuthorizationDecision,
)
from poe_backup_orchestrator.models.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationArtifact,
    PreservationBaselineAuthorizationPersistenceResult,
)
from poe_backup_orchestrator.utilities.locking import (
    LockContentionError,
    LockingError,
    exclusive_file_lock,
)

AUTHORIZATION_PERSISTENCE_LOCK_FILENAME: Final[str] = "preservation-baseline-authorization.lock"
_ARTIFACT_PREFIX: Final[str] = "preservation-baseline-authorization-"


class PreservationBaselineAuthorizationPersistenceError(RuntimeError):
    """Base error for authorization serialization or durable persistence failures."""


class PreservationBaselineAuthorizationConflictError(
    PreservationBaselineAuthorizationPersistenceError
):
    """Raised when immutable authorization persistence state is contradictory."""


class PreservationBaselineAuthorizationLockError(PreservationBaselineAuthorizationPersistenceError):
    """Raised when exclusive authorization persistence ownership is unavailable."""


class PreservationBaselineAuthorizationSerializer:
    """Serialize one exact authorization decision as canonical UTF-8 JSON."""

    def serialize(self, decision: PreservationBaselineAuthorizationDecision) -> bytes:
        if not isinstance(decision, PreservationBaselineAuthorizationDecision):
            raise PreservationBaselineAuthorizationPersistenceError(
                "decision must be PreservationBaselineAuthorizationDecision"
            )
        try:
            payload = _json_value(decision)
            text = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        except PreservationBaselineAuthorizationPersistenceError:
            raise
        except (TypeError, ValueError) as exc:
            raise PreservationBaselineAuthorizationPersistenceError(
                f"authorization decision serialization failed: {exc}"
            ) from exc
        return f"{text}\n".encode()

    def calculate_sha256(self, decision: PreservationBaselineAuthorizationDecision) -> str:
        """Return SHA-256 for the exact canonical decision bytes."""

        return hashlib.sha256(self.serialize(decision)).hexdigest()


@dataclass(slots=True)
class PreservationBaselineAuthorizationStore:
    """Persist immutable authorization evidence with exact replay verification."""

    serializer: PreservationBaselineAuthorizationSerializer = (
        PreservationBaselineAuthorizationSerializer()
    )

    def persist(
        self,
        *,
        decision: PreservationBaselineAuthorizationDecision,
        destination_directory: Path,
    ) -> PreservationBaselineAuthorizationPersistenceResult:
        if not isinstance(decision, PreservationBaselineAuthorizationDecision):
            raise PreservationBaselineAuthorizationPersistenceError(
                "decision must be PreservationBaselineAuthorizationDecision"
            )

        destination = Path(destination_directory)
        if not destination.is_absolute():
            raise PreservationBaselineAuthorizationPersistenceError(
                "destination_directory must be absolute"
            )

        content = self.serializer.serialize(decision)
        digest = hashlib.sha256(content).hexdigest()
        authorization_id = decision.identity.authorization_id
        filename = f"{_ARTIFACT_PREFIX}{authorization_id}.json"
        evidence_path = destination / filename
        sha256_path = evidence_path.with_name(f"{evidence_path.name}.sha256")
        lock_path = destination / ".locks" / AUTHORIZATION_PERSISTENCE_LOCK_FILENAME
        sidecar_content = f"{digest}  {filename}\n".encode("ascii")

        if evidence_path.parent != destination or sha256_path.parent != destination:
            raise PreservationBaselineAuthorizationPersistenceError(
                "authorization identity produced an unsafe persistence path"
            )

        try:
            destination.mkdir(parents=True, exist_ok=True, mode=0o770)
            if not destination.is_dir():
                raise PreservationBaselineAuthorizationPersistenceError(
                    "destination_directory must identify a directory"
                )
            lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o770)
        except PreservationBaselineAuthorizationPersistenceError:
            raise
        except OSError as exc:
            raise PreservationBaselineAuthorizationPersistenceError(
                f"unable to prepare authorization persistence destination {destination}: {exc}"
            ) from exc

        try:
            with exclusive_file_lock(lock_path):
                return self._persist_under_lock(
                    decision=decision,
                    evidence_path=evidence_path,
                    sha256_path=sha256_path,
                    content=content,
                    digest=digest,
                    sidecar_content=sidecar_content,
                )
        except LockContentionError as exc:
            raise PreservationBaselineAuthorizationLockError(
                f"authorization persistence is already active: {destination}"
            ) from exc
        except LockingError as exc:
            raise PreservationBaselineAuthorizationLockError(
                f"authorization persistence lock failed for {destination}: {exc}"
            ) from exc

    def _persist_under_lock(
        self,
        *,
        decision: PreservationBaselineAuthorizationDecision,
        evidence_path: Path,
        sha256_path: Path,
        content: bytes,
        digest: str,
        sidecar_content: bytes,
    ) -> PreservationBaselineAuthorizationPersistenceResult:
        evidence_exists = os.path.lexists(evidence_path)
        sidecar_exists = os.path.lexists(sha256_path)

        if evidence_exists or sidecar_exists:
            if not (evidence_exists and sidecar_exists):
                raise self._conflict(
                    decision=decision,
                    target=evidence_path,
                    classification="incomplete_persistence_pair",
                    proposed_digest=digest,
                )
            self._require_exact_replay(
                decision=decision,
                evidence_path=evidence_path,
                sha256_path=sha256_path,
                content=content,
                digest=digest,
                sidecar_content=sidecar_content,
            )
            return self._result(
                decision=decision,
                evidence_path=evidence_path,
                sha256_path=sha256_path,
                digest=digest,
                byte_count=len(content),
                idempotent_replay=True,
            )

        evidence_created = False
        sidecar_created = False
        try:
            _persist_exclusively(evidence_path, content)
            evidence_created = True
            _fsync_directory(evidence_path.parent)
            _persist_exclusively(sha256_path, sidecar_content)
            sidecar_created = True
            _fsync_directory(evidence_path.parent)
        except FileExistsError as exc:
            replay_error: PreservationBaselineAuthorizationPersistenceError | None = None
            if os.path.lexists(evidence_path) and os.path.lexists(sha256_path):
                try:
                    self._require_exact_replay(
                        decision=decision,
                        evidence_path=evidence_path,
                        sha256_path=sha256_path,
                        content=content,
                        digest=digest,
                        sidecar_content=sidecar_content,
                    )
                except PreservationBaselineAuthorizationPersistenceError as error:
                    replay_error = error
                else:
                    return self._result(
                        decision=decision,
                        evidence_path=evidence_path,
                        sha256_path=sha256_path,
                        digest=digest,
                        byte_count=len(content),
                        idempotent_replay=True,
                    )
            cleanup_error = _cleanup_created(
                evidence_path=evidence_path,
                sha256_path=sha256_path,
                evidence_created=evidence_created,
                sidecar_created=sidecar_created,
            )
            if cleanup_error is not None:
                raise PreservationBaselineAuthorizationPersistenceError(
                    "authorization persistence race cleanup failed"
                ) from cleanup_error
            if replay_error is not None:
                raise replay_error from exc
            raise self._conflict(
                decision=decision,
                target=Path(exc.filename) if exc.filename else evidence_path,
                classification="concurrent_persistence_race",
                proposed_digest=digest,
            ) from exc
        except OSError as exc:
            cleanup_error = _cleanup_created(
                evidence_path=evidence_path,
                sha256_path=sha256_path,
                evidence_created=evidence_created,
                sidecar_created=sidecar_created,
            )
            if cleanup_error is not None:
                raise PreservationBaselineAuthorizationPersistenceError(
                    "authorization persistence failed and cleanup also failed"
                ) from cleanup_error
            raise PreservationBaselineAuthorizationPersistenceError(
                f"unable to persist authorization evidence at {evidence_path}: {exc}"
            ) from exc

        return self._result(
            decision=decision,
            evidence_path=evidence_path,
            sha256_path=sha256_path,
            digest=digest,
            byte_count=len(content),
            idempotent_replay=False,
        )

    def _require_exact_replay(
        self,
        *,
        decision: PreservationBaselineAuthorizationDecision,
        evidence_path: Path,
        sha256_path: Path,
        content: bytes,
        digest: str,
        sidecar_content: bytes,
    ) -> None:
        for target in (evidence_path, sha256_path):
            try:
                mode = target.lstat().st_mode
            except OSError as exc:
                raise PreservationBaselineAuthorizationPersistenceError(
                    f"unable to inspect existing authorization evidence {target}: {exc}"
                ) from exc
            if not stat.S_ISREG(mode):
                raise self._conflict(
                    decision=decision,
                    target=target,
                    classification="non_regular_persistence_target",
                    proposed_digest=digest,
                )

        try:
            existing_content = evidence_path.read_bytes()
            existing_sidecar = sha256_path.read_bytes()
        except OSError as exc:
            raise PreservationBaselineAuthorizationPersistenceError(
                f"unable to read existing authorization evidence pair: {exc}"
            ) from exc

        existing_digest = hashlib.sha256(existing_content).hexdigest()
        if existing_content != content:
            raise self._conflict(
                decision=decision,
                target=evidence_path,
                classification="artifact_content_conflict",
                proposed_digest=digest,
                existing_digest=existing_digest,
            )
        if existing_digest != digest:
            raise self._conflict(
                decision=decision,
                target=evidence_path,
                classification="artifact_digest_conflict",
                proposed_digest=digest,
                existing_digest=existing_digest,
            )
        if existing_sidecar != sidecar_content:
            raise self._conflict(
                decision=decision,
                target=sha256_path,
                classification="sidecar_conflict",
                proposed_digest=digest,
                existing_digest=existing_digest,
            )

    @staticmethod
    def _result(
        *,
        decision: PreservationBaselineAuthorizationDecision,
        evidence_path: Path,
        sha256_path: Path,
        digest: str,
        byte_count: int,
        idempotent_replay: bool,
    ) -> PreservationBaselineAuthorizationPersistenceResult:
        return PreservationBaselineAuthorizationPersistenceResult(
            authorization_id=decision.identity.authorization_id,
            baseline_id=decision.identity.baseline_id,
            artifact=PreservationBaselineAuthorizationArtifact(
                evidence_path=evidence_path,
                sha256_path=sha256_path,
                sha256=digest,
                byte_count=byte_count,
            ),
            idempotent_replay=idempotent_replay,
        )

    @staticmethod
    def _conflict(
        *,
        decision: PreservationBaselineAuthorizationDecision,
        target: Path,
        classification: str,
        proposed_digest: str,
        existing_digest: str | None = None,
    ) -> PreservationBaselineAuthorizationConflictError:
        detail = (
            f"authorization_id={decision.identity.authorization_id}; "
            f"classification={classification}; target={target}; "
            f"proposed_digest={proposed_digest}"
        )
        if existing_digest is not None:
            detail += f"; existing_digest={existing_digest}"
        return PreservationBaselineAuthorizationConflictError(detail)


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise PreservationBaselineAuthorizationPersistenceError(
                "authorization decision contains a naive datetime"
            )
        if value.utcoffset() != UTC.utcoffset(value):
            raise PreservationBaselineAuthorizationPersistenceError(
                "authorization decision contains a non-UTC datetime"
            )
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise PreservationBaselineAuthorizationPersistenceError(
        f"authorization decision contains unsupported value of type {type(value).__name__}"
    )


def _persist_exclusively(destination: Path, content: bytes) -> None:
    descriptor = -1
    temporary_path: Path | None = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        temporary_path = Path(raw_path)
        os.fchmod(descriptor, 0o640)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_path, destination)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _cleanup_created(
    *,
    evidence_path: Path,
    sha256_path: Path,
    evidence_created: bool,
    sidecar_created: bool,
) -> OSError | None:
    try:
        if sidecar_created:
            sha256_path.unlink(missing_ok=True)
        if evidence_created:
            evidence_path.unlink(missing_ok=True)
        if evidence_created or sidecar_created:
            _fsync_directory(evidence_path.parent)
    except OSError as exc:
        return exc
    return None


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
