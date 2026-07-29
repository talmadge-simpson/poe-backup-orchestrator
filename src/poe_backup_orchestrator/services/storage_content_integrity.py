"""Independent streaming verification of captured source-content evidence."""

from __future__ import annotations

import hashlib
import stat
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.storage_content_capture import (
    FileContentCertification,
    InventoryContentCaptureResult,
)
from poe_backup_orchestrator.models.storage_content_integrity import (
    STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
    ContentIntegrityFailureCode,
    ContentIntegrityOutcome,
    ContentIntegrityTotals,
    ContentIntegrityVerificationResult,
    FileIntegrityEvidence,
    SourceFileObservation,
)

Clock = Callable[[], datetime]


class ContentIntegrityVerificationError(RuntimeError):
    """Raised when integrity-verification input violates the service contract."""


@dataclass(frozen=True, slots=True)
class ContentIntegrityVerificationPolicy:
    """Bounded streaming policy for independent content verification."""

    chunk_size_bytes: int = 1024 * 1024

    def __post_init__(self) -> None:
        if self.chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be positive")


class ContentIntegrityVerifier:
    """Re-read captured files and produce independently verifiable evidence."""

    def __init__(
        self,
        *,
        policy: ContentIntegrityVerificationPolicy | None = None,
        clock: Clock | None = None,
    ) -> None:
        self._policy = policy or ContentIntegrityVerificationPolicy()
        self._clock = clock or _utc_now

    def verify(
        self,
        *,
        root_path: Path,
        capture_result: InventoryContentCaptureResult,
    ) -> ContentIntegrityVerificationResult:
        root = Path(root_path)
        if not root.is_absolute():
            raise ContentIntegrityVerificationError("root_path must be absolute")
        if root != capture_result.root_path:
            raise ContentIntegrityVerificationError("root_path must match the captured source root")

        certifications = tuple(
            sorted(
                capture_result.certifications,
                key=lambda item: item.relative_path.as_posix(),
            )
        )
        if len({item.item_id for item in certifications}) != len(certifications):
            raise ContentIntegrityVerificationError(
                "capture certifications contain duplicate item identifiers"
            )
        if len({item.relative_path for item in certifications}) != len(certifications):
            raise ContentIntegrityVerificationError(
                "capture certifications contain duplicate relative paths"
            )

        verification_started_at_utc = self._clock()
        evidence = tuple(
            self._verify_one(root=root, certification=certification)
            for certification in certifications
        )
        verification_completed_at_utc = self._clock()

        return ContentIntegrityVerificationResult(
            schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
            source_root_id=capture_result.source_root_id,
            verification_started_at_utc=verification_started_at_utc,
            verification_completed_at_utc=verification_completed_at_utc,
            evidence=evidence,
            totals=_build_totals(evidence),
        )

    def _verify_one(
        self,
        *,
        root: Path,
        certification: FileContentCertification,
    ) -> FileIntegrityEvidence:
        path = root / certification.relative_path
        started_at_utc = self._clock()
        before: SourceFileObservation | None = None
        after: SourceFileObservation | None = None
        observed_size: int | None = None
        observed_sha256: str | None = None

        try:
            before_stat = path.lstat()
            before = _observation(before_stat)
            if not stat.S_ISREG(before_stat.st_mode):
                return self._failure(
                    certification=certification,
                    started_at_utc=started_at_utc,
                    outcome=ContentIntegrityOutcome.NOT_REGULAR_FILE,
                    failure_code=ContentIntegrityFailureCode.NOT_REGULAR_FILE,
                    detail="source path is not a regular file",
                    before=before,
                )

            observed_sha256, observed_size = _stream_sha256(
                path=path,
                chunk_size_bytes=self._policy.chunk_size_bytes,
            )
            after_stat = path.lstat()
            after = _observation(after_stat)

            if not stat.S_ISREG(after_stat.st_mode) or _source_changed(before, after):
                return self._failure(
                    certification=certification,
                    started_at_utc=started_at_utc,
                    outcome=ContentIntegrityOutcome.SOURCE_CHANGED,
                    failure_code=(ContentIntegrityFailureCode.SOURCE_CHANGED_DURING_VERIFICATION),
                    detail="source metadata changed during integrity verification",
                    observed_size=observed_size,
                    observed_sha256=observed_sha256,
                    before=before,
                    after=after,
                )
            if observed_size != certification.expected_byte_count:
                return self._failure(
                    certification=certification,
                    started_at_utc=started_at_utc,
                    outcome=ContentIntegrityOutcome.SIZE_MISMATCH,
                    failure_code=ContentIntegrityFailureCode.OBSERVED_SIZE_MISMATCH,
                    detail=(
                        f"expected {certification.expected_byte_count} bytes; "
                        f"observed {observed_size}"
                    ),
                    observed_size=observed_size,
                    observed_sha256=observed_sha256,
                    before=before,
                    after=after,
                )
            if observed_sha256 != certification.sha256:
                return self._failure(
                    certification=certification,
                    started_at_utc=started_at_utc,
                    outcome=ContentIntegrityOutcome.DIGEST_MISMATCH,
                    failure_code=ContentIntegrityFailureCode.SHA256_MISMATCH,
                    detail="observed SHA-256 does not match capture certification",
                    observed_size=observed_size,
                    observed_sha256=observed_sha256,
                    before=before,
                    after=after,
                )

            return FileIntegrityEvidence(
                schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
                item_id=certification.item_id,
                relative_path=certification.relative_path,
                expected_size_bytes=certification.expected_byte_count,
                observed_size_bytes=observed_size,
                expected_sha256=certification.sha256,
                observed_sha256=observed_sha256,
                verification_started_at_utc=started_at_utc,
                verification_completed_at_utc=self._clock(),
                outcome=ContentIntegrityOutcome.VERIFIED,
                source_observation_before=before,
                source_observation_after=after,
            )
        except FileNotFoundError:
            return self._failure(
                certification=certification,
                started_at_utc=started_at_utc,
                outcome=ContentIntegrityOutcome.MISSING,
                failure_code=ContentIntegrityFailureCode.SOURCE_MISSING,
                detail="source file was not found",
                observed_size=observed_size,
                observed_sha256=observed_sha256,
                before=before,
                after=after,
            )
        except PermissionError:
            return self._failure(
                certification=certification,
                started_at_utc=started_at_utc,
                outcome=ContentIntegrityOutcome.INACCESSIBLE,
                failure_code=ContentIntegrityFailureCode.PERMISSION_DENIED,
                detail="permission denied while verifying source file",
                observed_size=observed_size,
                observed_sha256=observed_sha256,
                before=before,
                after=after,
            )
        except OSError as error:
            return self._failure(
                certification=certification,
                started_at_utc=started_at_utc,
                outcome=ContentIntegrityOutcome.FILESYSTEM_ERROR,
                failure_code=ContentIntegrityFailureCode.FILESYSTEM_ERROR,
                detail=f"{type(error).__name__}: {error}",
                observed_size=observed_size,
                observed_sha256=observed_sha256,
                before=before,
                after=after,
            )

    def _failure(
        self,
        *,
        certification: FileContentCertification,
        started_at_utc: datetime,
        outcome: ContentIntegrityOutcome,
        failure_code: ContentIntegrityFailureCode,
        detail: str,
        observed_size: int | None = None,
        observed_sha256: str | None = None,
        before: SourceFileObservation | None = None,
        after: SourceFileObservation | None = None,
    ) -> FileIntegrityEvidence:
        return FileIntegrityEvidence(
            schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
            item_id=certification.item_id,
            relative_path=certification.relative_path,
            expected_size_bytes=certification.expected_byte_count,
            observed_size_bytes=observed_size,
            expected_sha256=certification.sha256,
            observed_sha256=observed_sha256,
            verification_started_at_utc=started_at_utc,
            verification_completed_at_utc=self._clock(),
            outcome=outcome,
            failure_code=failure_code,
            detail=detail,
            source_observation_before=before,
            source_observation_after=after,
        )


