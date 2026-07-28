"""Tests for post-promotion verification and restore completion."""

from __future__ import annotations

import hashlib
import json
import os
import socket
import stat
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from poe_backup_orchestrator.models.restore_authoritative_promotion import (
    RESTORE_AUTHORITATIVE_PROMOTION_SCHEMA_VERSION,
    RestoreAuthoritativePromotion,
    RestoreAuthoritativePromotionReasonCode,
    RestoreAuthoritativePromotionStatus,
)
from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
)
from poe_backup_orchestrator.services.restore.post_promotion_verification import (
    RestorePostPromotionVerificationError,
    RestorePostPromotionVerificationService,
)

NOW = datetime(2026, 7, 28, 17, 0, tzinfo=UTC)


def _observation(path: Path) -> RestorePromotionArtifactObservation:
    data = path.read_bytes()
    file_stat = path.stat()
    return RestorePromotionArtifactObservation(
        path=path,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        mode=stat.S_IMODE(file_stat.st_mode),
        modified_at_utc=datetime.fromtimestamp(file_stat.st_mtime, tz=UTC),
    )


def _plan(tmp_path: Path, *, rollback_exists: bool) -> SimpleNamespace:
    staged = tmp_path / "staging" / "registry.sqlite3"
    target = tmp_path / "authoritative" / "registry.sqlite3"
    rollback = tmp_path / "rollback" / "registry-before-restore.sqlite3"
    staged.parent.mkdir()
    target.parent.mkdir()
    rollback.parent.mkdir()
    target.write_bytes(b"promoted-registry")
    if rollback_exists:
        rollback.write_bytes(b"prior-registry")
    return SimpleNamespace(
        plan_id="plan-post-promotion",
        staging_target_path=staged,
        authoritative_target_path=target,
        rollback_artifact_path=rollback,
    )


def _ownership(tmp_path: Path, plan_id: str) -> RestoreExecutionOwnership:
    lock_path = tmp_path / "restore.lock"
    evidence = RestoreExecutionOwnership(
        lock_path=lock_path,
        plan_id=plan_id,
        owner_pid=os.getpid(),
        owner_hostname=socket.gethostname(),
        acquired_at_utc=NOW,
    )
    lock_path.write_text(
        json.dumps(
            {
                "plan_id": evidence.plan_id,
                "owner_pid": evidence.owner_pid,
                "owner_hostname": evidence.owner_hostname,
                "acquired_at_utc": evidence.acquired_at_utc.isoformat(),
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return evidence


def _promotion(
    plan: SimpleNamespace,
    ownership: RestoreExecutionOwnership,
    *,
    rollback_exists: bool,
) -> RestoreAuthoritativePromotion:
    promoted = _observation(plan.authoritative_target_path)
    rollback = _observation(plan.rollback_artifact_path) if rollback_exists else None
    staged = RestorePromotionArtifactObservation(
        path=plan.staging_target_path,
        size_bytes=promoted.size_bytes,
        sha256=promoted.sha256,
        mode=promoted.mode,
        modified_at_utc=promoted.modified_at_utc,
    )
    return RestoreAuthoritativePromotion(
        schema_version=RESTORE_AUTHORITATIVE_PROMOTION_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        executed_at_utc=NOW,
        status=RestoreAuthoritativePromotionStatus.PROMOTED,
        reason_codes=(
            RestoreAuthoritativePromotionReasonCode.READINESS_ACCEPTED,
            RestoreAuthoritativePromotionReasonCode.ATOMIC_PROMOTION_COMPLETED,
            RestoreAuthoritativePromotionReasonCode.POST_PROMOTION_VERIFICATION_REQUIRED,
        ),
        readiness_evaluated_at_utc=NOW,
        ownership=ownership,
        staged_observation=staged,
        prior_authoritative_observation=rollback,
        rollback_observation=rollback,
        promoted_observation=promoted,
        atomic_replace_used=True,
        promoted_file_fsynced=True,
        authoritative_parent_fsynced=True,
        staged_path_consumed=True,
        authoritative_target_modified=True,
        rollback_artifact_modified=False,
        post_promotion_verification_required=True,
        restore_completed=False,
    )


def test_verifies_restore_completion_with_rollback(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=True)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=True)

    result = RestorePostPromotionVerificationService(digest_chunk_size=4).verify(
        plan,
        promotion,
        verified_at_utc=NOW,
    )

    assert result.status.value == "verified"
    assert result.authoritative_integrity_verified is True
    assert result.rollback_artifact_preserved is True
    assert result.execution_ownership_continuous is True
    assert result.restore_completed is True


def test_verifies_restore_completion_without_rollback(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=False)

    result = RestorePostPromotionVerificationService().verify(
        plan,
        promotion,
        verified_at_utc=NOW,
    )

    assert result.rollback_observation is None
    assert result.restore_completed is True


def test_authoritative_drift_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=False)
    plan.authoritative_target_path.write_bytes(b"changed")

    with pytest.raises(
        RestorePostPromotionVerificationError,
        match="authoritative target changed after promotion",
    ):
        RestorePostPromotionVerificationService().verify(
            plan,
            promotion,
            verified_at_utc=NOW,
        )


def test_staged_path_reappearance_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=False)
    plan.staging_target_path.write_bytes(b"unexpected")

    with pytest.raises(
        RestorePostPromotionVerificationError,
        match="staged path reappeared",
    ):
        RestorePostPromotionVerificationService().verify(
            plan,
            promotion,
            verified_at_utc=NOW,
        )


def test_rollback_drift_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=True)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=True)
    plan.rollback_artifact_path.write_bytes(b"changed")

    with pytest.raises(
        RestorePostPromotionVerificationError,
        match="rollback artifact changed after promotion",
    ):
        RestorePostPromotionVerificationService().verify(
            plan,
            promotion,
            verified_at_utc=NOW,
        )


def test_unexpected_rollback_creation_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=False)
    plan.rollback_artifact_path.write_bytes(b"unexpected")

    with pytest.raises(
        RestorePostPromotionVerificationError,
        match="unexpected rollback artifact appeared",
    ):
        RestorePostPromotionVerificationService().verify(
            plan,
            promotion,
            verified_at_utc=NOW,
        )


def test_ownership_lock_replacement_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=False)
    ownership.lock_path.write_text('{"plan_id":"other"}\n', encoding="utf-8")

    with pytest.raises(
        RestorePostPromotionVerificationError,
        match="ownership lock identity changed",
    ):
        RestorePostPromotionVerificationService().verify(
            plan,
            promotion,
            verified_at_utc=NOW,
        )


def test_promotion_plan_mismatch_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, rollback_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    promotion = _promotion(plan, ownership, rollback_exists=False)
    plan.plan_id = "different-plan"

    with pytest.raises(
        RestorePostPromotionVerificationError,
        match="promotion plan_id does not match",
    ):
        RestorePostPromotionVerificationService().verify(
            plan,
            promotion,
            verified_at_utc=NOW,
        )
