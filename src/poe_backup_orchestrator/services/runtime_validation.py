"""Runtime filesystem, identity, and capability validation."""

from __future__ import annotations

import grp
import os
import pwd
import tempfile
from collections.abc import Iterable
from pathlib import Path

from poe_backup_orchestrator.models.runtime import (
    RuntimeDescriptor,
    RuntimeEnvironment,
    RuntimeValidationCheck,
    RuntimeValidationResult,
)


def validate_runtime(
    descriptor: RuntimeDescriptor,
    *,
    repository_paths: Iterable[Path] = (),
) -> RuntimeValidationResult:
    """Validate the runtime contract without retaining probe artifacts."""
    checks: list[RuntimeValidationCheck] = [
        _file_check("configuration_file", descriptor.config_path)
    ]
    checks.extend(_directory_checks("state_root", descriptor.state_root))
    checks.extend(_directory_checks("log_root", descriptor.log_root))
    checks.extend(_identity_checks(descriptor))

    for index, path in enumerate(repository_paths, start=1):
        checks.extend(_directory_checks(f"repository_path_{index}", Path(path)))

    return RuntimeValidationResult(descriptor=descriptor, checks=tuple(checks))


def require_valid_runtime(result: RuntimeValidationResult) -> None:
    """Raise a controlled bootstrap failure when runtime validation fails."""
    if result.is_valid:
        return
    from poe_backup_orchestrator.exceptions import BootstrapError

    failures = "; ".join(check.detail for check in result.checks if not check.passed)
    raise BootstrapError(f"Runtime validation failed: {failures}")


def _file_check(name: str, path: Path) -> RuntimeValidationCheck:
    passed = path.is_file() and os.access(path, os.R_OK)
    detail = (
        f"{path} is a readable regular file."
        if passed
        else f"{path} is missing, unreadable, or not a regular file."
    )
    return RuntimeValidationCheck(name, passed, detail)


def _directory_checks(name: str, path: Path) -> tuple[RuntimeValidationCheck, ...]:
    exists = path.is_dir()
    accessible = exists and os.access(path, os.R_OK | os.W_OK | os.X_OK)
    capability = False
    capability_detail = f"{path} is unavailable for capability validation."

    if accessible:
        try:
            descriptor, raw_path = tempfile.mkstemp(
                dir=path,
                prefix=".poe-runtime-validation-",
                suffix=".tmp",
            )
            os.close(descriptor)
            probe = Path(raw_path)
            probe.write_text("POE runtime validation\n", encoding="utf-8")
            probe.unlink()
            capability = True
            capability_detail = f"{path} supports create, write, and remove operations."
        except OSError as exc:
            capability_detail = f"{path} capability probe failed: {exc}"

    return (
        RuntimeValidationCheck(
            f"{name}_directory",
            exists,
            f"{path} is a directory." if exists else f"{path} is not an available directory.",
        ),
        RuntimeValidationCheck(
            f"{name}_access",
            accessible,
            (
                f"{path} is readable, writable, and searchable."
                if accessible
                else f"{path} lacks required read, write, or search access."
            ),
        ),
        RuntimeValidationCheck(f"{name}_capability", capability, capability_detail),
    )


def _identity_checks(
    descriptor: RuntimeDescriptor,
) -> tuple[RuntimeValidationCheck, ...]:
    try:
        expected_user = pwd.getpwnam(descriptor.service_account)
        account_exists = True
        account_detail = (
            f"Service account {descriptor.service_account} exists with UID {expected_user.pw_uid}."
        )
    except KeyError:
        expected_user = None
        account_exists = False
        account_detail = f"Service account {descriptor.service_account} does not exist."

    try:
        expected_group = grp.getgrnam(descriptor.service_group)
        group_exists = True
        group_detail = (
            f"Service group {descriptor.service_group} exists with GID {expected_group.gr_gid}."
        )
    except KeyError:
        expected_group = None
        group_exists = False
        group_detail = f"Service group {descriptor.service_group} does not exist."

    identity_required = descriptor.environment is RuntimeEnvironment.PRODUCTION
    identity_matches = not identity_required or (
        expected_user is not None
        and expected_group is not None
        and os.geteuid() == expected_user.pw_uid
        and os.getegid() == expected_group.gr_gid
    )
    identity_detail = (
        (
            f"Process identity matches {descriptor.service_account}:{descriptor.service_group}."
            if identity_matches
            else (
                "Process identity does not match production service identity "
                f"{descriptor.service_account}:{descriptor.service_group}."
            )
        )
        if identity_required
        else "Development and test runtimes do not require production service identity."
    )

    return (
        RuntimeValidationCheck("service_account_exists", account_exists, account_detail),
        RuntimeValidationCheck("service_group_exists", group_exists, group_detail),
        RuntimeValidationCheck("process_identity", identity_matches, identity_detail),
    )
