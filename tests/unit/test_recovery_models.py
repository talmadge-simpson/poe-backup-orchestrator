"""Tests for governed Registry recovery-point domain models."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RecoveryPoint,
    RecoveryPointEligibility,
    RecoveryPointEligibilityResult,
    RecoveryPointReasonCode,
)

NOW = datetime(2026, 7, 27, 17, 0, tzinfo=UTC)


def eligibility(
    classification: RecoveryPointEligibility = RecoveryPointEligibility.ELIGIBLE,
    *,
    reason_codes: tuple[RecoveryPointReasonCode, ...] = (RecoveryPointReasonCode.PACKAGE_VALID,),
    warnings: tuple[str, ...] = (),
    override_required: bool = False,
) -> RecoveryPointEligibilityResult:
    return RecoveryPointEligibilityResult(
        classification=classification,
        reason_codes=reason_codes,
        warnings=warnings,
        override_required=override_required,
        evaluated_at_utc=NOW,
        policy_version="5A.1",
    )


def recovery_point(**overrides: object) -> RecoveryPoint:
    values: dict[str, object] = {
        "recovery_point_id": "rp-20260727T170000Z",
        "package_path": Path("/srv/poe-backup/Registry/package"),
        "artifact_path": Path("/srv/poe-backup/Registry/package/registry.sqlite3"),
        "manifest_path": Path("/srv/poe-backup/Registry/package/manifest.json"),
        "source_backup_execution_id": "backup-20260727T170000Z",
        "source_registry_id": "poeregistry",
        "created_at_utc": NOW,
        "artifact_size_bytes": 4096,
        "artifact_sha256": "A" * 64,
        "manifest_version": "1.0",
        "backup_status": "completed",
        "verification_status": "passed",
        "quarantined": False,
        "eligibility": eligibility(),
    }
    values.update(overrides)
    return RecoveryPoint(**values)  # type: ignore[arg-type]


def test_recovery_point_accepts_and_normalizes_valid_values() -> None:
    point = recovery_point(
        recovery_point_id="  rp-20260727T170000Z  ",
        source_registry_id="  poeregistry  ",
    )

    assert point.recovery_point_id == "rp-20260727T170000Z"
    assert point.source_registry_id == "poeregistry"
    assert point.artifact_sha256 == "a" * 64
    assert point.eligibility.classification is RecoveryPointEligibility.ELIGIBLE


@pytest.mark.parametrize("value", ["", "   ", "recovery point"])
def test_recovery_point_rejects_invalid_identity(value: str) -> None:
    with pytest.raises(ValueError, match="recovery_point_id"):
        recovery_point(recovery_point_id=value)


@pytest.mark.parametrize(
    "digest",
    [
        "",
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_recovery_point_rejects_invalid_sha256(digest: str) -> None:
    with pytest.raises(ValueError, match="64 hexadecimal"):
        recovery_point(artifact_sha256=digest)


def test_recovery_point_allows_incomplete_discovery_metadata() -> None:
    point = recovery_point(
        artifact_path=None,
        manifest_path=None,
        source_backup_execution_id=None,
        source_registry_id=None,
        created_at_utc=None,
        artifact_size_bytes=None,
        artifact_sha256=None,
        manifest_version=None,
        backup_status=None,
        verification_status=None,
        eligibility=eligibility(
            RecoveryPointEligibility.UNKNOWN,
            reason_codes=(RecoveryPointReasonCode.STATUS_UNDETERMINED,),
        ),
    )

    assert point.artifact_path is None
    assert point.eligibility.classification is RecoveryPointEligibility.UNKNOWN


def test_recovery_point_rejects_negative_artifact_size() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        recovery_point(artifact_size_bytes=-1)


def test_recovery_point_requires_utc_created_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        recovery_point(created_at_utc=datetime(2026, 7, 27, 17, 0))


def test_eligibility_normalizes_policy_and_warnings() -> None:
    result = RecoveryPointEligibilityResult(
        classification=RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE,
        reason_codes=(RecoveryPointReasonCode.RECOVERY_POINT_EXPIRED,),
        warnings=("  Recovery point exceeds normal age policy.  ",),
        override_required=True,
        evaluated_at_utc=NOW,
        policy_version="  5A.1  ",
    )

    assert result.policy_version == "5A.1"
    assert result.warnings == ("Recovery point exceeds normal age policy.",)


def test_eligibility_rejects_duplicate_reason_codes() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        eligibility(
            reason_codes=(
                RecoveryPointReasonCode.MANIFEST_INVALID,
                RecoveryPointReasonCode.MANIFEST_INVALID,
            )
        )


def test_eligible_result_cannot_require_override() -> None:
    with pytest.raises(ValueError, match="must not require an override"):
        eligibility(override_required=True)


def test_conditionally_eligible_result_requires_override() -> None:
    with pytest.raises(ValueError, match="must require an override"):
        eligibility(
            RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE,
            reason_codes=(RecoveryPointReasonCode.OPERATOR_REVIEW_REQUIRED,),
            override_required=False,
        )


def test_recovery_point_and_eligibility_are_immutable() -> None:
    point = recovery_point()

    with pytest.raises(FrozenInstanceError):
        point.recovery_point_id = "changed"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        point.eligibility.override_required = True  # type: ignore[misc]
