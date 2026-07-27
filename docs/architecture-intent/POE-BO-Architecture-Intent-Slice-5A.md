# POE Backup Orchestrator Architecture Intent — Slice 5A

## Restore Domain and Recovery-Point Discovery

**Document ID:** POE-BO-Architecture-Intent-Slice-5A  
**Phase:** Phase 5 — Restore Architecture and Governed Recovery Workflow  
**Slice:** 5A — Restore Domain and Recovery-Point Discovery  
**Status:** Approved for Implementation Planning  
**Baseline Date:** 2026-07-27  

---

## 1. Purpose

This document defines the architecture intent for Slice 5A of the POE Backup Orchestrator.

Slice 5A establishes the governed restore domain and the read-only discovery, inspection, and eligibility classification of Registry recovery points.

The slice does not restore, stage, validate, promote, replace, or roll back an authoritative Registry. Its purpose is to create the domain model, service boundaries, safety rules, evidence model, and operator-facing discovery surface required by all later Phase 5 restore capabilities.

The primary architectural objective is:

> Establish a deterministic and evidence-backed method for identifying which governed Registry backup packages may be considered recovery points.

---

## 2. Context

The POE Backup Orchestrator has completed and certified the following phases:

- Phase 1 — Repository Foundation
- Phase 2 — Repository Services
- Phase 3 — Governed Registry Backup Workflow
- Phase 4 — Production Runtime

The certified Phase 4 baseline provides:

- authoritative production runtime discovery,
- runtime validation,
- durable runtime-state persistence,
- exclusive execution ownership,
- restart and recovery inspection,
- interrupted-execution classification,
- lifecycle coordination,
- centralized production composition,
- runtime-state CLI inspection,
- runtime-aware operational acceptance,
- and formal certification evidence.

The system can produce governed Registry backup artifacts and associated evidence. It does not yet provide a governed method to determine which backup packages are suitable for recovery.

Repository presence alone is not sufficient evidence of recoverability.

---

## 3. Architectural Problem

A backup file may exist while being unsuitable for restore because it is:

- incomplete,
- missing its manifest,
- associated with a failed workflow,
- checksum-invalid,
- quarantined,
- incompatible,
- ambiguous in origin,
- unsupported by the current manifest contract,
- or otherwise inconsistent with recovery policy.

Without a restore-domain boundary, an operator could be forced to select recovery inputs by filename, path, timestamp, or assumption.

Slice 5A must eliminate that ambiguity.

The system must distinguish between:

- a file present in the repository,
- a governed backup package,
- an identified recovery point,
- an eligible recovery point,
- and a future staged restore candidate.

---

## 4. Governing Principles

### 4.1 Repository presence does not imply recovery eligibility

Every discovered package must be interpreted through governed metadata and policy.

### 4.2 Restore selection must be identity-based

Recovery points must be selected using a deterministic identifier rather than an arbitrary filesystem path or filename.

### 4.3 Discovery is read-only

Slice 5A must not modify:

- backup packages,
- manifests,
- repository state,
- runtime state associated with backup execution,
- restore workspaces,
- or the authoritative Registry.

### 4.4 Eligibility must be explicit

A recovery point must be classified as one of:

- eligible,
- conditionally eligible,
- ineligible,
- unknown.

No recovery point may be treated as eligible through omission or inference.

### 4.5 Evidence must be traceable

Every recovery-point result must retain sufficient information to trace it to:

- its source package,
- source backup execution,
- manifest,
- Registry identity,
- workflow result,
- and validation evidence.

### 4.6 Safety overrides convenience

Malformed, unsupported, conflicting, or ambiguous packages must be surfaced as such rather than silently ignored or accepted.

---

## 5. Scope

Slice 5A includes:

- authoritative recovery-point discovery boundaries,
- governed backup package enumeration,
- manifest loading and interpretation,
- recovery-point identity,
- backup execution linkage,
- Registry source identity,
- package metadata inspection,
- eligibility classification,
- unsupported-package handling,
- malformed-package handling,
- duplicate-identity detection,
- path-containment validation,
- read-only operator commands,
- discovery evidence,
- structured logging,
- unit tests,
- filesystem integration tests,
- CLI tests,
- and architecture-aligned acceptance criteria.

