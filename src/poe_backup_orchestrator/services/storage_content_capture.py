"""Deterministic, bounded-memory source-content capture and SHA-256 certification."""

from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.storage_baseline_manifest import InventoryTotals
from poe_backup_orchestrator.models.storage_content_capture import (
    STORAGE_CONTENT_CAPTURE_SCHEMA_VERSION,
    ContentCaptureException,
    ContentCaptureExceptionCode,
    FileContentCertification,
    InventoryContentCaptureResult,
)
from poe_backup_orchestrator.models.storage_inventory import (
    FileInventoryRecord,
    InventoryCaptureStatus,
    InventoryItemType,
)
from poe_backup_orchestrator.models.storage_inventory_assembly import (
    AssembledInventoryItem,
    InventoryAssemblyResult,
)

Clock = Callable[[], datetime]


class InventoryContentCaptureError(RuntimeError):
    """Raised when a capture request itself is structurally invalid."""


@dataclass(frozen=True, slots=True)
class ContentCapturePolicy:
    """Bounded-memory policy for source-file content reads."""

    chunk_size_bytes: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be positive")


class InventoryContentCaptureService:
    """Hash pending file inventory records without mutating source content."""

    def __init__(
        self,
        *,
        policy: ContentCapturePolicy | None = None,
        clock: Clock | None = None,
    ) -> None:
        self._policy = policy or ContentCapturePolicy()
        self._clock = clock or _utc_now

    def capture(
        self,
        *,
        root_path: Path,
        inventory: InventoryAssemblyResult,
    ) -> InventoryContentCaptureResult:
        """Return immutable capture evidence in deterministic relative-path order."""

        root = Path(root_path)
        if not root.is_absolute():
            raise InventoryContentCaptureError("root_path must be absolute")

        started_at_utc = self._clock()
        updated_items: list[AssembledInventoryItem] = []
        certifications: list[FileContentCertification] = []
        exceptions: list[ContentCaptureException] = []

        for item in inventory.items:
            record = item.record
            if record.identity.item_type is not InventoryItemType.FILE:
                updated_items.append(item)
                continue
            if not isinstance(record, FileInventoryRecord):
                raise InventoryContentCaptureError(
                    f"file identity does not contain a file record: {record.identity.relative_path}"
                )
            if record.capture_status is not InventoryCaptureStatus.PENDING:
                raise InventoryContentCaptureError(
                    "content capture accepts only pending file records: "
                    f"{record.identity.relative_path}"
                )

            updated, certification, exception = self._capture_file(
                root=root,
                item=item,
                record=record,
            )
            updated_items.append(updated)
            if certification is not None:
                certifications.append(certification)
            if exception is not None:
                exceptions.append(exception)

        updated_items.sort(key=lambda value: value.record.identity.relative_path.as_posix())
        certifications.sort(key=lambda value: value.relative_path.as_posix())
        exceptions.sort(key=lambda value: value.relative_path.as_posix())
        completed_at_utc = self._clock()

        return InventoryContentCaptureResult(
            schema_version=STORAGE_CONTENT_CAPTURE_SCHEMA_VERSION,
            source_root_id=inventory.source_root_id,
            root_path=root,
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
            items=tuple(updated_items),
            unsupported_items=inventory.unsupported_items,
            certifications=tuple(certifications),
            exceptions=tuple(exceptions),
            totals=_build_totals(
                items=tuple(updated_items),
                unsupported_count=len(inventory.unsupported_items),
                original=inventory.totals,
            ),
        )

    def _capture_file(
        self,
        *,
        root: Path,
        item: AssembledInventoryItem,
        record: FileInventoryRecord,
    ) -> tuple[
        AssembledInventoryItem,
        FileContentCertification | None,
        ContentCaptureException | None,
    ]:
        path = root / record.identity.relative_path
        started_at_utc = self._clock()

        try:
            metadata = os.lstat(path)
            if not stat.S_ISREG(metadata.st_mode):
                return self._exception_result(
                    item=item,
                    record=record,
                    code=ContentCaptureExceptionCode.NOT_REGULAR_FILE,
                    detail=f"Source path is not a regular file: {path}",
                    status=InventoryCaptureStatus.ERROR,
                )
            digest, observed_bytes = _stream_sha256(
                path=path,
                chunk_size_bytes=self._policy.chunk_size_bytes,
            )
        except FileNotFoundError as exc:
            return self._exception_result(
                item=item,
                record=record,
                code=ContentCaptureExceptionCode.FILE_NOT_FOUND,
                detail=str(exc),
                status=InventoryCaptureStatus.INACCESSIBLE,
            )
        except PermissionError as exc:
            return self._exception_result(
                item=item,
                record=record,
                code=ContentCaptureExceptionCode.PERMISSION_DENIED,
                detail=str(exc),
                status=InventoryCaptureStatus.INACCESSIBLE,
            )
        except OSError as exc:
            return self._exception_result(
                item=item,
                record=record,
                code=ContentCaptureExceptionCode.FILESYSTEM_ERROR,
                detail=str(exc),
                status=InventoryCaptureStatus.ERROR,
            )

        completed_at_utc = self._clock()
        if observed_bytes != record.size_bytes:
            detail = (
                "Source byte count changed after discovery: "
                f"expected {record.size_bytes}, observed {observed_bytes}"
            )
            updated = replace(
                record,
                sha256=None,
                capture_status=InventoryCaptureStatus.ERROR,
                error_detail=detail,
            )
            return (
                AssembledInventoryItem(item_id=item.item_id, record=updated),
                None,
                ContentCaptureException(
                    code=ContentCaptureExceptionCode.BYTE_COUNT_MISMATCH,
                    item_id=item.item_id,
                    relative_path=record.identity.relative_path,
                    detail=detail,
                ),
            )

        updated = replace(
            record,
            sha256=digest,
            capture_status=InventoryCaptureStatus.CAPTURED,
            error_detail=None,
            captured_at_utc=completed_at_utc,
        )
        certification = FileContentCertification(
            item_id=item.item_id,
            relative_path=record.identity.relative_path,
            expected_byte_count=record.size_bytes,
            observed_byte_count=observed_bytes,
            sha256=digest,
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
        )
        return (
            AssembledInventoryItem(item_id=item.item_id, record=updated),
            certification,
            None,
        )

    @staticmethod
    def _exception_result(
        *,
        item: AssembledInventoryItem,
        record: FileInventoryRecord,
        code: ContentCaptureExceptionCode,
        detail: str,
        status: InventoryCaptureStatus,
    ) -> tuple[AssembledInventoryItem, None, ContentCaptureException]:
        updated = replace(
            record,
            sha256=None,
            capture_status=status,
            error_detail=detail,
        )
        return (
            AssembledInventoryItem(item_id=item.item_id, record=updated),
            None,
            ContentCaptureException(
                code=code,
                item_id=item.item_id,
                relative_path=record.identity.relative_path,
                detail=detail,
            ),
        )


