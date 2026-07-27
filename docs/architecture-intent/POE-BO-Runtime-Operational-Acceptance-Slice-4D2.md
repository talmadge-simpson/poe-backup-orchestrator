# POE Backup Orchestrator Runtime Operational Acceptance Specification

## Slice 4D.2 — Phase 4 Runtime Operational Acceptance

**Document ID:** POE-BO-Runtime-Operational-Acceptance-Slice-4D2
**Status:** Approved for implementation
**Parent:** POE-BO-Architecture-Intent-Slice-4D
**Phase:** Phase 4 — Production Runtime
**Purpose:** Define the authoritative operational acceptance contract for the implemented runtime subsystem.

---

## 1. Acceptance Objective

The Phase 4 runtime subsystem is accepted when it can:

- discover and validate the authoritative production runtime
- establish exclusive execution ownership
- persist runtime state durably and deterministically
- distinguish safe restart conditions from unsafe ownership conditions
- recover dead same-host ownership as interrupted execution
- expose authoritative runtime state through the CLI
- coordinate runtime lifecycle with orchestration state
- preserve terminal completion and failure state
- centralize production dependency composition
- pass all automated quality and regression checks

Operational acceptance validates the implemented runtime baseline. It does not introduce new runtime behavior.

---

## 2. Acceptance Authority

The authoritative acceptance basis consists of:

1. approved Phase 4 architecture-intent documents
2. implemented runtime production code
3. automated test evidence
4. CLI-observable behavior
5. repository quality checks
6. the final Phase 4 certification record

Where documentation and implementation differ, certification must record the discrepancy explicitly. Documentation must not be used to claim behavior that the implementation does not support.

---

## 3. Required Acceptance Environment

Acceptance must be executed from the authoritative repository checkout on the Raspberry Pi runtime host.

Required conditions:

- branch under review is based on current `main`
- working tree is clean except for the documentation being reviewed
- Python virtual environment is active
- configuration parses successfully
- runtime roots are discoverable
- repository quality tools are installed
- all automated tests can be collected and executed

The Phase 4D baseline begins with:

- 71 Python files under Ruff formatting control
- 322 tests collected and passing
- runtime architecture merged through Slice 4C.2
- no known failing quality checks

---

## 4. Acceptance Evidence Classes

Each acceptance scenario must identify one or more evidence classes.

### 4.1 Automated Test Evidence

Evidence produced by named pytest tests that directly exercise the acceptance claim.

### 4.2 Static Architecture Evidence

Evidence produced by source inspection, import boundaries, composition factories, and absence of prohibited construction.

### 4.3 CLI Evidence

Evidence produced by invoking supported CLI commands and observing stable output and exit behavior.

### 4.4 Persistence Evidence

Evidence produced by reading the authoritative runtime-state record before and after a scenario.

### 4.5 Quality Evidence

Evidence produced by:

```bash
ruff format --check src tests
ruff check src tests
pytest -q
git diff --check
```

### 4.6 Governance Evidence

Evidence recorded in the architecture baseline, traceability matrix, certification checklist, and technical-debt register.

---

## 5. Acceptance Result Model

Each acceptance scenario must result in one of:

- **PASS** — all required observations match the acceptance criteria
- **FAIL** — one or more required observations contradict the criteria
- **BLOCKED** — the scenario cannot be executed because a prerequisite is unavailable
- **NOT APPLICABLE** — the scenario is intentionally outside the certified scope

A BLOCKED result prevents Phase 4 certification unless the certification authority explicitly accepts the block as a documented exception.

A FAIL result prevents certification.

---

## 6. Scenario OA-RT-001 — No Prior Runtime State

### Objective

Prove that a runtime with no persisted state permits a new execution to establish ownership.

### Preconditions

- runtime-state file is absent
- state root is writable
- no active process owns the runtime

### Expected Results

- recovery outcome is `no_state`
- lifecycle startup is permitted
- a runtime-state record is created
- status is `running`
- execution state is `created`
- run ID, PID, hostname, environment, and UTC timestamps are present

### Automated Traceability

- `test_no_state_returns_no_state`
- `test_start_publishes_created_running_state[no_state]`
- `test_save_load_round_trip_and_create_root`

---

