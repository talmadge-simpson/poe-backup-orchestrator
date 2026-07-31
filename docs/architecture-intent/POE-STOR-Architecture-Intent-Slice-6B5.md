# POE Storage Architecture Intent — Slice 6B-5

## Preservation Baseline Authorization Persistence

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B5
**Status:** Approved architecture; implementation in review
**Phase:** 6B — Preservation Baseline Acceptance
**Slice:** 6B-5 — Preservation Baseline Authorization Persistence
**Parent architecture:** `POE-STOR-Architecture-Intent-Phase-6B.md`
**Predecessor:** Slice 6B-4 — Preservation Baseline Human Authorization
**Repository:** `~/poe-backup-orchestrator`
**Certified predecessor baseline:** `main` at `f2f6a7c`
**Certified predecessor quality gate:** Ruff PASS; 791 tests passing
**Implementation authorization:** Granted by explicit human approval

---

## 1. Purpose

Slice 6B-5 defines deterministic, immutable persistence for one existing,
valid:

```python
PreservationBaselineAuthorizationDecision
```

The slice converts the exact in-memory authorization decision into canonical
UTF-8 JSON bytes, persists those bytes with an independently verifiable
SHA-256 sidecar, and returns immutable persistence evidence.

The core invariant is:

> Persistence is serialization and durable storage, not transformation.

This slice answers:

> Was this exact authorization decision durably stored as canonical,
> independently verifiable governance evidence?

It does not answer:

> Has an accepted preservation baseline been constructed or published for
> consumption by later phases?

---

## 2. Architectural Context

The pipeline entering this slice is:

```text
PreservationBaselineCandidate
        ↓
PreservationBaselineValidationResult
        ↓
PreservationBaselineAcceptanceRecommendation
        ↓
PreservationBaselineAuthorizationDecision
```

Slice 6B-5 extends the pipeline only as follows:

```text
PreservationBaselineAuthorizationDecision
        ↓
Canonical Serialization
        ↓
Synchronized Immutable Persistence
        ↓
Authorization Artifact + SHA-256 Sidecar
        ↓
PreservationBaselineAuthorizationPersistenceResult
```

The next boundary remains separate:

```text
Persisted Authorization Decision
        ↓
Later Accepted-Baseline Construction and Publication
```

Persistence does not create an accepted baseline and grants no migration,
redirection, cleanup, or destructive authority.

---

## 3. Exact Slice Responsibility

Slice 6B-5 shall:

1. accept exactly one immutable authorization decision;
2. serialize the complete decision without changing it;
3. calculate SHA-256 over the exact serialized bytes;
4. derive deterministic persistence paths from the existing authorization ID;
5. persist one JSON artifact and one SHA-256 sidecar;
6. synchronize concurrent attempts through the existing locking primitive;
7. distinguish first persistence from identical replay;
8. fail closed on incomplete or conflicting existing state;
9. return immutable persistence-result evidence.

The service shall not reconstruct, validate again, normalize, enrich, or
reinterpret the decision.

---

## 4. Included Scope

This slice includes:

- a persistence-artifact model;
- a persistence-result model;
- canonical authorization-decision serialization;
- deterministic authorization artifact naming;
- deterministic SHA-256 sidecar naming and content;
- absolute destination-directory validation;
- restricted destination and lock-directory preparation;
- non-blocking exclusive locking;
- staged and synchronized file creation;
- exclusive immutable artifact placement;
- exact-byte SHA-256 calculation;
- independent sidecar verification;
- first-persistence and identical-replay distinction;
- incomplete-pair detection;
- immutable conflict detection;
- cleanup of temporary or newly created partial state owned by the current
  failed attempt;
- public model and service exports;
- model, serializer, persistence, concurrency, failure, and negative-boundary
  tests.

---

## 5. Explicit Exclusions and Deferred Responsibilities

Slice 6B-5 excludes:

- accepted-preservation-baseline construction;
- accepted-baseline identity derivation;
- accepted-baseline reference publication;
- baseline supersession execution or publication;
- authorization workflow or approval requests;
- authorization reevaluation;
- acceptance-policy reevaluation;
- validation recomputation;
- evidence reopening or reconciliation;
- source-content access;
- execution-plan or migration-plan creation;
- preservation or migration execution;
- NAS consolidation;
- client redirection;
- source cleanup;
- deletion, deduplication, restructuring, or destructive operations;
- source-system or authoritative-source modification;
- CLI commands;
- reports or notifications;
- external integrations;
- digital signatures or cryptographic attestations beyond SHA-256 evidence;
- authentication;
- identity-provider or directory integration;
- a generic persistence framework or cross-repository persistence refactor.

