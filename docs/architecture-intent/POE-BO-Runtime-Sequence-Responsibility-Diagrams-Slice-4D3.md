# POE Backup Orchestrator Runtime Sequence & Responsibility Diagrams

## Slice 4D.3 — Phase 4 Runtime Architecture Visualization

**Document ID:** POE-BO-Runtime-Sequence-Responsibility-Diagrams-Slice-4D3
**Status:** Approved for implementation
**Parent:** POE-BO-Architecture-Intent-Slice-4D
**Phase:** Phase 4 — Production Runtime
**Purpose:** Provide the authoritative visual model of runtime execution, recovery, ownership, lifecycle, composition, and component responsibility.

---

## 1. Diagram Conventions

The diagrams in this document are normative architectural views of the implemented runtime baseline.

Conventions:

- solid arrows represent invocation or control flow
- dashed arrows represent observation or returned evidence
- brackets represent persisted state
- decision diamonds are rendered as explicit yes/no branches
- composition diagrams show construction ownership, not runtime call order
- responsibility tables describe the implemented ownership boundary

---

## 2. Runtime Execution Sequence

```text
Operator
   |
   v
CLI: run / acceptance-run
   |
   v
bootstrap_application()
   |
   +--> discover runtime
   +--> validate runtime
   +--> load application configuration
   |
   v
ApplicationContext + RuntimeDescriptor
   |
   v
build_registry_backup_run_service()
   |
   +--> build RuntimeStateStore
   +--> build RuntimeRecoveryInspector
   +--> build RuntimeLifecycleCoordinator
   +--> build RegistryBackupOrchestrator
   +--> build RegistryBackupRunService
   |
   v
RegistryBackupRunService.run()
   |
   v
RuntimeLifecycleCoordinator.start()
   |
   +--> RuntimeRecoveryInspector.inspect()
   |       |
   |       +--> RuntimeStateStore.load()
   |       +--> host identity comparison
   |       +--> process liveness evaluation
   |
   +--> reject unsafe ownership
   +--> persist RUNNING / CREATED
   |
   v
RegistryBackupOrchestrator.execute()
   |
   +--> validate repository
   +--> accept registry source
   +--> create consistent backup
   +--> generate manifest
   +--> verify integrity
   +--> publish report
   |
   +--> RuntimeLifecycleCoordinator.transition(...)
   |       |
   |       +--> RuntimeStateStore.save()
   |
   v
RuntimeLifecycleCoordinator.complete() or fail()
   |
   +--> persist COMPLETED or FAILED
   |
   v
RegistryBackupRunService publishes governed result
   |
   v
CLI renders result and returns stable exit code
```

---

## 3. Runtime Recovery Inspection Sequence

```text
Operator
   |
   v
CLI: runtime-state
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
   +--> RuntimeStateStore.load()
   |
   +--> no state?
   |       |
   |       +--> return NO_STATE
   |
   +--> terminal state?
   |       |
   |       +--> return TERMINAL_STATE
   |
   +--> owner host differs?
   |       |
   |       +--> return AMBIGUOUS_OWNERSHIP
   |
   +--> owner PID alive?
           |
           +--> yes: return ACTIVE_EXECUTION
           |
           +--> no:
                  persist INTERRUPTED
                  return INTERRUPTED_EXECUTION
   |
   v
CLI renders outcome, mutation indicator, and state fields
```

---

## 4. Runtime Ownership Decision Tree

```text
                         +----------------------+
                         | Load persisted state |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | State record absent? |
                         +----+------------+----+
                              | yes        | no
                              v            v
                         NO_STATE   +------------------+
                                    | State terminal?  |
                                    +----+--------+----+
                                         | yes    | no
                                         v        v
                                  TERMINAL_STATE  +----------------------+
                                                  | Same owner hostname? |
                                                  +----+------------+----+
                                                       | no         | yes
                                                       v            v
                                             AMBIGUOUS_OWNERSHIP  +---------------+
                                                                  | PID alive?    |
                                                                  +----+-----+----+
                                                                       | yes | no
                                                                       v     v
                                                              ACTIVE_EXECUTION
                                                                             |
                                                                             v
                                                                  persist INTERRUPTED
                                                                             |
                                                                             v
                                                              INTERRUPTED_EXECUTION
```

---

