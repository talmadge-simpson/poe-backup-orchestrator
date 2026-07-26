# POE Backup Orchestrator
## Architecture Intent — Slice 3B: Execution State Machine

**Status:** Approved for implementation  
**Phase:** 3 — End-to-End Orchestration Pipeline  
**Slice:** 3B — Execution State Machine  

## 1. Purpose

Introduce a deterministic execution state machine that governs legal lifecycle transitions for one Registry backup orchestration job.

The state machine will define which transitions are permitted, reject invalid transitions, preserve transition history, and provide the orchestration layer with a single authoritative mechanism for lifecycle control.

## 2. Problem Being Solved

Slice 3A established the execution vocabulary, including `ExecutionState`, but it did not define how an execution may move between those states.

Without an explicit state machine:

- Orchestration code could skip required stages.
- Terminal states could be exited.
- Failure handling could assign inconsistent states.
- Tests would need to infer lifecycle rules indirectly.
- Reporting could not rely on a stable transition history.
- Future stages could be inserted without a central lifecycle contract.

The state machine must therefore become the authoritative source for execution progression.

## 3. Scope

This slice will introduce:

- `ExecutionTransition`
- `InvalidExecutionTransitionError`
- `ExecutionStateMachine`
- An explicit transition map
- Transition timestamps
- Immutable transition-history exposure
- Unit tests for every legal and illegal transition

## 4. Out of Scope

This slice will not:

- Invoke repository validation
- Invoke Registry acquisition
- Invoke Registry validation
- Invoke Registry acceptance
- Generate operational reports
- Map service exceptions to failure categories
- Add CLI behavior
- Acquire filesystem locks
- Access the production repository
- Implement orchestration sequencing

## 5. Lifecycle Model

The intended successful lifecycle is:

```text
CREATED
  -> LOCK_ACQUISITION
  -> REPOSITORY_VALIDATION
  -> REGISTRY_ACQUISITION
  -> ACQUISITION_VALIDATION
  -> REGISTRY_ACCEPTANCE
  -> REPORT_GENERATION
  -> COMPLETED
```

Any nonterminal operational state may transition to:

```text
FAILED
```

Terminal states are:

- `COMPLETED`
- `FAILED`

No transition is permitted from a terminal state.

## 6. Architectural Intent

The execution state machine will:

- Start in `ExecutionState.CREATED`.
- Accept an injected UTC clock for deterministic tests.
- Validate each requested transition against an explicit transition map.
- Record every successful transition as an immutable `ExecutionTransition`.
- Reject self-transitions unless explicitly introduced in a future design.
- Reject skipped stages.
- Reject transitions out of terminal states.
- Permit transition to `FAILED` from any nonterminal state.
- Expose current state and immutable transition history.
- Avoid knowledge of service implementations or exceptions.
- Remain reusable by the future orchestrator.

## 7. Required Invariants

### Initialization

- A new state machine starts in `CREATED`.
- Transition history is empty at initialization.

### Successful progression

- Each state may advance only to its defined next state.
- Each accepted transition records:
  - previous state
  - new state
  - UTC timestamp
- Transition timestamps must be timezone-aware and normalized to UTC.

### Failure progression

- Any nonterminal state may transition to `FAILED`.
- `FAILED` is terminal.
- The operational state that failed remains inferable from the final transition record.

### Terminal behavior

- `COMPLETED` cannot transition to another state.
- `FAILED` cannot transition to another state.
- Repeated terminal transitions are rejected.

### General behavior

- Invalid transitions raise `InvalidExecutionTransitionError`.
- Rejected transitions do not mutate current state or history.
- Public transition-history collections are immutable.
- State-machine behavior is deterministic under an injected clock.

## 8. Proposed Public Contract

```python
@dataclass(frozen=True, slots=True)
class ExecutionTransition:
    previous_state: ExecutionState
    new_state: ExecutionState
    occurred_at_utc: datetime
```

```python
class InvalidExecutionTransitionError(Exception):
    previous_state: ExecutionState
    requested_state: ExecutionState
```

```python
class ExecutionStateMachine:
    @property
    def current_state(self) -> ExecutionState: ...

    @property
    def history(self) -> tuple[ExecutionTransition, ...]: ...

    def can_transition_to(self, state: ExecutionState) -> bool: ...

    def transition_to(self, state: ExecutionState) -> ExecutionTransition: ...
```

## 9. Verification Strategy

Unit tests must verify:

- Initial state and empty history
- Every legal successful transition
- Complete successful lifecycle
- Failure transition from every nonterminal state
- Rejection of skipped stages
- Rejection of backward transitions
- Rejection of self-transitions
- Rejection of transitions from `COMPLETED`
- Rejection of transitions from `FAILED`
- State and history remain unchanged after rejection
- UTC enforcement
- Immutable transition records
- Immutable history exposure
- Deterministic clock use

All existing tests must continue to pass.

## 10. Compatibility Requirements

The design must remain compatible with:

- Slice 3A execution models
- Future orchestration context
- Future failure mapping
- Future operational reporting
- Future JSON serialization
- Future insertion of manifest, retention, verification, and restore-test states

The transition map must be centralized so lifecycle expansion does not require distributed conditional logic.

## 11. Acceptance Criteria

Slice 3B is complete when:

1. Slice 3A is merged into `main`.
2. The state machine and transition model are implemented.
3. All legal and illegal transitions are covered by tests.
4. All new tests pass.
5. All existing tests pass.
6. Ruff formatting and static analysis are clean.
7. No existing service behavior changes.
8. The Git working tree is clean.
9. The feature branch is pushed to GitHub.
10. The implementation is reviewed against this Architecture Intent.
