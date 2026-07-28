"""Controlled directory materialization for governed restore workspaces."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_workspace import (
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightReadiness,
)
from poe_backup_orchestrator.models.restore_workspace_materialization import (
    RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION,
    RestoreWorkspaceDirectoryRecord,
    RestoreWorkspaceMaterialization,
    RestoreWorkspaceMaterializationReasonCode,
    RestoreWorkspaceMaterializationStatus,
)


class RestoreWorkspaceMaterializationError(RuntimeError):
    """Raised when governed workspace materialization cannot complete safely."""


class WorkspaceFilesystemOperator(Protocol):
    """Filesystem operations required by workspace materialization."""

    def exists(self, path: Path) -> bool: ...

    def is_directory(self, path: Path) -> bool: ...

    def create_directory(self, path: Path) -> tuple[Path, ...]: ...

    def remove_directory_if_empty(self, path: Path) -> None: ...


@dataclass(frozen=True, slots=True)
class LocalWorkspaceFilesystemOperator:
    """Local filesystem implementation with bounded directory mutation."""

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_directory(self, path: Path) -> bool:
        return path.is_dir()

    def create_directory(self, path: Path) -> tuple[Path, ...]:
        missing: list[Path] = []
        candidate = path
        while not candidate.exists():
            missing.append(candidate)
            parent = candidate.parent
            if parent == candidate:
                break
            candidate = parent

        path.mkdir(parents=True, exist_ok=False)
        return tuple(reversed(missing))

    def remove_directory_if_empty(self, path: Path) -> None:
        path.rmdir()


@dataclass(frozen=True, slots=True)
class RestoreWorkspaceMaterializationService:
    """Create only plan-derived staging and rollback directory structures."""

    filesystem: WorkspaceFilesystemOperator

    def materialize(
        self,
        plan: RestorePlan,
        preflight: RestoreWorkspacePreflight,
        *,
        materialized_at_utc: datetime,
    ) -> RestoreWorkspaceMaterialization:
        _validate_inputs(plan, preflight, materialized_at_utc)

        staging_artifact = plan.staging_target_path
        rollback_artifact = plan.rollback_artifact_path
        if self.filesystem.exists(staging_artifact):
            raise RestoreWorkspaceMaterializationError(
                f"staging artifact path already exists: {staging_artifact}"
            )
        if self.filesystem.exists(rollback_artifact):
            raise RestoreWorkspaceMaterializationError(
                f"rollback artifact path already exists: {rollback_artifact}"
            )

        required = (
            ("staging", staging_artifact.parent),
            ("rollback", rollback_artifact.parent),
        )
        if required[0][1] == required[1][1]:
            raise RestoreWorkspaceMaterializationError(
                "staging and rollback directories must be distinct"
            )

        records: list[RestoreWorkspaceDirectoryRecord] = []
        created_this_run: list[Path] = []

        try:
            for purpose, directory in required:
                if self.filesystem.exists(directory):
                    if not self.filesystem.is_directory(directory):
                        raise RestoreWorkspaceMaterializationError(
                            f"{purpose} workspace path is not a directory: {directory}"
                        )
                    created = False
                else:
                    created_paths = self.filesystem.create_directory(directory)
                    created_this_run.extend(created_paths)
                    created = True

                records.append(
                    RestoreWorkspaceDirectoryRecord(
                        ordinal=len(records) + 1,
                        purpose=purpose,
                        path=directory,
                        created=created,
                    )
                )
        except Exception as exc:
            cleanup_errors = _cleanup(
                self.filesystem,
                created_this_run,
            )
            detail = f"workspace materialization failed: {exc}"
            if cleanup_errors:
                detail += "; cleanup failures: " + " | ".join(cleanup_errors)
            raise RestoreWorkspaceMaterializationError(detail) from exc

        reason = (
            RestoreWorkspaceMaterializationReasonCode.WORKSPACE_MATERIALIZED
            if any(record.created for record in records)
            else RestoreWorkspaceMaterializationReasonCode.WORKSPACE_REUSED
        )

        return RestoreWorkspaceMaterialization(
            schema_version=RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            materialized_at_utc=materialized_at_utc,
            status=RestoreWorkspaceMaterializationStatus.MATERIALIZED,
            reason_codes=(reason,),
            directories=tuple(records),
            artifact_copied=False,
        )


def materialize_restore_workspace(
    plan: RestorePlan,
    preflight: RestoreWorkspacePreflight,
    *,
    materialized_at_utc: datetime,
    filesystem: WorkspaceFilesystemOperator | None = None,
) -> RestoreWorkspaceMaterialization:
    """Materialize one governed restore workspace."""

    return RestoreWorkspaceMaterializationService(
        filesystem=filesystem or LocalWorkspaceFilesystemOperator()
    ).materialize(
        plan,
        preflight,
        materialized_at_utc=materialized_at_utc,
    )


def _validate_inputs(
    plan: RestorePlan,
    preflight: RestoreWorkspacePreflight,
    materialized_at_utc: datetime,
) -> None:
    if materialized_at_utc.tzinfo is None or materialized_at_utc.utcoffset() is None:
        raise RestoreWorkspaceMaterializationError("materialized_at_utc must be timezone-aware")
    if materialized_at_utc.utcoffset() != UTC.utcoffset(materialized_at_utc):
        raise RestoreWorkspaceMaterializationError("materialized_at_utc must use UTC")
    if preflight.plan_id != plan.plan_id:
        raise RestoreWorkspaceMaterializationError("preflight plan_id does not match restore plan")
    if preflight.readiness is not RestoreWorkspacePreflightReadiness.READY:
        raise RestoreWorkspaceMaterializationError("workspace preflight must be ready")
    if preflight.mutation_performed:
        raise RestoreWorkspaceMaterializationError("workspace preflight must be read-only")


def _cleanup(
    filesystem: WorkspaceFilesystemOperator,
    created_paths: list[Path],
) -> tuple[str, ...]:
    errors: list[str] = []
    for path in reversed(created_paths):
        try:
            filesystem.remove_directory_if_empty(path)
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    return tuple(errors)
