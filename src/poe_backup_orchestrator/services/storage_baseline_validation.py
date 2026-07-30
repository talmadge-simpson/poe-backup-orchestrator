"""Service boundaries for preservation-baseline evidence validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceType,
)


class PreservationBaselineValidationError(Exception):
    """Raised when deterministic validation cannot safely be produced."""


class PreservationEvidenceAdapter(Protocol):
    """Typed adapter for one evidence category and schema family."""

    evidence_type: PreservationEvidenceType
    schema_name: str
    supported_versions: tuple[str, ...]

    def parse(self, evidence_bytes: bytes) -> object:
        """Parse authenticated evidence bytes."""

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        """Extract only facts required for technical validation."""


@dataclass(frozen=True, slots=True)
class ValidationAdapterRegistry:
    """Immutable deterministic evidence-adapter registry."""

    adapters: tuple[PreservationEvidenceAdapter, ...]

    def __post_init__(self) -> None:
        adapters = tuple(self.adapters)
        if not adapters:
            raise PreservationBaselineValidationError("at least one validation adapter is required")

        registrations: dict[
            tuple[PreservationEvidenceType, str, str],
            PreservationEvidenceAdapter,
        ] = {}

        for adapter in adapters:
            schema_name = adapter.schema_name.strip()
            versions = tuple(version.strip() for version in adapter.supported_versions)

            if not schema_name:
                raise PreservationBaselineValidationError("adapter schema_name must not be empty")
            if not versions or any(not version for version in versions):
                raise PreservationBaselineValidationError(
                    "adapter supported_versions must be explicit"
                )
            if len(set(versions)) != len(versions):
                raise PreservationBaselineValidationError(
                    "adapter supported_versions must not contain duplicates"
                )

            for version in versions:
                key = (adapter.evidence_type, schema_name, version)
                if key in registrations:
                    raise PreservationBaselineValidationError(
                        "duplicate or ambiguous validation adapter registration: "
                        f"{adapter.evidence_type.value}/{schema_name}/{version}"
                    )
                registrations[key] = adapter

        canonical = tuple(
            sorted(
                adapters,
                key=lambda adapter: (
                    adapter.evidence_type.value,
                    adapter.schema_name.strip(),
                    tuple(sorted(version.strip() for version in adapter.supported_versions)),
                ),
            )
        )
        object.__setattr__(self, "adapters", canonical)

    def resolve(
        self,
        *,
        evidence_type: PreservationEvidenceType,
        schema_name: str,
        schema_version: str,
    ) -> PreservationEvidenceAdapter:
        """Resolve exactly one adapter by evidence type, schema, and version."""

        normalized_schema = schema_name.strip()
        normalized_version = schema_version.strip()
        matches = tuple(
            adapter
            for adapter in self.adapters
            if adapter.evidence_type is evidence_type
            and adapter.schema_name.strip() == normalized_schema
            and normalized_version
            in tuple(version.strip() for version in adapter.supported_versions)
        )
        if len(matches) != 1:
            raise PreservationBaselineValidationError(
                "no unique validation adapter for "
                f"{evidence_type.value}/{normalized_schema}/{normalized_version}"
            )
        return matches[0]
