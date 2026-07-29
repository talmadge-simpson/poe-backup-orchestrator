"""Contract tests for the operational-certification harness."""

from pathlib import Path

HARNESS = Path("scripts/operations/certify_restore_operational.sh")

EXPECTED_ALLOWED_EMPTY = {
    "asset_backup_requirements",
    "asset_operational_status",
    "backup_status",
    "disposition_records",
    "indexing_status",
    "projects",
    "relationships",
    "supersessions",
}


def _harness_text() -> str:
    return HARNESS.read_text(encoding="utf-8")


def test_certification_harness_exists_and_is_strict_shell() -> None:
    harness = _harness_text()

    assert HARNESS.is_file()
    assert harness.startswith("#!/usr/bin/env bash")
    assert "set -euo pipefail" in harness


def test_certification_harness_declares_legitimate_empty_registry_tables() -> None:
    harness = _harness_text()

    for table in EXPECTED_ALLOWED_EMPTY:
        assert f'"{table}"' in harness


def test_certification_harness_generates_explicit_validation_policy() -> None:
    harness = _harness_text()

    assert "tables_allowed_empty" in harness
    assert "required_columns" in harness
    assert "restore-validation-policy.toml" in harness


def test_certification_harness_executes_governed_restore() -> None:
    harness = _harness_text().lower()

    assert "restore execute" in harness
    assert "authoritative" in harness
    assert "rollback" in harness
    assert "execution" in harness


def test_certification_harness_verifies_integrity_and_content_identity() -> None:
    harness = _harness_text().lower()

    assert "sqlite3" in harness
    assert "integrity_check" in harness
    assert "sha256sum" in harness


def test_certification_harness_verifies_execution_record_sidecar() -> None:
    harness = _harness_text()

    assert ".sha256" in harness
    assert "sha256sum" in harness
    assert "Execution sidecar:" in harness
    assert "sidecar matches" in harness


def test_certification_harness_emits_final_certification_result() -> None:
    harness = _harness_text()

    assert "CERTIFICATION RESULT" in harness
    assert "Governed restore operational certification completed" in harness