---

## 6. Exclusions

Slice 5A explicitly excludes:

- restoring a database,
- creating a restore workspace,
- copying backup artifacts,
- executing SQLite integrity checks against a staged candidate,
- application-level Registry validation,
- target locking,
- authoritative Registry replacement,
- promotion authorization,
- rollback artifact creation,
- rollback execution,
- destructive cleanup,
- retention mutation,
- quarantine mutation,
- unattended restore execution,
- and non-Registry recovery.

These capabilities belong to later Phase 5 slices.

---

## 7. Domain Terminology

### 7.1 Backup artifact

The Registry database artifact produced by a governed backup workflow.

### 7.2 Backup package

The governed collection of files and metadata representing one completed backup result.

A backup package may include:

- the Registry backup artifact,
- a manifest,
- checksums,
- reports,
- workflow evidence,
- and related metadata.

### 7.3 Recovery point

A discovered and identified backup package that can be evaluated as a potential source for restore.

A recovery point is not automatically eligible.

### 7.4 Eligible recovery point

A recovery point that satisfies all mandatory recovery eligibility rules.

### 7.5 Conditionally eligible recovery point

A recovery point that is not disqualified but requires an explicit operator override or policy exception before later restore staging.

### 7.6 Ineligible recovery point

A recovery point that violates a mandatory recovery requirement.

### 7.7 Unknown recovery point

A discovered package whose recovery status cannot be determined reliably.

### 7.8 Restore candidate

A future isolated database instance materialized from a selected recovery point.

Restore candidates are outside Slice 5A.

### 7.9 Restore execution

A future governed runtime execution that stages, validates, promotes, or rolls back a recovery point.

Restore execution behavior is outside Slice 5A.

### 7.10 Authoritative Registry

The configured live Registry database used as the current system of record.

Slice 5A must not modify it.

---

## 8. Recovery-Point Identity

Each recovery point must have a deterministic identity.

The identity model should use the strongest authoritative identifier already present in the governed backup package.

Preferred identity inputs include:

- source backup execution identifier,
- manifest identifier,
- source Registry identifier,
- backup creation timestamp,
- artifact checksum,
- and manifest version.

The architecture must avoid using filename alone as the recovery-point identity.

A recovery-point identifier must:

- be stable across repeated discovery operations,
- uniquely identify one governed package,
- be displayable to an operator,
- be suitable for future CLI selection,
- and support evidence correlation.

Duplicate identifiers must be treated as an architectural fault or package ambiguity, not silently deduplicated.

---

## 9. Authoritative Discovery Boundary

Recovery-point discovery must be restricted to configured and validated repository paths.

The discovery service must:

- begin from the production runtime’s authoritative repository configuration,
- reject paths outside the configured backup package boundary,
- reject path traversal,
- define symlink behavior explicitly,
- avoid following unexpected links by default,
- distinguish files from directories,
- and produce deterministic ordering.

Discovery must not scan arbitrary local or mounted filesystems.

The initial scope is limited to governed Registry backup packages created by the POE Backup Orchestrator.

---

## 10. Manifest Contract

The manifest is the primary semantic contract for recovery-point interpretation.

The Slice 5A architecture must define:

- supported manifest versions,
- required fields,
- optional fields,
- field types,
- timestamp format,
- checksum algorithm,
- artifact naming rules,
- source Registry identity,
- source backup execution identity,
- workflow outcome representation,
- verification status representation,
- and compatibility behavior.

A manifest must not be considered valid solely because it can be parsed.

Manifest validation must distinguish:

- unreadable,
- syntactically invalid,
- structurally invalid,
- semantically invalid,
- unsupported,
- and valid.

Unsupported manifest versions should normally yield an unknown or conditionally eligible classification, depending on explicit compatibility policy.

---

## 11. Recovery-Point Eligibility Model

### 11.1 Eligible

A recovery point may be classified as eligible only when all mandatory conditions pass.

