# POE Storage Architecture Intent — Phase 6B

## Preservation Baseline Acceptance

**Document ID:** POE-STOR-Architecture-Intent-Phase-6B
**Status:** Proposed for architectural review
**Phase:** 6B — Preservation Baseline Acceptance
**Predecessor:** Phase 6A — Discovery, Inventory, and Preservation Baseline Evidence
**Implementation authorization:** Not granted by this document

---

## 1. Purpose

Phase 6B establishes the governed transition from independently verifiable
Phase 6A preservation evidence into explicitly authorized preservation
baselines.

Phase 6B does not migrate, reorganize, deduplicate, redirect, clean, delete, or
otherwise modify source content. It creates the governance boundary that must
exist before later storage-consolidation analysis and planning may consume a
preservation baseline.

The governing distinction is:

- Phase 6A produces evidence describing source reality.
- Phase 6B determines whether that evidence is sufficiently complete,
  internally consistent, policy-compliant, and explicitly authorized to become
  an accepted preservation baseline.

An accepted preservation baseline is an authorized analytical input. It is not
migration authority, redirection authority, cleanup authority, or destructive
authority.

---

## 2. Architectural Position

The Phase 6 preservation lifecycle is:

```text
Discovery
    ↓
Inventory Assembly
    ↓
Inventory Evidence
    ↓
Source Content Capture
    ↓
Content Integrity Evidence
    ↓
Preservation Baseline Composition
    ↓
Evidence Validation
    ↓
Acceptance Evaluation
    ↓
Human Authorization
    ↓
Accepted Preservation Baseline
    ↓
Later Classification and Planning
```

The first five stages are Phase 6A responsibilities.

Phase 6B begins with preservation-baseline composition and ends with durable,
immutable evidence that a preservation baseline has been accepted, rejected,
or superseded by an identified authority.

No Phase 6B result authorizes migration.

---

## 3. Governing Principles

Phase 6B shall conform to the following principles:

1. Architecture before implementation.
2. Evidence before authority.
3. Acceptance before migration.
4. Migration before client redirection.
5. Reconciliation before cleanup.
6. No destructive operation may be inferred from an analytical, validation,
   acceptance, planning, or migration result.
7. Duplicate detection must never imply duplicate deletion.
8. Baseline acceptance must never implicitly authorize migration.
9. Migration completion must never implicitly authorize source cleanup.
10. Every authority transition must be explicit, immutable, auditable, and
    independently verifiable.
11. Existing Phase 6A contracts shall be referenced and reused rather than
    duplicated unless an architectural correction is separately documented.
12. Domain models must not depend on services.
13. Services may consume immutable domain models.
14. Persistence must use canonical deterministic serialization, atomic
    replacement, SHA-256 evidence, idempotency, and explicit conflict handling.
15. Human authorization must be represented as evidence rather than inferred
    from successful automated evaluation.
16. Rejection and exception decisions must be retained with the same rigor as
    acceptance decisions.
17. No production implementation or commit is authorized until the relevant
    architecture-intent slice has passed review and quality gates.

---

## 4. Phase 6B Scope

### 4.1 Included capabilities

Phase 6B includes:

- preservation-baseline composition;
- evidence-reference assembly;
- evidence completeness validation;
- evidence digest validation;
- evidence reconciliation;
- schema compatibility evaluation;
- identity and source-root consistency evaluation;
- acceptance-policy evaluation;
- exception classification;
- explicit exception approval;
- human authorization;
- rejection recording;
- immutable acceptance-decision evidence;
- acceptance persistence;
- SHA-256 sidecars;
- idempotent publication;
- conflict detection;
- baseline lineage;
- baseline supersession;
- publication of an accepted-baseline reference for later phases;
- Phase 6B certification evidence.

### 4.2 Excluded capabilities

Phase 6B explicitly excludes:

- source-content modification;
- source restructuring;
- storage classification;
- retention-policy assignment for migrated content;
- NAS destination mapping;
- duplicate-candidate analysis;
- duplicate adjudication;
- migration-unit definition;
- migration-wave planning;
- migration execution;
- migration reconciliation;
- client redirection;
- source cleanup;
- duplicate deletion;
- source deletion;
- source archival authority.

These capabilities belong to later Phase 6 boundaries and require their own
explicit architecture and authority transitions.

---

## 5. Preservation Baseline Composition

### 5.1 Responsibility

Preservation-baseline composition assembles the evidence produced by Phase 6A
into a deterministic baseline candidate.

Composition does not determine whether evidence is valid or acceptable.
Composition records what evidence is being presented for evaluation.

### 5.2 Required evidence categories

A baseline candidate shall reference, as applicable:

- source identity records;
- source-device, source-volume, and source-root identity;
- discovery requests and results;
- discovery exceptions;
- assembled inventory;
- unsupported inventory-item evidence;
- persisted inventory evidence;
- inventory evidence digests;
- capture-session identity and state;
- source-content certifications;
- content-capture exceptions;
- independently generated content-integrity evidence;
- integrity evidence digests;
- reconciliation evidence;
- exception evidence;
- schema names and schema versions;
- evidence creation timestamps;
- evidence publication references.

### 5.3 Composition rules

Composition shall be:

- deterministic;
- read-only with respect to source content;
- based on immutable Phase 6A domain records;
- explicit about absent evidence;
- explicit about optional and non-applicable evidence;
- independent of acceptance policy;
- independent of human authorization;
- reproducible from the same ordered evidence inputs.

A composed baseline must not silently repair, reinterpret, or replace Phase 6A
evidence.

---

## 6. Evidence Validation

### 6.1 Responsibility

Evidence validation determines whether a composed baseline candidate is
internally verifiable and policy-evaluable.

Validation is analytical. It does not grant acceptance authority.

### 6.2 Mandatory validation dimensions

Validation shall evaluate at minimum:

- required evidence presence;
- evidence-reference resolvability;
- canonical evidence digest verification;
- SHA-256 sidecar verification;
- schema-name compatibility;
- schema-version compatibility;
- preservation-baseline identity consistency;
- source-device identity consistency;
- source-volume identity consistency;
- source-root identity consistency;
- capture-session identity consistency;
- discovery-to-inventory reconciliation;
- inventory-to-content-capture reconciliation;
- content-capture-to-integrity-evidence reconciliation;
- file and directory totals;
- captured-byte totals;
- certified-content totals;
- integrity success and failure totals;
- exception totals;
- unsupported-object totals;
- capture-session completion;
- source accessibility;
- evidence ordering and duplicate-reference conflicts;
- source-change observations during capture or verification.

### 6.3 Blocking conditions

The following conditions shall block strict baseline acceptance:

- missing mandatory evidence;
- missing or unreadable evidence references;
- evidence digest failure;
- sidecar mismatch;
- unreconciled totals;
- unexplained evidence duplication;
- content-integrity failure;
- inaccessible required source content;
- source identity mismatch;
- source-root mismatch;
- capture-session mismatch;
- source changes during capture or verification;
- unsupported filesystem objects not covered by explicit policy;
- incomplete capture sessions;
- incompatible schema versions;
- contradictory exception evidence;
- unresolved persistence conflicts.

A blocking condition may only be overridden when the acceptance mode permits
exceptions and an authorized human decision explicitly approves the specific
exception. Some conditions may be classified as non-overridable by policy.

---

## 7. Acceptance Evaluation

### 7.1 Responsibility

Acceptance evaluation applies deterministic policy to a completed validation
result.

Acceptance evaluation does not record human approval and does not publish an
accepted baseline.

### 7.2 Evaluation outcomes

The policy engine should support the following recommended outcomes:

- `ACCEPTABLE`
- `ACCEPTABLE_WITH_EXCEPTIONS`
- `PARTIAL`
- `REJECTED`

These outcomes are recommendations produced from evidence and policy. They are
not final authority decisions.

