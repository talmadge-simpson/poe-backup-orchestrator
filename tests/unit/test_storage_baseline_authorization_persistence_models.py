"""Tests for immutable authorization-persistence result contracts."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationArtifact,
    PreservationBaselineAuthorizationPersistenceResult,
)

DIGEST = "a" * 64
AUTHORIZATION_ID = "pbd-" + "b" * 64


def artifact() -> PreservationBaselineAuthorizationArtifact:
    evidence = Path(f"/evidence/preservation-baseline-authorization-{AUTHORIZATION_ID}.json")
    return PreservationBaselineAuthorizationArtifact(
        evidence_path=evidence,
        sha256_path=evidence.with_name(f"{evidence.name}.sha256"),
        sha256=DIGEST,
        byte_count=100,
    )


def test_artifact_accepts_governed_paths_digest_and_byte_count() -> None:
    value = artifact()

    assert value.evidence_path.is_absolute()
    assert value.sha256_path == Path(f"{value.evidence_path}.sha256")
    assert value.sha256 == DIGEST
    assert value.byte_count == 100


@pytest.mark.parametrize("field_name", ("evidence_path", "sha256_path"))
def test_artifact_requires_absolute_paths(field_name: str) -> None:
    values = {
        "evidence_path": Path("decision.json"),
        "sha256_path": Path("decision.json.sha256"),
        "sha256": DIGEST,
        "byte_count": 1,
    }

    with pytest.raises(ValueError, match="absolute"):
        PreservationBaselineAuthorizationArtifact(**values)  # type: ignore[arg-type]


def test_artifact_requires_derived_sidecar_path() -> None:
    with pytest.raises(ValueError, match="appended"):
        PreservationBaselineAuthorizationArtifact(
            evidence_path=Path("/evidence/decision.json"),
            sha256_path=Path("/evidence/other.sha256"),
            sha256=DIGEST,
            byte_count=1,
        )


@pytest.mark.parametrize("digest", ("A" * 64, "a" * 63, "g" * 64))
def test_artifact_rejects_noncanonical_digest(digest: str) -> None:
    with pytest.raises(ValueError, match="64 lowercase"):
        PreservationBaselineAuthorizationArtifact(
            evidence_path=Path("/evidence/decision.json"),
            sha256_path=Path("/evidence/decision.json.sha256"),
            sha256=digest,
            byte_count=1,
        )


def test_artifact_requires_positive_byte_count() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        PreservationBaselineAuthorizationArtifact(
            evidence_path=Path("/evidence/decision.json"),
            sha256_path=Path("/evidence/decision.json.sha256"),
            sha256=DIGEST,
            byte_count=0,
        )


def test_persistence_result_accepts_exact_identity_and_replay_state() -> None:
    value = PreservationBaselineAuthorizationPersistenceResult(
        authorization_id=AUTHORIZATION_ID,
        baseline_id="baseline-a",
        artifact=artifact(),
        idempotent_replay=False,
    )

    assert value.authorization_id == AUTHORIZATION_ID
    assert value.baseline_id == "baseline-a"
    assert value.idempotent_replay is False


def test_persistence_result_rejects_invalid_contract_fields() -> None:
    with pytest.raises(ValueError, match="governed pbd"):
        PreservationBaselineAuthorizationPersistenceResult(
            authorization_id="authorization-a",
            baseline_id="baseline-a",
            artifact=artifact(),
            idempotent_replay=False,
        )

    with pytest.raises(ValueError, match="artifact"):
        PreservationBaselineAuthorizationPersistenceResult(
            authorization_id=AUTHORIZATION_ID,
            baseline_id="baseline-a",
            artifact=object(),  # type: ignore[arg-type]
            idempotent_replay=False,
        )

    with pytest.raises(ValueError, match="bool"):
        PreservationBaselineAuthorizationPersistenceResult(
            authorization_id=AUTHORIZATION_ID,
            baseline_id="baseline-a",
            artifact=artifact(),
            idempotent_replay=1,  # type: ignore[arg-type]
        )

    mismatched = PreservationBaselineAuthorizationArtifact(
        evidence_path=Path("/evidence/other.json"),
        sha256_path=Path("/evidence/other.json.sha256"),
        sha256=DIGEST,
        byte_count=1,
    )
    with pytest.raises(ValueError, match="authorization_id"):
        PreservationBaselineAuthorizationPersistenceResult(
            authorization_id=AUTHORIZATION_ID,
            baseline_id="baseline-a",
            artifact=mismatched,
            idempotent_replay=False,
        )


def test_persistence_contracts_are_frozen() -> None:
    value = PreservationBaselineAuthorizationPersistenceResult(
        authorization_id=AUTHORIZATION_ID,
        baseline_id="baseline-a",
        artifact=artifact(),
        idempotent_replay=False,
    )

    with pytest.raises(FrozenInstanceError):
        value.idempotent_replay = True  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        value.artifact.sha256 = "c" * 64  # type: ignore[misc]