Initial mandatory conditions should include:

- package boundary is valid,
- manifest is present,
- manifest is readable,
- manifest version is supported,
- required manifest fields are valid,
- backup artifact is present,
- source backup execution completed successfully,
- artifact checksum metadata is present,
- stored verification result meets policy,
- source Registry identity is acceptable,
- package is not quarantined,
- and no identity conflict exists.

Slice 5A may inspect previously recorded checksum and verification evidence.

It does not need to rehash the full artifact unless architecture review determines that read-only checksum revalidation is necessary at discovery time. Full execution-time package revalidation remains mandatory in Slice 5B.

### 11.2 Conditionally eligible

A recovery point may be conditionally eligible when:

- the package is structurally valid,
- no corruption is established,
- and a defined policy exception is required.

Examples may include:

- recovery point age exceeds the normal policy threshold,
- manifest version is older but explicitly recognized,
- recorded verification evidence is incomplete,
- or source software version requires operator review.

Every conditional result must include:

- condition code,
- explanatory message,
- and future override requirement.

### 11.3 Ineligible

A recovery point must be classified as ineligible when any mandatory recovery requirement fails.

Examples include:

- checksum mismatch recorded,
- backup workflow failure,
- missing artifact,
- missing manifest,
- invalid manifest,
- quarantined package,
- unsupported package structure,
- source identity conflict,
- duplicate recovery-point identity,
- or evidence of package mutation.

### 11.4 Unknown

A recovery point must be classified as unknown when the system cannot determine its status reliably.

Unknown is not equivalent to conditionally eligible.

Unknown packages must not proceed to staging without a future explicit resolution process.

---

## 12. Proposed Domain Models

The implementation should introduce domain models conceptually equivalent to:

### RecoveryPoint

Represents one discovered governed backup package.

Candidate fields:

- recovery_point_id,
- package_path,
- artifact_path,
- manifest_path,
- source_backup_execution_id,
- source_registry_id,
- created_at,
- artifact_size_bytes,
- artifact_sha256,
- manifest_version,
- backup_status,
- verification_status,
- quarantine_status,
- eligibility,
- eligibility_reasons,
- warnings.

### RecoveryPointEligibility

Represents the policy result.

Candidate fields:

- classification,
- reason_codes,
- warnings,
- override_required,
- evaluated_at,
- policy_version.

### RecoveryPointInspection

Represents the full read-only inspection result.

Candidate fields:

- recovery_point,
- package_findings,
- manifest_findings,
- identity_findings,
- policy_findings,
- evidence_references.

Exact implementation names may differ, but the domain distinctions must be preserved.

---

## 13. Proposed Service Responsibilities

### 13.1 RecoveryPointLocator

Responsibilities:

- enumerate candidate backup packages,
- enforce configured discovery boundaries,
- reject unsafe paths,
- and return deterministic package locations.

The locator must not interpret eligibility.

### 13.2 RecoveryPointManifestReader

Responsibilities:

- locate the expected manifest,
- read the manifest,
- parse supported formats,
- and return structured manifest data or explicit faults.

The reader must not classify policy eligibility.

### 13.3 RecoveryPointInspector

Responsibilities:

- inspect package structure,
- correlate artifact and manifest,
- validate package identity,
- detect inconsistencies,
- and assemble inspection findings.

### 13.4 RecoveryPointEligibilityEvaluator

Responsibilities:

- apply recovery eligibility policy,
- produce a classification,
- assign reason codes,
- identify warnings,
- and determine whether an override would be required.

### 13.5 RecoveryPointDiscoveryService

Responsibilities:

- orchestrate locator, reader, inspector, and evaluator behavior,
- return operator-ready results,
- preserve deterministic ordering,
- and emit discovery evidence.

### 13.6 RecoveryPointPresenter

Responsibilities:

- convert domain results into CLI-friendly representations,
- preserve machine-readable fields,
- and avoid embedding domain decisions in presentation logic.

---

## 14. Error and Finding Taxonomy

The implementation should distinguish operational errors from package findings.

### Operational errors

