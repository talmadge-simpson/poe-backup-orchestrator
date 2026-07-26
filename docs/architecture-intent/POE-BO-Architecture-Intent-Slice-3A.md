# POE Backup Orchestrator
## Architecture Intent — Slice 3A: Orchestration Domain Model

**Status:** Approved for implementation  
**Phase:** 3 — End-to-End Orchestration Pipeline  
**Slice:** 3A — Execution Domain Model  

## 1. Purpose

Establish the stable domain vocabulary required to represent one end-to-end Registry backup execution before orchestration behavior is implemented.

This slice introduces immutable contracts for job identity, execution requests, lifecycle state, execution outcomes, failures, evidence references, and the final structured execution result.

## 2. Problem Being Solved

The existing Backup Orchestrator services perform independently tested operations, but no common model currently represents:

- A complete backup transaction
- Its identity and timestamps
- Its lifecycle state
- Its final outcome
- Evidence produced during execution
- Partial results retained after failure
- A structured failure classification
- A machine-readable result returned to the CLI or future schedulers

Without these contracts, orchestration logic would be forced to coordinate loosely related values and service-specific result types, increasing coupling and making failure handling inconsistent.

## 3. Scope

This slice will introduce:

- `JobId`
- `RegistryBackupRequest`
- `ExecutionState`
- `ExecutionOutcome`
- `FailureCategory`
- `ExecutionFailure`
- `EvidenceType`
- `EvidenceReference`
- `RegistryBackupExecutionResult`
- Clock and job-ID generation protocols, where required for deterministic testing

## 4. Out of Scope

This slice will not:

- Invoke any existing service
- Change repository validation behavior
- Change Registry acquisition behavior
- Change Registry validation behavior
- Change Registry acceptance behavior
- Implement orchestration sequencing
- Implement the execution state machine
- Generate reports
- Add CLI commands
- Access the production repository

## 5. Architectural Intent

The orchestration layer will use:

- A mutable internal execution context while work is in progress
- An immutable public execution result after work completes
- Explicit enums rather than uncontrolled status strings
- Domain-specific component results rather than one oversized generic service result
- Evidence references rather than embedding complete logs or reports
- UTC timestamps for all persisted and returned execution data
- Dependency-injected time and identity generation for deterministic tests

## 6. Required Invariants

### Successful execution result

A successful result must:

- Have a terminal state of `COMPLETED`
- Have no failure object
- Include repository validation, acquisition, validation, and acceptance results
- Include start and completion timestamps
- Have a non-negative duration
- Include an operational report reference once reporting is implemented

### Failed execution result

A failed result must:

- Have a terminal state of `FAILED`
- Include an `ExecutionFailure`
- Preserve results from all successfully completed prior steps
- Leave results for unexecuted steps absent
- Include start and completion timestamps
- Have a non-negative duration

### General invariants

- Public result objects are immutable.
- Job identifiers are non-empty and validated.
- Timestamps are timezone-aware and normalized to UTC.
- Enum values are stable and serialization-safe.
- Evidence references describe artifacts without requiring them to exist during pure unit tests.
- Idempotent acceptance is modeled as a successful outcome, not a failure.

## 7. Compatibility Requirements

The design must remain compatible with:

- Existing service-specific result types
- Existing repository-wide locking
- Future orchestration state-machine implementation
- Future operational reporting
- Future JSON serialization
- Future systemd and scheduled execution
- Future addition of manifest, verification, retention, and restore-validation stages

## 8. Verification Strategy

Unit tests must verify:

- Valid construction of each model
- Rejection of invalid identifiers
- UTC timestamp enforcement
- Negative-duration rejection
- Success-result invariants
- Failure-result invariants
- Immutability
- Stable enum values
- Tuple-based immutable collections
- Serialization-friendly field values
- Idempotent-success representation

All existing tests must continue to pass.

## 9. Acceptance Criteria

Slice 3A is complete when:

1. All domain models are implemented.
2. All new model tests pass.
3. All existing tests pass without modification unless imports require a nonfunctional adjustment.
4. Ruff formatting and static analysis are clean.
5. No existing service behavior changes.
6. The Git working tree is clean.
7. The feature branch is pushed to GitHub.
8. The implementation is reviewed against this Architecture Intent.