## 7. Scenario OA-RT-002 — Prior Completed State

### Expected Results

- recovery outcome is terminal
- prior state is not mutated during inspection
- lifecycle startup is permitted
- new execution ownership may replace the prior terminal record

### Automated Traceability

- `test_terminal_state_is_observable_without_mutation[completed-completed]`
- `test_start_publishes_created_running_state[terminal_state]`

---

## 8. Scenario OA-RT-003 — Prior Failed State

### Expected Results

- recovery outcome is terminal
- failure state remains unchanged during inspection
- lifecycle startup is permitted
- new ownership may be established

### Automated Traceability

- `test_terminal_state_is_observable_without_mutation[failed-failed]`
- `test_start_publishes_created_running_state[terminal_state]`

---

## 9. Scenario OA-RT-004 — Prior Interrupted State

### Expected Results

- inspection does not mutate the record again
- recovery treats the state as terminal observation
- lifecycle startup is permitted
- a new execution may establish ownership

### Automated Traceability

- `test_terminal_state_is_observable_without_mutation[interrupted-repository_validation]`
- `test_start_publishes_created_running_state[interrupted_execution]`
- `test_reinspection_of_interrupted_state_is_terminal`

---

## 10. Scenario OA-RT-005 — Same-Host Live Owner

### Expected Results

- recovery outcome is `active_execution`
- lifecycle startup is rejected
- existing state is not mutated
- no operational work begins

### Automated Traceability

- `test_same_host_live_pid_is_active`
- `test_start_blocks_unsafe_ownership[active_execution]`
- `test_runtime_start_failure_prevents_operational_work`

---

## 11. Scenario OA-RT-006 — Different-Host Running Owner

### Expected Results

- recovery outcome is `ambiguous_ownership`
- persisted state is not mutated
- lifecycle startup is rejected
- no process-liveness decision is used to seize ownership

### Automated Traceability

- `test_different_host_is_ambiguous_and_not_mutated`
- `test_start_blocks_unsafe_ownership[ambiguous_ownership]`

---

## 12. Scenario OA-RT-007 — Same-Host Dead Owner Recovery

### Expected Results

- recovery outcome is `interrupted_execution`
- status is changed to `interrupted`
- execution state remains the last known nonterminal state
- updated timestamp advances
- the recovered state is persisted
- a later inspection observes terminal interrupted state

### Automated Traceability

- `test_dead_same_host_owner_is_persisted_as_interrupted`
- `test_reinspection_of_interrupted_state_is_terminal`
- `test_save_load_round_trip_and_create_root`

---

## 13. Scenario OA-RT-008 — Successful Runtime-Aware Orchestration

### Expected Results

- runtime lifecycle starts before operational work
- each accepted orchestration transition is persisted
- terminal runtime status is `completed`
- terminal execution state is `completed`
- operational result remains successful

### Automated Traceability

- `test_runtime_lifecycle_observes_successful_orchestration`
- `test_transition_persists_each_accepted_state`
- `test_builder_composes_runtime_lifecycle_into_orchestrator`

---

## 14. Scenario OA-RT-009 — Controlled Runtime-Aware Failure

### Expected Results

- orchestration result is failed
- runtime status is `failed`
- runtime execution state is `failed`
- operational failure mapping remains intact
- prior successful component results remain available where applicable

### Automated Traceability

- `test_runtime_lifecycle_observes_controlled_failure`
- `test_failed_transition_persists_failed_terminal_state`
- `test_execute_returns_typed_failed_result`
- `test_run_service_publishes_governed_failure_and_returns_mapped_exit`

---

## 15. Scenario OA-RT-010 — Runtime-State CLI Inspection

### Expected Results

For no state:

- exit code is zero
- recovery outcome is displayed
- state-changed indicator is displayed
- absence of state is explicit

For persisted state:

- exit code is zero
- recovery outcome is displayed
- state-changed indicator is displayed
- runtime status is displayed
- execution state is displayed
- run ID is displayed
- hostname is displayed
- PID is displayed
- environment is displayed

### Automated Traceability

- `test_runtime_state_command_reports_no_state`
- `test_runtime_state_command_reports_persisted_state`
- `test_runtime_state_command_is_present_in_help`

---

## 16. Scenario OA-RT-011 — Runtime-State Persistence Integrity