These responsibilities require later, separately approved architecture.

---

## 6. Governing Invariants

1. Persistence consumes one already-valid immutable decision.
2. Persistence must not change any authorization field or nested lineage.
3. Persistence metadata must remain outside the authorization decision.
4. The existing `authorization_id` remains authoritative semantic identity.
5. The persistence digest identifies exact stored bytes, not decision
   semantics independently of serialization.
6. Existing authorization evidence must never be overwritten.
7. Artifact and sidecar are one required persistence pair.
8. An incomplete pair is conflict state, not an invitation to repair.
9. Identical replay is success and must be explicit in the result.
10. Differing content at the same identity is an immutable conflict.
11. Persistence failure grants no later authority.
12. Successful persistence grants no accepted-baseline publication, migration,
    redirection, or cleanup authority.

---

## 7. Input Contract

The service input is exactly:

```python
PreservationBaselineAuthorizationDecision
```

The persistence layer shall not accept:

- dictionaries;
- generic JSON objects;
- untyped mappings;
- independently supplied authorization, evaluation, validation, candidate, or
  baseline identifiers;
- an independently supplied timestamp, authority, outcome, scope, rationale,
  or recommendation;
- a caller-supplied artifact filename.

All semantic content and lineage must come from the single certified decision
object. A wrong input type is a programmer or integration error and shall fail
before filesystem mutation.

---

## 8. Output Contracts

### 8.1 Persistence artifact

The immutable artifact contract shall be:

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationArtifact:
    evidence_path: Path
    sha256_path: Path
    sha256: str
    byte_count: int
```

Required invariants:

- both paths are absolute;
- `sha256_path` is the evidence filename with `.sha256` appended;
- `sha256` is exactly 64 lowercase hexadecimal characters;
- `byte_count` is greater than zero;
- the contract contains persistence metadata only;
- the contract carries no acceptance, migration, or cleanup status.

### 8.2 Persistence result

The primary output contract shall be:

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationPersistenceResult:
    authorization_id: str
    baseline_id: str
    artifact: PreservationBaselineAuthorizationArtifact
    idempotent_replay: bool
```

Required invariants:

- `authorization_id` equals the input decision identity;
- `baseline_id` equals the input decision lineage;
- `idempotent_replay` is `False` only for successful first persistence;
- `idempotent_replay` is `True` only after exact existing-pair verification;
- the result does not contain or construct an accepted baseline.

### 8.3 Persistence identity

No separate `PreservationBaselineAuthorizationPersistenceIdentity` is required
in this slice. The existing `authorization_id` identifies the semantic decision
and the artifact SHA-256 identifies the exact persisted bytes. Introducing a
third stable identity would duplicate rather than clarify those contracts.

If later architecture demonstrates a distinct persistence-identity need, the
name is reserved as:

```python
PreservationBaselineAuthorizationPersistenceIdentity
```

It must not be introduced implicitly in Slice 6B-5 implementation.

---

## 9. Model, Service, and Module Naming

Proposed model module:

```text
src/poe_backup_orchestrator/models/storage_baseline_authorization_persistence.py
```

Proposed service module:

```text
src/poe_backup_orchestrator/services/storage_baseline_authorization_persistence.py
```

Approved names for implementation planning:

```python
PreservationBaselineAuthorizationArtifact
PreservationBaselineAuthorizationPersistenceResult
PreservationBaselineAuthorizationSerializer
PreservationBaselineAuthorizationStore
PreservationBaselineAuthorizationPersistenceError
PreservationBaselineAuthorizationConflictError
PreservationBaselineAuthorizationLockError
```

The primary output name must use `PersistenceResult`. Accepted-baseline
publication terminology is reserved for Slice 6B-6.

---

## 10. Canonical Serialization Rules

`PreservationBaselineAuthorizationSerializer` shall serialize the complete
decision as one canonical JSON document.

Canonical rules are:

1. encoding is UTF-8;
2. the document is terminated by exactly one `\n` byte;
3. JSON object keys use lexical ordering at every level;
4. separators are exactly `,` and `:` without incidental whitespace;
5. Unicode content is emitted as UTF-8 rather than platform-dependent escapes;
6. dataclass fields become JSON object members without omission or enrichment;
7. `StrEnum` and other enum values become their governed string values;
8. tuples become arrays while preserving the model-enforced order;
9. paths become POSIX strings as a JSON representation only;
10. timezone-aware UTC datetimes use `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`;
11. `None`, booleans, integers, and strings retain their JSON equivalents;
12. unsupported runtime values fail explicitly;
13. sets, unordered mappings supplied outside certified dataclasses, floats,
    and arbitrary objects are not accepted as repairable input;
14. repeated serialization of the same decision produces identical bytes.

Primitive JSON representation is serialization, not semantic normalization.
The serializer must traverse the certified decision as held and must not sort,
trim, deduplicate, default, omit, or otherwise change decision values.

The persisted document shall be the decision itself. It shall not be wrapped in
a persistence envelope. Artifact paths, digest, byte count, replay state, host,
process, and lock metadata belong only in separate persistence contracts.

---

## 11. Authorization Identity and Persistence Digest

The two hashes serve different purposes.

### 11.1 Authorization identity

The existing identifier remains:

```text
pbd-<64 lowercase hexadecimal characters>
```

`authorization_id` identifies canonical authorization semantics as defined by
Slice 6B-4. Persistence must neither replace nor recalculate it using a new
algorithm.

As already governed, `authorization_id` excludes:

- `decided_at_utc`;
- persistence paths;
- persistence digest;
- host and process identity;
- random identifiers;
- authentication or external directory state.

### 11.2 Persistence digest

The persistence digest is:

```python
sha256(canonical_serialized_decision_bytes).hexdigest()
```

It covers every serialized byte, including:

- the complete embedded recommendation and lineage;
- the exact authorization decision fields;
- `decided_at_utc`;
- the final newline.

Therefore, the semantic authorization ID and persistence digest are not
expected to be equal and must never be treated as interchangeable.

---

## 12. Deterministic Paths and Filenames

The store shall receive an explicit absolute `destination_directory` and derive
both filenames internally.

Evidence filename:

```text
preservation-baseline-authorization-<authorization_id>.json
```

SHA-256 filename:

```text
preservation-baseline-authorization-<authorization_id>.json.sha256
```

Lock path:

```text
<destination_directory>/.locks/preservation-baseline-authorization.lock
```

Rules:

- the destination directory must be absolute;
- the `authorization_id` must already satisfy the certified `pbd-` pattern;
- callers cannot supply or override filenames;
- the derived target must be a direct child of the destination directory;
- `.` and `..`, separators, alternate separators, and traversal are impossible
  under the certified identifier contract and shall still fail if observed;
- existing symbolic links or non-regular target objects fail closed as
  conflicts.

The directory location is operationally supplied because repository
configuration and CLI integration are outside this slice.

---

## 13. Persistence Lifecycle

The service lifecycle shall be:

```text
Receive exact decision
        ↓
Validate input and absolute destination contract
        ↓
Serialize exact canonical bytes
        ↓
Calculate persistence SHA-256 and sidecar bytes
        ↓
Derive deterministic artifact, sidecar, and lock paths
        ↓
Prepare restricted destination and lock directories
        ↓
Acquire exclusive non-blocking lock
        ↓
Inspect artifact-pair state
        ├── both absent → first persistence
        ├── both present and exact → idempotent replay
        ├── one present → incomplete-pair conflict
        └── either differs → immutable conflict
        ↓
Stage, flush, fsync, and exclusively place first-persistence files
        ↓
Fsync destination directory
        ↓
Return PreservationBaselineAuthorizationPersistenceResult
```

Serialization must complete before destination files are created. All
filesystem decisions occur under the lock.

---

## 14. Locking and Concurrency

The store shall reuse:

```python
exclusive_file_lock
```

from `poe_backup_orchestrator.utilities.locking`.

Required behavior:

- locking is exclusive, advisory, and non-blocking;
- one lock serializes authorization persistence within the destination
  directory;
- a persistent lock file does not mean a live owner exists;
- lock contention raises
  `PreservationBaselineAuthorizationLockError`;
- other locking failures raise the same slice-specific lock error with the
  underlying failure chained;
