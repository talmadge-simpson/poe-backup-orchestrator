# POE Backup Orchestrator Architecture Intent — Slice 4B

## Persistent Runtime State & Recovery Foundation

**Document ID:** POE-BO-Architecture-Intent-Slice-4B
**Status:** Approved for implementation
**Parent phase:** Phase 4 — Production Runtime
**Predecessor:** Slice 4A — Production Runtime Foundation
**Authoritative baseline:** `5d84696 — Merge Slice 4A production runtime foundation`

---

## 1. Purpose

Slice 4B introduces durable runtime-state persistence for one POE Backup Orchestrator execution.

The slice will make an active execution externally observable, preserve its latest lifecycle state across process termination, and provide deterministic startup inspection for identifying an execution that was interrupted before reaching a terminal condition.

The runtime-state mechanism will complement, not replace, the existing execution state machine and operational reporting model.

---

## 2. Problem Statement

The orchestrator currently maintains execution progression in memory through `ExecutionStateMachine`. Final execution results and operational reports are durable, and Registry acceptance publishes governed repository artifacts atomically. However, no authoritative runtime record exists while an execution is in progress.

If the process terminates unexpectedly because of power loss, host restart, process kill, or unhandled failure, the system cannot answer with certainty:

- which execution was active;
- when that execution started;
- which operational state it last entered;
- which process and host owned the execution;
- whether the recorded owner is still active;
- whether the previous execution completed, failed normally, or was interrupted;
- whether startup requires recovery classification before a new run proceeds.

Slice 4B closes this gap using a small, filesystem-native, atomic runtime-state store.

---

## 3. Architectural Context

The system already contains three distinct state-related concerns:

1. **Runtime environment description**
   - Determines where production and development runtime state and logs reside.
   - Established in Slice 4A through `RuntimeDescriptor`.

2. **Execution lifecycle state**
   - Governs legal orchestration transitions.
   - Established in Phase 3 through `ExecutionState` and `ExecutionStateMachine`.

3. **Durable operational and repository evidence**
   - Includes final reports, manifests, accepted Registry backup artifacts, and acceptance evidence.
   - Published atomically by existing services.

Slice 4B introduces a fourth concern:

4. **Durable runtime execution state**
   - Describes the current or most recent process-level execution condition.
   - Persists beneath the runtime `state_root`.
   - Supports interruption detection and operational inspection.

These concerns must remain separate.

---

## 4. Scope

Slice 4B will implement:

- an immutable runtime-state model;
- a coarse-grained runtime execution status;
- schema-versioned JSON serialization and deserialization;
- an atomic filesystem-backed runtime-state store;
- deterministic startup inspection;
- interruption classification for an abandoned `RUNNING` record;
- process-ownership metadata;
- CLI visibility into the current persisted runtime state;
- unit tests covering model validation, persistence, corruption handling, ownership checks, and recovery classification;
- architecture documentation.

---

## 5. Out of Scope

Slice 4B will not implement:

- restart from an execution checkpoint;
- automatic replay of partially completed work;
- event sourcing;
- an append-only execution journal;
- database-backed runtime state;
- distributed coordination;
- cross-host leader election;
- systemd service or timer installation;
- log rotation or structured JSON logging;
- metrics aggregation;
- retention policy for historical runtime-state files;
- mutation of accepted Registry backup artifacts;
- replacement of the existing execution state machine;
- replacement of final operational reports.

A later slice may add execution-history retention or richer operational recovery workflows if justified by observed requirements.

---

## 6. Design Principles

The implementation must satisfy the following principles:

### 6.1 Single authoritative current-state record

Each runtime environment will have one authoritative current-state file:

```text
<state_root>/runtime-state.json
```

The file represents the active or most recently classified execution.

### 6.2 Atomic publication

Readers must never observe partially written JSON.

Persistence will use:

1. a temporary file in the same directory;
2. complete UTF-8 JSON write;
3. file flush and `fsync`;
4. atomic `os.replace`;
5. parent-directory `fsync` where supported by the existing project pattern.

### 6.3 Schema versioning

The persisted record will include a schema version. Unsupported versions must fail explicitly rather than being silently interpreted.

Initial version:

```text
schema_version = 1
```

### 6.4 Separation of state dimensions

`ExecutionState` will continue to identify the detailed orchestration stage.

A separate runtime status will identify the process-level condition:

- `RUNNING`
- `COMPLETED`
- `FAILED`
- `INTERRUPTED`

The runtime status must not duplicate stage names.

### 6.5 Immutable domain model

The runtime-state model will be immutable and validated at construction time.

### 6.6 Deterministic inspection

Process-liveness checks, host identity, process ID, and clock behavior must be injectable or isolated behind narrow collaborators so tests remain deterministic.

### 6.7 Conservative recovery semantics

A persisted `RUNNING` record will be classified as interrupted only when the system can establish that its owning process is not active on the recorded host.

