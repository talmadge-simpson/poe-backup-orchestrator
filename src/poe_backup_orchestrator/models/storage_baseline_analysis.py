"""Immutable contracts for accepted-baseline analytical intake."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.storage_accepted_baseline import (
    AcceptedPreservationBaseline,
    AcceptedPreservationBaselineArtifact,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    EvidenceRequirementObservation,
    PreservationEvidenceType,
)

STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION: Final[str] = "1.0"
STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION: Final[str] = "1.0"

BASELINE_ANALYSIS_RESOURCE_PROFILE_VERSION: Final[str] = (
    "poe.storage.baseline-analysis.resource-profile/1.0"
)
BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID: Final[str] = (
    "f8d9caf9c32ff3da38b901efb001faf4f31cd131a567f2e2acfc0abaf06825d2"
)
BASELINE_ANALYSIS_FACT_PROJECTION_ID: Final[str] = (
    "00c4f0f475908c11ebc8f42aec8d4b4dd9b39f5fdfa3dbcd56fdde4feebfdaec"
)

type FrozenJsonScalar = str | int | bool | None


@dataclass(frozen=True, slots=True)
class FrozenJsonObject:
    """An immutable JSON object whose type remains explicit even when empty."""

    entries: tuple[tuple[str, FrozenJsonValue], ...]

    def __post_init__(self) -> None:
        entries = tuple(self.entries)
        if any(
            not isinstance(entry, tuple) or len(entry) != 2 or not isinstance(entry[0], str)
            for entry in entries
        ):
            raise ValueError("frozen JSON object entries must be string-keyed pairs")
        keys = tuple(entry[0] for entry in entries)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("frozen JSON object keys must be unique and ordered")
        for _, value in entries:
            _require_frozen_json(value)
        object.__setattr__(self, "entries", entries)


@dataclass(frozen=True, slots=True)
class FrozenJsonArray:
    """An immutable JSON array preserving its approved semantic order."""

    values: tuple[FrozenJsonValue, ...]

    def __post_init__(self) -> None:
        values = tuple(self.values)
        for value in values:
            _require_frozen_json(value)
        object.__setattr__(self, "values", values)


type FrozenJsonValue = FrozenJsonScalar | FrozenJsonObject | FrozenJsonArray

_PROFILE_ID = re.compile(r"pbaip-[0-9a-f]{64}")
_CONTEXT_ID = re.compile(r"pbac-[0-9a-f]{64}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


def _required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


def _sha256(value: str, field_name: str) -> str:
    normalized = value.strip()
    if _SHA256.fullmatch(normalized) is None:
        raise ValueError(f"{field_name} must contain 64 lowercase hexadecimal characters")
    return normalized


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_value(value: FrozenJsonValue) -> object:
    if isinstance(value, FrozenJsonObject):
        return {key: _json_value(item) for key, item in value.entries}
    if isinstance(value, FrozenJsonArray):
        return [_json_value(item) for item in value.values]
    return value


class AcceptedBaselineAnalysisEvidenceRequirement(StrEnum):
    """Profile disposition for one accepted-baseline evidence type."""

    REQUIRED = "required"
    LINEAGE_ONLY = "lineage_only"


class AcceptedBaselineAnalysisEvidenceStatus(StrEnum):
    """Valid context state for one governed evidence observation."""

    AUTHENTICATED = "authenticated"
    LINEAGE_ONLY = "lineage_only"


@dataclass(frozen=True, slots=True)
class AcceptedBaselineAnalysisProfileIdentity:
    """Stable identity of one immutable analytical-intake profile."""

    schema_version: str
    analysis_profile_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION:
            raise ValueError("unsupported analysis-profile schema_version")
        if _PROFILE_ID.fullmatch(self.analysis_profile_id) is None:
            raise ValueError("analysis_profile_id must use the governed pbaip identifier")


@dataclass(frozen=True, slots=True, order=True)
class AcceptedBaselineAnalysisEvidenceRule:
    """One deterministic evidence rule in an analytical-intake profile."""

    evidence_type: PreservationEvidenceType
    schema_name: str
    schema_version: str
    requirement: AcceptedBaselineAnalysisEvidenceRequirement

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_name", _required(self.schema_name, "schema_name"))
        object.__setattr__(
            self,
            "schema_version",
            _required(self.schema_version, "schema_version"),
        )


@dataclass(frozen=True, slots=True)
class AcceptedBaselineAnalysisProfile:
    """Immutable semantic policy and resource envelope for analytical intake."""

    identity: AcceptedBaselineAnalysisProfileIdentity
    profile_version: str
    resource_profile_version: str
    evidence_rules: tuple[AcceptedBaselineAnalysisEvidenceRule, ...]
    missing_evidence_behavior: str
    unsupported_evidence_behavior: str
    adapter_registry_id: str
    fact_projection_id: str
    maximum_inventory_evidence_bytes: int
    maximum_content_integrity_evidence_bytes: int
    maximum_inventory_items_per_root: int
    maximum_integrity_observations_per_root: int
    maximum_aggregate_evidence_bytes: int
    maximum_aggregate_projected_items: int
    maximum_inventory_ndjson_record_bytes: int
    json_nesting_depth_limit: int | None
    deterministic_ordering: str

    def __post_init__(self) -> None:
        profile_version = _required(self.profile_version, "profile_version")
        resource_version = _required(self.resource_profile_version, "resource_profile_version")
        missing = _required(self.missing_evidence_behavior, "missing_evidence_behavior")
        unsupported = _required(
            self.unsupported_evidence_behavior,
            "unsupported_evidence_behavior",
        )
        ordering = _required(self.deterministic_ordering, "deterministic_ordering")
        rules = tuple(self.evidence_rules)
        if not rules:
            raise ValueError("evidence_rules must not be empty")
        keys = tuple(
            (rule.evidence_type.value, rule.schema_name, rule.schema_version) for rule in rules
        )
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("evidence_rules must be unique and canonically ordered")
        if len({rule.evidence_type for rule in rules}) != len(rules):
            raise ValueError("evidence_rules must not contain duplicate evidence types")
        limits = (
            self.maximum_inventory_evidence_bytes,
            self.maximum_content_integrity_evidence_bytes,
            self.maximum_inventory_items_per_root,
            self.maximum_integrity_observations_per_root,
            self.maximum_aggregate_evidence_bytes,
            self.maximum_aggregate_projected_items,
            self.maximum_inventory_ndjson_record_bytes,
        )
        if any(value <= 0 for value in limits):
            raise ValueError("analysis resource limits must be greater than zero")
        if self.json_nesting_depth_limit is not None and self.json_nesting_depth_limit <= 0:
            raise ValueError("json_nesting_depth_limit must be positive when present")
        adapter_id = _sha256(self.adapter_registry_id, "adapter_registry_id")
        projection_id = _sha256(self.fact_projection_id, "fact_projection_id")
        expected = stable_accepted_baseline_analysis_profile_id(
            profile_version=profile_version,
            resource_profile_version=resource_version,
            evidence_rules=rules,
            missing_evidence_behavior=missing,
            unsupported_evidence_behavior=unsupported,
            adapter_registry_id=adapter_id,
            fact_projection_id=projection_id,
            maximum_inventory_evidence_bytes=self.maximum_inventory_evidence_bytes,
            maximum_content_integrity_evidence_bytes=(
                self.maximum_content_integrity_evidence_bytes
            ),
            maximum_inventory_items_per_root=self.maximum_inventory_items_per_root,
            maximum_integrity_observations_per_root=(self.maximum_integrity_observations_per_root),
            maximum_aggregate_evidence_bytes=self.maximum_aggregate_evidence_bytes,
            maximum_aggregate_projected_items=self.maximum_aggregate_projected_items,
            maximum_inventory_ndjson_record_bytes=(self.maximum_inventory_ndjson_record_bytes),
            json_nesting_depth_limit=self.json_nesting_depth_limit,
            deterministic_ordering=ordering,
        )
        if self.identity.analysis_profile_id != expected:
            raise ValueError("analysis_profile_id does not match profile semantics")
        object.__setattr__(self, "profile_version", profile_version)
        object.__setattr__(self, "resource_profile_version", resource_version)
        object.__setattr__(self, "evidence_rules", rules)
        object.__setattr__(self, "missing_evidence_behavior", missing)
        object.__setattr__(self, "unsupported_evidence_behavior", unsupported)
        object.__setattr__(self, "adapter_registry_id", adapter_id)
        object.__setattr__(self, "fact_projection_id", projection_id)
        object.__setattr__(self, "deterministic_ordering", ordering)


@dataclass(frozen=True, slots=True)
class AcceptedBaselineAnalysisContextIdentity:
    """Stable identity and predecessor keys for one analytical context."""

    schema_version: str
    analysis_context_id: str
    accepted_baseline_id: str
    analysis_profile_id: str

    def __post_init__(self) -> None:
        if self.schema_version != STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION:
            raise ValueError("unsupported analysis-context schema_version")
        if _CONTEXT_ID.fullmatch(self.analysis_context_id) is None:
            raise ValueError("analysis_context_id must use the governed pbac identifier")
        object.__setattr__(
            self,
            "accepted_baseline_id",
            _required(self.accepted_baseline_id, "accepted_baseline_id"),
        )
        if _PROFILE_ID.fullmatch(self.analysis_profile_id) is None:
            raise ValueError("analysis_profile_id must use the governed pbaip identifier")


@dataclass(frozen=True, slots=True)
class AcceptedBaselineAnalysisEvidence:
    """Authenticated semantic facts or unopened lineage for one observation."""

    observation: EvidenceRequirementObservation
    status: AcceptedBaselineAnalysisEvidenceStatus
    schema_name: str | None
    schema_version: str | None
    evidence_semantic_id: str | None
    fact_projection_id: str | None
    semantic_facts: FrozenJsonValue | None
    artifact_path: Path | None = None
    sidecar_path: Path | None = None
    transport_sha256: str | None = None
    verified_byte_count: int | None = None
    artifact_link_count: int | None = None
    sidecar_link_count: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.observation, EvidenceRequirementObservation):
            raise ValueError("observation must be EvidenceRequirementObservation")
        if self.status is AcceptedBaselineAnalysisEvidenceStatus.AUTHENTICATED:
            required = (
                self.schema_name,
                self.schema_version,
                self.evidence_semantic_id,
                self.fact_projection_id,
                self.semantic_facts,
                self.artifact_path,
                self.sidecar_path,
                self.transport_sha256,
                self.verified_byte_count,
                self.artifact_link_count,
                self.sidecar_link_count,
            )
            if any(value is None for value in required):
                raise ValueError("authenticated evidence requires semantic and transport fields")
            _require_frozen_json(self.semantic_facts)
            object.__setattr__(
                self, "schema_name", _required(self.schema_name or "", "schema_name")
            )
            object.__setattr__(
                self,
                "schema_version",
                _required(self.schema_version or "", "schema_version"),
            )
            object.__setattr__(
                self,
                "evidence_semantic_id",
                _sha256(self.evidence_semantic_id or "", "evidence_semantic_id"),
            )
            object.__setattr__(
                self,
                "fact_projection_id",
                _sha256(self.fact_projection_id or "", "fact_projection_id"),
            )
            for field_name in ("artifact_path", "sidecar_path"):
                path = Path(getattr(self, field_name))
                if not path.is_absolute():
                    raise ValueError(f"{field_name} must be absolute")
                object.__setattr__(self, field_name, path)
            object.__setattr__(
                self,
                "transport_sha256",
                _sha256(self.transport_sha256 or "", "transport_sha256"),
            )
            if self.verified_byte_count is None or self.verified_byte_count <= 0:
                raise ValueError("verified_byte_count must be positive")
            if self.artifact_link_count is None or self.artifact_link_count <= 0:
                raise ValueError("artifact_link_count must be positive")
            if self.sidecar_link_count is None or self.sidecar_link_count <= 0:
                raise ValueError("sidecar_link_count must be positive")
        else:
            if any(
                value is not None
                for value in (
                    self.schema_name,
                    self.schema_version,
                    self.evidence_semantic_id,
                    self.fact_projection_id,
                    self.semantic_facts,
                    self.artifact_path,
                    self.sidecar_path,
                    self.transport_sha256,
                    self.verified_byte_count,
                    self.artifact_link_count,
                    self.sidecar_link_count,
                )
            ):
                raise ValueError("lineage-only evidence must not contain authenticated fields")


@dataclass(frozen=True, slots=True)
class AcceptedBaselineAnalysisContext:
    """Complete deterministic in-memory analytical intake for one accepted baseline."""

    identity: AcceptedBaselineAnalysisContextIdentity
    reference_artifact: AcceptedPreservationBaselineArtifact
    accepted_baseline: AcceptedPreservationBaseline
    profile: AcceptedBaselineAnalysisProfile
    authenticated_evidence: tuple[AcceptedBaselineAnalysisEvidence, ...]
    lineage_only_evidence: tuple[AcceptedBaselineAnalysisEvidence, ...]

    def __post_init__(self) -> None:
        authenticated = tuple(self.authenticated_evidence)
        lineage = tuple(self.lineage_only_evidence)
        if not authenticated:
            raise ValueError("authenticated_evidence must not be empty")
        if any(
            item.status is not AcceptedBaselineAnalysisEvidenceStatus.AUTHENTICATED
            for item in authenticated
        ):
            raise ValueError("authenticated_evidence contains a non-authenticated record")
        if any(
            item.status is not AcceptedBaselineAnalysisEvidenceStatus.LINEAGE_ONLY
            for item in lineage
        ):
            raise ValueError("lineage_only_evidence contains an authenticated record")
        keys = tuple(_evidence_key(item) for item in authenticated)
        lineage_keys = tuple(_evidence_key(item) for item in lineage)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("authenticated_evidence must be unique and ordered")
        if lineage_keys != tuple(sorted(lineage_keys)) or len(lineage_keys) != len(
            set(lineage_keys)
        ):
            raise ValueError("lineage_only_evidence must be unique and ordered")
        if (
            self.identity.accepted_baseline_id
            != self.accepted_baseline.identity.accepted_baseline_id
        ):
            raise ValueError("context accepted_baseline_id does not match predecessor")
        if self.identity.analysis_profile_id != self.profile.identity.analysis_profile_id:
            raise ValueError("context analysis_profile_id does not match profile")
        expected = stable_accepted_baseline_analysis_context_id(
            accepted_baseline_id=self.identity.accepted_baseline_id,
            profile=self.profile,
            authenticated_evidence=authenticated,
            lineage_only_evidence=lineage,
        )
        if self.identity.analysis_context_id != expected:
            raise ValueError("analysis_context_id does not match context semantics")
        object.__setattr__(self, "authenticated_evidence", authenticated)
        object.__setattr__(self, "lineage_only_evidence", lineage)


def stable_accepted_baseline_analysis_profile_id(
    *,
    profile_version: str,
    resource_profile_version: str,
    evidence_rules: tuple[AcceptedBaselineAnalysisEvidenceRule, ...],
    missing_evidence_behavior: str,
    unsupported_evidence_behavior: str,
    adapter_registry_id: str,
    fact_projection_id: str,
    maximum_inventory_evidence_bytes: int,
    maximum_content_integrity_evidence_bytes: int,
    maximum_inventory_items_per_root: int,
    maximum_integrity_observations_per_root: int,
    maximum_aggregate_evidence_bytes: int,
    maximum_aggregate_projected_items: int,
    maximum_inventory_ndjson_record_bytes: int,
    json_nesting_depth_limit: int | None,
    deterministic_ordering: str,
) -> str:
    payload = {
        "schema_version": STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION,
        "profile_version": profile_version,
        "resource_profile_version": resource_profile_version,
        "evidence_rules": [
            {
                "evidence_type": rule.evidence_type.value,
                "schema_name": rule.schema_name,
                "schema_version": rule.schema_version,
                "requirement": rule.requirement.value,
            }
            for rule in evidence_rules
        ],
        "missing_evidence_behavior": missing_evidence_behavior,
        "unsupported_evidence_behavior": unsupported_evidence_behavior,
        "adapter_registry_id": adapter_registry_id,
        "fact_projection_id": fact_projection_id,
        "maximum_inventory_evidence_bytes": maximum_inventory_evidence_bytes,
        "maximum_content_integrity_evidence_bytes": maximum_content_integrity_evidence_bytes,
        "maximum_inventory_items_per_root": maximum_inventory_items_per_root,
        "maximum_integrity_observations_per_root": maximum_integrity_observations_per_root,
        "maximum_aggregate_evidence_bytes": maximum_aggregate_evidence_bytes,
        "maximum_aggregate_projected_items": maximum_aggregate_projected_items,
        "maximum_inventory_ndjson_record_bytes": maximum_inventory_ndjson_record_bytes,
        "json_nesting_depth_limit": json_nesting_depth_limit,
        "deterministic_ordering": deterministic_ordering,
    }
    return f"pbaip-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def stable_accepted_baseline_analysis_context_id(
    *,
    accepted_baseline_id: str,
    profile: AcceptedBaselineAnalysisProfile,
    authenticated_evidence: tuple[AcceptedBaselineAnalysisEvidence, ...],
    lineage_only_evidence: tuple[AcceptedBaselineAnalysisEvidence, ...],
) -> str:
    payload = {
        "schema_version": STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION,
        "accepted_baseline_id": accepted_baseline_id,
        "analysis_profile_id": profile.identity.analysis_profile_id,
        "profile_version": profile.profile_version,
        "adapter_registry_id": profile.adapter_registry_id,
        "fact_projection_id": profile.fact_projection_id,
        "authenticated_evidence": [
            {
                "source_root_id": item.observation.source_root_id,
                "evidence_type": item.observation.evidence_type.value,
                "observation_status": item.observation.status.value,
                "schema_name": item.schema_name,
                "schema_version": item.schema_version,
                "evidence_semantic_id": item.evidence_semantic_id,
                "semantic_facts": _json_value(item.semantic_facts),
            }
            for item in authenticated_evidence
        ],
        "lineage_only_evidence": [
            {
                "source_root_id": item.observation.source_root_id,
                "evidence_type": item.observation.evidence_type.value,
                "observation_status": item.observation.status.value,
                "detail": item.observation.detail,
            }
            for item in lineage_only_evidence
        ],
    }
    return f"pbac-{hashlib.sha256(_canonical_bytes(payload)).hexdigest()}"


def _evidence_key(item: AcceptedBaselineAnalysisEvidence) -> tuple[str, str]:
    return (item.observation.source_root_id, item.observation.evidence_type.value)


def _require_frozen_json(value: object) -> None:
    if value is None or isinstance(value, (str, int, bool)):
        return
    if isinstance(value, FrozenJsonObject):
        for _, item in value.entries:
            _require_frozen_json(item)
        return
    if isinstance(value, FrozenJsonArray):
        for item in value.values:
            _require_frozen_json(item)
        return
    raise ValueError("semantic_facts must be recursively immutable JSON values")
