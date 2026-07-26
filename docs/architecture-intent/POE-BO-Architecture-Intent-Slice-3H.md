# POE Backup Orchestrator Architecture Intent — Slice 3H

## End-to-End Operational Acceptance and Evidence Capture

### Status

Implementation baseline for Slice 3H.

## 1. Purpose

Slice 3H establishes a governed operational-acceptance layer around the
production Registry backup execution path introduced in Slice 3G.

The slice must prove that the production CLI can execute the complete workflow
against the managed POE repository and leave durable, machine-verifiable
acceptance evidence.

## 2. Architectural Position

```text
CLI acceptance-run command
    ↓
OperationalAcceptanceService
    ↓
RegistryBackupRunService
    ↓
RegistryBackupOrchestrator
    ↓
Operational report publication
    ↓
Post-run evidence verification
    ↓
Atomic acceptance evidence publication
```

The CLI remains a presentation boundary. It does not perform evidence
verification itself.

## 3. Acceptance Invariants

A run passes operational acceptance only when:

1. The source SQLite database exists before execution.
2. The governed Registry backup run succeeds.
3. The source remains present and byte-identical.
4. The accepted snapshot and manifest exist.
5. The accepted snapshot size and SHA-256 match the acceptance result.
6. The operational JSON and text reports exist.
7. The JSON report identifies the same successful job.
8. The JSON report references the accepted destination.
9. The repository validates successfully after execution.
10. Paired acceptance evidence is published atomically.

## 4. Evidence Package

Each execution publishes:

```text
<reports_root>/Backup-Orchestrator/Acceptance/
    registry-backup-acceptance-<job-id>.json
    registry-backup-acceptance-<job-id>.txt
```

The evidence records source identity, accepted artifact identity, operational
report identity, repository validation before and after execution, named
acceptance checks, issues, status, and exit code.

## 5. Exit Policy

- `0`: all acceptance invariants pass.
- `70`: the acceptance procedure completes but one or more invariants fail.
- `60`: acceptance evidence publication fails.
- Existing governed workflow exit codes remain authoritative for the underlying
  Registry backup run.

## 6. Safety Properties

- Source data is read-only from the acceptance layer.
- Accepted artifacts are inspected without modification.
- Evidence files use staged writes, fsync, atomic replacement, and rollback.
- No staging or accepted artifacts are deleted.
- Registry acceptance locking remains authoritative.

## 7. Testing

Tests cover successful acceptance, source mutation, failed governed execution,
report identity mismatch, post-run repository failure, evidence publication,
and CLI delegation.

## 8. Out of Scope

Systemd installation, scheduling, retention, restore automation, notification,
and production service-account deployment remain later slices.

## 9. Completion Criteria

Slice 3H is complete when static analysis and all automated tests pass, the real
`acceptance-run` command succeeds against the controlled Registry source, and
the resulting evidence package is reviewed and approved.
