# POE Storage Architecture Intent — Phase 6C

## Classification and Destination Design

**Document ID:** POE-STOR-Architecture-Intent-Phase-6C

**Status:** Proposed for architectural review

**Phase:** 6C — Classification and Destination Design

**Predecessor:** Certified and closed Phase 6B under `POE-STOR-PHASE-6B-CERT`

**Certified repository baseline:** `main` at `5ea1ccd26ec30937f0b2e7b18cb63cf1d646d994`

**Certified predecessor quality gate:** Ruff passing; 889 tests passing

**Implementation authorization:** Not granted by this document

---

## 1. Purpose

Phase 6C consumes an independently verified accepted-preservation-baseline
reference and produces governed, reviewable classification and
destination-design evidence for the authorized accepted scope.

The phase advances the preservation-governance pipeline from accepted evidence
to analytical recommendations and separately approved target design. It does
not migrate, restructure, redirect, clean, supersede, or otherwise alter source
or target storage.

The governing rule remains:

> We do not restructure the only copy of anything.

Phase 6C may describe and recommend future structure. It cannot alter the
accepted source or create later authority through analysis.

---

## 2. Architectural Context and Entry Gate

Phase 6B established and certified this boundary:

```text
AcceptedPreservationBaselineReference artifact pair
        ↓ independent verification
AcceptedPreservationBaseline
        ↓ accepted-evidence authentication
Phase 6C analytical context
```

Phase 6C begins only after all of the following are true:

1. Phase 6B certification is merged into `main`;
2. `main` and `origin/main` are synchronized;
3. the repository is clean; and
4. the authoritative accepted-baseline reference can be independently verified.

Those conditions are satisfied by the certified predecessor state recorded
above. They grant permission to design Phase 6C, not permission to implement a
slice or exercise any later authority.

Phase 6C inherits no migration, cleanup, redirection, duplicate-disposition,
retention-release, or supersession authority.

### 2.1 Conceptual Analytical Pipeline

```text
Accepted Preservation Baseline Reference
        ↓ independent verification
Accepted Preservation Baseline
        ↓
Accepted-Baseline Analytical Context — Slice 6C-1
        ↓
Classification Policy and Observations — Slice 6C-2
        ↓
Classification Findings and Result — Slice 6C-3
        ↓
Published Classification Evidence and Reference — Slice 6C-4
        ↓
Logical Information Architecture and Destination Recommendations — Slice 6C-5
        ↓
Human Classification and Target-Architecture Approval — Slice 6C-6
        ↓
Approved Classification and Target-Design Publication — Slice 6C-7
        ↓
Phase 6D Duplicate Analysis and Migration Planning
```

Each arrow represents a governed dependency, not an authority transfer. Verified
intake does not imply classification; classification does not imply human
approval; publication does not imply approval; approval does not imply migration
authority; destination recommendation does not authorize destination creation;
and Phase 6D analysis does not authorize migration execution or deletion.

---

## 3. Phase Responsibility

Phase 6C may:

- establish a verified analytical context;
- authenticate accepted evidence referenced by the verified accepted baseline;
- classify content through explicit deterministic policies;
- preserve unknown, ambiguous, insufficient-evidence, conflicting, unsupported,
  and review-required states;
- recommend ownership, stewardship, sensitivity, retention, lifecycle, recovery,
  indexing, and information-domain classifications;
- define a logical information architecture;
- recommend physical NAS destinations and placement constraints;
- obtain separate human approval for classification and target architecture; and
- publish immutable approved analytical evidence for later planning.

Phase 6C must not:

- construct migration units, dependencies, waves, runbooks, or plans;
- execute preservation or migration;
- create NAS directories or reservation files;
- create or modify Samba shares;
- redirect clients or applications;
- alter authoritative paths;
- treat duplicate observations as disposition or deletion authority;
- execute supersession or release preservation retention;
- authorize or perform cleanup;
- modify source content;
- access live source content unless separately authorized by later architecture;
- invoke external AI or LLM classification; or
- claim Phase 6 operational readiness.

