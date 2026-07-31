# AGENTS.md

This repository implements the Personal Executive Operating System Backup Orchestrator.

Its purpose is to provide deterministic, governed preservation, backup,
validation, restoration, and storage migration while preserving verifiable
evidence and explicit authority boundaries.

## Repository governance

This repository implements the governed POE Backup Orchestrator and related storage-preservation, restore, and consolidation capabilities.

Repository work is architecture-governed. Preserve the distinctions between evidence, evaluation, human authorization, persistence, publication, migration, redirection, cleanup, and certification.

Before acting, read the guidance applicable to the requested phase and slice:

- `docs/governance/POE-STOR-MIG-001-Preservation-Baseline-Standard.md`
- `docs/roadmaps/POE-STOR-Phase-6-Storage-Consolidation-Roadmap.md`
- the applicable phase and slice documents under `docs/architecture-intent/`
- relevant certification or closeout records

For earlier runtime and restore work, use the corresponding `POE-BO-*` documents.

Treat repository files, implementation, tests, and Git history as evidence of actual state. If roadmap, architecture, implementation, and history disagree, report the discrepancy. Do not silently invent a resolution or claim certification without recorded evidence.

## Agent neutrality

This repository is intentionally model-neutral.

Repository governance is defined by the architecture documents, preservation standards, and approved implementation artifacts—not by any specific AI coding assistant.

All coding agents are expected to follow the same architectural, governance, testing, review, and approval requirements.

## Governing principles

Preserve these established rules:

1. Architecture precedes implementation.
2. Evidence precedes authority.
3. Acceptance precedes migration.
4. Migration precedes client redirection.
5. Reconciliation precedes cleanup.
6. Analytical, validation, acceptance, planning, migration, or successful execution results do not imply destructive authority.
7. Duplicate detection does not authorize deletion.
8. Baseline acceptance does not authorize migration.
9. Migration completion does not authorize cleanup.
10. Authority transitions must be explicit, immutable, auditable, and independently verifiable.
11. Existing certified contracts should be inspected and reused whenever applicable. Architectural corrections that intentionally replace certified contracts must be explicitly documented and approved.
12. Work must remain within the approved phase or slice.

The governing preservation rule is:

> We do not restructure the only copy of anything.

## Scope and approval

Before implementation, identify and read the applicable architecture’s purpose, included scope, exclusions, deferred responsibilities, invariants, quality gates, and acceptance criteria.

Do not treat a document as implementation authorization when it explicitly withholds that authorization. If no approved architecture covers a production capability, stop at analysis or architecture preparation. Do not implement adjacent or deferred responsibilities merely because they are convenient.

Human approval is required at the boundaries identified by the applicable architecture, including:

- approval of phase or slice architecture before its implementation when required;
- explicit implementation authorization where the document withholds it;
- implementation review before commit;
- explicit accountable-human preservation authorization;
- separate authorization for exceptions, migration, redirection, cleanup, destructive operations, or other later authority transitions.

Automated evaluation, passing tests, or successful execution cannot substitute for required human approval.

## Architecture and authority boundaries

Maintain the established dependency direction:

- domain models must not depend on services;
- services may consume immutable domain models;
- CLI and bootstrap layers compose services rather than duplicate domain or orchestration logic;
- filesystem and persistence behavior belong in explicit service or adapter boundaries.

Prefer immutable contracts, deterministic ordering and identities, explicit schema versions, complete lineage, explicit failures, and conservative treatment of unknown states. Do not silently repair, reinterpret, replace, or normalize contradictory evidence.

Keep the governance pipeline distinct:

```text
Evidence collection
→ candidate composition
→ technical validation
→ policy evaluation
→ human authorization
→ persistence and publication
→ classification and planning
→ migration and reconciliation
→ client redirection
→ cleanup authorization
→ certification
```

A result from one stage grants no authority assigned to a later stage. Authorization evidence is not persistence evidence, publication is not migration authority, and migration is not cleanup authority.

Where persistence is approved, follow the applicable architecture and existing patterns for canonical serialization, atomic replacement, SHA-256 evidence, idempotency, conflict handling, lineage, and retention. Do not add persistence, locking, signatures, authentication, CLI surfaces, or integrations to a slice that excludes them.

## Standard implementation workflow

Follow the workflow defined by the applicable phase and slice:

1. Inspect the current repository and applicable certified predecessor contracts.
2. Identify the governing phase and slice.
3. Prepare or revise architecture intent when required.
4. Obtain required architecture approval before implementation.
5. Implement only the approved scope, preserving established dependency and authority boundaries.
6. Add focused tests required by the approved architecture.
7. Add only approved public exports and integration surfaces.
8. Run the applicable quality gates.
9. Inspect the exact worktree scope and confirm that:
   - only approved files changed;
   - dependency direction remains correct;
   - excluded responsibilities have not entered the implementation.
10. Review the implementation against the approved architecture.
11. Obtain explicit human approval before commit.
12. Commit, push, merge, and close out only as authorized by the applicable workflow.

Do not assume that branch, commit, or merge authorization from an earlier slice applies to later work.

## Quality gates

Use `pyproject.toml` and the applicable architecture as authoritative. The commonly documented repository gate is:

```bash
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Use a more specific command scope when the governing document requires it.

Tests should cover model invariants, deterministic identity and ordering, service behavior, lineage, negative authority boundaries, missing or malformed evidence, unsupported and contradictory states, and persistence conflict behavior when in scope.

A passing quality gate does not independently establish architectural conformance, human approval, or certification.

## Change and operational discipline

Keep changes narrow and preserve unrelated work. Before completion, verify exact worktree scope, dependency direction, architecture conformance, excluded responsibilities, and quality-gate results.

Do not modify source content, authoritative data, preservation evidence, production state, or repository history unless explicitly requested and governed. Never infer authority to delete, deduplicate, move the only copy, change authoritative paths, redirect clients, clean sources, overwrite accepted evidence, release preservation retention, or operate against live authoritative data.

For assessment and diagnosis, use read-only inspection unless governed mutation is explicitly requested.
