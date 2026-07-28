# POE Backup Orchestrator
## Architecture Intent — Slice 5B-1 Restore Plan Domain Contract

**Document ID:** POE-BO-Architecture-Intent-Slice-5B1
**Status:** Implementation Baseline
**Phase:** 5B — Governed Restore Planning
**Slice:** 5B-1 — Restore Plan Domain Contract

## Purpose

Slice 5B-1 establishes the immutable domain vocabulary for governed restore
planning. It defines what a restore plan is, what an operator requests, what
actions a future planning engine may describe, and how conflicts, warnings,
approval requirements, and readiness are represented.

This slice is intentionally non-mutating. It does not copy a recovery artifact,
create rollback evidence, stage a restore, replace the authoritative Registry,
or publish a plan.

## Architectural Boundary

This slice may define immutable models, enumerations, invariants, exports, and
unit tests. It must not inspect the live filesystem, calculate capacity, copy
artifacts, create staging or rollback directories, invoke SQLite, acquire
runtime locks, add CLI commands, publish evidence, or execute a restore.

## Principles

1. Planning precedes mutation.
2. A plan is descriptive, not executable.
3. Every proposed mutation must be explicit.
4. Conflicts and warnings are first-class evidence.
5. Approval requirements are independent from readiness.
6. Restore execution remains prohibited until later authorization.
7. Model instances are immutable.
8. Paths use `pathlib.Path`.
9. Planning timestamps are timezone-aware UTC values.
10. Collections are immutable tuples.

## Domain Objects

- `RestorePlanRequest`: operator planning intent only.
- `RestoreAction`: one ordered future operation.
- `RestoreWarning`: non-blocking condition.
- `RestoreConflict`: blocking or approval-dependent condition.
- `RestorePlanValidation`: governed readiness result.
- `RestorePlan`: complete immutable proposed restore description.

## Readiness

- `ready`
- `approval_required`
- `blocked`
- `unknown`

Readiness is not execution authorization.

## Invariants

- identifiers, descriptions, codes, and policy versions are non-empty;
- timestamps are timezone-aware UTC;
- action ordinals are positive, unique, and contiguous from one;
- warning and conflict codes are unique;
- ready plans have no blocking conflicts and require no approval;
- blocked plans contain a blocking conflict;
- approval-required plans require approval;
- execution authorization is prohibited;
- authoritative, staging, and rollback paths are distinct;
- override requests require operator rationale.

## Acceptance Criteria

1. Model module exists.
2. Models are frozen and slot-based.
3. Package exports expose the complete contract.
4. Invariants are unit tested.
5. Ruff passes.
6. Full test suite passes.
7. No restore execution or filesystem mutation is introduced.

## Deferred Work

Planning engine, CLI, environmental preflight, evidence publication, staging,
rollback creation, promotion, Registry replacement, and execution remain
outside this slice.
