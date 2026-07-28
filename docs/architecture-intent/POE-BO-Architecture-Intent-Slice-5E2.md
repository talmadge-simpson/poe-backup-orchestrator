# POE Backup Orchestrator Architecture Intent — Slice 5E-2

## Restore Execution Record and Evidence Aggregation

### Status

Implementation candidate.

### Purpose

Slice 5E-2 introduces one immutable aggregate record for a completed governed
restore execution. The record preserves the evidence emitted by every
certified restore stage and makes the full execution chain available to later
persistence, reporting, and operator-integration slices.

### Architectural boundary

The execution record:

- includes the authorized restore plan;
- includes the governed execution lock path;
- includes start and completion timestamps;
- includes every immutable evidence object emitted by the composed restore
  services;
- declares completion only when post-promotion verification declares
  completion;
- validates plan identity across the entire evidence chain.

The execution record does not:

- serialize or persist itself;
- implement restart or resumability;
- represent partial or failed execution;
- suppress domain-service exceptions;
- alter ownership-release behavior;
- expose a CLI command.

Partial and failed execution recording is deferred until a durable execution
journal exists. Slice 5E-2 therefore creates a completed-execution aggregate
only after successful post-promotion verification.

### Orchestrator change

`RestoreExecutionOrchestrator.execute(...)` returns
`RestoreExecutionRecord` rather than returning only
`RestorePostPromotionVerification`.

The post-promotion verification remains available unchanged as the final
evidence member of the aggregate.

### Certification criteria

Slice 5E-2 is complete when tests prove:

- every stage evidence object is retained unchanged;
- the authorized restore plan and lock path are retained;
- execution timestamps are deterministic and coherent;
- plan identity mismatches are rejected;
- an incomplete final verification cannot create a completed record;
- the orchestrator returns the aggregate record;
- ownership release behavior remains unchanged;
- package exports expose the execution-record model.
