"""Tests for Slice 6C-1 reference-first analytical intake."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from poe_backup_orchestrator.models.storage_accepted_baseline import (
    AcceptedPreservationBaselineArtifact,
)
from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
    AcceptanceDecision,
    AcceptanceEvaluationIdentity,
    AcceptanceMode,
    PreservationBaselineAcceptanceRecommendation,
    stable_preservation_baseline_acceptance_evaluation_id,
)
from poe_backup_orchestrator.models.storage_baseline_analysis import (
    STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION,
    AcceptedBaselineAnalysisEvidenceStatus,
    AcceptedBaselineAnalysisProfileIdentity,
    stable_accepted_baseline_analysis_profile_id,
)
from poe_backup_orchestrator.models.storage_baseline_authorization import (
    AuthorizationAuthority,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
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
from poe_backup_orchestrator.models.storage_baseline_manifest import InventoryTotals
from poe_backup_orchestrator.models.storage_baseline_validation import (
    STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
    EvidenceValidationStatus,
    PreservationBaselineValidationIdentity,
    PreservationBaselineValidationResult,
    ValidatedEvidenceReference,
    stable_preservation_baseline_validation_id,
)
from poe_backup_orchestrator.models.storage_content_integrity import (
    STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
    ContentIntegrityOutcome,
    ContentIntegrityTotals,
    ContentIntegrityVerificationResult,
    FileIntegrityEvidence,
    SourceFileObservation,
)
from poe_backup_orchestrator.models.storage_inventory import (
    FileInventoryRecord,
    InventoryCaptureStatus,
    InventoryItemIdentity,
    InventoryItemType,
    InventoryMetadata,
)
from poe_backup_orchestrator.models.storage_inventory_assembly import (
    AssembledInventoryItem,
    InventoryAssemblyResult,
    stable_inventory_item_id,
)
from poe_backup_orchestrator.services import storage_baseline_analysis as analysis_module
from poe_backup_orchestrator.services.storage_accepted_baseline import (
    AcceptedPreservationBaselineConstructor,
    AcceptedPreservationBaselinePublicationError,
    AcceptedPreservationBaselinePublisher,
)
from poe_backup_orchestrator.services.storage_baseline_analysis import (
    AcceptedBaselineAnalysisIntakeService,
    AcceptedBaselineEvidenceAuthenticationError,
    AcceptedBaselineReferenceVerificationError,
)
from poe_backup_orchestrator.services.storage_baseline_authorization import (
    PreservationBaselineAuthorizationDecisionAssembler,
)
from poe_backup_orchestrator.services.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationStore,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    PreservationBaselineValidationError,
    ValidationAdapterRegistry,
)
from poe_backup_orchestrator.services.storage_content_integrity_persistence import (
    ContentIntegrityEvidencePersistence,
)
from poe_backup_orchestrator.services.storage_inventory_persistence import InventoryEvidenceStore

NOW = datetime(2026, 7, 31, 18, 0, tzinfo=UTC)


class StubPublisher(AcceptedPreservationBaselinePublisher):
    def __init__(self, baseline):
        super().__init__()
        self.baseline = baseline
        self.calls = 0

    def load_from_reference(self, reference_artifact):
        self.calls += 1
        return self.baseline


class FailingPublisher(AcceptedPreservationBaselinePublisher):
    def load_from_reference(self, reference_artifact):
        raise AcceptedPreservationBaselinePublicationError("synthetic reference failure")


def _bundle(tmp_path: Path):
    identity = InventoryItemIdentity(
        baseline_id="baseline-a",
        capture_session_id="capture-a",
        source_device_id="device-a",
        source_volume_id="volume-a",
        source_root_id="root-a",
        relative_path=Path("documents/file.txt"),
        item_type=InventoryItemType.FILE,
    )
    item_id = stable_inventory_item_id(identity)
    record = FileInventoryRecord(
        identity=identity,
        size_bytes=10,
        sha256=None,
        metadata=InventoryMetadata(None, NOW, None, "owner-a", "0640"),
        capture_status=InventoryCaptureStatus.PENDING,
    )
    inventory = InventoryAssemblyResult(
        discovery_request_id="discovery-a",
        source_root_id="root-a",
        items=(AssembledInventoryItem(item_id, record),),
        unsupported_items=(),
        totals=InventoryTotals(0, 1, 0, 0, 0, 10, 0, 0, 0, 0, 1),
        exception_summaries=(),
    )
    inventory_publication = InventoryEvidenceStore().publish(
        result=inventory,
        evidence_path=(tmp_path / "inventory" / "inventory-evidence.ndjson"),
    )
    observation = SourceFileObservation(10, 1, 0o100640, 1, 2)
    integrity = ContentIntegrityVerificationResult(
        schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
        source_root_id="root-a",
        verification_started_at_utc=NOW,
        verification_completed_at_utc=NOW,
        evidence=(
            FileIntegrityEvidence(
                schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
                item_id=item_id,
                relative_path=Path("documents/file.txt"),
                expected_size_bytes=10,
                observed_size_bytes=10,
                expected_sha256="a" * 64,
                observed_sha256="a" * 64,
                verification_started_at_utc=NOW,
                verification_completed_at_utc=NOW,
                outcome=ContentIntegrityOutcome.VERIFIED,
                source_observation_before=observation,
                source_observation_after=observation,
            ),
        ),
        totals=ContentIntegrityTotals(1, 1, 0, 0, 0, 0, 0, 0, 0, 10, 10),
    )
    integrity_publication = ContentIntegrityEvidencePersistence().persist(
        destination_directory=tmp_path / "integrity",
        result=integrity,
    )
    references = (
        PreservationEvidenceReference(
            PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            "root-a",
            "1.0",
            integrity_publication.evidence_path,
            integrity_publication.digest_path,
            integrity_publication.sha256,
            integrity_publication.byte_count,
        ),
        PreservationEvidenceReference(
            PreservationEvidenceType.INVENTORY_EVIDENCE,
            "root-a",
            "1.0",
            inventory_publication.evidence_path,
            inventory_publication.sha256_path,
            inventory_publication.sha256,
            inventory_publication.byte_count,
        ),
    )
    observations = (
        EvidenceRequirementObservation(
            "root-a",
            PreservationEvidenceType.BASELINE_MANIFEST,
            EvidenceRequirementStatus.NOT_APPLICABLE,
            None,
            "No manifest artifact is opened by analytical intake.",
        ),
        *(
            EvidenceRequirementObservation(
                "root-a", ref.evidence_type, EvidenceRequirementStatus.PRESENT, ref
            )
            for ref in references
        ),
    )
    candidate = PreservationBaselineCandidate(
        PreservationBaselineCandidateIdentity(
            STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
            "pbc-" + "b" * 64,
            "baseline-a",
            NOW,
        ),
        PreservationBaselineCandidateScope("baseline-a", ("root-a",)),
        observations,
    )
    validated = tuple(
        ValidatedEvidenceReference(
            ref,
            EvidenceValidationStatus.VERIFIED,
            ref.sha256,
            ref.byte_count,
            ref.sha256,
            (
                "poe.storage.inventory-evidence"
                if ref.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
                else "poe.storage.content-integrity-evidence"
            ),
            "1.0",
        )
        for ref in references
    )
    validation_id = stable_preservation_baseline_validation_id(
        candidate_id=candidate.identity.candidate_id,
        policy_profile_id="strict-validation-v1",
        validated_evidence=validated,
        findings=(),
    )
    validation = PreservationBaselineValidationResult(
        PreservationBaselineValidationIdentity(
            STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION,
            validation_id,
            candidate.identity.candidate_id,
            "baseline-a",
            NOW,
        ),
        candidate,
        "strict-validation-v1",
        validated,
        (),
    )
    rationale = ("no_validation_findings", "recommend_acceptance")
    evaluation_id = stable_preservation_baseline_acceptance_evaluation_id(
        validation_id=validation_id,
        candidate_id=candidate.identity.candidate_id,
        baseline_id="baseline-a",
        policy_id="baseline-acceptance",
        policy_version="1.0",
        mode=AcceptanceMode.REVIEW_PERMITTED,
        conditions=(),
        decision=AcceptanceDecision.RECOMMEND_ACCEPTANCE,
        rationale_codes=rationale,
    )
    recommendation = PreservationBaselineAcceptanceRecommendation(
        AcceptanceEvaluationIdentity(
            STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION,
            evaluation_id,
            validation_id,
            candidate.identity.candidate_id,
            "baseline-a",
            "baseline-acceptance",
            "1.0",
        ),
        validation,
        AcceptanceMode.REVIEW_PERMITTED,
        AcceptanceDecision.RECOMMEND_ACCEPTANCE,
        (),
        rationale,
    )
    decision = PreservationBaselineAuthorizationDecisionAssembler().assemble(
        recommendation=recommendation,
        outcome=AuthorizationDecisionOutcome.AUTHORIZE,
        authority=AuthorizationAuthority(
            "authority-a", "Owner", "Repository Owner", "Explicit synthetic authority"
        ),
        decided_at_utc=NOW,
        condition_decisions=(),
        scope=AuthorizationScope(("root-a",), (), ()),
        pilot=None,
        retention_obligations=("retain",),
        supersession_eligible=True,
        rationale="Synthetic authorization for unit testing.",
    )
    persisted = PreservationBaselineAuthorizationStore().persist(
        decision=decision,
        destination_directory=tmp_path / "authorization",
    )
    baseline = AcceptedPreservationBaselineConstructor().construct(persisted)
    artifact = AcceptedPreservationBaselineArtifact(
        tmp_path / "reference.json",
        tmp_path / "reference.json.sha256",
        "c" * 64,
        100,
    )
    publisher = StubPublisher(baseline)
    return AcceptedBaselineAnalysisIntakeService(publisher=publisher), artifact, baseline


def _profile_with(profile, **changes):
    values = {
        field: getattr(profile, field)
        for field in (
            "profile_version",
            "resource_profile_version",
            "evidence_rules",
            "missing_evidence_behavior",
            "unsupported_evidence_behavior",
            "adapter_registry_id",
            "fact_projection_id",
            "maximum_inventory_evidence_bytes",
            "maximum_content_integrity_evidence_bytes",
            "maximum_inventory_items_per_root",
            "maximum_integrity_observations_per_root",
            "maximum_aggregate_evidence_bytes",
            "maximum_aggregate_projected_items",
            "maximum_inventory_ndjson_record_bytes",
            "json_nesting_depth_limit",
            "deterministic_ordering",
        )
    }
    values.update(changes)
    identity = stable_accepted_baseline_analysis_profile_id(**values)
    return replace(
        profile,
        identity=AcceptedBaselineAnalysisProfileIdentity(
            STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION,
            identity,
        ),
        **changes,
    )


def _reference(baseline, evidence_type):
    reference = next(
        item.evidence_reference
        for item in baseline.accepted_evidence_graph
        if item.evidence_type is evidence_type
    )
    assert reference is not None
    return reference


def _replace_evidence_bytes(reference, content: bytes) -> None:
    digest = hashlib.sha256(content).hexdigest()
    reference.evidence_path.write_bytes(content)
    sidecar = (
        f"{digest}  {reference.evidence_path.name}\n"
        if reference.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
        else f"{digest}\n"
    )
    reference.digest_path.write_text(sidecar, encoding="ascii")
    object.__setattr__(reference, "sha256", digest)
    object.__setattr__(reference, "byte_count", len(content))


def _canonical_document(reference) -> object:
    if reference.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        return [json.loads(line) for line in reference.evidence_path.read_text().splitlines()]
    return json.loads(reference.evidence_path.read_text())


def _write_canonical_document(reference, value: object) -> None:
    if reference.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        content = b"".join(
            json.dumps(item, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
            + b"\n"
            for item in value
        )
    else:
        content = (
            json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
        ).encode()
    _replace_evidence_bytes(reference, content)


def test_reference_first_authentication_constructs_complete_deterministic_context(
    tmp_path: Path,
) -> None:
    service, artifact, baseline = _bundle(tmp_path)

    first = service.build_context(artifact)
    second = service.build_context(artifact)

    assert first == second
    assert service.publisher.calls == 2
    assert first.accepted_baseline == baseline
    assert first.identity.analysis_context_id.startswith("pbac-")
    assert [item.observation.evidence_type for item in first.authenticated_evidence] == [
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
        PreservationEvidenceType.INVENTORY_EVIDENCE,
    ]
    assert (
        first.lineage_only_evidence[0].status is AcceptedBaselineAnalysisEvidenceStatus.LINEAGE_ONLY
    )
    assert first.accepted_baseline.retention_obligations == ("retain",)
    assert first.accepted_baseline.supersession_eligible is True


def test_reference_failure_is_wrapped_and_no_evidence_is_opened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, artifact, _ = _bundle(tmp_path)
    opened = False

    def forbidden(*args, **kwargs):
        nonlocal opened
        opened = True
        raise AssertionError("evidence opened")

    monkeypatch.setattr(analysis_module, "_read_regular", forbidden)
    service = AcceptedBaselineAnalysisIntakeService(publisher=FailingPublisher())
    with pytest.raises(AcceptedBaselineReferenceVerificationError) as raised:
        service.build_context(artifact)

    assert isinstance(raised.value.__cause__, AcceptedPreservationBaselinePublicationError)
    assert not opened


def test_wrong_public_input_fails_before_loader() -> None:
    service = AcceptedBaselineAnalysisIntakeService()
    with pytest.raises(AcceptedBaselineReferenceVerificationError):
        service.build_context({})  # type: ignore[arg-type]


@pytest.mark.parametrize("evidence_type", ("inventory", "integrity"))
def test_malformed_producer_sidecar_fails_closed(tmp_path: Path, evidence_type: str) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    selected_type = (
        PreservationEvidenceType.INVENTORY_EVIDENCE
        if evidence_type == "inventory"
        else PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE
    )
    observation = next(
        item for item in baseline.accepted_evidence_graph if item.evidence_type is selected_type
    )
    reference = observation.evidence_reference
    assert reference is not None
    reference.digest_path.write_text(reference.sha256.upper() + "\n", encoding="ascii")

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="sidecar"):
        service.build_context(artifact)


def test_valid_hard_link_count_is_recorded_not_rejected(tmp_path: Path) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    reference = next(
        item.evidence_reference
        for item in baseline.accepted_evidence_graph
        if item.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
    )
    assert reference is not None
    os.link(reference.evidence_path, tmp_path / "inventory-hard-link")

    context = service.build_context(artifact)

    inventory = next(
        item
        for item in context.authenticated_evidence
        if item.observation.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
    )
    assert inventory.artifact_link_count == 2


def test_declared_artifact_limit_fails_before_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, _ = _bundle(tmp_path)
    service.profile = _profile_with(service.profile, maximum_inventory_evidence_bytes=1)
    opened: list[Path] = []
    original = analysis_module._read_regular

    def observed(path, **kwargs):
        opened.append(path)
        return original(path, **kwargs)

    monkeypatch.setattr(analysis_module, "_read_regular", observed)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="byte count"):
        service.build_context(artifact)

    assert all("inventory-evidence" not in path.name for path in opened)


def test_inventory_record_limit_fails_before_json_projection(tmp_path: Path) -> None:
    service, artifact, _ = _bundle(tmp_path)
    service.profile = _profile_with(service.profile, maximum_inventory_ndjson_record_bytes=10)

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="record"):
        service.build_context(artifact)


def test_symlink_and_directory_evidence_fail_closed(tmp_path: Path) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    reference = next(
        item.evidence_reference
        for item in baseline.accepted_evidence_graph
        if item.evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
    )
    assert reference is not None
    content = reference.evidence_path.read_bytes()
    reference.evidence_path.unlink()
    underlying = tmp_path / "underlying-inventory"
    underlying.write_bytes(content)
    reference.evidence_path.symlink_to(underlying)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="regular file"):
        service.build_context(artifact)


def test_authentication_performs_no_filesystem_write(tmp_path: Path, monkeypatch) -> None:
    service, artifact, _ = _bundle(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("write capability invoked")

    monkeypatch.setattr(Path, "write_bytes", forbidden)
    monkeypatch.setattr(Path, "write_text", forbidden)
    context = service.build_context(artifact)
    assert context.authenticated_evidence


def test_only_governed_evidence_and_sidecar_paths_are_opened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    governed = {
        path
        for observation in baseline.accepted_evidence_graph
        if observation.evidence_reference is not None
        for path in (
            observation.evidence_reference.evidence_path,
            observation.evidence_reference.digest_path,
        )
    }
    opened: list[Path] = []
    original = analysis_module._read_regular

    def observed(path, *, max_bytes):
        opened.append(Path(path))
        return original(path, max_bytes=max_bytes)

    monkeypatch.setattr(analysis_module, "_read_regular", observed)
    service.build_context(artifact)

    assert set(opened) == governed
    assert Path("documents/file.txt") not in opened


def test_service_surface_contains_no_later_authority() -> None:
    names = set(dir(AcceptedBaselineAnalysisIntakeService))
    forbidden = {"classify", "publish", "persist", "migrate", "delete", "cleanup", "approve"}
    assert names.isdisjoint(forbidden)
    source = Path(analysis_module.__file__).read_text(encoding="utf-8")
    for dependency in ("subprocess", "requests", "socket", "boto", "sqlite3"):
        assert f"import {dependency}" not in source


def test_fifo_and_representative_non_regular_file_are_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fifo = tmp_path / "evidence.fifo"
    os.mkfifo(fifo)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="regular file"):
        analysis_module._read_regular(fifo, max_bytes=100)

    representative = tmp_path / "representative-device"
    representative.write_bytes(b"")
    actual = os.lstat(representative)
    monkeypatch.setattr(
        os,
        "lstat",
        lambda path: SimpleNamespace(
            st_mode=stat.S_IFCHR,
            **{
                name: getattr(actual, name)
                for name in (
                    "st_dev",
                    "st_ino",
                    "st_size",
                    "st_mtime_ns",
                    "st_ctime_ns",
                    "st_nlink",
                )
            },
        ),
    )
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="regular file"):
        analysis_module._read_regular(representative, max_bytes=100)


def test_descriptor_identity_mismatch_and_mutation_are_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "artifact"
    path.write_bytes(b"evidence")
    real_fstat = os.fstat
    calls = 0

    def mismatched(descriptor):
        nonlocal calls
        calls += 1
        result = real_fstat(descriptor)
        if calls == 1:
            return SimpleNamespace(
                st_mode=result.st_mode,
                st_dev=result.st_dev,
                st_ino=result.st_ino + 1,
                st_size=result.st_size,
                st_mtime_ns=result.st_mtime_ns,
                st_ctime_ns=result.st_ctime_ns,
                st_nlink=result.st_nlink,
            )
        return result

    monkeypatch.setattr(os, "fstat", mismatched)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="changed during open"):
        analysis_module._read_regular(path, max_bytes=100)

    monkeypatch.setattr(os, "fstat", real_fstat)
    real_lstat = os.lstat
    lstat_calls = 0

    def replaced(target):
        nonlocal lstat_calls
        lstat_calls += 1
        result = real_lstat(target)
        if lstat_calls == 2:
            return SimpleNamespace(
                st_mode=result.st_mode,
                st_dev=result.st_dev,
                st_ino=result.st_ino + 1,
                st_size=result.st_size,
                st_mtime_ns=result.st_mtime_ns,
                st_ctime_ns=result.st_ctime_ns,
                st_nlink=result.st_nlink,
            )
        return result

    monkeypatch.setattr(os, "lstat", replaced)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="changed during"):
        analysis_module._read_regular(path, max_bytes=100)


@pytest.mark.parametrize("mismatch", ("byte_count", "sha256"))
def test_evidence_transport_mismatch_fails_closed(tmp_path: Path, mismatch: str) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    reference = _reference(baseline, PreservationEvidenceType.INVENTORY_EVIDENCE)
    object.__setattr__(
        reference,
        mismatch,
        reference.byte_count + 1 if mismatch == "byte_count" else "0" * 64,
    )

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="mismatch"):
        service.build_context(artifact)


def test_missing_sidecar_fails_closed_with_preserved_cause(tmp_path: Path) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    reference = _reference(baseline, PreservationEvidenceType.INVENTORY_EVIDENCE)
    reference.digest_path.unlink()

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError) as raised:
        service.build_context(artifact)

    assert isinstance(raised.value.__cause__, FileNotFoundError)


def test_unreadable_sidecar_fails_closed_with_preserved_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    sidecar = _reference(baseline, PreservationEvidenceType.INVENTORY_EVIDENCE).digest_path
    original = analysis_module._read_regular

    def unreadable(path, *, max_bytes):
        if Path(path) == sidecar:
            raise PermissionError("synthetic permission denial")
        return original(path, max_bytes=max_bytes)

    monkeypatch.setattr(analysis_module, "_read_regular", unreadable)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError) as raised:
        service.build_context(artifact)
    assert isinstance(raised.value.__cause__, PermissionError)


@pytest.mark.parametrize(
    ("evidence_type", "content"),
    (
        (PreservationEvidenceType.INVENTORY_EVIDENCE, b"\xff\n"),
        (PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE, b"\xff"),
        (PreservationEvidenceType.INVENTORY_EVIDENCE, b"{malformed}\n"),
        (PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE, b"{malformed}"),
        (PreservationEvidenceType.INVENTORY_EVIDENCE, b'{"b":1, "a":2}\n'),
        (PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE, b'{"evidence": []}\n'),
        (PreservationEvidenceType.INVENTORY_EVIDENCE, b'{"a":1,"a":2}\n'),
        (
            PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            b'{"evidence":[],"evidence":[]}\n',
        ),
    ),
)
def test_encoding_json_and_canonical_failures_are_closed(
    tmp_path: Path,
    evidence_type: PreservationEvidenceType,
    content: bytes,
) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    _replace_evidence_bytes(_reference(baseline, evidence_type), content)

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError):
        service.build_context(artifact)


def test_retained_byte_and_aggregate_byte_limits_fail_without_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, _ = _bundle(tmp_path)
    original = analysis_module._read_regular

    def constrained(path, *, max_bytes):
        if Path(path).name.endswith(".json"):
            return original(path, max_bytes=1)
        return original(path, max_bytes=max_bytes)

    monkeypatch.setattr(analysis_module, "_read_regular", constrained)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="byte limit"):
        service.build_context(artifact)

    service, artifact, baseline = _bundle(tmp_path / "aggregate")
    total = sum(
        item.evidence_reference.byte_count
        for item in baseline.accepted_evidence_graph
        if item.evidence_reference is not None
    )
    service.profile = _profile_with(service.profile, maximum_aggregate_evidence_bytes=total - 1)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="aggregate"):
        service.build_context(artifact)


def test_per_root_and_aggregate_item_limits_fail_before_projection(tmp_path: Path) -> None:
    service, _, baseline = _bundle(tmp_path)
    inventory = _reference(baseline, PreservationEvidenceType.INVENTORY_EVIDENCE)
    integrity = _reference(baseline, PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE)

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="inventory item"):
        analysis_module._require_canonical(
            inventory.evidence_path.read_bytes(),
            PreservationEvidenceType.INVENTORY_EVIDENCE,
            service.profile,
            item_limit=0,
            aggregate_item_remaining=50_000,
        )
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="content-integrity"):
        analysis_module._require_canonical(
            integrity.evidence_path.read_bytes(),
            PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            service.profile,
            item_limit=0,
            aggregate_item_remaining=50_000,
        )
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="item count"):
        analysis_module._require_canonical(
            inventory.evidence_path.read_bytes(),
            PreservationEvidenceType.INVENTORY_EVIDENCE,
            service.profile,
            item_limit=25_000,
            aggregate_item_remaining=0,
        )


def test_unsupported_schema_and_missing_registry_adapter_fail(tmp_path: Path) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    reference = _reference(baseline, PreservationEvidenceType.INVENTORY_EVIDENCE)
    document = _canonical_document(reference)
    document[0]["schema_version"] = "999.0"
    _write_canonical_document(reference, document)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="deserialization"):
        service.build_context(artifact)

    with pytest.raises(
        PreservationBaselineValidationError, match="at least one validation adapter"
    ):
        AcceptedBaselineAnalysisIntakeService(registry=ValidationAdapterRegistry(adapters=()))

    adapters = analysis_module._default_registry().adapters
    with pytest.raises(PreservationBaselineValidationError, match="ambiguous"):
        ValidationAdapterRegistry(adapters=(*adapters, adapters[0]))


def test_projection_shape_drift_and_adapter_failure_preserve_causes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    reference = _reference(baseline, PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE)
    document = _canonical_document(reference)
    document["unexpected"] = True
    _write_canonical_document(reference, document)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError) as drift:
        service.build_context(artifact)
    assert isinstance(drift.value.__cause__, ValueError)

    service, artifact, _ = _bundle(tmp_path / "adapter")

    def failed(*args, **kwargs):
        raise ValueError("synthetic adapter failure")

    monkeypatch.setattr(
        analysis_module.PreservationEvidenceDeserializationService,
        "deserialize",
        failed,
    )
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError) as raised:
        service.build_context(artifact)
    assert isinstance(raised.value.__cause__, ValueError)


def test_scope_overlap_and_unknown_root_fail_before_evidence_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    object.__setattr__(baseline, "excluded_source_root_ids", ("root-a",))
    opened = False

    def forbidden(*args, **kwargs):
        nonlocal opened
        opened = True
        raise AssertionError("opened")

    monkeypatch.setattr(analysis_module, "_read_regular", forbidden)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="scope"):
        service.build_context(artifact)
    assert not opened

    object.__setattr__(baseline, "excluded_source_root_ids", ())
    for observation in baseline.accepted_evidence_graph:
        object.__setattr__(observation, "source_root_id", "unknown-root")
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="unknown"):
        service.build_context(artifact)
    assert not opened


@pytest.mark.parametrize(
    ("target", "value", "message"),
    (
        ("header", "other-root", "source-root lineage"),
        ("nested_root", "other-root", "inventory item lineage"),
        ("nested_path", "other/path", "inventory item lineage"),
        ("nested_item", "other-item", "does not reconcile"),
        ("integrity_item", "other-item", "does not reconcile"),
    ),
)
def test_nested_scope_and_item_lineage_contradictions_fail(
    tmp_path: Path, target: str, value: str, message: str
) -> None:
    service, artifact, baseline = _bundle(tmp_path)
    inventory = _reference(baseline, PreservationEvidenceType.INVENTORY_EVIDENCE)
    integrity = _reference(baseline, PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE)
    if target == "integrity_item":
        document = _canonical_document(integrity)
        document["evidence"][0]["item_id"] = value
        _write_canonical_document(integrity, document)
    else:
        document = _canonical_document(inventory)
        if target == "header":
            document[0]["source_root_id"] = value
        elif target == "nested_root":
            document[1]["record"]["identity"]["source_root_id"] = value
        elif target == "nested_path":
            document[1]["record"]["identity"]["relative_path"] = value
        else:
            document[1]["item_id"] = value
        _write_canonical_document(inventory, document)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match=message):
        service.build_context(artifact)


def test_second_required_artifact_failure_returns_no_partial_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, artifact, _ = _bundle(tmp_path)
    original = analysis_module._authenticate_reference
    calls = 0

    def fail_second(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise AcceptedBaselineEvidenceAuthenticationError("second artifact failed")
        return original(**kwargs)

    monkeypatch.setattr(analysis_module, "_authenticate_reference", fail_second)
    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="second artifact"):
        service.build_context(artifact)
    assert calls == 2


@pytest.mark.parametrize("duplicate_type", ("inventory", "integrity"))
def test_duplicate_projected_fact_identity_fails(tmp_path: Path, duplicate_type: str) -> None:
    _, _, baseline = _bundle(tmp_path)
    inventory_records = [
        {"source_root_id": "root-a"},
        {
            "support_status": "unsupported",
            "relative_path": "same/path",
            "item_id": "item-a",
        },
    ]
    integrity_records = [{"relative_path": "same/path", "item_id": "item-a"}]
    if duplicate_type == "inventory":
        inventory_records.append(dict(inventory_records[1]))
    else:
        integrity_records.append(dict(integrity_records[0]))
    projected = {
        PreservationEvidenceType.INVENTORY_EVIDENCE: analysis_module._freeze_json(
            inventory_records
        ),
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE: analysis_module._freeze_json(
            {"source_root_id": "root-a", "evidence": integrity_records}
        ),
    }

    with pytest.raises(AcceptedBaselineEvidenceAuthenticationError, match="duplicate|reconcile"):
        analysis_module._validate_root_lineage("root-a", projected, baseline)


def test_private_authenticator_is_not_exported_and_no_later_contract_names_exist() -> None:
    import poe_backup_orchestrator.services as service_exports

    assert not hasattr(service_exports, "_authenticate_reference")
    public_model_names = {
        name
        for name in dir(
            __import__(
                "poe_backup_orchestrator.models.storage_baseline_analysis",
                fromlist=["*"],
            )
        )
        if not name.startswith("_")
    }
    forbidden = {
        "Classification",
        "Destination",
        "Migration",
        "Cleanup",
        "SupersessionExecution",
    }
    assert not any(any(term in name for term in forbidden) for name in public_model_names)
