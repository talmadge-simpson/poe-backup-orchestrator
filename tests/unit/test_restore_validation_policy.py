from pathlib import Path

import pytest

from poe_backup_orchestrator.services.restore import (
    RestoreValidationPolicyError,
    load_restore_validation_policy,
)


def test_load_policy(tmp_path: Path) -> None:
    path = tmp_path / "policy.toml"
    path.write_text(
        '[policy]\nid = "poe-registry"\nversion = "1.0"\n\n'
        '[required_columns]\nassets = ["asset_id", "name"]\n',
        encoding="utf-8",
    )
    policy = load_restore_validation_policy(path)
    assert policy.policy_id == "poe-registry"
    assert dict(policy.required_columns)["assets"] == ("asset_id", "name")


def test_missing_policy_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(RestoreValidationPolicyError, match="not found"):
        load_restore_validation_policy(tmp_path / "missing.toml")


def test_load_policy_reads_tables_allowed_empty(tmp_path: Path) -> None:
    policy_path = tmp_path / "policy.toml"
    policy_path.write_text(
        (
            "[policy]\n"
            'id = "registry-policy"\n'
            'version = "1.1"\n'
            'tables_allowed_empty = ["projects", "relationships"]\n'
            "\n"
            "[required_columns]\n"
            'projects = ["project_id"]\n'
            'relationships = ["relationship_id"]\n'
        ),
        encoding="utf-8",
    )

    policy = load_restore_validation_policy(policy_path)

    assert policy.tables_allowed_empty == ("projects", "relationships")


def test_load_policy_defaults_tables_allowed_empty_to_empty_tuple(
    tmp_path: Path,
) -> None:
    policy_path = tmp_path / "policy.toml"
    policy_path.write_text(
        (
            "[policy]\n"
            'id = "registry-policy"\n'
            'version = "1.0"\n'
            "\n"
            "[required_columns]\n"
            'assets = ["asset_id"]\n'
        ),
        encoding="utf-8",
    )

    policy = load_restore_validation_policy(policy_path)

    assert policy.tables_allowed_empty == ()


def test_load_policy_rejects_non_array_tables_allowed_empty(
    tmp_path: Path,
) -> None:
    policy_path = tmp_path / "policy.toml"
    policy_path.write_text(
        (
            "[policy]\n"
            'id = "registry-policy"\n'
            'version = "1.0"\n'
            'tables_allowed_empty = "projects"\n'
            "\n"
            "[required_columns]\n"
            'projects = ["project_id"]\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        RestoreValidationPolicyError,
        match="tables_allowed_empty must be a TOML array",
    ):
        load_restore_validation_policy(policy_path)


def test_load_policy_without_policy_table_raises_governed_error(
    tmp_path: Path,
) -> None:
    policy_path = tmp_path / "policy.toml"
    policy_path.write_text(
        '[required_columns]\nassets = ["asset_id"]\n',
        encoding="utf-8",
    )

    with pytest.raises(
        RestoreValidationPolicyError,
        match="policy must be a TOML table",
    ):
        load_restore_validation_policy(policy_path)
