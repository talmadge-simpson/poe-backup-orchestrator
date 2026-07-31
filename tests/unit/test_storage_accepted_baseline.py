"""Tests for accepted-preservation-baseline construction and publication."""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest
from test_storage_accepted_baseline_models import (
    authorization_decision,
    persisted_authorization,
)
from test_storage_baseline_authorization import assemble, recommendation

from poe_backup_orchestrator.models.storage_accepted_baseline import (
    AcceptedPreservationBaselineMode,
)
from poe_backup_orchestrator.models.storage_baseline_acceptance import AcceptanceDecision
from poe_backup_orchestrator.models.storage_baseline_authorization import (
    AuthorizationConditionDecision,
    AuthorizationConditionDisposition,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    PilotAuthorization,
)
from poe_backup_orchestrator.services import storage_accepted_baseline as publication_module
from poe_backup_orchestrator.services.storage_accepted_baseline import (
    AcceptedPreservationBaselineConflictError,
    AcceptedPreservationBaselineConstructionError,
    AcceptedPreservationBaselineConstructor,
    AcceptedPreservationBaselineLockError,
    AcceptedPreservationBaselinePublicationError,
    AcceptedPreservationBaselinePublisher,
    AcceptedPreservationBaselineSerializer,
    PersistedAuthorizationVerificationError,
)
from poe_backup_orchestrator.services.storage_baseline_authorization import (
    PreservationBaselineAuthorizationDecisionAssembler,
)
from poe_backup_orchestrator.services.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationStore,
)
from poe_backup_orchestrator.utilities.locking import exclusive_file_lock


def rejected_persistence(tmp_path: Path):
    original = authorization_decision()
    rejected = PreservationBaselineAuthorizationDecisionAssembler().assemble(
        recommendation=original.recommendation,
        outcome=AuthorizationDecisionOutcome.REJECT,
        authority=original.authority,
        decided_at_utc=original.decided_at_utc,
        condition_decisions=(),
        scope=AuthorizationScope(
            accepted_source_root_ids=(),
            excluded_source_root_ids=("root-a",),
            scope_limitations=(),
        ),
        pilot=None,
        retention_obligations=original.retention_obligations,
        supersession_eligible=original.supersession_eligible,
        rationale="Explicit human rejection.",
    )
    return PreservationBaselineAuthorizationStore().persist(
        decision=rejected, destination_directory=tmp_path / "authorization"
    )


def publication_paths(destination: Path, accepted_id: str) -> tuple[Path, ...]:
    full = destination / f"accepted-preservation-baseline-{accepted_id}.json"
    reference = destination / (f"accepted-preservation-baseline-reference-{accepted_id}.json")
    return full, Path(f"{full}.sha256"), reference, Path(f"{reference}.sha256")


def test_constructor_requires_exact_persistence_result() -> None:
    with pytest.raises(PersistedAuthorizationVerificationError, match="persistence_result"):
        AcceptedPreservationBaselineConstructor().construct({})  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("outcome", "mode"),
    (
        (AuthorizationDecisionOutcome.AUTHORIZE, AcceptedPreservationBaselineMode.STRICT),
        (
            AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS,
            AcceptedPreservationBaselineMode.APPROVED_EXCEPTIONS,
        ),
        (
            AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE,
            AcceptedPreservationBaselineMode.PARTIAL_SOURCE,
        ),
        (AuthorizationDecisionOutcome.AUTHORIZE_PILOT, AcceptedPreservationBaselineMode.PILOT),
    ),
)
def test_eligible_outcome_mapping_is_exact(outcome, mode) -> None:
    assert publication_module._mode_for_outcome(outcome) is mode


