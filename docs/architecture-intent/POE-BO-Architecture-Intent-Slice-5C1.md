# POE Backup Orchestrator Architecture Intent — Slice 5C-1

## Governed Restore Artifact Staging

**Status:** Implementation baseline
**Phase:** 5C — Isolated Restore Preparation
**Slice:** 5C-1
**Baseline:** `c972e27`
**Feature branch:** `feature/restore-artifact-staging`

## 1. Purpose

Slice 5C-1 introduces governed copying of the selected recovery artifact into
the isolated staging workspace.

The staging service consumes an immutable `RestorePlan`, a successful
`RestoreWorkspacePreflight`, and successful
`RestoreWorkspaceMaterialization` evidence. It copies exactly one source
artifact to the plan-defined staging path and returns immutable staging
evidence.

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
artifact staging
    ↓
future checksum and SQLite validation
```

## 3. Inputs

The service accepts:

- one immutable `RestorePlan`;
- one ready `RestoreWorkspacePreflight`;
- one successful `RestoreWorkspaceMaterialization`;
- one explicit timezone-aware UTC staging timestamp;
- and an injectable artifact filesystem operator.

## 4. Output

The service returns immutable `RestoreArtifactStaging` evidence containing:

- schema version;
- plan identifier;
- staging timestamp;
- source path;
- staged path;
- source size;
- staged size;
- status;
- stable reason codes;
- and explicit confirmation that no authoritative target was modified.

## 5. Controlled Mutation

The service may:

- create the staging artifact at the exact plan-defined staging path;
- copy bytes from the selected source artifact;
- flush the staged artifact to stable storage;
- and remove an incomplete staging artifact after failure.

The service must not create any other file.

## 6. Preconditions

Staging is rejected unless:

1. preflight readiness is `ready`;
2. preflight plan identifier matches the supplied plan;
3. materialization plan identifier matches the supplied plan;
4. materialization status is `materialized`;
5. source artifact is a readable regular file;
6. staging parent exists and is a directory;
7. staging artifact does not already exist;
8. rollback artifact does not exist;
9. authoritative target path is distinct from source and staging paths;
10. staging timestamp is timezone-aware UTC.

## 7. Copy Semantics

The initial implementation:

- copies bytes using a temporary sibling path;
- flushes and fsyncs the temporary file;
- atomically renames the temporary file into the final staging path;
- verifies source and staged byte counts are equal;
- and removes the temporary file on failure.

No checksum assertion is introduced in this slice.

## 8. Failure Semantics

Expected environmental conflicts raise `RestoreArtifactStagingError`.

On failure:

- the final staging artifact must not exist unless atomic promotion completed;
- the temporary sibling artifact is removed when possible;
- the source artifact is never modified;
- and cleanup failures are preserved in the raised error message.

## 9. Idempotency

Staging is intentionally not idempotent in this slice.

An existing staging artifact is treated as a conflict and staging is rejected.
A later slice may introduce explicit resume or reconciliation semantics.

## 10. Safety Boundary

Slice 5C-1 must not:

- modify the authoritative Registry;
- create a rollback artifact;
- calculate or verify cryptographic checksums;
- invoke SQLite;
- inspect database contents;
- acquire authoritative target ownership;
- authorize restore execution;
- promote the staged artifact;
- execute rollback;
- or publish final recovery certification.

## 11. Acceptance Criteria

Slice 5C-1 is accepted when:

- immutable staging evidence models exist;
- an injectable artifact filesystem operator exists;
- exactly one plan-defined staging artifact is created;
- copying uses a temporary sibling plus atomic rename;
- byte counts are verified;
- partial temporary artifacts are cleaned up;
- existing staging artifacts are rejected;
- the authoritative target remains untouched;
- focused tests pass;
- and the complete quality baseline passes.

## 12. Deferred Work

Deferred capabilities include:

- SHA-256 verification;
- SQLite integrity validation;
- Registry application validation;
- rollback artifact capture;
- approval persistence;
- target locking;
- authoritative promotion;
- rollback execution;
- interrupted restore recovery;
- and recovery certification.
