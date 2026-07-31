"""Tests for canonical immutable authorization-decision persistence."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from datetime import UTC, datetime
from pathlib import Path

import pytest

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
from poe_backup_orchestrator.services import (
    storage_baseline_authorization_persistence as persistence_module,
)
from poe_backup_orchestrator.services.storage_baseline_authorization import (
    PreservationBaselineAuthorizationDecisionAssembler,
)
from poe_backup_orchestrator.services.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationConflictError,
    PreservationBaselineAuthorizationLockError,
    PreservationBaselineAuthorizationPersistenceError,
    PreservationBaselineAuthorizationSerializer,
    PreservationBaselineAuthorizationStore,
)
from poe_backup_orchestrator.utilities.locking import exclusive_file_lock

DECIDED_AT = datetime(2026, 7, 31, 18, 2, 3, 456789, tzinfo=UTC)


def decision() -> PreservationBaselineAuthorizationDecision:
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
            authority_id="talmadge-simpson",
            display_name="Talmadge Simpson",
            authority_role="System Owner",
            authority_basis="Designated preservation-governance authority",
            organization="Personal Executive Operating System",
        ),
        decided_at_utc=DECIDED_AT,
        condition_decisions=(),
        scope=AuthorizationScope(
            accepted_source_root_ids=("root-a",),
            excluded_source_root_ids=(),
            scope_limitations=(),
        ),
        pilot=None,
        retention_obligations=("retain preservation evidence",),
        supersession_eligible=True,
        rationale="Explicit accountable decision with café evidence.",
    )


def expected_paths(
    root: Path, value: PreservationBaselineAuthorizationDecision
) -> tuple[Path, Path]:
    artifact = root / (
        f"preservation-baseline-authorization-{value.identity.authorization_id}.json"
    )
    return artifact, Path(f"{artifact}.sha256")


def test_serializer_is_canonical_complete_and_deterministic() -> None:
    value = decision()
    serializer = PreservationBaselineAuthorizationSerializer()
    original_identity = value.identity
    original_recommendation = value.recommendation

    first = serializer.serialize(value)
    second = serializer.serialize(value)
    payload = json.loads(first)

    assert first == second
    assert first.endswith(b"\n")
    assert not first.endswith(b"\n\n")
    assert b'"authority":{' in first
    assert b'"identity":{' in first
    assert "café".encode() in first
    assert payload["decided_at_utc"] == "2026-07-31T18:02:03.456789Z"
    assert payload["identity"]["authorization_id"] == value.identity.authorization_id
    assert payload["recommendation"]["identity"]["evaluation_id"] == (
        value.recommendation.identity.evaluation_id
    )
    assert payload["recommendation"]["validation_result"]["identity"]["validation_id"] == (
        value.recommendation.validation_result.identity.validation_id
    )
    assert payload["scope"]["accepted_source_root_ids"] == ["root-a"]
    assert serializer.calculate_sha256(value) == hashlib.sha256(first).hexdigest()
    assert value.identity is original_identity
    assert value.recommendation is original_recommendation


def test_serializer_rejects_generic_input_without_filesystem_effect(tmp_path: Path) -> None:
    with pytest.raises(PreservationBaselineAuthorizationPersistenceError, match="decision"):
        PreservationBaselineAuthorizationSerializer().serialize({})  # type: ignore[arg-type]

    assert list(tmp_path.iterdir()) == []


def test_unsupported_mapping_content_fails_before_filesystem_mutation(tmp_path: Path) -> None:
    value = decision()
    object.__setattr__(value, "rationale", {"unsupported": "mapping"})
    destination = tmp_path / "must-not-exist"

    with pytest.raises(
        PreservationBaselineAuthorizationPersistenceError,
        match="unsupported value of type dict",
    ):
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=destination,
        )

    assert not destination.exists()


def test_first_persistence_creates_restricted_exact_pair(tmp_path: Path) -> None:
    value = decision()
    result = PreservationBaselineAuthorizationStore().persist(
        decision=value,
        destination_directory=tmp_path,
    )
    artifact, sidecar = expected_paths(tmp_path, value)
    content = artifact.read_bytes()

    assert result.authorization_id == value.identity.authorization_id
    assert result.baseline_id == value.identity.baseline_id
    assert result.artifact.evidence_path == artifact
    assert result.artifact.sha256_path == sidecar
    assert result.artifact.byte_count == len(content)
    assert result.artifact.sha256 == hashlib.sha256(content).hexdigest()
    assert result.idempotent_replay is False
    assert not hasattr(result, "accepted_baseline")
    assert not hasattr(result, "publication_reference")
    assert sidecar.read_text(encoding="ascii") == (f"{result.artifact.sha256}  {artifact.name}\n")
    assert artifact.stat().st_mode & 0o777 == 0o640
    assert sidecar.stat().st_mode & 0o777 == 0o640
    assert not list(tmp_path.glob("*.tmp"))
    assert not list(tmp_path.glob(".*.tmp"))


def test_persist_requires_exact_decision_and_absolute_destination(tmp_path: Path) -> None:
    store = PreservationBaselineAuthorizationStore()
    with pytest.raises(PreservationBaselineAuthorizationPersistenceError, match="decision"):
        store.persist(decision={}, destination_directory=tmp_path)  # type: ignore[arg-type]
    with pytest.raises(PreservationBaselineAuthorizationPersistenceError, match="absolute"):
        store.persist(decision=decision(), destination_directory=Path("relative"))


def test_identical_replay_verifies_pair_without_rewriting(tmp_path: Path) -> None:
    value = decision()
    store = PreservationBaselineAuthorizationStore()
    first = store.persist(decision=value, destination_directory=tmp_path)
    artifact_stat = first.artifact.evidence_path.stat()
    sidecar_stat = first.artifact.sha256_path.stat()

    second = store.persist(decision=value, destination_directory=tmp_path)

    assert second.idempotent_replay is True
    assert second.artifact == first.artifact
    assert second.artifact.evidence_path.stat().st_mtime_ns == artifact_stat.st_mtime_ns
    assert second.artifact.sha256_path.stat().st_mtime_ns == sidecar_stat.st_mtime_ns


@pytest.mark.parametrize("missing", ("artifact", "sidecar"))
def test_incomplete_pair_fails_closed(tmp_path: Path, missing: str) -> None:
    value = decision()
    artifact, sidecar = expected_paths(tmp_path, value)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    if missing == "artifact":
        sidecar.write_text("a" * 64 + f"  {artifact.name}\n", encoding="ascii")
    else:
        artifact.write_bytes(PreservationBaselineAuthorizationSerializer().serialize(value))

    with pytest.raises(
        PreservationBaselineAuthorizationConflictError,
        match="incomplete_persistence_pair",
    ):
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=tmp_path,
        )

    assert artifact.exists() is (missing != "artifact")
    assert sidecar.exists() is (missing != "sidecar")


def test_differing_artifact_and_sidecar_conflicts_are_not_repaired(tmp_path: Path) -> None:
    value = decision()
    store = PreservationBaselineAuthorizationStore()
    persisted = store.persist(decision=value, destination_directory=tmp_path)
    persisted.artifact.evidence_path.write_bytes(b"contradictory\n")
    before = persisted.artifact.evidence_path.read_bytes()

    with pytest.raises(PreservationBaselineAuthorizationConflictError, match="content_conflict"):
        store.persist(decision=value, destination_directory=tmp_path)

    assert persisted.artifact.evidence_path.read_bytes() == before

    persisted.artifact.evidence_path.write_bytes(
        PreservationBaselineAuthorizationSerializer().serialize(value)
    )
    persisted.artifact.sha256_path.write_text("malformed\n", encoding="ascii")
    with pytest.raises(PreservationBaselineAuthorizationConflictError, match="sidecar_conflict"):
        store.persist(decision=value, destination_directory=tmp_path)
    assert persisted.artifact.sha256_path.read_text(encoding="ascii") == "malformed\n"


@pytest.mark.parametrize("target_kind", ("artifact_symlink", "sidecar_directory"))
def test_links_and_nonregular_targets_fail_closed(tmp_path: Path, target_kind: str) -> None:
    value = decision()
    artifact, sidecar = expected_paths(tmp_path, value)
    content = PreservationBaselineAuthorizationSerializer().serialize(value)
    digest = hashlib.sha256(content).hexdigest()
    if target_kind == "artifact_symlink":
        underlying = tmp_path / "underlying"
        underlying.write_bytes(content)
        artifact.symlink_to(underlying)
        sidecar.write_text(f"{digest}  {artifact.name}\n", encoding="ascii")
    else:
        artifact.write_bytes(content)
        sidecar.mkdir()

    with pytest.raises(
        PreservationBaselineAuthorizationConflictError,
        match="non_regular_persistence_target",
    ):
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=tmp_path,
        )


def test_lock_contention_preserves_immutable_absence(tmp_path: Path) -> None:
    value = decision()
    lock_path = tmp_path / ".locks" / "preservation-baseline-authorization.lock"

    with exclusive_file_lock(lock_path):
        with pytest.raises(PreservationBaselineAuthorizationLockError) as captured:
            PreservationBaselineAuthorizationStore().persist(
                decision=value,
                destination_directory=tmp_path,
            )

    assert captured.value.__cause__ is not None
    artifact, sidecar = expected_paths(tmp_path, value)
    assert not artifact.exists()
    assert not sidecar.exists()


def test_sidecar_placement_failure_removes_only_current_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = decision()
    real_link = os.link
    calls = 0

    def fail_second_link(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated sidecar placement failure")
        real_link(source, target)

    monkeypatch.setattr(os, "link", fail_second_link)
    with pytest.raises(PreservationBaselineAuthorizationPersistenceError) as captured:
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=tmp_path,
        )

    assert captured.value.__cause__ is not None
    artifact, sidecar = expected_paths(tmp_path, value)
    assert not artifact.exists()
    assert not sidecar.exists()
    assert not list(tmp_path.glob(".*.tmp"))


def test_first_persistence_fsyncs_staged_files_and_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    synchronized_types: list[str] = []
    real_fsync = os.fsync

    def record_fsync(descriptor: int) -> None:
        mode = os.fstat(descriptor).st_mode
        synchronized_types.append("directory" if stat.S_ISDIR(mode) else "file")
        real_fsync(descriptor)

    monkeypatch.setattr(os, "fsync", record_fsync)
    PreservationBaselineAuthorizationStore().persist(
        decision=decision(),
        destination_directory=tmp_path,
    )

    assert synchronized_types == ["file", "directory", "file", "directory"]


def test_staged_file_fsync_failure_leaves_no_final_pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = decision()

    def fail_fsync(descriptor: int) -> None:
        del descriptor
        raise OSError("simulated fsync failure")

    monkeypatch.setattr(os, "fsync", fail_fsync)
    with pytest.raises(PreservationBaselineAuthorizationPersistenceError) as captured:
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=tmp_path,
        )

    assert captured.value.__cause__ is not None
    artifact, sidecar = expected_paths(tmp_path, value)
    assert not artifact.exists()
    assert not sidecar.exists()
    assert not list(tmp_path.glob(".*.tmp"))


def test_cleanup_failure_is_preserved_as_causal_persistence_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = decision()
    real_link = os.link
    calls = 0

    def fail_second_link(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated sidecar failure")
        real_link(source, target)

    monkeypatch.setattr(os, "link", fail_second_link)
    monkeypatch.setattr(
        persistence_module,
        "_cleanup_created",
        lambda **kwargs: OSError("simulated cleanup failure"),
    )

    with pytest.raises(
        PreservationBaselineAuthorizationPersistenceError,
        match="cleanup also failed",
    ) as captured:
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=tmp_path,
        )

    assert isinstance(captured.value.__cause__, OSError)


def test_concurrent_identical_pair_resolves_as_exact_replay(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = decision()
    artifact, sidecar = expected_paths(tmp_path, value)
    content = PreservationBaselineAuthorizationSerializer().serialize(value)
    digest = hashlib.sha256(content).hexdigest()
    real_link = os.link
    raced = False

    def create_identical_pair_then_conflict(source: Path, target: Path) -> None:
        nonlocal raced
        if not raced:
            raced = True
            artifact.write_bytes(content)
            sidecar.write_text(f"{digest}  {artifact.name}\n", encoding="ascii")
            raise FileExistsError(target)
        real_link(source, target)

    monkeypatch.setattr(os, "link", create_identical_pair_then_conflict)
    result = PreservationBaselineAuthorizationStore().persist(
        decision=value,
        destination_directory=tmp_path,
    )

    assert result.idempotent_replay is True
    assert artifact.read_bytes() == content
    assert sidecar.read_text(encoding="ascii") == f"{digest}  {artifact.name}\n"
    assert not list(tmp_path.glob(".*.tmp"))


def test_concurrent_differing_pair_is_preserved_as_conflict(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = decision()
    artifact, sidecar = expected_paths(tmp_path, value)
    contradictory = b"contradictory\n"

    def create_different_pair_then_conflict(source: Path, target: Path) -> None:
        del source
        artifact.write_bytes(contradictory)
        sidecar.write_text(f"{'c' * 64}  {artifact.name}\n", encoding="ascii")
        raise FileExistsError(target)

    monkeypatch.setattr(os, "link", create_different_pair_then_conflict)
    with pytest.raises(PreservationBaselineAuthorizationConflictError):
        PreservationBaselineAuthorizationStore().persist(
            decision=value,
            destination_directory=tmp_path,
        )

    assert artifact.read_bytes() == contradictory
    assert sidecar.read_text(encoding="ascii") == f"{'c' * 64}  {artifact.name}\n"
    assert not list(tmp_path.glob(".*.tmp"))


def test_persistence_does_not_read_or_modify_source_content(tmp_path: Path) -> None:
    value = decision()
    source = tmp_path / "source.txt"
    source.write_bytes(b"preserve exactly")
    before = source.stat()

    PreservationBaselineAuthorizationStore().persist(
        decision=value,
        destination_directory=tmp_path / "authorization-evidence",
    )

    after = source.stat()
    assert source.read_bytes() == b"preserve exactly"
    assert after.st_size == before.st_size
    assert after.st_mtime_ns == before.st_mtime_ns
