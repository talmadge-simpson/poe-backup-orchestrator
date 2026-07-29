#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-config/orchestrator.toml}"
REPOSITORY_ROOT="/srv/poe-backup"
RECOVERY_ROOT="${REPOSITORY_ROOT}/Registry/POERegistry"
CERT_ROOT="${REPOSITORY_ROOT}/Restore-Tests/Operational-Certification"
REPORTS_ROOT="${REPOSITORY_ROOT}/Reports/Backup-Orchestrator/Restore/Operational-Certification"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ROOT="${CERT_ROOT}/${STAMP}"
TARGET_ROOT="${RUN_ROOT}/authoritative"
TARGET="${TARGET_ROOT}/poe-registry.sqlite3"
STAGING_ROOT="${RUN_ROOT}/staging"
ROLLBACK_ROOT="${RUN_ROOT}/rollback"
LOCK_PATH="${RUN_ROOT}/locks/restore-execution.lock"
EXECUTIONS_ROOT="${RUN_ROOT}/executions"
EVIDENCE_ROOT="${RUN_ROOT}/evidence"
POLICY="${EVIDENCE_ROOT}/restore-validation-policy.toml"
REPORT="${REPORTS_ROOT}/restore-operational-certification-${STAMP}.txt"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

sqlite_integrity() {
  local database="$1"
  python - "${database}" <<'PY'
import sqlite3
import sys

path = sys.argv[1]
with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as connection:
    result = connection.execute("PRAGMA integrity_check").fetchone()
if result != ("ok",):
    raise SystemExit(f"SQLite integrity check failed for {path}: {result!r}")
print("ok")
PY
}

artifact_for() {
  local recovery_id="$1"
  find "${RECOVERY_ROOT}/${recovery_id}" -maxdepth 1 -type f \
    \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) \
    -print -quit
}

echo "===== PREPARE CERTIFICATION ENVIRONMENT ====="

sudo mkdir -p \
  "${CERT_ROOT}" \
  "${REPORTS_ROOT}"

sudo chown "${USER}:poe-backup" \
  "${CERT_ROOT}" \
  "${REPORTS_ROOT}"

sudo chmod 2770 \
  "${CERT_ROOT}" \
  "${REPORTS_ROOT}"

mkdir -p \
  "${TARGET_ROOT}" \
  "${STAGING_ROOT}" \
  "${ROLLBACK_ROOT}" \
  "$(dirname "${LOCK_PATH}")" \
  "${EXECUTIONS_ROOT}" \
  "${EVIDENCE_ROOT}"

chmod 2770 \
  "${RUN_ROOT}" \
  "${TARGET_ROOT}" \
  "${STAGING_ROOT}" \
  "${ROLLBACK_ROOT}" \
  "$(dirname "${LOCK_PATH}")" \
  "${EXECUTIONS_ROOT}" \
  "${EVIDENCE_ROOT}"

exec > >(tee -a "${REPORT}") 2>&1

echo "===== POE RESTORE OPERATIONAL CERTIFICATION ====="
echo "Timestamp: ${STAMP}"
echo "Configuration: ${CONFIG}"
echo "Run root: ${RUN_ROOT}"
echo "Report: ${REPORT}"
echo

echo "===== REPOSITORY VALIDATION ====="
poe-backup-orchestrator --config "${CONFIG}" validate-repository
echo

mapfile -t RECOVERY_IDS < <(
  find "${RECOVERY_ROOT}" -mindepth 1 -maxdepth 1 -type d \
    ! -name '.locks' -printf '%f\n' | sort -r
)

