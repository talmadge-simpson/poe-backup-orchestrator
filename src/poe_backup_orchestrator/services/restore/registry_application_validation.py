"""Policy-driven read-only validation of a staged POE Registry database."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import quote

from poe_backup_orchestrator.models.restore_plan import RestorePlan
from poe_backup_orchestrator.models.restore_registry_application_validation import (
    RESTORE_REGISTRY_APPLICATION_VALIDATION_SCHEMA_VERSION,
    RegistryApplicationValidationPolicy,
    RegistryMetadataExpectation,
    RegistryRowCountInvariant,
    RestoreRegistryApplicationValidation,
    RestoreRegistryApplicationValidationReasonCode,
    RestoreRegistryApplicationValidationStatus,
    RowCountInvariantOperator,
)
from poe_backup_orchestrator.models.restore_staged_artifact_validation import (
    RestoreStagedArtifactValidation,
    RestoreStagedArtifactValidationStatus,
)


class RestoreRegistryApplicationValidationError(RuntimeError):
    """Raised when the staged Registry violates its application contract."""


@dataclass(frozen=True, slots=True)
class RestoreRegistryApplicationValidationService:
    """Validate an isolated Registry database without mutation."""

    policy: RegistryApplicationValidationPolicy

    def validate(
        self,
        plan: RestorePlan,
        staged_validation: RestoreStagedArtifactValidation,
        *,
        validated_at_utc: datetime,
    ) -> RestoreRegistryApplicationValidation:
        _validate_inputs(plan, staged_validation, validated_at_utc)

        staged_path = plan.staging_target_path
        uri = f"file:{quote(str(staged_path.resolve()))}?mode=ro&immutable=1"

        try:
            connection = sqlite3.connect(uri, uri=True)
        except sqlite3.Error as exc:
            raise RestoreRegistryApplicationValidationError(
                f"staged Registry could not be opened read-only: {exc}"
            ) from exc

        try:
            tables = _discover_tables(connection)
            required = dict(self.policy.required_columns)
            missing_tables = sorted(set(required) - set(tables))
            if missing_tables:
                raise RestoreRegistryApplicationValidationError(
                    "required Registry tables are missing: " + ", ".join(missing_tables)
                )

            discovered_columns = tuple(
                (table, _discover_columns(connection, table)) for table in sorted(required)
            )
            for table, required_table_columns in self.policy.required_columns:
                actual_columns = dict(discovered_columns)[table]
                missing_columns = sorted(set(required_table_columns) - set(actual_columns))
                if missing_columns:
                    raise RestoreRegistryApplicationValidationError(
                        f"required columns missing from {table}: " + ", ".join(missing_columns)
                    )

            metadata_observations = tuple(
                _validate_metadata(connection, expectation)
                for expectation in self.policy.metadata_expectations
            )

            row_counts = tuple((table, _row_count(connection, table)) for table in sorted(required))
            row_count_map = dict(row_counts)

            allowed_empty = set(self.policy.tables_allowed_empty)
            empty_disallowed = sorted(
                table for table, count in row_counts if count == 0 and table not in allowed_empty
            )
            if empty_disallowed:
                raise RestoreRegistryApplicationValidationError(
                    "required Registry tables are unexpectedly empty: "
                    + ", ".join(empty_disallowed)
                )

            for invariant in self.policy.row_count_invariants:
                _validate_row_count_invariant(row_count_map, invariant)
        except sqlite3.Error as exc:
            raise RestoreRegistryApplicationValidationError(
                f"Registry application validation query failed: {exc}"
            ) from exc
        finally:
            connection.close()

        return RestoreRegistryApplicationValidation(
            schema_version=RESTORE_REGISTRY_APPLICATION_VALIDATION_SCHEMA_VERSION,
            plan_id=plan.plan_id,
            validated_at_utc=validated_at_utc,
            status=RestoreRegistryApplicationValidationStatus.VALID,
            reason_codes=(
                RestoreRegistryApplicationValidationReasonCode.REQUIRED_TABLES_PRESENT,
                RestoreRegistryApplicationValidationReasonCode.REQUIRED_COLUMNS_PRESENT,
                RestoreRegistryApplicationValidationReasonCode.REQUIRED_METADATA_VALID,
                RestoreRegistryApplicationValidationReasonCode.ROW_COUNTS_VALID,
                RestoreRegistryApplicationValidationReasonCode.REGISTRY_APPLICATION_VALID,
            ),
            policy_id=self.policy.policy_id,
            policy_version=self.policy.policy_version,
            staged_path=staged_path,
            discovered_tables=tables,
            discovered_columns=discovered_columns,
            metadata_observations=metadata_observations,
            row_count_observations=row_counts,
            staged_artifact_modified=False,
            authoritative_target_modified=False,
        )


def validate_staged_registry_application(
    plan: RestorePlan,
    staged_validation: RestoreStagedArtifactValidation,
    policy: RegistryApplicationValidationPolicy,
    *,
    validated_at_utc: datetime,
) -> RestoreRegistryApplicationValidation:
    """Validate one staged Registry against an explicit application policy."""

    return RestoreRegistryApplicationValidationService(policy=policy).validate(
        plan,
        staged_validation,
        validated_at_utc=validated_at_utc,
    )


def _validate_inputs(
    plan: RestorePlan,
    staged_validation: RestoreStagedArtifactValidation,
    validated_at_utc: datetime,
) -> None:
    if validated_at_utc.tzinfo is None or validated_at_utc.utcoffset() is None:
        raise RestoreRegistryApplicationValidationError("validated_at_utc must be timezone-aware")
    if validated_at_utc.utcoffset() != UTC.utcoffset(validated_at_utc):
        raise RestoreRegistryApplicationValidationError("validated_at_utc must use UTC")
    if staged_validation.plan_id != plan.plan_id:
        raise RestoreRegistryApplicationValidationError(
            "staged validation plan_id does not match restore plan"
        )
    if staged_validation.status is not RestoreStagedArtifactValidationStatus.VALID:
        raise RestoreRegistryApplicationValidationError(
            "staged artifact validation must be successful"
        )
    if staged_validation.staged_path != plan.staging_target_path:
        raise RestoreRegistryApplicationValidationError(
            "validated staged path does not match restore plan"
        )
    if staged_validation.authoritative_target_modified:
        raise RestoreRegistryApplicationValidationError(
            "staged validation reports authoritative target modification"
        )


def _discover_tables(connection: sqlite3.Connection) -> tuple[str, ...]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_schema
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return tuple(str(row[0]) for row in rows)


def _discover_columns(
    connection: sqlite3.Connection,
    table: str,
) -> tuple[str, ...]:
    quoted = _quote_identifier(table)
    rows = connection.execute(f"PRAGMA table_info({quoted})")
    return tuple(str(row[1]) for row in rows)


def _validate_metadata(
    connection: sqlite3.Connection,
    expectation: RegistryMetadataExpectation,
) -> tuple[str, str, str]:
    table = _quote_identifier(expectation.table)
    key_column = _quote_identifier(expectation.key_column)
    value_column = _quote_identifier(expectation.value_column)
    row = connection.execute(
        f"SELECT {value_column} FROM {table} WHERE {key_column} = ?",
        (expectation.key,),
    ).fetchone()
    if row is None:
        raise RestoreRegistryApplicationValidationError(
            f"required metadata key is missing: {expectation.key}"
        )
    observed = str(row[0])
    if observed != expectation.expected_value:
        raise RestoreRegistryApplicationValidationError(
            f"metadata value mismatch for {expectation.key}: "
            f"expected {expectation.expected_value!r}, observed {observed!r}"
        )
    return expectation.table, expectation.key, observed


def _row_count(connection: sqlite3.Connection, table: str) -> int:
    quoted = _quote_identifier(table)
    row = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()
    if row is None:
        raise RestoreRegistryApplicationValidationError(f"could not observe row count for {table}")
    return int(row[0])


def _validate_row_count_invariant(
    row_counts: dict[str, int],
    invariant: RegistryRowCountInvariant,
) -> None:
    try:
        left = row_counts[invariant.left_table]
        right = row_counts[invariant.right_table]
    except KeyError as exc:
        raise RestoreRegistryApplicationValidationError(
            f"row-count invariant references unknown table: {exc.args[0]}"
        ) from exc

    valid = (
        left == right if invariant.operator is RowCountInvariantOperator.EQUAL else left >= right
    )
    if not valid:
        raise RestoreRegistryApplicationValidationError(
            "row-count invariant failed: "
            f"{invariant.left_table} {invariant.operator.value} "
            f"{invariant.right_table}"
        )


def _quote_identifier(identifier: str) -> str:
    if not identifier or "\x00" in identifier:
        raise RestoreRegistryApplicationValidationError("SQLite identifier is invalid")
    return '"' + identifier.replace('"', '""') + '"'
