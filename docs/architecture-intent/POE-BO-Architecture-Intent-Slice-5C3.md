# POE Backup Orchestrator Architecture Intent — Slice 5C-3

## Registry Application Validation

**Status:** Implementation baseline
**Phase:** 5C — Isolated Restore Preparation
**Slice:** 5C-3
**Baseline:** `e0eca04`
**Feature branch:** `feature/restore-registry-application-validation`

## 1. Purpose

Slice 5C-3 verifies that a cryptographically and structurally valid staged
SQLite artifact is also a valid POE Registry application database.

The slice validates an explicit Registry contract against the isolated staged
database. It remains read-only and does not authorize restoration.

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
future rollback capture and execution authorization
```

## 3. Contract-Driven Validation

The restore engine does not embed hidden schema assumptions.

A `RegistryApplicationValidationPolicy` explicitly defines:

- policy identifier and version;
- required tables;
- required columns for each table;
- metadata expectations;
- allowed empty-table conditions;
- and declarative row-count invariants.

This allows Registry schema evolution to remain governed and testable.

## 4. Validation Evidence

Successful validation emits immutable
`RestoreRegistryApplicationValidation` evidence containing:

- schema version;
- plan identifier;
- validation timestamp;
- validation status;
- stable reason codes;
- policy identifier and version;
- staged artifact path;
- discovered tables;
- discovered columns;
- metadata observations;
- row-count observations;
- and confirmation that neither the staged artifact nor authoritative target
  was modified.

## 5. Required Checks

The service performs:

1. evidence-chain consistency;
2. staged path identity;
3. read-only SQLite open;
4. required-table presence;
5. required-column presence;
6. metadata-key/value validation;
7. row-count observation;
8. allowed-empty-table validation;
9. declarative row-count invariant validation.

## 6. Metadata Validation

Metadata expectations are represented as table, key-column, value-column,
expected-key, and expected-value contracts.

The validator rejects:

- missing metadata tables;
- missing metadata columns;
- missing required keys;
- and unexpected required values.

## 7. Domain Invariants

Slice 5C-3 supports deterministic row-count invariants such as:

- table must contain at least one row;
- table A row count must be greater than or equal to table B;
- two tables must have equal row counts.

The slice does not introduce arbitrary executable SQL supplied by external
callers.

## 8. Safety Boundary

Slice 5C-3 must not:

- mutate the staged database;
- mutate the source artifact;
- modify the authoritative Registry;
- create rollback evidence;
- capture rollback bytes;
- persist approval;
- acquire execution ownership;
- promote the staged artifact;
- or certify recovery completion.

## 9. Failure Semantics

Application-contract failures raise
`RestoreRegistryApplicationValidationError`.

Failure messages identify the violated contract category. The service never
returns successful evidence after a failed check.

## 10. Acceptance Criteria

Slice 5C-3 is accepted when:

- validation is policy-driven;
- required tables are enforced;
- required columns are enforced;
- required metadata is enforced;
- row-count observations are recorded;
- empty-table policy is enforced;
- declarative count invariants are enforced;
- evidence-chain mismatch is rejected;
- the staged database is opened read-only;
- no authoritative mutation occurs;
- focused tests pass;
- and the complete quality baseline passes.

## 11. Deferred Work

Deferred capabilities include:

- production policy selection by configuration;
- rollback artifact capture;
- restore approval persistence;
- target locking;
- authoritative promotion;
- interrupted execution recovery;
- and final recovery certification.
