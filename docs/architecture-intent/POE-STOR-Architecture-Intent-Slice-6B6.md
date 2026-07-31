# POE Storage Architecture Intent — Slice 6B-6

## Accepted Preservation Baseline Construction and Publication

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B6
**Status:** Approved architecture; implementation in review
**Phase:** 6B — Preservation Baseline Acceptance
**Slice:** 6B-6 — Accepted Preservation Baseline Construction and Publication
**Predecessor:** Slice 6B-5 — Preservation Baseline Authorization Persistence
**Certified predecessor repository state:** `8314448762e36983d66d7b94a94b742fde4bf0d5`
**Certified predecessor quality gate:** Ruff passing; 821 tests passing
**Implementation authorization:** Granted by explicit human approval

---

## 1. Purpose

Slice 6B-6 establishes the final Phase 6B authority-publication boundary before
later classification and planning.

It independently verifies one persisted human-authorization decision,
deterministically constructs the corresponding immutable accepted preservation
baseline, and durably publishes both the complete accepted-baseline evidence and
the lightweight reference that later phases are permitted to consume.

The accepted baseline is an authoritative analytical input. It grants no
migration, client-redirection, cleanup, supersession-execution, or destructive
authority.

---

## 2. Architectural Context

The governed pipeline entering this slice is:

```text
Discovery
→ Inventory Assembly
→ Inventory Evidence
→ Source Content Capture
→ Content Integrity Evidence
→ Baseline Candidate Formation
→ Validation
→ Acceptance Evaluation
→ Human Authorization
→ Authorization Persistence
```

Slice 6B-5 ends with one exact
`PreservationBaselineAuthorizationDecision` stored as canonical immutable
evidence with a SHA-256 sidecar. Successful persistence does not itself create
an accepted baseline.

Slice 6B-6 extends the pipeline only as follows:

```text
Authorization Persistence
→ Independent Persisted-Authorization Verification
→ Accepted-Baseline Construction
→ Accepted-Baseline Artifact Publication
→ Accepted-Baseline Reference Publication
```

The existing Phase 6A `PreservationBaselineManifest` remains capture and
preservation evidence. It is not the accepted governance object introduced by
this slice and must not be reused as one.

---

## 3. Exact Slice Responsibility

Slice 6B-6 shall:

1. accept one `PreservationBaselineAuthorizationPersistenceResult` as the
   locator and expected-value contract for persisted authorization evidence;
2. independently reload and verify the referenced authorization artifact and
   SHA-256 sidecar;
3. reconstruct the exact typed
   `PreservationBaselineAuthorizationDecision` from canonical stored bytes;
4. reject an unverifiable, malformed, conflicting, or rejected authorization;
5. deterministically construct exactly one immutable
   `AcceptedPreservationBaseline` from the verified authorization;
6. publish the full accepted-baseline JSON artifact and SHA-256 sidecar;
7. publish a lightweight `AcceptedPreservationBaselineReference` JSON artifact
   and SHA-256 sidecar last; and
8. return an immutable publication result that distinguishes first publication
   from verified identical replay.

The core one-to-one invariant is:

> The `AcceptedPreservationBaseline` is a deterministic projection of exactly
> one independently verified authorization decision.

For one semantic `authorization_id`, there exists exactly one valid
`accepted_baseline_id` and exactly one valid `AcceptedPreservationBaseline`.

No additional caller input may alter this projection.

---

## 4. Included Scope

This slice includes:

- strict persisted-authorization artifact and sidecar verification;
- strict typed deserialization of the exact persisted authorization decision;
- canonical-byte verification through deterministic reserialization;
- authorization-outcome eligibility enforcement;
- deterministic accepted-baseline identity derivation;
- accepted and excluded scope projection;
- accepted evidence-graph projection;
- preservation of conditions, pilot constraints, retention obligations, and
  supersession eligibility;
- full candidate, validation, evaluation, authorization, and persistence
  lineage;
- canonical serialization of the full accepted baseline and its reference;
- deterministic identity-derived filenames;
- SHA-256 sidecar creation and independent replay verification;
- synchronized, restrictive, exclusive placement;
- locking, concurrency control, idempotent replay, immutable conflicts, and
  attempt-scoped cleanup;
- public model and service exports approved by this document; and
- focused model, verification, construction, publication, durability,
  concurrency, failure, and negative-authority tests.

---

## 5. Explicit Exclusions and Deferred Responsibilities

Slice 6B-6 excludes:

- reevaluation of technical validation;
- reevaluation of acceptance policy;
- alteration, repair, normalization, enrichment, or reinterpretation of the
  human authorization decision;