---

## 4. Governing Input Contract

The certified Phase 6B entry method is:

```python
AcceptedPreservationBaselinePublisher.load_from_reference(
    reference_artifact: AcceptedPreservationBaselineArtifact,
) -> AcceptedPreservationBaseline
```

The Phase 6C public caller supplies exactly one
`AcceptedPreservationBaselineArtifact` representing the authoritative reference
JSON artifact and its SHA-256 sidecar. The artifact contract is a governed
locator and expected-value contract, not proof by itself.

Phase 6C services must not accept as substitutes:

- an already decoded `AcceptedPreservationBaselineReference`;
- an in-memory `AcceptedPreservationBaseline`;
- a caller-supplied full-baseline path;
- caller-supplied baseline, authorization, evaluation, validation, or candidate
  identity fields;
- caller-supplied digests, byte counts, or scope;
- a candidate, validation result, recommendation, or authorization decision
  directly; or
- live source-content paths.

Slice 6C-1 shall reuse the certified publisher verification method through an
explicit analytical-intake service. The wrapper establishes the analytical
boundary and adds accepted-evidence authentication; it must not duplicate,
weaken, or bypass the certified reference loader.

---

## 5. Reference-First Verification

Before analytical construction, the certified loader must verify:

- absolute artifact and sidecar paths;
- regular-file status and absence of symbolic links;
- reference artifact byte count and SHA-256;
- canonical two-space SHA-256 sidecar syntax;
- the exact sidecar filename and exactly one final newline;
- strict reference schema and canonical reference bytes;
- deterministic referenced full-baseline and sidecar filenames;
- full-baseline regular-file status and absence of symbolic links;
- full-baseline byte count, SHA-256, strict schema, and canonical bytes;
- accepted-baseline identity and its agreement with the reference;
- authorization, evaluation, validation, candidate, and original baseline lineage;
- accepted and excluded source-root scope;
- authorization conditions and pilot limitations;
- retention obligations; and
- supersession eligibility.

Any missing, malformed, linked, non-regular, noncanonical, contradictory, or
unverifiable state must fail before analytical-context construction. Successful
persistence or the existence of a filename must never be inferred as verification.

---

## 6. Accepted-Evidence Reopening Boundary

Phase 6C may reopen only evidence artifacts referenced by the independently
verified `AcceptedPreservationBaseline`. It must not reopen live source content.

Reopening is permitted only for analytical authentication and fact extraction
required by approved Phase 6C slices. It is constrained to:

- evidence observations for accepted source roots only;
- `PRESENT` observations where an artifact is required;
- the exact evidence and sidecar paths already carried by the accepted lineage;
- exact expected byte counts and SHA-256 values;
- exact sidecar syntax and filename;
- exact evidence type, schema identity, and source-root identity;
- canonical deserialization through governed loaders and adapters;
- deterministic, immutable adapter registration and resolution;
- no caller-supplied substitute path;
- no symbolic-link following;
- no mutation, repair, normalization, enrichment, or silent substitution; and
- explicit failed, absent, not-applicable, unsupported, inaccessible, and
  insufficient-evidence states.

The existing `FilesystemPreservationEvidenceLoader`, validation adapters, and
fact-extraction services are certified technical precedents. Their facts may be
authenticated inputs. They are not Phase 6C classification decisions and must
not be silently promoted into recommendations or approvals.

---

## 7. Accepted-Baseline Analytical Context

Slice 6C-1 introduces the first analytical object:

```python
AcceptedBaselineAnalysisContext
```

Recommended supporting contracts are:

- `STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION`;
- `AcceptedBaselineAnalysisContextIdentity`;
- `AcceptedBaselineAnalysisEvidence`;
- `AcceptedBaselineAnalysisContext`; and
- `stable_accepted_baseline_analysis_context_id`.

