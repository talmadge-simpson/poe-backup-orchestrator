# POE Backup Orchestrator Architecture Intent — Slice 5D-1

## Authoritative Target Preflight and Rollback Planning

**Status:** Implementation baseline
**Phase:** 5D — Controlled Restore Execution Preparation
**Slice:** 5D-1
**Baseline:** `fff3af4`
**Feature branch:** `feature/restore-authoritative-target-preflight`

## 1. Purpose

Slice 5D-1 inspects the authoritative Registry target and determines the
rollback obligations that must be satisfied before any restore execution may
begin.

The slice is observational and planning-only. It does not capture rollback
bytes, acquire execution ownership, or replace the authoritative Registry.

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
future rollback capture and controlled promotion
```

## 3. Authoritative Target States

The preflight service classifies the target as one of:

- `absent`;
- `regular_file`;
- `non_regular_path`;
- `unreadable`.

A missing authoritative target is not inherently an error. It means rollback
capture is not required because no prior authoritative database exists.

A non-regular or unreadable target is unsafe and blocks restore execution.

## 4. Required Observations

When the authoritative target is a regular file, the service records:

- canonical path;
- byte count;
- SHA-256 digest;
- file mode;
- owner user identifier;
- owner group identifier;
- and last-modified timestamp.

The service opens the file read-only and does not change metadata or content.

## 5. Rollback Planning

Rollback planning is deterministic:

- if the target is absent, rollback is not required;
- if the target is a readable regular file, rollback is required;
- the rollback destination must match the restore plan;
- the rollback destination must not already exist;
- the rollback destination must differ from both the authoritative target and
  staged artifact;
- and the rollback parent directory must already exist and be writable.

The planner emits the exact source and destination paths that a later slice
must use for rollback capture.

## 6. Evidence Contract

Successful preflight emits immutable
`RestoreAuthoritativeTargetPreflight` evidence containing:

- schema version;
- plan identifier;
- preflight timestamp;
- target state;
- stable reason codes;
- authoritative target path;
- target observations where applicable;
- rollback requirement;
- rollback source path;
- rollback destination path;
- rollback-parent readiness;
- and explicit confirmation that no authoritative or rollback bytes were
  modified.

## 7. Evidence Chain

The service consumes successful Registry application validation evidence and
rejects:

- plan identifier mismatch;
- staged path mismatch;
- failed or malformed validation status;
- or any evidence indicating prior authoritative modification.

This extends the immutable restore evidence chain through execution
preparation.

## 8. Safety Boundary

Slice 5D-1 must not:

- modify the staged artifact;
- modify the authoritative Registry;
- create the rollback artifact;
- create rollback directories;
- acquire restore execution ownership;
- stop Registry consumers;
- persist approval;
- replace the authoritative target;
- or certify recovery completion.

## 9. Failure Semantics

Unsafe preflight conditions raise
`RestoreAuthoritativeTargetPreflightError`.

The service fails closed for:

- non-regular target paths;
- unreadable target files;
- pre-existing rollback destinations;
- missing rollback parent directories;
- unwritable rollback parent directories;
- path collisions;
- evidence-chain inconsistencies;
- and non-UTC timestamps.

## 10. Acceptance Criteria

Slice 5D-1 is accepted when:

- absent targets are classified correctly;
- regular targets are inspected without mutation;
- SHA-256 and byte count are observed;
- unsafe target types are rejected;
- rollback requirement is derived deterministically;
- rollback path collisions are rejected;
- existing rollback destinations are rejected;
- rollback-parent readiness is enforced;
- successful immutable evidence is emitted;
- no authoritative or rollback bytes are created or changed;
- focused tests pass;
- and the complete quality baseline passes.

## 11. Deferred Work

Deferred capabilities include:

- execution ownership acquisition;
- consumer quiescence;
- rollback artifact capture;
- rollback manifest generation;
- authoritative target promotion;
- post-promotion verification;
- interrupted execution recovery;
- and final restore certification.
