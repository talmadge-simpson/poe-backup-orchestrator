# POE Backup Orchestrator Architecture Intent — Slice 4D

## Runtime Operational Acceptance & Architecture Certification

**Document ID:** POE-BO-Architecture-Intent-Slice-4D
**Status:** Approved for implementation
**Parent phase:** Phase 4 — Production Runtime
**Predecessors:** Slice 4A — Production Runtime Foundation; Slice 4B — Persistent Runtime State & Recovery Foundation; Slice 4C — Runtime Composition Consolidation
**Authoritative baseline:** `74959d7 — Merge Slice 4C.2 runtime inspection composition`

---

## 1. Purpose

Slice 4D formally certifies the Phase 4 production-runtime architecture.

The slice does not introduce new runtime behavior. It consolidates the implemented runtime model into an authoritative architecture record, defines the operational acceptance scenarios for that model, establishes traceability from Phase 4 objectives to implementation and tests, and records any residual technical debt before Phase 5 begins.

Phase 4D is therefore a verification, documentation, and certification slice.

---

## 2. Scope

Slice 4D will produce four governed deliverables:

1. **Runtime Architecture Baseline**
   - runtime discovery
   - bootstrap and validation
   - runtime ownership
   - persistent runtime state
   - lifecycle coordination
   - recovery inspection
   - production composition
   - CLI delegation

2. **Runtime Operational Acceptance Specification**
   - no prior runtime state
   - completed prior state
   - failed prior state
   - interrupted prior state
   - active same-host ownership
   - ambiguous cross-host ownership
   - dead same-host owner recovery
   - runtime-state inspection
   - runtime-aware orchestration startup and termination

3. **Runtime Sequence and Responsibility Diagrams**
   - execution composition path
   - inspection composition path
   - lifecycle persistence path
   - recovery decision path

4. **Phase 4 Certification Record**
   - objective-to-implementation traceability
   - objective-to-test traceability
   - acceptance checklist
   - known limitations
   - deferred capabilities
   - Phase 5 readiness decision

---

## 3. Non-Goals

Slice 4D will not:

- add new runtime domain models
- change runtime-state schema version
- change recovery semantics
- change lifecycle transition behavior
- change CLI exit codes
- introduce systemd services or timers
- introduce deployment packaging
- introduce log rotation
- introduce retention or restore-test execution
- alter repository locking or Registry acceptance semantics
- add abstractions solely for documentation convenience

Any production-code change discovered during certification must be treated as a separately reviewed corrective slice rather than silently included in Phase 4D.

---

## 4. Certified Runtime Architecture

### 4.1 Runtime Discovery and Bootstrap

Runtime discovery determines the authoritative configuration, state root, log root, service identity, and environment.

Bootstrap validates that the selected runtime is internally consistent and operationally usable before exposing application context.

The configuration remains authoritative for application paths. Runtime discovery remains authoritative for environment-specific operational roots and identity.

### 4.2 Runtime Ownership

One running process owns one active runtime execution.

Ownership is represented by:

- run identifier
- runtime execution status
- execution state
- start and update timestamps
- process identifier
- hostname
- runtime environment

The persisted runtime-state record is the authoritative observation point for runtime ownership.

### 4.3 Persistent Runtime State

`RuntimeStateStore` owns durable serialization and replacement of the runtime-state record.

The store must preserve these properties:

- deterministic UTF-8 JSON
- explicit schema validation
- UTC timestamp validation
- atomic replacement
- filesystem synchronization
- controlled corruption errors
- controlled persistence errors
- idempotent clear behavior

The authoritative runtime-state filename remains centralized and stable.

### 4.4 Recovery Inspection

`RuntimeRecoveryInspector` interprets persisted state without duplicating lifecycle logic.

Recovery outcomes distinguish:

- no state
- terminal state
- interrupted execution
- active execution
- ambiguous ownership

A dead process on the current host may be reclassified and persisted as interrupted.

A live process on the current host remains active.

A running state owned by another host remains ambiguous and must not be mutated automatically.

### 4.5 Runtime Lifecycle Coordination

`RuntimeLifecycleCoordinator` owns runtime-state publication during orchestration.

It:

1. inspects prior state before work begins
2. blocks unsafe ownership
3. publishes the new running execution
4. persists accepted execution-state transitions
5. persists terminal completion
6. persists terminal failure

Runtime lifecycle state complements the orchestration state machine; it does not replace it.

### 4.6 Production Composition

Production dependency construction is centralized behind two composition boundaries:

```text
build_registry_backup_run_service(...)
    ├── RuntimeStateStore
    ├── RuntimeRecoveryInspector
    ├── RuntimeLifecycleCoordinator
    └── RegistryBackupOrchestrator
```

```text
build_runtime_recovery_inspector(...)
    ├── RuntimeStateStore
    ├── SystemHostIdentity
    ├── SystemProcessLiveness
    ├── SystemUtcClock
    └── RuntimeRecoveryInspector
```

The CLI may request these composed services but must not construct their implementation dependencies directly.

### 4.7 CLI Responsibility

The CLI owns:

- argument parsing
- bootstrap invocation
- composition-factory invocation
- request construction
- result rendering
- stable process exit behavior

The CLI does not own:

- runtime-state persistence
- runtime ownership decisions
- process-liveness semantics
- host-identity semantics
- runtime lifecycle transitions
- orchestration internals

---

## 5. Runtime Execution Sequence

```text
Operator
   |
   v
CLI run / acceptance-run
   |
   v
bootstrap_application()
   |
   v
ApplicationContext + RuntimeDescriptor
   |
   v
build_registry_backup_run_service()
   |
   +--> RuntimeStateStore
   +--> RuntimeRecoveryInspector
   +--> RuntimeLifecycleCoordinator
   +--> RegistryBackupOrchestrator
   |
   v
RuntimeLifecycleCoordinator.start()
   |
   +--> inspect prior runtime state
   +--> reject unsafe ownership
   +--> persist CREATED / RUNNING
   |
   v
RegistryBackupOrchestrator.execute()
   |
   +--> persist accepted state transitions
   +--> coordinate operational services
   |
   v
persist COMPLETED or FAILED
   |
   v
publish operational result
```

---

## 6. Runtime Inspection Sequence

```text
Operator
   |
   v
CLI runtime-state
   |
   v
bootstrap_application()
   |
   v
build_runtime_recovery_inspector()
   |
   +--> RuntimeStateStore
   +--> SystemHostIdentity
   +--> SystemProcessLiveness
   +--> SystemUtcClock
   |
   v
RuntimeRecoveryInspector.inspect()
   |
   +--> no state
   +--> terminal state
   +--> active execution
   +--> interrupted execution
   +--> ambiguous ownership
   |
   v
CLI renders authoritative runtime state
```

---

## 7. Recovery Decision Model

```text
Persisted state absent?
    yes -> NO_STATE
    no
     |
     v
Persisted state terminal?
    yes -> TERMINAL_STATE
    no
     |
     v
Owner hostname equals current hostname?
    no -> AMBIGUOUS_OWNERSHIP
    yes
     |
     v
Owner PID alive?
    yes -> ACTIVE_EXECUTION
    no  -> persist INTERRUPTED
           return INTERRUPTED_EXECUTION
```

Reinspection of an already interrupted state is terminal observation, not repeated mutation.

---

## 8. Operational Acceptance Scenarios

Phase 4 runtime acceptance must demonstrate:

1. **No-state startup**
   - startup is permitted
   - a new running state is published

2. **Prior completed state**
   - startup is permitted
   - prior terminal evidence remains observable
   - new execution ownership may be established

3. **Prior failed state**
   - startup is permitted
   - prior failure remains observable
   - new execution ownership may be established

4. **Prior interrupted state**
   - startup is permitted
   - interrupted history remains observable
   - new execution ownership may be established

5. **Same-host live owner**
   - startup is rejected
   - existing state is not mutated

6. **Different-host running owner**
   - startup is rejected as ambiguous
   - existing state is not mutated

7. **Same-host dead owner**
   - prior state is persisted as interrupted
   - recovery outcome is interrupted execution
   - subsequent startup may establish new ownership

8. **Successful orchestration**
   - runtime state progresses with execution
   - final state is completed

9. **Controlled orchestration failure**
   - runtime state records the failed terminal condition
   - operational failure evidence remains available