- inference of acceptance from successful authorization persistence;
- expansion or contraction of authorized source-root scope;
- creation of an accepted baseline from a rejection;
- mutation of existing Phase 6A or Phase 6B evidence;
- supersession-scope comparison;
- creation or execution of a supersession decision or record;
- mutation or invalidation of a prior accepted baseline or reference;
- content classification or retention-policy assignment;
- target architecture or final NAS destination mapping;
- duplicate adjudication or deletion authority;
- migration-unit, wave, rollback, or execution planning;
- preservation or migration execution;
- NAS consolidation;
- client redirection;
- cleanup authorization or execution;
- deletion, deduplication, restructuring, renaming, replacement, or modification
  of source content;
- operational or Phase 6B certification;
- CLI commands, bootstrap integration, or configuration changes;
- digital signatures, authentication, identity-provider integration,
  notifications, or external integrations; and
- a generic persistence, serialization, registry, or publication framework.

These exclusions remain separately governed later responsibilities.

---

## 6. Input Contract

The public construction-and-publication entry point consumes exactly one:

```text
PreservationBaselineAuthorizationPersistenceResult
```

The result supplies:

- expected `authorization_id`;
- expected `baseline_id`;
- authorization artifact path;
- authorization sidecar path;
- expected authorization artifact SHA-256;
- expected authorization artifact byte count; and
- prior persistence replay metadata, which has no semantic effect here.

The persistence result is a locator and expected-value contract. It is not
accepted as proof that the referenced bytes remain valid.

The service must not accept:

- an in-memory `PreservationBaselineAuthorizationDecision` by itself;
- generic dictionaries or mappings;
- untyped decoded JSON;
- separately supplied identity, scope, mode, lineage, or digest fields;
- caller-supplied accepted-baseline content;
- caller-supplied final filenames; or
- successful persistence state as an acceptance outcome.

Persisted-authorization verification is an internal service concern. This slice
must not introduce or export a public
`VerifiedPreservationBaselineAuthorizationEvidence` model. Any internal verified
representation must remain private to the service module and must not become an
alternative public input contract.

---

## 7. Persisted-Authorization Verification

Before construction, the service must independently:

1. require absolute artifact and sidecar paths already enforced by the input
   contract;
2. require the deterministic authorization filename associated with the
   expected `authorization_id`;
3. reject symbolic links and other non-regular targets;
4. require both artifact and sidecar to exist;
5. read the exact artifact bytes without mutation;
6. verify the exact byte count against the persistence result;
7. calculate SHA-256 over the exact stored bytes;
8. require agreement among the calculated digest, persistence-result digest,
   and sidecar digest;
9. require the governed two-space SHA-256 sidecar format and exact filename;
10. strictly decode the canonical JSON using only the fields and types of the
    existing governed authorization dataclasses;
11. reject unknown, missing, duplicated, malformed, or incorrectly typed
    content;
12. instantiate the exact typed
    `PreservationBaselineAuthorizationDecision` and all nested contracts;
13. require the existing model invariants to validate semantic identity and
    lineage;
14. require the decoded `authorization_id` and `baseline_id` to equal the
    persistence result; and
15. canonically reserialize the typed decision using the certified Slice 6B-5
    serializer and require byte-for-byte equality with the stored artifact.

Verification must not repair, normalize, supplement, or rewrite the evidence.
This slice does not reopen or reevaluate underlying Phase 6A evidence; the exact
nested validation result remains the governed technical-validation evidence.

---

## 8. Eligible Authorization Outcomes

The exact mapping is:

| Authorization outcome | Construction eligibility | Accepted-baseline mode |
|---|---:|---|
| `AUTHORIZE` | Eligible | `STRICT` |
| `AUTHORIZE_WITH_EXCEPTIONS` | Eligible | `APPROVED_EXCEPTIONS` |
| `AUTHORIZE_PARTIAL_SCOPE` | Eligible | `PARTIAL_SOURCE` |
| `AUTHORIZE_PILOT` | Eligible | `PILOT` |
| `REJECT` | Ineligible | None |

`REJECT` remains immutable authorization evidence associated with its candidate.
It must produce no accepted-baseline artifact, reference, sidecar, temporary
publication file, or publication result.

Outcome interpretation is a fixed mapping, not policy reevaluation.

---

## 9. Output Contracts

### 9.1 `AcceptedPreservationBaseline`

The full immutable governance object must contain or directly preserve:

- accepted-baseline schema version and semantic identity;
- baseline, candidate, validation, evaluation, and authorization identities;
- the exact verified `PreservationBaselineAuthorizationDecision`;
- authorization artifact SHA-256 and byte count as lineage evidence;
- accepted-baseline mode;
- exact accepted and excluded source-root IDs;
- exact scope limitations;
- the accepted evidence graph;
- exact approved condition decisions and exception evidence;
- pilot purpose and limitations when applicable;
- retention obligations;
- `supersession_eligible`; and
- immutable lineage to every preceding governance stage.

