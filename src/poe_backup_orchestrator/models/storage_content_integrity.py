"""Immutable domain contracts for independently verifiable content integrity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.job import require_utc

STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION: Final[str] = "1.0"
_SHA256_HEX_LENGTH: Final[int] = 64


class ContentIntegrityOutcome(StrEnum):
    """Deterministic high-level integrity-verification outcome."""

    VERIFIED = "verified"
    SOURCE_CHANGED = "source_changed"
    SIZE_MISMATCH = "size_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    MISSING = "missing"
    INACCESSIBLE = "inaccessible"
    NOT_REGULAR_FILE = "not_regular_file"
    FILESYSTEM_ERROR = "filesystem_error"


class ContentIntegrityFailureCode(StrEnum):
    """Stable machine-readable failure classification."""

    SOURCE_CHANGED_DURING_VERIFICATION = "source_changed_during_verification"
    SOURCE_MISSING = "source_missing"
    PERMISSION_DENIED = "permission_denied"
    NOT_REGULAR_FILE = "not_regular_file"
    OBSERVED_SIZE_MISMATCH = "observed_size_mismatch"
    SHA256_MISMATCH = "sha256_mismatch"
    FILESYSTEM_ERROR = "filesystem_error"


@dataclass(frozen=True, slots=True)
class SourceFileObservation:
    """Portable filesystem evidence captured before or after hashing."""

    size_bytes: int
    modified_at_ns: int
    mode: int
    device_id: int | None = None
    inode: int | None = None

    def __post_init__(self) -> None:
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        if self.modified_at_ns < 0:
            raise ValueError("modified_at_ns must not be negative")
        if self.mode < 0:
            raise ValueError("mode must not be negative")
        if self.device_id is not None and self.device_id < 0:
            raise ValueError("device_id must not be negative")
        if self.inode is not None and self.inode < 0:
            raise ValueError("inode must not be negative")


@dataclass(frozen=True, slots=True)
class FileIntegrityEvidence:
    """Independent integrity evidence for one captured regular file."""

    schema_version: str
    item_id: str
    relative_path: Path
    expected_size_bytes: int
    observed_size_bytes: int | None
    expected_sha256: str
    observed_sha256: str | None
    verification_started_at_utc: datetime
    verification_completed_at_utc: datetime
    outcome: ContentIntegrityOutcome
    failure_code: ContentIntegrityFailureCode | None = None
    detail: str | None = None
    source_observation_before: SourceFileObservation | None = None
    source_observation_after: SourceFileObservation | None = None

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION:
            raise ValueError("schema_version must match the supported integrity schema")

        item_id = _normalize_identifier(self.item_id, "item_id")
        relative_path = Path(self.relative_path)
        if relative_path.is_absolute() or str(relative_path) in {"", "."}:
            raise ValueError("relative_path must identify an item below the source root")
        if self.expected_size_bytes < 0:
            raise ValueError("expected_size_bytes must not be negative")
        if self.observed_size_bytes is not None and self.observed_size_bytes < 0:
            raise ValueError("observed_size_bytes must not be negative")

        expected_sha256 = _normalize_sha256(self.expected_sha256, "expected_sha256")
        observed_sha256 = (
            None
            if self.observed_sha256 is None
            else _normalize_sha256(self.observed_sha256, "observed_sha256")
        )
        detail = None if self.detail is None else self.detail.strip()
        if detail == "":
            raise ValueError("detail must not be empty")

        require_utc(
            self.verification_started_at_utc,
            field_name="verification_started_at_utc",
        )
        require_utc(
            self.verification_completed_at_utc,
            field_name="verification_completed_at_utc",
        )
        if self.verification_completed_at_utc < self.verification_started_at_utc:
            raise ValueError(
                "verification_completed_at_utc must not precede verification_started_at_utc"
            )

        if self.outcome is ContentIntegrityOutcome.VERIFIED:
            if self.failure_code is not None or detail is not None:
                raise ValueError("verified evidence cannot contain failure evidence")
            if self.observed_size_bytes != self.expected_size_bytes:
                raise ValueError("verified evidence requires matching sizes")
            if observed_sha256 != expected_sha256:
                raise ValueError("verified evidence requires matching SHA-256")
            if self.source_observation_before is None or self.source_observation_after is None:
                raise ValueError("verified evidence requires before and after observations")
        else:
            if self.failure_code is None or detail is None:
                raise ValueError("failed evidence requires failure_code and detail")

        object.__setattr__(self, "item_id", item_id)
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "expected_sha256", expected_sha256)
        object.__setattr__(self, "observed_sha256", observed_sha256)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class ContentIntegrityTotals:
    """Deterministic reconciliation totals for integrity verification."""

    candidate_file_count: int
    verified_count: int
    source_changed_count: int
    size_mismatch_count: int
    digest_mismatch_count: int
    missing_count: int
    inaccessible_count: int
    not_regular_file_count: int
    filesystem_error_count: int
    total_expected_bytes: int
    total_observed_bytes: int

    def __post_init__(self) -> None:
        values = (
            self.candidate_file_count,
            self.verified_count,
            self.source_changed_count,
            self.size_mismatch_count,
            self.digest_mismatch_count,
            self.missing_count,
            self.inaccessible_count,
            self.not_regular_file_count,
            self.filesystem_error_count,
            self.total_expected_bytes,
            self.total_observed_bytes,
        )
        if any(value < 0 for value in values):
            raise ValueError("integrity totals must not be negative")
        classified = (
            self.verified_count
            + self.source_changed_count
            + self.size_mismatch_count
            + self.digest_mismatch_count
            + self.missing_count
            + self.inaccessible_count
            + self.not_regular_file_count
            + self.filesystem_error_count
        )
        if classified != self.candidate_file_count:
            raise ValueError("integrity outcome counts must reconcile candidates")

    @property
    def failed_count(self) -> int:
        """Return the total number of non-verified candidates."""

        return self.candidate_file_count - self.verified_count


@dataclass(frozen=True, slots=True)
class ContentIntegrityVerificationResult:
    """Ordered immutable result of an independent integrity pass."""

    schema_version: str
    source_root_id: str
    verification_started_at_utc: datetime
    verification_completed_at_utc: datetime
    evidence: tuple[FileIntegrityEvidence, ...]
    totals: ContentIntegrityTotals

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION:
            raise ValueError("schema_version must match the supported integrity schema")
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        require_utc(
            self.verification_started_at_utc,
            field_name="verification_started_at_utc",
        )
        require_utc(
            self.verification_completed_at_utc,
            field_name="verification_completed_at_utc",
        )
        if self.verification_completed_at_utc < self.verification_started_at_utc:
            raise ValueError(
                "verification_completed_at_utc must not precede verification_started_at_utc"
            )

        evidence = tuple(self.evidence)
        paths = [item.relative_path.as_posix() for item in evidence]
        item_ids = [item.item_id for item in evidence]
        if paths != sorted(paths):
            raise ValueError("integrity evidence must be ordered by relative path")
        if len(paths) != len(set(paths)):
            raise ValueError("integrity evidence must not contain duplicate paths")
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("integrity evidence must not contain duplicate item identifiers")
        if self.totals.candidate_file_count != len(evidence):
            raise ValueError("integrity totals must reconcile evidence count")

        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "evidence", evidence)


def _normalize_identifier(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


def _normalize_sha256(value: str, field_name: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != _SHA256_HEX_LENGTH or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{field_name} must contain exactly 64 hexadecimal characters")
    return normalized
