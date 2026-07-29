"""Deterministic serialization and exclusive persistence of storage inventory evidence."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, Final

from poe_backup_orchestrator.services.storage_inventory_assembly import (
    AssembledInventoryItem,
    InventoryAssemblyResult,
    UnsupportedInventoryItem,
)
from poe_backup_orchestrator.utilities.locking import (
    LockContentionError,
    LockingError,
    exclusive_file_lock,
)

STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION: Final[str] = "1.0"
INVENTORY_EVIDENCE_LOCK_FILENAME: Final[str] = "inventory-evidence.lock"
_SHA256_HEX_LENGTH: Final[int] = 64


class InventoryEvidencePersistenceError(RuntimeError):
    """Base error for inventory-evidence serialization or persistence failures."""


class InventoryEvidenceConflictError(InventoryEvidencePersistenceError):
    """Raised when an existing evidence path does not match requested content."""


class InventoryEvidenceLockError(InventoryEvidencePersistenceError):
    """Raised when exclusive publication ownership cannot be acquired."""


@dataclass(frozen=True, slots=True)
class InventoryEvidencePublication:
    """Evidence proving one inventory publication and its integrity sidecar."""

    evidence_path: Path
    sha256_path: Path
    sha256: str
    item_count: int
    byte_count: int
    idempotent_replay: bool

    def __post_init__(self) -> None:
        evidence_path = Path(self.evidence_path)
        sha256_path = Path(self.sha256_path)
        sha256 = self.sha256.strip().lower()

        if not evidence_path.is_absolute():
            raise ValueError("evidence_path must be absolute")
        if not sha256_path.is_absolute():
            raise ValueError("sha256_path must be absolute")
        if sha256_path != evidence_path.with_name(f"{evidence_path.name}.sha256"):
            raise ValueError("sha256_path must be the evidence path with .sha256 appended")
        if len(sha256) != _SHA256_HEX_LENGTH or any(
            character not in "0123456789abcdef" for character in sha256
        ):
            raise ValueError("sha256 must contain exactly 64 lowercase hexadecimal characters")
        if self.item_count < 0:
            raise ValueError("item_count must not be negative")
        if self.byte_count <= 0:
            raise ValueError("byte_count must be greater than zero")

        object.__setattr__(self, "evidence_path", evidence_path)
        object.__setattr__(self, "sha256_path", sha256_path)
        object.__setattr__(self, "sha256", sha256)


class InventoryEvidenceSerializer:
    """Serialize assembled inventory evidence as canonical newline-delimited JSON."""

    def serialize(self, result: InventoryAssemblyResult) -> bytes:
        """Return deterministic UTF-8 NDJSON terminated by one newline."""

        records: list[dict[str, Any]] = [self._header(result)]
        records.extend(self._item_payload(item) for item in result.ordered_items)
        content = "\n".join(_canonical_json(record) for record in records) + "\n"
        return content.encode("utf-8")

    def calculate_sha256(self, result: InventoryAssemblyResult) -> str:
        """Return the digest of the exact serialized evidence bytes."""

        return hashlib.sha256(self.serialize(result)).hexdigest()

    @staticmethod
    def _header(result: InventoryAssemblyResult) -> dict[str, Any]:
        return {
            "record_kind": "inventory_header",
            "schema_version": STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION,
            "discovery_request_id": result.discovery_request_id,
            "source_root_id": result.source_root_id,
            "item_count": result.totals.item_count,
            "totals": _to_primitive(result.totals),
            "exception_summaries": _to_primitive(result.exception_summaries),
        }

    @staticmethod
    def _item_payload(
        item: AssembledInventoryItem | UnsupportedInventoryItem,
    ) -> dict[str, Any]:
        if isinstance(item, AssembledInventoryItem):
            return {
                "record_kind": "inventory_item",
                "support_status": "supported",
                "item_id": item.item_id,
                "relative_path": item.record.identity.relative_path.as_posix(),
                "item_type": item.record.identity.item_type.value,
                "record": _to_primitive(item.record),
            }

        return {
            "record_kind": "inventory_item",
            "support_status": "unsupported",
            "item_id": item.item_id,
            "relative_path": item.relative_path.as_posix(),
            "item_type": item.item_type.value,
            "detail": item.detail,
        }


@dataclass(slots=True)
class InventoryEvidenceStore:
    """Publish immutable inventory evidence using exclusive, synchronized placement."""

    serializer: InventoryEvidenceSerializer = InventoryEvidenceSerializer()

    def publish(
        self,
        *,
        result: InventoryAssemblyResult,
        evidence_path: Path,
    ) -> InventoryEvidencePublication:
        """Persist evidence and digest without overwriting contradictory content."""

        destination = Path(evidence_path)
        if not destination.is_absolute():
            raise InventoryEvidencePersistenceError("evidence_path must be absolute")
        if destination.name in {"", ".", ".."}:
            raise InventoryEvidencePersistenceError("evidence_path must identify a file")

        destination_parent = destination.parent
        digest_path = destination.with_name(f"{destination.name}.sha256")
        lock_path = destination_parent / ".locks" / INVENTORY_EVIDENCE_LOCK_FILENAME

        try:
            destination_parent.mkdir(parents=True, exist_ok=True, mode=0o770)
            lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o770)
        except OSError as exc:
            raise InventoryEvidencePersistenceError(
                f"unable to prepare inventory evidence destination {destination_parent}: {exc}"
            ) from exc

        content = self.serializer.serialize(result)
        digest = hashlib.sha256(content).hexdigest()
        digest_content = f"{digest}  {destination.name}\n".encode()

        try:
            with exclusive_file_lock(lock_path):
                return self._publish_under_lock(
                    result=result,
                    destination=destination,
                    digest_path=digest_path,
                    content=content,
                    digest=digest,
                    digest_content=digest_content,
                )
        except LockContentionError as exc:
            raise InventoryEvidenceLockError(
                f"inventory evidence publication is already active: {destination_parent}"
            ) from exc
        except LockingError as exc:
            raise InventoryEvidenceLockError(
                f"inventory evidence lock failed for {destination_parent}: {exc}"
            ) from exc

    def _publish_under_lock(
        self,
        *,
        result: InventoryAssemblyResult,
        destination: Path,
        digest_path: Path,
        content: bytes,
        digest: str,
        digest_content: bytes,
    ) -> InventoryEvidencePublication:
        existing_evidence = destination.exists()
        existing_digest = digest_path.exists()

        if existing_evidence or existing_digest:
            if not (existing_evidence and existing_digest):
                raise InventoryEvidenceConflictError(
                    "inventory evidence publication is incomplete; evidence and digest "
                    "must either both exist or both be absent"
                )
            self._require_idempotent_match(
                destination=destination,
                digest_path=digest_path,
                content=content,
                digest=digest,
            )
            return InventoryEvidencePublication(
                evidence_path=destination,
                sha256_path=digest_path,
                sha256=digest,
                item_count=result.totals.item_count,
                byte_count=len(content),
                idempotent_replay=True,
            )

        evidence_created = False
        try:
            _publish_exclusively(destination=destination, content=content)
            evidence_created = True
            _publish_exclusively(destination=digest_path, content=digest_content)
            _fsync_directory(destination.parent)
        except FileExistsError as exc:
            if evidence_created:
                _remove_if_exists(destination)
                _fsync_directory(destination.parent)
            raise InventoryEvidenceConflictError(
                f"inventory evidence appeared during publication: {exc.filename}"
            ) from exc
        except OSError as exc:
            if evidence_created:
                _remove_if_exists(destination)
                _fsync_directory(destination.parent)
            raise InventoryEvidencePersistenceError(
                f"unable to publish inventory evidence at {destination}: {exc}"
            ) from exc

        return InventoryEvidencePublication(
            evidence_path=destination,
            sha256_path=digest_path,
            sha256=digest,
            item_count=result.totals.item_count,
            byte_count=len(content),
            idempotent_replay=False,
        )

    @staticmethod
    def _require_idempotent_match(
        *,
        destination: Path,
        digest_path: Path,
        content: bytes,
        digest: str,
    ) -> None:
        try:
            existing_content = destination.read_bytes()
            digest_line = digest_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise InventoryEvidencePersistenceError(
                f"unable to inspect existing inventory evidence: {exc}"
            ) from exc

        expected_digest_line = f"{digest}  {destination.name}"
        if existing_content != content or digest_line != expected_digest_line:
            raise InventoryEvidenceConflictError(
                "existing inventory evidence differs from requested canonical content"
            )


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _to_primitive(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, tuple):
        return [_to_primitive(item) for item in value]
    if isinstance(value, list):
        return [_to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    if is_dataclass(value):
        return {
            field_name: _to_primitive(field_value)
            for field_name, field_value in asdict(value).items()
        }
    return value


def _publish_exclusively(*, destination: Path, content: bytes) -> None:
    descriptor, raw_path = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary_path = Path(raw_path)
    try:
        os.fchmod(descriptor, 0o640)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_path, destination)
        _fsync_directory(destination.parent)
    finally:
        temporary_path.unlink(missing_ok=True)


def _remove_if_exists(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def _fsync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
