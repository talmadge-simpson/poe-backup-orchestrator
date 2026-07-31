"""Immutable accepted-preservation-baseline publication contracts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_authorization import (
    AuthorizationConditionDecision,
    AuthorizationDecisionOutcome,
    PilotAuthorization,
    PreservationBaselineAuthorizationDecision,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    EvidenceRequirementObservation,
)

STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION: Final[str] = "1.0"

_ACCEPTED_BASELINE_ID_PATTERN = re.compile(r"pab-[0-9a-f]{64}")
_AUTHORIZATION_ID_PATTERN = re.compile(r"pbd-[0-9a-f]{64}")
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def _required_code(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


def _ordered_unique(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    normalized = tuple(_required_code(value, field_name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} must not contain duplicates")
    if normalized != tuple(sorted(normalized)):
        raise ValueError(f"{field_name} must use canonical ordering")
    return normalized


def _sha256(value: str, field_name: str) -> str:
    normalized = value.strip()
    if _SHA256_PATTERN.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must contain 64 lowercase hexadecimal characters")
    return normalized


class AcceptedPreservationBaselineMode(StrEnum):
    """Governed acceptance mode projected from a human authorization outcome."""

    STRICT = "strict"
    APPROVED_EXCEPTIONS = "approved_exceptions"
    PARTIAL_SOURCE = "partial_source"
    PILOT = "pilot"


@dataclass(frozen=True, slots=True)
class AcceptedPreservationBaselineIdentity:
    """Semantic accepted-baseline identity with complete predecessor lineage."""

    schema_version: str
    accepted_baseline_id: str
    authorization_id: str
    evaluation_id: str
    validation_id: str
    candidate_id: str
    baseline_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION:
            raise ValueError("unsupported accepted-baseline schema_version")
        if _ACCEPTED_BASELINE_ID_PATTERN.fullmatch(self.accepted_baseline_id) is None:
            raise ValueError("accepted_baseline_id must use the governed pab identifier")
        if _AUTHORIZATION_ID_PATTERN.fullmatch(self.authorization_id) is None:
            raise ValueError("authorization_id must use the governed pbd identifier")
        for field_name in ("evaluation_id", "validation_id", "candidate_id", "baseline_id"):
            object.__setattr__(
                self,
                field_name,
                _required_code(getattr(self, field_name), field_name),
            )


def stable_accepted_preservation_baseline_id(
    *,
    authorization_id: str,
    evaluation_id: str,
    validation_id: str,
    candidate_id: str,
    baseline_id: str,
    mode: AcceptedPreservationBaselineMode,
    accepted_source_root_ids: tuple[str, ...],
    excluded_source_root_ids: tuple[str, ...],
    scope_limitations: tuple[str, ...],
    condition_decisions: tuple[AuthorizationConditionDecision, ...],
    pilot: PilotAuthorization | None,
    retention_obligations: tuple[str, ...],
    supersession_eligible: bool,
) -> str:
    """Derive the one accepted-baseline identity from authorization semantics."""

    accepted = _ordered_unique(tuple(accepted_source_root_ids), "accepted_source_root_ids")
    excluded = _ordered_unique(tuple(excluded_source_root_ids), "excluded_source_root_ids")
    limitations = tuple(scope_limitations)
    obligations = tuple(retention_obligations)
    conditions = tuple(condition_decisions)
    payload = {
        "schema_version": STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION,
        "authorization_id": _required_code(authorization_id, "authorization_id"),
        "evaluation_id": _required_code(evaluation_id, "evaluation_id"),
        "validation_id": _required_code(validation_id, "validation_id"),
        "candidate_id": _required_code(candidate_id, "candidate_id"),
        "baseline_id": _required_code(baseline_id, "baseline_id"),
        "mode": mode.value,
        "accepted_source_root_ids": list(accepted),
        "excluded_source_root_ids": list(excluded),
        "scope_limitations": list(limitations),
        "condition_decisions": [
            {
                "condition_sequence": item.condition_sequence,
                "condition_code": item.condition_code,
                "disposition": item.disposition.value,
                "rationale": item.rationale,
            }
            for item in conditions
        ],
        "pilot": (
            None
            if pilot is None
            else {"purpose": pilot.purpose, "limitations": list(pilot.limitations)}
        ),
        "retention_obligations": list(obligations),
        "supersession_eligible": supersession_eligible,
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"pab-{hashlib.sha256(canonical).hexdigest()}"


@dataclass(frozen=True, slots=True)
class AcceptedPreservationBaseline:
    """One immutable deterministic projection of one verified authorization."""

    identity: AcceptedPreservationBaselineIdentity
    authorization_decision: PreservationBaselineAuthorizationDecision
    authorization_artifact_sha256: str
    authorization_artifact_byte_count: int
    mode: AcceptedPreservationBaselineMode
    accepted_source_root_ids: tuple[str, ...]
    excluded_source_root_ids: tuple[str, ...]
    scope_limitations: tuple[str, ...]
    accepted_evidence_graph: tuple[EvidenceRequirementObservation, ...]
    condition_decisions: tuple[AuthorizationConditionDecision, ...]
    pilot: PilotAuthorization | None
    retention_obligations: tuple[str, ...]
    supersession_eligible: bool

    def __post_init__(self) -> None:
        decision = self.authorization_decision
        if not isinstance(decision, PreservationBaselineAuthorizationDecision):
            raise ValueError(
                "authorization_decision must be PreservationBaselineAuthorizationDecision"
            )
        digest = _sha256(self.authorization_artifact_sha256, "authorization_artifact_sha256")
        if self.authorization_artifact_byte_count <= 0:
            raise ValueError("authorization_artifact_byte_count must be greater than zero")

        accepted = _ordered_unique(tuple(self.accepted_source_root_ids), "accepted_source_root_ids")
        excluded = _ordered_unique(tuple(self.excluded_source_root_ids), "excluded_source_root_ids")
        limitations = tuple(self.scope_limitations)
        graph = tuple(self.accepted_evidence_graph)
        conditions = tuple(self.condition_decisions)
        obligations = tuple(self.retention_obligations)

        authorization_identity = decision.identity
        for field_name in (
            "authorization_id",
            "evaluation_id",
            "validation_id",
            "candidate_id",
            "baseline_id",
        ):
            if getattr(self.identity, field_name) != getattr(authorization_identity, field_name):
                raise ValueError(f"accepted-baseline {field_name} does not match authorization")

        if accepted != decision.scope.accepted_source_root_ids:
            raise ValueError("accepted source roots must exactly match authorization")
        if excluded != decision.scope.excluded_source_root_ids:
            raise ValueError("excluded source roots must exactly match authorization")
        if limitations != decision.scope.scope_limitations:
            raise ValueError("scope limitations must exactly match authorization")
        if conditions != decision.condition_decisions:
            raise ValueError("condition decisions must exactly match authorization")
        if self.pilot != decision.pilot:
            raise ValueError("pilot constraints must exactly match authorization")
        if obligations != decision.retention_obligations:
            raise ValueError("retention obligations must exactly match authorization")
        if self.supersession_eligible is not decision.supersession_eligible:
            raise ValueError("supersession eligibility must exactly match authorization")

        expected_mode = {
            AuthorizationDecisionOutcome.AUTHORIZE: AcceptedPreservationBaselineMode.STRICT,
            AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS: (
                AcceptedPreservationBaselineMode.APPROVED_EXCEPTIONS
            ),
            AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE: (
                AcceptedPreservationBaselineMode.PARTIAL_SOURCE
            ),
            AuthorizationDecisionOutcome.AUTHORIZE_PILOT: (AcceptedPreservationBaselineMode.PILOT),
        }.get(decision.outcome)
        if self.mode is not expected_mode:
            raise ValueError("accepted-baseline mode does not match authorization outcome")

        expected_graph = tuple(
            observation
            for observation in decision.recommendation.validation_result.candidate.observations
            if observation.source_root_id in set(accepted)
        )
        if graph != expected_graph:
            raise ValueError(
                "accepted evidence graph must contain exactly accepted-root observations"
            )

        stable_id = stable_accepted_preservation_baseline_id(
            authorization_id=authorization_identity.authorization_id,
            evaluation_id=authorization_identity.evaluation_id,
            validation_id=authorization_identity.validation_id,
            candidate_id=authorization_identity.candidate_id,
            baseline_id=authorization_identity.baseline_id,
            mode=self.mode,
            accepted_source_root_ids=accepted,
            excluded_source_root_ids=excluded,
            scope_limitations=limitations,
            condition_decisions=conditions,
            pilot=self.pilot,
            retention_obligations=obligations,
            supersession_eligible=self.supersession_eligible,
        )
        if self.identity.accepted_baseline_id != stable_id:
            raise ValueError("accepted_baseline_id does not match semantic projection")

        object.__setattr__(self, "authorization_artifact_sha256", digest)
        object.__setattr__(self, "accepted_source_root_ids", accepted)
        object.__setattr__(self, "excluded_source_root_ids", excluded)
        object.__setattr__(self, "scope_limitations", limitations)
        object.__setattr__(self, "accepted_evidence_graph", graph)
        object.__setattr__(self, "condition_decisions", conditions)
        object.__setattr__(self, "retention_obligations", obligations)


@dataclass(frozen=True, slots=True)
class AcceptedPreservationBaselineReference:
    """Sole authoritative publication boundary exposed to downstream consumers."""

    schema_version: str
    accepted_baseline_id: str
    baseline_id: str
    authorization_id: str
    mode: AcceptedPreservationBaselineMode
    accepted_source_root_ids: tuple[str, ...]
    excluded_source_root_ids: tuple[str, ...]
    accepted_baseline_filename: str
    accepted_baseline_sha256_filename: str
    accepted_baseline_sha256: str
    accepted_baseline_byte_count: int

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION:
            raise ValueError("unsupported reference schema_version")
        if _ACCEPTED_BASELINE_ID_PATTERN.fullmatch(self.accepted_baseline_id) is None:
            raise ValueError("accepted_baseline_id must use the governed pab identifier")
        if _AUTHORIZATION_ID_PATTERN.fullmatch(self.authorization_id) is None:
            raise ValueError("authorization_id must use the governed pbd identifier")
        object.__setattr__(self, "baseline_id", _required_code(self.baseline_id, "baseline_id"))
        accepted = _ordered_unique(tuple(self.accepted_source_root_ids), "accepted_source_root_ids")
        excluded = _ordered_unique(tuple(self.excluded_source_root_ids), "excluded_source_root_ids")
        expected_filename = f"accepted-preservation-baseline-{self.accepted_baseline_id}.json"
        if self.accepted_baseline_filename != expected_filename:
            raise ValueError("accepted_baseline_filename must match accepted_baseline_id")
        if self.accepted_baseline_sha256_filename != f"{expected_filename}.sha256":
            raise ValueError("accepted_baseline_sha256_filename must match artifact filename")
        digest = _sha256(self.accepted_baseline_sha256, "accepted_baseline_sha256")
        if self.accepted_baseline_byte_count <= 0:
            raise ValueError("accepted_baseline_byte_count must be greater than zero")
        object.__setattr__(self, "accepted_source_root_ids", accepted)
        object.__setattr__(self, "excluded_source_root_ids", excluded)
        object.__setattr__(self, "accepted_baseline_sha256", digest)


@dataclass(frozen=True, slots=True)
class AcceptedPreservationBaselineArtifact:
    """Filesystem metadata for one immutable published JSON artifact."""

    evidence_path: Path
    sha256_path: Path
    sha256: str
    byte_count: int

    def __post_init__(self) -> None:
        evidence_path = Path(self.evidence_path)
        sha256_path = Path(self.sha256_path)
        if not evidence_path.is_absolute() or not sha256_path.is_absolute():
            raise ValueError("artifact paths must be absolute")
        if sha256_path != evidence_path.with_name(f"{evidence_path.name}.sha256"):
            raise ValueError("sha256_path must append .sha256 to evidence filename")
        digest = _sha256(self.sha256, "sha256")
        if self.byte_count <= 0:
            raise ValueError("byte_count must be greater than zero")
        object.__setattr__(self, "evidence_path", evidence_path)
        object.__setattr__(self, "sha256_path", sha256_path)
        object.__setattr__(self, "sha256", digest)


@dataclass(frozen=True, slots=True)
class AcceptedPreservationBaselinePublicationResult:
    """Result of first accepted-baseline publication or verified exact replay."""

    accepted_baseline_id: str
    baseline_id: str
    authorization_id: str
    accepted_baseline_artifact: AcceptedPreservationBaselineArtifact
    reference_artifact: AcceptedPreservationBaselineArtifact
    idempotent_replay: bool

    def __post_init__(self) -> None:
        if _ACCEPTED_BASELINE_ID_PATTERN.fullmatch(self.accepted_baseline_id) is None:
            raise ValueError("accepted_baseline_id must use the governed pab identifier")
        if _AUTHORIZATION_ID_PATTERN.fullmatch(self.authorization_id) is None:
            raise ValueError("authorization_id must use the governed pbd identifier")
        object.__setattr__(self, "baseline_id", _required_code(self.baseline_id, "baseline_id"))
        expected_full = f"accepted-preservation-baseline-{self.accepted_baseline_id}.json"
        expected_reference = (
            f"accepted-preservation-baseline-reference-{self.accepted_baseline_id}.json"
        )
        if self.accepted_baseline_artifact.evidence_path.name != expected_full:
            raise ValueError("accepted-baseline artifact filename does not match identity")
        if self.reference_artifact.evidence_path.name != expected_reference:
            raise ValueError("reference artifact filename does not match identity")
        if not isinstance(self.idempotent_replay, bool):
            raise ValueError("idempotent_replay must be bool")