@pytest.mark.parametrize(
    ("outcome", "expected_mode"),
    (
        (AuthorizationDecisionOutcome.AUTHORIZE, AcceptedPreservationBaselineMode.STRICT),
        (
            AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS,
            AcceptedPreservationBaselineMode.APPROVED_EXCEPTIONS,
        ),
        (
            AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE,
            AcceptedPreservationBaselineMode.PARTIAL_SOURCE,
        ),
        (AuthorizationDecisionOutcome.AUTHORIZE_PILOT, AcceptedPreservationBaselineMode.PILOT),
    ),
)
def test_every_eligible_typed_authorization_constructs_exact_mode(
    tmp_path: Path,
    outcome: AuthorizationDecisionOutcome,
    expected_mode: AcceptedPreservationBaselineMode,
) -> None:
    if outcome is AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS:
        recommendation_value = recommendation(AcceptanceDecision.RECOMMEND_REVIEW)
        decision = assemble(
            recommendation_value,
            outcome=outcome,
            condition_decisions=(
                AuthorizationConditionDecision(
                    condition_sequence=1,
                    condition_code="exception_review",
                    disposition=AuthorizationConditionDisposition.APPROVED,
                    rationale="Approved exception.",
                ),
            ),
        )
    elif outcome is AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE:
        recommendation_value = recommendation(
            AcceptanceDecision.RECOMMEND_ACCEPTANCE, roots=("root-a", "root-b")
        )
        decision = assemble(
            recommendation_value,
            outcome=outcome,
            scope=AuthorizationScope(
                accepted_source_root_ids=("root-a",),
                excluded_source_root_ids=("root-b",),
                scope_limitations=("root-b remains excluded",),
            ),
        )
    elif outcome is AuthorizationDecisionOutcome.AUTHORIZE_PILOT:
        recommendation_value = recommendation(AcceptanceDecision.RECOMMEND_ACCEPTANCE)
        decision = assemble(
            recommendation_value,
            outcome=outcome,
            pilot=PilotAuthorization(
                purpose="Validate later analytical consumption",
                limitations=("No migration authority",),
            ),
        )
    else:
        decision = assemble(
            recommendation(AcceptanceDecision.RECOMMEND_ACCEPTANCE), outcome=outcome
        )
    persisted = PreservationBaselineAuthorizationStore().persist(
        decision=decision,
        destination_directory=tmp_path / outcome.value,
    )

    baseline = AcceptedPreservationBaselineConstructor().construct(persisted)

    assert baseline.mode is expected_mode
    assert baseline.authorization_decision == decision
    assert baseline.accepted_source_root_ids == decision.scope.accepted_source_root_ids
    assert baseline.excluded_source_root_ids == decision.scope.excluded_source_root_ids


def test_rejected_authorization_creates_no_publication_destination(tmp_path: Path) -> None:
    result = rejected_persistence(tmp_path)
    destination = tmp_path / "must-not-exist"

    with pytest.raises(AcceptedPreservationBaselineConstructionError, match="rejected"):
        AcceptedPreservationBaselinePublisher().publish(
            persistence_result=result, destination_directory=destination
        )

    assert not destination.exists()


@pytest.mark.parametrize(
    "mutation",
    ("missing", "symlink", "directory", "bytes", "sidecar", "byte_count", "digest"),
)
def test_authorization_verification_fails_before_publication_mutation(
    tmp_path: Path, mutation: str
) -> None:
    result = persisted_authorization(tmp_path)
    artifact = result.artifact
    if mutation == "missing":
        artifact.evidence_path.unlink()
    elif mutation == "symlink":
        content = artifact.evidence_path.read_bytes()
        artifact.evidence_path.unlink()
        underlying = tmp_path / "underlying"
        underlying.write_bytes(content)
        artifact.evidence_path.symlink_to(underlying)
    elif mutation == "directory":
        artifact.sha256_path.unlink()
        artifact.sha256_path.mkdir()
    elif mutation == "bytes":
        artifact.evidence_path.write_bytes(b"contradictory\n")
    elif mutation == "sidecar":
        artifact.sha256_path.write_text("malformed\n", encoding="ascii")
    elif mutation == "byte_count":
        result = replace(result, artifact=replace(artifact, byte_count=artifact.byte_count + 1))
    else:
        result = replace(result, artifact=replace(artifact, sha256="0" * 64))
    destination = tmp_path / "publication"

    with pytest.raises(PersistedAuthorizationVerificationError):
        AcceptedPreservationBaselinePublisher().publish(
            persistence_result=result, destination_directory=destination
        )

    assert not destination.exists()


