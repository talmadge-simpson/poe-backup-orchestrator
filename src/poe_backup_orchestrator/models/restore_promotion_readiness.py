"""Domain contracts for restore execution ownership and promotion readiness."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_PROMOTION_READINESS_SCHEMA_VERSION = "1.0"


class RestorePromotionReadinessStatus(StrEnum):
    """Promotion readiness outcome."""

    READY = "ready"


class RestorePromotionReadinessReasonCode(StrEnum):
    """Stable successful readiness reason codes."""

    EXECUTION_OWNERSHIP_ACQUIRED = "execution_ownership_acquired"
    EVIDENCE_CHAIN_ACCEPTED = "evidence_chain_accepted"
    GOVERNED_PATHS_DISTINCT = "governed_paths_distinct"
    STAGED_ARTIFACT_REVALIDATED = "staged_artifact_revalidated"
    AUTHORITATIVE_TARGET_REVALIDATED = "authoritative_target_revalidated"
    ROLLBACK_ARTIFACT_REVALIDATED = "rollback_artifact_revalidated"
    PROMOTION_READY = "promotion_ready"


@dataclass(frozen=True, slots=True)
class RestoreExecutionOwnership:
    """Immutable ownership evidence for one restore execution."""

    lock_path: Path
    plan_id: str
    owner_pid: int
    owner_hostname: str
    acquired_at_utc: datetime

    def __post_init__(self) -> None:
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.owner_pid <= 0:
            raise ValueError("owner_pid must be positive")
        if not self.owner_hostname.strip():
            raise ValueError("owner_hostname must not be empty")
        if self.acquired_at_utc.tzinfo is None or self.acquired_at_utc.utcoffset() is None:
            raise ValueError("acquired_at_utc must be timezone-aware")
        if self.acquired_at_utc.utcoffset() != UTC.utcoffset(self.acquired_at_utc):
            raise ValueError("acquired_at_utc must use UTC")


@dataclass(frozen=True, slots=True)
class RestorePromotionArtifactObservation:
    """Immutable observation of a governed promotion artifact."""

    path: Path
    size_bytes: int
    sha256: str
    mode: int
    modified_at_utc: datetime

    def __post_init__(self) -> None:
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        if len(self.sha256) != 64:
            raise ValueError("sha256 must contain 64 hexadecimal characters")
        try:
            int(self.sha256, 16)
        except ValueError as exc:
            raise ValueError("sha256 must be hexadecimal") from exc
        if self.modified_at_utc.tzinfo is None or self.modified_at_utc.utcoffset() is None:
            raise ValueError("modified_at_utc must be timezone-aware")
        if self.modified_at_utc.utcoffset() != UTC.utcoffset(self.modified_at_utc):
            raise ValueError("modified_at_utc must use UTC")


@dataclass(frozen=True, slots=True)
class RestorePromotionReadiness:
    """Immutable successful promotion readiness evidence."""

    schema_version: str
    plan_id: str
    evaluated_at_utc: datetime
    status: RestorePromotionReadinessStatus
    reason_codes: tuple[RestorePromotionReadinessReasonCode, ...]
    ownership: RestoreExecutionOwnership
    staged_observation: RestorePromotionArtifactObservation
    authoritative_observation: RestorePromotionArtifactObservation | None
    rollback_observation: RestorePromotionArtifactObservation | None
    staged_artifact_modified: bool = False
    authoritative_target_modified: bool = False
    rollback_artifact_modified: bool = False
    promotion_performed: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.evaluated_at_utc.tzinfo is None or self.evaluated_at_utc.utcoffset() is None:
            raise ValueError("evaluated_at_utc must be timezone-aware")
        if self.evaluated_at_utc.utcoffset() != UTC.utcoffset(self.evaluated_at_utc):
            raise ValueError("evaluated_at_utc must use UTC")
        if self.ownership.plan_id != self.plan_id:
            raise ValueError("ownership plan_id must match readiness plan_id")
        if self.staged_artifact_modified:
            raise ValueError("readiness cannot modify staged artifact")
        if self.authoritative_target_modified:
            raise ValueError("readiness cannot modify authoritative target")
        if self.rollback_artifact_modified:
            raise ValueError("readiness cannot modify rollback artifact")
        if self.promotion_performed:
            raise ValueError("readiness cannot perform promotion")