### 9.2 `AcceptedPreservationBaselineReference`

The lightweight immutable downstream contract must contain:

- reference schema version;
- `accepted_baseline_id`;
- `baseline_id` and `authorization_id`;
- accepted-baseline mode;
- exact accepted and excluded source-root IDs;
- accepted-baseline artifact filename;
- accepted-baseline sidecar filename;
- accepted-baseline artifact SHA-256; and
- accepted-baseline artifact byte count.

The reference must use plain sibling filenames rather than persisted absolute
filesystem paths. It must not contain a redundant semantic `reference_id`.
Its exact serialized bytes receive their own publication digest and sidecar.

### 9.3 `AcceptedPreservationBaselineArtifact`

The filesystem artifact contract should bind one artifact path, sidecar path,
SHA-256 digest, and byte count. The same typed contract may represent the full
artifact and reference artifact when their roles remain explicit in the
publication result.

### 9.4 `AcceptedPreservationBaselinePublicationResult`

The operational result must contain:

- `accepted_baseline_id`;
- `baseline_id` and `authorization_id`;
- full accepted-baseline artifact metadata;
- reference artifact metadata; and
- `idempotent_replay`.

The result is not a third durable semantic record and grants no later authority.

---

## 10. Model, Service, and Module Naming

The approved model module is:

```text
src/poe_backup_orchestrator/models/storage_accepted_baseline.py
```

Approved public model contracts are:

- `STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION`;
- `AcceptedPreservationBaselineMode`;
- `AcceptedPreservationBaselineIdentity`;
- `AcceptedPreservationBaseline`;
- `AcceptedPreservationBaselineReference`;
- `AcceptedPreservationBaselineArtifact`;
- `AcceptedPreservationBaselinePublicationResult`; and
- `stable_accepted_preservation_baseline_id`.

The approved service module is:

```text
src/poe_backup_orchestrator/services/storage_accepted_baseline.py
```

Approved public services are:

- `AcceptedPreservationBaselineConstructor`;
- `AcceptedPreservationBaselineSerializer`; and
- `AcceptedPreservationBaselinePublisher`.

Approved public failures are:

- `AcceptedPreservationBaselineError`;
- `PersistedAuthorizationVerificationError`;
- `AcceptedPreservationBaselineConstructionError`;
- `AcceptedPreservationBaselinePublicationError`;
- `AcceptedPreservationBaselineConflictError`; and
- `AcceptedPreservationBaselineLockError`.

Persisted-authorization loading, strict decoding, and its verified intermediate
representation remain private implementation details in the service module.

---

## 11. Accepted-Baseline Semantic Identity

The accepted-baseline identity format is:

```text
pab-<sha256>
```

The digest is calculated from compact, canonical semantic JSON containing:

- accepted-baseline schema version;
- `authorization_id`;
- `baseline_id`;
- `candidate_id`;
- `validation_id`;
- `evaluation_id`;
- accepted-baseline mode;
- accepted source-root IDs;
- excluded source-root IDs;
- scope limitations;
- ordered approved condition decisions;
- pilot purpose and limitations, when present;
- retention obligations; and
- `supersession_eligible`.

The model-enforced canonical ordering of each governed collection must be
preserved. Identity derivation must not silently sort, deduplicate, or normalize
invalid caller content outside those certified model invariants.

The semantic identity excludes:

- authorization `decided_at_utc`;
- candidate, validation, construction, or publication timestamps;
- filesystem paths and filenames;
- artifact byte counts;
- authorization artifact digest;
- accepted-baseline artifact digest;
- reference artifact digest;
- sidecar paths or digests;
- lock or temporary-file metadata; and
- first-publication or replay state.

The one-to-one model invariant must recalculate the stable `pab-` identity from
the exact decision projection and reject disagreement. The constructor must not
accept any independent semantic field capable of producing a second accepted
baseline for the same `authorization_id`.

---

## 12. Identity and Digest Distinctions

The following meanings must remain separate:

| Value | Meaning |
|---|---|
| `authorization_id` (`pbd-…`) | Semantic identity of the human authorization decision |
| Authorization artifact SHA-256 | Integrity identity of the exact persisted authorization bytes |
| `accepted_baseline_id` (`pab-…`) | Semantic identity of the accepted-baseline projection |
| Accepted-baseline artifact SHA-256 | Integrity identity of the exact full-baseline publication bytes |
| Reference artifact SHA-256 | Integrity identity of the exact downstream-reference bytes |

