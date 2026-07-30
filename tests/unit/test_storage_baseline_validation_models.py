from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
    EvidenceRequirementObservation,
    EvidenceRequirementStatus,
    PreservationBaselineCandidate,
    PreservationBaselineCandidateIdentity,
    PreservationBaselineCandidateScope,
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.models.storage_baseline_validation import (
    STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
    EvidenceSchemaCompatibilityRule,
    EvidenceValidationStatus,
    PreservationBaselineValidationIdentity,
    PreservationBaselineValidationResult,
    PreservationEvidenceValidationPolicy,
    ValidatedEvidenceReference,
    ValidationFinding,
    ValidationFindingCategory,
    ValidationFindingSeverity,
    stable_preservation_baseline_validation_id,
)


def _reference() -> PreservationEvidenceReference:
    return PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        source_root_id="root-a",
        schema_version="1.0",
        evidence_path=Path("/evidence/inventory.jsonl"),
        digest_path=Path("/evidence/inventory.jsonl.sha256"),
        sha256="a" * 64,
        byte_count=100,
    )


def _candidate() -> PreservationBaselineCandidate:
    reference = _reference()
    return PreservationBaselineCandidate(
        identity=PreservationBaselineCandidateIdentity(
            schema_version=STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
            candidate_id="pbc-" + "b" * 64,
            baseline_id="baseline-a",
            created_at_utc=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
        ),
        scope=PreservationBaselineCandidateScope(
            baseline_id="baseline-a",
            source_root_ids=("root-a",),
        ),
        observations=(
            EvidenceRequirementObservation(
                source_root_id="root-a",
                evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
                status=EvidenceRequirementStatus.PRESENT,
                evidence_reference=reference,
            ),
        ),
    )


def _validated() -> ValidatedEvidenceReference:
    return ValidatedEvidenceReference(
        evidence_reference=_reference(),
        status=EvidenceValidationStatus.VERIFIED,
        calculated_sha256="a" * 64,
        calculated_byte_count=100,
        sidecar_sha256="a" * 64,
        resolved_schema_name="poe.storage.inventory-evidence",
        resolved_schema_version="1.0",
    )


def test_validation_schema_version_is_governed() -> None:
    assert STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION == "1.0"


def test_finding_normalizes_text_and_requires_absolute_path() -> None:
    finding = ValidationFinding(
        sequence=1,
        category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
        severity=ValidationFindingSeverity.WARNING,
        source_root_id=" root-a ",
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        evidence_path=Path("/evidence/inventory.jsonl"),
        field_name=" exception_count ",
        expected=" 0 ",
        observed=" 1 ",
        detail=" explicit exception remains visible ",
    )

    assert finding.source_root_id == "root-a"
    assert finding.field_name == "exception_count"
    assert finding.detail == "explicit exception remains visible"

    with pytest.raises(ValueError, match="absolute"):
        ValidationFinding(
            sequence=1,
            category=ValidationFindingCategory.EVIDENCE_UNREADABLE,
            severity=ValidationFindingSeverity.ERROR,
            source_root_id="root-a",
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            evidence_path=Path("relative.json"),
            field_name=None,
            expected=None,
            observed=None,
            detail="unreadable",
        )


def test_policy_requires_canonical_explicit_rules() -> None:
    rule = EvidenceSchemaCompatibilityRule(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        schema_name=" poe.storage.inventory-evidence ",
        supported_versions=("1.0",),
    )
    policy = PreservationEvidenceValidationPolicy(
        profile_id=" strict-v1 ",
        supported_schema_versions=(rule,),
    )

    assert policy.profile_id == "strict-v1"
    assert rule.schema_name == "poe.storage.inventory-evidence"

    with pytest.raises(ValueError, match="duplicates"):
        PreservationEvidenceValidationPolicy(
            profile_id="strict-v1",
            supported_schema_versions=(rule, rule),
        )


def test_validation_identity_requires_utc_and_governed_id() -> None:
    with pytest.raises(ValueError, match="UTC"):
        PreservationBaselineValidationIdentity(
            schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
            validation_id="pbv-" + "c" * 64,
            candidate_id="pbc-" + "b" * 64,
            baseline_id="baseline-a",
            validated_at_utc=datetime(2026, 7, 30, 14, 0),
        )


def test_stable_validation_id_excludes_timestamp() -> None:
    candidate = _candidate()
    validated = (_validated(),)
    findings: tuple[ValidationFinding, ...] = ()

    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-v1",
        validated_evidence=validated,
        findings=findings,
    )

    first = PreservationBaselineValidationIdentity(
        schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
        validation_id=validation_id,
        candidate_id=candidate.identity.candidate_id,
        baseline_id=candidate.identity.baseline_id,
        validated_at_utc=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
    )
    second = PreservationBaselineValidationIdentity(
        schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
        validation_id=validation_id,
        candidate_id=candidate.identity.candidate_id,
        baseline_id=candidate.identity.baseline_id,
        validated_at_utc=datetime(2026, 7, 30, 15, 0, tzinfo=UTC),
    )

    assert first.validation_id == second.validation_id


def test_result_enforces_lineage_and_exact_present_reference_coverage() -> None:
    candidate = _candidate()
    validated = (_validated(),)
    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-v1",
        validated_evidence=validated,
        findings=(),
    )
    result = PreservationBaselineValidationResult(
        identity=PreservationBaselineValidationIdentity(
            schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
            validation_id=validation_id,
            candidate_id=candidate.identity.candidate_id,
            baseline_id=candidate.identity.baseline_id,
            validated_at_utc=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
        ),
        candidate=candidate,
        policy_profile_id="strict-v1",
        validated_evidence=validated,
        findings=(),
    )

    assert result.validated_evidence == validated
    with pytest.raises(FrozenInstanceError):
        result.policy_profile_id = "changed"  # type: ignore[misc]


def test_result_rejects_noncontiguous_finding_sequences() -> None:
    candidate = _candidate()
    validated = (_validated(),)
    finding = ValidationFinding(
        sequence=2,
        category=ValidationFindingCategory.EVIDENCE_EXCEPTIONS_PRESENT,
        severity=ValidationFindingSeverity.WARNING,
        source_root_id="root-a",
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        evidence_path=Path("/evidence/inventory.jsonl"),
        field_name="exception_count",
        expected="0",
        observed="1",
        detail="explicit exception remains visible",
    )
    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-v1",
        validated_evidence=validated,
        findings=(finding,),
    )

    with pytest.raises(ValueError, match="contiguous"):
        PreservationBaselineValidationResult(
            identity=PreservationBaselineValidationIdentity(
                schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
                validation_id=validation_id,
                candidate_id=candidate.identity.candidate_id,
                baseline_id=candidate.identity.baseline_id,
                validated_at_utc=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
            ),
            candidate=candidate,
            policy_profile_id="strict-v1",
            validated_evidence=validated,
            findings=(finding,),
        )


def test_validation_models_do_not_expose_authority_fields() -> None:
    fields = set(PreservationBaselineValidationResult.__dataclass_fields__)

    assert "acceptance_recommendation" not in fields
    assert "acceptance_mode" not in fields
    assert "human_authorization" not in fields
    assert "migration_authority" not in fields
    assert "cleanup_authority" not in fields