def _stream_sha256(*, path: Path, chunk_size_bytes: int) -> tuple[str, int]:
    digest = hashlib.sha256()
    observed_size = 0
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size_bytes):
            digest.update(chunk)
            observed_size += len(chunk)
    return digest.hexdigest(), observed_size


def _observation(value: object) -> SourceFileObservation:
    return SourceFileObservation(
        size_bytes=int(value.st_size),
        modified_at_ns=int(value.st_mtime_ns),
        mode=int(value.st_mode),
        device_id=_optional_nonnegative_int(getattr(value, "st_dev", None)),
        inode=_optional_nonnegative_int(getattr(value, "st_ino", None)),
    )


def _optional_nonnegative_int(value: object) -> int | None:
    if value is None:
        return None
    converted = int(value)
    return converted if converted >= 0 else None


def _source_changed(
    before: SourceFileObservation,
    after: SourceFileObservation,
) -> bool:
    return (
        before.size_bytes != after.size_bytes
        or before.modified_at_ns != after.modified_at_ns
        or before.mode != after.mode
        or (
            before.device_id is not None
            and after.device_id is not None
            and before.device_id != after.device_id
        )
        or (before.inode is not None and after.inode is not None and before.inode != after.inode)
    )


def _build_totals(
    evidence: tuple[FileIntegrityEvidence, ...],
) -> ContentIntegrityTotals:
    counts = {outcome: 0 for outcome in ContentIntegrityOutcome}
    for item in evidence:
        counts[item.outcome] += 1
    return ContentIntegrityTotals(
        candidate_file_count=len(evidence),
        verified_count=counts[ContentIntegrityOutcome.VERIFIED],
        source_changed_count=counts[ContentIntegrityOutcome.SOURCE_CHANGED],
        size_mismatch_count=counts[ContentIntegrityOutcome.SIZE_MISMATCH],
        digest_mismatch_count=counts[ContentIntegrityOutcome.DIGEST_MISMATCH],
        missing_count=counts[ContentIntegrityOutcome.MISSING],
        inaccessible_count=counts[ContentIntegrityOutcome.INACCESSIBLE],
        not_regular_file_count=counts[ContentIntegrityOutcome.NOT_REGULAR_FILE],
        filesystem_error_count=counts[ContentIntegrityOutcome.FILESYSTEM_ERROR],
        total_expected_bytes=sum(item.expected_size_bytes for item in evidence),
        total_observed_bytes=sum(item.observed_size_bytes or 0 for item in evidence),
    )


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)
