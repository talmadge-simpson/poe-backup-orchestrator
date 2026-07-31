"""Reference-first accepted-baseline analytical intake and evidence authentication."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from poe_backup_orchestrator.models.storage_accepted_baseline import (
    AcceptedPreservationBaseline,
    AcceptedPreservationBaselineArtifact,
)
from poe_backup_orchestrator.models.storage_baseline_analysis import (
    BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID,
    BASELINE_ANALYSIS_FACT_PROJECTION_ID,
    BASELINE_ANALYSIS_RESOURCE_PROFILE_VERSION,
    STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION,
    STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION,
    AcceptedBaselineAnalysisContext,
    AcceptedBaselineAnalysisContextIdentity,
    AcceptedBaselineAnalysisEvidence,
    AcceptedBaselineAnalysisEvidenceRequirement,
    AcceptedBaselineAnalysisEvidenceRule,
    AcceptedBaselineAnalysisEvidenceStatus,
    AcceptedBaselineAnalysisProfile,
    AcceptedBaselineAnalysisProfileIdentity,
    FrozenJsonArray,
    FrozenJsonObject,
    FrozenJsonValue,
    stable_accepted_baseline_analysis_context_id,
    stable_accepted_baseline_analysis_profile_id,
)
from poe_backup_orchestrator.models.storage_baseline_candidate import (
    EvidenceRequirementObservation,
    EvidenceRequirementStatus,
    PreservationEvidenceReference,
    PreservationEvidenceType,
)
from poe_backup_orchestrator.services.storage_accepted_baseline import (
    AcceptedPreservationBaselineError,
    AcceptedPreservationBaselinePublisher,
)
from poe_backup_orchestrator.services.storage_baseline_validation import (
    CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
    INVENTORY_EVIDENCE_SCHEMA_NAME,
    ContentIntegrityEvidenceAdapter,
    DeserializedPreservationEvidence,
    EvidenceDeserializationStatus,
    EvidenceLoadStatus,
    InventoryEvidenceAdapter,
    LoadedPreservationEvidence,
    PreservationEvidenceDeserializationService,
    ValidationAdapterRegistry,
)

_READ_CHUNK_BYTES: Final[int] = 1024 * 1024
_SIDECAR_MAX_BYTES: Final[int] = 4096


class AcceptedBaselineAnalysisIntakeError(RuntimeError):
    """Base failure for accepted-baseline analytical intake."""


class AcceptedBaselineReferenceVerificationError(AcceptedBaselineAnalysisIntakeError):
    """Certified accepted-baseline reference verification failed."""


class AcceptedBaselineEvidenceAuthenticationError(AcceptedBaselineAnalysisIntakeError):
    """Required accepted evidence could not be authenticated exactly."""


class AcceptedBaselineAnalysisContextError(AcceptedBaselineAnalysisIntakeError):
    """Authenticated evidence could not form the governed analytical context."""


@dataclass(frozen=True, slots=True)
class _AuthenticatedArtifact:
    content: bytes
    sha256: str
    byte_count: int
    artifact_link_count: int
    sidecar_link_count: int


@dataclass(slots=True)
class AcceptedBaselineAnalysisIntakeService:
    """Build one deterministic context from the authoritative reference boundary."""

    publisher: AcceptedPreservationBaselinePublisher = field(
        default_factory=AcceptedPreservationBaselinePublisher
    )
    profile: AcceptedBaselineAnalysisProfile = field(default_factory=lambda: _default_profile())
    registry: ValidationAdapterRegistry = field(default_factory=lambda: _default_registry())

    def __post_init__(self) -> None:
        if not isinstance(self.publisher, AcceptedPreservationBaselinePublisher):
            raise ValueError("publisher must be AcceptedPreservationBaselinePublisher")
        if not isinstance(self.profile, AcceptedBaselineAnalysisProfile):
            raise ValueError("profile must be AcceptedBaselineAnalysisProfile")
        if not isinstance(self.registry, ValidationAdapterRegistry):
            raise ValueError("registry must be ValidationAdapterRegistry")
        _verify_behavior_manifests()
        _verify_registry(self.registry)
        if self.profile.adapter_registry_id != BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID:
            raise ValueError("profile adapter_registry_id is not architecture-approved")
        if self.profile.fact_projection_id != BASELINE_ANALYSIS_FACT_PROJECTION_ID:
            raise ValueError("profile fact_projection_id is not architecture-approved")

    def build_context(
        self,
        reference_artifact: AcceptedPreservationBaselineArtifact,
    ) -> AcceptedBaselineAnalysisContext:
        """Verify the reference and selected evidence, then construct one context."""

        if not isinstance(reference_artifact, AcceptedPreservationBaselineArtifact):
            raise AcceptedBaselineReferenceVerificationError(
                "reference_artifact must be AcceptedPreservationBaselineArtifact"
            )
        try:
            baseline = self.publisher.load_from_reference(reference_artifact)
        except AcceptedPreservationBaselineError as exc:
            raise AcceptedBaselineReferenceVerificationError(
                "accepted-baseline reference verification failed"
            ) from exc

        try:
            return self._build_verified(reference_artifact, baseline)
        except AcceptedBaselineAnalysisIntakeError:
            raise
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AcceptedBaselineEvidenceAuthenticationError(
                "accepted evidence authentication failed"
            ) from exc

    def _build_verified(
        self,
        reference_artifact: AcceptedPreservationBaselineArtifact,
        baseline: AcceptedPreservationBaseline,
    ) -> AcceptedBaselineAnalysisContext:
        accepted = set(baseline.accepted_source_root_ids)
        excluded = set(baseline.excluded_source_root_ids)
        if not accepted or accepted & excluded:
            raise AcceptedBaselineEvidenceAuthenticationError(
                "accepted and excluded source-root scope is invalid"
            )

        observations = tuple(baseline.accepted_evidence_graph)
        keys = tuple((item.source_root_id, item.evidence_type.value) for item in observations)
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise AcceptedBaselineEvidenceAuthenticationError(
                "accepted evidence observations must be unique and ordered"
            )
        if any(item.source_root_id not in accepted for item in observations):
            raise AcceptedBaselineEvidenceAuthenticationError(
                "accepted evidence graph contains excluded or unknown source scope"
            )

        by_key = {(item.source_root_id, item.evidence_type): item for item in observations}
        rules = {rule.evidence_type: rule for rule in self.profile.evidence_rules}
        required_types = tuple(
            sorted(
                (
                    rule.evidence_type
                    for rule in self.profile.evidence_rules
                    if rule.requirement is AcceptedBaselineAnalysisEvidenceRequirement.REQUIRED
                ),
                key=lambda item: item.value,
            )
        )
        selected: list[
            tuple[EvidenceRequirementObservation, AcceptedBaselineAnalysisEvidenceRule]
        ] = []
        for root in sorted(accepted):
            for evidence_type in required_types:
                observation = by_key.get((root, evidence_type))
                if (
                    observation is None
                    or observation.status is not EvidenceRequirementStatus.PRESENT
                ):
                    raise AcceptedBaselineEvidenceAuthenticationError(
                        f"required accepted evidence is not PRESENT: {root}/{evidence_type.value}"
                    )
                if observation.evidence_reference is None:
                    raise AcceptedBaselineEvidenceAuthenticationError(
                        f"required accepted evidence has no reference: {root}/{evidence_type.value}"
                    )
                selected.append((observation, rules[evidence_type]))

        aggregate_bytes = 0
        aggregate_items = 0
        authenticated: list[AcceptedBaselineAnalysisEvidence] = []
        projected_by_root: dict[str, dict[PreservationEvidenceType, FrozenJsonValue]] = {}
        for observation, rule in selected:
            reference = observation.evidence_reference
            assert reference is not None
            artifact_limit = _artifact_limit(self.profile, observation.evidence_type)
            if reference.byte_count > artifact_limit:
                raise AcceptedBaselineEvidenceAuthenticationError(
                    f"declared evidence byte count exceeds profile: {reference.evidence_path}"
                )
            if (
                aggregate_bytes + reference.byte_count
                > self.profile.maximum_aggregate_evidence_bytes
            ):
                raise AcceptedBaselineEvidenceAuthenticationError(
                    "declared evidence exceeds aggregate context byte budget"
                )
            verified = _authenticate_reference(
                reference=reference,
                evidence_type=observation.evidence_type,
                artifact_limit=artifact_limit,
                aggregate_remaining=(
                    self.profile.maximum_aggregate_evidence_bytes - aggregate_bytes
                ),
            )
            aggregate_bytes += verified.byte_count
            parsed, schema_name, schema_version = _deserialize(
                reference=reference,
                content=verified.content,
                registry=self.registry,
                rule=rule,
                profile=self.profile,
                item_limit=_item_limit(self.profile, observation.evidence_type),
                aggregate_item_remaining=(
                    self.profile.maximum_aggregate_projected_items - aggregate_items
                ),
            )
            item_count = _projected_item_count(observation.evidence_type, parsed)
            aggregate_items += item_count
            semantic_id = hashlib.sha256(_canonical_frozen_bytes(parsed)).hexdigest()
            item = AcceptedBaselineAnalysisEvidence(
                observation=observation,
                status=AcceptedBaselineAnalysisEvidenceStatus.AUTHENTICATED,
                schema_name=schema_name,
                schema_version=schema_version,
                evidence_semantic_id=semantic_id,
                fact_projection_id=self.profile.fact_projection_id,
                semantic_facts=parsed,
                artifact_path=reference.evidence_path,
                sidecar_path=reference.digest_path,
                transport_sha256=verified.sha256,
                verified_byte_count=verified.byte_count,
                artifact_link_count=verified.artifact_link_count,
                sidecar_link_count=verified.sidecar_link_count,
            )
            authenticated.append(item)
            projected_by_root.setdefault(observation.source_root_id, {})[
                observation.evidence_type
            ] = parsed

        for root in sorted(accepted):
            _validate_root_lineage(root, projected_by_root.get(root, {}), baseline)

        lineage_only = tuple(
            AcceptedBaselineAnalysisEvidence(
                observation=item,
                status=AcceptedBaselineAnalysisEvidenceStatus.LINEAGE_ONLY,
                schema_name=None,
                schema_version=None,
                evidence_semantic_id=None,
                fact_projection_id=None,
                semantic_facts=None,
            )
            for item in observations
            if rules.get(item.evidence_type) is not None
            and rules[item.evidence_type].requirement
            is AcceptedBaselineAnalysisEvidenceRequirement.LINEAGE_ONLY
        )
        authenticated_tuple = tuple(authenticated)
        context_id = stable_accepted_baseline_analysis_context_id(
            accepted_baseline_id=baseline.identity.accepted_baseline_id,
            profile=self.profile,
            authenticated_evidence=authenticated_tuple,
            lineage_only_evidence=lineage_only,
        )
        try:
            return AcceptedBaselineAnalysisContext(
                identity=AcceptedBaselineAnalysisContextIdentity(
                    schema_version=STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION,
                    analysis_context_id=context_id,
                    accepted_baseline_id=baseline.identity.accepted_baseline_id,
                    analysis_profile_id=self.profile.identity.analysis_profile_id,
                ),
                reference_artifact=reference_artifact,
                accepted_baseline=baseline,
                profile=self.profile,
                authenticated_evidence=authenticated_tuple,
                lineage_only_evidence=lineage_only,
            )
        except ValueError as exc:
            raise AcceptedBaselineAnalysisContextError(
                "authenticated evidence could not form the analytical context"
            ) from exc


def _default_registry() -> ValidationAdapterRegistry:
    return ValidationAdapterRegistry(
        adapters=(InventoryEvidenceAdapter(), ContentIntegrityEvidenceAdapter())
    )


def _default_profile() -> AcceptedBaselineAnalysisProfile:
    rules = tuple(
        sorted(
            (
                AcceptedBaselineAnalysisEvidenceRule(
                    PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE,
                    CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
                    "1.0",
                    AcceptedBaselineAnalysisEvidenceRequirement.REQUIRED,
                ),
                AcceptedBaselineAnalysisEvidenceRule(
                    PreservationEvidenceType.INVENTORY_EVIDENCE,
                    INVENTORY_EVIDENCE_SCHEMA_NAME,
                    "1.0",
                    AcceptedBaselineAnalysisEvidenceRequirement.REQUIRED,
                ),
                *(
                    AcceptedBaselineAnalysisEvidenceRule(
                        evidence_type,
                        "lineage-only",
                        "1.0",
                        AcceptedBaselineAnalysisEvidenceRequirement.LINEAGE_ONLY,
                    )
                    for evidence_type in (
                        PreservationEvidenceType.BASELINE_MANIFEST,
                        PreservationEvidenceType.CONTENT_CAPTURE_RESULT,
                        PreservationEvidenceType.DISCOVERY_RESULT,
                        PreservationEvidenceType.EXCEPTION_EVIDENCE,
                        PreservationEvidenceType.RECONCILIATION_EVIDENCE,
                    )
                ),
            ),
            key=lambda rule: (rule.evidence_type.value, rule.schema_name, rule.schema_version),
        )
    )
    kwargs: dict[str, Any] = {
        "profile_version": "1.0",
        "resource_profile_version": BASELINE_ANALYSIS_RESOURCE_PROFILE_VERSION,
        "evidence_rules": rules,
        "missing_evidence_behavior": "fail_closed",
        "unsupported_evidence_behavior": "fail_closed",
        "adapter_registry_id": BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID,
        "fact_projection_id": BASELINE_ANALYSIS_FACT_PROJECTION_ID,
        "maximum_inventory_evidence_bytes": 40_000_000,
        "maximum_content_integrity_evidence_bytes": 40_000_000,
        "maximum_inventory_items_per_root": 25_000,
        "maximum_integrity_observations_per_root": 25_000,
        "maximum_aggregate_evidence_bytes": 80_000_000,
        "maximum_aggregate_projected_items": 50_000,
        "maximum_inventory_ndjson_record_bytes": 1_647,
        "json_nesting_depth_limit": None,
        "deterministic_ordering": "lexical-semantic-v1",
    }
    profile_id = stable_accepted_baseline_analysis_profile_id(**kwargs)
    return AcceptedBaselineAnalysisProfile(
        identity=AcceptedBaselineAnalysisProfileIdentity(
            STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION,
            profile_id,
        ),
        **kwargs,
    )


def _artifact_limit(
    profile: AcceptedBaselineAnalysisProfile,
    evidence_type: PreservationEvidenceType,
) -> int:
    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        return profile.maximum_inventory_evidence_bytes
    if evidence_type is PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE:
        return profile.maximum_content_integrity_evidence_bytes
    raise AcceptedBaselineEvidenceAuthenticationError("unsupported analytical evidence type")


def _item_limit(
    profile: AcceptedBaselineAnalysisProfile,
    evidence_type: PreservationEvidenceType,
) -> int:
    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        return profile.maximum_inventory_items_per_root
    return profile.maximum_integrity_observations_per_root


def _authenticate_reference(
    *,
    reference: PreservationEvidenceReference,
    evidence_type: PreservationEvidenceType,
    artifact_limit: int,
    aggregate_remaining: int,
) -> _AuthenticatedArtifact:
    content, artifact_stat = _read_regular(
        reference.evidence_path,
        max_bytes=min(artifact_limit, aggregate_remaining),
    )
    if len(content) != reference.byte_count:
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence byte count mismatch: {reference.evidence_path}"
        )
    digest = hashlib.sha256(content).hexdigest()
    if digest != reference.sha256:
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence SHA-256 mismatch: {reference.evidence_path}"
        )
    sidecar, sidecar_stat = _read_regular(reference.digest_path, max_bytes=_SIDECAR_MAX_BYTES)
    expected = (
        f"{digest}  {reference.evidence_path.name}\n".encode("ascii")
        if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE
        else f"{digest}\n".encode("ascii")
    )
    if sidecar != expected:
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence sidecar is not producer-canonical: {reference.digest_path}"
        )
    return _AuthenticatedArtifact(
        content=content,
        sha256=digest,
        byte_count=len(content),
        artifact_link_count=artifact_stat.st_nlink,
        sidecar_link_count=sidecar_stat.st_nlink,
    )


def _read_regular(path: Path, *, max_bytes: int) -> tuple[bytes, os.stat_result]:
    target = Path(path)
    if not target.is_absolute():
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence path must be absolute: {target}"
        )
    before = os.lstat(target)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence path must be a non-symlink regular file: {target}"
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(target, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise AcceptedBaselineEvidenceAuthenticationError(
                f"evidence descriptor must identify a regular file: {target}"
            )
        if (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise AcceptedBaselineEvidenceAuthenticationError(
                f"evidence path changed during open: {target}"
            )
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(_READ_CHUNK_BYTES, max_bytes + 1 - total))
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise AcceptedBaselineEvidenceAuthenticationError(
                    f"evidence exceeds approved byte limit: {target}"
                )
            chunks.append(chunk)
        after_descriptor = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    after_path = os.lstat(target)
    stable = (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    )
    if stable != (
        after_descriptor.st_dev,
        after_descriptor.st_ino,
        after_descriptor.st_size,
        after_descriptor.st_mtime_ns,
        after_descriptor.st_ctime_ns,
    ) or (after_path.st_dev, after_path.st_ino) != (opened.st_dev, opened.st_ino):
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence changed during authentication: {target}"
        )
    return b"".join(chunks), opened


def _deserialize(
    *,
    reference: PreservationEvidenceReference,
    content: bytes,
    registry: ValidationAdapterRegistry,
    rule: AcceptedBaselineAnalysisEvidenceRule,
    profile: AcceptedBaselineAnalysisProfile,
    item_limit: int,
    aggregate_item_remaining: int,
) -> tuple[FrozenJsonValue, str, str]:
    _require_canonical(
        content,
        reference.evidence_type,
        profile,
        item_limit=item_limit,
        aggregate_item_remaining=aggregate_item_remaining,
    )
    loaded = LoadedPreservationEvidence(
        reference=reference,
        status=EvidenceLoadStatus.VERIFIED,
        evidence_bytes=content,
        calculated_sha256=reference.sha256,
        calculated_byte_count=len(content),
        sidecar_sha256=reference.sha256,
    )
    result: DeserializedPreservationEvidence = PreservationEvidenceDeserializationService(
        registry=registry
    ).deserialize(loaded)
    if (
        result.status is not EvidenceDeserializationStatus.DESERIALIZED
        or result.parsed_evidence is None
        or result.schema_name != rule.schema_name
        or result.schema_version != rule.schema_version
    ):
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"evidence schema or typed deserialization failed: {reference.evidence_path}"
        )
    projected = _freeze_authenticated_semantics(reference.evidence_type, content)
    _validate_projected_shape(reference.evidence_type, projected)
    return projected, result.schema_name, result.schema_version


def _freeze_authenticated_semantics(
    evidence_type: PreservationEvidenceType,
    content: bytes,
) -> FrozenJsonValue:
    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        return FrozenJsonArray(
            tuple(_freeze_json(json.loads(line.decode("utf-8"))) for line in content.splitlines())
        )
    return _freeze_json(json.loads(content.decode("utf-8")))


def _freeze_json(value: object) -> FrozenJsonValue:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        raise ValueError("floating-point semantic facts are not approved")
    if isinstance(value, list):
        return FrozenJsonArray(tuple(_freeze_json(item) for item in value))
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("semantic fact object keys must be strings")
        return FrozenJsonObject(tuple((key, _freeze_json(value[key])) for key in sorted(value)))
    raise ValueError("unsupported semantic JSON value")


def _require_canonical(
    content: bytes,
    evidence_type: PreservationEvidenceType,
    profile: AcceptedBaselineAnalysisProfile,
    *,
    item_limit: int,
    aggregate_item_remaining: int,
) -> None:
    def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field: {key}")
            result[key] = value
        return result

    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        if not content.endswith(b"\n") or content.endswith(b"\n\n"):
            raise AcceptedBaselineEvidenceAuthenticationError(
                "inventory evidence must have exactly one final newline"
            )
        records = content.splitlines(keepends=True)
        item_count = len(records) - 1
        if item_count > item_limit or item_count > aggregate_item_remaining:
            raise AcceptedBaselineEvidenceAuthenticationError(
                "inventory item count exceeds approved profile before decoding"
            )
        canonical_lines: list[bytes] = []
        for record in records:
            if len(record) > profile.maximum_inventory_ndjson_record_bytes:
                raise AcceptedBaselineEvidenceAuthenticationError(
                    "inventory evidence record exceeds approved byte limit"
                )
            if not record.endswith(b"\n"):
                raise AcceptedBaselineEvidenceAuthenticationError(
                    "inventory evidence record is not newline terminated"
                )
            value = json.loads(record[:-1].decode("utf-8"), object_pairs_hook=object_pairs)
            canonical_lines.append(
                json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
                    "utf-8"
                )
                + b"\n"
            )
        if b"".join(canonical_lines) != content:
            raise AcceptedBaselineEvidenceAuthenticationError("inventory evidence is not canonical")
        return
    value = json.loads(content.decode("utf-8"), object_pairs_hook=object_pairs)
    if not isinstance(value, dict) or not isinstance(value.get("evidence"), list):
        raise AcceptedBaselineEvidenceAuthenticationError(
            "content-integrity evidence has an invalid document shape"
        )
    item_count = len(value["evidence"])
    if item_count > item_limit or item_count > aggregate_item_remaining:
        raise AcceptedBaselineEvidenceAuthenticationError(
            "content-integrity item count exceeds approved profile before projection"
        )
    canonical = (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode("utf-8")
    if canonical != content:
        raise AcceptedBaselineEvidenceAuthenticationError(
            "content-integrity evidence is not canonical"
        )


def _validate_projected_shape(
    evidence_type: PreservationEvidenceType,
    parsed: object,
) -> None:
    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        records = _frozen_array(parsed, "inventory evidence")
        if not records:
            raise ValueError("inventory evidence is empty")
        header = _frozen_object(records[0], "inventory header")
        _exact_keys(
            header,
            {
                "record_kind",
                "schema_version",
                "discovery_request_id",
                "source_root_id",
                "item_count",
                "totals",
                "exception_summaries",
            },
            "inventory header",
        )
        _exact_keys(
            _frozen_object(header["totals"], "inventory totals"),
            {
                "directory_count",
                "file_count",
                "symbolic_link_count",
                "junction_count",
                "other_item_count",
                "total_file_bytes",
                "captured_count",
                "excluded_count",
                "inaccessible_count",
                "error_count",
                "pending_count",
            },
            "inventory totals",
        )
        for summary in _frozen_array(header["exception_summaries"], "exception summaries"):
            _exact_keys(
                _frozen_object(summary, "exception summary"),
                {"category", "count", "example_paths", "detail"},
                "exception summary",
            )
        for raw in records[1:]:
            envelope = _frozen_object(raw, "inventory record")
            if envelope.get("support_status") == "unsupported":
                _exact_keys(
                    envelope,
                    {
                        "record_kind",
                        "support_status",
                        "item_id",
                        "relative_path",
                        "item_type",
                        "detail",
                    },
                    "unsupported inventory record",
                )
                continue
            _exact_keys(
                envelope,
                {
                    "record_kind",
                    "support_status",
                    "item_id",
                    "relative_path",
                    "item_type",
                    "record",
                },
                "supported inventory record",
            )
            record = _frozen_object(envelope["record"], "inventory record payload")
            common = {"identity", "metadata", "capture_status", "exclusion_reason", "error_detail"}
            if envelope.get("item_type") == "file":
                expected = common | {"size_bytes", "sha256", "captured_at_utc"}
            elif envelope.get("item_type") == "directory":
                expected = common | {
                    "direct_file_count",
                    "direct_directory_count",
                    "descendant_file_count",
                    "descendant_directory_count",
                    "descendant_size_bytes",
                }
            else:
                raise ValueError("supported inventory record has unsupported item_type")
            _exact_keys(record, expected, "inventory record payload")
            _exact_keys(
                _frozen_object(record["identity"], "inventory identity"),
                {
                    "baseline_id",
                    "capture_session_id",
                    "source_device_id",
                    "source_volume_id",
                    "source_root_id",
                    "relative_path",
                    "item_type",
                },
                "inventory identity",
            )
            _exact_keys(
                _frozen_object(record["metadata"], "inventory metadata"),
                {"created_at_utc", "modified_at_utc", "accessed_at_utc", "owner", "permissions"},
                "inventory metadata",
            )
        return

    document = _frozen_object(parsed, "content-integrity evidence")
    _exact_keys(
        document,
        {
            "schema_version",
            "source_root_id",
            "verification_started_at_utc",
            "verification_completed_at_utc",
            "evidence",
            "totals",
        },
        "content-integrity evidence",
    )
    _exact_keys(
        _frozen_object(document["totals"], "content-integrity totals"),
        {
            "candidate_file_count",
            "verified_count",
            "source_changed_count",
            "size_mismatch_count",
            "digest_mismatch_count",
            "missing_count",
            "inaccessible_count",
            "not_regular_file_count",
            "filesystem_error_count",
            "total_expected_bytes",
            "total_observed_bytes",
        },
        "content-integrity totals",
    )
    fields = {
        "schema_version",
        "item_id",
        "relative_path",
        "expected_size_bytes",
        "observed_size_bytes",
        "expected_sha256",
        "observed_sha256",
        "verification_started_at_utc",
        "verification_completed_at_utc",
        "outcome",
        "failure_code",
        "detail",
        "source_observation_before",
        "source_observation_after",
    }
    observation_fields = {"size_bytes", "modified_at_ns", "mode", "device_id", "inode"}
    for raw in _frozen_array(document["evidence"], "content-integrity evidence array"):
        item = _frozen_object(raw, "content-integrity item")
        _exact_keys(item, fields, "content-integrity item")
        for name in ("source_observation_before", "source_observation_after"):
            if item[name] is not None:
                _exact_keys(
                    _frozen_object(item[name], name),
                    observation_fields,
                    name,
                )


def _exact_keys(
    value: dict[str, FrozenJsonValue],
    expected: set[str],
    description: str,
) -> None:
    if set(value) != expected:
        raise ValueError(f"{description} fields do not match the semantic manifest")


def _projected_item_count(
    evidence_type: PreservationEvidenceType,
    parsed: FrozenJsonValue,
) -> int:
    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        records = _frozen_array(parsed, "inventory evidence")
        if not records:
            raise ValueError("inventory evidence is empty")
        return len(records) - 1
    document = _frozen_object(parsed, "content-integrity evidence")
    return len(_frozen_array(document["evidence"], "content-integrity evidence array"))


def _validate_root_lineage(
    root: str,
    evidence: dict[PreservationEvidenceType, FrozenJsonValue],
    baseline: AcceptedPreservationBaseline,
) -> None:
    inventory = evidence.get(PreservationEvidenceType.INVENTORY_EVIDENCE)
    integrity = evidence.get(PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE)
    if inventory is None or integrity is None:
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"required projected facts are incomplete for accepted root: {root}"
        )
    inventory_records = _frozen_array(inventory, "inventory evidence")
    header = _frozen_object(inventory_records[0], "inventory header")
    integrity_document = _frozen_object(integrity, "content-integrity evidence")
    if header.get("source_root_id") != root or integrity_document.get("source_root_id") != root:
        raise AcceptedBaselineEvidenceAuthenticationError(
            f"projected evidence source-root lineage contradicts accepted scope: {root}"
        )
    inventory_by_path: dict[str, str] = {}
    for value in inventory_records[1:]:
        envelope = _frozen_object(value, "inventory record")
        path = _string(envelope, "relative_path")
        item_id = _string(envelope, "item_id")
        if path in inventory_by_path:
            raise AcceptedBaselineEvidenceAuthenticationError(
                f"duplicate inventory fact identity for accepted root: {root}"
            )
        inventory_by_path[path] = item_id
        if envelope.get("support_status") == "supported":
            record = _frozen_object(envelope["record"], "supported inventory record")
            identity = _frozen_object(record["identity"], "inventory identity")
            if (
                identity.get("source_root_id") != root
                or identity.get("relative_path") != path
                or identity.get("item_type") != envelope.get("item_type")
            ):
                raise AcceptedBaselineEvidenceAuthenticationError(
                    f"inventory item lineage contradicts accepted root: {root}"
                )
    seen_integrity: set[str] = set()
    for value in _frozen_array(integrity_document["evidence"], "integrity evidence"):
        record = _frozen_object(value, "integrity record")
        path = _string(record, "relative_path")
        item_id = _string(record, "item_id")
        if path in seen_integrity or inventory_by_path.get(path) != item_id:
            raise AcceptedBaselineEvidenceAuthenticationError(
                f"content-integrity lineage does not reconcile to inventory: {root}"
            )
        seen_integrity.add(path)
    if root not in baseline.accepted_source_root_ids:
        raise AcceptedBaselineEvidenceAuthenticationError("projected root is not accepted")


def _frozen_object(value: FrozenJsonValue, description: str) -> dict[str, FrozenJsonValue]:
    if not isinstance(value, FrozenJsonObject):
        raise ValueError(f"{description} must be an immutable object")
    return dict(value.entries)


def _frozen_array(value: FrozenJsonValue, description: str) -> tuple[FrozenJsonValue, ...]:
    if not isinstance(value, FrozenJsonArray):
        raise ValueError(f"{description} must be an immutable array")
    return value.values


def _string(value: dict[str, FrozenJsonValue], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ValueError(f"{key} must be a nonempty string")
    return item


def _canonical_frozen_bytes(value: FrozenJsonValue) -> bytes:
    return json.dumps(
        _thaw(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _thaw(value: FrozenJsonValue) -> object:
    if isinstance(value, FrozenJsonObject):
        return {key: _thaw(item) for key, item in value.entries}
    if isinstance(value, FrozenJsonArray):
        return [_thaw(item) for item in value.values]
    return value


def _verify_registry(registry: ValidationAdapterRegistry) -> None:
    registrations = tuple(
        (adapter.evidence_type.value, adapter.schema_name, tuple(adapter.supported_versions))
        for adapter in registry.adapters
    )
    expected = (
        (
            PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE.value,
            CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
            ("1.0",),
        ),
        (
            PreservationEvidenceType.INVENTORY_EVIDENCE.value,
            INVENTORY_EVIDENCE_SCHEMA_NAME,
            ("1.0",),
        ),
    )
    if registrations != expected:
        raise ValueError("registry does not match the architecture-approved semantic manifest")


def _verify_behavior_manifests() -> None:
    adapter = {
        "manifest_schema_version": "poe.storage.baseline-analysis.adapter-registry/1.0",
        "registrations": [
            {
                "canonical_bytes_required": True,
                "evidence_type": "content_integrity_evidence",
                "parse_contract_id": "poe.storage.content-integrity-evidence.typed-parse/1.0",
                "schema_name": "poe.storage.content-integrity-evidence",
                "schema_version": "1.0",
                "sidecar_rule_id": (
                    "poe.storage.content-integrity-evidence.sidecar/"
                    "lowercase-digest-final-newline/1.0"
                ),
                "strict_schema_resolution": True,
            },
            {
                "canonical_bytes_required": True,
                "evidence_type": "inventory_evidence",
                "parse_contract_id": "poe.storage.inventory-evidence.typed-parse/1.0",
                "schema_name": "poe.storage.inventory-evidence",
                "schema_version": "1.0",
                "sidecar_rule_id": (
                    "poe.storage.inventory-evidence.sidecar/"
                    "lowercase-digest-two-spaces-exact-filename-final-newline/1.0"
                ),
                "strict_schema_resolution": True,
            },
        ],
    }
    projection = _fact_projection_manifest()
    if (
        hashlib.sha256(_canonical_manifest_bytes(adapter)).hexdigest()
        != BASELINE_ANALYSIS_ADAPTER_REGISTRY_ID
    ):
        raise ValueError("adapter-registry manifest digest does not match architecture")
    if (
        hashlib.sha256(_canonical_manifest_bytes(projection)).hexdigest()
        != BASELINE_ANALYSIS_FACT_PROJECTION_ID
    ):
        raise ValueError("fact-projection manifest digest does not match architecture")


def _canonical_manifest_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )


def _fact_projection_manifest() -> dict[str, object]:
    # The complete field lists are architecture-owned; retaining them here makes a
    # semantic change fail the independently verified digest gate.
    content_fields = [
        "evidence[].detail",
        "evidence[].expected_sha256",
        "evidence[].expected_size_bytes",
        "evidence[].failure_code",
        "evidence[].item_id",
        "evidence[].observed_sha256",
        "evidence[].observed_size_bytes",
        "evidence[].outcome",
        "evidence[].relative_path",
        "evidence[].schema_version",
        "evidence[].source_observation_after.device_id",
        "evidence[].source_observation_after.inode",
        "evidence[].source_observation_after.mode",
        "evidence[].source_observation_after.modified_at_ns",
        "evidence[].source_observation_after.size_bytes",
        "evidence[].source_observation_before.device_id",
        "evidence[].source_observation_before.inode",
        "evidence[].source_observation_before.mode",
        "evidence[].source_observation_before.modified_at_ns",
        "evidence[].source_observation_before.size_bytes",
        "evidence[].verification_completed_at_utc",
        "evidence[].verification_started_at_utc",
        "schema_version",
        "source_root_id",
        "totals.candidate_file_count",
        "totals.digest_mismatch_count",
        "totals.filesystem_error_count",
        "totals.inaccessible_count",
        "totals.missing_count",
        "totals.not_regular_file_count",
        "totals.size_mismatch_count",
        "totals.source_changed_count",
        "totals.total_expected_bytes",
        "totals.total_observed_bytes",
        "totals.verified_count",
        "verification_completed_at_utc",
        "verification_started_at_utc",
    ]
    inventory_fields = [
        "header.discovery_request_id",
        "header.exception_summaries[].category",
        "header.exception_summaries[].count",
        "header.exception_summaries[].detail",
        "header.exception_summaries[].example_paths[]",
        "header.item_count",
        "header.record_kind",
        "header.schema_version",
        "header.source_root_id",
        "header.totals.captured_count",
        "header.totals.directory_count",
        "header.totals.error_count",
        "header.totals.excluded_count",
        "header.totals.file_count",
        "header.totals.inaccessible_count",
        "header.totals.junction_count",
        "header.totals.other_item_count",
        "header.totals.pending_count",
        "header.totals.symbolic_link_count",
        "header.totals.total_file_bytes",
        "records[].detail",
        "records[].item_id",
        "records[].item_type",
        "records[].record.capture_status",
        "records[].record.captured_at_utc",
        "records[].record.descendant_directory_count",
        "records[].record.descendant_file_count",
        "records[].record.descendant_size_bytes",
        "records[].record.direct_directory_count",
        "records[].record.direct_file_count",
        "records[].record.error_detail",
        "records[].record.exclusion_reason",
        "records[].record.identity.baseline_id",
        "records[].record.identity.capture_session_id",
        "records[].record.identity.item_type",
        "records[].record.identity.relative_path",
        "records[].record.identity.source_device_id",
        "records[].record.identity.source_root_id",
        "records[].record.identity.source_volume_id",
        "records[].record.metadata.accessed_at_utc",
        "records[].record.metadata.created_at_utc",
        "records[].record.metadata.modified_at_utc",
        "records[].record.metadata.owner",
        "records[].record.metadata.permissions",
        "records[].record.sha256",
        "records[].record.size_bytes",
        "records[].record_kind",
        "records[].relative_path",
        "records[].support_status",
    ]
    return {
        "duplicate_key_rules": [
            "duplicate canonical object key fails",
            "duplicate integrity item_id fails",
            "duplicate integrity relative_path fails",
            "duplicate inventory item_id fails",
            "duplicate inventory relative_path fails",
        ],
        "evidence_projections": [
            {
                "evidence_type": "content_integrity_evidence",
                "field_paths": content_fields,
                "schema_name": "poe.storage.content-integrity-evidence",
                "schema_version": "1.0",
            },
            {
                "evidence_type": "inventory_evidence",
                "field_paths": inventory_fields,
                "schema_name": "poe.storage.inventory-evidence",
                "schema_version": "1.0",
            },
        ],
        "immutable_representation_rules": {
            "arrays": "tuples preserving approved semantic order",
            "json_objects": "tuples of key-value pairs ordered by lexical key",
            "null": "None",
            "scalars": "exact JSON string, integer, boolean, or null value",
        },
        "lineage_validation_rules": [
            "authenticated evidence source_root_id equals its accepted observation "
            "and reference source_root_id",
            "content-integrity document source_root_id equals its authenticated "
            "evidence source_root_id",
            "content-integrity item_id and relative_path reconcile uniquely to "
            "inventory item_id and relative_path",
            "every supported inventory record identity.source_root_id equals the "
            "inventory header source_root_id",
            "inventory envelope item_id, item_type, and relative_path equal their "
            "nested record identity values",
            "inventory header source_root_id equals its authenticated evidence source_root_id",
            "selected evidence belongs to accepted roots and never to excluded roots",
        ],
        "manifest_schema_version": "poe.storage.baseline-analysis.fact-projection/1.0",
        "operationally_excluded_fields": [
            "artifact_descriptor_device_id",
            "artifact_descriptor_inode",
            "artifact_link_count",
            "artifact_path",
            "artifact_transport_sha256",
            "artifact_verified_byte_count",
            "authentication_host",
            "authentication_timestamp",
            "sidecar_descriptor_device_id",
            "sidecar_descriptor_inode",
            "sidecar_link_count",
            "sidecar_path",
            "sidecar_transport_sha256",
            "temporary_path",
        ],
        "ordering_rules": {
            "content_integrity_evidence": "(source_root_id, relative_path, item_id)",
            "inventory_evidence": "(source_root_id, relative_path, item_id)",
            "object_keys": "lexical Unicode code-point order",
            "projected_evidence": "(source_root_id, evidence_type, schema_name, schema_version)",
        },
        "path_representation": "exact canonical POSIX relative-path string; no normalization",
        "timestamp_representation": (
            "exact producer-canonical ISO 8601 UTC string with explicit offset; "
            "no timezone conversion"
        ),
    }