### 7.3 Acceptance modes

Phase 6B should support exactly four acceptance modes:

#### Strict acceptance

All mandatory evidence is present, verified, reconciled, compatible, and free
of unapproved blocking conditions.

#### Acceptance with approved exceptions

The baseline contains identified exceptions that policy allows an authorized
decision-maker to approve explicitly.

Each exception approval must be individually referenced and retained.

#### Partial-source acceptance

A defined subset of identified source roots is accepted while other source
roots remain excluded, incomplete, rejected, or pending.

Partial acceptance must identify the exact accepted scope and must never be
represented as environment-wide acceptance.

#### Pilot-baseline acceptance

A deliberately limited baseline is accepted for validating later analytical or
planning capabilities.

Pilot acceptance must identify its restricted purpose and scope. It must not be
represented as a complete preservation baseline.

### 7.4 Environment-wide acceptance

A later complete environment baseline should be represented as a distinct
accepted baseline that may supersede earlier pilot or partial baselines.

It should not mutate the identity or evidence of the earlier baseline.

---

## 8. Human Authorization

### 8.1 Responsibility

Human authorization converts an evaluative recommendation into an explicit
governance decision.

Automated success must never substitute for human authorization where policy
requires an accountable authority.

### 8.2 Required decision evidence

An authorization decision shall record:

- decision identity;
- baseline-candidate identity;
- validation-result identity;
- evaluation-result identity;
- decision outcome;
- acceptance mode;
- decision timestamp;
- decision authority identity;
- decision authority role or basis;
- accepted evidence references;
- approved exception references;
- rejected exception references;
- rejection reasons;
- scope limitations;
- retention obligations;
- supersession eligibility;
- decision rationale;
- schema identity and version.

### 8.3 Decision outcomes

Human authorization shall support:

- acceptance;
- acceptance with approved exceptions;
- partial-source acceptance;
- pilot acceptance;
- rejection.

A rejection decision is immutable evidence associated with the candidate
baseline. It does not transform the candidate into an accepted baseline.

---

## 9. Baseline Lifecycle and States

The recommended baseline lifecycle is:

```text
DRAFT
  ↓
VALIDATED
  ↓
AUTHORIZED
  ↓
SUPERSEDED
```

### DRAFT

Evidence references have been composed into a baseline candidate.

### VALIDATED

Evidence validation and acceptance evaluation have completed and produced
immutable results.

### AUTHORIZED

A human authority has explicitly accepted the baseline under a defined
acceptance mode.

### SUPERSEDED

A later authorized baseline has explicitly superseded the baseline for a
defined scope.

Rejection is not a lifecycle state. Rejection is an immutable authorization
decision attached to a baseline candidate.

This distinction preserves candidate lineage and avoids conflating evidence
state with decision outcome.

---

## 10. Accepted Preservation Baseline

Phase 6B should introduce a governance object distinct from the existing
Phase 6A preservation manifest.

The existing preservation manifest describes capture and preservation
evidence.

The accepted preservation baseline represents an authority transition over a
specific, validated evidence set.

These responsibilities must remain separate.

An accepted preservation baseline shall include or reference:

- baseline identity;
- accepted scope;
- acceptance mode;
- accepted evidence graph;
- validation result;
- evaluation result;
- authorization decision;
- approved exceptions;
- lineage;
- supersession status;
- canonical serialization metadata;
- publication digest;
- SHA-256 sidecar reference.

The accepted baseline must remain immutable after publication.

Corrections require a new decision or a superseding baseline rather than
in-place mutation.

---

## 11. Persistence and Publication

### 11.1 Canonical persistence

Acceptance evidence shall use:

- canonical deterministic serialization;
- stable field ordering;
- deterministic collection ordering;
- explicit schema identity and version;
- atomic file replacement;
- durable filesystem synchronization where required;
- SHA-256 digest generation;
- SHA-256 sidecar publication;
- independent digest verification;
- restrictive and intentional file permissions.

