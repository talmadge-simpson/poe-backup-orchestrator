# POE Backup Orchestrator Architecture Intent — Slice 5E-1

## Controlled Restore Execution Orchestration

### Status

Implementation candidate.

### Purpose

Slice 5E-1 introduces the first composition layer for governed restore
execution. It sequences the independently certified restore services without
absorbing or duplicating their domain responsibilities.

### Architectural boundary

The execution orchestrator:

- accepts an already constructed and authorized `RestorePlan`;
- acquires exclusive execution ownership before any restore-workspace mutation;
- invokes the certified restore services in their required order;
- supplies one UTC timestamp to each service invocation;
- passes immutable evidence from each stage to the next;
- releases execution ownership on both successful and failed execution paths;
- returns only the final `RestorePostPromotionVerification` evidence.

The execution orchestrator does not:

- discover recovery points;
- construct or authorize restore plans;
- implement filesystem, integrity, policy, rollback, or promotion mechanics;
- persist evidence;
- expose an operator-facing CLI command;
- suppress or reinterpret domain-service failures;
- declare restore completion independently.

### Ordered workflow

1. Acquire exclusive restore execution ownership.
2. Evaluate restore-workspace preflight.
3. Materialize the governed restore workspace.
4. Stage the selected recovery artifact.
5. Validate staged artifact integrity and SQLite consistency.
6. Validate Registry application compatibility.
7. Preflight the authoritative target.
8. Capture rollback evidence and artifact state.
9. Evaluate promotion readiness using continuous ownership evidence.
10. Execute atomic authoritative promotion.
11. Verify promoted state and emit restore-completion evidence.
12. Release execution ownership.

### Failure semantics

The orchestrator is fail-fast. Any exception raised by a composed domain
service terminates the workflow immediately. Previously emitted in-memory
evidence is not transformed into success evidence. Execution ownership is
released through a `finally` boundary.

Persistence, resumability, execution journals, and advanced cleanup semantics
are intentionally deferred to later Phase 5E slices.

### Certification criteria

Slice 5E-1 is complete when tests prove:

- exact service invocation order;
- evidence chaining between every stage;
- ownership evidence is supplied to promotion-readiness evaluation;
- final post-promotion verification is returned unchanged;
- ownership is released after successful execution;
- ownership is released after a composed service fails;
- downstream services are not invoked after failure;
- package exports expose the orchestration service.
