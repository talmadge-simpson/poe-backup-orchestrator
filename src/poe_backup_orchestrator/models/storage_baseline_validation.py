"""Immutable preservation-baseline evidence-validation contracts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    EvidenceRequirementStatus,
    PreservationBaselineCandidate,
    PreservationEvidenceReference,
    PreservationEvidenceType,
)

STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION: Final[str] = "1.0"

_VALIDATION_ID_PATTERN = re.compile(r"pbv-[0-9a-f]{64}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


class ValidationFindingSeverity(StrEnum):
    """Technical severity without acceptance-policy semantics."""

    INFORMATIONAL = "informational"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationFindingCategory(StrEnum):
    """Deterministic categories supported by the approved validation contract."""

    EVIDENCE_MISSING = "evidence_missing"
    EVIDENCE_NOT_APPLICABLE = "evidence_not_applicable"
    EVIDENCE_ARTIFACT_MISSING = "evidence_artifact_missing"
    EVIDENCE_UNREADABLE = "evidence_unreadable"
    EVIDENCE_SIZE_MISMATCH = "evidence_size_mismatch"
    EVIDENCE_DIGEST_MISMATCH = "evidence_digest_mismatch"
    DIGEST_SIDECAR_MISSING = "digest_sidecar_missing"
    DIGEST_SIDECAR_UNREADABLE = "digest_sidecar_unreadable"
    DIGEST_SIDECAR_MALFORMED = "digest_sidecar_malformed"
    DIGEST_SIDECAR_MISMATCH = "digest_sidecar_mismatch"
    EVIDENCE_MALFORMED = "evidence_malformed"
    EVIDENCE_SCHEMA_UNSUPPORTED = "evidence_schema_unsupported"
    EVIDENCE_SCHEMA_INCOMPATIBLE = "evidence_schema_incompatible"
    CANDIDATE_REFERENCE_INCONSISTENT = "candidate_reference_inconsistent"
    BASELINE_IDENTITY_MISMATCH = "baseline_identity_mismatch"
    SOURCE_DEVICE_IDENTITY_MISMATCH = "source_device_identity_mismatch"
    SOURCE_VOLUME_IDENTITY_MISMATCH = "source_volume_identity_mismatch"
    SOURCE_ROOT_IDENTITY_MISMATCH = "source_root_identity_mismatch"
    CAPTURE_SESSION_IDENTITY_MISMATCH = "capture_session_identity_mismatch"
    DUPLICATE_EVIDENCE = "duplicate_evidence"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    INVENTORY_RECONCILIATION_MISMATCH = "inventory_reconciliation_mismatch"
    CONTENT_CAPTURE_RECONCILIATION_MISMATCH = "content_capture_reconciliation_mismatch"
    CONTENT_INTEGRITY_RECONCILIATION_MISMATCH = "content_integrity_reconciliation_mismatch"
    UNSUPPORTED_OBJECTS_PRESENT = "unsupported_objects_present"
    EVIDENCE_EXCEPTIONS_PRESENT = "evidence_exceptions_present"
    SOURCE_CHANGE_OBSERVED = "source_change_observed"
    CAPTURE_INCOMPLETE = "capture_incomplete"


class EvidenceValidationStatus(StrEnum):
    """Validation outcome for one present evidence reference."""

    VERIFIED = "verified"
    MISSING = "missing"
    UNREADABLE = "unreadable"
    SIZE_MISMATCH = "size_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    MALFORMED = "malformed"
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    INCOMPATIBLE_SCHEMA = "incompatible_schema"


def _normalize_required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _require_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must be UTC")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """One normalized technical validation observation."""

    sequence: int
    category: ValidationFindingCategory
    severity: ValidationFindingSeverity
    source_root_id: str | None
    evidence_type: PreservationEvidenceType | None
    evidence_path: Path | None
    field_name: str | None
    expected: str | None
    observed: str | None
    detail: str

    def __post_init__(self) -> None:
        if self.sequence <= 0:
            raise ValueError("sequence must be positive")

        source_root_id = _normalize_optional(self.source_root_id)
        field_name = _normalize_optional(self.field_name)
        expected = _normalize_optional(self.expected)
        observed = _normalize_optional(self.observed)
        detail = _normalize_required(self.detail, "detail")

        if self.evidence_path is not None and not self.evidence_path.is_absolute():
            raise ValueError("evidence_path must be absolute when present")

        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "field_name", field_name)
        object.__setattr__(self, "expected", expected)
        object.__setattr__(self, "observed", observed)
        object.__setattr__(self, "detail", detail)


@dataclass(frozen=True, slots=True)
class ValidatedEvidenceReference:
    """Validation outcome for exactly one candidate evidence reference."""

    evidence_reference: PreservationEvidenceReference
    status: EvidenceValidationStatus
    calculated_sha256: str | None
    calculated_byte_count: int | None
    sidecar_sha256: str | None
    resolved_schema_name: str | None
    resolved_schema_version: str | None

    def __post_init__(self) -> None:
        for field_name in ("calculated_sha256", "sidecar_sha256"):
            value = getattr(self, field_name)
            if value is not None and _SHA256_PATTERN.fullmatch(value) is None:
                raise ValueError(f"{field_name} must be 64 lowercase hexadecimal characters")

        if self.calculated_byte_count is not None and self.calculated_byte_count < 0:
            raise ValueError("calculated_byte_count must not be negative")

        object.__setattr__(
            self,
            "resolved_schema_name",
            _normalize_optional(self.resolved_schema_name),
        )
        object.__setattr__(
            self,
            "resolved_schema_version",
            _normalize_optional(self.resolved_schema_version),
        )


@dataclass(frozen=True, slots=True)
class EvidenceSchemaCompatibilityRule:
    """One explicitly supported evidence schema registration."""

    evidence_type: PreservationEvidenceType
    schema_name: str
    supported_versions: tuple[str, ...]

    def __post_init__(self) -> None:
        schema_name = _normalize_required(self.schema_name, "schema_name")
        versions = tuple(
            _normalize_required(version, "supported version") for version in self.supported_versions
        )
        if not versions:
            raise ValueError("supported_versions must not be empty")
        if len(set(versions)) != len(versions):
            raise ValueError("supported_versions must not contain duplicates")
        if versions != tuple(sorted(versions)):
            raise ValueError("supported_versions must be in ascending order")

        object.__setattr__(self, "schema_name", schema_name)
        object.__setattr__(self, "supported_versions", versions)


@dataclass(frozen=True, slots=True)
class PreservationEvidenceValidationPolicy:
    """Technical validation configuration without acceptance authority."""

    profile_id: str
    supported_schema_versions: tuple[EvidenceSchemaCompatibilityRule, ...]
    require_digest_sidecars: bool = True
    verify_reference_byte_count: bool = True
    verify_reference_sha256: bool = True

    def __post_init__(self) -> None:
        profile_id = _normalize_required(self.profile_id, "profile_id")
        rules = tuple(self.supported_schema_versions)
        keys = [(rule.evidence_type.value, rule.schema_name) for rule in rules]
        if len(set(keys)) != len(keys):
            raise ValueError("supported schema rules must not contain duplicates")
        if keys != sorted(keys):
            raise ValueError("supported schema rules must use canonical ordering")

        object.__setattr__(self, "profile_id", profile_id)
        object.__setattr__(self, "supported_schema_versions", rules)


@dataclass(frozen=True, slots=True)
class PreservationBaselineValidationIdentity:
    """Stable validation identity plus audit timestamp."""

    schema_version: str
    validation_id: str
    candidate_id: str
    baseline_id: str
    validated_at_utc: datetime

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION:
            raise ValueError("unsupported validation schema_version")
        if _VALIDATION_ID_PATTERN.fullmatch(self.validation_id) is None:
            raise ValueError("validation_id must use the governed pbv identifier")
        object.__setattr__(
            self,
            "candidate_id",
            _normalize_required(self.candidate_id, "candidate_id"),
        )
        object.__setattr__(
            self,
            "baseline_id",
            _normalize_required(self.baseline_id, "baseline_id"),
        )
        object.__setattr__(
            self,
            "validated_at_utc",
            _require_utc(self.validated_at_utc, "validated_at_utc"),
        )


def _validated_reference_key(
    item: ValidatedEvidenceReference,
) -> tuple[str, str, str, str]:
    reference = item.evidence_reference
    return (
        reference.source_root_id,
        reference.evidence_type.value,
        reference.schema_version,
        reference.sha256,
    )


def _finding_semantic_payload(finding: ValidationFinding) -> dict[str, object]:
    return {
        "category": finding.category.value,
        "severity": finding.severity.value,
        "source_root_id": finding.source_root_id,
        "evidence_type": (
            finding.evidence_type.value if finding.evidence_type is not None else None
        ),
        "evidence_path": (
            finding.evidence_path.as_posix() if finding.evidence_path is not None else None
        ),
        "field_name": finding.field_name,
        "expected": finding.expected,
        "observed": finding.observed,
        "detail": finding.detail,
    }


def stable_preservation_baseline_validation_id(
    *,
    candidate_id: str,
    policy_profile_id: str,
    validated_evidence: tuple[ValidatedEvidenceReference, ...],
    findings: tuple[ValidationFinding, ...],
) -> str:
    """Derive stable validation identity from semantic validation outcomes."""

    candidate_id = _normalize_required(candidate_id, "candidate_id")
    policy_profile_id = _normalize_required(
        policy_profile_id,
        "policy_profile_id",
    )

    evidence_payload = []
    for item in validated_evidence:
        reference = item.evidence_reference
        evidence_payload.append(
            {
                "source_root_id": reference.source_root_id,
                "evidence_type": reference.evidence_type.value,
                "schema_version": reference.schema_version,
                "reference_sha256": reference.sha256,
                "reference_byte_count": reference.byte_count,
                "status": item.status.value,
                "calculated_sha256": item.calculated_sha256,
                "calculated_byte_count": item.calculated_byte_count,
                "sidecar_sha256": item.sidecar_sha256,
                "resolved_schema_name": item.resolved_schema_name,
                "resolved_schema_version": item.resolved_schema_version,
            }
        )

    payload = {
        "schema_version": STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
        "candidate_id": candidate_id,
        "policy_profile_id": policy_profile_id,
        "validated_evidence": evidence_payload,
        "findings": [_finding_semantic_payload(item) for item in findings],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return f"pbv-{hashlib.sha256(encoded).hexdigest()}"


@dataclass(frozen=True, slots=True)
class PreservationBaselineValidationResult:
    """Immutable technical validation result with candidate lineage."""

    identity: PreservationBaselineValidationIdentity
    candidate: PreservationBaselineCandidate
    policy_profile_id: str
    validated_evidence: tuple[ValidatedEvidenceReference, ...]
    findings: tuple[ValidationFinding, ...]

    def __post_init__(self) -> None:
        policy_profile_id = _normalize_required(
            self.policy_profile_id,
            "policy_profile_id",
        )
        validated_evidence = tuple(self.validated_evidence)
        findings = tuple(self.findings)

        if self.identity.candidate_id != self.candidate.identity.candidate_id:
            raise ValueError("validation candidate identity does not match candidate")
        if self.identity.baseline_id != self.candidate.identity.baseline_id:
            raise ValueError("validation baseline identity does not match candidate")

        if validated_evidence != tuple(sorted(validated_evidence, key=_validated_reference_key)):
            raise ValueError("validated_evidence must use canonical ordering")

        validated_keys = [
            (
                item.evidence_reference.source_root_id,
                item.evidence_reference.evidence_type,
            )
            for item in validated_evidence
        ]
        if len(set(validated_keys)) != len(validated_keys):
            raise ValueError("duplicate validated evidence references are prohibited")

        present_keys = {
            (observation.source_root_id, observation.evidence_type)
            for observation in self.candidate.observations
            if observation.status is EvidenceRequirementStatus.PRESENT
        }
        if set(validated_keys) != present_keys:
            raise ValueError(
                "every present candidate reference requires exactly one validation result"
            )

        expected_sequences = tuple(range(1, len(findings) + 1))
        actual_sequences = tuple(finding.sequence for finding in findings)
        if actual_sequences != expected_sequences:
            raise ValueError("finding sequences must be contiguous beginning with one")

        stable_id = stable_preservation_baseline_validation_id(
            candidate_id=self.candidate.identity.candidate_id,
            policy_profile_id=policy_profile_id,
            validated_evidence=validated_evidence,
            findings=findings,
        )
        if self.identity.validation_id != stable_id:
            raise ValueError("validation_id does not match semantic validation result")

        object.__setattr__(self, "policy_profile_id", policy_profile_id)
        object.__setattr__(self, "validated_evidence", validated_evidence)
        object.__setattr__(self, "findings", findings)