The context must be immutable, deterministic, lexically ordered where order is
not semantic, and constructed only after successful reference-first loading and
accepted-evidence authentication. It is a statement of verified analytical
inputs, not a classification, recommendation, approval, or plan.

For one accepted baseline and one exact analytical-intake semantic configuration,
there is exactly one valid analytical-context identity and one valid context.

Slice 6C-1 is computation-only and in-memory. It must not persist or publish the
context, perform classification judgment, or recommend a destination.

---

## 8. Semantic Identity

The analytical-context identity format is:

```text
pbac-<64 lowercase hexadecimal characters>
```

The digest is SHA-256 over the complete compact canonical semantic payload.
Identity must include at minimum:

- analysis-context schema version;
- accepted-baseline ID;
- analytical-intake profile ID and version;
- deterministic identity of the evidence-authentication policy or adapter
  registry;
- deterministic semantic representation of the complete authenticated accepted
  evidence set; and
- all semantic facts included in the context.

Identity must not be defined only from schema version and accepted-baseline ID.
Changing policy identity, authenticated evidence semantics, or context facts must
change the identity.

Exclude operational metadata from semantic identity, including:

- filesystem paths;
- artifact and sidecar digests used only for transport verification;
- byte counts used only for transport verification;
- loading or analysis timestamps;
- execution host;
- lock state;
- replay metadata;
- persistence destination; and
- temporary paths.

Paths, digests, and byte counts that establish lineage remain recorded evidence
even when they are excluded from the semantic identifier as operational metadata.
No timestamp or persistence location may make identical semantic analysis differ.

---

## 9. Complete Lineage

The analytical context must retain complete, immutable lineage to:

- the authoritative reference artifact contract;
- accepted-baseline ID, artifact digest, and byte count;
- authorization artifact digest and byte count;
- authorization ID;
- evaluation ID;
- validation ID;
- candidate ID;
- original baseline ID;
- accepted and excluded source roots;
- conditions and pilot constraints;
- retention obligations;
- supersession eligibility;
- accepted evidence observations;
- evidence type and schema identity;
- source-root ID;
- evidence and sidecar paths, digest, and byte count; and
- item-level provenance, including source device, volume, root, relative path,
  capture session, and inventory identity where present.

No analytical operation may erase, collapse, replace, or reinterpret provenance.
Excluded-root evidence must never leak into the accepted analytical set.

---

## 10. Classification Taxonomy Boundary

Phase 6C may define deterministic policies, descriptive observations, and
reviewable recommendations for:

- information domain;
- business or personal purpose;
- content type;
- project or system affiliation;
- authoritative status;
- lifecycle state;
- sensitivity and handling;
- retention requirement;
- recovery priority;
- backup policy;
- indexing eligibility;
- external-AI eligibility;
- ownership;
- stewardship;
- logical collection;
- destination domain; and
- quarantine or review state.

Unknown, unclassified, ambiguous, conflicting, insufficient-evidence,
unsupported, and review-required states are first-class values. They must not be
converted to defaults, inferred approvals, or fabricated answers.

Descriptive observations remain distinct from recommendations. Recommendations
remain distinct from human-approved assignments. Classification policies must be
deterministic, versioned, immutable, and independently identified.

Classification never implies deletion, duplicate disposition, migration,
cleanup, redirection, supersession, or operational authority.

---

## 11. Ownership, Sensitivity, and Retention

Ownership and stewardship outputs are recommendations until explicit human
approval. Ambiguous ownership must remain explicit and must not be assigned by a
convenience default.

Sensitivity and handling recommendations must be conservative, evidenced, and
reviewable. Unknown sensitivity must not be silently classified as low risk.

Retention recommendations may not weaken an inherited preservation or human-
authorization obligation. A shorter recommended duration does not override the
longer inherited obligation. No Phase 6C result or approval may release
preservation retention.

---

