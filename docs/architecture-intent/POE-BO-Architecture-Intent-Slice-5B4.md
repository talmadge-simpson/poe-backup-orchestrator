# POE Backup Orchestrator Architecture Intent — Slice 5B-4

## Governed Restore Workspace Preflight

**Status:** Implementation baseline
**Phase:** 5B — Governed Restore Planning
**Slice:** 5B-4
**Baseline:** `11b8895`
**Feature branch:** `feature/restore-workspace-preflight`

## 1. Purpose

Slice 5B-4 introduces a read-only environmental preflight boundary for an
immutable `RestorePlan`.

The preflight service inspects the live filesystem conditions required by a
future isolated restore workspace and returns structured readiness evidence.
It does not create the workspace or execute any restore action.

## 2. Architectural Position

The Phase 5 flow becomes:

```text
recovery-point discovery
    ↓
eligibility evaluation
    ↓
deterministic restore planning
    ↓
workspace preflight
    ↓
future isolated staging and validation
```

Preflight is environmental observation. It does not modify the plan and does
not convert plan readiness into execution authorization.

## 3. Inputs

The service accepts:

- one immutable `RestorePlan`;
- an explicit timezone-aware UTC evaluation timestamp;
- a filesystem probe abstraction.

## 4. Output

The service returns immutable `RestoreWorkspacePreflight` evidence containing:

- schema version;
- plan identifier;
- evaluation timestamp;
- overall readiness;
- ordered checks;
- stable reason codes;
- warnings;
- and explicit confirmation that no mutation was performed.

## 5. Required Checks

The initial baseline checks:

1. plan readiness is not blocked;
2. source artifact is a readable regular file;
3. source manifest is a readable regular file;
4. authoritative target parent exists and is writable/searchable;
5. an existing authoritative target is a readable regular file;
6. staging target does not already exist;
7. rollback artifact does not already exist;
8. the nearest existing staging ancestor is writable/searchable;
9. the nearest existing rollback ancestor is writable/searchable;
10. authoritative, staging, and rollback paths remain distinct.

A failed mandatory check produces a blocked preflight result.

## 6. Safety Boundary

Slice 5B-4 must not:

- create directories;
- create temporary probe files;
- copy the recovery artifact;
- calculate checksums;
- invoke SQLite;
- create rollback evidence;
- acquire restore execution ownership;
- persist a restore plan;
- authorize execution;
- modify the authoritative Registry;
- promote a staged artifact;
- or publish final restore evidence.

Filesystem checks use metadata and access inspection only.

## 7. Determinism and Ordering

For an unchanged filesystem view, the same plan, and the same evaluation
timestamp, preflight produces an equal result.

Checks are emitted in stable contract order.

## 8. Failure Semantics

Expected environmental conflicts are represented as failed checks and reason
codes. Invalid service inputs raise `RestoreWorkspacePreflightError`.

A blocked plan remains blocked and is not treated as an operational exception.

## 9. Acceptance Criteria

Slice 5B-4 is accepted when:

- immutable preflight domain models exist;
- a read-only workspace preflight service exists;
- the service uses an injectable filesystem probe;
- source, target, staging, and rollback conditions are evaluated;
- results and check ordering are deterministic;
- no filesystem mutation occurs;
- no execution authorization is introduced;
- focused tests pass;
- and the complete quality baseline passes.

## 10. Deferred Work

The following remain deferred:

- workspace directory creation;
- recovery artifact staging;
- staged checksum verification;
- SQLite integrity validation;
- Registry application-level validation;
- rollback artifact creation;
- approval persistence;
- authoritative target locking;
- promotion;
- rollback execution;
- interrupted restore recovery;
- and recovery certification.