- no artifact-state inspection or placement occurs outside the acquired lock;
- lock release occurs after success or failure;
- concurrent appearance of either target is resolved as exact replay or
  immutable conflict, never overwrite.

No new generic locking framework is authorized.

---

## 15. Idempotent Replay

An existing persistence pair is an identical replay only when all conditions
hold:

1. artifact and sidecar both exist as regular files;
2. existing artifact bytes exactly equal proposed canonical bytes;
3. SHA-256 recalculated from existing bytes equals the proposed digest;
4. the sidecar contains the same digest;
5. the sidecar names the exact artifact filename;
6. the sidecar uses the exact canonical line format;
7. the target path derives from the input `authorization_id`.

Exact replay returns:

```python
idempotent_replay = True
```

and performs no rewrite, timestamp update, permission repair, sidecar repair,
or other mutation.

First persistence returns:

```python
idempotent_replay = False
```

Compatible retry is not a weaker comparison. It is an identical replay after a
caller retries a completed first persistence.

---

## 16. Immutable Conflict Behavior

The following conditions are conflicts:

- existing artifact bytes differ from proposed bytes;
- existing artifact digest differs from the proposed digest;
- sidecar digest differs;
- sidecar filename differs;
- sidecar format is malformed or non-canonical;
- only one member of the required pair exists;
- either target is a directory, symbolic link, or other non-regular object;
- a concurrent writer creates non-identical state;
- content at the identity-derived path represents another decision;
- an attempt would mutate already persisted authorization evidence.

Conflicts shall raise:

```python
PreservationBaselineAuthorizationConflictError
```

The error shall identify, where safely observable:

- authorization ID;
- target path;
- failure classification;
- proposed digest;
- existing digest, when calculable.

Conflict handling must not overwrite, merge, normalize, repair, supplement,
version, quarantine, or delete existing state. Persisting conflict evidence as
a separate artifact is not authorized by this slice.

---

## 17. Partial-Pair and Interrupted-Write Handling

Artifact and sidecar form one required persistence pair.

If either member existed before the current attempt without the other, the
store shall fail closed. It shall not recreate the missing member even when it
can calculate what the member should contain.

During first persistence:

1. temporary files are staged in the destination filesystem;
2. artifact is exclusively placed;
3. sidecar is exclusively placed;
4. the destination directory is synchronized;
5. success is returned only after both placements and synchronization succeed.

If the current attempt places the artifact but fails before placing the
sidecar, it shall remove only the artifact created by that attempt and
synchronize the directory. It must not remove pre-existing state.

If cleanup fails, the operation raises a persistence error and leaves the
incomplete pair visible for later fail-closed diagnosis. A later retry must not
silently repair that state.

Temporary files shall be removed after success or failure where removal is
possible.

---

## 18. SHA-256 Sidecar

The canonical sidecar content is exactly:

```text
<64 lowercase hexadecimal characters>  <artifact filename>\n
```

Example shape:

```text
0123456789abcdef...  preservation-baseline-authorization-pbd-....json
```

The sidecar shall:

- be ASCII encoded;
- contain one line;
- contain two ASCII spaces between digest and filename;
- name only the artifact filename, not an absolute path;
- contain no additional metadata;
- receive the same restrictive mode as the artifact;
- be independently read and verified during replay.

Digest-only sidecars are not canonical for this slice.

---

## 19. Atomicity, Durability, Fsync, and Permissions

The behavioral precedent is `InventoryEvidenceStore`.

Required first-persistence mechanics:

- destination and `.locks` directories are created with requested mode `0o770`;
- temporary files are created in the destination filesystem;
- artifact and sidecar temporary descriptors receive mode `0o640`;
- exact bytes are written, flushed, and file-synchronized;
- final paths are created through exclusive placement that cannot overwrite an
  existing path;
- the destination directory is synchronized after placement;
- cleanup changes are followed by directory synchronization;
- return occurs only after durable pair placement.

“Atomic” in this slice means synchronized, exclusive placement of each member
under one lock with fail-closed pair semantics. It does not authorize replacing
an existing immutable artifact.

`ContentIntegrityEvidencePersistence` is not the primary precedent because its
`os.replace` behavior permits replacement and it lacks the required immutable
conflict, locking, and replay controls.

Restore execution-record persistence provides useful staged-write and
filesystem synchronization examples, but its existing replay path does not
verify the sidecar strongly enough for this slice.

---

## 20. Lineage Requirements

