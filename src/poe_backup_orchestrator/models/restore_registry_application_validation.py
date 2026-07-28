"""Domain contracts for policy-driven Registry application validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

RESTORE_REGISTRY_APPLICATION_VALIDATION_SCHEMA_VERSION = "1.0"


class RowCountInvariantOperator(StrEnum):
    """Supported deterministic row-count comparisons."""

    EQUAL = "equal"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"


@dataclass(frozen=True, slots=True)
class RegistryMetadataExpectation:
    """Required metadata key/value observation."""

    table: str
    key_column: str
    value_column: str
    key: str
    expected_value: str


@dataclass(frozen=True, slots=True)
class RegistryRowCountInvariant:
    """Declarative row-count relationship between two tables."""

    left_table: str
    operator: RowCountInvariantOperator
    right_table: str


@dataclass(frozen=True, slots=True)
class RegistryApplicationValidationPolicy:
    """Explicit Registry application contract."""

    policy_id: str
    policy_version: str
    required_columns: tuple[tuple[str, tuple[str, ...]], ...]
    metadata_expectations: tuple[RegistryMetadataExpectation, ...] = ()
    tables_allowed_empty: tuple[str, ...] = ()
    row_count_invariants: tuple[RegistryRowCountInvariant, ...] = ()

    def __post_init__(self) -> None:
        if not self.policy_id.strip():
            raise ValueError("policy_id must not be empty")
        if not self.policy_version.strip():
            raise ValueError("policy_version must not be empty")
        tables = [table for table, _ in self.required_columns]
        if not tables:
            raise ValueError("required_columns must define at least one table")
        if len(tables) != len(set(tables)):
            raise ValueError("required table names must be unique")
        for table, columns in self.required_columns:
            if not table.strip():
                raise ValueError("required table name must not be empty")
            if not columns:
                raise ValueError(f"required table {table} must define columns")
            if len(columns) != len(set(columns)):
                raise ValueError(f"required columns for table {table} must be unique")


class RestoreRegistryApplicationValidationStatus(StrEnum):
    """Outcome of Registry application validation."""

    VALID = "valid"


class RestoreRegistryApplicationValidationReasonCode(StrEnum):
    """Stable successful validation reason codes."""

    REQUIRED_TABLES_PRESENT = "required_tables_present"
    REQUIRED_COLUMNS_PRESENT = "required_columns_present"
    REQUIRED_METADATA_VALID = "required_metadata_valid"
    ROW_COUNTS_VALID = "row_counts_valid"
    REGISTRY_APPLICATION_VALID = "registry_application_valid"


@dataclass(frozen=True, slots=True)
class RestoreRegistryApplicationValidation:
    """Immutable successful Registry application validation evidence."""

    schema_version: str
    plan_id: str
    validated_at_utc: datetime
    status: RestoreRegistryApplicationValidationStatus
    reason_codes: tuple[RestoreRegistryApplicationValidationReasonCode, ...]
    policy_id: str
    policy_version: str
    staged_path: Path
    discovered_tables: tuple[str, ...]
    discovered_columns: tuple[tuple[str, tuple[str, ...]], ...]
    metadata_observations: tuple[tuple[str, str, str], ...]
    row_count_observations: tuple[tuple[str, int], ...]
    staged_artifact_modified: bool = False
    authoritative_target_modified: bool = False

    def __post_init__(self) -> None:
        if not self.schema_version.strip():
            raise ValueError("schema_version must not be empty")
        if not self.plan_id.strip():
            raise ValueError("plan_id must not be empty")
        if self.validated_at_utc.tzinfo is None or self.validated_at_utc.utcoffset() is None:
            raise ValueError("validated_at_utc must be timezone-aware")
        if self.validated_at_utc.utcoffset() != UTC.utcoffset(self.validated_at_utc):
            raise ValueError("validated_at_utc must use UTC")
        if not self.policy_id.strip() or not self.policy_version.strip():
            raise ValueError("policy identity must not be empty")
        if self.staged_artifact_modified:
            raise ValueError("application validation cannot modify staged bytes")
        if self.authoritative_target_modified:
            raise ValueError("application validation cannot modify the authoritative target")
