"""Governed Registry recovery-point domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.job import require_utc

_SHA256_HEX_LENGTH: Final[int] = 64


class RecoveryPointEligibility(StrEnum):
    """Policy classification assigned to one discovered recovery point."""

    ELIGIBLE = "eligible"
    CONDITIONALLY_ELIGIBLE = "conditionally_eligible"
    INELIGIBLE = "ineligible"
    UNKNOWN = "unknown"


class RecoveryPointReasonCode(StrEnum):
    """Stable policy and inspection reason codes for recovery-point decisions."""

    PACKAGE_VALID = "package_valid"
    MANIFEST_MISSING = "manifest_missing"
    MANIFEST_UNREADABLE = "manifest_unreadable"
    MANIFEST_INVALID = "manifest_invalid"
    MANIFEST_VERSION_UNSUPPORTED = "manifest_version_unsupported"
    ARTIFACT_MISSING = "artifact_missing"
    BACKUP_INCOMPLETE = "backup_incomplete"
    BACKUP_FAILED = "backup_failed"
    CHECKSUM_MISSING = "checksum_missing"
    CHECKSUM_INVALID = "checksum_invalid"
    VERIFICATION_INCOMPLETE = "verification_incomplete"
    VERIFICATION_FAILED = "verification_failed"
    SOURCE_IDENTITY_MISSING = "source_identity_missing"
    SOURCE_IDENTITY_CONFLICT = "source_identity_conflict"
    PACKAGE_QUARANTINED = "package_quarantined"
    DUPLICATE_IDENTITY = "duplicate_identity"
    PACKAGE_MUTATED = "package_mutated"
    RECOVERY_POINT_EXPIRED = "recovery_point_expired"
    OPERATOR_REVIEW_REQUIRED = "operator_review_required"
    STATUS_UNDETERMINED = "status_undetermined"

    RECOVERY_POINT_ELIGIBLE = "recovery_point_eligible"
    ARTIFACT_PATH_MISSING = "artifact_path_missing"
    ARTIFACT_NOT_REGULAR_FILE = "artifact_not_regular_file"
    ARTIFACT_SIZE_MISMATCH = "artifact_size_mismatch"
    ARTIFACT_CHECKSUM_MISMATCH = "artifact_checksum_mismatch"
    VERIFICATION_STATUS_UNKNOWN = "verification_status_unknown"
    RECOVERY_POINT_QUARANTINED = "recovery_point_quarantined"


@dataclass(frozen=True, slots=True)
class RecoveryPointEligibilityResult:
    """Immutable policy result for one recovery point."""

    classification: RecoveryPointEligibility
    reason_codes: tuple[RecoveryPointReasonCode, ...]
    warnings: tuple[str, ...]
    override_required: bool
    evaluated_at_utc: datetime
    policy_version: str

    def __post_init__(self) -> None:
        require_utc(self.evaluated_at_utc, field_name="evaluated_at_utc")

        policy_version = self.policy_version.strip()
        warnings = tuple(item.strip() for item in self.warnings)
        if not policy_version:
            raise ValueError("policy_version must not be empty")
        if any(not warning for warning in warnings):
            raise ValueError("warnings must not contain empty values")

        reason_codes = tuple(self.reason_codes)
        if len(set(reason_codes)) != len(reason_codes):
            raise ValueError("reason_codes must not contain duplicates")

        if self.classification is RecoveryPointEligibility.ELIGIBLE and self.override_required:
            raise ValueError("eligible recovery points must not require an override")

        if (
            self.classification is RecoveryPointEligibility.CONDITIONALLY_ELIGIBLE
            and not self.override_required
        ):
            raise ValueError("conditionally eligible recovery points must require an override")

        object.__setattr__(self, "policy_version", policy_version)
        object.__setattr__(self, "reason_codes", reason_codes)
        object.__setattr__(self, "warnings", warnings)


@dataclass(frozen=True, slots=True)
class RecoveryPoint:
    """Identified governed backup package considered as a recovery source."""

    recovery_point_id: str
    package_path: Path
    artifact_path: Path | None
    manifest_path: Path | None
    source_backup_execution_id: str | None
    source_registry_id: str | None
    created_at_utc: datetime | None
    artifact_size_bytes: int | None
    artifact_sha256: str | None
    manifest_version: str | None
    backup_status: str | None
    verification_status: str | None
    quarantined: bool
    eligibility: RecoveryPointEligibilityResult

    def __post_init__(self) -> None:
        recovery_point_id = self.recovery_point_id.strip()
        if not recovery_point_id:
            raise ValueError("recovery_point_id must not be empty")
        if any(character.isspace() for character in recovery_point_id):
            raise ValueError("recovery_point_id must not contain whitespace")

        if self.created_at_utc is not None:
            require_utc(self.created_at_utc, field_name="created_at_utc")

        if self.artifact_size_bytes is not None and self.artifact_size_bytes < 0:
            raise ValueError("artifact_size_bytes must not be negative")

        artifact_sha256 = _normalize_optional_sha256(self.artifact_sha256)
        source_backup_execution_id = _normalize_optional_text(
            self.source_backup_execution_id,
            field_name="source_backup_execution_id",
        )
        source_registry_id = _normalize_optional_text(
            self.source_registry_id,
            field_name="source_registry_id",
        )
        manifest_version = _normalize_optional_text(
            self.manifest_version,
            field_name="manifest_version",
        )
        backup_status = _normalize_optional_text(
            self.backup_status,
            field_name="backup_status",
        )
        verification_status = _normalize_optional_text(
            self.verification_status,
            field_name="verification_status",
        )

        object.__setattr__(self, "recovery_point_id", recovery_point_id)
        object.__setattr__(self, "package_path", Path(self.package_path))
        object.__setattr__(
            self,
            "artifact_path",
            None if self.artifact_path is None else Path(self.artifact_path),
        )
        object.__setattr__(
            self,
            "manifest_path",
            None if self.manifest_path is None else Path(self.manifest_path),
        )
        object.__setattr__(
            self,
            "source_backup_execution_id",
            source_backup_execution_id,
        )
        object.__setattr__(self, "source_registry_id", source_registry_id)
        object.__setattr__(self, "artifact_sha256", artifact_sha256)
        object.__setattr__(self, "manifest_version", manifest_version)
        object.__setattr__(self, "backup_status", backup_status)
        object.__setattr__(self, "verification_status", verification_status)


def _normalize_optional_text(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty when provided")
    return normalized


def _normalize_optional_sha256(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if len(normalized) != _SHA256_HEX_LENGTH or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError("artifact_sha256 must contain exactly 64 hexadecimal characters")
    return normalized
