"""Immutable preservation-baseline authorization-persistence contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_AUTHORIZATION_ID_PATTERN = re.compile(r"pbd-[0-9a-f]{64}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def _required_code(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationArtifact:
    """Filesystem evidence for one durably stored authorization decision."""

    evidence_path: Path
    sha256_path: Path
    sha256: str
    byte_count: int

    def __post_init__(self) -> None:
        evidence_path = Path(self.evidence_path)
        sha256_path = Path(self.sha256_path)
        sha256 = self.sha256.strip()

        if not evidence_path.is_absolute():
            raise ValueError("evidence_path must be absolute")
        if not sha256_path.is_absolute():
            raise ValueError("sha256_path must be absolute")
        if sha256_path != evidence_path.with_name(f"{evidence_path.name}.sha256"):
            raise ValueError("sha256_path must be the evidence path with .sha256 appended")
        if _SHA256_PATTERN.fullmatch(sha256) is None:
            raise ValueError("sha256 must contain exactly 64 lowercase hexadecimal characters")
        if self.byte_count <= 0:
            raise ValueError("byte_count must be greater than zero")

        object.__setattr__(self, "evidence_path", evidence_path)
        object.__setattr__(self, "sha256_path", sha256_path)
        object.__setattr__(self, "sha256", sha256)


@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationPersistenceResult:
    """Result of first persistence or verified exact replay."""

    authorization_id: str
    baseline_id: str
    artifact: PreservationBaselineAuthorizationArtifact
    idempotent_replay: bool

    def __post_init__(self) -> None:
        authorization_id = _required_code(self.authorization_id, "authorization_id")
        baseline_id = _required_code(self.baseline_id, "baseline_id")
        if _AUTHORIZATION_ID_PATTERN.fullmatch(authorization_id) is None:
            raise ValueError("authorization_id must use the governed pbd identifier")
        if not isinstance(self.artifact, PreservationBaselineAuthorizationArtifact):
            raise ValueError("artifact must be PreservationBaselineAuthorizationArtifact")
        expected_filename = f"preservation-baseline-authorization-{authorization_id}.json"
        if self.artifact.evidence_path.name != expected_filename:
            raise ValueError("artifact evidence_path must match authorization_id")
        if not isinstance(self.idempotent_replay, bool):
            raise ValueError("idempotent_replay must be bool")

        object.__setattr__(self, "authorization_id", authorization_id)
        object.__setattr__(self, "baseline_id", baseline_id)
