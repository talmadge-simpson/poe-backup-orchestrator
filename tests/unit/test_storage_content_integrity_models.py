"""Tests for immutable content-integrity domain contracts."""

from __future__ import annotations

import hashlib
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models.storage_content_integrity import (
    STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
    ContentIntegrityFailureCode,
    ContentIntegrityOutcome,
    ContentIntegrityTotals,
    ContentIntegrityVerificationResult,
    FileIntegrityEvidence,
    SourceFileObservation,
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


def verified(path: str = "a.bin") -> FileIntegrityEvidence:
    return FileIntegrityEvidence(
        schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
        item_id=f"item-{path}",
        relative_path=Path(path),
        expected_size_bytes=1,
        observed_size_bytes=1,
        expected_sha256=DIGEST,
        observed_sha256=DIGEST.upper(),
        verification_started_at_utc=T0,
        verification_completed_at_utc=T0,
        outcome=ContentIntegrityOutcome.VERIFIED,
        source_observation_before=OBSERVATION,
        source_observation_after=OBSERVATION,
    )


def test_verified_evidence_is_immutable_and_normalized() -> None:
    evidence = verified()
    assert evidence.observed_sha256 == DIGEST
    with pytest.raises(FrozenInstanceError):
        evidence.item_id = "changed"  # type: ignore[misc]


def test_verified_evidence_rejects_size_mismatch() -> None:
    with pytest.raises(ValueError, match="matching sizes"):
        FileIntegrityEvidence(
            schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
            item_id="item-a",
            relative_path=Path("a.bin"),
            expected_size_bytes=1,
            observed_size_bytes=2,
            expected_sha256=DIGEST,
            observed_sha256=DIGEST,
            verification_started_at_utc=T0,
            verification_completed_at_utc=T0,
            outcome=ContentIntegrityOutcome.VERIFIED,
            source_observation_before=OBSERVATION,
            source_observation_after=OBSERVATION,
        )


def test_failed_evidence_requires_failure_detail() -> None:
    with pytest.raises(ValueError, match="requires"):
        FileIntegrityEvidence(
            schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
            item_id="item-a",
            relative_path=Path("a.bin"),
            expected_size_bytes=1,
            observed_size_bytes=None,
            expected_sha256=DIGEST,
            observed_sha256=None,
            verification_started_at_utc=T0,
            verification_completed_at_utc=T0,
            outcome=ContentIntegrityOutcome.MISSING,
        )


def test_totals_must_reconcile() -> None:
    with pytest.raises(ValueError, match="reconcile"):
        ContentIntegrityTotals(
            candidate_file_count=2,
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


def test_result_requires_sorted_evidence() -> None:
    totals = ContentIntegrityTotals(
        candidate_file_count=2,
        verified_count=2,
        source_changed_count=0,
        size_mismatch_count=0,
        digest_mismatch_count=0,
        missing_count=0,
        inaccessible_count=0,
        not_regular_file_count=0,
        filesystem_error_count=0,
        total_expected_bytes=2,
        total_observed_bytes=2,
    )
    with pytest.raises(ValueError, match="ordered"):
        ContentIntegrityVerificationResult(
            schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
            source_root_id="root-1",
            verification_started_at_utc=T0,
            verification_completed_at_utc=T0,
            evidence=(verified("z.bin"), verified("a.bin")),
            totals=totals,
        )


def test_failure_code_is_preserved() -> None:
    evidence = FileIntegrityEvidence(
        schema_version=STORAGE_CONTENT_INTEGRITY_SCHEMA_VERSION,
        item_id="item-a",
        relative_path=Path("a.bin"),
        expected_size_bytes=1,
        observed_size_bytes=None,
        expected_sha256=DIGEST,
        observed_sha256=None,
        verification_started_at_utc=T0,
        verification_completed_at_utc=T0,
        outcome=ContentIntegrityOutcome.MISSING,
        failure_code=ContentIntegrityFailureCode.SOURCE_MISSING,
        detail="missing",
    )
    assert evidence.failure_code is ContentIntegrityFailureCode.SOURCE_MISSING
