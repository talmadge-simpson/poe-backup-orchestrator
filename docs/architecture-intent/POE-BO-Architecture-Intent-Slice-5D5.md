# POE Backup Orchestrator Architecture Intent — Slice 5D-5

**Status:** Implementation baseline
**Phase:** 5D — Controlled Restore Execution
**Slice:** 5D-5
**Baseline:** `25b9081`

## Purpose

Slice 5D-5 verifies the authoritative registry after controlled promotion and
emits immutable restore-completion evidence.

This is the first slice permitted to declare a restore complete. Completion is
allowed only when the authoritative artifact remains identical to the promoted
artifact, the rollback artifact remains unchanged, and execution ownership is
still held by the same restore plan.

## Evidence Chain

```text
Restore Plan
    ↓
Promotion Readiness
    ↓
Controlled Authoritative Promotion
    ↓
Post-Promotion Verification
    ↓
Restore Completion Evidence
```

## Required Preconditions

Verification fails closed unless:

1. The promotion evidence status is `PROMOTED`.
2. Promotion evidence belongs to the same restore plan.
3. Promotion evidence explicitly requires post-promotion verification.
4. Promotion evidence does not already declare restore completion.
5. The authoritative target remains a regular file.
6. Its size and SHA-256 match the promoted observation.
7. The staged path remains consumed.
8. The rollback artifact remains unchanged when present.
9. No rollback artifact appears when none was expected.
10. The execution ownership lock still exists and matches the recorded owner.

## Completion Semantics

Successful verification emits immutable evidence recording:

- schema version;
- plan ID;
- verification timestamp;
- accepted promotion timestamp;
- ownership evidence;
- promoted authoritative observation;
- verified authoritative observation;
- rollback observation, when present;
- staged-path consumption;
- authoritative integrity verification;
- rollback preservation;
- ownership continuity;
- post-promotion verification completion; and
- restore completion.

The verification service is observational. It must not mutate the authoritative
target, rollback artifact, staged path, or ownership lock.

## Failure Semantics

Any mismatch raises a dedicated post-promotion verification error.

A verification failure means promotion occurred but restore completion cannot be
asserted. The caller must preserve promotion and rollback evidence for operator
review or governed rollback.

## Non-Goals

Slice 5D-5 does not:

- release execution ownership;
- delete rollback evidence;
- perform rollback;
- rotate or archive completion evidence;
- expose a production CLI command;
- update external registry consumers; or
- certify end-to-end operational recovery.

Those concerns belong to later restore orchestration and certification slices.

## Acceptance Criteria

Tests must prove:

- successful verification after promotion;
- authoritative drift rejection;
- staged-path reappearance rejection;
- rollback drift rejection;
- unexpected rollback creation rejection;
- ownership-lock loss or replacement rejection;
- promotion evidence mismatch rejection;
- immutable completion evidence;
- restore completion is asserted only after all checks pass.
