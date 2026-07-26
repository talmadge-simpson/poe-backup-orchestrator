"""Tests for orchestration evidence models."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import EvidenceReference, EvidenceType


def test_evidence_reference_accepts_valid_values() -> None:
    digest = "a" * 64

    evidence = EvidenceReference(
        evidence_type=EvidenceType.CHECKSUM,
        description="Registry acquisition SHA-256",
        path=Path("/tmp/checksum.txt"),
        sha256=digest,
    )

    assert evidence.sha256 == digest
    assert evidence.path == Path("/tmp/checksum.txt")


def test_evidence_reference_normalizes_digest_case() -> None:
    evidence = EvidenceReference(
        evidence_type=EvidenceType.CHECKSUM,
        description="Checksum",
        sha256="A" * 64,
    )

    assert evidence.sha256 == "a" * 64


@pytest.mark.parametrize(
    "digest",
    [
        "",
        "a" * 63,
        "a" * 65,
        "g" * 64,
    ],
)
def test_evidence_reference_rejects_invalid_digest(digest: str) -> None:
    with pytest.raises(ValueError, match="64 hexadecimal"):
        EvidenceReference(
            evidence_type=EvidenceType.CHECKSUM,
            description="Checksum",
            sha256=digest,
        )


def test_evidence_reference_rejects_empty_description() -> None:
    with pytest.raises(ValueError, match="description"):
        EvidenceReference(
            evidence_type=EvidenceType.LOG,
            description=" ",
        )


def test_evidence_reference_is_immutable() -> None:
    evidence = EvidenceReference(
        evidence_type=EvidenceType.LOG,
        description="Execution log",
    )

    with pytest.raises(FrozenInstanceError):
        evidence.description = "changed"  # type: ignore[misc]
