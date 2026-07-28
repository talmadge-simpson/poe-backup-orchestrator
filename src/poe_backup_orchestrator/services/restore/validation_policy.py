from __future__ import annotations

import tomllib
from pathlib import Path

from poe_backup_orchestrator.models import RegistryApplicationValidationPolicy


class RestoreValidationPolicyError(ValueError):
    pass


def load_restore_validation_policy(path: Path) -> RegistryApplicationValidationPolicy:
    candidate = Path(path)
    if not candidate.is_file():
        raise RestoreValidationPolicyError(f"restore validation policy not found: {candidate}")
    try:
        with candidate.open("rb") as stream:
            document = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RestoreValidationPolicyError(
            f"unable to load restore validation policy: {exc}"
        ) from exc

    policy = document.get("policy")
    columns = document.get("required_columns")
    if not isinstance(policy, dict):
        raise RestoreValidationPolicyError("policy must be a TOML table")
    if not isinstance(columns, dict) or not columns:
        raise RestoreValidationPolicyError("required_columns must be a non-empty TOML table")

    try:
        required_columns = tuple(
            (table, tuple(values)) for table, values in sorted(columns.items())
        )
        return RegistryApplicationValidationPolicy(
            policy_id=str(policy["id"]),
            policy_version=str(policy["version"]),
            required_columns=required_columns,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise RestoreValidationPolicyError(str(exc)) from exc