def _stream_sha256(*, path: Path, chunk_size_bytes: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    byte_count = 0
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size_bytes):
            digest.update(chunk)
            byte_count += len(chunk)
    return digest.hexdigest(), byte_count


def _build_totals(
    *,
    items: tuple[AssembledInventoryItem, ...],
    unsupported_count: int,
    original: InventoryTotals,
) -> InventoryTotals:
    captured_count = 0
    excluded_count = 0
    inaccessible_count = 0
    error_count = 0
    pending_count = unsupported_count

    for item in items:
        status = item.record.capture_status
        if status is InventoryCaptureStatus.CAPTURED:
            captured_count += 1
        elif status is InventoryCaptureStatus.EXCLUDED:
            excluded_count += 1
        elif status is InventoryCaptureStatus.INACCESSIBLE:
            inaccessible_count += 1
        elif status is InventoryCaptureStatus.ERROR:
            error_count += 1
        elif status is InventoryCaptureStatus.PENDING:
            pending_count += 1

    return InventoryTotals(
        directory_count=original.directory_count,
        file_count=original.file_count,
        symbolic_link_count=original.symbolic_link_count,
        junction_count=original.junction_count,
        other_item_count=original.other_item_count,
        total_file_bytes=original.total_file_bytes,
        captured_count=captured_count,
        excluded_count=excluded_count,
        inaccessible_count=inaccessible_count,
        error_count=error_count,
        pending_count=pending_count,
    )


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)