Examples:

- repository unavailable,
- configuration invalid,
- permission denied,
- runtime discovery failure,
- unexpected I/O failure.

Operational errors may prevent discovery from completing.

### Package findings

Examples:

- manifest missing,
- manifest invalid,
- artifact missing,
- duplicate identity,
- unsupported version,
- quarantine marker present,
- recorded checksum failure.

Package findings should normally produce a classified recovery-point result rather than aborting discovery of all other packages.

One malformed package must not prevent inspection of unrelated packages unless repository integrity is broadly compromised.

---

## 15. CLI Intent

Slice 5A should introduce a restore discovery command family.

Proposed commands:

```text
poe-backup-orchestrator restore list
poe-backup-orchestrator restore show --backup-id <recovery-point-id>
poe-backup-orchestrator restore evaluate --backup-id <recovery-point-id>
```

The final CLI syntax may be adjusted during implementation, but the following behavior is required.

### restore list

Displays discovered recovery points with concise fields such as:

- recovery-point identifier,
- created timestamp,
- age,
- source Registry,
- backup status,
- verification status,
- eligibility,
- and warning indicator.

### restore show

Displays complete inspection information for one recovery point.

### restore evaluate

Displays the explicit policy decision, reason codes, warnings, and future override requirement.

No Slice 5A command may:

- create a restore workspace,
- modify a backup package,
- modify runtime lifecycle state for a restore execution,
- or touch the authoritative Registry.

Machine-readable output should be considered for later implementation or included if consistent with the current CLI architecture.

---

## 16. Evidence and Logging

Discovery must produce evidence sufficient to reconstruct:

- when discovery occurred,
- which repository boundary was inspected,
- how many packages were found,
- which packages were classified,
- which packages produced warnings,
- which packages could not be interpreted,
- and which policy version was applied.

Logging must:

- use existing production logging composition,
- avoid exposing sensitive path details unnecessarily,
- preserve recovery-point identifiers,
- and distinguish warnings from failures.

Discovery evidence must not imply that a backup has been restored or independently validated as a staged database.

---

## 17. Security and Safety Requirements

The implementation must enforce:

- configured path containment,
- safe path normalization,
- no arbitrary operator-supplied package paths in the initial baseline,
- no implicit symlink traversal,
- no package mutation,
- no target writes,
- no filename-only trust,
- no automatic eligibility for unknown packages,
- and explicit handling of duplicate identities.

Manifest content must be treated as untrusted input.

The parser must not execute embedded content or resolve uncontrolled external references.

---

## 18. Runtime Integration

Slice 5A must use the existing production composition root.

It should reuse:

- runtime discovery,
- runtime validation,
- production configuration,
- repository path resolution,
- logging,
- and CLI composition.

Read-only discovery does not require a full restore execution lifecycle.

However, the design should not prevent later integration with:

- restore execution identifiers,
- durable restore state,
- exclusive runtime ownership,
- interrupted restore inspection,
- and promotion locks.

Where practical, domain interfaces should be designed so later slices can reuse the same recovery-point discovery services without CLI-specific coupling.

---

## 19. Test Strategy

### 19.1 Unit tests

Unit tests should cover:

- deterministic recovery-point identity,
- manifest parsing,
- supported and unsupported versions,
- eligibility rules,
- reason codes,
- conditional eligibility,
- ineligible classifications,
- unknown classifications,
- duplicate identity handling,
- path normalization,
- and presentation mapping.

### 19.2 Filesystem integration tests

Integration fixtures should include:

- one valid package,
- multiple valid packages,
- missing manifest,
- invalid manifest,
- missing artifact,
- unsupported manifest version,
- quarantined package,
- duplicate identifiers,
- unsafe symlink,
- path traversal attempt,
- unrelated repository files,
- and partial package directories.

### 19.3 CLI tests

CLI tests should prove:

- deterministic listing,
- successful inspection,
- successful evaluation,
- clear not-found behavior,
- classified malformed packages,
- repository failure handling,
- and no filesystem mutation.

### 19.4 Regression tests

