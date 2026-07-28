"""Governed copying of recovery artifacts into isolated staging."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO, Protocol
from uuid import uuid4

from poe_backup_orchestrator.models.restore_artifact_staging import (
    RESTORE_ARTIFACT_STAGING_SCHEMA_VERSION,
    RestoreArtifactStaging,
    RestoreArtifactStagingReasonCode,
    RestoreArtifactStagingStatus,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_workspace import (
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightReadiness,
)
from poe_backup_orchestrator.models.restore_workspace_materialization import (
    RestoreWorkspaceMaterialization,
    RestoreWorkspaceMaterializationStatus,
)


class RestoreArtifactStagingError(RuntimeError):
    """Raised when governed artifact staging cannot complete safely."""


class ArtifactFilesystemOperator(Protocol):
    """Filesystem operations required by artifact staging."""

    def is_readable_file(self, path: Path) -> bool: ...

    def is_directory(self, path: Path) -> bool: ...

    def exists(self, path: Path) -> bool: ...

    def size_bytes(self, path: Path) -> int: ...

    def temporary_sibling(self, final_path: Path) -> Path: ...

    def copy_file(self, source: Path, temporary_path: Path) -> None: ...

    def replace(self, temporary_path: Path, final_path: Path) -> None: ...

    def remove_file_if_exists(self, path: Path) -> None: ...


@dataclass(frozen=True, slots=True)
class LocalArtifactFilesystemOperator:
    """Local filesystem implementation with atomic final placement."""

    def is_readable_file(self, path: Path) -> bool:
        return path.is_file() and os.access(path, os.R_OK)

    def is_directory(self, path: Path) -> bool:
        return path.is_dir()

    def exists(self, path: Path) -> bool:
        return path.exists()

    def size_bytes(self, path: Path) -> int:
        return path.stat().st_size

    def temporary_sibling(self, final_path: Path) -> Path:
        return final_path.with_name(f".{final_path.name}.staging-{uuid4().hex}.tmp")

    def copy_file(self, source: Path, temporary_path: Path) -> None:
        with source.open("rb") as source_handle:
            with temporary_path.open("xb") as target_handle:
                _copy_and_sync(source_handle, target_handle)

    def replace(self, temporary_path: Path, final_path: Path) -> None:
        os.replace(temporary_path, final_path)

    def remove_file_if_exists(self, path: Path) -> None:
        path.unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class RestoreArtifactStagingService:
    """Copy exactly one recovery artifact into the governed staging path."""

    filesystem: ArtifactFilesystemOperator

    def stage(
        self,
        plan: RestorePlan,
        preflight: RestoreWorkspacePreflight,
        materialization: RestoreWorkspaceMaterialization,
        *,
        staged_at_utc: datetime,
    ) -> RestoreArtifactStaging:
        _validate_inputs(plan, preflight, materialization, staged_at_utc)

        source = plan.source_artifact_path
        staged = plan.staging_target_path
        rollback = plan.rollback_artifact_path
        authoritative = plan.authoritative_target_path

        if len({source, staged, authoritative}) != 3:
            raise RestoreArtifactStagingError(
                "source, staging, and authoritative paths must be distinct"
            )
        if not self.filesystem.is_readable_file(source):
            raise RestoreArtifactStagingError(
                f"source artifact is unavailable or unreadable: {source}"
            )
        if not self.filesystem.is_directory(staged.parent):
            raise RestoreArtifactStagingError(f"staging parent is not a directory: {staged.parent}")
        if self.filesystem.exists(staged):
            raise RestoreArtifactStagingError(f"staging artifact already exists: {staged}")
        if self.filesystem.exists(rollback):
            raise RestoreArtifactStagingError(f"rollback artifact already exists: {rollback}")

        temporary = self.filesystem.temporary_sibling(staged)
        if temporary.parent != staged.parent:
            raise RestoreArtifactStagingError(
                "temporary artifact must be a sibling of the final staging path"
            )
        if self.filesystem.exists(temporary):
            raise RestoreArtifactStagingError(f"temporary staging path already exists: {temporary}")

        try:
            source_size = self.filesystem.size_bytes(source)
            self.filesystem.copy_file(source, temporary)
            temporary_size = self.filesystem.size_bytes(temporary)
            if source_size != temporary_size:
                raise RestoreArtifactStagingError("source and temporary staged byte counts differ")
            self.filesystem.replace(temporary, staged)
            staged_size = self.filesystem.size_bytes(staged)
            if source_size != staged_size:
                raise RestoreArtifactStagingError("source and final staged byte counts differ")
        except Exception as exc:
            cleanup_error: Exception | None = None
            try:
                self.filesystem.remove_file_if_exists(temporary)
            except Exception as cleanup_exc:
                cleanup_error = cleanup_exc

            detail = f"artifact staging failed: {exc}"
            if cleanup_error is not None:
                detail += f"; temporary cleanup failed: {cleanup_error}"
            raise RestoreArtifactStagingError(detail) from exc

        return RestoreArtifactStaging(
            schema_version=RESTORE_ARTIFACT_STAGING_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            staged_at_utc=staged_at_utc,
            status=RestoreArtifactStagingStatus.STAGED,
            reason_codes=(RestoreArtifactStagingReasonCode.ARTIFACT_STAGED,),
            source_path=source,
            staged_path=staged,
            source_size_bytes=source_size,
            staged_size_bytes=staged_size,
            authoritative_target_modified=False,
        )


def stage_restore_artifact(
    plan: RestorePlan,
    preflight: RestoreWorkspacePreflight,
    materialization: RestoreWorkspaceMaterialization,
    *,
    staged_at_utc: datetime,
    filesystem: ArtifactFilesystemOperator | None = None,
) -> RestoreArtifactStaging:
    """Stage one recovery artifact in the isolated restore workspace."""

    return RestoreArtifactStagingService(
        filesystem=filesystem or LocalArtifactFilesystemOperator()
    ).stage(
        plan,
        preflight,
        materialization,
        staged_at_utc=staged_at_utc,
    )


def _validate_inputs(
    plan: RestorePlan,
    preflight: RestoreWorkspacePreflight,
    materialization: RestoreWorkspaceMaterialization,
    staged_at_utc: datetime,
) -> None:
    if staged_at_utc.tzinfo is None or staged_at_utc.utcoffset() is None:
        raise RestoreArtifactStagingError("staged_at_utc must be timezone-aware")
    if staged_at_utc.utcoffset() != UTC.utcoffset(staged_at_utc):
        raise RestoreArtifactStagingError("staged_at_utc must use UTC")
    if preflight.plan_id != plan.plan_id:
        raise RestoreArtifactStagingError("preflight plan_id does not match restore plan")
    if preflight.readiness is not RestoreWorkspacePreflightReadiness.READY:
        raise RestoreArtifactStagingError("workspace preflight must be ready")
    if materialization.plan_id != plan.plan_id:
        raise RestoreArtifactStagingError("materialization plan_id does not match restore plan")
    if materialization.status is not RestoreWorkspaceMaterializationStatus.MATERIALIZED:
        raise RestoreArtifactStagingError("workspace materialization must be successful")
    if materialization.artifact_copied:
        raise RestoreArtifactStagingError(
            "materialization evidence must not report artifact copying"
        )


def _copy_and_sync(source: BinaryIO, target: BinaryIO) -> None:
    shutil.copyfileobj(source, target, length=1024 * 1024)
    target.flush()
    os.fsync(target.fileno())