### 11.2 Idempotency

Republishing the same decision for the same baseline identity and canonical
content shall be idempotent.

The persistence layer must distinguish:

- identical replay;
- compatible retry;
- conflicting content for an existing identity;
- attempted mutation of an immutable accepted decision.

### 11.3 Conflict handling

A conflicting publication must fail explicitly.

It must not overwrite, merge, repair, or silently version an existing accepted
decision.

Conflict evidence should identify:

- target identity;
- existing digest;
- proposed digest;
- conflict timestamp;
- attempted operation;
- failure classification.

### 11.4 Publication boundary

Later phases shall consume a durable accepted-baseline reference rather than
reassembling or reevaluating Phase 6A evidence independently.

The publication boundary prevents downstream components from bypassing
Phase 6B authority.

---

## 12. Authority Boundaries

The following boundaries are mandatory:

### Baseline composition

May assemble evidence references.

May not validate, accept, migrate, redirect, or clean.

### Evidence validation

May verify evidence and reconciliation.

May not approve exceptions or grant authority.

### Acceptance evaluation

May apply deterministic policy.

May not represent a human decision.

### Human authorization

May accept, reject, or approve permitted exceptions.

May not perform migration or source modification.

### Acceptance persistence

May persist immutable decision evidence.

May not reinterpret or change the decision.

### Classification

May categorize accepted source content in a later phase.

May not authorize migration or deletion.

### Destination mapping

May propose target storage locations in a later phase.

May not move content.

### Duplicate analysis

May identify duplicate candidates in a later phase.

May not declare deletion authority.

### Migration-unit planning

May define controlled migration units in a later phase.

May not execute migration.

### Migration execution

May copy or move content only under separately granted execution authority.

May not authorize cleanup.

### Reconciliation

May verify migration results.

May not infer redirection or cleanup authority.

### Client redirection

Requires separate explicit authority after successful reconciliation.

### Source cleanup

Requires the final and most restrictive authority transition.

It must never be inferred from acceptance, migration, reconciliation, or
redirection success.

---

## 13. Recommended Phase 6B Slice Sequence

### 6B-1 — Preservation Baseline Composition

Define the immutable domain representation and deterministic composition of
Phase 6A evidence references.

No validation, authorization, or persistence authority.

### 6B-2 — Baseline Evidence Validation

Validate completeness, digests, identity consistency, schema compatibility,
and reconciliation.

Produce immutable validation evidence.

### 6B-3 — Acceptance Evaluation

Apply deterministic acceptance policy to validation results.

Produce an immutable recommendation without human authority.

### 6B-4 — Acceptance Authorization

Represent accountable human acceptance, exception approval, partial
acceptance, pilot acceptance, and rejection.

### 6B-5 — Acceptance Persistence

Persist authorization and accepted-baseline evidence using canonical
serialization, atomic replacement, SHA-256 sidecars, idempotency, and conflict
handling.

### 6B-6 — Accepted-Baseline Publication

Publish the durable accepted-baseline reference that later phases may consume.

Publication does not grant migration authority.

### 6B-7 — Phase 6B Certification

Verify architecture conformance, evidence integrity, negative controls,
authority boundaries, persistence behavior, lineage, supersession, and
operational closeout.

Each slice depends on the preceding slice and must receive architectural review
before production implementation.

---

## 14. Recommended Later Phase Boundaries

### Phase 6C — Classification and Destination Design

Recommended capabilities:

- storage classification;
- sensitivity and governance classification;
- retention-policy assignment;
- target storage policy;
- NAS destination mapping;
- placement constraints;
- destination conflict analysis.

Phase 6C consumes accepted baselines but does not authorize migration.

### Phase 6D — Duplicate Analysis and Migration Planning

Recommended capabilities:

- duplicate-candidate identification;
- duplicate evidence;
- duplicate adjudication planning;
- migration-unit definition;
- dependency analysis;
- migration-wave planning;
- rollback and reconciliation planning.