No persistence digest replaces a semantic identity. No semantic identity proves
that a filesystem artifact remains intact without independent digest
verification.

---

## 13. Scope and Evidence-Graph Projection

Accepted and excluded source-root IDs must be copied exactly from
`AuthorizationScope`.

For every accepted root, the accepted evidence graph must retain the candidate
observations and evidence references belonging to that root in their existing
canonical order. Present, absent, and not-applicable observations retain their
exact certified meanings.

Excluded roots must remain explicit in the accepted-baseline scope. Their full
candidate and decision history remains independently available through the
embedded authorization lineage. Excluded roots must not be represented as
accepted evidence.

Construction must fail if:

- an accepted or excluded root is omitted or added;
- accepted and excluded roots overlap;
- the two sets do not account for the candidate scope;
- an accepted evidence observation belongs to an excluded or unknown root;
- an accepted-root observation is silently omitted; or
- projection would require evidence repair or policy reinterpretation.

---

## 14. Conditions, Pilot Limits, Retention, and Supersession Eligibility

The full accepted baseline must retain exactly:

- condition sequence, code, disposition, and rationale;
- the recommendation condition to which each decision refers;
- pilot purpose and every pilot limitation;
- scope limitations;
- retention obligations; and
- `supersession_eligible`.

`supersession_eligible` is governance evidence only. It does not identify a
prior baseline, compare scopes, create supersession lineage, change publication
status, or authorize supersession execution.

Any later supersession must create a separately authorized immutable record and
must retain the earlier accepted baseline and reference unchanged.

---

## 15. Canonical Serialization

Both the full accepted baseline and reference must use:

- exact typed contracts rather than generic mappings;
- UTF-8 JSON;
- compact separators;
- lexicographically sorted object keys;
- model-enforced deterministic collection ordering;
- lowercase enum values;
- UTC timestamps in the repository's governed representation;
- explicit `null` only where the typed schema permits it;
- no insignificant whitespace; and
- exactly one final newline.

Serialization is representation, not semantic transformation. The serializer
must reject unsupported types rather than stringify, coerce, normalize, or
silently omit them.

The published full-baseline representation includes persistence-lineage
metadata such as the authorization artifact digest. Such metadata remains
excluded from `accepted_baseline_id` and must not alter the exact authorization
decision.

---

## 16. Deterministic Paths and Filenames

The publisher requires one absolute destination directory.

The deterministic final filenames are:

```text
accepted-preservation-baseline-{accepted_baseline_id}.json
accepted-preservation-baseline-{accepted_baseline_id}.json.sha256
accepted-preservation-baseline-reference-{accepted_baseline_id}.json
accepted-preservation-baseline-reference-{accepted_baseline_id}.json.sha256
```

The publication lock filename is:

```text
accepted-preservation-baseline-publication.lock
```

It resides beneath the destination's `.locks` directory.

All filenames must be derived by the service from the validated
`accepted_baseline_id`. Caller-supplied final paths or names are prohibited.
The reference contains only the sibling full-artifact and sidecar filenames.

---

## 17. Publication Lifecycle and Ordering

Under one exclusive publication lock, the publisher shall:

1. independently verify persisted authorization evidence;
2. construct and validate the accepted-baseline model;
3. serialize the full baseline and calculate its SHA-256;
4. construct the reference from that exact identity, filename, digest, and byte
   count;
5. serialize the reference and calculate its SHA-256;
6. derive both exact SHA-256 sidecars;
7. inspect all four final targets before first placement;
8. handle an existing complete set only as exact replay or conflict;
9. write, flush, and fsync each temporary file with restrictive permissions;
10. exclusively place the full accepted-baseline artifact;
11. fsync the destination directory;
12. exclusively place the full-baseline sidecar;
13. fsync the destination directory;
14. exclusively place the reference artifact;
15. fsync the destination directory;
16. exclusively place the reference sidecar last;
17. fsync the destination directory; and
18. return a first-publication result.

Reference publication last is mandatory. The existence of a complete,
independently verifiable reference pair is the downstream publication boundary.

Publication must reuse `exclusive_file_lock` and the repository's existing
exclusive-placement mechanism. It must not introduce a generic persistence
utility or use replacement semantics for immutable final evidence.

---

## 18. SHA-256 Sidecars

Each sidecar must contain exactly:

```text
<64-lowercase-hex-sha256>  <exact-artifact-filename>\n
```

There are exactly two ASCII spaces between digest and filename and exactly one
final newline.

Verification must require:

- one line only;
- lowercase SHA-256 syntax;
- the exact two-space separator;
- the exact sibling artifact filename;
- agreement with the calculated artifact digest; and
- agreement with the digest declared by the governing model or reference.

Malformed or contradictory sidecars are immutable conflicts, not repair
opportunities.

---

## 19. Atomicity, Durability, and Permissions

Every file must be staged in the destination filesystem, written completely,
flushed, and fsynced before exclusive final placement.

There must be one meaningful destination-directory fsync after each final
placement. The reference sidecar is placed last.

Final artifacts and sidecars must use restrictive `0640` permissions. Directory
and lock-directory permissions must follow the existing intentional `0770`
convention used by immutable preservation evidence.

The publisher must preserve causal exception chains for write, flush, fsync,
permission, placement, cleanup, and lock failures.

---

## 20. Locking and Concurrency

One destination-scoped exclusive lock protects construction publication checks,
all four placements, replay verification, and attempt-scoped cleanup.

Lock acquisition follows the repository utility's non-blocking contract. The
publisher attempts the destination lock exactly once. Lock contention and lock
infrastructure failures must be distinguishable from content conflicts and
general publication failures, preserve their causal exception chains, and must
not introduce polling, sleeps, retry counts, or an implicit timeout policy.

A final-placement race must be resolved only by:

- complete exact replay verification when all four targets now exist and match;
  or
- explicit conflict failure.

Concurrency must never cause overwrite, merge, repair, version allocation, or
deletion of another publisher's state.

---

## 21. Idempotent Replay

An identical replay succeeds only when all four final files:

- exist;
- are regular non-link files;
- use the deterministic filenames;
- match the proposed canonical bytes exactly;
- match their expected byte counts;
- have exact governed sidecars;
- match calculated and declared digests; and
- maintain consistent authorization, accepted-baseline, scope, and reference
  lineage.

The returned publication result must set `idempotent_replay=True`.

Replay must independently reverify persisted authorization evidence. The prior
publication result or the continued existence of a reference cannot substitute
for verification.

---

## 22. Immutable Conflicts and Interrupted Publication

Publication fails closed when any target exists without the complete exact
four-file set. This includes every incomplete combination of:

- full baseline artifact;
- full baseline sidecar;
- reference artifact; and
- reference sidecar.

It also fails closed for:

- differing artifact or reference bytes;
- differing byte counts or digests;
- malformed or contradictory sidecars;
- links or non-regular targets;
- identity-derived filename disagreement;
- reference-to-full-artifact disagreement;
- unsafe paths;
- authorization or accepted-baseline lineage disagreement; or
- placement races that do not resolve to complete exact replay.

Conflicting final evidence must never be overwritten, repaired, merged,
renamed, versioned, normalized, or silently removed.

On a failed first attempt, cleanup may remove only temporary files and final
files demonstrably created by that attempt. If safe cleanup cannot be proven or
completed, publication must report failure and leave pre-existing evidence
untouched.

---

## 23. Downstream Consumer Contract

Every downstream phase must begin from an independently verified
`AcceptedPreservationBaselineReference`.

The `AcceptedPreservationBaselineReference` is the sole authoritative
publication boundary exposed to downstream consumers.

The full `AcceptedPreservationBaseline` exists as immutable governance evidence
and shall not be consumed directly except through successful verification
initiated from its corresponding reference.

A downstream consumer must:

1. load the reference artifact and sidecar;
2. verify canonical bytes, byte count, filename, and SHA-256;
3. resolve only the governed sibling full-artifact filename;
4. load the full accepted-baseline artifact and sidecar;
5. verify exact bytes, digest, identity, and reference agreement; and
6. consume the typed `AcceptedPreservationBaseline` without reassembling or
   reevaluating its predecessor evidence.

Downstream phases must not begin from:

- a candidate;
- a validation result;
- an acceptance recommendation;
- an authorization decision;
- an authorization persistence result;
- a caller-supplied full-baseline path;
- an unverified accepted-baseline object; or
- successful publication metadata alone.

This rule prevents classification and planning components from bypassing the
Phase 6B authority boundary.

---

## 24. Failure Taxonomy

Stable failure classifications must distinguish at least:

- invalid public input type;
- unsafe or non-absolute destination;
- authorization artifact or sidecar missing;
- authorization artifact or sidecar unreadable;
- link or non-regular authorization target;
- authorization byte-count mismatch;
- malformed authorization sidecar;
- authorization digest disagreement;
- invalid or noncanonical authorization JSON;
- unknown, missing, duplicated, or wrongly typed authorization fields;
- unsupported authorization schema;
- authorization identity or lineage disagreement;
- rejected authorization outcome;
- incompatible outcome-to-mode mapping;
- scope or evidence-graph projection disagreement;
- accepted-baseline identity disagreement;
- construction invariant failure;
- serialization failure;
- lock contention or lock infrastructure failure;
- incomplete publication set;
- full-artifact, reference, or sidecar conflict;
- reference-to-artifact disagreement;
- concurrent publication race;
- temporary-file write, flush, fsync, permission, or placement failure; and
- attempt-scoped cleanup failure.

