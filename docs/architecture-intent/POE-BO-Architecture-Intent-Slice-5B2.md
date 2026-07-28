# POE Backup Orchestrator

## Architecture Intent — Slice 5B-2 Deterministic Restore Planning Engine

**Document ID:** POE-BO-Architecture-Intent-Slice-5B2
**Status:** Implementation Baseline
**Phase:** 5B — Governed Restore Planning
**Slice:** 5B-2 — Deterministic Restore Planning Engine

## Purpose

Slice 5B-2 introduces the deterministic, non-mutating service that converts one
governed `RecoveryPoint` and one `RestorePlanRequest` into an immutable
`RestorePlan`.

The planning engine describes a future restore. It does not execute one.

## Inputs

- an existing `RecoveryPoint`;
- an operator-supplied `RestorePlanRequest`;
- an explicit timezone-aware UTC planning timestamp.

## Outputs

The service returns an immutable `RestorePlan` containing:

- a deterministic plan identifier;
- deterministic staging and rollback paths;
- the selected recovery artifact and manifest paths;
- an ordered future-action sequence;
- readiness, warnings, conflicts, and approval requirements;
- execution authorization fixed to `False`.

## Determinism

For identical inputs and an identical planning timestamp, the engine returns an
equal plan. It reads no system clock, environment variable, filesystem state,
repository state, runtime state, or external service.

## Eligibility Translation

- `eligible` produces a `ready` plan;
- `conditionally_eligible` produces an `approval_required` plan;
- `ineligible` produces a `blocked` plan;
- `unknown` produces a `blocked` plan.

An eligibility override request records operator intent but never constitutes
approval or execution authorization.

## Architectural Boundary

This slice may perform pure validation and path composition. It must not:

- inspect whether paths exist;
- create directories;
- copy, rename, replace, or delete files;
- invoke SQLite;
- calculate checksums;
- acquire runtime ownership;
- inspect repository health or capacity;
- publish evidence;
- add or modify CLI behavior;
- authorize or execute a restore.

Environmental preflight and broader policy validation remain deferred.

## Action Sequence

A ready or approval-gated plan describes these future operations:

1. inspect the authoritative target;
2. stage the recovery artifact;
3. verify the staged checksum;
4. verify staged SQLite integrity;
5. create a rollback artifact;
6. verify the rollback artifact;
7. await approval when required;
8. promote the staged artifact;
9. verify the authoritative target;
10. publish restore evidence.

Blocked plans contain no mutating future actions.

## Acceptance Criteria

1. A planning service exists under `services.restore`.
2. The service is deterministic and side-effect free.
3. Recovery-point and request identifiers must match.
4. Required artifact and manifest metadata is enforced.
5. Paths are composed without filesystem inspection.
6. Eligibility classifications map predictably to plan readiness.
7. Conditional eligibility remains approval-gated.
8. Ineligible and unknown points produce blocked plans.
9. Execution authorization remains false.
10. Focused tests and the full suite pass.
