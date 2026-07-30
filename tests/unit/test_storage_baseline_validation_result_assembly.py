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
    EvidenceSchemaCompatibilityRule,
    EvidenceValidationStatus,
    PreservationEvidenceValidationPolicy,
    ValidatedEvidenceReference,
    ValidationFinding,
    ValidationFindingCategory,
    ValidationFindingSeverity,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    PreservationBaselineValidationError,
    PreservationBaselineValidationResultAssembler,
)


def reference(
    *,
    evidence_type: PreservationEvidenceType,
    path: str,
    digest: str,
) -> PreservationEvidenceReference:
    return PreservationEvidenceReference(
        evidence_type=evidence_type,
        source_root_id="root-a",
        schema_version="1.0",
        evidence_path=Path(path),
        digest_path=Path(f"{path}.sha256"),
        sha256=digest,
        byte_count=100,
    )


INVENTORY = reference(
    evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
    path="/evidence/inventory.jsonl",
    digest="a" * 64,
)
INTEGRITY = reference(
    evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
    path="/evidence/integrity.jsonl",
    digest="b" * 64,
)


def candidate() -> PreservationBaselineCandidate:
    observations = tuple(
        EvidenceRequirementObservation(
            source_root_id="root-a",
            evidence_type=item.evidence_type,
            status=EvidenceRequirementStatus.PRESENT,
            evidence_reference=item,
        )
        for item in (INTEGRITY, INVENTORY)
    )
    return PreservationBaselineCandidate(
        identity=PreservationBaselineCandidateIdentity(
            schema_version=STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
            candidate_id="pbc-" + "c" * 64,
            baseline_id="baseline-a",
            created_at_utc=datetime(2026, 7, 30, 12, 0, tzinfo=UTC),
        ),
        scope=PreservationBaselineCandidateScope(
            baseline_id="baseline-a",
            source_root_ids=("root-a",),
        ),
        observations=observations,
    )


def policy() -> PreservationEvidenceValidationPolicy:
    return PreservationEvidenceValidationPolicy(
        profile_id="strict-v1",
        supported_schema_versions=(
            EvidenceSchemaCompatibilityRule(
                evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
                schema_name="poe.storage.content-integrity-evidence",
                supported_versions=("1.0",),
            ),
            EvidenceSchemaCompatibilityRule(
                evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
                schema_name="poe.storage.inventory-evidence",
                supported_versions=("1.0",),
            ),
        ),
    )


def validated(
    item: PreservationEvidenceReference,
    *,
    schema_name: str,
) -> ValidatedEvidenceReference:
    return ValidatedEvidenceReference(
        evidence_reference=item,
        status=EvidenceValidationStatus.VERIFIED,
        calculated_sha256=item.sha256,
        calculated_byte_count=item.byte_count,
        sidecar_sha256=item.sha256,
        resolved_schema_name=schema_name,
        resolved_schema_version="1.0",
    )


def finding(sequence: int = 1) -> ValidationFinding:
    return ValidationFinding(
        sequence=sequence,
        category=ValidationFindingCategory.CONTRADICTORY_EVIDENCE,
        severity=ValidationFindingSeverity.ERROR,
        source_root_id="root-a",
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        evidence_path=INVENTORY.evidence_path,
        field_name="item_id",
        expected="inventory-id",
        observed="integrity-id",
        detail="inventory and integrity item identifiers conflict",
    )


def assemble(
    *,
    validated_evidence: tuple[ValidatedEvidenceReference, ...],
    findings: tuple[ValidationFinding, ...] = (),
    timestamp: datetime = datetime(2026, 7, 30, 13, 0, tzinfo=UTC),
):
    return PreservationBaselineValidationResultAssembler().assemble(
        candidate=candidate(),
        validation_policy=policy(),
        validated_evidence=validated_evidence,
        findings=findings,
        validated_at_utc=timestamp,
    )


def all_validated() -> tuple[ValidatedEvidenceReference, ...]:
    return (
        validated(
            INVENTORY,
            schema_name="poe.storage.inventory-evidence",
        ),
        validated(
            INTEGRITY,
            schema_name="poe.storage.content-integrity-evidence",
        ),
    )


def test_assembler_produces_immutable_result_with_exact_lineage() -> None:
    result = assemble(validated_evidence=all_validated())

    assert result.identity.candidate_id == result.candidate.identity.candidate_id
    assert result.identity.baseline_id == result.candidate.identity.baseline_id
    assert result.policy_profile_id == "strict-v1"
    assert result.identity.validation_id.startswith("pbv-")
    with pytest.raises(FrozenInstanceError):
        result.policy_profile_id = "changed"  # type: ignore[misc]


def test_assembler_canonicalizes_validated_evidence_order() -> None:
    expected = assemble(validated_evidence=all_validated())
    reversed_result = assemble(validated_evidence=tuple(reversed(all_validated())))

    assert reversed_result.validated_evidence == expected.validated_evidence
    assert reversed_result.identity.validation_id == expected.identity.validation_id


def test_validation_identity_excludes_timestamp() -> None:
    first = assemble(
        validated_evidence=all_validated(),
        timestamp=datetime(2026, 7, 30, 13, 0, tzinfo=UTC),
    )
    second = assemble(
        validated_evidence=all_validated(),
        timestamp=datetime(2026, 7, 30, 14, 0, tzinfo=UTC),
    )

    assert first.identity.validation_id == second.identity.validation_id
    assert first.identity.validated_at_utc != second.identity.validated_at_utc


def test_assembler_preserves_ordered_contiguous_findings() -> None:
    result = assemble(
        validated_evidence=all_validated(),
        findings=(finding(),),
    )

    assert result.findings == (finding(),)


def test_assembler_rejects_duplicate_validated_references() -> None:
    duplicate = all_validated()[0]
    with pytest.raises(
        PreservationBaselineValidationError,
        match="duplicate references",
    ):
        assemble(validated_evidence=(duplicate, duplicate))


def test_assembler_rejects_noncontiguous_finding_sequences() -> None:
    with pytest.raises(
        PreservationBaselineValidationError,
        match="contiguous",
    ):
        assemble(validated_evidence=all_validated(), findings=(finding(2),))


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("candidate", object(), "candidate must"),
        ("validation_policy", object(), "validation_policy must"),
        ("validated_evidence", list(all_validated()), "immutable tuple"),
        ("findings", [finding()], "immutable tuple"),
    ],
)
def test_assembler_rejects_untyped_or_mutable_inputs(
    field: str,
    value: object,
    message: str,
) -> None:
    arguments = {
        "candidate": candidate(),
        "validation_policy": policy(),
        "validated_evidence": all_validated(),
        "findings": (),
        "validated_at_utc": datetime(2026, 7, 30, 13, 0, tzinfo=UTC),
    }
    arguments[field] = value

    with pytest.raises(PreservationBaselineValidationError, match=message):
        PreservationBaselineValidationResultAssembler().assemble(**arguments)


def test_result_assembly_exposes_no_policy_or_authority_fields() -> None:
    result = assemble(validated_evidence=all_validated())
    fields = set(result.__dataclass_fields__)

    assert "acceptance_recommendation" not in fields
    assert "acceptance_mode" not in fields
    assert "blocking" not in fields
    assert "overridable" not in fields
    assert "human_authorization" not in fields
    assert "migration_authority" not in fields
    assert "cleanup_authority" not in fields