Failures must provide sufficient identity and classification context for
review without exposing unrelated sensitive content.

---

## 25. Security Controls

Slice 6B-6 requires:

- typed public inputs;
- strict schema and field validation;
- no generic mapping serialization or deserialization boundary;
- independent canonical-byte and SHA-256 verification;
- regular-file and no-link enforcement;
- deterministic filenames;
- plain sibling filenames in the durable reference;
- absolute destination enforcement;
- path-containment checks;
- exclusive locking and exclusive final placement;
- staged, flushed, fsynced writes;
- restrictive permissions;
- fail-closed partial-state and conflict handling;
- complete immutable lineage;
- no silent evidence repair or normalization; and
- conservative treatment of unknown states.

SHA-256 establishes integrity, not signer identity. This slice makes no
authentication, non-repudiation, or digital-signature claim.

---

## 26. Immutability and No-Reinterpretation Invariant

The exact independently verified authorization decision must be retained
without:

- normalization;
- enrichment;
- annotation inside the decision;
- repair;
- reinterpretation;
- supplementation;
- semantic migration;
- policy reevaluation; or
- scope expansion or contraction.

Accepted-baseline construction is a governed deterministic projection, not a
new decision. Publication metadata must remain in separate accepted-baseline,
reference, artifact, or result fields and must never alter the embedded
authorization decision or its `authorization_id`.

Published accepted-baseline evidence is immutable. Corrections require a new
authorization and a new accepted baseline. No in-place correction is permitted.

---

## 27. Negative Authority Boundaries

Slice 6B-6 may verify, construct, and publish accepted-baseline governance
evidence.

It may not:

- validate source content again;
- change a validation result or recommendation;
- act as the human authority;
- accept rejected authorization;
- infer authorization from persistence;
- alter accepted or excluded scope;
- execute supersession;
- classify content;
- assign retention policy beyond preserving existing obligations;
- define target storage or NAS mappings;
- analyze or adjudicate duplicates for deletion;
- create migration or execution plans;
- preserve, migrate, redirect, consolidate, clean, delete, or restructure data;
- modify authoritative source content;
- release preservation retention;
- certify Phase 6B or any operational state; or
- introduce CLI, configuration, authentication, signatures, notifications, or
  external integrations.

A published reference grants only the authority for later approved analytical
phases to verify and consume the accepted baseline.

---

## 28. Exact Architecture Worktree Scope

Architecture preparation is limited to:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6B6.md
```

This document grants no implementation authorization.

---

## 29. Approved Later Implementation Worktree Scope

After separate explicit implementation authorization, the exact approved
seven-file scope is:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6B6.md
src/poe_backup_orchestrator/models/storage_accepted_baseline.py
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/storage_accepted_baseline.py
src/poe_backup_orchestrator/services/__init__.py
tests/unit/test_storage_accepted_baseline_models.py
tests/unit/test_storage_accepted_baseline.py
```

Splitting verification, construction, serialization, or publication into
additional production or test modules requires separate architecture approval.

---

## 30. Required Tests

### Model and identity tests

- schema and enum invariants;
- exact `pab-<sha256>` derivation;
- one authorization ID produces exactly one valid accepted-baseline ID and
  object;
- timestamps, paths, byte counts, digests, and replay metadata do not affect
  semantic identity;
- every semantic field does affect identity where applicable;
- invalid ordering, duplicate scope, and lineage disagreement fail closed;
- reference and artifact contract invariants; and
- models do not import services.

### Verification tests

- exact persisted authorization reload and reconstruction;
- artifact and sidecar missing, unreadable, malformed, linked, or non-regular;
- byte-count, calculated-digest, result-digest, and sidecar disagreement;
- wrong sidecar separator or filename;
- invalid UTF-8 or JSON;
- missing, unknown, duplicate, and wrongly typed fields;
- unsupported schema;
- noncanonical but semantically decodable bytes rejected;
- authorization and baseline identity disagreement; and
- verification failure causes no publication filesystem mutation.

### Construction tests

- all four eligible outcomes map exactly;
- `REJECT` creates nothing;
- accepted and excluded roots are preserved exactly;
- accepted evidence graph includes exactly accepted-root observations;
- conditions, pilot limitations, retention obligations, and
  `supersession_eligible` are preserved;
