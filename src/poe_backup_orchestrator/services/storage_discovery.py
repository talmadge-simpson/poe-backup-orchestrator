"""Read-only filesystem discovery adapter foundation."""

from __future__ import annotations

import os
import stat
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from poe_backup_orchestrator.models.storage_discovery import (
    STORAGE_DISCOVERY_SCHEMA_VERSION,
    DiscoveredFilesystemEntry,
    DiscoveryEntryType,
    DiscoveryException,
    DiscoveryExceptionCode,
    DiscoveryStatus,
    FilesystemDiscoveryRequest,
    FilesystemDiscoveryResult,
)

Clock = Callable[[], datetime]


class FilesystemDiscoveryAdapter(Protocol):
    """Adapter contract for read-only source-root discovery."""

    def discover(
        self,
        request: FilesystemDiscoveryRequest,
    ) -> FilesystemDiscoveryResult:
        """Discover source-root entries without modifying the source."""


class LocalFilesystemDiscoveryAdapter:
    """Portable local-filesystem adapter using metadata-only operations."""

    def __init__(self, *, clock: Clock | None = None) -> None:
        self._clock = clock or _utc_now

    def discover(
        self,
        request: FilesystemDiscoveryRequest,
    ) -> FilesystemDiscoveryResult:
        started_at_utc = self._clock()
        root = request.root_path

        if not root.exists():
            return self._failed_result(
                request=request,
                started_at_utc=started_at_utc,
                code=DiscoveryExceptionCode.ROOT_NOT_FOUND,
                detail=f"Source root does not exist: {root}",
            )
        if not root.is_dir():
            return self._failed_result(
                request=request,
                started_at_utc=started_at_utc,
                code=DiscoveryExceptionCode.ROOT_NOT_DIRECTORY,
                detail=f"Source root is not a directory: {root}",
            )

        entries: list[DiscoveredFilesystemEntry] = []
        exceptions: list[DiscoveryException] = []
        self._walk_directory(
            request=request,
            current_path=root,
            depth=0,
            entries=entries,
            exceptions=exceptions,
        )

        entries.sort(key=lambda entry: entry.relative_path.as_posix())
        completed_at_utc = self._clock()
        status = (
            DiscoveryStatus.COMPLETED_WITH_EXCEPTIONS if exceptions else DiscoveryStatus.COMPLETED
        )
        return FilesystemDiscoveryResult(
            schema_version=STORAGE_DISCOVERY_SCHEMA_VERSION,
            discovery_request_id=request.discovery_request_id,
            source_root_id=request.source_root_id,
            root_path=root,
            started_at_utc=started_at_utc,
            completed_at_utc=completed_at_utc,
            status=status,
            entries=tuple(entries),
            exceptions=tuple(exceptions),
        )

    def _walk_directory(
        self,
        *,
        request: FilesystemDiscoveryRequest,
        current_path: Path,
        depth: int,
        entries: list[DiscoveredFilesystemEntry],
        exceptions: list[DiscoveryException],
    ) -> None:
        try:
            with os.scandir(current_path) as iterator:
                directory_entries = sorted(iterator, key=lambda item: item.name)
        except PermissionError as error:
            exceptions.append(
                DiscoveryException(
                    code=DiscoveryExceptionCode.PERMISSION_DENIED,
                    relative_path=_relative_or_none(current_path, request.root_path),
                    detail=str(error),
                )
            )
            return
        except OSError as error:
            exceptions.append(
                DiscoveryException(
                    code=DiscoveryExceptionCode.FILESYSTEM_ERROR,
                    relative_path=_relative_or_none(current_path, request.root_path),
                    detail=str(error),
                )
            )
            return

        for directory_entry in directory_entries:
            if not request.policy.include_hidden and directory_entry.name.startswith("."):
                continue

            entry_path = Path(directory_entry.path)
            relative_path = entry_path.relative_to(request.root_path)

            try:
                metadata = directory_entry.stat(follow_symlinks=False)
            except FileNotFoundError as error:
                exceptions.append(
                    DiscoveryException(
                        code=DiscoveryExceptionCode.ENTRY_DISAPPEARED,
                        relative_path=relative_path,
                        detail=str(error),
                    )
                )
                continue
            except PermissionError as error:
                exceptions.append(
                    DiscoveryException(
                        code=DiscoveryExceptionCode.PERMISSION_DENIED,
                        relative_path=relative_path,
                        detail=str(error),
                    )
                )
                continue
            except OSError as error:
                exceptions.append(
                    DiscoveryException(
                        code=DiscoveryExceptionCode.FILESYSTEM_ERROR,
                        relative_path=relative_path,
                        detail=str(error),
                    )
                )
                continue

            entry_type = _entry_type(metadata.st_mode)
            size_bytes = metadata.st_size if entry_type is DiscoveryEntryType.FILE else None
            modified_at_utc = datetime.fromtimestamp(metadata.st_mtime, tz=UTC)

            entries.append(
                DiscoveredFilesystemEntry(
                    source_root_id=request.source_root_id,
                    relative_path=relative_path,
                    entry_type=entry_type,
                    size_bytes=size_bytes,
                    modified_at_utc=modified_at_utc,
                    mode=stat.S_IMODE(metadata.st_mode),
                    is_hidden=directory_entry.name.startswith("."),
                )
            )

            if entry_type is not DiscoveryEntryType.DIRECTORY:
                continue

            next_depth = depth + 1
            if request.policy.max_depth is not None and next_depth > request.policy.max_depth:
                exceptions.append(
                    DiscoveryException(
                        code=DiscoveryExceptionCode.MAX_DEPTH_REACHED,
                        relative_path=relative_path,
                        detail=(
                            "Traversal stopped because the configured maximum depth "
                            f"of {request.policy.max_depth} was reached."
                        ),
                    )
                )
                continue

            self._walk_directory(
                request=request,
                current_path=entry_path,
                depth=next_depth,
                entries=entries,
                exceptions=exceptions,
            )

    def _failed_result(
        self,
        *,
        request: FilesystemDiscoveryRequest,
        started_at_utc: datetime,
        code: DiscoveryExceptionCode,
        detail: str,
    ) -> FilesystemDiscoveryResult:
        return FilesystemDiscoveryResult(
            schema_version=STORAGE_DISCOVERY_SCHEMA_VERSION,
            discovery_request_id=request.discovery_request_id,
            source_root_id=request.source_root_id,
            root_path=request.root_path,
            started_at_utc=started_at_utc,
            completed_at_utc=self._clock(),
            status=DiscoveryStatus.FAILED,
            entries=(),
            exceptions=(
                DiscoveryException(
                    code=code,
                    relative_path=None,
                    detail=detail,
                ),
            ),
        )


def _entry_type(mode: int) -> DiscoveryEntryType:
    if stat.S_ISLNK(mode):
        return DiscoveryEntryType.SYMBOLIC_LINK
    if stat.S_ISDIR(mode):
        return DiscoveryEntryType.DIRECTORY
    if stat.S_ISREG(mode):
        return DiscoveryEntryType.FILE
    return DiscoveryEntryType.OTHER


def _relative_or_none(path: Path, root: Path) -> Path | None:
    if path == root:
        return None
    return path.relative_to(root)


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)
