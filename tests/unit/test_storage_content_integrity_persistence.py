"""Tests for canonical atomic content-integrity evidence persistence."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models.storage_content_integrity import (
    STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
    ContentIntegrityOutcome,
    ContentIntegrityTotals,
    ContentIntegrityVerificationResult,
    FileIntegrityEvidence,
    SourceFileObservation,
)
from poe_backup_orchestrator.services.storage_content_integrity_persistence import (
    ContentIntegrityEvidencePersistence,
)

T0 = datetime(2026, 7, 29, 16, 0, tzinfo=UTC)
DIGEST = hashlib.sha256(b"x").hexdigest()
OBSERVATION = SourceFileObservation(
    size_bytes=1,
    modified_at_ns=1,
    mode=0o100644,
    device_id=1,
    inode=2,
)


def result() -> ContentIntegrityVerificationResult:
    evidence = FileIntegrityEvidence(
        schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
        item_id="item-a",
        relative_path=Path("a.bin"),
        expected_size_bytes=1,
        observed_size_bytes=1,
        expected_sha256=DIGEST,
        observed_sha256=DIGEST,
        verification_started_at_utc=T0,
        verification_completed_at_utc=T0,
        outcome=ContentIntegrityOutcome.VERIFIED,
        source_observation_before=OBSERVATION,
        source_observation_after=OBSERVATION,
    )
    totals = ContentIntegrityTotals(
        candidate_file_count=1,
        verified_count=1,
        source_changed_count=0,
        size_mismatch_count=0,
        digest_mismatch_count=0,
        missing_count=0,
        inaccessible_count=0,
        not_regular_file_count=0,
        filesystem_error_count=0,
        total_expected_bytes=1,
        total_observed_bytes=1,
    )
    return ContentIntegrityVerificationResult(
        schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
        source_root_id="root-1",
        verification_started_at_utc=T0,
        verification_completed_at_utc=T0,
        evidence=(evidence,),
        totals=totals,
    )


def test_persistence_is_deterministic_and_digest_is_correct(tmp_path: Path) -> None:
    service = ContentIntegrityEvidencePersistence()
    first = service.persist(destination_directory=tmp_path, result=result())
    first_bytes = first.evidence_path.read_bytes()
    second = service.persist(destination_directory=tmp_path, result=result())
    second_bytes = second.evidence_path.read_bytes()

    assert first_bytes == second_bytes
    assert first_bytes.endswith(b"\n")
    assert first.sha256 == hashlib.sha256(first_bytes).hexdigest()
    assert second.digest_path.read_text(encoding="ascii") == f"{second.sha256}\n"
    assert second.byte_count == len(second_bytes)


def test_persistence_creates_destination(tmp_path: Path) -> None:
    destination = tmp_path / "nested" / "integrity"
    persisted = ContentIntegrityEvidencePersistence().persist(
        destination_directory=destination,
        result=result(),
    )
    assert persisted.evidence_path.is_file()
    assert persisted.digest_path.is_file()