## 5. Runtime State Transition Model

```text
                         lifecycle start
                               |
                               v
                         +-----------+
                         |  RUNNING  |
                         |  CREATED  |
                         +-----+-----+
                               |
                               v
                    accepted execution transitions
                               |
          +--------------------+--------------------+
          |                    |                    |
          v                    v                    v
 repository validation   registry acceptance   backup creation
          |                    |                    |
          +--------------------+--------------------+
                               |
                               v
                         verification/reporting
                               |
                    +----------+----------+
                    |                     |
                    v                     v
             +-------------+       +-------------+
             |  COMPLETED  |       |   FAILED    |
             |  COMPLETED  |       |   FAILED    |
             +-------------+       +-------------+

External recovery path:

RUNNING + same-host dead PID
               |
               v
        +-------------+
        | INTERRUPTED |
        | last known  |
        | exec state  |
        +-------------+
```

Terminal runtime statuses:

- `completed`
- `failed`
- `interrupted`

Nonterminal runtime status:

- `running`

---

## 6. Production Composition Diagram

```text
CLI
 |
 +--> bootstrap_application()
 |
 +--> build_registry_backup_run_service()
 |       |
 |       +--> RuntimeStateStore
 |       |
 |       +--> RuntimeRecoveryInspector
 |       |       |
 |       |       +--> SystemHostIdentity
 |       |       +--> SystemProcessLiveness
 |       |       +--> SystemUtcClock
 |       |
 |       +--> RuntimeLifecycleCoordinator
 |       |
 |       +--> RegistryBackupOrchestrator
 |       |       |
 |       |       +--> repository validation service
 |       |       +--> registry acceptance service
 |       |       +--> backup service
 |       |       +--> manifest service
 |       |       +--> integrity verification service
 |       |       +--> reporting service
 |       |
 |       +--> RegistryBackupRunService
 |
 +--> build_runtime_recovery_inspector()
         |
         +--> RuntimeStateStore
         +--> SystemHostIdentity
         +--> SystemProcessLiveness
         +--> SystemUtcClock
         +--> RuntimeRecoveryInspector
```

The CLI requests fully composed services. It does not assemble implementation dependencies directly.

---

## 7. Persistent Runtime State Interaction

```text
RuntimeLifecycleCoordinator
          |
          | save initial ownership
          v
 [authoritative runtime-state JSON]
          ^
          |
          | load / save recovered state
          |
RuntimeRecoveryInspector
          ^
          |
          | load for operator inspection
          |
CLI runtime-state through composition factory
```

Persistence properties:

```text
serialize deterministically
        |
write temporary file
        |
flush file contents
        |
fsync temporary file
        |
atomic replace
        |
fsync containing directory
        |
authoritative state visible
```

Failure during replacement must preserve the prior authoritative record.

---

## 8. Runtime Failure Propagation

```text
Operational service failure
          |
          v
RegistryBackupOrchestrator
          |
          +--> map controlled domain failure
          +--> retain completed component evidence
          |
          v
RuntimeLifecycleCoordinator.fail()
          |
          +--> persist FAILED / FAILED
          |
          v
RegistryBackupRunService
          |
          +--> publish governed failure result
          |
          v
CLI
          |
          +--> render failure
          +--> return mapped exit code
```

A runtime persistence failure is itself operationally significant and must not be silently ignored.

---

## 9. Component Responsibility Matrix

| Component | Primary Responsibility | May Decide | Must Not Own |
|---|---|---|---|
| CLI | Parse commands, invoke bootstrap and composition, render results, return exit codes | command routing and presentation | runtime ownership, persistence semantics, lifecycle transitions |
| Production bootstrap | Discover and validate runtime, load application context | whether runtime prerequisites are valid | orchestration behavior |
| Runtime composition | Construct production dependency graphs | concrete dependency wiring | operator presentation or business workflow |
| RuntimeStateStore | Persist and load authoritative runtime state | serialization and atomic replacement mechanics | ownership interpretation |
| RuntimeRecoveryInspector | Interpret prior runtime state | recovery outcome and safe reclassification | orchestration execution |
| RuntimeLifecycleCoordinator | Publish execution ownership and lifecycle state | startup blocking and runtime transition persistence | operational stage implementation |
| RegistryBackupOrchestrator | Coordinate operational backup stages | workflow progression and mapped failure result | filesystem-level state serialization |
| RegistryBackupRunService | Execute governed run and publish result | run-level result and mapped exit behavior | dependency construction |
| SystemHostIdentity | Report current hostname | host identity value | recovery policy |
| SystemProcessLiveness | Report whether a PID is alive | process liveness observation | ownership seizure |
| SystemUtcClock | Provide UTC timestamps | current time value | lifecycle policy |