Ambiguous ownership must not be silently treated as safe.

---

## 7. Proposed Domain Model

### 7.1 RuntimeExecutionStatus

```python
class RuntimeExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
```

### 7.2 RuntimeState

Proposed fields:

```python
@dataclass(frozen=True, slots=True)
class RuntimeState:
    schema_version: int
    run_id: str
    status: RuntimeExecutionStatus
    execution_state: ExecutionState
    started_at_utc: datetime
    updated_at_utc: datetime
    pid: int
    hostname: str
    environment: RuntimeEnvironment
```

Optional failure or completion details will not be duplicated from `ExecutionResult` in this slice. The final operational report remains authoritative for detailed outcome information.

### 7.3 Validation Rules

The model must enforce:

- `schema_version == 1`;
- non-empty `run_id`;
- positive `pid`;
- non-empty `hostname`;
- timezone-aware UTC timestamps;
- `updated_at_utc >= started_at_utc`;
- `RUNNING` cannot use terminal execution states;
- `COMPLETED` requires `ExecutionState.COMPLETED`;
- `FAILED` requires `ExecutionState.FAILED`;
- `INTERRUPTED` must preserve the last nonterminal operational state rather than replacing it with `FAILED`.

---

## 8. Persistence Contract

A runtime-state store will expose a narrow interface conceptually equivalent to:

```python
class RuntimeStateStore:
    def load(self) -> RuntimeState | None: ...
    def save(self, state: RuntimeState) -> None: ...
    def clear(self) -> None: ...
```

Expected behavior:

- `load()` returns `None` when no state file exists;
- malformed JSON raises a precise runtime-state corruption error;
- unsupported schema versions raise a precise version error;
- `save()` atomically replaces the current state;
- `clear()` is idempotent;
- the store does not infer recovery state itself.

The store path will derive from `RuntimeDescriptor.state_root`.

---

## 9. Recovery Inspection

A dedicated recovery inspector will evaluate the persisted state.

Conceptual outcomes:

- `NO_STATE`
- `TERMINAL_STATE`
- `ACTIVE_EXECUTION`
- `INTERRUPTED_EXECUTION`
- `AMBIGUOUS_OWNERSHIP`

Inspection rules:

1. No state file:
   - no recovery condition exists.

2. Terminal status (`COMPLETED`, `FAILED`, `INTERRUPTED`):
   - state is observable but does not indicate an active owner.

3. `RUNNING`, same hostname, PID active:
   - execution is active;
   - a second run must not proceed.

4. `RUNNING`, same hostname, PID absent:
   - classify as interrupted;
   - atomically persist status `INTERRUPTED`;
   - preserve the last detailed `ExecutionState`.

5. `RUNNING`, different hostname:
   - treat ownership as ambiguous;
   - do not automatically overwrite the record.

This conservative behavior avoids falsely declaring a remote or migrated execution dead.

---

## 10. Integration Strategy

Slice 4B will integrate with orchestration incrementally.

### 10.1 Execution start

Before operational work begins:

- create the runtime-state record;
- set status to `RUNNING`;
- set execution state to `CREATED`;
- persist run ID, PID, hostname, environment, and timestamps.

### 10.2 State transitions

After each accepted `ExecutionStateMachine` transition:

- update `execution_state`;
- update `updated_at_utc`;
- persist atomically.

The state machine remains authoritative for transition validity.

### 10.3 Successful completion

After transition to `COMPLETED`:

- persist status `COMPLETED`;
- persist execution state `COMPLETED`.

### 10.4 Controlled failure

After transition to `FAILED`:

- persist status `FAILED`;
- persist execution state `FAILED`.

Detailed failure information remains in `ExecutionResult` and the operational report.

### 10.5 Unexpected termination

No special shutdown hook is required to guarantee interruption detection. If the process terminates before a terminal state is saved, the persisted `RUNNING` record remains and is evaluated during the next startup inspection.

---

## 11. Locking and Concurrency

Existing advisory file-locking primitives will be reused where appropriate.

The runtime-state design must distinguish:

- **execution ownership**, represented by the runtime-state record;
- **kernel-enforced mutual exclusion**, represented by an advisory lock.

A persistent lock file is not itself proof of active ownership. Kernel lock state remains authoritative for lock acquisition.

The runtime-state store must not introduce a second contradictory lock semantics. Startup inspection will provide diagnostics and recovery classification; the existing orchestration locking mechanism will continue to enforce concurrency.

---

## 12. CLI Behavior

Slice 4B will add an operational command conceptually named:

```text
poe-backup-orchestrator runtime-state
```

The command should report:

- state file path;
- schema version;
- run ID;
- runtime status;
- detailed execution state;
- start and update timestamps;
- PID;
- hostname;
- runtime environment;
- recovery inspection outcome.