@pytest.mark.parametrize("fault", ("unknown", "missing", "wrong_type", "duplicate"))
def test_strict_authorization_decoder_rejects_schema_faults(tmp_path: Path, fault: str) -> None:
    result = persisted_authorization(tmp_path)
    artifact = result.artifact
    payload = json.loads(artifact.evidence_path.read_bytes())
    if fault == "unknown":
        payload["unknown"] = True
        content = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    elif fault == "missing":
        del payload["scope"]
        content = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    elif fault == "wrong_type":
        payload["supersession_eligible"] = 1
        content = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    else:
        original = artifact.evidence_path.read_text()
        content = original.replace(
            '"supersession_eligible":true',
            '"supersession_eligible":true,"supersession_eligible":true',
        ).encode()
    digest = hashlib.sha256(content).hexdigest()
    artifact.evidence_path.write_bytes(content)
    artifact.sha256_path.write_text(f"{digest}  {artifact.evidence_path.name}\n", encoding="ascii")
    result = replace(
        result,
        artifact=replace(artifact, sha256=digest, byte_count=len(content)),
    )

    with pytest.raises(PersistedAuthorizationVerificationError):
        AcceptedPreservationBaselineConstructor().construct(result)


def test_noncanonical_authorization_bytes_are_rejected(tmp_path: Path) -> None:
    result = persisted_authorization(tmp_path)
    artifact = result.artifact
    payload = json.loads(artifact.evidence_path.read_bytes())
    content = json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"
    digest = hashlib.sha256(content).hexdigest()
    artifact.evidence_path.write_bytes(content)
    artifact.sha256_path.write_text(f"{digest}  {artifact.evidence_path.name}\n", encoding="ascii")
    result = replace(result, artifact=replace(artifact, sha256=digest, byte_count=len(content)))

    with pytest.raises(PersistedAuthorizationVerificationError, match="canonical"):
        AcceptedPreservationBaselineConstructor().construct(result)


