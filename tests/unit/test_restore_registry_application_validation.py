"""Tests for policy-driven staged Registry application validation."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from poe_backup_orchestrator.models import (
    RESTORE_PLAN_POLICY_VERSION,
    RESTORE_PLAN_SCHEMA_VERSION,
    RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION,
    RegistryApplicationValidationPolicy,
    RegistryMetadataExpectation,
    RegistryRowCountInvariant,
    RestoreAction,
    RestoreActionType,
    RestorePlan,
    RestorePlanReadiness,
    RestorePlanReasonCode,
    RestorePlanValidation,
    RestoreStagedArtifactValidation,
    RestoreStagedArtifactValidationReasonCode,
    RestoreStagedArtifactValidationStatus,
    RowCountInvariantOperator,
)
from poe_backup_orchestrator.services.restore import (
    RestoreRegistryApplicationValidationError,
    validate_staged_registry_application,
)

NOW = datetime(2026, 7, 28, 19, 0, tzinfo=UTC)


def _create_registry(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.executescript(
            """
            CREATE TABLE registry_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE assets (
                asset_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );
            CREATE TABLE locations (
                location_id INTEGER PRIMARY KEY,
                asset_id INTEGER NOT NULL,
                path TEXT NOT NULL
            );
            INSERT INTO registry_metadata(key, value)
            VALUES ('schema_version', '5');
            INSERT INTO assets(name) VALUES ('POE Registry');
            INSERT INTO locations(asset_id, path)
            VALUES (1, '/srv/poe/registry');
            """
        )
        connection.commit()
    finally:
        connection.close()


def _plan(tmp_path: Path) -> RestorePlan:
    source = tmp_path / "source.sqlite3"
    staged = tmp_path / "staging" / "registry.sqlite3"
    _create_registry(source)
    staged.parent.mkdir(parents=True)
    staged.write_bytes(source.read_bytes())

    return RestorePlan(
        schema_version=RESTORE_PLAN_SCHEMA_VERSION,
        policy_version=RESTORE_PLAN_POLICY_VERSION,
        plan_id="plan-application-validation",
        created_at_utc=NOW,
        recovery_point_id="rp-application-validation",
        source_artifact_path=source,
        source_manifest_path=tmp_path / "manifest.json",
        authoritative_target_path=tmp_path / "authoritative.sqlite3",
        staging_target_path=staged,
        rollback_artifact_path=tmp_path / "rollback.sqlite3",
        actions=(
            RestoreAction(
                1,
                RestoreActionType.INSPECT_TARGET,
                "Inspect target.",
                destination_path=tmp_path / "authoritative.sqlite3",
            ),
        ),
        validation=RestorePlanValidation(
            readiness=RestorePlanReadiness.READY,
            reason_codes=(RestorePlanReasonCode.PLAN_READY,),
            warnings=(),
            conflicts=(),
            approval_required=False,
            evaluated_at_utc=NOW,
        ),
        execution_authorized=False,
    )


def _staged_validation(plan: RestorePlan) -> RestoreStagedArtifactValidation:
    payload = plan.staging_target_path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    size = len(payload)
    return RestoreStagedArtifactValidation(
        schema_version=RESTORE_STAGED_ARTIFACT_VALIDATION_SCHEMA_VERSION,
        plan_id=plan.plan_id,
        validated_at_utc=NOW,
        status=RestoreStagedArtifactValidationStatus.VALID,
        reason_codes=(
            RestoreStagedArtifactValidationReasonCode.BYTE_COUNTS_MATCH,
            RestoreStagedArtifactValidationReasonCode.SHA256_MATCH,
            RestoreStagedArtifactValidationReasonCode.SQLITE_QUICK_CHECK_OK,
            RestoreStagedArtifactValidationReasonCode.SQLITE_INTEGRITY_CHECK_OK,
            RestoreStagedArtifactValidationReasonCode.STAGED_ARTIFACT_VALID,
        ),
        source_path=plan.source_artifact_path,
        staged_path=plan.staging_target_path,
        source_size_bytes=size,
        staged_size_bytes=size,
        source_sha256=digest,
        staged_sha256=digest,
        sqlite_opened_read_only=True,
        quick_check_results=("ok",),
        integrity_check_results=("ok",),
        authoritative_target_modified=False,
    )


def _policy() -> RegistryApplicationValidationPolicy:
    return RegistryApplicationValidationPolicy(
        policy_id="poe-registry-test",
        policy_version="1.0",
        required_columns=(
            ("assets", ("asset_id", "name")),
            ("locations", ("location_id", "asset_id", "path")),
            ("registry_metadata", ("key", "value")),
        ),
        metadata_expectations=(
            RegistryMetadataExpectation(
                table="registry_metadata",
                key_column="key",
                value_column="value",
                key="schema_version",
                expected_value="5",
            ),
        ),
        row_count_invariants=(
            RegistryRowCountInvariant(
                left_table="locations",
                operator=RowCountInvariantOperator.GREATER_THAN_OR_EQUAL,
                right_table="assets",
            ),
        ),
    )


def test_valid_registry_application_passes(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    before = plan.staging_target_path.read_bytes()

    result = validate_staged_registry_application(
        plan,
        _staged_validation(plan),
        _policy(),
        validated_at_utc=NOW,
    )

    assert result.policy_id == "poe-registry-test"
    assert result.metadata_observations == (("registry_metadata", "schema_version", "5"),)
    assert dict(result.row_count_observations)["assets"] == 1
    assert result.staged_artifact_modified is False
    assert result.authoritative_target_modified is False
    assert plan.staging_target_path.read_bytes() == before
    assert not plan.authoritative_target_path.exists()


def test_missing_required_table_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    connection = sqlite3.connect(plan.staging_target_path)
    connection.execute("DROP TABLE locations")
    connection.commit()
    connection.close()

    with pytest.raises(
        RestoreRegistryApplicationValidationError,
        match="required Registry tables are missing: locations",
    ):
        validate_staged_registry_application(
            plan,
            _staged_validation(plan),
            _policy(),
            validated_at_utc=NOW,
        )


def test_missing_required_column_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    policy = RegistryApplicationValidationPolicy(
        policy_id="missing-column",
        policy_version="1.0",
        required_columns=(("assets", ("asset_id", "name", "checksum")),),
    )

    with pytest.raises(
        RestoreRegistryApplicationValidationError,
        match="required columns missing from assets: checksum",
    ):
        validate_staged_registry_application(
            plan,
            _staged_validation(plan),
            policy,
            validated_at_utc=NOW,
        )


def test_metadata_mismatch_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    policy = RegistryApplicationValidationPolicy(
        policy_id="metadata-mismatch",
        policy_version="1.0",
        required_columns=(("registry_metadata", ("key", "value")),),
        metadata_expectations=(
            RegistryMetadataExpectation(
                table="registry_metadata",
                key_column="key",
                value_column="value",
                key="schema_version",
                expected_value="6",
            ),
        ),
    )

    with pytest.raises(
        RestoreRegistryApplicationValidationError,
        match="metadata value mismatch",
    ):
        validate_staged_registry_application(
            plan,
            _staged_validation(plan),
            policy,
            validated_at_utc=NOW,
        )


def test_unexpected_empty_table_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    connection = sqlite3.connect(plan.staging_target_path)
    connection.execute("DELETE FROM locations")
    connection.commit()
    connection.close()

    with pytest.raises(
        RestoreRegistryApplicationValidationError,
        match="unexpectedly empty: locations",
    ):
        validate_staged_registry_application(
            plan,
            _staged_validation(plan),
            _policy(),
            validated_at_utc=NOW,
        )


def test_policy_can_allow_empty_table(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    connection = sqlite3.connect(plan.staging_target_path)
    connection.execute("DELETE FROM locations")
    connection.commit()
    connection.close()
    policy = RegistryApplicationValidationPolicy(
        policy_id="allow-empty",
        policy_version="1.0",
        required_columns=(("locations", ("location_id", "asset_id", "path")),),
        tables_allowed_empty=("locations",),
    )

    result = validate_staged_registry_application(
        plan,
        _staged_validation(plan),
        policy,
        validated_at_utc=NOW,
    )

    assert result.row_count_observations == (("locations", 0),)


def test_row_count_invariant_failure_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    connection = sqlite3.connect(plan.staging_target_path)
    connection.execute("INSERT INTO assets(name) VALUES ('Second asset')")
    connection.commit()
    connection.close()

    with pytest.raises(
        RestoreRegistryApplicationValidationError,
        match="row-count invariant failed",
    ):
        validate_staged_registry_application(
            plan,
            _staged_validation(plan),
            _policy(),
            validated_at_utc=NOW,
        )


def test_evidence_plan_mismatch_is_rejected(tmp_path: Path) -> None:
    plan = _plan(tmp_path)
    evidence = _staged_validation(plan)
    mismatched = RestoreStagedArtifactValidation(
        schema_version=evidence.schema_version,
        plan_id="other-plan",
        validated_at_utc=evidence.validated_at_utc,
        status=evidence.status,
        reason_codes=evidence.reason_codes,
        source_path=evidence.source_path,
        staged_path=evidence.staged_path,
        source_size_bytes=evidence.source_size_bytes,
        staged_size_bytes=evidence.staged_size_bytes,
        source_sha256=evidence.source_sha256,
        staged_sha256=evidence.staged_sha256,
        sqlite_opened_read_only=evidence.sqlite_opened_read_only,
        quick_check_results=evidence.quick_check_results,
        integrity_check_results=evidence.integrity_check_results,
        authoritative_target_modified=False,
    )

    with pytest.raises(
        RestoreRegistryApplicationValidationError,
        match="plan_id does not match",
    ):
        validate_staged_registry_application(
            plan,
            mismatched,
            _policy(),
            validated_at_utc=NOW,
        )
