"""Tests for controlled authoritative restore promotion."""

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

from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
    RestorePromotionReadinessStatus,
)
from poe_backup_orchestrator.services.restore.authoritative_promotion import (
    RestoreAuthoritativePromotionError,
    RestoreAuthoritativePromotionService,
)

NOW = datetime(2026, 7, 28, 16, 0, tzinfo=UTC)


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


def _plan(tmp_path: Path, *, target_exists: bool) -> SimpleNamespace:
    staged = tmp_path / "staging" / "registry.sqlite3"
    target = tmp_path / "authoritative" / "registry.sqlite3"
    rollback = tmp_path / "rollback" / "registry-before-restore.sqlite3"
    staged.parent.mkdir()
    target.parent.mkdir()
    rollback.parent.mkdir()
    staged.write_bytes(b"validated-staged-registry")
    if target_exists:
        target.write_bytes(b"prior-authoritative-registry")
        rollback.write_bytes(target.read_bytes())
    return SimpleNamespace(
        plan_id="plan-authoritative-promotion",
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


def _readiness(
    plan: SimpleNamespace,
    ownership: RestoreExecutionOwnership,
    *,
    target_exists: bool,
) -> SimpleNamespace:
    return SimpleNamespace(
        plan_id=plan.plan_id,
        evaluated_at_utc=NOW,
        status=RestorePromotionReadinessStatus.READY,
        ownership=ownership,
        staged_observation=_observation(plan.staging_target_path),
        authoritative_observation=(
            _observation(plan.authoritative_target_path) if target_exists else None
        ),
        rollback_observation=(_observation(plan.rollback_artifact_path) if target_exists else None),
        staged_artifact_modified=False,
        authoritative_target_modified=False,
        rollback_artifact_modified=False,
        promotion_performed=False,
    )


def test_promotes_over_existing_target_and_preserves_rollback(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=True)
    staged_digest = readiness.staged_observation.sha256
    rollback_bytes = plan.rollback_artifact_path.read_bytes()

    result = RestoreAuthoritativePromotionService(digest_chunk_size=4).execute(
        plan,
        readiness,
        executed_at_utc=NOW,
    )

    assert result.status.value == "promoted"
    assert not plan.staging_target_path.exists()
    assert hashlib.sha256(plan.authoritative_target_path.read_bytes()).hexdigest() == staged_digest
    assert plan.rollback_artifact_path.read_bytes() == rollback_bytes
    assert result.post_promotion_verification_required is True
    assert result.restore_completed is False


def test_promotes_when_authoritative_target_was_absent(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=False)

    result = RestoreAuthoritativePromotionService().execute(
        plan,
        readiness,
        executed_at_utc=NOW,
    )

    assert plan.authoritative_target_path.read_bytes() == b"validated-staged-registry"
    assert result.prior_authoritative_observation is None
    assert result.rollback_observation is None


def test_staged_drift_is_rejected_before_mutation(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=False)
    plan.staging_target_path.write_bytes(b"changed")

    with pytest.raises(
        RestoreAuthoritativePromotionError,
        match="staged artifact changed after readiness",
    ):
        RestoreAuthoritativePromotionService().execute(
            plan,
            readiness,
            executed_at_utc=NOW,
        )

    assert not plan.authoritative_target_path.exists()


def test_authoritative_drift_is_rejected_before_mutation(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=True)
    plan.authoritative_target_path.write_bytes(b"changed")

    with pytest.raises(
        RestoreAuthoritativePromotionError,
        match="authoritative target changed after readiness",
    ):
        RestoreAuthoritativePromotionService().execute(
            plan,
            readiness,
            executed_at_utc=NOW,
        )

    assert plan.staging_target_path.exists()


def test_rollback_drift_is_rejected_before_mutation(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=True)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=True)
    plan.rollback_artifact_path.write_bytes(b"changed")

    with pytest.raises(
        RestoreAuthoritativePromotionError,
        match="rollback artifact changed after readiness",
    ):
        RestoreAuthoritativePromotionService().execute(
            plan,
            readiness,
            executed_at_utc=NOW,
        )

    assert plan.staging_target_path.exists()


def test_modified_ownership_lock_is_rejected_before_mutation(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=False)
    ownership.lock_path.write_text('{"plan_id":"other"}\n', encoding="utf-8")

    with pytest.raises(
        RestoreAuthoritativePromotionError,
        match="ownership lock identity changed",
    ):
        RestoreAuthoritativePromotionService().execute(
            plan,
            readiness,
            executed_at_utc=NOW,
        )

    assert plan.staging_target_path.exists()
    assert not plan.authoritative_target_path.exists()


def test_replay_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path, target_exists=False)
    ownership = _ownership(tmp_path, plan.plan_id)
    readiness = _readiness(plan, ownership, target_exists=False)
    readiness.promotion_performed = True

    with pytest.raises(
        RestoreAuthoritativePromotionError,
        match="already been performed",
    ):
        RestoreAuthoritativePromotionService().execute(
            plan,
            readiness,
            executed_at_utc=NOW,
        )