Machine-readable JSON output may be added if the current CLI conventions already support it. Otherwise, human-readable output is sufficient for this slice.

The command must be read-only unless an explicit future recovery command is approved.

---

## 13. Error Model

Precise exceptions should distinguish at minimum:

- runtime-state persistence failure;
- runtime-state corruption;
- unsupported runtime-state schema version;
- invalid persisted runtime-state content;
- runtime-state ownership ambiguity.

Exceptions should be added to the existing exception hierarchy rather than creating unrelated local exception types.

---

## 14. File Layout

Expected additions or modifications include:

```text
src/poe_backup_orchestrator/models/runtime.py
src/poe_backup_orchestrator/services/runtime_state_store.py
src/poe_backup_orchestrator/services/runtime_recovery.py
src/poe_backup_orchestrator/services/orchestrator.py
src/poe_backup_orchestrator/services/run_service.py
src/poe_backup_orchestrator/cli.py
src/poe_backup_orchestrator/exceptions.py
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/__init__.py

tests/unit/test_runtime_state_models.py
tests/unit/test_runtime_state_store.py
tests/unit/test_runtime_recovery.py
tests/unit/test_runtime_state_integration.py
tests/unit/test_cli.py
```

Exact placement may be adjusted during implementation to remain consistent with the established package structure.

---

## 15. Test Strategy

Tests must cover:

### Model validation

- valid running state;
- valid completed state;
- valid failed state;
- valid interrupted state;
- invalid schema version;
- blank run ID or hostname;
- nonpositive PID;
- non-UTC timestamps;
- reversed timestamps;
- inconsistent status and execution-state combinations.

### Serialization and persistence

- deterministic JSON structure;
- round-trip serialization;
- no-file behavior;
- atomic replacement;
- overwrite of prior state;
- idempotent clear;
- malformed JSON;
- unsupported schema;
- invalid field content;
- no temporary-file residue after success;
- cleanup behavior after persistence failure.

### Recovery inspection

- no state;
- terminal state;
- active same-host process;
- dead same-host process;
- different-host ambiguity;
- interrupted classification persistence;
- preservation of last operational state.

### Integration

- state created before orchestration stages execute;
- persisted after each legal transition;
- successful terminal persistence;
- controlled-failure terminal persistence;
- existing execution result behavior remains unchanged;
- existing reports remain authoritative;
- no regression in current orchestration sequencing.

### CLI

- no persisted state;
- active state;
- terminal state;
- interrupted state;
- corrupted state;
- stable exit-code behavior.

---

## 16. Acceptance Criteria

Slice 4B is complete when:

1. Runtime state is represented by an immutable, schema-versioned model.
2. The authoritative state file is stored beneath the active runtime `state_root`.
3. State publication is atomic and durable.
4. Existing execution-state transitions remain authoritative.
5. Active process ownership is recorded.
6. Startup inspection distinguishes active, terminal, interrupted, and ambiguous conditions.
7. A dead same-host owner can be classified as interrupted.
8. CLI inspection exposes the persisted state and recovery outcome.
9. Corrupt or unsupported state fails explicitly.
10. Development and production runtime roots both function.
11. Existing Phase 1–4A behavior remains unchanged.
12. Ruff formatting and lint checks pass.
13. The full test suite passes.
14. `git diff --check` passes.
15. Implementation evidence is captured.
16. The feature branch is merged into `main` with a clean synchronized working tree.

---

## 17. Deferred Decisions

The following decisions are intentionally deferred:

- whether to retain historical runtime-state records;
- whether to add a privileged operator command to acknowledge or clear interrupted state;
- whether systemd service startup should perform recovery classification automatically;
- whether interruption should generate a dedicated operational report;
- whether process identity should later include Linux boot ID or process start time to mitigate PID reuse;
- whether a future state journal is justified.

PID reuse is a known limitation of the initial model. The implementation should be structured so a stronger process identity can be added without changing the overall persistence contract.

---

## 18. Implementation Sequence

Recommended implementation order:

1. Create the feature branch.
2. Add runtime-state exceptions.
3. Implement runtime status and immutable state model.
4. Implement serialization and deserialization.
5. Implement atomic state store.
6. Implement process-liveness abstraction and recovery inspector.
7. Integrate lifecycle persistence with orchestration.
8. Add CLI inspection.
9. Add and expand unit tests.
10. Run full validation.
11. Capture implementation evidence.
12. Review staged changes.
13. Commit, push, merge, and verify `main`.

---

## 19. Architecture Decision

Slice 4B will implement a small, filesystem-native **Persistent Runtime State & Recovery Foundation**.

It will preserve the existing separation between:

- runtime environment;
- execution lifecycle;
- repository evidence;
- operational reporting;
- process-level runtime state.

The design favors explicit state, atomic persistence, deterministic recovery inspection, and conservative ownership semantics over generalized workflow checkpointing or distributed coordination.
