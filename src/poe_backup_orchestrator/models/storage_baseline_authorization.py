"""Immutable preservation-baseline human-authorization contracts."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

from poe_backup_orchestrator.models.storage_baseline_acceptance import (
    AcceptanceConditionDisposition,
    AcceptanceDecision,
    PreservationBaselineAcceptanceRecommendation,
)

STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION: Final[str] = "1.0"

_AUTHORIZATION_ID_PATTERN = re.compile(r"pbd-[0-9a-f]{64}")


def _normalize_required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _normalize_code(value: str, field_name: str) -> str:
    normalized = _normalize_required(value, field_name)
    if any(character.isspace() for character in normalized):
        raise ValueError(f"{field_name} must not contain whitespace")
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_ordered_unique(
    values: tuple[str, ...],
    field_name: str,
    *,
    codes: bool = False,
) -> tuple[str, ...]:
    normalizer = _normalize_code if codes else _normalize_required
    normalized = tuple(normalizer(value, field_name) for value in values)
    if len(set(normalized)) != len(normalized):
        raise ValueError(f"{field_name} must not contain duplicates")
    if normalized != tuple(sorted(normalized)):
        raise ValueError(f"{field_name} must use canonical ordering")
    return normalized


def _require_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError(f"{field_name} must be UTC")
    return value.astimezone(UTC)


class AuthorizationDecisionOutcome(StrEnum):
    """Explicit accountable human decision outcome."""

    AUTHORIZE = "authorize"
    AUTHORIZE_WITH_EXCEPTIONS = "authorize_with_exceptions"
    AUTHORIZE_PARTIAL_SCOPE = "authorize_partial_scope"
    AUTHORIZE_PILOT = "authorize_pilot"
    REJECT = "reject"


class AuthorizationConditionDisposition(StrEnum):
    """Human disposition for one recommendation condition."""

    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class AuthorizationAuthority:
    """Accountable authority identity evidence without authentication claims."""

    authority_id: str
    display_name: str
    authority_role: str
    authority_basis: str
    organization: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "authority_id",
            _normalize_code(self.authority_id, "authority_id"),
        )
        object.__setattr__(
            self,
            "display_name",
            _normalize_required(self.display_name, "display_name"),
        )
        object.__setattr__(
            self,
            "authority_role",
            _normalize_required(self.authority_role, "authority_role"),
        )
        object.__setattr__(
            self,
            "authority_basis",
            _normalize_required(self.authority_basis, "authority_basis"),
        )
        object.__setattr__(self, "organization", _normalize_optional(self.organization))


@dataclass(frozen=True, slots=True)
class AuthorizationConditionDecision:
    """One explicit human disposition for one recommendation condition."""

    condition_sequence: int
    condition_code: str
    disposition: AuthorizationConditionDisposition
    rationale: str

    def __post_init__(self) -> None:
        if self.condition_sequence <= 0:
            raise ValueError("condition_sequence must be positive")
        object.__setattr__(
            self,
            "condition_code",
            _normalize_code(self.condition_code, "condition_code"),
        )
        object.__setattr__(
            self,
            "rationale",
            _normalize_required(self.rationale, "rationale"),
        )


@dataclass(frozen=True, slots=True)
class AuthorizationScope:
    """Explicit accepted and excluded preservation-baseline source scope."""

    accepted_source_root_ids: tuple[str, ...]
    excluded_source_root_ids: tuple[str, ...]
    scope_limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        accepted = _normalize_ordered_unique(
            tuple(self.accepted_source_root_ids),
            "accepted_source_root_ids",
            codes=True,
        )
        excluded = _normalize_ordered_unique(
            tuple(self.excluded_source_root_ids),
            "excluded_source_root_ids",
            codes=True,
        )
        limitations = _normalize_ordered_unique(
            tuple(self.scope_limitations),
            "scope_limitations",
        )
        if set(accepted) & set(excluded):
            raise ValueError("accepted and excluded source roots must not overlap")
        object.__setattr__(self, "accepted_source_root_ids", accepted)
        object.__setattr__(self, "excluded_source_root_ids", excluded)
        object.__setattr__(self, "scope_limitations", limitations)


@dataclass(frozen=True, slots=True)
class PilotAuthorization:
    """Explicit constrained pilot purpose and limitations."""

    purpose: str
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        purpose = _normalize_required(self.purpose, "purpose")
        limitations = _normalize_ordered_unique(
            tuple(self.limitations),
            "limitations",
        )
        if not limitations:
            raise ValueError("pilot limitations must not be empty")
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "limitations", limitations)


@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationIdentity:
    """Stable human-authorization identity with exact recommendation lineage."""

    schema_version: str
    authorization_id: str
    evaluation_id: str
    validation_id: str
    candidate_id: str
    baseline_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION:
            raise ValueError("unsupported authorization schema_version")
        if _AUTHORIZATION_ID_PATTERN.fullmatch(self.authorization_id) is None:
            raise ValueError("authorization_id must use the governed pbd identifier")
        for field_name in (
            "evaluation_id",
            "validation_id",
            "candidate_id",
            "baseline_id",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_code(getattr(self, field_name), field_name),
            )


def stable_preservation_baseline_authorization_id(
    *,
    evaluation_id: str,
    validation_id: str,
    candidate_id: str,
    baseline_id: str,
    outcome: AuthorizationDecisionOutcome,
    authority: AuthorizationAuthority,
    condition_decisions: tuple[AuthorizationConditionDecision, ...],
    scope: AuthorizationScope,
    pilot: PilotAuthorization | None,
    retention_obligations: tuple[str, ...],
    supersession_eligible: bool,
    rationale: str,
) -> str:
    """Derive stable identity from canonical authorization semantics."""

    payload = {
        "schema_version": STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION,
        "evaluation_id": _normalize_code(evaluation_id, "evaluation_id"),
        "validation_id": _normalize_code(validation_id, "validation_id"),
        "candidate_id": _normalize_code(candidate_id, "candidate_id"),
        "baseline_id": _normalize_code(baseline_id, "baseline_id"),
        "outcome": outcome.value,
        "authority": {
            "authority_id": authority.authority_id,
            "display_name": authority.display_name,
            "authority_role": authority.authority_role,
            "authority_basis": authority.authority_basis,
            "organization": authority.organization,
        },
        "condition_decisions": [
            {
                "condition_sequence": item.condition_sequence,
                "condition_code": item.condition_code,
                "disposition": item.disposition.value,
                "rationale": item.rationale,
            }
            for item in condition_decisions
        ],
        "scope": {
            "accepted_source_root_ids": list(scope.accepted_source_root_ids),
            "excluded_source_root_ids": list(scope.excluded_source_root_ids),
            "scope_limitations": list(scope.scope_limitations),
        },
        "pilot": (
            None
            if pilot is None
            else {
                "purpose": pilot.purpose,
                "limitations": list(pilot.limitations),
            }
        ),
        "retention_obligations": list(retention_obligations),
        "supersession_eligible": supersession_eligible,
        "rationale": _normalize_required(rationale, "rationale"),
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return f"pbd-{hashlib.sha256(encoded).hexdigest()}"


@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationDecision:
    """Immutable accountable human decision without persistence authority."""

    identity: PreservationBaselineAuthorizationIdentity
    recommendation: PreservationBaselineAcceptanceRecommendation
    outcome: AuthorizationDecisionOutcome
    authority: AuthorizationAuthority
    decided_at_utc: datetime
    condition_decisions: tuple[AuthorizationConditionDecision, ...]
    scope: AuthorizationScope
    pilot: PilotAuthorization | None
    retention_obligations: tuple[str, ...]
    supersession_eligible: bool
    rationale: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.recommendation,
            PreservationBaselineAcceptanceRecommendation,
        ):
            raise ValueError("recommendation must be PreservationBaselineAcceptanceRecommendation")

        decided_at_utc = _require_utc(self.decided_at_utc, "decided_at_utc")
        condition_decisions = tuple(self.condition_decisions)
        sequences = tuple(item.condition_sequence for item in condition_decisions)
        if len(set(sequences)) != len(sequences):
            raise ValueError("condition_decisions must not contain duplicates")
        if sequences != tuple(sorted(sequences)):
            raise ValueError("condition_decisions must use canonical ordering")

        retention_obligations = _normalize_ordered_unique(
            tuple(self.retention_obligations),
            "retention_obligations",
        )
        rationale = _normalize_required(self.rationale, "rationale")

        recommendation_identity = self.recommendation.identity
        if self.identity.evaluation_id != recommendation_identity.evaluation_id:
            raise ValueError("authorization evaluation identity does not match recommendation")
        if self.identity.validation_id != recommendation_identity.validation_id:
            raise ValueError("authorization validation identity does not match recommendation")
        if self.identity.candidate_id != recommendation_identity.candidate_id:
            raise ValueError("authorization candidate identity does not match recommendation")
        if self.identity.baseline_id != recommendation_identity.baseline_id:
            raise ValueError("authorization baseline identity does not match recommendation")

        source_roots = set(self.recommendation.validation_result.candidate.scope.source_root_ids)
        accepted_roots = set(self.scope.accepted_source_root_ids)
        excluded_roots = set(self.scope.excluded_source_root_ids)
        if accepted_roots | excluded_roots != source_roots:
            raise ValueError("authorization scope must account for every candidate source root")
        if not accepted_roots.issubset(source_roots) or not excluded_roots.issubset(source_roots):
            raise ValueError("authorization scope references source roots outside candidate scope")

        recommendation_conditions = {
            condition.sequence: condition for condition in self.recommendation.conditions
        }
        for item in condition_decisions:
            condition = recommendation_conditions.get(item.condition_sequence)
            if condition is None:
                raise ValueError("condition decision references nonexistent condition")
            if item.condition_code != condition.condition_code:
                raise ValueError("condition decision code does not match recommendation")
            if (
                item.disposition is AuthorizationConditionDisposition.APPROVED
                and condition.disposition is not AcceptanceConditionDisposition.REVIEW_REQUIRED
            ):
                raise ValueError("only review-required conditions may be approved")

        approved_sequences = {
            item.condition_sequence
            for item in condition_decisions
            if item.disposition is AuthorizationConditionDisposition.APPROVED
        }
        review_sequences = {
            condition.sequence
            for condition in self.recommendation.conditions
            if condition.disposition is AcceptanceConditionDisposition.REVIEW_REQUIRED
        }
        blocking_sequences = {
            condition.sequence
            for condition in self.recommendation.conditions
            if condition.disposition is AcceptanceConditionDisposition.BLOCKING
        }

        _validate_outcome_compatibility(
            recommendation_decision=self.recommendation.decision,
            outcome=self.outcome,
        )

        if self.outcome is AuthorizationDecisionOutcome.AUTHORIZE:
            if accepted_roots != source_roots or excluded_roots:
                raise ValueError("authorize requires complete candidate scope")
            if condition_decisions:
                raise ValueError("authorize must not include condition decisions")
            if self.pilot is not None:
                raise ValueError("authorize must not include pilot metadata")
        elif self.outcome is AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS:
            if accepted_roots != source_roots or excluded_roots:
                raise ValueError("exception authorization requires complete candidate scope")
            if approved_sequences != review_sequences or not approved_sequences:
                raise ValueError("every review-required condition must be explicitly approved")
            if any(
                item.disposition is not AuthorizationConditionDisposition.APPROVED
                for item in condition_decisions
            ):
                raise ValueError(
                    "exception authorization must not contain rejected condition decisions"
                )
            if self.pilot is not None:
                raise ValueError("exception authorization must not include pilot metadata")
        elif self.outcome is AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE:
            if not accepted_roots or accepted_roots == source_roots:
                raise ValueError("partial authorization requires a non-empty proper subset")
            if not excluded_roots:
                raise ValueError("partial authorization requires excluded source roots")
            if not self.scope.scope_limitations:
                raise ValueError("partial authorization requires scope limitations")
            if blocking_sequences:
                raise ValueError("partial authorization cannot approve blocking conditions")
            if review_sequences and approved_sequences != review_sequences:
                raise ValueError(
                    "partial authorization must approve every review-required condition"
                )
            if self.pilot is not None:
                raise ValueError("partial authorization must not include pilot metadata")
        elif self.outcome is AuthorizationDecisionOutcome.AUTHORIZE_PILOT:
            if not accepted_roots:
                raise ValueError("pilot authorization requires accepted source roots")
            if self.pilot is None:
                raise ValueError("pilot authorization requires pilot metadata")
            if blocking_sequences:
                raise ValueError("pilot authorization cannot approve blocking conditions")
            if review_sequences and approved_sequences != review_sequences:
                raise ValueError("pilot authorization must approve every review-required condition")
        else:
            if accepted_roots:
                raise ValueError("rejection must not accept source roots")
            if self.pilot is not None:
                raise ValueError("rejection must not include pilot metadata")
            if any(
                item.disposition is AuthorizationConditionDisposition.APPROVED
                for item in condition_decisions
            ):
                raise ValueError("rejection must not approve conditions")

        stable_id = stable_preservation_baseline_authorization_id(
            evaluation_id=recommendation_identity.evaluation_id,
            validation_id=recommendation_identity.validation_id,
            candidate_id=recommendation_identity.candidate_id,
            baseline_id=recommendation_identity.baseline_id,
            outcome=self.outcome,
            authority=self.authority,
            condition_decisions=condition_decisions,
            scope=self.scope,
            pilot=self.pilot,
            retention_obligations=retention_obligations,
            supersession_eligible=self.supersession_eligible,
            rationale=rationale,
        )
        if self.identity.authorization_id != stable_id:
            raise ValueError("authorization_id does not match semantic decision")

        object.__setattr__(self, "decided_at_utc", decided_at_utc)
        object.__setattr__(self, "condition_decisions", condition_decisions)
        object.__setattr__(self, "retention_obligations", retention_obligations)
        object.__setattr__(self, "rationale", rationale)


def _validate_outcome_compatibility(
    *,
    recommendation_decision: AcceptanceDecision,
    outcome: AuthorizationDecisionOutcome,
) -> None:
    allowed = {
        AcceptanceDecision.RECOMMEND_ACCEPTANCE: {
            AuthorizationDecisionOutcome.AUTHORIZE,
            AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE,
            AuthorizationDecisionOutcome.AUTHORIZE_PILOT,
            AuthorizationDecisionOutcome.REJECT,
        },
        AcceptanceDecision.RECOMMEND_REVIEW: {
            AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS,
            AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE,
            AuthorizationDecisionOutcome.AUTHORIZE_PILOT,
            AuthorizationDecisionOutcome.REJECT,
        },
        AcceptanceDecision.RECOMMEND_REJECTION: {
            AuthorizationDecisionOutcome.REJECT,
        },
    }
    if outcome not in allowed[recommendation_decision]:
        raise ValueError("authorization outcome is incompatible with recommendation")
