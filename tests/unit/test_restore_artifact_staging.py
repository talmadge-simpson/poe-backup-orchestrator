"""Tests for governed restore artifact staging."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION,
    RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanValidation,
    RestoreWorkspaceDirectoryRecord,
    RestoreWorkspaceMaterialization,
    RestoreWorkspaceMaterializationReasonCode,
    RestoreWorkspaceMaterializationStatus,
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightCheck,
    RestoreWorkspacePreflightReadiness,
    RestoreWorkspacePreflightReasonCode,
)
from poe_backup_orchestrator.services.restore import (
    RestoreArtifactStagingError,
    stage_restore_artifact,
)

NOW = datetime(2026, 7, 28, 17, 0, tzinfo=UTC)


def plan(tmp_path: Path) -> RestorePlan:
    source = tmp_path / "repository" / "registry.sqlite3"
    target = tmp_path / "authoritative" / "POERegistry.db"
    staging = tmp_path / "restore-tests" / "Staging" / "plan-1" / "registry.sqlite3"
    rollback = tmp_path / "restore-tests" / "Rollback" / "plan-1" / "POERegistry.db"

    source.parent.mkdir(parents=True)
    staging.parent.mkdir(parents=True)
    rollback.parent.mkdir(parents=True)
    target.parent.mkdir(parents=True)
    source.write_bytes(b"registry-backup-content")

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-1",
        created_at_utc=NOW,
        recovery_point_id="rp-1",
        source_artifact_path=source,
        source_manifest_path=tmp_path / "repository" / "manifest.json",
        authoritative_target_path=target,
        staging_target_path=staging,
        rollback_artifact_path=rollback,
        actions=(
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect target.",
                destination_path=target,
            ),
        ),
        validation=RestorePlanValidation(
            readiness=RestorePlanReadiness.READY,
            reason_codes=(RestorePlanReasonCode.PLAN_READY,),
            warnings=(),
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=NOW,
        ),
        execution_authorized=False,
    )


def ready_preflight(restore_plan: RestorePlan) -> RestoreWorkspacePreflight:
    return RestoreWorkspacePreflight(
        schema_version=RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
        plan_id=restore_plan.plan_id,
        evaluated_at_utc=NOW,
        readiness=RestoreWorkspacePreflightReadiness.READY,
        reason_codes=(RestoreWorkspacePreflightReasonCode.PREFLIGHT_READY,),
        checks=(
            RestoreWorkspacePreflightCheck(
                ordinal=1,
                code="ready",
                passed=True,
                path=None,
                detail="Ready.",
            ),
        ),
        warnings=(),
        mutation_performed=False,
    )


def materialized(restore_plan: RestorePlan) -> RestoreWorkspaceMaterialization:
    return RestoreWorkspaceMaterialization(
        schema_version=RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION,
        plan_id=restore_plan.plan_id,
        materialized_at_utc=NOW,
        status=RestoreWorkspaceMaterializationStatus.MATERIALIZED,
        reason_codes=(RestoreWorkspaceMaterializationReasonCode.WORKSPACE_MATERIALIZED,),
        directories=(
            RestoreWorkspaceDirectoryRecord(
                ordinal=1,
                purpose="staging",
                path=restore_plan.staging_target_path.parent,
                created=True,
            ),
            RestoreWorkspaceDirectoryRecord(
                ordinal=2,
                purpose="rollback",
                path=restore_plan.rollback_artifact_path.parent,
                created=True,
            ),
        ),
        artifact_copied=False,
    )


def test_stage_copies_exact_source_bytes(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    target_before = restore_plan.authoritative_target_path.exists()

    result = stage_restore_artifact(
        restore_plan,
        ready_preflight(restore_plan),
        materialized(restore_plan),
        staged_at_utc=NOW,
    )

    assert restore_plan.staging_target_path.read_bytes() == (
        restore_plan.source_artifact_path.read_bytes()
    )
    assert result.source_size_bytes == result.staged_size_bytes
    assert result.authoritative_target_modified is False
    assert restore_plan.authoritative_target_path.exists() is target_before
    assert not restore_plan.rollback_artifact_path.exists()


def test_existing_staging_artifact_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    restore_plan.staging_target_path.write_bytes(b"existing")

    with pytest.raises(
        RestoreArtifactStagingError,
        match="staging artifact already exists",
    ):
        stage_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staged_at_utc=NOW,
        )

    assert restore_plan.staging_target_path.read_bytes() == b"existing"


def test_missing_source_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    restore_plan.source_artifact_path.unlink()

    with pytest.raises(
        RestoreArtifactStagingError,
        match="source artifact is unavailable",
    ):
        stage_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staged_at_utc=NOW,
        )


def test_mismatched_materialization_plan_id_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    evidence = materialized(restore_plan)
    mismatched = RestoreWorkspaceMaterialization(
        schema_version=evidence.schema_version,
        plan_id="another-plan",
        materialized_at_utc=evidence.materialized_at_utc,
        status=evidence.status,
        reason_codes=evidence.reason_codes,
        directories=evidence.directories,
        artifact_copied=False,
    )

    with pytest.raises(
        RestoreArtifactStagingError,
        match="materialization plan_id does not match",
    ):
        stage_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            mismatched,
            staged_at_utc=NOW,
        )


def test_non_utc_timestamp_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    non_utc = NOW.astimezone(timezone(timedelta(hours=-4)))

    with pytest.raises(RestoreArtifactStagingError, match="must use UTC"):
        stage_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staged_at_utc=non_utc,
        )


class FailingCopyFilesystem:
    """Test double that leaves a temporary file before copy failure."""

    def __init__(self, restore_plan: RestorePlan) -> None:
        self.restore_plan = restore_plan
        self.temporary = restore_plan.staging_target_path.with_name(".registry.sqlite3.test.tmp")
        self.removed: list[Path] = []

    def is_readable_file(self, path: Path) -> bool:
        return path == self.restore_plan.source_artifact_path

    def is_directory(self, path: Path) -> bool:
        return path == self.restore_plan.staging_target_path.parent

    def exists(self, path: Path) -> bool:
        return path.exists()

    def size_bytes(self, path: Path) -> int:
        return path.stat().st_size

    def temporary_sibling(self, final_path: Path) -> Path:
        return self.temporary

    def copy_file(self, source: Path, temporary_path: Path) -> None:
        temporary_path.write_bytes(b"partial")
        raise OSError("simulated copy failure")

    def replace(self, temporary_path: Path, final_path: Path) -> None:
        raise AssertionError("replace must not be called")

    def remove_file_if_exists(self, path: Path) -> None:
        path.unlink(missing_ok=True)
        self.removed.append(path)


def test_partial_temporary_artifact_is_cleaned_up(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    filesystem = FailingCopyFilesystem(restore_plan)

    with pytest.raises(
        RestoreArtifactStagingError,
        match="simulated copy failure",
    ):
        stage_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staged_at_utc=NOW,
            filesystem=filesystem,
        )

    assert filesystem.temporary in filesystem.removed
    assert not filesystem.temporary.exists()
    assert not restore_plan.staging_target_path.exists()


def test_staging_contract_is_exported() -> None:
    from poe_backup_orchestrator.services import restore

    assert restore.stage_restore_artifact is stage_restore_artifact