def test_first_publication_creates_four_restricted_files_and_reference_last(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = persisted_authorization(tmp_path)
    destination = tmp_path / "publication"
    placements: list[str] = []
    original = publication_module._persist_exclusively

    def recording_placement(path: Path, content: bytes) -> None:
        placements.append(path.name)
        original(path, content)

    monkeypatch.setattr(publication_module, "_persist_exclusively", recording_placement)
    publication = AcceptedPreservationBaselinePublisher().publish(
        persistence_result=result, destination_directory=destination
    )
    paths = publication_paths(destination, publication.accepted_baseline_id)

    assert all(path.is_file() for path in paths)
    assert placements == [path.name for path in paths]
    assert placements[-1].startswith("accepted-preservation-baseline-reference-")
    assert placements[-1].endswith(".json.sha256")
    assert all(path.stat().st_mode & 0o777 == 0o640 for path in paths)
    assert publication.idempotent_replay is False
    assert not list(destination.glob("*.tmp"))
    assert not list(destination.glob(".*.tmp"))


def test_serialization_is_canonical_complete_and_deterministic(tmp_path: Path) -> None:
    baseline = AcceptedPreservationBaselineConstructor().construct(
        persisted_authorization(tmp_path)
    )
    serializer = AcceptedPreservationBaselineSerializer()
    first = serializer.serialize(baseline)

    assert first == serializer.serialize(baseline)
    assert first.endswith(b"\n") and not first.endswith(b"\n\n")
    payload = json.loads(first)
    assert payload["authorization_decision"]["identity"]["authorization_id"] == (
        baseline.identity.authorization_id
    )
    assert payload["accepted_evidence_graph"][0]["source_root_id"] == "root-a"


def test_identical_replay_verifies_all_four_without_rewrite(tmp_path: Path) -> None:
    result = persisted_authorization(tmp_path)
    destination = tmp_path / "publication"
    publisher = AcceptedPreservationBaselinePublisher()
    first = publisher.publish(persistence_result=result, destination_directory=destination)
    paths = publication_paths(destination, first.accepted_baseline_id)
    stats = tuple(path.stat().st_mtime_ns for path in paths)
    second = publisher.publish(persistence_result=result, destination_directory=destination)

    assert second.idempotent_replay is True
    assert tuple(path.stat().st_mtime_ns for path in paths) == stats


@pytest.mark.parametrize("sidecar_index", (1, 3), ids=("baseline", "reference"))
@pytest.mark.parametrize(
    "malformation",
    ("wrong_filename", "uppercase_digest", "wrong_separator", "extra_line", "no_newline"),
)
def test_replay_rejects_malformed_publication_sidecars_without_mutation(
    tmp_path: Path,
    sidecar_index: int,
    malformation: str,
) -> None:
    result = persisted_authorization(tmp_path)
    destination = tmp_path / "publication"
    publisher = AcceptedPreservationBaselinePublisher()
    publication = publisher.publish(persistence_result=result, destination_directory=destination)
    paths = publication_paths(destination, publication.accepted_baseline_id)
    sidecar = paths[sidecar_index]
    artifact = paths[sidecar_index - 1]
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if malformation == "wrong_filename":
        malformed = f"{digest}  wrong.json\n".encode("ascii")
    elif malformation == "uppercase_digest":
        malformed = f"{digest.upper()}  {artifact.name}\n".encode("ascii")
    elif malformation == "wrong_separator":
        malformed = f"{digest} {artifact.name}\n".encode("ascii")
    elif malformation == "extra_line":
        malformed = f"{digest}  {artifact.name}\nextra\n".encode("ascii")
    else:
        malformed = f"{digest}  {artifact.name}".encode("ascii")
    sidecar.write_bytes(malformed)
    before = tuple(path.read_bytes() for path in paths)

    with pytest.raises(AcceptedPreservationBaselineConflictError):
        publisher.publish(persistence_result=result, destination_directory=destination)

    assert tuple(path.read_bytes() for path in paths) == before


@pytest.mark.parametrize("mask", range(1, 16))
def test_every_partial_or_preexisting_publication_permutation_fails_closed(
    tmp_path: Path, mask: int
) -> None:
    result = persisted_authorization(tmp_path)
    constructor = AcceptedPreservationBaselineConstructor()
    accepted_id = constructor.construct(result).identity.accepted_baseline_id
    destination = tmp_path / "publication"
    destination.mkdir()
    paths = publication_paths(destination, accepted_id)
    for index, path in enumerate(paths):
        if mask & (1 << index):
            path.write_bytes(b"preexisting\n")

    with pytest.raises(AcceptedPreservationBaselineConflictError):
        AcceptedPreservationBaselinePublisher().publish(
            persistence_result=result, destination_directory=destination
        )

    for index, path in enumerate(paths):
        assert path.exists() is bool(mask & (1 << index))


@pytest.mark.parametrize("target_index", range(4))
def test_links_and_nonregular_publication_targets_fail_closed(
    tmp_path: Path, target_index: int
) -> None:
    result = persisted_authorization(tmp_path)
    baseline = AcceptedPreservationBaselineConstructor().construct(result)
    destination = tmp_path / "publication"
    destination.mkdir()
    paths = publication_paths(destination, baseline.identity.accepted_baseline_id)
    for index, path in enumerate(paths):
        if index == target_index:
            path.mkdir()
        else:
            path.write_bytes(b"existing\n")

    with pytest.raises(AcceptedPreservationBaselineConflictError):
        AcceptedPreservationBaselinePublisher().publish(
            persistence_result=result, destination_directory=destination
        )


def test_reference_is_sole_verified_downstream_boundary(tmp_path: Path) -> None:
    result = persisted_authorization(tmp_path)
    publisher = AcceptedPreservationBaselinePublisher()
    publication = publisher.publish(
        persistence_result=result, destination_directory=tmp_path / "publication"
    )
    loaded = publisher.load_from_reference(publication.reference_artifact)

    assert loaded.identity.accepted_baseline_id == publication.accepted_baseline_id
    with pytest.raises(AcceptedPreservationBaselinePublicationError, match="reference_artifact"):
        publisher.load_from_reference(loaded)  # type: ignore[arg-type]


def test_downstream_reference_detects_full_artifact_and_metadata_conflicts(
    tmp_path: Path,
) -> None:
    result = persisted_authorization(tmp_path)
    publisher = AcceptedPreservationBaselinePublisher()
    publication = publisher.publish(
        persistence_result=result, destination_directory=tmp_path / "publication"
    )
    publication.accepted_baseline_artifact.evidence_path.write_bytes(b"changed\n")

    with pytest.raises(AcceptedPreservationBaselineConflictError):
        publisher.load_from_reference(publication.reference_artifact)


def test_identical_concurrent_publication_is_first_plus_lock_contention(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = persisted_authorization(tmp_path)
    destination = tmp_path / "publication"
    first_placement_entered = threading.Event()
    release_first_placement = threading.Event()
    original = publication_module._persist_exclusively
    placement_calls = 0

    def hold_first_placement(path: Path, content: bytes) -> None:
        nonlocal placement_calls
        placement_calls += 1
        if placement_calls == 1:
            first_placement_entered.set()
            assert release_first_placement.wait(timeout=5)
        original(path, content)

    monkeypatch.setattr(publication_module, "_persist_exclusively", hold_first_placement)

    def publish():
        return AcceptedPreservationBaselinePublisher().publish(
            persistence_result=result, destination_directory=destination
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(publish)
        assert first_placement_entered.wait(timeout=5)
        second = pool.submit(publish)
        with pytest.raises(AcceptedPreservationBaselineLockError) as captured:
            second.result()
        release_first_placement.set()
        publication = first.result()

    assert publication.idempotent_replay is False
    assert captured.value.__cause__ is not None


def test_lock_contention_preserves_publication_absence(tmp_path: Path) -> None:
    result = persisted_authorization(tmp_path)
    destination = tmp_path / "publication"
    lock_path = destination / ".locks" / ("accepted-preservation-baseline-publication.lock")

    with exclusive_file_lock(lock_path):
        with pytest.raises(AcceptedPreservationBaselineLockError) as captured:
            AcceptedPreservationBaselinePublisher().publish(
                persistence_result=result, destination_directory=destination
            )

    assert captured.value.__cause__ is not None
    assert not list(destination.glob("*.json"))


def test_failed_attempt_cleans_only_files_it_created(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = persisted_authorization(tmp_path)
    destination = tmp_path / "publication"
    destination.mkdir()
    unrelated = destination / "unrelated"
    unrelated.write_text("preserve")
    original = publication_module._persist_exclusively
    calls = 0

    def fail_third(path: Path, content: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 3:
            raise OSError("injected placement failure")
        original(path, content)

    monkeypatch.setattr(publication_module, "_persist_exclusively", fail_third)
    with pytest.raises(AcceptedPreservationBaselinePublicationError) as captured:
        AcceptedPreservationBaselinePublisher().publish(
            persistence_result=result, destination_directory=destination
        )

    assert captured.value.__cause__ is not None
    assert unrelated.read_text() == "preserve"
    assert not list(destination.glob("*.json"))
    assert not list(destination.glob("*.sha256"))


def test_directory_fsync_occurs_once_after_each_placement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = persisted_authorization(tmp_path)
    synchronized: list[Path] = []
    monkeypatch.setattr(
        publication_module, "_fsync_directory", lambda path: synchronized.append(path)
    )
    destination = tmp_path / "publication"

    AcceptedPreservationBaselinePublisher().publish(
        persistence_result=result, destination_directory=destination
    )

    assert synchronized == [destination] * 4


def test_no_excluded_authority_or_public_verified_model() -> None:
    source = Path("src/poe_backup_orchestrator/services/storage_accepted_baseline.py").read_text()

    assert "VerifiedPreservationBaselineAuthorizationEvidence" not in source
    for prohibited in (
        "migration_plan",
        "delete_source",
        "redirect_client",
        "supersession_record",
        "argparse",
        "click.command",
        "requests.",
    ):
        assert prohibited not in source
    assert not hasattr(publication_module, "VerifiedPreservationBaselineAuthorizationEvidence")
