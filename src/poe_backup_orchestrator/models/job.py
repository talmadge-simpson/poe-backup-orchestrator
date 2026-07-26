"""Job identity and execution request models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol


def require_utc(value: datetime, *, field_name: str) -> datetime:
    """Validate that a datetime is timezone-aware and normalized to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must be normalized to UTC")
    return value


@dataclass(frozen=True, slots=True)
class JobId:
    """Validated identifier for one orchestration execution."""

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("job ID must not be empty")
        if any(character.isspace() for character in normalized):
            raise ValueError("job ID must not contain whitespace")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RegistryBackupRequest:
    """Input contract for one Registry backup execution."""

    source_path: Path
    job_id: JobId | None = None
    requested_at_utc: datetime | None = None

    def __post_init__(self) -> None:
        source_path = Path(self.source_path)
        if not str(source_path):
            raise ValueError("source_path must not be empty")
        object.__setattr__(self, "source_path", source_path)

        if self.requested_at_utc is not None:
            require_utc(self.requested_at_utc, field_name="requested_at_utc")


class Clock(Protocol):
    """Provides the current UTC time."""

    def now_utc(self) -> datetime:
        """Return the current timezone-aware UTC time."""


class JobIdGenerator(Protocol):
    """Generates unique orchestration job identifiers."""

    def generate(self, now_utc: datetime) -> JobId:
        """Generate a job identifier using a UTC timestamp."""
