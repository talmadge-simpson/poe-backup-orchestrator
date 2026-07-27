"""Policy-driven recovery-point eligibility evaluation."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.recovery import (
    RecoveryPoint,
    RecoveryPointEligibility,
    RecoveryPointEligibilityResult,
    RecoveryPointReasonCode,
)

DEFAULT_ELIGIBILITY_POLICY_VERSION: Final[str] = "5A.4"


def evaluate_recovery_point(
    recovery_point: RecoveryPoint,
    *,
    evaluated_at_utc: datetime,
    policy_version: str = DEFAULT_ELIGIBILITY_POLICY_VERSION,
) -> RecoveryPoint:
    """Return a recovery point with a deterministic eligibility decision."""

    _validate_evaluation_timestamp(evaluated_at_utc)

    unresolved_reasons = tuple(
        reason
        for reason in recovery_point.eligibility.reason_codes
        if reason is not RecoveryPointReasonCode.STATUS_UNDETERMINED
    )
    if unresolved_reasons:
        return replace(
            recovery_point,
            eligibility=_result(
                RecoveryPointEligibility.UNKNOWN,
                unresolved_reasons,
                recovery_point.eligibility.warnings,
                evaluated_at_utc=evaluated_at_utc,
                policy_version=policy_version,
            ),
        )

    if recovery_point.quarantined:
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.RECOVERY_POINT_QUARANTINED,
            "Recovery point is quarantined.",
            evaluated_at_utc,
            policy_version,
            override_required=True,
        )

    artifact_path = recovery_point.artifact_path
    if artifact_path is None:
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.ARTIFACT_PATH_MISSING,
            "Recovery point does not declare an artifact path.",
            evaluated_at_utc,
            policy_version,
        )

    artifact_path = Path(artifact_path)
    if not artifact_path.exists():
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.ARTIFACT_MISSING,
            f"Recovery artifact does not exist: {artifact_path}",
            evaluated_at_utc,
            policy_version,
        )

    if not artifact_path.is_file():
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.ARTIFACT_NOT_REGULAR_FILE,
            f"Recovery artifact is not a regular file: {artifact_path}",
            evaluated_at_utc,
            policy_version,
        )

    verification_status = (recovery_point.verification_status or "").strip().upper()
    if verification_status == "FAIL":
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.VERIFICATION_FAILED,
            "Source backup verification status is FAIL.",
            evaluated_at_utc,
            policy_version,
        )

    if verification_status != "PASS":
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.UNKNOWN,
            RecoveryPointReasonCode.VERIFICATION_STATUS_UNKNOWN,
            "Source backup verification status is not PASS or FAIL.",
            evaluated_at_utc,
            policy_version,
        )

    expected_size = recovery_point.artifact_size_bytes
    if expected_size is None:
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.UNKNOWN,
            RecoveryPointReasonCode.STATUS_UNDETERMINED,
            "Recovery artifact size is not declared.",
            evaluated_at_utc,
            policy_version,
        )

    actual_size = artifact_path.stat().st_size
    if actual_size != expected_size:
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.ARTIFACT_SIZE_MISMATCH,
            (
                "Recovery artifact size does not match the manifest: "
                f"expected {expected_size}, found {actual_size}."
            ),
            evaluated_at_utc,
            policy_version,
        )

    expected_sha256 = (recovery_point.artifact_sha256 or "").strip().lower()
    if not expected_sha256:
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.UNKNOWN,
            RecoveryPointReasonCode.STATUS_UNDETERMINED,
            "Recovery artifact checksum is not declared.",
            evaluated_at_utc,
            policy_version,
        )

    actual_sha256 = _sha256_file(artifact_path)
    if actual_sha256 != expected_sha256:
        return _with_result(
            recovery_point,
            RecoveryPointEligibility.INELIGIBLE,
            RecoveryPointReasonCode.ARTIFACT_CHECKSUM_MISMATCH,
            "Recovery artifact checksum does not match the manifest.",
            evaluated_at_utc,
            policy_version,
        )

    return _with_result(
        recovery_point,
        RecoveryPointEligibility.ELIGIBLE,
        RecoveryPointReasonCode.RECOVERY_POINT_ELIGIBLE,
        "Recovery point satisfies the current eligibility policy.",
        evaluated_at_utc,
        policy_version,
    )


def evaluate_recovery_points(
    recovery_points: tuple[RecoveryPoint, ...],
    *,
    evaluated_at_utc: datetime,
    policy_version: str = DEFAULT_ELIGIBILITY_POLICY_VERSION,
) -> tuple[RecoveryPoint, ...]:
    """Evaluate a collection while preserving the caller's deterministic order."""

    _validate_evaluation_timestamp(evaluated_at_utc)
    return tuple(
        evaluate_recovery_point(
            point,
            evaluated_at_utc=evaluated_at_utc,
            policy_version=policy_version,
        )
        for point in recovery_points
    )


def _with_result(
    recovery_point: RecoveryPoint,
    classification: RecoveryPointEligibility,
    reason_code: RecoveryPointReasonCode,
    warning: str,
    evaluated_at_utc: datetime,
    policy_version: str,
    *,
    override_required: bool = False,
) -> RecoveryPoint:
    return replace(
        recovery_point,
        eligibility=_result(
            classification,
            (reason_code,),
            (warning,),
            evaluated_at_utc=evaluated_at_utc,
            policy_version=policy_version,
            override_required=override_required,
        ),
    )


def _result(
    classification: RecoveryPointEligibility,
    reason_codes: tuple[RecoveryPointReasonCode, ...],
    warnings: tuple[str, ...],
    *,
    evaluated_at_utc: datetime,
    policy_version: str,
    override_required: bool = False,
) -> RecoveryPointEligibilityResult:
    return RecoveryPointEligibilityResult(
        classification=classification,
        reason_codes=reason_codes,
        warnings=warnings,
        override_required=override_required,
        evaluated_at_utc=evaluated_at_utc,
        policy_version=policy_version,
    )


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_evaluation_timestamp(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("evaluated_at_utc must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError("evaluated_at_utc must use UTC")
