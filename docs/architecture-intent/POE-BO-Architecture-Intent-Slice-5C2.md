# POE Backup Orchestrator Architecture Intent — Slice 5C-2

## Staged Artifact Integrity Validation

**Status:** Implementation baseline
**Phase:** 5C — Isolated Restore Preparation
**Slice:** 5C-2
**Baseline:** `f6496b8`
**Feature branch:** `feature/restore-staged-artifact-validation`

## 1. Purpose

Slice 5C-2 validates the staged recovery artifact before any rollback capture,
execution authorization, or authoritative promotion is permitted.

The validation service consumes immutable restore plan, preflight,
materialization, and staging evidence. It performs cryptographic byte identity
validation and read-only SQLite structural validation against the isolated
staged artifact.

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
staged artifact integrity validation
    ↓
future application validation and execution authorization
```

## 3. Inputs

The service accepts:

- one immutable `RestorePlan`;
- one ready `RestoreWorkspacePreflight`;
- one successful `RestoreWorkspaceMaterialization`;
- one successful `RestoreArtifactStaging`;
- one explicit timezone-aware UTC validation timestamp;
- and injectable hashing and SQLite validation operators.

## 4. Output

The service returns immutable `RestoreStagedArtifactValidation` evidence
containing:

- schema version;
- plan identifier;
- validation timestamp;
- status;
- stable reason codes;
- source and staged paths;
- source and staged SHA-256 digests;
- source and staged byte counts;
- SQLite quick-check results;
- SQLite integrity-check results;
- whether the database opened read-only;
- and explicit confirmation that the authoritative target was not modified.

## 5. Validation Sequence

The service validates in this order:

1. evidence-chain consistency;
2. staged path identity;
3. source and staged regular-file availability;
4. source and staged byte-count equality;
5. source SHA-256 calculation;
6. staged SHA-256 calculation;
7. digest equality;
8. read-only SQLite open;
9. `PRAGMA quick_check`;
10. `PRAGMA integrity_check`.

A failed check prevents successful validation evidence.

## 6. Cryptographic Validation

SHA-256 is calculated independently for the source and staged artifacts.

Validation succeeds only when:

- both byte counts match;
- both SHA-256 digests match;
- and the digest format is a 64-character lowercase hexadecimal string.

The service does not trust size equality alone.

## 7. SQLite Validation

The staged database is opened through a SQLite read-only URI.

The service must:

- avoid journal creation;
- avoid schema mutation;
- avoid transaction mutation;
- execute `PRAGMA quick_check`;
- execute `PRAGMA integrity_check`;
- and require every returned row from both pragmas to equal `ok`
  case-insensitively after whitespace normalization.

No application-level table or Registry-domain validation is introduced here.

## 8. Safety Boundary

Slice 5C-2 must not:

- modify the source artifact;
- modify the staged artifact;
- modify the authoritative Registry;
- create a rollback artifact;
- acquire execution ownership;
- persist approval;
- promote the staged artifact;
- execute rollback;
- or publish final recovery certification.

## 9. Failure Semantics

Environmental and integrity failures raise
`RestoreStagedArtifactValidationError`.

The error must identify the failed validation category without exposing an
ambiguous success result.

No cleanup mutation is required because the slice is read-only.

## 10. Acceptance Criteria

Slice 5C-2 is accepted when:

- immutable validation evidence exists;
- source and staged SHA-256 digests are calculated independently;
- digest mismatch is rejected;
- size mismatch is rejected;
- SQLite is opened read-only;
- quick-check failure is rejected;
- integrity-check failure is rejected;
- evidence-chain mismatch is rejected;
- the authoritative target remains untouched;
- focused tests pass;
- and the complete quality baseline passes.

## 11. Deferred Work

Deferred capabilities include:

- Registry schema/application validation;
- logical record-count validation;
- rollback artifact capture;
- approval persistence;
- target locking;
- authoritative promotion;
- rollback execution;
- interrupted restore recovery;
- and recovery certification.