## 12. Duplicate and Equivalence Boundary

Duplicate and equivalence analysis, adjudication, canonical-copy recommendation,
and disposition planning are Phase 6D responsibilities.

Phase 6C may preserve hashes, provenance, and descriptive metadata needed later.
It may record an unadjudicated duplicate-relationship observation only when that
observation is explicitly non-authoritative.

A matching SHA-256 establishes evidence of byte equality only. It does not
authorize:

- equivalence beyond byte equality;
- canonical-copy designation;
- provenance collapse;
- deletion or deduplication;
- cleanup;
- migration; or
- supersession.

Every provenance chain remains explicit even for byte-identical content.

---

## 13. Logical Information Architecture

Phase 6C defines logical target design separately from physical placement.
Logical design may include:

- information domain;
- logical collection;
- ownership namespace;
- sensitivity zone;
- retention zone;
- lifecycle zone;
- recovery profile;
- backup profile;
- indexing eligibility; and
- quarantine or review zone.

Logical architecture outputs are recommendations until explicitly approved by a
human. Logical placement does not select a physical device path and cannot make a
location authoritative.

---

## 14. Physical Destination Recommendation

Physical destination recommendation is separate from logical classification. It
may recommend:

- physical storage root;
- NAS-relative path;
- naming constraints;
- collision findings;
- permissions profile;
- placement constraints; and
- required capacity or storage characteristics.

Recommendations must use safe, normalized-by-validation path components without
altering preserved source identities. Unsafe, absolute where relative is required,
empty, dot, dot-dot, traversal, ambiguous, conflicting, or colliding target
components fail closed or become explicit review findings as defined by the slice.

Phase 6C must not create directories, shares, or reservation files; mutate NAS
state; alter client-visible or authoritative paths; redirect clients; declare a
destination authoritative; or authorize migration. An approved destination
assignment still does not authorize migration.

---

## 15. Human Approval Boundaries

The governance model requires separately evidenced decisions for:

1. analytical evidence review;
2. classification approval;
3. ownership and stewardship approval;
4. retention and sensitivity approval;
5. target-architecture approval;
6. duplicate or equivalence disposition;
7. migration authorization;
8. client redirection;
9. cleanup authorization;
10. supersession; and
11. operational certification.

No approval implies another. Phase 6C may include classification and target-
architecture approval as its exit authorities. Duplicate disposition, migration,
redirection, cleanup, supersession, and operational certification remain later,
separately modeled and persisted decisions.

Automated analysis, persistence, passing tests, successful publication, or human
classification approval cannot create migration or destructive authority.

---

## 16. Persistence and Publication Architecture

Classification computation, finding and result assembly, persistence, human
approval, and final approved publication are separate responsibilities.

Slice 6C-1 is in-memory and must not persist an analysis context. Slice 6C-4 may
publish unapproved classification evidence and its authoritative reference, but
publication must not imply human approval. Slice 6C-7 publishes only explicitly
approved classification and target-design evidence.

Durable Phase 6C evidence shall reuse certified repository conventions:

- compact canonical UTF-8 JSON;
- lexically deterministic content;
- exactly one final newline;
- deterministic semantic identities;
- one full artifact with a SHA-256 sidecar;
- one lightweight authoritative reference with a SHA-256 sidecar;
- staged writes with file fsync;
- exclusive immutable placement and directory fsync after each final placement;
- restrictive permissions;
- one destination-scoped nonblocking lock;
- exact idempotent replay under the lock;
- complete four-file replay verification;
- fail-closed partial or contradictory state;
- cleanup limited to temporary and final files created by the failed attempt;
- no overwrite, repair, merge, normalization, silent replacement, or silent
  versioning; and
- causal exception preservation.

The eventual downstream boundary is an independently verified approved-
classification-and-target reference. A caller-supplied path, decoded reference,
or in-memory result cannot substitute for that artifact-pair verification.

