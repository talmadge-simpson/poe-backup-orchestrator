"""Service boundaries for preservation-baseline evidence validation."""

from __future__ import annotations

import hashlib
import re
import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final, Protocol

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceReference,
    PreservationEvidenceType,
)


class PreservationBaselineValidationError(Exception):
    """Raised when deterministic validation cannot safely be produced."""


_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")
_DEFAULT_EVIDENCE_CHUNK_SIZE_BYTES: Final[int] = 1024 * 1024


class EvidenceLoadStatus(StrEnum):
    """Deterministic loading and authenticity outcome for one reference."""

    VERIFIED = "verified"
    EVIDENCE_MISSING = "evidence_missing"
    EVIDENCE_NOT_REGULAR_FILE = "evidence_not_regular_file"
    EVIDENCE_UNREADABLE = "evidence_unreadable"
    EVIDENCE_SIZE_MISMATCH = "evidence_size_mismatch"
    EVIDENCE_DIGEST_MISMATCH = "evidence_digest_mismatch"
    DIGEST_SIDECAR_MISSING = "digest_sidecar_missing"
    DIGEST_SIDECAR_NOT_REGULAR_FILE = "digest_sidecar_not_regular_file"
    DIGEST_SIDECAR_UNREADABLE = "digest_sidecar_unreadable"
    DIGEST_SIDECAR_MALFORMED = "digest_sidecar_malformed"
    DIGEST_SIDECAR_MISMATCH = "digest_sidecar_mismatch"


@dataclass(frozen=True, slots=True)
class LoadedPreservationEvidence:
    """Immutable evidence-loading facts without semantic interpretation."""

    reference: PreservationEvidenceReference
    status: EvidenceLoadStatus
    evidence_bytes: bytes | None
    calculated_sha256: str | None
    calculated_byte_count: int | None
    sidecar_sha256: str | None
    detail_code: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("calculated_sha256", "sidecar_sha256"):
            value = getattr(self, field_name)
            if value is not None and _SHA256_PATTERN.fullmatch(value) is None:
                raise ValueError(
                    f"{field_name} must contain exactly 64 lowercase hexadecimal characters"
                )
        if self.calculated_byte_count is not None and self.calculated_byte_count < 0:
            raise ValueError("calculated_byte_count must not be negative")
        detail_code = None if self.detail_code is None else self.detail_code.strip()
        if detail_code == "":
            detail_code = None
        if self.status is EvidenceLoadStatus.VERIFIED:
            if self.evidence_bytes is None:
                raise ValueError("verified evidence requires evidence_bytes")
            if self.calculated_sha256 is None:
                raise ValueError("verified evidence requires calculated_sha256")
            if self.calculated_byte_count is None:
                raise ValueError("verified evidence requires calculated_byte_count")
            if self.sidecar_sha256 is None:
                raise ValueError("verified evidence requires sidecar_sha256")
            if detail_code is not None:
                raise ValueError("verified evidence must not include detail_code")
        else:
            if self.evidence_bytes is not None:
                raise ValueError("unverified evidence must not expose evidence_bytes")
            if detail_code is None:
                raise ValueError("unverified evidence requires detail_code")
        object.__setattr__(self, "detail_code", detail_code)


class PreservationEvidenceLoader(Protocol):
    """Load and authenticate exactly one candidate evidence reference."""

    def load(
        self,
        reference: PreservationEvidenceReference,
    ) -> LoadedPreservationEvidence:
        """Return deterministic immutable loading facts."""


@dataclass(frozen=True, slots=True)
class FilesystemPreservationEvidenceLoader:
    """Read exact referenced files and verify byte count, digest, and sidecar."""

    chunk_size_bytes: int = _DEFAULT_EVIDENCE_CHUNK_SIZE_BYTES

    def __post_init__(self) -> None:
        if self.chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be greater than zero")

    def load(
        self,
        reference: PreservationEvidenceReference,
    ) -> LoadedPreservationEvidence:
        evidence_path = reference.evidence_path
        evidence_state = _regular_file_state(evidence_path)
        if evidence_state == "missing":
            return _load_failure(
                reference, EvidenceLoadStatus.EVIDENCE_MISSING, "evidence_path_missing"
            )
        if evidence_state == "not_regular":
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_NOT_REGULAR_FILE,
                "evidence_path_not_regular_file",
            )
        if evidence_state == "unreadable":
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_UNREADABLE,
                "evidence_path_metadata_unreadable",
            )
        try:
            evidence_bytes, calculated_sha256, calculated_byte_count = _stream_evidence(
                evidence_path, self.chunk_size_bytes
            )
        except OSError:
            return _load_failure(
                reference, EvidenceLoadStatus.EVIDENCE_UNREADABLE, "evidence_bytes_unreadable"
            )
        if calculated_byte_count != reference.byte_count:
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_SIZE_MISMATCH,
                "reference_byte_count_mismatch",
                calculated_sha256,
                calculated_byte_count,
            )
        if calculated_sha256 != reference.sha256:
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_DIGEST_MISMATCH,
                "reference_sha256_mismatch",
                calculated_sha256,
                calculated_byte_count,
            )
        digest_state = _regular_file_state(reference.digest_path)
        if digest_state == "missing":
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISSING,
                "digest_path_missing",
                calculated_sha256,
                calculated_byte_count,
            )
        if digest_state == "not_regular":
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_NOT_REGULAR_FILE,
                "digest_path_not_regular_file",
                calculated_sha256,
                calculated_byte_count,
            )
        if digest_state == "unreadable":
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_UNREADABLE,
                "digest_path_metadata_unreadable",
                calculated_sha256,
                calculated_byte_count,
            )
        try:
            sidecar_text = reference.digest_path.read_text(encoding="ascii")
        except (OSError, UnicodeError):
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_UNREADABLE,
                "digest_sidecar_unreadable",
                calculated_sha256,
                calculated_byte_count,
            )
        parsed = _parse_digest_sidecar(sidecar_text, evidence_path.name)
        if parsed is None:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MALFORMED,
                "digest_sidecar_malformed",
                calculated_sha256,
                calculated_byte_count,
            )
        sidecar_sha256, filename_matches = parsed
        if not filename_matches:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH,
                "digest_sidecar_filename_mismatch",
                calculated_sha256,
                calculated_byte_count,
                sidecar_sha256,
            )
        if sidecar_sha256 != reference.sha256:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH,
                "digest_sidecar_reference_mismatch",
                calculated_sha256,
                calculated_byte_count,
                sidecar_sha256,
            )
        if sidecar_sha256 != calculated_sha256:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH,
                "digest_sidecar_calculated_mismatch",
                calculated_sha256,
                calculated_byte_count,
                sidecar_sha256,
            )
        return LoadedPreservationEvidence(
            reference=reference,
            status=EvidenceLoadStatus.VERIFIED,
            evidence_bytes=evidence_bytes,
            calculated_sha256=calculated_sha256,
            calculated_byte_count=calculated_byte_count,
            sidecar_sha256=sidecar_sha256,
        )


