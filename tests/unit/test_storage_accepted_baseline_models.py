"""Tests for accepted-preservation-baseline publication contracts."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_accepted_baseline import (
    STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION,
    AcceptedPreservationBaseline,
    AcceptedPreservationBaselineArtifact,
    AcceptedPreservationBaselineMode,
    AcceptedPreservationBaselinePublicationResult,
    AcceptedPreservationBaselineReference,
    stable_accepted_preservation_baseline_id,
)
from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
    AcceptanceDecision,
    AcceptanceEvaluationIdentity,
    AcceptanceMode,
    PreservationBaselineAcceptanceRecommendation,
    stable_preservation_baseline_acceptance_evaluation_id,
)
from poe_backup_orchestrator.models.storage_baseline_authorization import (
    AuthorizationAuthority,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    PreservationBaselineAuthorizationDecision,
)
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
    EvidenceValidationStatus,
    PreservationBaselineValidationIdentity,
    PreservationBaselineValidationResult,
    ValidatedEvidenceReference,
    stable_preservation_baseline_validation_id,
)
from poe_backup_orchestrator.services.storage_baseline_authorization import (
    PreservationBaselineAuthorizationDecisionAssembler,
)
from poe_backup_orchestrator.services.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationStore,
)


def authorization_decision() -> PreservationBaselineAuthorizationDecision:
    """Build one complete strict authorization for Slice 6B-6 tests."""

    reference = PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        source_root_id="root-a",
        schema_version="1.0",
        evidence_path=Path("/evidence/inventory.jsonl"),
        digest_path=Path("/evidence/inventory.jsonl.sha256"),
        sha256="a" * 64,
        byte_count=100,
    )
    candidate = PreservationBaselineCandidate(
        identity=PreservationBaselineCandidateIdentity(
            schema_version=STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
            candidate_id="pbc-" + "b" * 64,
            baseline_id="baseline-a",
            created_at_utc=datetime(2026, 7, 31, 14, 0, tzinfo=UTC),
        ),
        scope=PreservationBaselineCandidateScope(
            baseline_id="baseline-a", source_root_ids=("root-a",)
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
    validated = (
        ValidatedEvidenceReference(
            evidence_reference=reference,
            status=EvidenceValidationStatus.VERIFIED,
            calculated_sha256=reference.sha256,
            calculated_byte_count=reference.byte_count,
            sidecar_sha256=reference.sha256,
            resolved_schema_name="poe.storage.inventory-evidence",
            resolved_schema_version="1.0",
        ),
    )
    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-validation-v1",
        validated_evidence=validated,
        findings=(),
    )
    validation = PreservationBaselineValidationResult(
        identity=PreservationBaselineValidationIdentity(
            schema_version=STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
            validation_id=validation_id,
            candidate_id=candidate.identity.candidate_id,
            baseline_id=candidate.identity.baseline_id,
            validated_at_utc=datetime(2026, 7, 31, 15, 0, tzinfo=UTC),
        ),
        candidate=candidate,
        policy_profile_id="strict-validation-v1",
        validated_evidence=validated,
        findings=(),
    )
    rationale_codes = ("no_validation_findings", "recommend_acceptance")
    evaluation_id = stable_preservation_baseline_acceptance_evaluation_id(
        validation_id=validation.identity.validation_id,
        candidate_id=validation.identity.candidate_id,
        baseline_id=validation.identity.baseline_id,
        policy_id="baseline-acceptance",
        policy_version="1.0",
        mode=AcceptanceMode.REVIEW_PERMITTED,
        conditions=(),
        decision=AcceptanceDecision.RECOMMEND_ACCEPTANCE,
        rationale_codes=rationale_codes,
    )
    recommendation = PreservationBaselineAcceptanceRecommendation(
        identity=AcceptanceEvaluationIdentity(
            schema_version=STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
            evaluation_id=evaluation_id,
            validation_id=validation.identity.validation_id,
            candidate_id=validation.identity.candidate_id,
            baseline_id=validation.identity.baseline_id,
            policy_id="baseline-acceptance",
            policy_version="1.0",
        ),
        validation_result=validation,
        mode=AcceptanceMode.REVIEW_PERMITTED,
        decision=AcceptanceDecision.RECOMMEND_ACCEPTANCE,
        conditions=(),
        rationale_codes=rationale_codes,
    )
    return PreservationBaselineAuthorizationDecisionAssembler().assemble(
        recommendation=recommendation,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        authority=AuthorizationAuthority(
            authority_id="authority-a",
            display_name="Governance Authority",
            authority_role="System Owner",
            authority_basis="Approved preservation governance",
        ),
        decided_at_utc=datetime(2026, 7, 31, 18, 0, tzinfo=UTC),
        condition_decisions=(),
        scope=AuthorizationScope(
            accepted_source_root_ids=("root-a",),
            excluded_source_root_ids=(),
            scope_limitations=(),
        ),
        pilot=None,
        retention_obligations=("retain until migration closeout",),
        supersession_eligible=True,
        rationale="Explicit human authorization.",
    )


def persisted_authorization(tmp_path: Path):
    return PreservationBaselineAuthorizationStore().persist(
        decision=authorization_decision(), destination_directory=tmp_path / "authorization"
    )


def baseline_from_persistence(tmp_path: Path) -> AcceptedPreservationBaseline:
    from poe_backup_orchestrator.services.storage_accepted_baseline import (
        AcceptedPreservationBaselineConstructor,
    )

    return AcceptedPreservationBaselineConstructor().construct(persisted_authorization(tmp_path))


def test_schema_identity_and_exact_projection(tmp_path: Path) -> None:
    baseline = baseline_from_persistence(tmp_path)
    decision = baseline.authorization_decision

    assert STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION == "1.0"
    assert baseline.identity.accepted_baseline_id.startswith("pab-")
    assert baseline.identity.authorization_id == decision.identity.authorization_id
    assert baseline.mode is AcceptedPreservationBaselineMode.STRICT
    assert baseline.accepted_source_root_ids == ("root-a",)
    assert baseline.excluded_source_root_ids == ()
    assert baseline.accepted_evidence_graph == (
        decision.recommendation.validation_result.candidate.observations[0],
    )
    assert baseline.authorization_decision is decision


def test_one_authorization_has_one_valid_identity_and_baseline(tmp_path: Path) -> None:
    first = baseline_from_persistence(tmp_path)
    second = baseline_from_persistence(tmp_path)

    assert first == second
    assert first.identity.accepted_baseline_id == second.identity.accepted_baseline_id
    with pytest.raises(ValueError, match="mode"):
        replace(first, mode=AcceptedPreservationBaselineMode.PILOT)
    with pytest.raises(ValueError, match="semantic projection"):
        replace(
            first,
            identity=replace(first.identity, accepted_baseline_id="pab-" + "0" * 64),
        )


def test_semantic_identity_excludes_artifact_metadata_and_timestamps(tmp_path: Path) -> None:
    baseline = baseline_from_persistence(tmp_path)
    decision = baseline.authorization_decision
    identity = decision.identity
    derived = stable_accepted_preservation_baseline_id(
        authorization_id=identity.authorization_id,
        evaluation_id=identity.evaluation_id,
        validation_id=identity.validation_id,
        candidate_id=identity.candidate_id,
        baseline_id=identity.baseline_id,
        mode=baseline.mode,
        accepted_source_root_ids=baseline.accepted_source_root_ids,
        excluded_source_root_ids=baseline.excluded_source_root_ids,
        scope_limitations=baseline.scope_limitations,
        condition_decisions=baseline.condition_decisions,
        pilot=baseline.pilot,
        retention_obligations=baseline.retention_obligations,
        supersession_eligible=baseline.supersession_eligible,
    )

    assert derived == baseline.identity.accepted_baseline_id
    assert "artifact" not in stable_accepted_preservation_baseline_id.__annotations__


def test_scope_graph_and_lineage_cannot_diverge(tmp_path: Path) -> None:
    baseline = baseline_from_persistence(tmp_path)

    with pytest.raises(ValueError, match="accepted source roots"):
        replace(baseline, accepted_source_root_ids=())
    with pytest.raises(ValueError, match="evidence graph"):
        replace(baseline, accepted_evidence_graph=())
    with pytest.raises(ValueError, match="authorization_id"):
        replace(
            baseline,
            identity=replace(baseline.identity, authorization_id="pbd-" + "0" * 64),
        )


def test_reference_has_no_semantic_reference_id(tmp_path: Path) -> None:
    baseline = baseline_from_persistence(tmp_path)
    accepted_id = baseline.identity.accepted_baseline_id
    filename = f"accepted-preservation-baseline-{accepted_id}.json"
    reference = AcceptedPreservationBaselineReference(
        schema_version=STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION,
        accepted_baseline_id=accepted_id,
        baseline_id=baseline.identity.baseline_id,
        authorization_id=baseline.identity.authorization_id,
        mode=baseline.mode,
        accepted_source_root_ids=baseline.accepted_source_root_ids,
        excluded_source_root_ids=baseline.excluded_source_root_ids,
        accepted_baseline_filename=filename,
        accepted_baseline_sha256_filename=f"{filename}.sha256",
        accepted_baseline_sha256="a" * 64,
        accepted_baseline_byte_count=100,
    )

    assert not hasattr(reference, "reference_id")
    with pytest.raises(ValueError, match="filename"):
        replace(reference, accepted_baseline_filename="other.json")


def test_artifact_and_publication_result_bind_identity(tmp_path: Path) -> None:
    accepted_id = "pab-" + "a" * 64
    full_path = tmp_path / f"accepted-preservation-baseline-{accepted_id}.json"
    ref_path = tmp_path / f"accepted-preservation-baseline-reference-{accepted_id}.json"
    full = AcceptedPreservationBaselineArtifact(
        evidence_path=full_path,
        sha256_path=Path(f"{full_path}.sha256"),
        sha256="b" * 64,
        byte_count=10,
    )
    reference = AcceptedPreservationBaselineArtifact(
        evidence_path=ref_path,
        sha256_path=Path(f"{ref_path}.sha256"),
        sha256="c" * 64,
        byte_count=10,
    )
    result = AcceptedPreservationBaselinePublicationResult(
        accepted_baseline_id=accepted_id,
        baseline_id="baseline-a",
        authorization_id="pbd-" + "d" * 64,
        accepted_baseline_artifact=full,
        reference_artifact=reference,
        idempotent_replay=False,
    )

    assert result.reference_artifact is reference
    with pytest.raises(ValueError, match="reference artifact filename"):
        replace(result, reference_artifact=full)


def test_model_module_has_no_service_dependency() -> None:
    source = Path("src/poe_backup_orchestrator/models/storage_accepted_baseline.py").read_text()
    assert "poe_backup_orchestrator.services" not in source