Existing Phase 1–4 behavior must remain unchanged.

The full quality baseline must continue to pass:

- Ruff format,
- Ruff lint,
- pytest.

---

## 20. Acceptance Criteria

Slice 5A is complete when all of the following are true.

### AC-5A-01 — Authoritative boundary

Recovery-point discovery operates only within the configured governed Registry backup package boundary.

### AC-5A-02 — Deterministic discovery

Repeated discovery over unchanged repository content produces the same recovery-point identities and ordering.

### AC-5A-03 — Manifest interpretation

Supported manifests are parsed and validated through an explicit contract.

### AC-5A-04 — Explicit classification

Every discovered package receives an eligible, conditionally eligible, ineligible, or unknown classification.

### AC-5A-05 — Traceability

Every classified recovery point can be traced to its package, manifest, source backup execution, and source Registry identity where available.

### AC-5A-06 — Malformed-package isolation

A malformed package does not prevent unrelated packages from being discovered and classified.

### AC-5A-07 — Duplicate detection

Conflicting or duplicate recovery-point identities are detected and not silently collapsed.

### AC-5A-08 — Read-only operation

Discovery and inspection do not modify packages, repository state, restore workspaces, or the authoritative Registry.

### AC-5A-09 — Operator CLI

The operator can list, show, and evaluate recovery points through the production CLI.

### AC-5A-10 — Evidence

Discovery and eligibility findings are logged and represented with explicit reason codes.

### AC-5A-11 — Security

Unsafe paths, path traversal, and unexpected symlink behavior are rejected.

### AC-5A-12 — Quality baseline

All formatting, linting, unit, integration, and regression tests pass.

---

## 21. Deferred Decisions

The following decisions are intentionally deferred to later Phase 5 slices:

- restore workspace directory design,
- candidate materialization method,
- execution-time full checksum revalidation,
- SQLite integrity validation hierarchy,
- Registry application-level validation rules,
- promotion authorization mechanism,
- authoritative target lock implementation,
- rollback artifact retention,
- atomic replacement mechanics,
- interrupted promotion recovery,
- and end-to-end recovery certification.

Slice 5A interfaces should preserve flexibility for these decisions without implementing them prematurely.

---

## 22. Slice 5A Deliverables

The expected implementation deliverables are:

- approved architecture-intent document,
- recovery-point domain models,
- manifest contract,
- recovery-point locator,
- manifest reader,
- package inspector,
- eligibility evaluator,
- discovery service,
- CLI list/show/evaluate surface,
- structured reason codes,
- discovery evidence,
- unit tests,
- filesystem integration tests,
- CLI tests,
- and slice acceptance evidence.

---

## 23. Phase 5 Roadmap Context

The approved Phase 5 roadmap is:

```text
5A  Restore Domain and Recovery-Point Discovery
5B  Isolated Restore Staging
5C  SQLite and Application-Level Validation
5D  Existing-Target Protection and Controlled Promotion
5E  Rollback and Interrupted-Recovery Handling
5F  Operational Acceptance and Recovery Certification
```

Slice 5A establishes the source-of-truth recovery-point model required by every subsequent slice.

---

## 24. Architecture Decision Summary

The following decisions govern Slice 5A:

1. Phase 5 is designated Restore Architecture and Governed Recovery Workflow.
2. Direct overwrite of the authoritative Registry is prohibited.
3. Restore staging and promotion are separate governed operations.
4. Restore begins from a manifest-backed recovery point.
5. Recovery points are selected by deterministic identity.
6. Eligibility is explicit and policy-driven.
7. Discovery is read-only.
8. Unknown does not imply eligible.
9. Duplicate identity is an error condition.
10. Slice 5A precedes all restore implementation that changes filesystem or Registry state.

---

## 25. Approval Boundary

Approval of this architecture-intent document authorizes implementation planning and development for Slice 5A only.

It does not authorize:

- restore staging,
- database restoration,
- candidate validation,
- promotion,
- authoritative Registry replacement,
- or rollback.

Those capabilities require separate architecture and acceptance approval in later Phase 5 slices.
