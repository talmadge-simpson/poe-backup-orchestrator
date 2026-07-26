"""Tests for orchestration job models."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import JobId, RegistryBackupRequest


def test_job_id_accepts_valid_value() -> None:
    job_id = JobId("20260726T144500000000Z-a1b2c3")

    assert str(job_id) == "20260726T144500000000Z-a1b2c3"


def test_job_id_strips_surrounding_whitespace() -> None:
    job_id = JobId("  job-123  ")

    assert job_id.value == "job-123"


@pytest.mark.parametrize("value", ["", "   ", "job 123", "job\t123"])
def test_job_id_rejects_invalid_value(value: str) -> None:
    with pytest.raises(ValueError):
        JobId(value)


def test_job_id_is_immutable() -> None:
    job_id = JobId("job-123")

    with pytest.raises(FrozenInstanceError):
        job_id.value = "changed"  # type: ignore[misc]


def test_registry_backup_request_normalizes_source_path() -> None:
    request = RegistryBackupRequest(source_path="registry.sqlite")

    assert request.source_path == Path("registry.sqlite")


def test_registry_backup_request_accepts_utc_timestamp() -> None:
    timestamp = datetime(2026, 7, 26, 14, 45, tzinfo=UTC)

    request = RegistryBackupRequest(
        source_path=Path("registry.sqlite"),
        requested_at_utc=timestamp,
    )

    assert request.requested_at_utc == timestamp


def test_registry_backup_request_rejects_naive_timestamp() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        RegistryBackupRequest(
            source_path=Path("registry.sqlite"),
            requested_at_utc=datetime(2026, 7, 26, 14, 45),
        )


def test_registry_backup_request_rejects_non_utc_timestamp() -> None:
    eastern_offset = timezone(timedelta(hours=-4))
    timestamp = datetime(2026, 7, 26, 10, 45, tzinfo=eastern_offset)

    with pytest.raises(ValueError, match="normalized to UTC"):
        RegistryBackupRequest(
            source_path=Path("registry.sqlite"),
            requested_at_utc=timestamp,
        )
