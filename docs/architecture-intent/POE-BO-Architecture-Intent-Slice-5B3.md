# POE Backup Orchestrator Architecture Intent — Slice 5B-3

## Deterministic Restore Plan CLI

**Status:** Implementation baseline
**Phase:** 5B — Governed Restore Planning
**Slice:** 5B-3
**Baseline:** `ae94ddb`
**Feature branch:** `feature/restore-plan-cli`

## 1. Purpose

Slice 5B-3 exposes the deterministic restore-planning engine through the
Backup Orchestrator command-line interface.

The slice allows an operator to select a discovered Registry recovery point,
evaluate it under the current eligibility policy, supply an authoritative
target path, and render the resulting immutable restore plan.

This slice does not execute a restore.

## 2. Command Contract

The primary command is:

```text
poe-backup-orchestrator restore plan \
  --backup-id <recovery-point-id> \
  --target <authoritative-registry-path>
```

Optional planning controls are:

```text
--destination-root <accepted-backup-root>
--staging-root <governed-planning-staging-root>
--rollback-root <governed-planning-rollback-root>
--eligibility-override
--operator-rationale <text>
```

An eligibility override requires a non-empty operator rationale.

## 3. Governed Defaults

When not explicitly supplied:

- recovery-point discovery uses
  `<repository_root>/Registry/POERegistry`;
- restore staging uses
  `<restore_tests_root>/Planning/Staging`;
- rollback planning uses
  `<restore_tests_root>/Planning/Rollback`.

These are planning inputs only. Slice 5B-3 does not create these directories
or write any artifacts.

## 4. Processing Pipeline

The CLI performs the following read-only planning sequence:

1. bootstrap configuration;
2. discover recovery points;
3. locate the selected recovery point;
4. evaluate current restore eligibility;
5. construct `RestorePlanRequest`;
6. invoke the deterministic planning engine;
7. render the immutable `RestorePlan`.

The same UTC timestamp is supplied to eligibility evaluation and plan
construction for one internally consistent command result.

## 5. Rendered Evidence

The command renders:

- plan identifier;
- schema and policy versions;
- creation timestamp;
- selected recovery-point identifier;
- source artifact and manifest paths;
- authoritative target;
- staging target;
- rollback artifact;
- readiness;
- reason codes;
- approval requirement;
- execution authorization state;
- warnings;
- conflicts;
- ordered planned actions.

Each action identifies its ordinal, controlled action type, description,
source and destination paths where applicable, mutation intent, and approval
requirement.

## 6. Exit Behavior

A successfully constructed plan returns exit code `0`, including plans whose
readiness is `blocked` or `approval_required`. Readiness is a governed domain
result, not a CLI processing failure.

Controlled input, discovery, and planning failures return exit code `1`.

Unsupported command syntax remains governed by `argparse` and returns exit
code `2`.

## 7. Explicit Non-Goals

Slice 5B-3 does not:

- copy or stage a recovery artifact;
- inspect or modify the authoritative Registry target;
- create a rollback artifact;
- acquire runtime ownership;
- authorize execution;
- mutate repository, staging, rollback, or runtime state;
- persist a restore plan;
- publish restore evidence.

## 8. Acceptance Criteria

The slice is accepted when:

- `restore plan` is visible in restore help;
- required and optional arguments parse correctly;
- configured default roots are deterministic;
- discovery, eligibility, and planning are invoked in order;
- a complete plan is rendered;
- override rationale is enforced;
- planning errors are controlled;
- existing restore commands remain unchanged;
- formatting, linting, whitespace validation, and the complete unit suite pass.
