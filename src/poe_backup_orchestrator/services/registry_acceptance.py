"""Atomic promotion of validated Registry acquisition artifacts."""

from __future__ import annotations

import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path

from poe_backup_orchestrator.exceptions import RegistryAcceptanceError
from poe_backup_orchestrator.models.registry_acceptance import (
    RegistryAcceptanceResult,
)
from poe_backup_orchestrator.models.registry_ingestion import (
    RegistryIngestionResult,
)


def _derive_run_id(created_at: str) -> str:
    """Convert an ISO-8601 acquisition timestamp into a repository run ID."""

    try:
        parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryAcceptanceError(f"Invalid acquisition timestamp: {created_at!r}") from exc

    return parsed.strftime("%Y%m%dT%H%M%SZ")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def _copy_and_sync(source: Path, partial_destination: Path) -> None:
    """Copy a file and force its contents to stable storage."""

    with source.open("rb") as source_handle:
        with partial_destination.open("xb") as destination_handle:
            shutil.copyfileobj(
                source_handle,
                destination_handle,
                length=1024 * 1024,
            )
            destination_handle.flush()
            os.fsync(destination_handle.fileno())


def _sync_directory(path: Path) -> None:
    """Force directory metadata changes to stable storage."""

    descriptor = os.open(path, os.O_RDONLY)

    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def accept_registry_acquisition(
    ingestion_result: RegistryIngestionResult,
    destination_root: Path,
) -> RegistryAcceptanceResult:
    """Promote a validated acquisition into the managed repository.

    The snapshot is copied, verified, and atomically published first. The
    manifest is atomically published last. The source acquisition is not
    modified or removed.
    """

    destination_root = destination_root.resolve()

    if not destination_root.exists():
        raise RegistryAcceptanceError(
            f"Registry destination root does not exist: {destination_root}"
        )

    if not destination_root.is_dir():
        raise RegistryAcceptanceError(
            f"Registry destination root is not a directory: {destination_root}"
        )

    source_snapshot = ingestion_result.snapshot_path.resolve()
    source_manifest = ingestion_result.manifest_path.resolve()

    if not source_snapshot.is_file():
        raise RegistryAcceptanceError(f"Validated snapshot no longer exists: {source_snapshot}")

    if not source_manifest.is_file():
        raise RegistryAcceptanceError(f"Validated manifest no longer exists: {source_manifest}")

    run_id = _derive_run_id(ingestion_result.created_at)
    destination_directory = destination_root / run_id

    if destination_directory.exists():
        raise RegistryAcceptanceError(
            f"Registry acceptance destination already exists: {destination_directory}"
        )

    snapshot_path = destination_directory / source_snapshot.name
    manifest_path = destination_directory / source_manifest.name

    partial_snapshot = snapshot_path.with_name(snapshot_path.name + ".partial")
    partial_manifest = manifest_path.with_name(manifest_path.name + ".partial")

    created_destination = False

    try:
        destination_directory.mkdir(mode=0o770)
        created_destination = True

        _copy_and_sync(source_snapshot, partial_snapshot)

        copied_size = partial_snapshot.stat().st_size
        if copied_size != ingestion_result.size_bytes:
            raise RegistryAcceptanceError(
                "Accepted snapshot size verification failed: "
                f"expected {ingestion_result.size_bytes}, got {copied_size}"
            )

        copied_sha256 = _sha256_file(partial_snapshot)
        if copied_sha256 != ingestion_result.sha256:
            raise RegistryAcceptanceError(
                "Accepted snapshot SHA-256 verification failed: "
                f"expected {ingestion_result.sha256}, got {copied_sha256}"
            )

        os.replace(partial_snapshot, snapshot_path)
        _sync_directory(destination_directory)

        _copy_and_sync(source_manifest, partial_manifest)
        os.replace(partial_manifest, manifest_path)
        _sync_directory(destination_directory)
        _sync_directory(destination_root)

    except RegistryAcceptanceError:
        if created_destination:
            shutil.rmtree(destination_directory, ignore_errors=True)
        raise
    except OSError as exc:
        if created_destination:
            shutil.rmtree(destination_directory, ignore_errors=True)

        raise RegistryAcceptanceError(f"Registry acquisition acceptance failed: {exc}") from exc

    return RegistryAcceptanceResult(
        asset_id=ingestion_result.asset_id,
        run_id=run_id,
        destination_directory=destination_directory,
        snapshot_path=snapshot_path,
        manifest_path=manifest_path,
        sha256=ingestion_result.sha256,
        size_bytes=ingestion_result.size_bytes,
    )