10. **Runtime-state inspection**
    - the CLI reports recovery outcome
    - the CLI reports whether state changed
    - persisted ownership and execution fields are rendered

11. **Composition integrity**
    - runtime execution composition is centralized
    - runtime inspection composition is centralized
    - the CLI contains no direct runtime implementation construction

12. **Regression safety**
    - all automated tests pass
    - Ruff formatting and linting pass
    - Git whitespace validation passes

---

## 9. Traceability Baseline

The certification record must trace at minimum to:

### Runtime discovery and validation

- `src/poe_backup_orchestrator/services/runtime_discovery.py`
- `src/poe_backup_orchestrator/services/runtime_validation.py`
- `src/poe_backup_orchestrator/services/production_bootstrap.py`
- `tests/unit/test_runtime_discovery.py`
- `tests/unit/test_runtime_validation.py`
- `tests/unit/test_production_bootstrap.py`

### Runtime persistence and recovery

- `src/poe_backup_orchestrator/models/runtime.py`
- `src/poe_backup_orchestrator/services/runtime_state_store.py`
- `src/poe_backup_orchestrator/services/runtime_recovery.py`
- `tests/unit/test_runtime_state_models.py`
- `tests/unit/test_runtime_state_store.py`
- `tests/unit/test_runtime_recovery.py`

### Runtime lifecycle and orchestration

- `src/poe_backup_orchestrator/services/runtime_lifecycle.py`
- `src/poe_backup_orchestrator/services/orchestrator.py`
- `src/poe_backup_orchestrator/services/run_service.py`
- `tests/unit/test_runtime_lifecycle.py`
- `tests/unit/test_orchestrator.py`
- `tests/unit/test_run_service.py`

### Runtime composition and CLI

- `src/poe_backup_orchestrator/services/runtime_composition.py`
- `src/poe_backup_orchestrator/cli.py`
- `tests/unit/test_runtime_composition.py`
- `tests/unit/test_cli.py`

---

## 10. Deferred Capabilities

The following remain outside Phase 4 certification:

- installation packaging
- service-account deployment automation
- systemd unit files
- timers and schedules
- log rotation
- production alerting
- remote runtime ownership coordination
- distributed locks
- runtime-state history beyond the authoritative latest record
- automated restore-test execution
- retention enforcement
- recovery-point cataloging
- operator runbooks for installed production service management

These are not Phase 4 defects. They are future implementation concerns.

---

## 11. Certification Deliverables

Slice 4D is complete when the repository contains:

1. this approved architecture intent
2. a runtime operational acceptance specification
3. runtime sequence and responsibility diagrams
4. a Phase 4 traceability and certification record
5. an explicit technical-debt and deferral register
6. a Phase 5 readiness decision

The deliverables may be separate documents where that improves governance and maintainability.

---

## 12. Verification Strategy

The certification work must verify:

```bash
ruff format --check src tests
ruff check src tests
pytest -q
git diff --check
```

The baseline at Slice 4D initiation is:

- 71 Python files formatted
- Ruff clean
- 322 tests passing
- clean `main`
- `origin/main` synchronized
- authoritative merge commit `74959d7`

Documentation must be reviewed against the implemented code and test inventory. Unsupported claims must not be introduced.

---

## 13. Acceptance Criteria

Slice 4D is complete when:

1. the runtime architecture is documented as implemented
2. operational acceptance scenarios are explicit
3. runtime responsibilities and composition boundaries are diagrammed
4. Phase 4 objectives are traced to implementation and tests
5. residual technical debt and deferred capabilities are recorded
6. no undocumented production behavior change is introduced
7. Ruff formatting and linting remain clean
8. all existing tests pass
9. Git whitespace validation passes
10. the feature branch is reviewed, committed, merged, and pushed
11. Phase 4 is formally certified or certification exceptions are explicitly recorded
12. a Phase 5 readiness decision is approved

---

## 14. Architecture Decision

Phase 4D is approved as a documentation-and-certification slice.

The implemented Phase 4 runtime architecture is sufficiently mature that additional production abstractions are not justified merely to continue implementation activity. The correct engineering action is to stabilize, verify, document, and certify the runtime baseline before beginning the next major capability phase.
