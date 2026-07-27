"""Read-only discovery of governed Registry recovery-point packages."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Final

from poe_backup_orchestrator.models.recovery import (
    RecoveryPoint,
    RecoveryPointEligibility,
    RecoveryPointEligibilityResult,
    RecoveryPointReasonCode,
)
from poe_backup_orchestrator.models.recovery_manifest import RecoveryManifestFaultCode
from poe_backup_orchestrator.services.restore.manifest import (
    RecoveryManifestError,
    read_recovery_manifest,
)

DEFAULT_RECOVERY_MANIFEST_FILENAME: Final[str] = "manifest.json"
DEFAULT_DISCOVERY_POLICY_VERSION: Final[str] = "5A.3-discovery"

_IGNORED_PACKAGE_SUFFIXES: Final[tuple[str, ...]] = (
    ".partial",
    ".tmp",
    ".staging",
)

_MANIFEST_FAULT_REASON_CODES: Final[dict[RecoveryManifestFaultCode, RecoveryPointReasonCode]] = {
    RecoveryManifestFaultCode.NOT_FOUND: RecoveryPointReasonCode.MANIFEST_MISSING,
    RecoveryManifestFaultCode.UNREADABLE: RecoveryPointReasonCode.MANIFEST_UNREADABLE,
    RecoveryManifestFaultCode.INVALID_JSON: RecoveryPointReasonCode.MANIFEST_INVALID,
    RecoveryManifestFaultCode.ROOT_NOT_OBJECT: RecoveryPointReasonCode.MANIFEST_INVALID,
    RecoveryManifestFaultCode.REQUIRED_FIELD_MISSING: (RecoveryPointReasonCode.MANIFEST_INVALID),
    RecoveryManifestFaultCode.FIELD_TYPE_INVALID: RecoveryPointReasonCode.MANIFEST_INVALID,
    RecoveryManifestFaultCode.FIELD_VALUE_INVALID: (RecoveryPointReasonCode.MANIFEST_INVALID),
    RecoveryManifestFaultCode.VERSION_UNSUPPORTED: (
        RecoveryPointReasonCode.MANIFEST_VERSION_UNSUPPORTED
    ),
    RecoveryManifestFaultCode.ACQUISITION_TYPE_UNSUPPORTED: (
        RecoveryPointReasonCode.MANIFEST_INVALID
    ),
    RecoveryManifestFaultCode.SNAPSHOT_FILENAME_UNSAFE: (RecoveryPointReasonCode.MANIFEST_INVALID),
    RecoveryManifestFaultCode.CHECKSUM_INVALID: RecoveryPointReasonCode.CHECKSUM_INVALID,
    RecoveryManifestFaultCode.TIMESTAMP_INVALID: RecoveryPointReasonCode.MANIFEST_INVALID,
}


class RecoveryPointDiscoveryError(RuntimeError):
    """Raised when the configured recovery-point root cannot be inspected safely."""


def locate_recovery_point_packages(destination_root: Path) -> tuple[Path, ...]:
    """Return deterministic candidate package directories beneath an accepted root.

    Discovery is intentionally shallow because Registry acceptance publishes each
    governed acquisition as one immediate child directory of the destination root.
    Hidden directories and known temporary publication directories are excluded.
    """

    root = Path(destination_root).expanduser().resolve()
    if not root.exists():
        raise RecoveryPointDiscoveryError(f"recovery-point destination root does not exist: {root}")
    if not root.is_dir():
        raise RecoveryPointDiscoveryError(
            f"recovery-point destination root is not a directory: {root}"
        )

    try:
        candidates = tuple(
            sorted(
                (
                    entry.resolve()
                    for entry in root.iterdir()
                    if entry.is_dir() and _is_candidate_package(entry)
                ),
                key=lambda value: value.name,
            )
        )
    except OSError as exc:
        raise RecoveryPointDiscoveryError(
            f"unable to enumerate recovery-point destination root {root}: {exc}"
        ) from exc

    return candidates


def discover_recovery_points(
    destination_root: Path,
    *,
    evaluated_at_utc: datetime,
    policy_version: str = DEFAULT_DISCOVERY_POLICY_VERSION,
) -> tuple[RecoveryPoint, ...]:
    """Discover candidate recovery points without making eligibility decisions.

    Every candidate package becomes a RecoveryPoint. Malformed or incomplete
    packages are retained with UNKNOWN eligibility and a stable inspection reason,
    allowing later policy evaluation and operator evidence to account for them.
    """

    packages = locate_recovery_point_packages(destination_root)
    points = tuple(
        _discover_package(
            package_path,
            evaluated_at_utc=evaluated_at_utc,
            policy_version=policy_version,
        )
        for package_path in packages
    )
    return tuple(sorted(points, key=_recovery_point_sort_key))


def _discover_package(
    package_path: Path,
    *,
    evaluated_at_utc: datetime,
    policy_version: str,
) -> RecoveryPoint:
    manifest_path = package_path / DEFAULT_RECOVERY_MANIFEST_FILENAME

    try:
        manifest = read_recovery_manifest(manifest_path)
    except RecoveryManifestError as exc:
        return RecoveryPoint(
            recovery_point_id=package_path.name,
            package_path=package_path,
            artifact_path=None,
            manifest_path=manifest_path,
            source_backup_execution_id=package_path.name,
            source_registry_id=None,
            created_at_utc=None,
            artifact_size_bytes=None,
            artifact_sha256=None,
            manifest_version=None,
            backup_status=None,
            verification_status=None,
            quarantined=False,
            eligibility=_unknown_eligibility(
                evaluated_at_utc=evaluated_at_utc,
                policy_version=policy_version,
                reason_code=_MANIFEST_FAULT_REASON_CODES[exc.fault_code],
                warning=str(exc),
            ),
        )

    artifact_path = package_path / manifest.snapshot.filename
    return RecoveryPoint(
        recovery_point_id=package_path.name,
        package_path=package_path,
        artifact_path=artifact_path,
        manifest_path=manifest_path,
        source_backup_execution_id=package_path.name,
        source_registry_id=manifest.asset_id,
        created_at_utc=manifest.created_at_utc,
        artifact_size_bytes=manifest.snapshot.size_bytes,
        artifact_sha256=manifest.snapshot.sha256,
        manifest_version=manifest.schema_version,
        backup_status=None,
        verification_status=manifest.verification.status,
        quarantined=False,
        eligibility=_unknown_eligibility(
            evaluated_at_utc=evaluated_at_utc,
            policy_version=policy_version,
            reason_code=RecoveryPointReasonCode.STATUS_UNDETERMINED,
            warning="Recovery point discovered; eligibility has not been evaluated.",
        ),
    )


def _unknown_eligibility(
    *,
    evaluated_at_utc: datetime,
    policy_version: str,
    reason_code: RecoveryPointReasonCode,
    warning: str,
) -> RecoveryPointEligibilityResult:
    return RecoveryPointEligibilityResult(
        classification=RecoveryPointEligibility.UNKNOWN,
        reason_codes=(reason_code,),
        warnings=(warning,),
        override_required=False,
        evaluated_at_utc=evaluated_at_utc,
        policy_version=policy_version,
    )


def _is_candidate_package(path: Path) -> bool:
    name = path.name
    return (
        not name.startswith(".")
        and not name.endswith(_IGNORED_PACKAGE_SUFFIXES)
        and name not in {"lost+found"}
    )


def _recovery_point_sort_key(point: RecoveryPoint) -> tuple[int, float, str]:
    if point.created_at_utc is None:
        return (1, 0.0, point.recovery_point_id)
    return (0, -point.created_at_utc.timestamp(), point.recovery_point_id)
