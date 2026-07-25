"""Create and publish a consistent POE Registry SQLite snapshot.

This utility runs on the Windows Registry host. It creates a transactionally
consistent local SQLite snapshot, verifies it, computes a SHA-256 digest,
writes an acquisition manifest, and publishes the artifacts to the POE NAS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_ASSET_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


class AcquisitionError(Exception):
    """Raised when Registry acquisition cannot be completed."""


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""
    digest = hashlib.sha256()

    with path.open("rb") as input_file:
        for block in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


def validate_asset_id(asset_id: str) -> str:
    """Validate and normalize an acquisition asset identifier."""
    normalized = asset_id.strip().lower()

    if not _ASSET_ID_PATTERN.fullmatch(normalized):
        raise AcquisitionError(
            "Asset ID must contain only lowercase letters, numbers, hyphens, and underscores."
        )

    return normalized


def sqlite_uri(path: Path, *, mode: str) -> str:
    """Return a SQLite file URI with the requested access mode."""
    return f"{path.resolve().as_uri()}?mode={mode}"


def create_local_snapshot(source_path: Path, snapshot_path: Path) -> str:
    """Create and verify a transactionally consistent SQLite snapshot."""
    source_connection: sqlite3.Connection | None = None
    destination_connection: sqlite3.Connection | None = None

    try:
        source_connection = sqlite3.connect(
            sqlite_uri(source_path, mode="ro"),
            uri=True,
            timeout=30,
        )
        destination_connection = sqlite3.connect(snapshot_path, timeout=30)

        source_connection.backup(destination_connection)
        destination_connection.commit()

        integrity_row = destination_connection.execute("PRAGMA integrity_check").fetchone()

        integrity_check = str(integrity_row[0]) if integrity_row is not None else "unknown"

        if integrity_check.casefold() != "ok":
            raise AcquisitionError(f"Snapshot integrity check failed: {integrity_check}")

        return integrity_check

    except sqlite3.Error as exc:
        raise AcquisitionError(f"SQLite snapshot failed: {exc}") from exc

    finally:
        if destination_connection is not None:
            destination_connection.close()

        if source_connection is not None:
            source_connection.close()


def publish_file(local_path: Path, final_path: Path) -> None:
    """Publish a file using a temporary name followed by atomic rename."""
    partial_path = final_path.with_name(final_path.name + ".partial")

    if partial_path.exists():
        partial_path.unlink()

    shutil.copy2(local_path, partial_path)

    with partial_path.open("rb") as published_file:
        os.fsync(published_file.fileno())

    partial_path.replace(final_path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write deterministic UTF-8 JSON."""
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def acquire_registry(
    source_path: Path,
    destination_root: Path,
    asset_id: str,
) -> tuple[Path, Path, dict[str, Any]]:
    """Create and publish a verified Registry snapshot and manifest."""
    source_path = source_path.expanduser().resolve()
    destination_root = destination_root.expanduser()
    normalized_asset_id = validate_asset_id(asset_id)

    if not source_path.is_file():
        raise AcquisitionError(f"Registry database not found: {source_path}")

    if not destination_root.is_dir():
        raise AcquisitionError(f"Acquisition destination not found: {destination_root}")

    created_at = datetime.now(UTC)
    created_at_text = created_at.strftime("%Y-%m-%dT%H:%M:%SZ")
    filename_timestamp = created_at.strftime("%Y%m%dT%H%M%SZ")

    asset_directory = destination_root / normalized_asset_id
    asset_directory.mkdir(parents=True, exist_ok=True)

    snapshot_name = f"{normalized_asset_id}_{filename_timestamp}.sqlite3"
    manifest_name = f"{normalized_asset_id}_{filename_timestamp}.manifest.json"

    published_snapshot = asset_directory / snapshot_name
    published_manifest = asset_directory / manifest_name

    if published_snapshot.exists() or published_manifest.exists():
        raise AcquisitionError(f"Acquisition timestamp collision: {filename_timestamp}")

    with tempfile.TemporaryDirectory(prefix="poe-registry-acquisition-") as temporary_directory:
        temporary_root = Path(temporary_directory)
        local_snapshot = temporary_root / snapshot_name
        local_manifest = temporary_root / manifest_name

        integrity_check = create_local_snapshot(
            source_path,
            local_snapshot,
        )

        size_bytes = local_snapshot.stat().st_size
        sha256 = sha256_file(local_snapshot)

        manifest: dict[str, Any] = {
            "schema_version": "1.0",
            "acquisition_type": "windows_sqlite_snapshot",
            "asset_id": normalized_asset_id,
            "created_at": created_at_text,
            "source": {
                "hostname": os.environ.get("COMPUTERNAME", ""),
                "path": str(source_path),
                "journal_mode": "wal",
            },
            "snapshot": {
                "filename": snapshot_name,
                "size_bytes": size_bytes,
                "sha256": sha256,
            },
            "verification": {
                "sqlite_integrity_check": integrity_check,
                "status": "PASS",
            },
            "publication": {
                "destination_root": str(destination_root),
                "manifest_published_last": True,
            },
        }

        write_json(local_manifest, manifest)

        publish_file(local_snapshot, published_snapshot)
        publish_file(local_manifest, published_manifest)

    return published_snapshot, published_manifest, manifest


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""
    parser = argparse.ArgumentParser(
        description=("Create and publish a consistent POE Registry SQLite snapshot.")
    )

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Path to the production POE Registry SQLite database.",
    )
    parser.add_argument(
        "--destination",
        required=True,
        type=Path,
        help="NAS acquisition directory.",
    )
    parser.add_argument(
        "--asset-id",
        default="poe-registry",
        help="Stable acquisition asset identifier.",
    )

    return parser


def main() -> int:
    """Run the Registry acquisition utility."""
    arguments = build_parser().parse_args()

    try:
        snapshot_path, manifest_path, manifest = acquire_registry(
            source_path=arguments.source,
            destination_root=arguments.destination,
            asset_id=arguments.asset_id,
        )
    except (AcquisitionError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("POE Windows Registry Acquisition")
    print(f"Source: {arguments.source}")
    print(f"Snapshot: {snapshot_path}")
    print(f"Manifest: {manifest_path}")
    print(f"Size: {manifest['snapshot']['size_bytes']} bytes")
    print(f"SHA-256: {manifest['snapshot']['sha256']}")
    print(f"SQLite integrity check: {manifest['verification']['sqlite_integrity_check']}")
    print("Result: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
