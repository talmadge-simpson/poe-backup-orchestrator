# POE Backup Orchestrator Architecture Intent — Slice 5D-2

## Rollback Artifact Capture and Validation

**Status:** Implementation baseline
**Phase:** 5D — Controlled Restore Execution Preparation
**Slice:** 5D-2
**Baseline:** `4166329`
**Feature branch:** `feature/restore-rollback-artifact-capture`

## 1. Purpose

Slice 5D-2 captures the current authoritative Registry as a rollback artifact
when Slice 5D-1 has determined that rollback protection is required.

The rollback copy is written only to the exact destination established by the
restore plan and confirmed by authoritative-target preflight evidence.

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
cryptographic and SQLite integrity validation
    ↓
Registry application validation
    ↓
authoritative target preflight
    ↓
rollback planning
    ↓
rollback artifact capture and validation
    ↓
future authoritative promotion
```

## 3. Capture Preconditions

Rollback capture proceeds only when:

- authoritative-target preflight status is `ready`;
- the preflight evidence belongs to the same restore plan;
- the authoritative target path matches the plan;
- rollback is required;
- the rollback source equals the authoritative target;
- the rollback destination equals the plan;
- the destination does not already exist;
- and the authoritative target still matches the observations recorded during
  preflight.

A preflight result declaring rollback unnecessary produces explicit
`not_required` evidence and performs no copy.

## 4. Capture Method

The service:

1. re-observes the authoritative source;
2. rejects drift from preflight evidence;
3. creates the rollback destination exclusively;
4. streams source bytes into the destination;
5. flushes and synchronizes the rollback file;
6. applies the source file mode;
7. validates byte count and SHA-256 identity;
8. validates that the authoritative source remained stable;
9. and removes the incomplete destination if capture fails.

The authoritative source is opened read-only.

## 5. Atomicity Boundary

The final rollback destination is created with exclusive creation semantics.
The service does not overwrite an existing path.

This slice does not yet introduce a temporary-file rename protocol because the
rollback destination itself is an immutable, newly created recovery artifact.
Any failed or incomplete artifact is removed before the error is returned.

## 6. Evidence Contract

Successful capture emits immutable `RestoreRollbackArtifactCapture` evidence:

- schema version;
- plan identifier;
- capture timestamp;
- status;
- stable reason codes;
- source path;
- destination path;
- whether capture was required;
- source observation;
- rollback observation;
- copied byte count;
- checksum match;
- source stability;
- rollback mode preservation;
- and explicit confirmation that neither staged nor authoritative bytes were
  modified.

## 7. Validation Guarantees

For required capture:

- source and rollback byte counts must match;
- source and rollback SHA-256 digests must match;
- rollback mode must match source mode;
- authoritative source identity must remain stable during capture;
- rollback destination must be a regular file;
- and incomplete rollback artifacts must not remain after failure.

## 8. Safety Boundary

Slice 5D-2 must not:

- modify the staged restore artifact;
- modify or replace the authoritative Registry;
- stop Registry consumers;
- acquire promotion ownership;
- authorize execution;
- promote the staged Registry;
- or certify restore completion.

## 9. Failure Semantics

Unsafe conditions raise `RestoreRollbackArtifactCaptureError`.

The service fails closed for:

- mismatched evidence;
- source drift after preflight;
- destination pre-existence;
- non-regular source or destination;
- read or write failures;
- byte-count mismatch;
- digest mismatch;
- mode mismatch;
- source mutation during capture;
- and non-UTC timestamps.

## 10. Acceptance Criteria

Slice 5D-2 is accepted when:

- rollback-not-required evidence is emitted without filesystem mutation;
- required rollback bytes are copied to the exact planned destination;
- exclusive destination creation is enforced;
- source drift is rejected;
- byte count and SHA-256 are validated;
- source mode is preserved;
- failed captures leave no incomplete artifact;
- immutable evidence is emitted;
- authoritative and staged bytes remain unchanged;
- focused tests pass;
- and the complete quality baseline passes.

## 11. Deferred Work

Deferred capabilities include:

- rollback manifest persistence;
- restore execution ownership;
- consumer quiescence;
- staged artifact promotion;
- post-promotion validation;
- automated rollback execution;
- interrupted promotion recovery;
- and final restore certification.