The persisted decision must retain, without alteration:

- authorization schema version and authorization ID;
- evaluation ID;
- validation ID;
- candidate ID;
- baseline ID;
- complete embedded recommendation;
- complete embedded validation result and candidate lineage;
- decision outcome;
- authority identity, role, basis, display name, and organization;
- decision timestamp;
- ordered condition decisions;
- accepted and excluded scope;
- pilot metadata when present;
- retention obligations;
- supersession eligibility;
- rationale.

The persistence result repeats only the minimum identity required to bind the
artifact to the input decision. It must not become a second semantic source of
truth.

---

## 21. Failure Taxonomy

The service shall expose:

```python
class PreservationBaselineAuthorizationPersistenceError(RuntimeError): ...


class PreservationBaselineAuthorizationConflictError(
    PreservationBaselineAuthorizationPersistenceError
): ...


class PreservationBaselineAuthorizationLockError(
    PreservationBaselineAuthorizationPersistenceError
): ...
```

Failure classifications include:

- wrong input type;
- relative or invalid destination directory;
- unsafe or inconsistent identity-derived path;
- destination preparation failure;
- canonical serialization failure;
- unsupported runtime value;
- invalid datetime representation;
- lock contention;
- lock open or acquisition failure;
- unreadable existing artifact or sidecar;
- incomplete existing pair;
- malformed sidecar;
- artifact-content conflict;
- digest conflict;
- non-regular or symbolic-link target conflict;
- temporary-file creation failure;
- permission-setting failure;
- write, flush, or file-fsync failure;
- exclusive-placement race or failure;
- directory-fsync failure;
- partial-attempt cleanup failure.

Expected filesystem and conflict failures shall be translated to the narrowest
slice-specific error with causal chaining. Programmer defects must not be
converted into successful persistence.

---

## 22. Security Controls

Slice 6B-5 requires:

- absolute destination paths;
- internal filename derivation from the validated `pbd-` identifier;
- no arbitrary caller filename;
- refusal to overwrite any existing target;
- fail-closed handling of links and non-regular targets;
- restrictive requested directory and file modes;
- staging inside the destination filesystem;
- non-blocking exclusive locking;
- exact-byte digest calculation;
- independent sidecar verification;
- no source-content access;
- no execution of serialized content;
- no resolution of external references from serialized evidence;
- no logging requirement that would expose arbitrary decision content;
- explicit cleanup limited to files created by the current failed attempt.

SHA-256 evidence provides integrity verification, not signer authentication.
This slice makes no digital-signature, identity-proofing, or identity-provider
claim.

---

## 23. Immutability and No-Transformation Invariant

The persistence layer shall serialize and store the exact immutable
`PreservationBaselineAuthorizationDecision` without:

- normalization;
- enrichment;
- annotation;
- repair;
- reinterpretation;
- supplementation;
- semantic migration;
- policy reevaluation;
- scope expansion;
- scope contraction.

It shall not:

- trim or rewrite text;
- reorder decision collections;
- add defaults;
- omit `None`, empty, rejected, excluded, or exceptional state;
- recalculate authorization identity using a new policy;
- change `decided_at_utc`;
- attach persistence paths or digest to the decision;
- turn rejection into a lifecycle state;
- turn authorization into an accepted-baseline object.

Persistence metadata exists only in
`PreservationBaselineAuthorizationArtifact` and
`PreservationBaselineAuthorizationPersistenceResult`.

---

## 24. Negative Authority Boundaries

Slice 6B-5 may persist immutable authorization-decision evidence.

It may not:

- authorize a decision not already authorized by Slice 6B-4;
- approve or reject conditions;
- alter authority identity or rationale;
- construct or publish an accepted baseline;
- execute supersession;
- classify information;
- map destinations;
- identify deletion authority;
- plan or execute migration;
- redirect clients or applications;
- authorize or execute cleanup;
- modify source content or source systems;
- perform destructive behavior.

Successful persistence proves only that exact decision evidence was durably
stored and independently hash-verifiable.

---

## 25. Exact Proposed Implementation Worktree Scope

Architecture-only scope before approval:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6B5.md
```

Proposed later implementation scope after explicit approval:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6B5.md
src/poe_backup_orchestrator/models/storage_baseline_authorization_persistence.py
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/storage_baseline_authorization_persistence.py
src/poe_backup_orchestrator/services/__init__.py
tests/unit/test_storage_baseline_authorization_persistence_models.py
tests/unit/test_storage_baseline_authorization_persistence.py
```