Duplicate analysis must not imply duplicate deletion.

### Phase 6E — Controlled Migration and Reconciliation

Recommended capabilities:

- authorized migration execution;
- migration evidence;
- destination verification;
- source-to-destination reconciliation;
- migration exception handling;
- rollback evidence;
- controlled client redirection after separate authorization.

Migration completion must not imply source cleanup authority.

### Final Phase 6 Certification and Cleanup Authority

Recommended capabilities:

- environment-wide reconciliation;
- client-redirection certification;
- preservation-retention verification;
- explicit source-cleanup authorization;
- cleanup execution evidence;
- final Phase 6 certification.

Source cleanup must remain the final, separately authorized destructive
transition.

---

## 15. Resolved Architectural Decisions

### Decision 1 — Phase 6B scope

**Decision:** Phase 6B contains preservation-baseline acceptance only.

**Rationale:** Combining acceptance with classification or migration planning
would weaken the authority boundary between verified evidence and downstream
analytical use.

### Decision 2 — Accepted baseline representation

**Decision:** Introduce an accepted preservation baseline as a governance
object distinct from the Phase 6A preservation manifest.

**Rationale:** Capture evidence and governance authorization have different
lifecycles, responsibilities, and mutation rules.

### Decision 3 — Acceptance modes

**Decision:** Support strict, approved-exception, partial-source, and pilot
acceptance.

**Rationale:** These modes cover complete, constrained, and incremental
adoption without creating ambiguous acceptance semantics.

### Decision 4 — Rejection representation

**Decision:** Represent rejection as an immutable decision record rather than a
baseline lifecycle state.

**Rationale:** The evidence candidate remains a draft baseline; rejection is a
governance decision about that candidate.

### Decision 5 — Supersession

**Decision:** Supersession creates explicit lineage between immutable accepted
baselines.

**Rationale:** Accepted evidence must not be mutated when a more complete or
newer baseline is authorized.

### Decision 6 — Downstream consumption

**Decision:** Later phases consume accepted-baseline references only.

**Rationale:** This prevents downstream services from bypassing Phase 6B
validation and authorization.

### Decision 7 — Migration authority

**Decision:** Baseline acceptance never grants migration authority.

**Rationale:** Acceptance certifies the preservation evidence set; migration
requires separate planning, authorization, execution, and reconciliation
controls.

---

## 16. Open Decisions for Slice-Level Architecture

The following decisions remain for the relevant Phase 6B slice documents:

1. Exact immutable model names and field contracts after direct inspection of
   all Phase 6A models and serializers.
2. Canonical accepted-baseline identifier derivation.
3. Evidence-reference ordering rules.
4. Required versus optional evidence by source type.
5. Overridable and non-overridable blocking-condition policy.
6. Acceptance authority identity mechanism.
7. Authority-role representation.
8. Persistence directory and file-naming conventions.
9. Locking and concurrent publication behavior.
10. Supersession-scope comparison rules.
11. Whether authorization signatures remain SHA-256 evidence only or later
    require cryptographic signing.
12. CLI and report surfaces, if any, for Phase 6B certification.

These decisions must be resolved before their corresponding implementation
slice begins.

---

## 17. Quality and Review Gates

Before any Phase 6B production implementation:

- the phase-level architecture must be approved;
- the relevant slice architecture-intent document must be approved;
- current repository contracts must be inspected directly;
- model-to-service dependency direction must be verified;
- canonical persistence patterns must be reused consistently;
- negative authority-boundary tests must be defined;
- no migration or cleanup behavior may enter scope;
- Ruff formatting and checks must pass;
- all existing tests must pass;
- new tests must pass;
- the worktree scope must match the approved slice;
- no commit may occur before architecture and implementation quality gates pass.

---

## 18. Approval Effect

Approval of this document authorizes preparation of the Phase 6B slice-level
architecture-intent documents.

It does not authorize production implementation, migration planning, migration
execution, client redirection, source cleanup, or any destructive operation.