def _regular_file_state(path: Path) -> str:
    try:
        file_status = path.stat()
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unreadable"
    return "regular" if stat.S_ISREG(file_status.st_mode) else "not_regular"


def _stream_evidence(path: Path, chunk_size_bytes: int) -> tuple[bytes, str, int]:
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    byte_count = 0
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size_bytes):
            chunks.append(chunk)
            byte_count += len(chunk)
            digest.update(chunk)
    return b"".join(chunks), digest.hexdigest(), byte_count


def _parse_digest_sidecar(sidecar_text: str, expected_filename: str) -> tuple[str, bool] | None:
    line = sidecar_text.strip()
    if _SHA256_PATTERN.fullmatch(line):
        return line, True
    match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
    if match is None:
        return None
    return match.group(1), match.group(2) == expected_filename


def _load_failure(
    reference: PreservationEvidenceReference,
    status: EvidenceLoadStatus,
    detail_code: str,
    calculated_sha256: str | None = None,
    calculated_byte_count: int | None = None,
    sidecar_sha256: str | None = None,
) -> LoadedPreservationEvidence:
    return LoadedPreservationEvidence(
        reference=reference,
        status=status,
        evidence_bytes=None,
        calculated_sha256=calculated_sha256,
        calculated_byte_count=calculated_byte_count,
        sidecar_sha256=sidecar_sha256,
        detail_code=detail_code,
    )


class PreservationEvidenceAdapter(Protocol):
    """Typed adapter for one evidence category and schema family."""

    evidence_type: PreservationEvidenceType
    schema_name: str
    supported_versions: tuple[str, ...]

    def parse(self, evidence_bytes: bytes) -> object:
        """Parse authenticated evidence bytes."""

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        """Extract only facts required for technical validation."""


@dataclass(frozen=True, slots=True)
class ValidationAdapterRegistry:
    """Immutable deterministic evidence-adapter registry."""

    adapters: tuple[PreservationEvidenceAdapter, ...]

    def __post_init__(self) -> None:
        adapters = tuple(self.adapters)
        if not adapters:
            raise PreservationBaselineValidationError("at least one validation adapter is required")

        registrations: dict[
            tuple[PreservationEvidenceType, str, str],
            PreservationEvidenceAdapter,
        ] = {}

        for adapter in adapters:
            schema_name = adapter.schema_name.strip()
            versions = tuple(version.strip() for version in adapter.supported_versions)

            if not schema_name:
                raise PreservationBaselineValidationError("adapter schema_name must not be empty")
            if not versions or any(not version for version in versions):
                raise PreservationBaselineValidationError(
                    "adapter supported_versions must be explicit"
                )
            if len(set(versions)) != len(versions):
                raise PreservationBaselineValidationError(
                    "adapter supported_versions must not contain duplicates"
                )

            for version in versions:
                key = (adapter.evidence_type, schema_name, version)
                if key in registrations:
                    raise PreservationBaselineValidationError(
                        "duplicate or ambiguous validation adapter registration: "
                        f"{adapter.evidence_type.value}/{schema_name}/{version}"
                    )
                registrations[key] = adapter

        canonical = tuple(
            sorted(
                adapters,
                key=lambda adapter: (
                    adapter.evidence_type.value,
                    adapter.schema_name.strip(),
                    tuple(sorted(version.strip() for version in adapter.supported_versions)),
                ),
            )
        )
        object.__setattr__(self, "adapters", canonical)

    def resolve(
        self,
        *,
        evidence_type: PreservationEvidenceType,
        schema_name: str,
        schema_version: str,
    ) -> PreservationEvidenceAdapter:
        """Resolve exactly one adapter by evidence type, schema, and version."""

        normalized_schema = schema_name.strip()
        normalized_version = schema_version.strip()
        matches = tuple(
            adapter
            for adapter in self.adapters
            if adapter.evidence_type is evidence_type
            and adapter.schema_name.strip() == normalized_schema
            and normalized_version
            in tuple(version.strip() for version in adapter.supported_versions)
        )
        if len(matches) != 1:
            raise PreservationBaselineValidationError(
                "no unique validation adapter for "
                f"{evidence_type.value}/{normalized_schema}/{normalized_version}"
            )
        return matches[0]
