from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION: Final[str] = "1.0"
_CANDIDATE_ID_PREFIX: Final[str] = "pbc-"
_SHA256_HEX_LENGTH: Final[int] = 64


class PreservationEvidenceType(StrEnum):
    BASELINE_MANIFEST = "baseline_manifest"
    DISCOVERY_RESULT = "discovery_result"
    INVENTORY_EVIDENCE = "inventory_evidence"
    CONTENT_CAPTURE_RESULT = "content_capture_result"
    CONTENT_INTEGRITY_EVIDENCE = "content_integrity_evidence"
    EXCEPTION_EVIDENCE = "exception_evidence"
    RECONCILIATION_EVIDENCE = "reconciliation_evidence"


class EvidenceRequirementStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    NOT_APPLICABLE = "not_applicable"


@dataclass(frozen=True, slots=True)
class PreservationEvidenceReference:
    evidence_type: PreservationEvidenceType
    source_root_id: str
    schema_version: str
    evidence_path: Path
    digest_path: Path
    sha256: str
    byte_count: int

    def __post_init__(self) -> None:
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        schema_version = _normalize_text(self.schema_version, "schema_version")
        evidence_path = Path(self.evidence_path)
        digest_path = Path(self.digest_path)
        sha256 = _normalize_sha256(self.sha256, "sha256")
        if not evidence_path.is_absolute():
            raise ValueError("evidence_path must be absolute")
        if not digest_path.is_absolute():
            raise ValueError("digest_path must be absolute")
        if evidence_path == digest_path:
            raise ValueError("evidence_path and digest_path must be different")
        if self.byte_count < 0:
            raise ValueError("byte_count must be non-negative")
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "evidence_path", evidence_path)
        object.__setattr__(self, "digest_path", digest_path)
        object.__setattr__(self, "sha256", sha256)


@dataclass(frozen=True, slots=True)
class PreservationEvidenceRequirement:
    source_root_id: str
    evidence_type: PreservationEvidenceType
    applicable: bool = True
    detail: str | None = None

    def __post_init__(self) -> None:
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        detail = _normalize_optional_text(self.detail, "detail")
        if self.applicable and detail is not None:
            raise ValueError("applicable evidence requirement must not include detail")
        if not self.applicable and detail is None:
            raise ValueError("non-applicable evidence requirement requires detail")
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class EvidenceRequirementObservation:
    source_root_id: str
    evidence_type: PreservationEvidenceType
    status: EvidenceRequirementStatus
    evidence_reference: PreservationEvidenceReference | None
    detail: str | None = None

    def __post_init__(self) -> None:
        source_root_id = _normalize_identifier(self.source_root_id, "source_root_id")
        detail = _normalize_optional_text(self.detail, "detail")
        reference = self.evidence_reference
        if self.status is EvidenceRequirementStatus.PRESENT:
            if reference is None:
                raise ValueError("PRESENT observation requires evidence_reference")
            if detail is not None:
                raise ValueError("PRESENT observation must not include detail")
        else:
            if reference is not None:
                raise ValueError(
                    f"{self.status.value} observation must not include evidence_reference"
                )
            if detail is None:
                raise ValueError(f"{self.status.value} observation requires explanatory detail")
        if reference is not None:
            if reference.source_root_id != source_root_id:
                raise ValueError("observation and evidence reference source roots must match")
            if reference.evidence_type is not self.evidence_type:
                raise ValueError("observation and evidence reference types must match")
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class PreservationBaselineCandidateScope:
    baseline_id: str
    source_root_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        baseline_id = _normalize_identifier(self.baseline_id, "baseline_id")
        roots = tuple(
            _normalize_identifier(value, "source_root_id") for value in self.source_root_ids
        )
        if not roots:
            raise ValueError("source_root_ids must not be empty")
        if len(set(roots)) != len(roots):
            raise ValueError("source_root_ids must not contain duplicates")
        if roots != tuple(sorted(roots)):
            raise ValueError("source_root_ids must be in deterministic ascending order")
        object.__setattr__(self, "baseline_id", baseline_id)
        object.__setattr__(self, "source_root_ids", roots)