### Expected Results

- authoritative filename is stable
- absent file loads as no state
- writes are deterministic UTF-8 JSON
- replacement is atomic
- malformed or unsupported records produce controlled errors
- failed replacement preserves the prior record
- clear is effective and idempotent

### Automated Traceability

- `tests/unit/test_runtime_state_store.py`

---

## 17. Scenario OA-RT-012 — Production Composition Integrity

### Expected Results

Execution composition:

```text
build_registry_backup_run_service()
    -> RuntimeStateStore
    -> RuntimeRecoveryInspector
    -> RuntimeLifecycleCoordinator
    -> RegistryBackupOrchestrator
```

Inspection composition:

```text
build_runtime_recovery_inspector()
    -> RuntimeStateStore
    -> SystemHostIdentity
    -> SystemProcessLiveness
    -> SystemUtcClock
    -> RuntimeRecoveryInspector
```

The CLI invokes composition factories and does not instantiate runtime implementation dependencies directly.

### Automated Traceability

- `test_builder_composes_runtime_lifecycle_into_orchestrator`
- `test_builder_composes_runtime_recovery_inspector`
- `test_builder_is_exported_from_services_package`
- `test_run_command_delegates_to_run_service`
- `test_runtime_state_command_reports_no_state`
- `test_runtime_state_command_reports_persisted_state`

---

## 18. Scenario OA-RT-013 — Runtime Discovery and Validation

### Expected Results

- production runtime uses authoritative paths
- explicit configuration path is honored
- filesystem capability is validated
- invalid runtime is rejected through a controlled domain error
- requested environment mismatch is rejected

### Automated Traceability

- `tests/unit/test_runtime_discovery.py`
- `tests/unit/test_runtime_validation.py`
- `tests/unit/test_production_bootstrap.py`

---

## 19. Scenario OA-RT-014 — Regression and Quality Baseline

### Execution

```bash
ruff format --check src tests
ruff check src tests
pytest -q
git diff --check
```

### Expected Results

- all files are formatted
- no Ruff violations exist
- all tests pass
- no whitespace errors exist

### Baseline

- 71 Python files formatted
- 322 tests passing
- Ruff clean

Any change to these counts must be explained in the certification record.

---

## 20. Acceptance Checklist

- [ ] OA-RT-001 No prior runtime state — PASS
- [ ] OA-RT-002 Prior completed state — PASS
- [ ] OA-RT-003 Prior failed state — PASS
- [ ] OA-RT-004 Prior interrupted state — PASS
- [ ] OA-RT-005 Same-host live owner — PASS
- [ ] OA-RT-006 Different-host running owner — PASS
- [ ] OA-RT-007 Same-host dead owner recovery — PASS
- [ ] OA-RT-008 Successful runtime-aware orchestration — PASS
- [ ] OA-RT-009 Controlled runtime-aware failure — PASS
- [ ] OA-RT-010 Runtime-state CLI inspection — PASS
- [ ] OA-RT-011 Runtime-state persistence integrity — PASS
- [ ] OA-RT-012 Production composition integrity — PASS
- [ ] OA-RT-013 Runtime discovery and validation — PASS
- [ ] OA-RT-014 Regression and quality baseline — PASS
- [ ] no undocumented runtime behavior change
- [ ] technical debt and deferred capabilities recorded
- [ ] architecture diagrams completed
- [ ] traceability matrix completed
- [ ] Phase 4 certification record approved

---

## 21. Exit Criteria

Slice 4D.2 is complete when:

1. every runtime acceptance scenario has explicit expected results and evidence
2. each scenario traces to implemented code and automated tests
3. pass, fail, blocked, and not-applicable outcomes are defined
4. the acceptance checklist is complete
5. no production behavior change is introduced
6. repository quality checks remain clean
7. the document is reviewed, committed, merged, and pushed

Phase 4 itself is not certified by this specification alone. Certification occurs only after the remaining Slice 4D deliverables are completed and the Phase 4 certification record is approved.

---

## 22. Approval Decision

This specification is approved as the authoritative operational acceptance contract for the Phase 4 runtime subsystem.

The next governed deliverable is Slice 4D.3 — Runtime Sequence and Responsibility Diagrams.
