"""Immutable evidence for staged restore artifact integrity validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION = "1.0"


class RestoreStagedArtifactValidationStatus(StrEnum):
    """Outcome of staged artifact integrity validation."""

    VALID = "valid"


class RestoreStagedArtifactValidationReasonCode(StrEnum):
    """Stable reason codes emitted by successful validation."""

    BYTE_COUNTS_MATCH = "byte_counts_match"
    SHA256_MATCH = "sha256_match"
    SQLITE_QUICK_CHECK_OK = "sqlite_quick_check_ok"
    SQLITE_INTEGRITY_CHECK_OK = "sqlite_integrity_check_ok"
    STAGED_ARTIFACT_VALID = "staged_artifact_valid"


@dataclass(frozen=True, slots=True)
class RestoreStagedArtifactValidation:
    """Complete evidence for successful staged-artifact validation."""

    schema_version: str
    plan_id: str
    validated_at_utc: datetime
    status: RestoreStagedArtifactValidationStatus
    reason_codes: tuple[RestoreStagedArtifactValidationReasonCode, ...]
    source_path: Path
    staged_path: Path
    source_size_bytes: int
    staged_size_bytes: int
    source_sha256: str
    staged_sha256: str
    sqlite_opened_read_only: bool
    quick_check_results: tuple[str, ...]
    integrity_check_results: tuple[str, ...]
    authoritative_target_modified: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version or not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id or not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.validated_at_utc.tzinfo is None or self.validated_at_utc.utcoffset() is None:
            raise ValueError("validated_at_utc must be timezone-aware")
        if self.validated_at_utc.utcoffset() != UTC.utcoffset(self.validated_at_utc):
            raise ValueError("validated_at_utc must use UTC")
        if self.source_size_bytes < 0 or self.staged_size_bytes < 0:
            raise ValueError("artifact sizes must not be negative")
        if self.source_size_bytes != self.staged_size_bytes:
            raise ValueError("source and staged sizes must match")
        if self.source_path == self.staged_path:
            raise ValueError("source and staged paths must be distinct")
        _validate_sha256(self.source_sha256, "source_sha256")
        _validate_sha256(self.staged_sha256, "staged_sha256")
        if self.source_sha256 != self.staged_sha256:
            raise ValueError("source and staged SHA-256 digests must match")
        if not self.sqlite_opened_read_only:
            raise ValueError("SQLite must be opened read-only")
        if not _results_ok(self.quick_check_results):
            raise ValueError("quick_check_results must contain only ok")
        if not _results_ok(self.integrity_check_results):
            raise ValueError("integrity_check_results must contain only ok")
        if self.authoritative_target_modified:
            raise ValueError("Slice 5C-2 cannot modify the authoritative target")


def _validate_sha256(value: str, field_name: str) -> None:
    if len(value) != 64:
        raise ValueError(f"{field_name} must contain 64 hexadecimal characters")
    if value != value.lower():
        raise ValueError(f"{field_name} must use lowercase hexadecimal")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be hexadecimal") from exc


def _results_ok(results: tuple[str, ...]) -> bool:
    return bool(results) and all(result.strip().lower() == "ok" for result in results)
