"""Evidence models for orchestration execution results."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class EvidenceType(StrEnum):
    """Stable categories for execution evidence."""

    LOG = "log"
    REPORT = "report"
    SOURCE_METADATA = "source_metadata"
    CHECKSUM = "checksum"
    VALIDATION = "validation"
    ACCEPTED_ARTIFACT = "accepted_artifact"
    FAILURE = "failure"


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    """Reference to evidence produced or preserved by an execution."""

    evidence_type: EvidenceType
    description: str
    path: Path | None = None
    sha256: str | None = None

    def __post_init__(self) -> None:
        description = self.description.strip()
        if not description:
            raise ValueError("evidence description must not be empty")
        object.__setattr__(self, "description", description)

        if self.path is not None:
            object.__setattr__(self, "path", Path(self.path))

        if self.sha256 is not None:
            digest = self.sha256.strip().lower()
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError("sha256 must contain exactly 64 hexadecimal characters")
            object.__setattr__(self, "sha256", digest)
