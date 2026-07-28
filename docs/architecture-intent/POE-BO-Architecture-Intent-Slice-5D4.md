# POE Backup Orchestrator Architecture Intent — Slice 5D-4

**Status:** Implementation baseline
**Phase:** 5D — Controlled Restore Execution Preparation
**Slice:** 5D-4
**Baseline:** `47d326c`

## Purpose

Slice 5D-4 introduces the first governed mutation of the authoritative registry:
atomic promotion of the validated staged artifact into the authoritative target
path.

This slice is intentionally narrow. It performs promotion only after consuming
a successful Slice 5D-3 promotion-readiness record, revalidating exclusive
execution ownership, and rechecking every filesystem boundary that could have
changed after readiness evaluation.

The slice does not declare the restore successful. Successful promotion produces
immutable execution evidence and requires a later post-promotion verification
slice before restore completion may be asserted.

## Architectural Boundary

The evidence chain is:

```text
Restore Plan
    ↓
Staged Artifact Validation
    ↓
Registry Application Validation
    ↓
Authoritative Target Preflight
    ↓
Rollback Artifact Capture
    ↓
Promotion Readiness
    ↓
Controlled Authoritative Promotion
    ↓
Post-Promotion Verification (future slice)
```

Promotion execution may mutate only:

- the governed staged path, which is consumed by atomic replacement; and
- the governed authoritative target path.

It must not modify the rollback artifact or release execution ownership.

## Required Preconditions

Promotion execution must fail closed unless all of the following remain true:

1. The promotion-readiness record is `READY`.
2. The readiness record belongs to the same restore plan.
3. Promotion has not already been performed.
4. The ownership lock exists and its serialized identity still matches the
   readiness evidence.
5. The staged artifact remains a regular file and matches the size, SHA-256,
   mode, and path recorded by promotion readiness.
6. The authoritative target still matches the readiness observation, or remains
   absent when readiness recorded an absent target.
7. The rollback artifact remains unchanged when present, and remains absent when
   no rollback capture was required.
8. The staging, authoritative, rollback, and ownership paths remain governed and
   distinct.

## Mutation Semantics

Promotion uses `os.replace()` so replacement of the authoritative path is atomic
within the filesystem namespace.

After replacement, the service must:

- open and `fsync()` the promoted authoritative file;
- `fsync()` the authoritative parent directory;
- re-observe the promoted artifact;
- prove that its size and SHA-256 match the readiness-staged observation; and
- emit immutable execution evidence.

The staged path is expected to be consumed by the atomic replacement.

## Evidence Contract

Successful execution evidence records:

- schema version;
- plan ID;
- execution timestamp;
- accepted readiness timestamp;
- ownership evidence;
- staged observation accepted for promotion;
- prior authoritative observation, when any;
- rollback observation, when any;
- promoted authoritative observation;
- atomic replacement use;
- file and parent-directory durability synchronization;
- staged-path consumption;
- authoritative mutation;
- rollback preservation;
- mandatory post-promotion verification; and
- explicit confirmation that restore completion has not yet been declared.

## Failure Semantics

All precondition failures occur before mutation.

A failure after `os.replace()` is an execution-boundary failure: the
authoritative target may already have changed. The service raises a specific
promotion-execution error and does not claim restore success. Recovery or
rollback orchestration remains outside this slice.

## Non-Goals

Slice 5D-4 does not:

- validate application semantics after promotion;
- declare the restore complete;
- delete or rotate rollback evidence;
- release exclusive execution ownership;
- automatically roll back a failed post-replacement durability check;
- expose a production CLI execution command; or
- bypass any earlier restore evidence contract.

## Acceptance Criteria

The slice is acceptable when tests prove:

- successful atomic promotion over an existing target;
- successful atomic promotion when the target was absent;
- rejection of staged drift;
- rejection of authoritative-target drift;
- rejection of rollback drift;
- rejection of ownership-lock replacement or modification;
- rejection of replay after promotion;
- preservation of rollback evidence;
- staged-path consumption;
- promoted digest equality; and
- explicit post-promotion verification requirement.