- complete candidate, validation, evaluation, authorization, and persistence
  lineage is retained;
- construction performs no policy reevaluation; and
- caller content cannot create a second accepted baseline for one authorization.

### Serialization and publication tests

- compact canonical UTF-8 JSON with exactly one newline;
- deterministic filenames;
- exact two-space sidecars;
- first publication creates exactly four final files;
- reference sidecar is placed last;
- restrictive file and directory permissions;
- file fsync before placement and one directory fsync after each placement;
- exact replay is distinguished from first publication;
- replay completely verifies all four final files;
- every incomplete four-file combination fails closed;
- byte, digest, sidecar, identity, link, non-regular, and reference conflicts;
- lock contention and lock failure preserve causes;
- concurrent same-content publication permits one first publication and one
  governed lock-contention failure under the non-blocking lock contract;
- a later same-content attempt acquires the lock before exact replay
  verification;
- different-content concurrency fails as conflict;
- cleanup removes only current-attempt state; and
- cleanup failure is explicit.

### Negative-authority tests

Tests must prove the absence of:

- validation or policy reevaluation;
- human authorization behavior;
- supersession execution;
- classification or destination design;
- duplicate adjudication;
- migration planning or execution;
- preservation execution;
- source access or mutation;
- redirection, cleanup, deletion, or destructive operations;
- CLI, configuration, signatures, authentication, notifications, or external
  integrations; and
- any downstream consumer path that bypasses independent reference
  verification.

---

## 31. Quality Gates

Implementation review must run in the repository virtual environment:

```bash
source .venv/bin/activate
ruff format .
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Review must also verify:

- only the approved seven files changed;
- model modules do not import services;
- the existing exact authorization decision remains unaltered;
- rejected authorization publishes nothing;
- no existing immutable artifact can be overwritten;
- all four publication files receive complete replay verification;
- the reference is published last;
- every downstream entry point begins with independent reference verification;
- no supersession execution or later authority entered scope; and
- no generic persistence framework or unapproved integration was introduced.

Passing tests do not independently establish architecture conformance,
implementation approval, certification, or later operational authority.

---

## 32. Acceptance Criteria

Slice 6B-6 implementation is ready for human review only when:

1. one verified semantic authorization produces exactly one deterministic
   accepted baseline;
2. all eligible outcomes map correctly and rejection publishes nothing;
3. the exact authorization decision and complete lineage are preserved;
4. accepted and excluded scopes are unchanged;
5. the accepted evidence graph contains exactly the authorized scope;
6. the full accepted baseline and lightweight reference are canonical and
   independently verifiable;
7. all four files use deterministic names and restrictive permissions;
8. reference publication occurs last;
9. identical replay is explicitly distinguishable and completely verified;
10. incomplete or contradictory state fails closed without repair or overwrite;
11. concurrency and cleanup preserve immutable evidence;
12. downstream consumers are contractually restricted to an independently
    verified reference;
13. supersession eligibility is preserved without supersession execution;
14. all negative authority boundaries are tested;
15. only approved files changed; and
16. all repository quality gates pass.

No implementation may be committed, pushed, merged, closed, or certified
without the separately required human approvals.

---

## 33. Recommended Implementation Sequence

After explicit implementation authorization:

1. reverify the exact certified predecessor state and approved worktree scope;
2. create the authorized feature branch while preserving this document;
3. implement immutable accepted-baseline, reference, artifact, result, mode, and
   identity contracts;
4. implement strict private authorization decoding and independent verification;
5. implement deterministic construction and one-to-one identity enforcement;
6. implement canonical full-baseline and reference serialization;
7. implement the locked four-file exclusive publication lifecycle;
8. implement complete replay, conflict, race, and cleanup handling;
9. add model, verification, construction, publication, durability, concurrency,
   and negative-authority tests;
10. add only the approved package exports;
11. run focused tests during implementation;
12. run the full quality gate;
13. inspect exact worktree scope, dependency direction, exclusions, and
    architecture conformance; and
14. present the implementation for explicit human approval before commit.

---

## 34. Relationship to Later Phases

Slice 6B-6 publishes the authoritative input boundary for later governed work.

Later classification and destination-design phases must begin from an
independently verified `AcceptedPreservationBaselineReference`. They may derive
classification and planning evidence but receive no migration authority.

Duplicate analysis and migration planning remain later analytical phases.
Duplicate detection never authorizes deletion.

Migration and preservation execution require separate approved plans and
authority. Migration completion does not authorize client redirection or source
cleanup.

Client redirection, cleanup authorization, cleanup execution, preservation
release, supersession execution, and operational certification remain separate
explicit transitions.

---

## 35. Known Roadmap, Naming, Numbering, and Status Discrepancies

### 35.1 Phase 6B naming

The storage-consolidation roadmap labels Phase 6B as “Information
Classification and Target Architecture.” The later, more specific Phase 6B
parent architecture labels it “Preservation Baseline Acceptance.”

This slice follows the specific parent architecture and implemented predecessor
sequence. It records the discrepancy without changing the roadmap or rewriting
historical intent.

### 35.2 Parent Slice 6B-5 responsibility

The parent architecture summarizes Slice 6B-5 as persisting “authorization and
accepted-baseline evidence.” The approved and implemented Slice 6B-5 is narrower:
it persists only the exact authorization decision. This slice constructs and
publishes accepted-baseline evidence and its reference.

### 35.3 Slice 6B-6 naming

The parent summary calls 6B-6 “Accepted-Baseline Publication” and explicitly
assigns durable-reference publication. The parent accepted-baseline section and
Slice 6B-5 boundary also require a distinct accepted-baseline governance object.
This document therefore records the complete responsibility as construction and
publication rather than silently treating a reference as the full evidence.

### 35.4 Supersession terminology

Slice 6B-1 mentions “supersession publication” as a 6B-6 handoff, while the
parent leaves supersession-scope comparison rules open and requires explicit
immutable lineage. No implemented supersession authorization contract exists.
This slice preserves `supersession_eligible` and defers supersession records and
execution.

### 35.5 Slice numbering

The Phase 6B parent identifies Slice 6B-7 as Phase 6B Certification. Repository
history already uses Slice 6B-7 for Validation Finding Generation and Slice 6B-8
for Validation Result Assembly. This document does not renumber those historical
slices or assign a new certification number. Phase 6B closeout must resolve the
remaining certification-document name explicitly.

### 35.6 Stale predecessor status metadata

The Slice 6B-4 and Slice 6B-5 architecture documents retain implementation-review
status wording even though Git history shows both implementations merged into
`main`. Slice 6B-5 also records an older predecessor HEAD and test total. This
document uses current repository history without editing prior records.

### 35.7 Certification evidence

Git history establishes that Slice 6B-5 was implemented, reviewed, merged, and
quality-gated at the stated 821-test baseline. The repository does not contain a
dedicated Slice 6B-5 closeout or certification record. This document treats the
merged implementation as the certified predecessor state supplied for this
slice but does not claim that a missing historical certification artifact
exists.

### 35.8 Atomic replacement wording

The parent architecture uses “atomic replacement” while prohibiting mutation of
immutable accepted evidence. This slice interprets the governed behavior as
staged, synchronized, exclusive placement. Existing immutable final evidence is
never replaced.

### 35.9 Existing publication conventions

Repository publication implementations are not uniform. This slice follows the
strong immutable-conflict behavior of `InventoryEvidenceStore` and Slice 6B-5
authorization persistence. Replacement-oriented or weaker “published last”
implementations are not the primary immutable-evidence precedent.

---

## 36. Resolved Architectural Decisions

This document approves:

1. `pab-<sha256>` as the accepted-baseline semantic identity;
2. a one-to-one deterministic projection from exactly one independently verified
   authorization decision;
3. `PreservationBaselineAuthorizationPersistenceResult` as the sole public
   locator input;
4. mandatory independent reload, digest verification, strict typed decoding,
   and canonical-byte verification;
5. private service-layer persisted-authorization verification with no public
   verified-evidence model;
6. one full accepted-baseline JSON artifact and sidecar;
7. one lightweight reference JSON artifact and sidecar;
8. no redundant semantic `reference_id`;
9. deterministic identity-derived filenames;
10. publication of the reference pair last;
11. mandatory independent reference verification as the starting point for
    every downstream phase;
12. preservation of `supersession_eligible` without supersession execution;
13. immutable four-file replay and conflict semantics;
14. the exact seven-file later implementation scope; and
15. continued separation of acceptance publication from classification,
    planning, migration, redirection, cleanup, supersession execution, and
    certification.

No unresolved architectural decisions remain that block implementation of the
approved Slice 6B-6 scope.

Future supersession contracts, Phase 6B certification sequencing, and later
governance phases remain intentionally deferred.

---

## 37. Architectural Decision

Slice 6B-6 establishes the immutable accepted-preservation-baseline publication
boundary.

The governing rule is:

> Verify one persisted human authorization independently. Project it exactly
> once into one immutable accepted baseline. Publish the full evidence, then
> publish its independently verifiable reference last. Grant no later authority.

Approval of this document approves the architecture only. Implementation
authorization remains explicitly withheld until granted by separate human
approval.
