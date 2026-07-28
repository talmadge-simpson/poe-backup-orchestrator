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
