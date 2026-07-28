"""Cryptographic and SQLite validation of isolated staged restore artifacts."""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol
from urllib.parse import quote

from poe_backup_orchestrator.models.restore_artifact_staging import (
    RestoreArtifactStaging,
    RestoreArtifactStagingStatus,
)
from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_staged_artifact_validation import (
    RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION,
    RestoreStagedArtifactValidation,
    RestoreStagedArtifactValidationReasonCode,
    RestoreStagedArtifactValidationStatus,
)
from poe_backup_orchestrator.models.restore_workspace import (
    RestoreWorkspacePreflight,
    RestoreWorkspacePreflightReadiness,
)
from poe_backup_orchestrator.models.restore_workspace_materialization import (
    RestoreWorkspaceMaterialization,
    RestoreWorkspaceMaterializationStatus,
)


class RestoreStagedArtifactValidationError(RuntimeError):
    """Raised when staged artifact validation cannot succeed safely."""


class ArtifactIntegrityOperator(Protocol):
    """Read-only file and SQLite operations required by validation."""

    def is_readable_file(self, path: Path) -> bool: ...

    def size_bytes(self, path: Path) -> int: ...

    def sha256(self, path: Path) -> str: ...

    def sqlite_checks(self, path: Path) -> tuple[tuple[str, ...], tuple[str, ...]]: ...