No configuration, CLI, bootstrap, migration, restore, source-content,
accepted-baseline, or generic persistence utility file is in scope.

---

## 26. Required Tests

### 26.1 Model tests

- artifact paths must be absolute;
- sidecar path must be derived from artifact path;
- digest must be lowercase 64-character hexadecimal;
- byte count must be positive;
- result identity must be valid and non-empty;
- artifact and result are immutable;
- replay state is explicit.

### 26.2 Serialization tests

- repeated serialization is byte-identical;
- output is canonical compact UTF-8 JSON;
- output ends with exactly one newline;
- lexical key ordering is stable;
- tuple ordering is preserved rather than repaired;
- enums use governed values;
- UTC timestamps use canonical `Z` form;
- `decided_at_utc` is present;
- complete nested lineage is present;
- optional and empty values are not silently omitted;
- unsupported values fail;
- serialization does not mutate the decision;
- digest covers exact bytes including the final newline.

### 26.3 First-persistence tests

- absolute destination is required;
- destination and lock directories are prepared;
- deterministic filenames are used;
- artifact and sidecar are created;
- artifact and sidecar modes are `0o640`;
- sidecar format is exact;
- recalculated artifact digest matches result and sidecar;
- first result has `idempotent_replay=False`;
- temporary files are removed;
- no source content is read or modified.

### 26.4 Replay and conflict tests

- exact pair replay is idempotent and performs no rewrite;
- artifact-only state fails closed;
- sidecar-only state fails closed;
- differing artifact bytes conflict;
- malformed sidecar conflicts;
- different sidecar digest conflicts;
- different sidecar filename conflicts;
- link and non-regular targets conflict;
- existing modes or timestamps are not repaired during replay;
- concurrent identical placement resolves as replay;
- concurrent differing placement resolves as conflict.

### 26.5 Failure and durability tests

- lock contention maps to the lock error;
- lock failure preserves the cause;
- staging failure leaves no final pair;
- artifact-placement failure cleans temporary files;
- sidecar-placement failure removes only the newly created artifact;
- cleanup failure remains visible as a persistence error;
- file fsync occurs before placement;
- directory fsync occurs after placement and cleanup;
- lock releases after success and failure.

### 26.6 Negative authority tests

- persistence does not call the authorization assembler;
- persistence does not reevaluate policy or validation;
- persistence does not create an accepted-baseline object;
- persistence exposes no accepted-baseline reference;
- persistence does not create plans or execute migration;
- persistence does not access source roots;
- persistence does not authorize redirection or cleanup;
- persistence performs no destructive source operation.

---

## 27. Quality Gates

Implementation shall not be accepted unless all of the following pass:

```bash
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Review shall also verify:

- the model module imports no service module;
- only approved files changed;
- the exact decision is serialized without transformation;
- authorization identity and persistence digest remain distinct;
- all first-persistence and replay paths verify the complete pair;
- no overwrite or repair path exists;
- no accepted-baseline construction or later authority enters scope;
- the full certified predecessor test suite remains passing with new tests.

Passing tools do not independently establish architecture approval,
implementation approval, or certification.

---

## 28. Acceptance Criteria

Slice 6B-5 architecture is ready for implementation review when:

1. input is exactly one `PreservationBaselineAuthorizationDecision`;
2. no generic mapping or separately supplied identity is accepted;
3. output uses
   `PreservationBaselineAuthorizationPersistenceResult`;
4. artifact metadata uses `PreservationBaselineAuthorizationArtifact`;
5. no redundant persistence identity is introduced;
6. canonical serialization is fully specified;
7. serialization preserves the exact decision without transformation;
8. `authorization_id` remains the existing semantic `pbd-` identity;
9. persistence SHA-256 covers exact serialized bytes;
10. `decided_at_utc` is persisted but remains excluded from authorization ID;
11. paths and filenames are deterministic and internally derived;
12. persistence uses staged, synchronized, exclusive placement;
13. existing immutable evidence can never be overwritten;
14. exact replay is explicit and read-only;
15. incomplete pairs fail closed;
16. conflicts are explicit and never repaired, merged, versioned, or replaced;
17. sidecar format and independent verification are exact;
18. locking and concurrent-race behavior are defined;
19. file and directory durability controls are defined;
20. lineage remains complete;
21. failure categories are explicit;
22. security boundaries are explicit;
23. no accepted baseline is constructed or published;
24. no planning, migration, redirection, cleanup, deletion, or source mutation
    is introduced;
25. no CLI, external integration, signing, authentication, identity-provider,
    or notification capability is introduced;
26. implementation scope is narrow and reviewable;
27. human architecture and implementation approval are required before code
    changes.

---

## 29. Recommended Implementation Sequence

After architecture approval and explicit implementation authorization:

1. create the required feature branch;
2. implement artifact and persistence-result models;
3. add model invariant and immutability tests;
4. implement canonical decision serialization;
5. add exact-byte, timestamp, lineage, and no-transformation tests;
6. implement deterministic path and sidecar construction;
7. implement destination preparation and existing lock reuse;
8. implement locked pair-state inspection;
9. implement exact replay verification;
10. implement staged, fsynced, exclusive first persistence;
11. implement partial-attempt cleanup and failure translation;
12. add persistence, replay, conflict, race, durability, permission, and cleanup
    tests;
13. add negative authority-boundary tests;
14. add only approved model and service exports;
15. run formatting, static analysis, the full test suite, and whitespace checks;
16. inspect exact worktree scope and dependency direction;
17. review implementation against this architecture;
18. obtain explicit human approval before commit;
19. commit, push, merge, and close out only as separately authorized.

---

## 30. Relationship to Phase 6B-6 and Later Phases

Slice 6B-5 ends with persisted authorization-decision evidence.

Slice 6B-6 must separately define:

- accepted-preservation-baseline construction;
- accepted-baseline identity;
- accepted scope and evidence graph representation;
- durable accepted-baseline reference;
- publication rules and consumer contract;
- supersession representation or later boundary;
- proof that downstream consumers cannot bypass Phase 6B authority.

Slice 6B-6 publication does not itself grant migration authority.

Classification, destination design, duplicate analysis, migration planning,
migration execution, reconciliation, client redirection, and source cleanup
remain later, separately approved responsibilities.

---

## 31. Known Roadmap and Naming Discrepancies

### 31.1 Phase naming

The storage-consolidation roadmap labels Phase 6B as “Information
Classification and Target Architecture.” The later and more specific Phase 6B
parent architecture labels Phase 6B as “Preservation Baseline Acceptance.”

This slice follows the specific Phase 6B parent and certified predecessor
sequence. It records the discrepancy without editing the roadmap or claiming
that the historical naming conflict is resolved.

### 31.2 Parent 6B-5 summary

The parent architecture summarizes Slice 6B-5 as persisting “authorization and
accepted-baseline evidence.” This approved slice is intentionally narrower:

- Slice 6B-5 persists only the exact authorization decision;
- Slice 6B-6 constructs and publishes the accepted-baseline reference.

This preserves the parent authority boundary while preventing persistence from
silently becoming accepted-baseline transformation or publication.

### 31.3 Persistence and publication terminology

Some existing services and the parent architecture use “publication” for
durable file placement. Slice 6B-5 uses persistence terminology for its primary
contracts and behavior. Publication terminology is reserved here for the later
accepted-baseline publication boundary.

This terminology refinement does not rename historical contracts such as
`InventoryEvidencePublication`; it governs only new Slice 6B-5 names.

### 31.4 Atomic replacement wording

The parent architecture mentions atomic replacement, while also prohibiting
mutation of immutable decision evidence. Slice 6B-5 resolves the operational
meaning as staged, synchronized, exclusive placement. No existing immutable
authorization artifact may be replaced.

### 31.5 Existing persistence conventions

Repository persistence implementations are not uniform. This slice selects
`InventoryEvidenceStore` as the behavioral precedent and records why
replacement-oriented content-integrity persistence is insufficient. It does
not silently standardize or refactor historical implementations.

---

## 32. Architectural Decision

Slice 6B-5 establishes deterministic, immutable persistence of one exact
`PreservationBaselineAuthorizationDecision`.

The governing rule is:

> Persist the decision exactly. Prove the stored bytes independently. Transform
> nothing. Publish no accepted baseline.

Approval of this document authorizes implementation planning only when paired
with explicit implementation authorization. It does not authorize an
accepted-baseline object, accepted-baseline publication, migration,
redirection, cleanup, source modification, or destructive operation.
