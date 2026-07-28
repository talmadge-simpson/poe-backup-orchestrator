"""Tests for staged restore artifact integrity validation."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_ARTIFACT_STAGING_SCHEMA_VERSION,
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RESTORE_WORKSPACE_MATERIALIZATION_SCHEMA_VERSION,
    RESTORE_WORKSPACE_PREFLIGHT_SCHEMA_VERSION,
    RestoreAction,
    RestoreActionType,
    RestoreArtifactStaging,
    RestoreArtifactStagingReasonCode,
    RestoreArtifactStagingStatus,
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
    RestoreStagedArtifactValidationError,
    validate_staged_restore_artifact,
)

NOW = datetime(2026, 7, 28, 18, 0, tzinfo=UTC)


def _create_sqlite(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE registry_asset (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO registry_asset(name) VALUES (?)",
            ("baseline",),
        )
        connection.commit()
    finally:
        connection.close()


def plan(tmp_path: Path) -> RestorePlan:
    source = tmp_path / "repository" / "registry.sqlite3"
    staged = tmp_path / "restore-tests" / "Staging" / "plan-1" / "registry.sqlite3"
    rollback = tmp_path / "restore-tests" / "Rollback" / "plan-1" / "POERegistry.db"
    authoritative = tmp_path / "authoritative" / "POERegistry.db"

    _create_sqlite(source)
    staged.parent.mkdir(parents=True)
    rollback.parent.mkdir(parents=True)
    authoritative.parent.mkdir(parents=True)
    staged.write_bytes(source.read_bytes())

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-1",
        created_at_utc=NOW,
        recovery_point_id="rp-1",
        source_artifact_path=source,
        source_manifest_path=tmp_path / "repository" / "manifest.json",
        authoritative_target_path=authoritative,
        staging_target_path=staged,
        rollback_artifact_path=rollback,
        actions=(
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect target.",
                destination_path=authoritative,
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


def staged(restore_plan: RestorePlan) -> RestoreArtifactStaging:
    source_size = restore_plan.source_artifact_path.stat().st_size
    staged_size = restore_plan.staging_target_path.stat().st_size
    return RestoreArtifactStaging(
        schema_version=RESTORE_ARTIFACT_STAGING_SCHEMA_VERSION,
        plan_id=restore_plan.plan_id,
        staged_at_utc=NOW,
        status=RestoreArtifactStagingStatus.STAGED,
        reason_codes=(RestoreArtifactStagingReasonCode.ARTIFACT_STAGED,),
        source_path=restore_plan.source_artifact_path,
        staged_path=restore_plan.staging_target_path,
        source_size_bytes=source_size,
        staged_size_bytes=staged_size,
        authoritative_target_modified=False,
    )


def test_valid_staged_sqlite_artifact_passes(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    authoritative_before = restore_plan.authoritative_target_path.exists()

    result = validate_staged_restore_artifact(
        restore_plan,
        ready_preflight(restore_plan),
        materialized(restore_plan),
        staged(restore_plan),
        validated_at_utc=NOW,
    )

    assert result.source_sha256 == result.staged_sha256
    assert result.quick_check_results == ("ok",)
    assert result.integrity_check_results == ("ok",)
    assert result.sqlite_opened_read_only is True
    assert result.authoritative_target_modified is False
    assert restore_plan.authoritative_target_path.exists() is authoritative_before


def test_digest_mismatch_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    staging_evidence = staged(restore_plan)
    content = bytearray(restore_plan.staging_target_path.read_bytes())
    content[-1] ^= 1
    restore_plan.staging_target_path.write_bytes(bytes(content))

    with pytest.raises(
        RestoreStagedArtifactValidationError,
        match="SHA-256 digests differ",
    ):
        validate_staged_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staging_evidence,
            validated_at_utc=NOW,
        )


def test_size_mismatch_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    staging_evidence = staged(restore_plan)
    with restore_plan.staging_target_path.open("ab") as handle:
        handle.write(b"x")

    with pytest.raises(
        RestoreStagedArtifactValidationError,
        match="byte counts differ",
    ):
        validate_staged_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staging_evidence,
            validated_at_utc=NOW,
        )


def test_non_sqlite_artifact_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    replacement = b"not-a-sqlite-database"
    restore_plan.source_artifact_path.write_bytes(replacement)
    restore_plan.staging_target_path.write_bytes(replacement)
    staging_evidence = staged(restore_plan)

    with pytest.raises(
        RestoreStagedArtifactValidationError,
        match="SQLite integrity checks failed to execute",
    ):
        validate_staged_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staging_evidence,
            validated_at_utc=NOW,
        )


class FailedQuickCheckOperator:
    def __init__(self, size_bytes: int) -> None:
        self._size_bytes = size_bytes

    def is_readable_file(self, path: Path) -> bool:
        return True

    def size_bytes(self, path: Path) -> int:
        return self._size_bytes

    def sha256(self, path: Path) -> str:
        return "a" * 64

    def sqlite_checks(
        self,
        path: Path,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        return ("database disk image is malformed",), ("ok",)


def test_quick_check_failure_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    staging_evidence = staged(restore_plan)

    with pytest.raises(
        RestoreStagedArtifactValidationError,
        match="quick_check did not return ok",
    ):
        validate_staged_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staging_evidence,
            validated_at_utc=NOW,
            integrity=FailedQuickCheckOperator(staging_evidence.source_size_bytes),
        )


def test_mismatched_staging_path_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    evidence = staged(restore_plan)
    mismatched = RestoreArtifactStaging(
        schema_version=evidence.schema_version,
        plan_id=evidence.plan_id,
        staged_at_utc=evidence.staged_at_utc,
        status=evidence.status,
        reason_codes=evidence.reason_codes,
        source_path=evidence.source_path,
        staged_path=tmp_path / "other.sqlite3",
        source_size_bytes=evidence.source_size_bytes,
        staged_size_bytes=evidence.staged_size_bytes,
        authoritative_target_modified=False,
    )

    with pytest.raises(
        RestoreStagedArtifactValidationError,
        match="staging target path does not match",
    ):
        validate_staged_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            mismatched,
            validated_at_utc=NOW,
        )


def test_non_utc_timestamp_is_rejected(tmp_path: Path) -> None:
    restore_plan = plan(tmp_path)
    non_utc = NOW.astimezone(timezone(timedelta(hours=-4)))

    with pytest.raises(
        RestoreStagedArtifactValidationError,
        match="must use UTC",
    ):
        validate_staged_restore_artifact(
            restore_plan,
            ready_preflight(restore_plan),
            materialized(restore_plan),
            staged(restore_plan),
            validated_at_utc=non_utc,
        )


def test_validation_contract_is_exported() -> None:
    from poe_backup_orchestrator.services import restore

    assert restore.validate_staged_restore_artifact is validate_staged_restore_artifact