@dataclass(frozen=True, slots=True)
class LocalArtifactIntegrityOperator:
    """Local read-only integrity implementation."""

    chunk_size_bytes: int = 1024 * 1024

    def is_readable_file(self, path: Path) -> bool:
        return path.is_file()

    def size_bytes(self, path: Path) -> int:
        return path.stat().st_size

    def sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(self.chunk_size_bytes):
                digest.update(chunk)
        return digest.hexdigest()

    def sqlite_checks(
        self,
        path: Path,
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        uri = f"file:{quote(str(path.resolve()))}?mode=ro&immutable=1"
        try:
            connection = sqlite3.connect(uri, uri=True)
        except sqlite3.Error as exc:
            raise RestoreStagedArtifactValidationError(
                f"staged SQLite artifact could not be opened read-only: {exc}"
            ) from exc

        try:
            quick = tuple(str(row[0]) for row in connection.execute("PRAGMA quick_check"))
            integrity = tuple(str(row[0]) for row in connection.execute("PRAGMA integrity_check"))
        except sqlite3.Error as exc:
            raise RestoreStagedArtifactValidationError(
                f"SQLite integrity checks failed to execute: {exc}"
            ) from exc
        finally:
            connection.close()

        return quick, integrity


@dataclass(frozen=True, slots=True)
class RestoreStagedArtifactValidationService:
    """Validate staged bytes and SQLite structure without mutation."""

    integrity: ArtifactIntegrityOperator

    def validate(
        self,
        plan: RestorePlan,
        preflight: RestoreWorkspacePreflight,
        materialization: RestoreWorkspaceMaterialization,
        staging: RestoreArtifactStaging,
        *,
        validated_at_utc: datetime,
    ) -> RestoreStagedArtifactValidation:
        _validate_inputs(
            plan,
            preflight,
            materialization,
            staging,
            validated_at_utc,
        )

        source = plan.source_artifact_path
        staged = plan.staging_target_path

        if not self.integrity.is_readable_file(source):
            raise RestoreStagedArtifactValidationError(f"source artifact is unavailable: {source}")
        if not self.integrity.is_readable_file(staged):
            raise RestoreStagedArtifactValidationError(f"staged artifact is unavailable: {staged}")

        source_size = self.integrity.size_bytes(source)
        staged_size = self.integrity.size_bytes(staged)
        if source_size != staged_size:
            raise RestoreStagedArtifactValidationError("source and staged byte counts differ")
        if source_size != staging.source_size_bytes:
            raise RestoreStagedArtifactValidationError(
                "source byte count differs from staging evidence"
            )
        if staged_size != staging.staged_size_bytes:
            raise RestoreStagedArtifactValidationError(
                "staged byte count differs from staging evidence"
            )

        source_sha256 = self.integrity.sha256(source)
        staged_sha256 = self.integrity.sha256(staged)
        if source_sha256 != staged_sha256:
            raise RestoreStagedArtifactValidationError("source and staged SHA-256 digests differ")

        quick_results, integrity_results = self.integrity.sqlite_checks(staged)
        if not _results_ok(quick_results):
            raise RestoreStagedArtifactValidationError("SQLite quick_check did not return ok")
        if not _results_ok(integrity_results):
            raise RestoreStagedArtifactValidationError("SQLite integrity_check did not return ok")

        return RestoreStagedArtifactValidation(
            schema_version=RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            validated_at_utc=validated_at_utc,
            status=RestoreStagedArtifactValidationStatus.VALID,
            reason_codes=(
                RestoreStagedArtifactValidationReasonCode.BYTE_COUNTS_MATCH,
                RestoreStagedArtifactValidationReasonCode.SHA256_MATCH,
                RestoreStagedArtifactValidationReasonCode.SQLITE_QUICK_CHECK_OK,
                RestoreStagedArtifactValidationReasonCode.SQLITE_INTEGRITY_CHECK_OK,
                RestoreStagedArtifactValidationReasonCode.STAGED_ARTIFACT_VALID,
            ),
            source_path=source,
            staged_path=staged,
            source_size_bytes=source_size,
            staged_size_bytes=staged_size,
            source_sha256=source_sha256,
            staged_sha256=staged_sha256,
            sqlite_opened_read_only=True,
            quick_check_results=quick_results,
            integrity_check_results=integrity_results,
            authoritative_target_modified=False,
        )


def validate_staged_restore_artifact(
    plan: RestorePlan,
    preflight: RestoreWorkspacePreflight,
    materialization: RestoreWorkspaceMaterialization,
    staging: RestoreArtifactStaging,
    *,
    validated_at_utc: datetime,
    integrity: ArtifactIntegrityOperator | None = None,
) -> RestoreStagedArtifactValidation:
    """Validate one isolated staged restore artifact."""

    return RestoreStagedArtifactValidationService(
        integrity=integrity or LocalArtifactIntegrityOperator()
    ).validate(
        plan,
        preflight,
        materialization,
        staging,
        validated_at_utc=validated_at_utc,
    )


def _validate_inputs(
    plan: RestorePlan,
    preflight: RestoreWorkspacePreflight,
    materialization: RestoreWorkspaceMaterialization,
    staging: RestoreArtifactStaging,
    validated_at_utc: datetime,
) -> None:
    if validated_at_utc.tzinfo is None or validated_at_utc.utcoffset() is None:
        raise RestoreStagedArtifactValidationError("validated_at_utc must be timezone-aware")
    if validated_at_utc.utcoffset() != UTC.utcoffset(validated_at_utc):
        raise RestoreStagedArtifactValidationError("validated_at_utc must use UTC")
    if preflight.plan_id != plan.plan_id:
        raise RestoreStagedArtifactValidationError("preflight plan_id does not match restore plan")
    if preflight.readiness is not RestoreWorkspacePreflightReadiness.READY:
        raise RestoreStagedArtifactValidationError("workspace preflight must be ready")
    if materialization.plan_id != plan.plan_id:
        raise RestoreStagedArtifactValidationError(
            "materialization plan_id does not match restore plan"
        )
    if materialization.status is not RestoreWorkspaceMaterializationStatus.MATERIALIZED:
        raise RestoreStagedArtifactValidationError("workspace materialization must be successful")
    if staging.plan_id != plan.plan_id:
        raise RestoreStagedArtifactValidationError("staging plan_id does not match restore plan")
    if staging.status is not RestoreArtifactStagingStatus.STAGED:
        raise RestoreStagedArtifactValidationError("artifact staging must be successful")
    if staging.source_path != plan.source_artifact_path:
        raise RestoreStagedArtifactValidationError(
            "staging source path does not match restore plan"
        )
    if staging.staged_path != plan.staging_target_path:
        raise RestoreStagedArtifactValidationError(
            "staging target path does not match restore plan"
        )
    if staging.authoritative_target_modified:
        raise RestoreStagedArtifactValidationError(
            "staging evidence reports authoritative target modification"
        )


def _results_ok(results: tuple[str, ...]) -> bool:
    return bool(results) and all(result.strip().lower() == "ok" for result in results)
