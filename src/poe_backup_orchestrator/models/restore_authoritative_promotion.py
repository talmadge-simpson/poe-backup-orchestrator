"""Immutable evidence for controlled authoritative restore promotion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from poe_backup_orchestrator.models.restore_promotion_readiness import (
    RestoreExecutionOwnership,
    RestorePromotionArtifactObservation,
)

RESTORE_AUTHORITATIVE_PROMOTION_SCHEMA_VERSION = "1.0"


class RestoreAuthoritativePromotionStatus(StrEnum):
    """Successful controlled-promotion status."""

    PROMOTED = "promoted"


class RestoreAuthoritativePromotionReasonCode(StrEnum):
    """Stable reason codes emitted by successful controlled promotion."""

    READINESS_ACCEPTED = "readiness_accepted"
    EXECUTION_OWNERSHIP_REVALIDATED = "execution_ownership_revalidated"
    STAGED_ARTIFACT_REVALIDATED = "staged_artifact_revalidated"
    AUTHORITATIVE_BOUNDARY_REVALIDATED = "authoritative_boundary_revalidated"
    ROLLBACK_ARTIFACT_PRESERVED = "rollback_artifact_preserved"
    ATOMIC_PROMOTION_COMPLETED = "atomic_promotion_completed"
    DURABILITY_SYNC_COMPLETED = "durability_sync_completed"
    POST_PROMOTION_VERIFICATION_REQUIRED = "post_promotion_verification_required"


@dataclass(frozen=True, slots=True)
class RestoreAuthoritativePromotion:
    """Complete evidence for one controlled authoritative promotion."""

    schema_version: str
    plan_id: str
    executed_at_utc: datetime
    status: RestoreAuthoritativePromotionStatus
    reason_codes: tuple[RestoreAuthoritativePromotionReasonCode, ...]
    readiness_evaluated_at_utc: datetime
    ownership: RestoreExecutionOwnership
    staged_observation: RestorePromotionArtifactObservation
    prior_authoritative_observation: RestorePromotionArtifactObservation | None
    rollback_observation: RestorePromotionArtifactObservation | None
    promoted_observation: RestorePromotionArtifactObservation
    atomic_replace_used: bool
    promoted_file_fsynced: bool
    authoritative_parent_fsynced: bool
    staged_path_consumed: bool
    authoritative_target_modified: bool
    rollback_artifact_modified: bool
    post_promotion_verification_required: bool
    restore_completed: bool

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        _require_utc(self.executed_at_utc, "executed_at_utc")
        _require_utc(self.readiness_evaluated_at_utc, "readiness_evaluated_at_utc")
        if self.status is not RestoreAuthoritativePromotionStatus.PROMOTED:
            raise ValueError("authoritative promotion status must be promoted")
        if not self.reason_codes:
            raise ValueError("reason_codes must not be empty")
        if self.ownership.plan_id != self.plan_id:
            raise ValueError("ownership plan_id must match promotion plan_id")
        if self.staged_observation.path == self.promoted_observation.path:
            raise ValueError("staged and promoted observations must use distinct paths")
        if self.staged_observation.size_bytes != self.promoted_observation.size_bytes:
            raise ValueError("promoted size must match staged size")
        if self.staged_observation.sha256 != self.promoted_observation.sha256:
            raise ValueError("promoted SHA-256 must match staged SHA-256")
        if not self.atomic_replace_used:
            raise ValueError("controlled promotion must use atomic replacement")
        if not self.promoted_file_fsynced:
            raise ValueError("promoted file must be fsynced")
        if not self.authoritative_parent_fsynced:
            raise ValueError("authoritative parent must be fsynced")
        if not self.staged_path_consumed:
            raise ValueError("staged path must be consumed")
        if not self.authoritative_target_modified:
            raise ValueError("authoritative target must be marked modified")
        if self.rollback_artifact_modified:
            raise ValueError("rollback artifact must remain unmodified")
        if not self.post_promotion_verification_required:
            raise ValueError("post-promotion verification must remain required")
        if self.restore_completed:
            raise ValueError("Slice 5D-4 cannot declare restore completion")


def _require_utc(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must use UTC")