Exact contract names, semantic payloads, filenames, locking scope, and replay
results for later publications must be approved in their slice architectures.

---

## 17. Failure Taxonomy

Phase 6C slice architectures must define typed failures covering, where relevant:

- reference verification failure;
- accepted-baseline loading failure;
- unsupported accepted-baseline schema;
- accepted-baseline identity mismatch;
- lineage or scope contradiction;
- missing required accepted evidence;
- evidence verification failure;
- unsupported evidence schema;
- evidence/source-root mismatch;
- invalid analytical-intake policy;
- policy or registry identity mismatch;
- ambiguous evidence-adapter registration;
- missing classification observation;
- conflicting classification;
- insufficient evidence;
- ambiguous ownership or retention;
- unsafe path component or traversal;
- target collision;
- forbidden authority escalation;
- persistence lock failure;
- partial publication; and
- immutable conflict.

Verification, identity, lineage, scope, schema, unsafe-path, authority-escalation,
and persistence conflicts fail closed. Analytical uncertainty normally becomes an
explicit unknown, ambiguous, insufficient-evidence, unsupported, or review-
required result rather than a fabricated answer.

The system must never silently normalize source identities, source-root IDs,
relative paths, provenance, hashes, accepted or excluded scope, ownership,
retention obligations, sensitivity, authoritative status, conflicts, or
unsupported states.

---

## 18. Security and Privacy Controls

Slice 6C-1 must not read live source content. It may read only the accepted
reference, its referenced accepted-baseline pair, and accepted evidence artifacts
under the verification controls in this architecture.

Any future content-inspection capability requires separately approved architecture
covering maximum bytes, streaming, binary data, malformed formats, inaccessible
files, sensitive data, privacy, temporary storage, extraction limits, failure
isolation, and audit evidence.

External AI or LLM classification is explicitly out of scope. Any future AI
classification is a separate governed integration requiring privacy and data-
egress controls, model governance, prompt and response retention rules,
deterministic fallback, security review, and explicit human approval.

Phase 6C requires no authentication, digital signatures, cloud services,
databases, external taxonomies, notifications, or new infrastructure. Paths must
be absolute at artifact boundaries; symlinks and non-regular artifacts fail
closed; target recommendations must reject traversal; and no Phase 6C service may
write source or live NAS content.

---

## 19. Negative Authority Invariants

The following statements are mandatory and testable:

- classification does not authorize migration;
- destination recommendation does not authorize destination creation;
- approved destination assignment does not authorize migration;
- duplicate detection does not authorize deletion;
- equivalence analysis does not erase provenance;
- migration completion does not authorize cleanup;
- supersession eligibility does not execute supersession;
- successful analysis does not establish operational readiness;
- analytical persistence does not imply human approval;
- human classification approval does not imply migration authority; and
- no Phase 6C output can restructure the only copy of anything.

No Phase 6C public model or service may expose migration execution, directory or
share creation, client redirection, cleanup, deletion, retention release, or
supersession-execution authority.

---

## 20. Approved Slice Sequence

### 20.1 Slice 6C-1 — Accepted-Baseline Analytical Intake and Evidence Authentication

Responsibility:

- independently load the accepted baseline from its authoritative reference;
- authenticate accepted evidence;
- construct one deterministic in-memory `AcceptedBaselineAnalysisContext`;
- preserve complete lineage and explicit authentication states; and
- perform no classification judgment, persistence, or destination recommendation.

### 20.2 Slice 6C-2 — Deterministic Classification Policy and Observation

Responsibility:

- define immutable, versioned, independently identified classification policy;
- produce deterministic observations and recommendations;
- preserve explicit unknown, ambiguity, conflict, and insufficiency states; and
- grant no human approval or later authority.

Persistence is excluded unless separately approved by this slice's architecture.

### 20.3 Slice 6C-3 — Classification Findings and Result Assembly

Responsibility:

- generate typed findings;
- compose a deterministic classification result;
- retain complete policy, evidence, scope, and baseline lineage; and
- prevent authority escalation.

### 20.4 Slice 6C-4 — Classification Evidence Persistence and Reference Publication

Responsibility:

- canonically serialize immutable classification evidence;
- publish a full artifact and authoritative reference with SHA-256 sidecars;
- enforce replay, locking, durability, permissions, partial-state, and immutable-
  conflict rules; and
- make no human approval claim.

### 20.5 Slice 6C-5 — Logical Information Architecture and Destination Recommendation

Responsibility:

- define logical target design;
- derive separately represented physical destination recommendations;
- record constraints and collisions; and
- create no destination, mapping authority, or migration authority.

### 20.6 Slice 6C-6 — Classification and Target-Architecture Human Approval

Responsibility:

- record separate explicit accountable-human approval;
- preserve authority, scope, conditions, rationale, decision timestamp, and
  complete lineage; and
- grant no migration, redirection, cleanup, or supersession authority.

### 20.7 Slice 6C-7 — Approved Classification and Target-Design Publication

Responsibility:

- publish immutable approved analytical evidence;
- publish the authoritative independently verifiable downstream reference;
- retain all approval and analytical lineage; and
- grant no migration authority.

### 20.8 POE-STOR-PHASE-6C-CERT — Phase 6C Closeout and Certification

Responsibility:

- use synthetic, isolated evidence to certify the Phase 6C software-governance
  boundary end to end;
- establish traceability, replay, conflict, and negative-authority evidence;
- require explicit human certification and closeout; and
- make no production migration, cleanup, or operational-readiness claim.

Each slice requires its own approved architecture and explicit implementation
authorization. Completion or approval of one slice does not authorize the next.

---

## 21. Later Phase Boundaries

Phase 6D owns duplicate-candidate and equivalence analysis, provenance-preserving
canonical-copy recommendations, migration-unit definition, dependency analysis,
migration grouping and waves, migration planning, and rollback and reconciliation
planning. Phase 6D analysis still cannot authorize deletion or execute migration.

Phase 6E, or another later separately approved phase, owns explicit migration
authorization, non-destructive copy execution, destination verification,
reconciliation, exception handling, and controlled redirection only after separate
authorization. Migration completion does not authorize cleanup.

Source cleanup remains the final separately authorized destructive transition. It
requires preservation, verified target copies, reconciliation, recovery controls,
representative restore evidence, explicit cleanup authorization, and retained
audit evidence. Supersession and retention release remain separate governed
transitions.

---

## 22. Parent-Level Testing Expectations

Phase 6C tests must cover, as applicable to each slice:

- immutable models and exact input types;
- deterministic semantic and policy identities;
- canonical ordering and repeated construction;
- complete lineage and accepted-only scope;
- explicit unknown, unsupported, insufficient, ambiguous, and conflicting states;
- reference-first loading and full-baseline verification;
- accepted-evidence authentication and source-root/schema consistency;
- no live source-content access and no input mutation;
- malformed, noncanonical, linked, non-regular, missing, and contradictory
  reference, sidecar, baseline, and evidence artifacts;
- incorrect filenames, byte counts, digests, sidecar syntax, schema, identities,
  scope, and lineage;
- excluded-root leakage and missing accepted evidence;
- ambiguous adapter registration and policy mismatch;
- classification conflict, ambiguity, and conservative retention behavior;
- unsafe target components, traversal, and collisions;
- persistence first publication, exact replay, nonblocking lock contention,
  partial state, immutable conflicts, permissions, durability, cleanup, and
  publication order where persistence is in scope;
- duplicate-analysis and provenance boundaries;
- absence of directory/share creation, migration plans and execution, redirection,
  cleanup, supersession execution, and external-AI surfaces; and
- package dependency direction and only explicitly approved exports.

The full repository quality gate is:

```bash
source .venv/bin/activate
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Before commit, also run:

```bash
git diff --cached --check
```

Passing tests do not substitute for architecture review, human approval, or phase
certification.

---

## 23. Phase 6C Certification Implications

`POE-STOR-PHASE-6C-CERT` must eventually prove:

- reference-first analytical intake;
- independent accepted-evidence authentication;
- deterministic classification and policy identity;
- explicit unknown and conflict handling;
- immutable classification publication and authoritative reference verification;
- logical target design and separate physical destination recommendation;
- separate human classification and target-architecture approval;
- approved analytical reference publication;
- end-to-end identity, scope, policy, approval, and provenance lineage;
- idempotent replay and immutable conflict behavior;
- no source mutation, destination creation, migration, cleanup, supersession
  execution, external AI, or unapproved integration; and
- explicit accountable-human phase certification and closeout.

Certification should use synthetic isolated evidence and cannot claim that a real
production classification, target design, migration, restore, cleanup, or Phase 6
operational readiness has been achieved.

---

## 24. Historical and Architectural Discrepancies

The repository preserves the following discrepancies rather than rewriting prior
documents or Git history:

1. The older Phase 6 roadmap names classification and target architecture as Phase
   6B and controlled migration as Phase 6C. The later approved Phase 6B parent
   architecture, certified implementation sequence, Phase 6B certification, and
   current human approval establish Phase 6C as Classification and Destination
   Design, Phase 6D as Duplicate Analysis and Migration Planning, and Phase 6E as
   Controlled Migration and Reconciliation.
2. The Phase 5 certification report repeats the older roadmap numbering. It remains
   historical and does not override later Phase 6 architecture.
3. The Phase 6B parent architecture used conceptual accepted-reference wording.
   The implemented and certified public entry type is
   `AcceptedPreservationBaselineArtifact`, supplied to
   `AcceptedPreservationBaselinePublisher.load_from_reference`; the decoded
   `AcceptedPreservationBaselineReference` is not caller input.
4. Existing validation adapters expose technical verification facts rather than
   Phase 6C classification domain models. Phase 6C may reuse authenticated facts but
   must introduce its own approved analytical contracts.
5. Historical Slice 6B-7 and 6B-8 identifiers belong to validation finding
   generation and validation result assembly. Phase 6B certification was correctly
   assigned the phase-level identifier `POE-STOR-PHASE-6B-CERT`.
6. Some completed slice documents retain implementation-review or proposal status.
   The Phase 6B certification record and certified Git history are authoritative
   for completed Phase 6B state; historical documents remain unchanged.
7. Phase 6A has no dedicated phase closeout record. Its implemented evidence
   contracts were traced and exercised by Phase 6B certification, but this does not
   manufacture a separate Phase 6A closeout.
8. Production-baseline acceptance and representative restore certification required
   by the preservation standard remain deferred. Phase 6B certified the software
   governance boundary, not a real production baseline.

---

## 25. Approved Deferrals

The following remain outside Phase 6C unless a future architecture explicitly
changes their boundary:

- live source-content inspection;
- external AI or LLM classification;
- duplicate and equivalence adjudication;
- canonical-copy recommendation;
- migration-unit and wave definition;
- migration planning and execution;
- NAS consolidation;
- directory and share creation;
- client redirection;
- cleanup authorization and execution;
- supersession records and execution;
- preservation-retention release;
- production-baseline acceptance;
- representative restore validation;
- final Phase 6 operational certification;
- authentication and digital signatures; and
- cloud or other external integrations.

These are explicit deferrals, not hidden capabilities and not omissions that a
Phase 6C implementation may fill opportunistically.

---

## 26. Exact Worktree Scopes

The architecture-only scope authorized for preparation and review of this document
is exactly:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Phase-6C.md
```

No Slice 6C-1 architecture or implementation is authorized by this document.

