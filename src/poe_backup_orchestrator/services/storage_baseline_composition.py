from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
    EvidenceRequirementObservation,
    EvidenceRequirementStatus,
    PreservationBaselineCandidate,
    PreservationBaselineCandidateIdentity,
    PreservationBaselineCandidateScope,
    PreservationEvidenceReference,
    PreservationEvidenceRequirement,
    PreservationEvidenceType,
    stable_preservation_baseline_candidate_id,
)
from poe_backup_orchestrator.models.storage_inventory import (
    PreservationBaselineIdentity,
)
from poe_backup_orchestrator.services.storage_content_integrity_persistence import (
    PersistedContentIntegrityEvidence,
)
from poe_backup_orchestrator.services.storage_inventory_persistence import (
    STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION,
    InventoryEvidencePublication,
)

Clock = Callable[[], datetime]


class PreservationBaselineCompositionError(RuntimeError):
    pass


class PreservationBaselineComposer:
    def __init__(self, *, clock: Clock | None = None) -> None:
        self._clock = clock or _utc_now

    def compose(
        self,
        *,
        baseline_identity: PreservationBaselineIdentity,
        source_root_ids: tuple[str, ...],
        requirements: tuple[PreservationEvidenceRequirement, ...],
        evidence_references: tuple[PreservationEvidenceReference, ...],
    ) -> PreservationBaselineCandidate:
        scope = PreservationBaselineCandidateScope(
            baseline_id=baseline_identity.baseline_id,
            source_root_ids=tuple(sorted(source_root_ids)),
        )
        requirements_by_key = self._requirements_by_key(
            scope,
            requirements,
        )
        references_by_key = self._references_by_key(
            scope,
            evidence_references,
        )
        unexpected = references_by_key.keys() - requirements_by_key.keys()
        if unexpected:
            raise PreservationBaselineCompositionError(
                "evidence references do not match configured requirements"
            )
        observations = tuple(
            self._observation(
                requirements_by_key[key],
                references_by_key.get(key),
            )
            for key in sorted(
                requirements_by_key,
                key=lambda value: (value[0], value[1].value),
            )
        )
        candidate_id = stable_preservation_baseline_candidate_id(
            baseline_id=scope.baseline_id,
            source_root_ids=scope.source_root_ids,
            observations=observations,
        )
        return PreservationBaselineCandidate(
            identity=PreservationBaselineCandidateIdentity(
                schema_version=STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION,
                candidate_id=candidate_id,
                baseline_id=scope.baseline_id,
                created_at_utc=self._clock(),
            ),
            scope=scope,
            observations=observations,
        )

    @staticmethod
    def inventory_evidence_reference(
        *,
        source_root_id: str,
        publication: InventoryEvidencePublication,
    ) -> PreservationEvidenceReference:
        return PreservationEvidenceReference(
            evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            source_root_id=source_root_id,
            schema_version=STORAGE_INVENTORY_EVIDENCE_SCHEMA_VERSION,
            evidence_path=publication.evidence_path,
            digest_path=publication.sha256_path,
            sha256=publication.sha256,
            byte_count=publication.byte_count,
        )

    @staticmethod
    def content_integrity_evidence_reference(
        *,
        source_root_id: str,
        schema_version: str,
        publication: PersistedContentIntegrityEvidence,
    ) -> PreservationEvidenceReference:
        return PreservationEvidenceReference(
            evidence_type=PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
            source_root_id=source_root_id,
            schema_version=schema_version,
            evidence_path=publication.evidence_path,
            digest_path=publication.digest_path,
            sha256=publication.sha256,
            byte_count=publication.byte_count,
        )

    @staticmethod
    def _requirements_by_key(scope, requirements):
        if not requirements:
            raise PreservationBaselineCompositionError("requirements must not be empty")
        result = {}
        scoped_roots = set(scope.source_root_ids)
        for requirement in requirements:
            if requirement.source_root_id not in scoped_roots:
                raise PreservationBaselineCompositionError(
                    "requirement source root is outside candidate scope"
                )
            key = (
                requirement.source_root_id,
                requirement.evidence_type,
            )
            if key in result:
                raise PreservationBaselineCompositionError("duplicate evidence requirement")
            result[key] = requirement
        return result

    @staticmethod
    def _references_by_key(scope, evidence_references):
        result = {}
        scoped_roots = set(scope.source_root_ids)
        for reference in evidence_references:
            if reference.source_root_id not in scoped_roots:
                raise PreservationBaselineCompositionError(
                    "evidence reference source root is outside candidate scope"
                )
            key = (
                reference.source_root_id,
                reference.evidence_type,
            )
            if key in result:
                raise PreservationBaselineCompositionError("duplicate evidence reference")
            result[key] = reference
        return result

    @staticmethod
    def _observation(requirement, reference):
        if not requirement.applicable:
            if reference is not None:
                raise PreservationBaselineCompositionError(
                    "non-applicable requirement must not have evidence"
                )
            return EvidenceRequirementObservation(
                source_root_id=requirement.source_root_id,
                evidence_type=requirement.evidence_type,
                status=EvidenceRequirementStatus.NOT_APPLICABLE,
                evidence_reference=None,
                detail=requirement.detail,
            )
        if reference is None:
            return EvidenceRequirementObservation(
                source_root_id=requirement.source_root_id,
                evidence_type=requirement.evidence_type,
                status=EvidenceRequirementStatus.ABSENT,
                evidence_reference=None,
                detail="evidence reference was not supplied",
            )
        return EvidenceRequirementObservation(
            source_root_id=requirement.source_root_id,
            evidence_type=requirement.evidence_type,
            status=EvidenceRequirementStatus.PRESENT,
            evidence_reference=reference,
        )


def _utc_now() -> datetime:
    return datetime.now(UTC)
