"""Immutable evidence for post-promotion verification and restore completion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
)

RESTORE_POST_PROMOTION_VERIFICATION_SCHEMA_VERSION = "1.0"


class RestorePostPromotionVerificationStatus(StrEnum):
    """Successful post-promotion verification status."""

    VERIFIED = "verified"


class RestorePostPromotionVerificationReasonCode(StrEnum):
    """Stable reason codes for successful restore completion."""

    PROMOTION_EVIDENCE_ACCEPTED = "promotion_evidence_accepted"
    EXECUTION_OWNERSHIP_REVALIDATED = "execution_ownership_revalidated"
    AUTHORITATIVE_ARTIFACT_VERIFIED = "authoritative_artifact_verified"
    STAGED_PATH_CONSUMPTION_VERIFIED = "staged_path_consumption_verified"
    ROLLBACK_ARTIFACT_PRESERVED = "rollback_artifact_preserved"
    POST_PROMOTION_VERIFICATION_COMPLETED = "post_promotion_verification_completed"
    RESTORE_COMPLETED = "restore_completed"


@dataclass(frozen=True, slots=True)
class RestorePostPromotionVerification:
    """Complete evidence for verified restore completion."""

    schema_version: str
    plan_id: str
    verified_at_utc: datetime
    status: RestorePostPromotionVerificationStatus
    reason_codes: tuple[RestorePostPromotionVerificationReasonCode, ...]
    promotion_executed_at_utc: datetime
    ownership: RestoreExecutionOwnership
    promoted_observation: RestorePromotionArtifactObservation
    verified_authoritative_observation: RestorePromotionArtifactObservation
    rollback_observation: RestorePromotionArtifactObservation | None
    authoritative_integrity_verified: bool
    staged_path_consumed: bool
    rollback_artifact_preserved: bool
    execution_ownership_continuous: bool
    post_promotion_verification_completed: bool
    restore_completed: bool

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        _require_utc(self.verified_at_utc, "verified_at_utc")
        _require_utc(self.promotion_executed_at_utc, "promotion_executed_at_utc")
        if self.status is not RestorePostPromotionVerificationStatus.VERIFIED:
            raise ValueError("post-promotion verification status must be verified")
        if not self.reason_codes:
            raise ValueError("reason_codes must not be empty")
        if self.ownership.plan_id != self.plan_id:
            raise ValueError("ownership plan_id must match verification plan_id")
        if self.promoted_observation.path != self.verified_authoritative_observation.path:
            raise ValueError("verified authoritative path must match promoted path")
        if (
            self.promoted_observation.size_bytes
            != self.verified_authoritative_observation.size_bytes
        ):
            raise ValueError("verified authoritative size must match promoted size")
        if self.promoted_observation.sha256 != self.verified_authoritative_observation.sha256:
            raise ValueError("verified authoritative SHA-256 must match promoted SHA-256")
        if not self.authoritative_integrity_verified:
            raise ValueError("authoritative integrity must be verified")
        if not self.staged_path_consumed:
            raise ValueError("staged path consumption must be verified")
        if not self.rollback_artifact_preserved:
            raise ValueError("rollback preservation must be verified")
        if not self.execution_ownership_continuous:
            raise ValueError("execution ownership continuity must be verified")
        if not self.post_promotion_verification_completed:
            raise ValueError("post-promotion verification must be complete")
        if not self.restore_completed:
            raise ValueError("successful verification must declare restore completion")


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must use UTC")
