"""Service boundaries for preservation-baseline evidence validation."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final, Protocol

from poe_backup_orchestrator.models.storage_baseline_candidate import (
    PreservationEvidenceReference,
    PreservationEvidenceType,
)


class PreservationBaselineValidationError(Exception):
    """Raised when deterministic validation cannot safely be produced."""


_SHA256_PATTERN: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")
_DEFAULT_EVIDENCE_CHUNK_SIZE_BYTES: Final[int] = 1024 * 1024


class EvidenceLoadStatus(StrEnum):
    """Deterministic loading and authenticity outcome for one reference."""

    VERIFIED = "verified"
    EVIDENCE_MISSING = "evidence_missing"
    EVIDENCE_NOT_REGULAR_FILE = "evidence_not_regular_file"
    EVIDENCE_UNREADABLE = "evidence_unreadable"
    EVIDENCE_SIZE_MISMATCH = "evidence_size_mismatch"
    EVIDENCE_DIGEST_MISMATCH = "evidence_digest_mismatch"
    DIGEST_SIDECAR_MISSING = "digest_sidecar_missing"
    DIGEST_SIDECAR_NOT_REGULAR_FILE = "digest_sidecar_not_regular_file"
    DIGEST_SIDECAR_UNREADABLE = "digest_sidecar_unreadable"
    DIGEST_SIDECAR_MALFORMED = "digest_sidecar_malformed"
    DIGEST_SIDECAR_MISMATCH = "digest_sidecar_mismatch"


@dataclass(frozen=True, slots=True)
class LoadedPreservationEvidence:
    """Immutable evidence-loading facts without semantic interpretation."""

    reference: PreservationEvidenceReference
    status: EvidenceLoadStatus
    evidence_bytes: bytes | None
    calculated_sha256: str | None
    calculated_byte_count: int | None
    sidecar_sha256: str | None
    detail_code: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("calculated_sha256", "sidecar_sha256"):
            value = getattr(self, field_name)
            if value is not None and _SHA256_PATTERN.fullmatch(value) is None:
                raise ValueError(
                    f"{field_name} must contain exactly 64 lowercase hexadecimal characters"
                )
        if self.calculated_byte_count is not None and self.calculated_byte_count < 0:
            raise ValueError("calculated_byte_count must not be negative")
        detail_code = None if self.detail_code is None else self.detail_code.strip()
        if detail_code == "":
            detail_code = None
        if self.status is EvidenceLoadStatus.VERIFIED:
            if self.evidence_bytes is None:
                raise ValueError("verified evidence requires evidence_bytes")
            if self.calculated_sha256 is None:
                raise ValueError("verified evidence requires calculated_sha256")
            if self.calculated_byte_count is None:
                raise ValueError("verified evidence requires calculated_byte_count")
            if self.sidecar_sha256 is None:
                raise ValueError("verified evidence requires sidecar_sha256")
            if detail_code is not None:
                raise ValueError("verified evidence must not include detail_code")
        else:
            if self.evidence_bytes is not None:
                raise ValueError("unverified evidence must not expose evidence_bytes")
            if detail_code is None:
                raise ValueError("unverified evidence requires detail_code")
        object.__setattr__(self, "detail_code", detail_code)


class PreservationEvidenceLoader(Protocol):
    """Load and authenticate exactly one candidate evidence reference."""

    def load(
        self,
        reference: PreservationEvidenceReference,
    ) -> LoadedPreservationEvidence:
        """Return deterministic immutable loading facts."""


@dataclass(frozen=True, slots=True)
class FilesystemPreservationEvidenceLoader:
    """Read exact referenced files and verify byte count, digest, and sidecar."""

    chunk_size_bytes: int = _DEFAULT_EVIDENCE_CHUNK_SIZE_BYTES

    def __post_init__(self) -> None:
        if self.chunk_size_bytes <= 0:
            raise ValueError("chunk_size_bytes must be greater than zero")

    def load(
        self,
        reference: PreservationEvidenceReference,
    ) -> LoadedPreservationEvidence:
        evidence_path = reference.evidence_path
        evidence_state = _regular_file_state(evidence_path)
        if evidence_state == "missing":
            return _load_failure(
                reference, EvidenceLoadStatus.EVIDENCE_MISSING, "evidence_path_missing"
            )
        if evidence_state == "not_regular":
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_NOT_REGULAR_FILE,
                "evidence_path_not_regular_file",
            )
        if evidence_state == "unreadable":
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_UNREADABLE,
                "evidence_path_metadata_unreadable",
            )
        try:
            evidence_bytes, calculated_sha256, calculated_byte_count = _stream_evidence(
                evidence_path, self.chunk_size_bytes
            )
        except OSError:
            return _load_failure(
                reference, EvidenceLoadStatus.EVIDENCE_UNREADABLE, "evidence_bytes_unreadable"
            )
        if calculated_byte_count != reference.byte_count:
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_SIZE_MISMATCH,
                "reference_byte_count_mismatch",
                calculated_sha256,
                calculated_byte_count,
            )
        if calculated_sha256 != reference.sha256:
            return _load_failure(
                reference,
                EvidenceLoadStatus.EVIDENCE_DIGEST_MISMATCH,
                "reference_sha256_mismatch",
                calculated_sha256,
                calculated_byte_count,
            )
        digest_state = _regular_file_state(reference.digest_path)
        if digest_state == "missing":
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISSING,
                "digest_path_missing",
                calculated_sha256,
                calculated_byte_count,
            )
        if digest_state == "not_regular":
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_NOT_REGULAR_FILE,
                "digest_path_not_regular_file",
                calculated_sha256,
                calculated_byte_count,
            )
        if digest_state == "unreadable":
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_UNREADABLE,
                "digest_path_metadata_unreadable",
                calculated_sha256,
                calculated_byte_count,
            )
        try:
            sidecar_text = reference.digest_path.read_text(encoding="ascii")
        except (OSError, UnicodeError):
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_UNREADABLE,
                "digest_sidecar_unreadable",
                calculated_sha256,
                calculated_byte_count,
            )
        parsed = _parse_digest_sidecar(sidecar_text, evidence_path.name)
        if parsed is None:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MALFORMED,
                "digest_sidecar_malformed",
                calculated_sha256,
                calculated_byte_count,
            )
        sidecar_sha256, filename_matches = parsed
        if not filename_matches:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH,
                "digest_sidecar_filename_mismatch",
                calculated_sha256,
                calculated_byte_count,
                sidecar_sha256,
            )
        if sidecar_sha256 != reference.sha256:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH,
                "digest_sidecar_reference_mismatch",
                calculated_sha256,
                calculated_byte_count,
                sidecar_sha256,
            )
        if sidecar_sha256 != calculated_sha256:
            return _load_failure(
                reference,
                EvidenceLoadStatus.DIGEST_SIDECAR_MISMATCH,
                "digest_sidecar_calculated_mismatch",
                calculated_sha256,
                calculated_byte_count,
                sidecar_sha256,
            )
        return LoadedPreservationEvidence(
            reference=reference,
            status=EvidenceLoadStatus.VERIFIED,
            evidence_bytes=evidence_bytes,
            calculated_sha256=calculated_sha256,
            calculated_byte_count=calculated_byte_count,
            sidecar_sha256=sidecar_sha256,
        )


def _regular_file_state(path: Path) -> str:
    try:
        file_status = path.stat()
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unreadable"
    return "regular" if stat.S_ISREG(file_status.st_mode) else "not_regular"


def _stream_evidence(path: Path, chunk_size_bytes: int) -> tuple[bytes, str, int]:
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    byte_count = 0
    with path.open("rb") as stream:
        while chunk := stream.read(chunk_size_bytes):
            chunks.append(chunk)
            byte_count += len(chunk)
            digest.update(chunk)
    return b"".join(chunks), digest.hexdigest(), byte_count


def _parse_digest_sidecar(sidecar_text: str, expected_filename: str) -> tuple[str, bool] | None:
    line = sidecar_text.strip()
    if _SHA256_PATTERN.fullmatch(line):
        return line, True
    match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
    if match is None:
        return None
    return match.group(1), match.group(2) == expected_filename


def _load_failure(
    reference: PreservationEvidenceReference,
    status: EvidenceLoadStatus,
    detail_code: str,
    calculated_sha256: str | None = None,
    calculated_byte_count: int | None = None,
    sidecar_sha256: str | None = None,
) -> LoadedPreservationEvidence:
    return LoadedPreservationEvidence(
        reference=reference,
        status=status,
        evidence_bytes=None,
        calculated_sha256=calculated_sha256,
        calculated_byte_count=calculated_byte_count,
        sidecar_sha256=sidecar_sha256,
        detail_code=detail_code,
    )


class PreservationEvidenceAdapter(Protocol):
    """Typed adapter for one evidence category and schema family."""

    evidence_type: PreservationEvidenceType
    schema_name: str
    supported_versions: tuple[str, ...]

    def parse(self, evidence_bytes: bytes) -> object:
        """Parse authenticated evidence bytes."""

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        """Extract only facts required for technical validation."""


INVENTORY_EVIDENCE_SCHEMA_NAME: Final[str] = "poe.storage.inventory-evidence"
CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME: Final[str] = "poe.storage.content-integrity-evidence"

FrozenJsonScalar = str | int | float | bool | None
FrozenJsonValue = (
    FrozenJsonScalar | tuple["FrozenJsonValue", ...] | tuple[tuple[str, "FrozenJsonValue"], ...]
)


class EvidenceDeserializationStatus(StrEnum):
    DESERIALIZED = "deserialized"
    AUTHENTICATION_REQUIRED = "authentication_required"
    INVALID_UTF8 = "invalid_utf8"
    MALFORMED_SERIALIZATION = "malformed_serialization"
    INVALID_DOCUMENT_SHAPE = "invalid_document_shape"
    SCHEMA_IDENTITY_MISSING = "schema_identity_missing"
    SCHEMA_IDENTITY_MISMATCH = "schema_identity_mismatch"
    ADAPTER_NOT_FOUND = "adapter_not_found"
    ADAPTER_PARSE_FAILED = "adapter_parse_failed"


@dataclass(frozen=True, slots=True)
class DeserializedPreservationEvidence:
    loaded_evidence: LoadedPreservationEvidence
    status: EvidenceDeserializationStatus
    schema_name: str | None
    schema_version: str | None
    parsed_evidence: object | None
    adapter: PreservationEvidenceAdapter | None
    detail_code: str | None = None

    def __post_init__(self) -> None:
        schema_name = None if self.schema_name is None else self.schema_name.strip()
        schema_version = None if self.schema_version is None else self.schema_version.strip()
        detail_code = None if self.detail_code is None else self.detail_code.strip()

        if schema_name == "":
            schema_name = None
        if schema_version == "":
            schema_version = None
        if detail_code == "":
            detail_code = None

        if self.status is EvidenceDeserializationStatus.DESERIALIZED:
            if self.loaded_evidence.status is not EvidenceLoadStatus.VERIFIED:
                raise ValueError("deserialized evidence requires authenticated input")
            if schema_name is None or schema_version is None:
                raise ValueError("deserialized evidence requires schema identity")
            if self.parsed_evidence is None:
                raise ValueError("deserialized evidence requires parsed_evidence")
            if self.adapter is None:
                raise ValueError("deserialized evidence requires resolved adapter")
            if detail_code is not None:
                raise ValueError("deserialized evidence must not include detail_code")
        else:
            if self.parsed_evidence is not None:
                raise ValueError("failed deserialization must not expose parsed evidence")
            if self.adapter is not None:
                raise ValueError("failed deserialization must not expose an adapter")
            if detail_code is None:
                raise ValueError("failed deserialization requires detail_code")

        object.__setattr__(self, "schema_name", schema_name)
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "detail_code", detail_code)


class EvidenceFactExtractionStatus(StrEnum):
    EXTRACTED = "extracted"
    DESERIALIZATION_REQUIRED = "deserialization_required"
    EXTRACTION_FAILED = "extraction_failed"


@dataclass(frozen=True, slots=True)
class InventoryValidationFacts:
    schema_version: str
    source_root_id: str
    declared_item_count: int
    records: tuple[FrozenJsonValue, ...]
    totals: FrozenJsonValue

    def __post_init__(self) -> None:
        schema_version = self.schema_version.strip()
        source_root_id = self.source_root_id.strip()
        records = tuple(self.records)
        if not schema_version:
            raise ValueError("inventory fact schema_version must not be empty")
        if not source_root_id:
            raise ValueError("inventory fact source_root_id must not be empty")
        if self.declared_item_count < 0:
            raise ValueError("declared_item_count must not be negative")
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "records", records)


@dataclass(frozen=True, slots=True)
class ContentIntegrityValidationFacts:
    schema_version: str
    source_root_id: str
    evidence: tuple[FrozenJsonValue, ...]
    totals: FrozenJsonValue

    def __post_init__(self) -> None:
        schema_version = self.schema_version.strip()
        source_root_id = self.source_root_id.strip()
        if not schema_version:
            raise ValueError("integrity fact schema_version must not be empty")
        if not source_root_id:
            raise ValueError("integrity fact source_root_id must not be empty")
        object.__setattr__(self, "schema_version", schema_version)
        object.__setattr__(self, "source_root_id", source_root_id)
        object.__setattr__(self, "evidence", tuple(self.evidence))


@dataclass(frozen=True, slots=True)
class ExtractedPreservationEvidenceFacts:
    deserialized_evidence: DeserializedPreservationEvidence
    status: EvidenceFactExtractionStatus
    facts: InventoryValidationFacts | ContentIntegrityValidationFacts | None
    detail_code: str | None = None

    def __post_init__(self) -> None:
        detail_code = None if self.detail_code is None else self.detail_code.strip()
        if detail_code == "":
            detail_code = None
        if self.status is EvidenceFactExtractionStatus.EXTRACTED:
            if self.deserialized_evidence.status is not EvidenceDeserializationStatus.DESERIALIZED:
                raise ValueError("extracted facts require deserialized evidence")
            if self.facts is None:
                raise ValueError("successful extraction requires facts")
            if detail_code is not None:
                raise ValueError("successful extraction must not include detail_code")
        else:
            if self.facts is not None:
                raise ValueError("failed extraction must not expose facts")
            if detail_code is None:
                raise ValueError("failed extraction requires detail_code")
        object.__setattr__(self, "detail_code", detail_code)


@dataclass(frozen=True, slots=True)
class PreservationEvidenceFactExtractionService:
    def extract(
        self,
        deserialized_evidence: DeserializedPreservationEvidence,
    ) -> ExtractedPreservationEvidenceFacts:
        if (
            deserialized_evidence.status is not EvidenceDeserializationStatus.DESERIALIZED
            or deserialized_evidence.parsed_evidence is None
            or deserialized_evidence.adapter is None
        ):
            return ExtractedPreservationEvidenceFacts(
                deserialized_evidence=deserialized_evidence,
                status=EvidenceFactExtractionStatus.DESERIALIZATION_REQUIRED,
                facts=None,
                detail_code="evidence_not_deserialized",
            )
        try:
            facts = deserialized_evidence.adapter.extract_validation_facts(
                deserialized_evidence.parsed_evidence
            )
        except (KeyError, TypeError, ValueError):
            return ExtractedPreservationEvidenceFacts(
                deserialized_evidence=deserialized_evidence,
                status=EvidenceFactExtractionStatus.EXTRACTION_FAILED,
                facts=None,
                detail_code="adapter_fact_extraction_failed",
            )
        if not isinstance(facts, (InventoryValidationFacts, ContentIntegrityValidationFacts)):
            return ExtractedPreservationEvidenceFacts(
                deserialized_evidence=deserialized_evidence,
                status=EvidenceFactExtractionStatus.EXTRACTION_FAILED,
                facts=None,
                detail_code="adapter_returned_unsupported_fact_type",
            )
        return ExtractedPreservationEvidenceFacts(
            deserialized_evidence=deserialized_evidence,
            status=EvidenceFactExtractionStatus.EXTRACTED,
            facts=facts,
        )


class EvidenceReconciliationStatus(StrEnum):
    RECONCILED = "reconciled"
    SOURCE_ROOT_MISMATCH = "source_root_mismatch"
    RECONCILIATION_FAILED = "reconciliation_failed"


@dataclass(frozen=True, slots=True, order=True)
class ReconciledEvidenceItem:
    relative_path: str
    inventory_item_id: str | None
    integrity_item_id: str | None

    def __post_init__(self) -> None:
        relative_path = self.relative_path.strip()
        if not relative_path:
            raise ValueError("relative_path must not be empty")
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(
            self,
            "inventory_item_id",
            _normalize_optional_text(self.inventory_item_id),
        )
        object.__setattr__(
            self,
            "integrity_item_id",
            _normalize_optional_text(self.integrity_item_id),
        )


@dataclass(frozen=True, slots=True, order=True)
class UnmatchedEvidenceItem:
    relative_path: str
    item_id: str | None

    def __post_init__(self) -> None:
        relative_path = self.relative_path.strip()
        if not relative_path:
            raise ValueError("relative_path must not be empty")
        object.__setattr__(self, "relative_path", relative_path)
        object.__setattr__(self, "item_id", _normalize_optional_text(self.item_id))


@dataclass(frozen=True, slots=True)
class EvidenceCountReconciliation:
    inventory_declared_item_count: int
    inventory_observed_record_count: int
    integrity_observed_record_count: int
    matched_record_count: int
    inventory_only_record_count: int
    integrity_only_record_count: int
    duplicate_inventory_path_count: int
    duplicate_integrity_path_count: int

    def __post_init__(self) -> None:
        values = (
            self.inventory_declared_item_count,
            self.inventory_observed_record_count,
            self.integrity_observed_record_count,
            self.matched_record_count,
            self.inventory_only_record_count,
            self.integrity_only_record_count,
            self.duplicate_inventory_path_count,
            self.duplicate_integrity_path_count,
        )
        if any(value < 0 for value in values):
            raise ValueError("reconciliation counts must not be negative")


@dataclass(frozen=True, slots=True)
class PreservationEvidenceReconciliation:
    inventory_facts: InventoryValidationFacts
    integrity_facts: ContentIntegrityValidationFacts
    status: EvidenceReconciliationStatus
    matched: tuple[ReconciledEvidenceItem, ...]
    inventory_only: tuple[UnmatchedEvidenceItem, ...]
    integrity_only: tuple[UnmatchedEvidenceItem, ...]
    duplicate_inventory_paths: tuple[str, ...]
    duplicate_integrity_paths: tuple[str, ...]
    counts: EvidenceCountReconciliation | None
    detail_code: str | None = None

    def __post_init__(self) -> None:
        detail_code = _normalize_optional_text(self.detail_code)
        matched = tuple(self.matched)
        inventory_only = tuple(self.inventory_only)
        integrity_only = tuple(self.integrity_only)
        duplicate_inventory_paths = tuple(self.duplicate_inventory_paths)
        duplicate_integrity_paths = tuple(self.duplicate_integrity_paths)

        if matched != tuple(sorted(matched)):
            raise ValueError("matched reconciliation items must be canonically ordered")
        if inventory_only != tuple(sorted(inventory_only)):
            raise ValueError("inventory-only items must be canonically ordered")
        if integrity_only != tuple(sorted(integrity_only)):
            raise ValueError("integrity-only items must be canonically ordered")
        if duplicate_inventory_paths != tuple(sorted(set(duplicate_inventory_paths))):
            raise ValueError("duplicate inventory paths must be unique and ordered")
        if duplicate_integrity_paths != tuple(sorted(set(duplicate_integrity_paths))):
            raise ValueError("duplicate integrity paths must be unique and ordered")

        if self.status is EvidenceReconciliationStatus.RECONCILED:
            if self.counts is None:
                raise ValueError("successful reconciliation requires counts")
            if detail_code is not None:
                raise ValueError("successful reconciliation must not include detail_code")
        else:
            if self.counts is not None:
                raise ValueError("failed reconciliation must not expose counts")
            if matched or inventory_only or integrity_only:
                raise ValueError("failed reconciliation must not expose relationships")
            if duplicate_inventory_paths or duplicate_integrity_paths:
                raise ValueError("failed reconciliation must not expose duplicate paths")
            if detail_code is None:
                raise ValueError("failed reconciliation requires detail_code")

        object.__setattr__(self, "matched", matched)
        object.__setattr__(self, "inventory_only", inventory_only)
        object.__setattr__(self, "integrity_only", integrity_only)
        object.__setattr__(self, "duplicate_inventory_paths", duplicate_inventory_paths)
        object.__setattr__(self, "duplicate_integrity_paths", duplicate_integrity_paths)
        object.__setattr__(self, "detail_code", detail_code)


@dataclass(frozen=True, slots=True)
class PreservationEvidenceReconciliationService:
    def reconcile(
        self,
        *,
        inventory_facts: InventoryValidationFacts,
        integrity_facts: ContentIntegrityValidationFacts,
    ) -> PreservationEvidenceReconciliation:
        if inventory_facts.source_root_id != integrity_facts.source_root_id:
            return _reconciliation_failure(
                inventory_facts=inventory_facts,
                integrity_facts=integrity_facts,
                status=EvidenceReconciliationStatus.SOURCE_ROOT_MISMATCH,
                detail_code="source_root_ids_do_not_match",
            )

        try:
            inventory_records = tuple(
                _reconciliation_record(record, "inventory record")
                for record in inventory_facts.records
            )
            integrity_records = tuple(
                _reconciliation_record(record, "integrity record")
                for record in integrity_facts.evidence
            )
        except (KeyError, TypeError, ValueError):
            return _reconciliation_failure(
                inventory_facts=inventory_facts,
                integrity_facts=integrity_facts,
                status=EvidenceReconciliationStatus.RECONCILIATION_FAILED,
                detail_code="reconciliation_record_shape_invalid",
            )

        inventory_by_path = _group_reconciliation_records(inventory_records)
        integrity_by_path = _group_reconciliation_records(integrity_records)

        duplicate_inventory_paths = tuple(
            sorted(path for path, records in inventory_by_path.items() if len(records) > 1)
        )
        duplicate_integrity_paths = tuple(
            sorted(path for path, records in integrity_by_path.items() if len(records) > 1)
        )

        unique_inventory = {
            path: records[0] for path, records in inventory_by_path.items() if len(records) == 1
        }
        unique_integrity = {
            path: records[0] for path, records in integrity_by_path.items() if len(records) == 1
        }

        matched_paths = sorted(set(unique_inventory) & set(unique_integrity))
        inventory_only_paths = sorted(set(unique_inventory) - set(unique_integrity))
        integrity_only_paths = sorted(set(unique_integrity) - set(unique_inventory))

        matched = tuple(
            ReconciledEvidenceItem(
                relative_path=path,
                inventory_item_id=unique_inventory[path][1],
                integrity_item_id=unique_integrity[path][1],
            )
            for path in matched_paths
        )
        inventory_only = tuple(
            UnmatchedEvidenceItem(
                relative_path=path,
                item_id=unique_inventory[path][1],
            )
            for path in inventory_only_paths
        )
        integrity_only = tuple(
            UnmatchedEvidenceItem(
                relative_path=path,
                item_id=unique_integrity[path][1],
            )
            for path in integrity_only_paths
        )

        counts = EvidenceCountReconciliation(
            inventory_declared_item_count=inventory_facts.declared_item_count,
            inventory_observed_record_count=len(inventory_records),
            integrity_observed_record_count=len(integrity_records),
            matched_record_count=len(matched),
            inventory_only_record_count=len(inventory_only),
            integrity_only_record_count=len(integrity_only),
            duplicate_inventory_path_count=len(duplicate_inventory_paths),
            duplicate_integrity_path_count=len(duplicate_integrity_paths),
        )

        return PreservationEvidenceReconciliation(
            inventory_facts=inventory_facts,
            integrity_facts=integrity_facts,
            status=EvidenceReconciliationStatus.RECONCILED,
            matched=matched,
            inventory_only=inventory_only,
            integrity_only=integrity_only,
            duplicate_inventory_paths=duplicate_inventory_paths,
            duplicate_integrity_paths=duplicate_integrity_paths,
            counts=counts,
        )


@dataclass(frozen=True, slots=True)
class InventoryEvidenceAdapter:
    evidence_type: Final[PreservationEvidenceType] = PreservationEvidenceType.INVENTORY_EVIDENCE
    schema_name: Final[str] = INVENTORY_EVIDENCE_SCHEMA_NAME
    supported_versions: Final[tuple[str, ...]] = ("1.0",)

    def parse(self, evidence_bytes: bytes) -> object:
        records, _, _ = _decode_inventory_evidence(evidence_bytes)
        return tuple(_freeze_json(record) for record in records)

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        records = _require_frozen_sequence(parsed_evidence, "inventory evidence")
        header = _require_frozen_object(records[0], "inventory header")
        return InventoryValidationFacts(
            schema_version=_required_frozen_string(header, "schema_version", "inventory header"),
            source_root_id=_required_frozen_string(header, "source_root_id", "inventory header"),
            declared_item_count=_required_frozen_int(header, "item_count", "inventory header"),
            records=records[1:],
            totals=_required_frozen_value(header, "totals", "inventory header"),
        )


@dataclass(frozen=True, slots=True)
class ContentIntegrityEvidenceAdapter:
    evidence_type: Final[PreservationEvidenceType] = (
        PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE
    )
    schema_name: Final[str] = CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME
    supported_versions: Final[tuple[str, ...]] = ("1.0",)

    def parse(self, evidence_bytes: bytes) -> object:
        document, _, _ = _decode_content_integrity_evidence(evidence_bytes)
        return _freeze_json(document)

    def extract_validation_facts(self, parsed_evidence: object) -> object:
        document = _require_frozen_object(parsed_evidence, "content-integrity evidence")
        evidence = _require_frozen_sequence(
            _required_frozen_value(document, "evidence", "content-integrity evidence"),
            "content-integrity evidence items",
        )
        return ContentIntegrityValidationFacts(
            schema_version=_required_frozen_string(
                document, "schema_version", "content-integrity evidence"
            ),
            source_root_id=_required_frozen_string(
                document, "source_root_id", "content-integrity evidence"
            ),
            evidence=evidence,
            totals=_required_frozen_value(document, "totals", "content-integrity evidence"),
        )


@dataclass(frozen=True, slots=True)
class PreservationEvidenceDeserializationService:
    registry: ValidationAdapterRegistry

    def deserialize(
        self,
        loaded_evidence: LoadedPreservationEvidence,
    ) -> DeserializedPreservationEvidence:
        if (
            loaded_evidence.status is not EvidenceLoadStatus.VERIFIED
            or loaded_evidence.evidence_bytes is None
        ):
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=EvidenceDeserializationStatus.AUTHENTICATION_REQUIRED,
                detail_code="evidence_not_authenticated",
            )

        try:
            schema_name, schema_version = _probe_schema_identity(
                evidence_type=loaded_evidence.reference.evidence_type,
                evidence_bytes=loaded_evidence.evidence_bytes,
            )
        except UnicodeDecodeError:
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=EvidenceDeserializationStatus.INVALID_UTF8,
                detail_code="evidence_not_utf8",
            )
        except json.JSONDecodeError:
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=EvidenceDeserializationStatus.MALFORMED_SERIALIZATION,
                detail_code="evidence_serialization_malformed",
            )
        except _InvalidEvidenceShapeError as error:
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=error.status,
                detail_code=error.detail_code,
                schema_name=error.schema_name,
                schema_version=error.schema_version,
            )

        if schema_version != loaded_evidence.reference.schema_version:
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=EvidenceDeserializationStatus.SCHEMA_IDENTITY_MISMATCH,
                detail_code="payload_reference_schema_version_mismatch",
                schema_name=schema_name,
                schema_version=schema_version,
            )

        try:
            adapter = self.registry.resolve(
                evidence_type=loaded_evidence.reference.evidence_type,
                schema_name=schema_name,
                schema_version=schema_version,
            )
        except PreservationBaselineValidationError:
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=EvidenceDeserializationStatus.ADAPTER_NOT_FOUND,
                detail_code="schema_adapter_not_found",
                schema_name=schema_name,
                schema_version=schema_version,
            )

        try:
            parsed_evidence = adapter.parse(loaded_evidence.evidence_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError):
            return _deserialization_failure(
                loaded_evidence=loaded_evidence,
                status=EvidenceDeserializationStatus.ADAPTER_PARSE_FAILED,
                detail_code="resolved_adapter_parse_failed",
                schema_name=schema_name,
                schema_version=schema_version,
            )

        return DeserializedPreservationEvidence(
            loaded_evidence=loaded_evidence,
            status=EvidenceDeserializationStatus.DESERIALIZED,
            schema_name=schema_name,
            schema_version=schema_version,
            parsed_evidence=parsed_evidence,
            adapter=adapter,
        )


@dataclass(frozen=True, slots=True)
class _InvalidEvidenceShapeError(Exception):
    status: EvidenceDeserializationStatus
    detail_code: str
    schema_name: str | None = None
    schema_version: str | None = None


def _probe_schema_identity(
    *,
    evidence_type: PreservationEvidenceType,
    evidence_bytes: bytes,
) -> tuple[str, str]:
    if evidence_type is PreservationEvidenceType.INVENTORY_EVIDENCE:
        _, schema_name, schema_version = _decode_inventory_evidence(evidence_bytes)
        return schema_name, schema_version
    if evidence_type is PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE:
        _, schema_name, schema_version = _decode_content_integrity_evidence(evidence_bytes)
        return schema_name, schema_version
    raise _InvalidEvidenceShapeError(
        status=EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE,
        detail_code="unsupported_evidence_type",
    )


def _decode_inventory_evidence(
    evidence_bytes: bytes,
) -> tuple[list[dict[str, object]], str, str]:
    decoded_text = evidence_bytes.decode("utf-8", errors="strict")
    lines = decoded_text.splitlines()
    if not lines:
        raise _InvalidEvidenceShapeError(
            status=EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE,
            detail_code="inventory_document_empty",
            schema_name=INVENTORY_EVIDENCE_SCHEMA_NAME,
        )

    records: list[dict[str, object]] = []
    for line in lines:
        decoded = json.loads(line)
        if not isinstance(decoded, dict):
            raise _InvalidEvidenceShapeError(
                status=EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE,
                detail_code="inventory_record_not_object",
                schema_name=INVENTORY_EVIDENCE_SCHEMA_NAME,
            )
        records.append(decoded)

    header = records[0]
    if header.get("record_kind") != "inventory_header":
        raise _InvalidEvidenceShapeError(
            status=EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE,
            detail_code="inventory_header_missing",
            schema_name=INVENTORY_EVIDENCE_SCHEMA_NAME,
        )

    schema_version = header.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise _InvalidEvidenceShapeError(
            status=EvidenceDeserializationStatus.SCHEMA_IDENTITY_MISSING,
            detail_code="inventory_schema_version_missing",
            schema_name=INVENTORY_EVIDENCE_SCHEMA_NAME,
        )

    return records, INVENTORY_EVIDENCE_SCHEMA_NAME, schema_version.strip()


def _decode_content_integrity_evidence(
    evidence_bytes: bytes,
) -> tuple[dict[str, object], str, str]:
    decoded_text = evidence_bytes.decode("utf-8", errors="strict")
    decoded = json.loads(decoded_text)
    if not isinstance(decoded, dict):
        raise _InvalidEvidenceShapeError(
            status=EvidenceDeserializationStatus.INVALID_DOCUMENT_SHAPE,
            detail_code="content_integrity_document_not_object",
            schema_name=CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
        )

    schema_version = decoded.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version.strip():
        raise _InvalidEvidenceShapeError(
            status=EvidenceDeserializationStatus.SCHEMA_IDENTITY_MISSING,
            detail_code="content_integrity_schema_version_missing",
            schema_name=CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME,
        )

    return decoded, CONTENT_INTEGRITY_EVIDENCE_SCHEMA_NAME, schema_version.strip()


def _freeze_json(value: object) -> FrozenJsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    if isinstance(value, dict):
        return tuple(
            (str(key), _freeze_json(item))
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        )
    raise TypeError(f"unsupported JSON value type: {type(value).__name__}")


def _require_frozen_object(
    value: object,
    description: str,
) -> dict[str, FrozenJsonValue]:
    if not isinstance(value, tuple):
        raise TypeError(f"{description} must be a frozen object")
    result: dict[str, FrozenJsonValue] = {}
    for pair in value:
        if not isinstance(pair, tuple) or len(pair) != 2 or not isinstance(pair[0], str):
            raise TypeError(f"{description} must be a frozen object")
        key, item = pair
        if key in result:
            raise ValueError(f"{description} contains duplicate key: {key}")
        result[key] = item
    return result


def _require_frozen_sequence(
    value: object,
    description: str,
) -> tuple[FrozenJsonValue, ...]:
    if not isinstance(value, tuple):
        raise TypeError(f"{description} must be a frozen sequence")
    return value


def _required_frozen_value(
    document: dict[str, FrozenJsonValue],
    key: str,
    description: str,
) -> FrozenJsonValue:
    if key not in document:
        raise KeyError(f"{description} is missing required field: {key}")
    return document[key]


def _required_frozen_string(
    document: dict[str, FrozenJsonValue],
    key: str,
    description: str,
) -> str:
    value = _required_frozen_value(document, key, description)
    if not isinstance(value, str) or not value.strip():
        raise TypeError(f"{description}.{key} must be a non-empty string")
    return value.strip()


def _required_frozen_int(
    document: dict[str, FrozenJsonValue],
    key: str,
    description: str,
) -> int:
    value = _required_frozen_value(document, key, description)
    if type(value) is not int:
        raise TypeError(f"{description}.{key} must be an integer")
    return value


def _normalize_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _reconciliation_record(
    value: FrozenJsonValue,
    description: str,
) -> tuple[str, str | None]:
    document = _require_frozen_object(value, description)
    relative_path = _required_frozen_string(document, "relative_path", description)
    item_id_value = document.get("item_id")
    if item_id_value is not None and not isinstance(item_id_value, str):
        raise TypeError(f"{description}.item_id must be a string when present")
    return relative_path, _normalize_optional_text(item_id_value)


def _group_reconciliation_records(
    records: tuple[tuple[str, str | None], ...],
) -> dict[str, tuple[tuple[str, str | None], ...]]:
    grouped: dict[str, list[tuple[str, str | None]]] = {}
    for record in records:
        grouped.setdefault(record[0], []).append(record)
    return {
        path: tuple(sorted(path_records, key=lambda record: record[1] or ""))
        for path, path_records in sorted(grouped.items())
    }


def _reconciliation_failure(
    *,
    inventory_facts: InventoryValidationFacts,
    integrity_facts: ContentIntegrityValidationFacts,
    status: EvidenceReconciliationStatus,
    detail_code: str,
) -> PreservationEvidenceReconciliation:
    return PreservationEvidenceReconciliation(
        inventory_facts=inventory_facts,
        integrity_facts=integrity_facts,
        status=status,
        matched=(),
        inventory_only=(),
        integrity_only=(),
        duplicate_inventory_paths=(),
        duplicate_integrity_paths=(),
        counts=None,
        detail_code=detail_code,
    )


def _deserialization_failure(
    *,
    loaded_evidence: LoadedPreservationEvidence,
    status: EvidenceDeserializationStatus,
    detail_code: str,
    schema_name: str | None = None,
    schema_version: str | None = None,
) -> DeserializedPreservationEvidence:
    return DeserializedPreservationEvidence(
        loaded_evidence=loaded_evidence,
        status=status,
        schema_name=schema_name,
        schema_version=schema_version,
        parsed_evidence=None,
        adapter=None,
        detail_code=detail_code,
    )


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