if (( ${#RECOVERY_IDS[@]} < 2 )); then
  fail "At least two recovery points are required"
fi

NEW_ID="${RECOVERY_IDS[0]}"
OLD_ID="${RECOVERY_IDS[1]}"
NEW_ARTIFACT="$(artifact_for "${NEW_ID}")"
OLD_ARTIFACT="$(artifact_for "${OLD_ID}")"

[[ -n "${NEW_ARTIFACT}" && -f "${NEW_ARTIFACT}" ]] \
  || fail "New recovery artifact not found for ${NEW_ID}"
[[ -n "${OLD_ARTIFACT}" && -f "${OLD_ARTIFACT}" ]] \
  || fail "Old recovery artifact not found for ${OLD_ID}"

echo "===== SELECTED RECOVERY POINTS ====="
echo "Restore recovery point: ${NEW_ID}"
echo "Restore artifact: ${NEW_ARTIFACT}"
echo "Seed recovery point: ${OLD_ID}"
echo "Seed artifact: ${OLD_ARTIFACT}"
echo

echo "===== SOURCE INTEGRITY ====="
echo "New artifact integrity: $(sqlite_integrity "${NEW_ARTIFACT}")"
echo "Old artifact integrity: $(sqlite_integrity "${OLD_ARTIFACT}")"
NEW_HASH="$(sha256sum "${NEW_ARTIFACT}" | awk '{print $1}')"
OLD_HASH="$(sha256sum "${OLD_ARTIFACT}" | awk '{print $1}')"
echo "New artifact SHA-256: ${NEW_HASH}"
echo "Old artifact SHA-256: ${OLD_HASH}"
echo

echo "===== GENERATE EXPLICIT VALIDATION POLICY ====="
python - "${NEW_ARTIFACT}" "${POLICY}" "${STAMP}" <<'PY'
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

database = Path(sys.argv[1])
policy_path = Path(sys.argv[2])
stamp = sys.argv[3]

with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as connection:
    tables = [
        row[0]
        for row in connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
    ]
    if not tables:
        raise SystemExit("No application tables found in restore artifact")

    required: dict[str, list[str]] = {}
    for table in tables:
        quoted = table.replace('"', '""')
        columns = [
            row[1]
            for row in connection.execute(f'PRAGMA table_info("{quoted}")')
        ]
        if not columns:
            raise SystemExit(f"No columns found for table {table}")
        required[table] = columns

allowed_empty = (
    "asset_backup_requirements",
    "asset_operational_status",
    "backup_status",
    "disposition_records",
    "indexing_status",
    "projects",
    "relationships",
    "supersessions",
)

lines = [
    "[policy]",
    'id = "poe-registry-operational-certification"',
    f'version = "{stamp}"',
    "",
    "tables_allowed_empty = [",
    *(f"  {json.dumps(table)}," for table in allowed_empty),
    "]",
    "",
    "[required_columns]",
]
for table, columns in required.items():
    key = json.dumps(table)
    values = ", ".join(json.dumps(column) for column in columns)
    lines.append(f"{key} = [{values}]")

policy_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(policy_path)
PY
cat "${POLICY}"
echo

echo "===== SEED ISOLATED AUTHORITATIVE TARGET ====="
cp --preserve=mode,timestamps "${OLD_ARTIFACT}" "${TARGET}"
PRE_RESTORE_HASH="$(sha256sum "${TARGET}" | awk '{print $1}')"
[[ "${PRE_RESTORE_HASH}" == "${OLD_HASH}" ]] \
  || fail "Seed target hash does not match old recovery artifact"
echo "Target: ${TARGET}"
echo "Pre-restore integrity: $(sqlite_integrity "${TARGET}")"
echo "Pre-restore SHA-256: ${PRE_RESTORE_HASH}"
echo

echo "===== EXECUTE GOVERNED RESTORE ====="
poe-backup-orchestrator \
  --config "${CONFIG}" \
  restore execute \
  --backup-id "${NEW_ID}" \
  --target "${TARGET}" \
  --validation-policy "${POLICY}" \
  --staging-root "${STAGING_ROOT}" \
  --rollback-root "${ROLLBACK_ROOT}" \
  --lock-path "${LOCK_PATH}" \
  --executions-root "${EXECUTIONS_ROOT}" \
  --confirm-execution
echo

echo "===== VERIFY PROMOTED TARGET ====="
POST_RESTORE_HASH="$(sha256sum "${TARGET}" | awk '{print $1}')"
echo "Post-restore integrity: $(sqlite_integrity "${TARGET}")"
echo "Post-restore SHA-256: ${POST_RESTORE_HASH}"
[[ "${POST_RESTORE_HASH}" == "${NEW_HASH}" ]] \
  || fail "Promoted target is not byte-identical to selected restore artifact"
echo "PASS: Promoted target matches selected restore artifact"
echo

echo "===== VERIFY ROLLBACK ARTIFACT ====="
mapfile -t ROLLBACK_FILES < <(
  find "${ROLLBACK_ROOT}" -type f \
    \( -name '*.sqlite' -o -name '*.sqlite3' -o -name '*.db' \) \
    -print | sort
)
(( ${#ROLLBACK_FILES[@]} == 1 )) \
  || fail "Expected exactly one rollback database; found ${#ROLLBACK_FILES[@]}"
ROLLBACK_FILE="${ROLLBACK_FILES[0]}"
ROLLBACK_HASH="$(sha256sum "${ROLLBACK_FILE}" | awk '{print $1}')"
echo "Rollback artifact: ${ROLLBACK_FILE}"
echo "Rollback integrity: $(sqlite_integrity "${ROLLBACK_FILE}")"
echo "Rollback SHA-256: ${ROLLBACK_HASH}"
[[ "${ROLLBACK_HASH}" == "${PRE_RESTORE_HASH}" ]] \
  || fail "Rollback artifact does not match the pre-restore target"
echo "PASS: Rollback artifact matches pre-restore target"
echo

echo "===== VERIFY EXECUTION RECORD ====="
mapfile -t RECORDS < <(
  find "${EXECUTIONS_ROOT}" -maxdepth 1 -type f -name '*.json' -print | sort
)
(( ${#RECORDS[@]} == 1 )) \
  || fail "Expected exactly one execution record; found ${#RECORDS[@]}"
RECORD="${RECORDS[0]}"

SIDECAR=""
for candidate in "${RECORD}.sha256" "${RECORD%.json}.sha256"; do
  if [[ -f "${candidate}" ]]; then
    SIDECAR="${candidate}"
    break
  fi
done
[[ -n "${SIDECAR}" ]] || fail "Execution-record SHA-256 sidecar not found"

RECORDED_HASH="$(awk '{print $1}' "${SIDECAR}")"
ACTUAL_RECORD_HASH="$(sha256sum "${RECORD}" | awk '{print $1}')"
echo "Execution record: ${RECORD}"
echo "Execution sidecar: ${SIDECAR}"
echo "Recorded SHA-256: ${RECORDED_HASH}"
echo "Actual SHA-256: ${ACTUAL_RECORD_HASH}"
[[ "${RECORDED_HASH}" == "${ACTUAL_RECORD_HASH}" ]] \
  || fail "Execution-record sidecar verification failed"
python -m json.tool "${RECORD}" >/dev/null
echo "PASS: Execution record is valid JSON and its sidecar matches"
echo

echo "===== CERTIFICATION RESULT ====="
echo "PASS: Governed restore operational certification completed"
echo "Restore recovery point: ${NEW_ID}"
echo "Seed recovery point: ${OLD_ID}"
echo "Authoritative target: ${TARGET}"
echo "Validation policy: ${POLICY}"
echo "Rollback artifact: ${ROLLBACK_FILE}"
echo "Execution record: ${RECORD}"
echo "Report: ${REPORT}"