The proposed later Slice 6C-1 implementation scope is:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C1.md
src/poe_backup_orchestrator/models/storage_baseline_analysis.py
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/storage_baseline_analysis.py
src/poe_backup_orchestrator/services/__init__.py
tests/unit/test_storage_baseline_analysis_models.py
tests/unit/test_storage_baseline_analysis.py
```

That scope is a planning boundary only. It requires separately approved Slice 6C-1
architecture and explicit implementation authorization.

---

## 27. Recommended Governance Sequence

1. Review and approve this Phase 6C parent architecture.
2. Prepare Slice 6C-1 architecture from the certified Phase 6B contracts and this
   parent boundary.
3. Review and explicitly approve the Slice 6C-1 architecture.
4. Grant explicit implementation authorization for its exact worktree scope.
5. Implement only reference-first intake, evidence authentication, and in-memory
   deterministic context construction.
6. Run focused tests and the full repository quality gate.
7. Verify exact worktree scope, dependency direction, and excluded authorities.
8. Obtain human implementation approval before commit, publication, and integration.
9. Repeat architecture-first governance separately for every later slice.
10. Conduct phase-level certification only after all approved Phase 6C slices are
    integrated and independently reviewable.

---

## 28. Acceptance Criteria for This Parent Architecture

This architecture is acceptable for approval when it:

1. establishes the certified reference-first Phase 6B entry boundary;
2. prevents callers from bypassing reference and full-baseline verification;
3. limits evidence reopening to accepted, referenced, independently authenticated
   artifacts and excludes live source content;
4. defines an immutable deterministic `AcceptedBaselineAnalysisContext` whose
   identity covers the complete semantic analytical configuration;
5. preserves full lineage, accepted scope, conditions, retention, and supersession
   eligibility;
6. separates observations, recommendations, human approvals, publication, planning,
   execution, redirection, cleanup, supersession, and certification;
7. preserves explicit uncertainty and prohibits fabricated defaults;
8. separates logical information architecture from physical destination
   recommendation and both from destination creation or migration;
9. defers duplicate and equivalence authority to Phase 6D;
10. defines the seven-slice sequence and phase-level certification boundary;
11. establishes persistence, security, failure, testing, and negative-authority
    expectations without prematurely designing slice-level contracts;
12. records discrepancies and deferrals without rewriting history; and
13. grants no implementation or operational authority.

---

## 29. Unresolved Decisions Reserved for Slice Architecture

No unresolved decision blocks review of this parent architecture. The following
details are intentionally reserved for separate slice-level architecture and human
approval:

- exact Slice 6C-1 intake profile fields, schema version, policy/registry identity,
  authenticated-evidence fact schema, error names, and context construction API;
- exact Phase 6C classification vocabulary, rule precedence, confidence or evidence
  representation, and policy versioning contract;
- exact classification result, finding, persistence, and reference identities and
  filenames;
- exact logical and physical target-design models, collision policy, and safe-path
  grammar;
- exact human approval outcomes, authority contract, exception handling, and
  persistence boundary;
- exact approved-publication contracts and authoritative downstream reference; and
- the controlled Phase 6C certification procedure and evidence record.

These details must not be inferred during implementation. Each requires the
applicable architecture review and explicit human approval.

---

## 30. Architectural Decision

Phase 6C is a multi-slice analytical and governance phase titled:

```text
POE Storage Architecture Intent — Phase 6C
Classification and Destination Design
```

It begins exclusively from one independently verified authoritative accepted-
baseline reference artifact pair. It authenticates only accepted referenced
evidence, builds deterministic analytical context, produces reviewable
classification and target-design evidence, obtains separate human approval, and
publishes an immutable authoritative reference for later planning.

It grants no duplicate disposition, migration, destination creation, redirection,
cleanup, retention-release, supersession-execution, destructive, or operational-
readiness authority.

This document is proposed for architectural review. Implementation authorization
is not granted. No Phase 6C slice may begin until this parent architecture and the
applicable slice architecture are separately approved and explicit implementation
authorization is granted.