@dataclass(frozen=True, slots=True)
class PreservationBaselineCandidateIdentity:
    schema_version: str
    candidate_id: str
    baseline_id: str
    created_at_utc: datetime

    def __post_init__(self) -> None:
        schema_version = _normalize_text(self.schema_version, "schema_version")
        candidate_id = _normalize_identifier(self.candidate_id, "candidate_id")
        baseline_id = _normalize_identifier(self.baseline_id, "baseline_id")
        created_at_utc = _require_utc(self.created_at_utc, "created_at_utc")
        if schema_version != STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION:
            raise ValueError(
                f"schema_version must equal {STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION}"
            )
        _validate_candidate_id(candidate_id)
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "candidate_id", candidate_id)
        object.__setattr__(self, "baseline_id", baseline_id)
        object.__setattr__(self, "created_at_utc", created_at_utc)


@dataclass(frozen=True, slots=True)
class PreservationBaselineCandidate:
    identity: PreservationBaselineCandidateIdentity
    scope: PreservationBaselineCandidateScope
    observations: tuple[EvidenceRequirementObservation, ...]

    def __post_init__(self) -> None:
        observations = tuple(self.observations)
        if self.identity.baseline_id != self.scope.baseline_id:
            raise ValueError("identity and scope baseline identifiers must match")
        if not observations:
            raise ValueError("observations must not be empty")
        keys = tuple((item.source_root_id, item.evidence_type.value) for item in observations)
        if len(set(keys)) != len(keys):
            raise ValueError("observations must not contain duplicate requirement keys")
        if keys != tuple(sorted(keys)):
            raise ValueError("observations must be in deterministic order")
        scoped_roots = set(self.scope.source_root_ids)
        if any(item.source_root_id not in scoped_roots for item in observations):
            raise ValueError("every observation source root must belong to candidate scope")
        object.__setattr__(self, "observations", observations)


def stable_preservation_baseline_candidate_id(
    *,
    baseline_id: str,
    source_root_ids: tuple[str, ...],
    observations: tuple[EvidenceRequirementObservation, ...],
) -> str:
    baseline_id = _normalize_identifier(baseline_id, "baseline_id")
    roots = tuple(_normalize_identifier(value, "source_root_id") for value in source_root_ids)
    if not roots or roots != tuple(sorted(roots)) or len(set(roots)) != len(roots):
        raise ValueError("source_root_ids must be unique, non-empty, and deterministically ordered")
    observations = tuple(observations)
    keys = tuple((item.source_root_id, item.evidence_type.value) for item in observations)
    if keys != tuple(sorted(keys)) or len(set(keys)) != len(keys):
        raise ValueError("observations must be unique and in deterministic order")
    payload = {
        "schema_version": STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
        "baseline_id": baseline_id,
        "source_root_ids": list(roots),
        "observations": [
            {
                "source_root_id": item.source_root_id,
                "evidence_type": item.evidence_type.value,
                "status": item.status.value,
                "schema_version": (
                    item.evidence_reference.schema_version if item.evidence_reference else None
                ),
                "sha256": (item.evidence_reference.sha256 if item.evidence_reference else None),
                "byte_count": (
                    item.evidence_reference.byte_count if item.evidence_reference else None
                ),
            }
            for item in observations
        ],
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"{_CANDIDATE_ID_PREFIX}{hashlib.sha256(canonical).hexdigest()}"


def _validate_candidate_id(value: str) -> None:
    if not value.startswith(_CANDIDATE_ID_PREFIX):
        raise ValueError(f"candidate_id must start with {_CANDIDATE_ID_PREFIX}")
    digest = value.removeprefix(_CANDIDATE_ID_PREFIX)
    if len(digest) != _SHA256_HEX_LENGTH or any(
        character not in "0123456789abcdef" for character in digest
    ):
        raise ValueError(
            "candidate_id digest must contain exactly 64 lowercase hexadecimal characters"
        )


def _normalize_identifier(value: str, field_name: str) -> str:
    normalized = _normalize_text(value, field_name)
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


def _normalize_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_optional_text(
    value: str | None,
    field_name: str,
) -> str | None:
    return None if value is None else _normalize_text(value, field_name)


def _normalize_sha256(value: str, field_name: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != _SHA256_HEX_LENGTH or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{field_name} must contain exactly 64 lowercase hexadecimal characters")
    return normalized


def _require_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value
