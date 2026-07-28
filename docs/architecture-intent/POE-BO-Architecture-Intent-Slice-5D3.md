# POE Backup Orchestrator Architecture Intent — Slice 5D-3

## Restore Execution Ownership and Promotion Readiness

**Status:** Implementation baseline
**Phase:** 5D — Controlled Restore Execution Preparation
**Slice:** 5D-3
**Baseline:** `8239d92`
**Feature branch:** `feature/restore-promotion-readiness`

## 1. Purpose

Slice 5D-3 establishes exclusive restore execution ownership and performs the
final fail-closed readiness evaluation immediately before authoritative
promotion.

This slice does not promote the staged Registry. It only determines whether
all evidence, files, paths, and ownership conditions remain valid.

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
exclusive execution ownership
    ↓
promotion readiness evaluation
    ↓
future authoritative promotion
```

## 3. Exclusive Ownership

Restore execution ownership is represented by an exclusively created lock file.

The lock:

- is created with `O_CREAT | O_EXCL`;
- records the plan identifier, process identifier, hostname, and acquisition
  timestamp;
- is flushed and synchronized;
- blocks concurrent restore execution;
- and is released explicitly by the caller.

The service does not break or replace an existing lock.

## 4. Evidence Chain

Promotion readiness consumes:

- the deterministic restore plan;
- successful staged artifact cryptographic validation evidence;
- successful Registry application validation evidence;
- authoritative target preflight evidence;
- and rollback artifact capture evidence.

The service rejects any mismatch in:

- plan identifier;
- staged artifact path;
- staged artifact byte count and SHA-256 identity;
- authoritative target path;
- rollback destination path;
- rollback requirement;
- or modification flags.

## 5. Immediate Revalidation

While ownership is held, the service revalidates:

- the staged artifact exists and is a regular file;
- staged byte count and SHA-256 exactly match the mandatory staged
  artifact validation evidence;
- the authoritative target still matches preflight observations when it
  existed;
- the authoritative target is still absent when preflight observed absence;
- the rollback artifact exists and matches capture evidence when required;
- the rollback artifact remains absent when not required;
- and all governed paths remain distinct after canonical resolution.

## 6. Readiness Decision

Successful evaluation emits immutable `RestorePromotionReadiness` evidence:

- schema version;
- plan identifier;
- evaluation timestamp;
- status `ready`;
- stable reason codes;
- ownership evidence;
- staged observation;
- authoritative target state;
- rollback observation;
- and explicit confirmation that no governed artifact was modified.

A failed condition raises `RestorePromotionReadinessError`; no partial readiness
record is emitted.

## 7. Safety Boundary

Slice 5D-3 must not:

- modify staged bytes;
- modify authoritative bytes;
- modify rollback bytes;
- create or replace the authoritative Registry;
- stop Registry consumers;
- rename governed files;
- authorize unattended promotion;
- or certify restore completion.

## 8. Failure Semantics

The service fails closed for:

- existing ownership lock;
- missing, malformed, or mismatched evidence;
- staged artifact drift;
- authoritative target drift;
- rollback artifact drift;
- path collisions;
- missing required files;
- unexpected files;
- non-regular paths;
- non-UTC timestamps;
- and lock persistence failures.

## 9. Acceptance Criteria

Slice 5D-3 is accepted when:

- exclusive ownership blocks concurrent evaluation;
- ownership evidence is immutable;
- the lock payload is durable and inspectable;
- staged artifact validation evidence is mandatory;
- staged artifact drift is rejected by byte count and SHA-256;
- authoritative target drift is rejected;
- rollback artifact drift is rejected;
- rollback-not-required state is enforced;
- successful readiness evidence is emitted;
- no governed bytes are modified;
- locks are released explicitly;
- focused tests pass;
- and the complete quality baseline passes.

## 10. Deferred Work

Deferred capabilities include:

- Registry consumer quiescence;
- atomic authoritative promotion;
- post-promotion verification;
- automated rollback execution;
- interrupted promotion recovery;
- promotion journal persistence;
- and final restore certification.

## Cryptographic Evidence Boundary

Promotion readiness consumes the dedicated staged-artifact validation evidence as the mandatory cryptographic chain-of-custody record. Registry application validation remains a separate semantic evidence contract and is not used as an optional source of checksum data.
