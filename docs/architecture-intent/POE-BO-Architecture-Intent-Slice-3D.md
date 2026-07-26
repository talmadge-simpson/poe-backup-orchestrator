# POE Backup Orchestrator
## Architecture Intent — Slice 3D: Orchestrator Skeleton

**Status:** Approved for implementation  
**Phase:** 3 — End-to-End Orchestration Pipeline  
**Slice:** 3D — Orchestrator Skeleton  

## 1. Purpose

Introduce the first orchestration service that coordinates the normalized service contracts and the execution state machine into a deterministic end-to-end workflow skeleton.

Slice 3D establishes sequencing and state progression. It does not yet implement final failure classification, operational reporting, CLI exposure, production locking, or filesystem integration acceptance.

## 2. Problem Being Solved

The Backup Orchestrator now contains:

- execution-domain models
- an execution state machine
- normalized orchestration-facing service contracts
- tested service implementations for repository validation, Registry acquisition, acquisition validation, and Registry acceptance

These components remain independent. No application service currently owns the complete workflow or guarantees that stages execute in the correct order.

Without an orchestrator:

- callers must sequence services manually
- execution state can diverge from service progress
- intermediate results can be lost or passed incorrectly
- stage skipping cannot be prevented centrally
- end-to-end behavior cannot be unit-tested as one workflow
- future failure mapping and reporting have no stable integration point

Slice 3D creates that integration point.

## 3. Scope

This slice will:

- merge Slice 3C into `main`
- create a dedicated feature branch for Slice 3D
- inspect the actual Slice 3A, 3B, and 3C contracts
- introduce an orchestration service that depends only on normalized protocols
- execute the four service stages in their required order
- drive the execution state machine through valid success-path transitions
- retain typed stage results in an execution outcome or context model
- return an explicit typed result
- add hermetic unit tests for complete successful sequencing
- add tests proving stage order and state-transition order
- add tests proving later stages do not execute when an earlier stage raises
- preserve all existing exception types unchanged
- preserve all existing service behavior unchanged

## 4. Out of Scope

This slice will not:

- classify exceptions into final failure categories
- convert exceptions into failed execution results
- generate operational reports
- write execution evidence to production filesystem locations
- acquire the process or orchestration lock
- add or modify CLI commands
- add retries
- add resumability
- add parallel execution
- add scheduling
- perform production repository integration tests
- suppress or rewrite unexpected exceptions

## 5. Architectural Intent

The orchestrator will be an application service whose only operational dependencies are:

- `RepositoryValidationService`
- `RegistryAcquisitionService`
- `AcquisitionValidationService`
- `RegistryAcceptanceService`
- the execution state machine or a state-machine-compatible collaborator
- a clock only where required by existing execution-domain contracts

The orchestrator must not directly:

- invoke subprocesses
- open SQLite connections
- calculate hashes
- parse manifests
- copy files
- inspect repository directories
- construct service-specific exceptions

Those responsibilities remain within the existing services.

## 6. Required Workflow

The success path must preserve this sequence:

1. initialize execution state
2. validate repository readiness
3. acquire Registry backup
4. validate acquisition evidence
5. accept the validated acquisition into the repository
6. complete execution
7. return a typed successful orchestration result

The exact state names and transition methods must be derived from the implemented Slice 3A and Slice 3B models during inspection. No new duplicate state vocabulary should be introduced.

## 7. Orchestration Result

Slice 3D must return a typed orchestration result or execution context containing the information required by later slices.

At minimum, the successful result must retain:

- execution or job identity already defined by Slice 3A
- final execution state
- repository validation result
- Registry acquisition result
- acquisition validation result
- Registry acceptance result
- state-transition history where already supported
- execution timestamps where already supported

The implementation should reuse existing domain models where possible. A new immutable orchestration result model may be introduced only when no existing model can represent the complete workflow without semantic loss.

## 8. Exception Behavior

Slice 3D owns sequencing, not failure classification.

Therefore:

- service exceptions propagate unchanged
- state-machine exceptions propagate unchanged
- no exception is converted into `None`
- no partial success result is returned after an exception
- no later stage executes after an earlier stage fails
- no final failed-state mapping is introduced here
- cleanup beyond existing service guarantees is out of scope

Slice 3E will own exception-to-failure-category mapping and failed execution-state handling.

## 9. Dependency Injection

The orchestrator must accept normalized service contracts through construction.

This enables:

- deterministic unit tests
- stage-order verification
- failure short-circuit verification
- future replacement of concrete service implementations
- future composition at the CLI or bootstrap layer

The orchestrator must not instantiate concrete filesystem or subprocess services internally.

## 10. Verification Strategy

Unit tests must verify:

- the success path invokes each service exactly once
- services execute in the required order
- each stage receives the correct typed result from the prior stage
- execution states advance in the required order
- the returned result contains all stage outputs
- repository validation failure prevents all later stages
- acquisition failure prevents validation and acceptance
- acquisition validation failure prevents acceptance
- acceptance failure prevents completion
- original exception objects propagate unchanged
- no production filesystem or subprocess operation occurs
- the full existing test suite remains green

## 11. Proposed File Structure

```text
src/poe_backup_orchestrator/
    models/
        orchestration.py          # only if a new result model is required
    services/
        orchestrator.py

tests/unit/
    test_orchestrator.py
```

Final placement may be refined after inspection, but orchestration logic must remain separate from low-level service implementations and CLI code.

## 12. Required Invariants

- orchestration depends only on normalized service protocols
- workflow order is explicit and deterministic
- state progression mirrors actual stage progression
- later stages cannot run after an earlier failure
- existing domain exceptions remain intact
- no service logic is duplicated
- no production side effects occur in unit tests
- orchestration results are typed and immutable where practical
- Ruff and the full test suite remain clean

## 13. Acceptance Criteria

Slice 3D is complete when:

1. Slice 3C is merged into `main`.
2. The actual execution models, state machine, and service contracts have been inspected.
3. The orchestrator skeleton is implemented.
4. The success path coordinates all four normalized services.
5. State transitions align with service progression.
6. A typed orchestration result is returned.
7. Unit tests cover sequencing, result propagation, state progression, and short-circuit behavior.
8. Existing exceptions propagate unchanged.
9. Ruff formatting and static analysis pass.
10. All tests pass.
11. The feature branch is committed and pushed.
12. The working tree is clean.
