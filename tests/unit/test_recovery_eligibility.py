"""Tests for recovery-point eligibility policy evaluation."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RecoveryPoint,
    RecoveryPointEligibility,
    RecoveryPointEligibilityResult,
    RecoveryPointReasonCode,
)
from poe_backup_orchestrator.services.restore import (
    evaluate_recovery_point,
    evaluate_recovery_points,
)

EVALUATED_AT = datetime(2026, 7, 27, 19, 0, tzinfo=UTC)


def point_for(
    artifact_path: Path | None,
    *,
    content: bytes = b"registry snapshot",
    verification_status: str | None = "PASS",
    quarantined: bool = False,
) -> RecoveryPoint:
    digest = hashlib.sha256(content).hexdigest()
    return RecoveryPoint(
        recovery_point_id="rp-1",
        package_path=Path("/repository/rp-1"),
        artifact_path=artifact_path,
        manifest_path=Path("/repository/rp-1/manifest.json"),
        source_backup_execution_id="backup-1",
        source_registry_id="poe-registry",
        created_at_utc=datetime(2026, 7, 27, 18, 0, tzinfo=UTC),
        artifact_size_bytes=len(content),
        artifact_sha256=digest,
        manifest_version="1.0",
        backup_status=None,
        verification_status=verification_status,
        quarantined=quarantined,
        eligibility=RecoveryPointEligibilityResult(
            classification=RecoveryPointEligibility.UNKNOWN,
            reason_codes=(RecoveryPointReasonCode.STATUS_UNDETERMINED,),
            warnings=("Not evaluated.",),
            override_required=False,
            evaluated_at_utc=datetime(2026, 7, 27, 18, 0, tzinfo=UTC),
            policy_version="5A.3-discovery",
        ),
    )


def write_artifact(tmp_path: Path, content: bytes = b"registry snapshot") -> Path:
    path = tmp_path / "poe-registry.sqlite3"
    path.write_bytes(content)
    return path


def test_valid_recovery_point_is_eligible(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)

    evaluated = evaluate_recovery_point(
        point_for(artifact),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.ELIGIBLE
    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.RECOVERY_POINT_ELIGIBLE,)
    assert evaluated.eligibility.override_required is False
    assert evaluated.eligibility.evaluated_at_utc == EVALUATED_AT


def test_evaluation_does_not_mutate_original_point(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)
    original = point_for(artifact)

    evaluated = evaluate_recovery_point(
        original,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert original.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert evaluated is not original


def test_manifest_discovery_fault_remains_unknown() -> None:
    original = point_for(None)
    original = replace(
        original,
        eligibility=replace(
            original.eligibility,
            reason_codes=(RecoveryPointReasonCode.MANIFEST_MISSING,),
            warnings=("Manifest missing.",),
        ),
    )

    evaluated = evaluate_recovery_point(
        original,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.MANIFEST_MISSING,)


def test_quarantined_recovery_point_is_ineligible(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)

    evaluated = evaluate_recovery_point(
        point_for(artifact, quarantined=True),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.INELIGIBLE
    assert evaluated.eligibility.reason_codes == (
        RecoveryPointReasonCode.RECOVERY_POINT_QUARANTINED,
    )
    assert evaluated.eligibility.override_required is True


def test_missing_artifact_path_is_ineligible() -> None:
    evaluated = evaluate_recovery_point(
        point_for(None),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.ARTIFACT_PATH_MISSING,)


def test_missing_artifact_is_ineligible(tmp_path: Path) -> None:
    evaluated = evaluate_recovery_point(
        point_for(tmp_path / "missing.sqlite3"),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.INELIGIBLE
    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.ARTIFACT_MISSING,)


def test_directory_artifact_is_ineligible(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact"
    artifact.mkdir()

    evaluated = evaluate_recovery_point(
        point_for(artifact),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.reason_codes == (
        RecoveryPointReasonCode.ARTIFACT_NOT_REGULAR_FILE,
    )


def test_failed_source_verification_is_ineligible(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)

    evaluated = evaluate_recovery_point(
        point_for(artifact, verification_status="FAIL"),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.VERIFICATION_FAILED,)


@pytest.mark.parametrize("status", [None, "UNKNOWN", "PENDING"])
def test_unknown_source_verification_remains_unknown(
    tmp_path: Path,
    status: str | None,
) -> None:
    artifact = write_artifact(tmp_path)

    evaluated = evaluate_recovery_point(
        point_for(artifact, verification_status=status),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert evaluated.eligibility.reason_codes == (
        RecoveryPointReasonCode.VERIFICATION_STATUS_UNKNOWN,
    )


def test_artifact_size_mismatch_is_ineligible(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)
    original = replace(point_for(artifact), artifact_size_bytes=999)

    evaluated = evaluate_recovery_point(
        original,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.ARTIFACT_SIZE_MISMATCH,)


def test_missing_declared_size_remains_unknown(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)
    original = replace(point_for(artifact), artifact_size_bytes=None)

    evaluated = evaluate_recovery_point(
        original,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.UNKNOWN
    assert evaluated.eligibility.reason_codes == (RecoveryPointReasonCode.STATUS_UNDETERMINED,)


def test_artifact_checksum_mismatch_is_ineligible(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)
    original = replace(point_for(artifact), artifact_sha256="b" * 64)

    evaluated = evaluate_recovery_point(
        original,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.reason_codes == (
        RecoveryPointReasonCode.ARTIFACT_CHECKSUM_MISMATCH,
    )


def test_missing_declared_checksum_remains_unknown(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)
    original = replace(point_for(artifact), artifact_sha256=None)

    evaluated = evaluate_recovery_point(
        original,
        evaluated_at_utc=EVALUATED_AT,
    )

    assert evaluated.eligibility.classification is RecoveryPointEligibility.UNKNOWN


def test_batch_evaluation_preserves_order(tmp_path: Path) -> None:
    first_artifact = tmp_path / "first.sqlite3"
    second_artifact = tmp_path / "second.sqlite3"
    first_artifact.write_bytes(b"registry snapshot")
    second_artifact.write_bytes(b"registry snapshot")

    first = point_for(first_artifact)
    second = replace(
        point_for(second_artifact),
        recovery_point_id="rp-2",
    )

    evaluated = evaluate_recovery_points(
        (second, first),
        evaluated_at_utc=EVALUATED_AT,
    )

    assert tuple(point.recovery_point_id for point in evaluated) == ("rp-2", "rp-1")


def test_policy_version_is_recorded(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)

    evaluated = evaluate_recovery_point(
        point_for(artifact),
        evaluated_at_utc=EVALUATED_AT,
        policy_version="test-policy",
    )

    assert evaluated.eligibility.policy_version == "test-policy"


def test_naive_evaluation_timestamp_is_rejected(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)

    with pytest.raises(ValueError, match="timezone-aware"):
        evaluate_recovery_point(
            point_for(artifact),
            evaluated_at_utc=datetime(2026, 7, 27, 19, 0),
        )


def test_non_utc_evaluation_timestamp_is_rejected(tmp_path: Path) -> None:
    artifact = write_artifact(tmp_path)
    eastern = timezone(-timedelta(hours=4))

    with pytest.raises(ValueError, match="must use UTC"):
        evaluate_recovery_point(
            point_for(artifact),
            evaluated_at_utc=datetime(2026, 7, 27, 15, 0, tzinfo=eastern),
        )
