# POE Backup Orchestrator Architecture Intent — Slice 5B-5

## Governed Restore Workspace Materialization

**Status:** Implementation baseline
**Phase:** 5B — Governed Restore Planning
**Slice:** 5B-5
**Baseline:** `4285936`
**Feature branch:** `feature/restore-workspace-materialization`

## 1. Purpose

Slice 5B-5 introduces the first controlled filesystem mutation in the restore
domain.

The materialization service consumes an immutable `RestorePlan` and a successful
`RestoreWorkspacePreflight`, then creates only the isolated directory structure
required by future restore staging and rollback preparation.

It does not copy, validate, promote, replace, or remove Registry artifacts.

## 2. Architectural Position

```text
recovery-point discovery
    ↓
eligibility evaluation
    ↓
deterministic restore planning
    ↓
workspace preflight
    ↓
workspace materialization
    ↓
future artifact staging and isolated validation
```

## 3. Inputs

The service accepts:

- one immutable `RestorePlan`;
- one immutable `RestoreWorkspacePreflight`;
- one explicit timezone-aware UTC materialization timestamp;
- and an injectable filesystem operator.

## 4. Output

The service returns immutable `RestoreWorkspaceMaterialization` evidence
containing:

- schema version;
- plan identifier;
- materialization timestamp;
- status;
- ordered directory records;
- created directories;
- reused directories;
- stable reason codes;
- and explicit confirmation that no artifact was copied.

## 5. Controlled Mutations

The service may create only:

- the parent directory of the planned staging artifact;
- the parent directory of the planned rollback artifact;
- and any missing ancestors required to reach those two directories.

Directory creation must use bounded plan-derived paths.

The service must not create either the staging artifact or rollback artifact.

## 6. Preconditions

Materialization is rejected unless:

1. preflight readiness is `ready`;
2. preflight plan identifier matches the supplied plan;
3. preflight reports that no mutation was performed;
4. staging and rollback artifact paths remain absent;
5. the materialization timestamp is timezone-aware UTC.

## 7. Transactional Cleanup

If directory creation fails:

- directories created during the current invocation are removed in reverse
  order when empty;
- pre-existing directories are never removed;
- cleanup failures are preserved in the raised error message;
- and no success evidence is returned.

## 8. Idempotency

Repeated materialization of the same plan is permitted when:

- the staging and rollback artifact paths remain absent;
- and the required workspace directories already exist.

A repeated invocation reports those directories as reused.

## 9. Safety Boundary

Slice 5B-5 must not:

- copy the recovery artifact;
- create the staging artifact;
- create the rollback artifact;
- calculate checksums;
- invoke SQLite;
- inspect database contents;
- create authoritative-target backups;
- acquire restore execution ownership;
- modify the authoritative Registry;
- promote a staged artifact;
- execute rollback;
- or publish final recovery certification.

## 10. Acceptance Criteria

Slice 5B-5 is accepted when:

- immutable materialization evidence models exist;
- a filesystem operator abstraction exists;
- only governed workspace directories are created;
- pre-existing directories are preserved;
- partial creation is cleaned up on failure;
- repeated materialization is safe;
- artifact paths remain absent;
- focused tests pass;
- and the complete quality baseline passes.

## 11. Deferred Work

Deferred capabilities include:

- artifact staging;
- checksum verification;
- SQLite integrity checks;
- Registry application validation;
- rollback artifact capture;
- approval persistence;
- target locking;
- authoritative promotion;
- rollback execution;
- interrupted restore recovery;
- and recovery certification.
