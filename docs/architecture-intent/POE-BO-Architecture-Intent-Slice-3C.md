# POE Backup Orchestrator
## Architecture Intent — Slice 3C: Service Contract Normalization

**Status:** Approved for implementation  
**Phase:** 3 — End-to-End Orchestration Pipeline  
**Slice:** 3C — Service Contract Normalization  

## 1. Purpose

Normalize the public contracts of the existing Backup Orchestrator services so the future orchestration layer can invoke each stage through predictable, explicit, and type-stable interfaces.

Slice 3C does not create the orchestrator. It prepares the service boundary that the orchestrator will consume.

## 2. Problem Being Solved

The existing service implementations were developed incrementally across earlier slices. They correctly perform their individual responsibilities, but their invocation patterns, inputs, return values, and exception behavior were not originally designed as one coordinated orchestration API.

Without normalization:

- The orchestrator would need service-specific conditional logic.
- Input dependencies could be passed inconsistently.
- Return values could expose implementation details.
- Failure handling would be coupled to individual service internals.
- Tests would need to mock unrelated filesystem and subprocess behavior.
- Future service replacement would require changes throughout the orchestrator.
- Operational reporting could not rely on consistent stage outcomes.

Slice 3C establishes a deliberate application-service boundary before orchestration sequencing begins.

## 3. Scope

This slice will:

- Inventory the current public contracts for:
  - repository validation
  - Registry acquisition
  - acquisition validation
  - Registry acceptance
- Introduce explicit callable service protocols for orchestration dependencies.
- Normalize service invocation around typed request and result contracts.
- Preserve existing service behavior.
- Add adapters where existing functions do not directly satisfy the normalized contract.
- Define orchestration-facing exception boundaries without implementing final failure classification.
- Export the normalized contracts through the services package.
- Add unit tests proving compatibility and substitutability.

## 4. Out of Scope

This slice will not:

- Implement end-to-end orchestration sequencing.
- Instantiate the execution state machine within an orchestrator.
- Acquire the orchestration lock.
- Generate operational reports.
- Map exceptions to final failure categories.
- Add new CLI commands.
- Change repository layouts.
- Change Registry backup semantics.
- Change Registry validation semantics.
- Change Registry acceptance semantics.
- Access the production backup repository during unit tests.

## 5. Architectural Intent

The orchestration layer must depend on stable service abstractions rather than concrete implementation details.

The normalized boundary will use structural typing through `Protocol` contracts. Each protocol will represent one orchestration stage and expose a single callable operation.

The expected orchestration dependencies are:

```python
class RepositoryValidationService(Protocol):
    def validate(self) -> RepositoryValidationResult: ...


class RegistryAcquisitionService(Protocol):
    def acquire(self, job_id: JobId) -> RegistryBackupExecutionResult: ...


class AcquisitionValidationService(Protocol):
    def validate(
        self,
        acquisition: RegistryBackupExecutionResult,
    ) -> RegistryAcquisitionValidationResult: ...


class RegistryAcceptanceService(Protocol):
    def accept(
        self,
        acquisition: RegistryBackupExecutionResult,
        validation: RegistryAcquisitionValidationResult,
        job_id: JobId,
    ) -> RegistryIngestionResult: ...
```

Exact argument names may be refined during implementation when required to preserve the existing domain terminology, but the following principles are mandatory:

- one protocol per orchestration stage
- one public operation per protocol
- explicit typed inputs
- explicit typed result
- no unstructured dictionaries at the orchestration boundary
- no direct subprocess invocation by the future orchestrator
- no direct filesystem mutation by the future orchestrator
- no dependency on concrete implementation classes

## 6. Adapter Strategy

Existing functions remain authoritative for current behavior.

Where an existing function already satisfies the normalized contract, it may be exposed directly through a thin callable adapter.

Where an existing function requires additional configuration or collaborators, an adapter object will bind those dependencies during construction and expose a normalized method to the orchestrator.

Adapters must:

- be narrow and deterministic
- delegate rather than duplicate service logic
- avoid hidden global state
- preserve original exceptions
- remain independently unit-testable
- expose only orchestration-relevant inputs

## 7. Result Contract Requirements

All orchestration-facing services must return explicit domain models.

The implementation must reuse existing models where they already represent the required result. New models may be introduced only when the existing service output cannot be represented without loss of meaning.

Result contracts must:

- be type-stable
- avoid optional fields that are meaningless for the stage
- preserve evidence references where available
- preserve job identity where applicable
- remain suitable for later operational reporting
- remain suitable for later JSON serialization
- avoid embedding open file handles, subprocess objects, or mutable filesystem state

## 8. Exception Boundary

Slice 3C will not implement final failure mapping, but it must make exception ownership clear.

Rules:

- adapters do not swallow service exceptions
- adapters do not convert failures into `None`
- adapters do not return success flags alongside partial results
- existing domain exceptions remain intact
- unexpected programmer errors remain visible
- the future orchestrator will own exception-to-failure-category mapping in Slice 3E

If a normalization-specific configuration error is required, it must use a dedicated exception with a clear message and no loss of the original cause.

## 9. Compatibility Requirements

The normalized contracts must remain compatible with:

- Slice 3A execution-domain models
- Slice 3B execution state machine
- existing repository-validation service behavior
- existing Registry acquisition behavior
- existing acquisition-validation behavior
- existing Registry-acceptance behavior
- future orchestration dependency injection
- future failure mapping
- future operational reporting
- future CLI integration

No existing public function may be removed in this slice.

## 10. Verification Strategy

Unit tests must verify:

- each protocol is runtime-checkable when appropriate
- each adapter delegates to the intended existing service
- constructor-bound dependencies are forwarded correctly
- typed inputs are preserved
- typed results are returned unchanged
- existing domain exceptions propagate unchanged
- adapters do not add filesystem or subprocess behavior
- fake implementations can satisfy each protocol
- normalized contracts can be imported from the public services package
- all existing tests continue to pass

Tests must not access the production repository.

## 11. Proposed File Structure

```text
src/poe_backup_orchestrator/services/
    contracts.py
    adapters.py
```

The final file structure may be split further if required for clarity, but contracts and concrete adapters must remain logically separate.

## 12. Required Invariants

- The orchestration layer will be able to depend only on normalized protocols.
- Existing service implementations remain independently callable.
- No service implementation is duplicated.
- No orchestration sequencing is introduced.
- No stage result is represented by an untyped mapping.
- No adapter suppresses or rewrites an existing domain failure.
- Unit tests remain hermetic.
- Ruff and the full test suite remain clean.

## 13. Acceptance Criteria

Slice 3C is complete when:

1. Slice 3B is merged into `main`.
2. Current service contracts have been reviewed and documented.
3. Orchestration-facing protocols are implemented.
4. Existing service implementations are exposed through thin adapters.
5. Public exports are updated coherently.
6. Compatibility tests cover each normalized service boundary.
7. Existing behavior remains unchanged.
8. Ruff formatting and static analysis pass.
9. All tests pass.
10. The Git working tree is clean.
11. The feature branch is pushed to GitHub.
12. The implementation is reviewed against this Architecture Intent.
