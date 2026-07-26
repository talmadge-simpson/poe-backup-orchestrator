# POE Backup Orchestrator
## Architecture Intent — Slice 3E: Failure Mapping

**Status:** Approved for implementation  
**Phase:** 3 — End-to-End Orchestration Pipeline  
**Slice:** 3E — Failure Mapping  

## 1. Purpose

Introduce deterministic mapping from operational exceptions to typed execution failures and failed orchestration results.

Slice 3E converts expected operational failures into explicit `ExecutionFailure` and `RegistryBackupExecutionResult` objects while preserving programmer defects and unknown internal errors as visible exceptions unless the implemented domain contract explicitly requires otherwise.

## 2. Problem Being Solved

Slice 3D established successful end-to-end sequencing and intentionally propagates all exceptions unchanged.

That behavior is correct for an orchestration skeleton, but it is incomplete for an operational system. Callers currently cannot rely on a typed result when an expected repository, acquisition, validation, or acceptance failure occurs.

Without failure mapping:

- operational failures cannot be reported consistently
- exit codes cannot be derived deterministically
- retryability cannot be represented
- the failed operational stage is not preserved in a returned result
- completed stage evidence may be lost to the caller
- CLI and reporting layers would need exception-specific logic
- expected environmental failures are indistinguishable from programming defects

Slice 3E establishes one authoritative failure-classification boundary.

## 3. Scope

This slice will:

- merge Slice 3D into `main`
- create a dedicated Slice 3E feature branch
- inspect all current exception classes and execution-domain failure models
- define an explicit mapping from known operational exceptions to:
  - `FailureCategory`
  - failed operational state
  - retryability
  - exit code
  - stable error type and message
- update orchestration so expected operational exceptions produce typed failed execution results
- transition the execution state machine to `FAILED`
- preserve completed stage results in failed execution results
- retain the original operational stage in `ExecutionFailure.failed_state`
- preserve successful behavior unchanged
- add hermetic tests for every supported mapping
- add tests proving unknown exceptions remain visible unless explicitly classified
- keep failure mapping independent of CLI and report formatting

## 4. Out of Scope

This slice will not:

- generate human-readable operational reports
- write JSON reports to disk
- add CLI commands or exit handling
- add retry execution
- add rollback or compensating actions
- acquire production orchestration locks
- add filesystem integration tests
- alter existing low-level exception behavior
- suppress unknown programmer errors
- implement alerting or notification

## 5. Architectural Intent

Failure classification must be centralized and deterministic.

The orchestration layer must not contain scattered `except` blocks with ad hoc result construction. A dedicated mapper or mapping function will own translation from known exception types to `ExecutionFailure`.

The mapping boundary must:

- use the concrete exception type as the primary classifier
- preserve the state active when the exception occurred
- produce stable exit codes
- produce explicit retryability
- preserve the original exception message
- preserve the original exception type name
- avoid parsing message text when a concrete exception type exists
- avoid converting unknown exceptions into misleading operational categories

## 6. Failed Execution Result

A mapped operational failure must produce a `RegistryBackupExecutionResult` with:

- the same job identity used by the execution
- `ExecutionOutcome.FAILED`
- the original execution start timestamp
- a completion timestamp
- a nonnegative duration
- `ExecutionState.FAILED` as the terminal state
- an `ExecutionFailure`
- every successfully completed prior stage result
- no result for the failed or unexecuted stage
- no fabricated success evidence

The state machine must transition from the active operational state to `FAILED` before the result is created.

## 7. Failure State Semantics

`ExecutionFailure.failed_state` must identify the operational state in which the exception occurred, not the terminal `FAILED` state.

Examples:

- repository validation exception → `REPOSITORY_VALIDATION`
- Registry acquisition exception → `REGISTRY_ACQUISITION`
- acquisition validation exception → `ACQUISITION_VALIDATION`
- Registry acceptance exception → `REGISTRY_ACCEPTANCE`

Failures in orchestration-only stages such as lock acquisition or report generation will be mapped only if corresponding implemented exceptions already exist and are in scope.

## 8. Unknown Exceptions

Unknown exceptions must not be silently reclassified as expected operational failures.

Unless the current domain specification explicitly defines a safe internal-failure mapping:

- unexpected exceptions propagate unchanged
- `KeyboardInterrupt`, `SystemExit`, and other `BaseException` subclasses are never captured
- programming defects remain visible
- tests must prove unknown exceptions are not swallowed

A later application boundary may choose to convert unknown failures into an internal exit code, but Slice 3E must not obscure defects without an explicit approved contract.

## 9. Compatibility Requirements

The implementation must remain compatible with:

- Slice 3A execution models
- Slice 3B state machine rules
- Slice 3C normalized service contracts
- Slice 3D success-path orchestration
- future operational reporting
- future CLI exit-code handling
- future integration tests
- existing service exception classes

No existing public service function may be removed.

## 10. Verification Strategy

Unit tests must verify:

- every known repository exception maps correctly
- every known acquisition exception maps correctly
- every known validation exception maps correctly
- every known acceptance exception maps correctly
- the failed state reflects the operational stage
- the state machine terminates in `FAILED`
- prior completed results are preserved
- failed and later stage results remain absent
- exit codes are stable and positive
- retryability is explicit
- error type and message are preserved
- the success path remains unchanged
- unknown exceptions propagate unchanged
- no production filesystem or subprocess behavior occurs
- all existing tests remain green

## 11. Proposed File Structure

```text
src/poe_backup_orchestrator/
    services/
        failure_mapping.py
        orchestrator.py

tests/unit/
    test_failure_mapping.py
    test_orchestrator.py
```

The exact structure may be refined after inspection, but mapping policy must remain separate from low-level services and presentation concerns.

## 12. Required Invariants

- one authoritative mapping exists for each classified exception
- operational state is captured before transition to `FAILED`
- only known operational exceptions are converted
- successful prior results are retained
- failed results satisfy all execution-domain invariants
- original exception type and message remain represented
- unknown exceptions remain visible
- no reporting or CLI concerns leak into mapping
- Ruff and the complete test suite remain clean

## 13. Acceptance Criteria

Slice 3E is complete when:

1. Slice 3D is merged into `main`.
2. Existing exception and failure-model contracts have been inspected.
3. A centralized failure mapper is implemented.
4. Known operational exceptions produce typed failed results.
5. The state machine transitions to `FAILED`.
6. Completed prior-stage results are preserved.
7. Unknown exceptions propagate unchanged.
8. Mapping tests cover every supported exception type.
9. Orchestrator tests cover failed results at each operational stage.
10. Successful behavior remains unchanged.
11. Ruff formatting and static analysis pass.
12. All tests pass.
13. The feature branch is committed and pushed.
14. The working tree is clean.