---

## 10. Responsibility Assignment View

Legend:

- **A** — accountable for the architectural decision
- **R** — responsible for execution
- **C** — consulted through dependency or result
- **I** — informed through returned evidence

| Activity | CLI | Bootstrap | Composition | State Store | Recovery Inspector | Lifecycle Coordinator | Orchestrator | Run Service |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Discover runtime | I | A/R | C |  |  |  |  |  |
| Validate runtime | I | A/R | C |  |  |  |  |  |
| Construct runtime graph | I | C | A/R | C | C | C | C | C |
| Load persisted runtime state | I |  | C | A/R | R | C |  |  |
| Interpret prior ownership | I |  | C | C | A/R | C |  |  |
| Block unsafe startup | I |  | C | C | C | A/R | I | I |
| Persist lifecycle transition | I |  | C | A/R | C | R | C | I |
| Coordinate backup workflow | I |  | C |  |  | C | A/R | C |
| Publish governed result | I |  | C |  |  | C | C | A/R |
| Render operator output | A/R | I | I |  | I | I | I | I |

---

## 11. Architectural Boundary Rules

The following rules are certified boundaries:

1. The CLI must invoke production composition factories.
2. The CLI must not instantiate runtime persistence or recovery implementations directly.
3. `RuntimeStateStore` must not interpret ownership policy.
4. `RuntimeRecoveryInspector` must not execute backup workflow stages.
5. `RuntimeLifecycleCoordinator` must not implement operational backup services.
6. `RegistryBackupOrchestrator` must not own runtime-state serialization.
7. Process liveness and host identity providers must remain policy-neutral.
8. Runtime state complements, but does not replace, the orchestration state machine.
9. Cross-host running ownership must remain ambiguous unless a future distributed ownership mechanism is introduced.
10. New deployment capabilities must not be folded into Phase 4 certification retroactively.

---

## 12. Traceability to Acceptance Scenarios

| Diagram or View | Acceptance Scenarios |
|---|---|
| Runtime Execution Sequence | OA-RT-001, OA-RT-008, OA-RT-009 |
| Recovery Inspection Sequence | OA-RT-001 through OA-RT-007, OA-RT-010 |
| Ownership Decision Tree | OA-RT-001 through OA-RT-007 |
| State Transition Model | OA-RT-001, OA-RT-004, OA-RT-007 through OA-RT-009 |
| Production Composition Diagram | OA-RT-012 |
| Persistent State Interaction | OA-RT-007, OA-RT-011 |
| Failure Propagation | OA-RT-009 |
| Responsibility Matrix | OA-RT-012, OA-RT-013 |
| Quality Boundary Rules | OA-RT-014 |

---

## 13. Verification Requirements

Slice 4D.3 must preserve the existing runtime baseline.

Required checks:

```bash
ruff format --check src tests
ruff check src tests
pytest -q
git diff --check
```

The document must be reviewed against:

- runtime composition implementation
- runtime lifecycle implementation
- recovery implementation
- runtime-state store implementation
- CLI delegation tests
- orchestration and run-service tests

Unsupported relationships must not be introduced into the diagrams.

---

## 14. Exit Criteria

Slice 4D.3 is complete when:

1. the execution path is diagrammed
2. the recovery path is diagrammed
3. the ownership decision tree is diagrammed
4. the runtime state transitions are diagrammed
5. the production composition graph is diagrammed
6. persistence and failure propagation are diagrammed
7. component responsibilities are explicit
8. architectural boundary rules are recorded
9. diagrams trace to the operational acceptance scenarios
10. no production behavior change is introduced
11. repository quality checks remain clean
12. the document is reviewed, committed, merged, and pushed

---

## 15. Approval Decision

This document is approved as the authoritative visual architecture companion for the Phase 4 runtime subsystem.

The next governed deliverable is Slice 4D.4 — Phase 4 Runtime Certification Record.
