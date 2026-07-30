# POE Storage Architecture Intent — Slice 6B-1

## Preservation Baseline Candidate Composition

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B1
**Status:** Proposed for architectural review
**Phase:** 6B — Preservation Baseline Acceptance
**Slice:** 6B-1 — Preservation Baseline Candidate Composition
**Parent architecture:** `POE-STOR-Architecture-Intent-Phase-6B.md`
**Predecessor:** Phase 6A certified preservation-evidence pipeline
**Implementation authorization:** Not granted by this document

---

## 1. Purpose

Slice 6B-1 defines the immutable domain representation and deterministic
composition of a preservation baseline candidate from existing Phase 6A
evidence.

This slice establishes the first Phase 6B boundary:

```text
Phase 6A Evidence
        ↓
Preservation Baseline Candidate Composition
        ↓
Preservation Baseline Candidate
```

The candidate represents the exact evidence set and exact source scope being
presented for later validation.

Slice 6B-1 does not determine whether the evidence is complete, valid,
reconciled, policy-compliant, acceptable, or authorized.

The governing distinction is:

- composition records what evidence is presented;
- validation determines whether that evidence is correct and complete;
- recommendation applies acceptance policy;
- authorization records accountable human authority;
- recording publishes the immutable governance decision.

---

## 2. Architectural Context

Phase 6A currently provides deterministic evidence through the following
pipeline:

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
```

The certified Phase 6A contracts already provide:

- preservation baseline identity;
- capture-session identity;
- source-device identity;
- source-volume identity;
- source-root identity;
- deterministic inventory item identity;
- deterministic inventory assembly;
- persisted inventory evidence and SHA-256 sidecars;
- source-content certifications;
- independently generated content-integrity evidence;
- persisted integrity evidence and SHA-256 sidecars;
- explicit unsupported-object evidence;
- explicit capture and verification exceptions;
- deterministic ordering and immutable domain models.

Slice 6B-1 shall reuse those contracts rather than duplicate them.

---

## 3. Scope

### 3.1 Included responsibilities

Slice 6B-1 includes:

- preservation baseline candidate domain models;
- candidate scope representation;
- typed evidence-reference representation;
- evidence requirement observations;
- deterministic evidence ordering;
- deterministic scope ordering;
- stable candidate identity derivation;
- composition service boundary;
- adaptation of existing Phase 6A publication metadata;
- composition-time structural checks;
- immutable composition output;
- public model and service exports;
- unit tests for domain invariants and deterministic composition.

### 3.2 Excluded responsibilities

Slice 6B-1 explicitly excludes:

- reading source content;
- modifying source content;
- recalculating evidence digests;
- verifying SHA-256 sidecars;
- validating evidence bytes;
- reconciling counts or byte totals;
- validating schema compatibility;
- validating identity consistency across evidence;
- determining whether evidence is mandatory;
- classifying blocking conditions;
- applying acceptance policy;
- recommending acceptance;
- approving exceptions;
- recording human authorization;
- persisting accepted-baseline decisions;
- superseding accepted baselines;
- classifying storage;
- mapping destinations;
- duplicate analysis;
- migration planning;
- migration execution;
- client redirection;
- source cleanup.

No Slice 6B-1 result authorizes migration or any destructive operation.

---

## 4. Governing Principles

Slice 6B-1 shall conform to the following principles:

1. Existing Phase 6A identities and evidence contracts shall be reused.
2. Models must not depend on services.
3. Services may consume immutable domain models.
4. Composition must be deterministic and side-effect free.
5. Composition must not read or reinterpret source content.
6. Missing evidence must be recorded, not judged.
7. Candidate identity must be based on semantic evidence identity rather than
   incidental filesystem location.
8. Evidence references must remain auditable to their persisted artifacts.
9. The candidate must be an evidence graph, not a duplicate inventory.
10. Unsupported objects and exceptions must remain explicit evidence.
11. The domain model must enforce deterministic ordering rather than relying on
    serializers to repair unordered input.
12. Successful composition must never imply validation or acceptance.
13. No production commit may occur until architecture and implementation
    quality gates pass.

---

## 5. Existing Contracts to Reuse

### 5.1 Preservation identity

Reuse:

```python
PreservationBaselineIdentity
```

Relevant existing fields:

```python
schema_version: str
baseline_id: str
created_at_utc: datetime
status: str
retained_until: str
```

The Phase 6A `baseline_id` remains the authoritative preservation-program
identity.

Slice 6B-1 shall not redefine or replace it.

### 5.2 Capture and source hierarchy

Reuse existing identifiers carried by Phase 6A contracts:

```text
capture_session_id
source_device_id
source_volume_id
source_root_id
```

The candidate shall reference the existing hierarchy rather than inventing a
parallel source identity model.

### 5.3 Inventory evidence publication

Reuse the semantic publication data exposed by:

```python
InventoryEvidencePublication
```

Relevant existing fields:

```python
evidence_path: Path
sha256_path: Path
sha256: str
item_count: int
byte_count: int
idempotent_replay: bool
```

The `idempotent_replay` field is operational publication metadata and shall not
participate in candidate identity.

### 5.4 Content-integrity evidence publication

Reuse the semantic publication data exposed by:

```python
PersistedContentIntegrityEvidence
```

Relevant existing fields:

```python
evidence_path: Path
digest_path: Path
byte_count: int
sha256: str
```

Slice 6B-1 shall normalize naming differences between `sha256_path` and
`digest_path` through a Phase 6B evidence-reference contract.

### 5.5 Existing evidence results

Reuse existing immutable evidence result contracts where needed for
composition input:

```python
InventoryAssemblyResult
InventoryContentCaptureResult
ContentIntegrityVerificationResult
PreservationBaselineManifest
```

These objects remain Phase 6A-owned contracts.

Slice 6B-1 may reference them or derive evidence references from their
publications, but shall not alter their semantics.

---

## 6. New Domain Contracts

The recommended model module is:

```text
src/poe_backup_orchestrator/models/storage_baseline_candidate.py
```

### 6.1 Schema version

Define:

```python
STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION: Final[str] = "1.0"
```

The schema version identifies the Phase 6B candidate contract.

It is distinct from Phase 6A evidence schema versions.

---

### 6.2 PreservationEvidenceType

Define an explicit string enumeration:

```python
class PreservationEvidenceType(StrEnum):
    BASELINE_MANIFEST = "baseline_manifest"
    DISCOVERY_RESULT = "discovery_result"
    INVENTORY_EVIDENCE = "inventory_evidence"
    CONTENT_CAPTURE_RESULT = "content_capture_result"
    CONTENT_INTEGRITY_EVIDENCE = "content_integrity_evidence"
    EXCEPTION_EVIDENCE = "exception_evidence"
    RECONCILIATION_EVIDENCE = "reconciliation_evidence"
```

Architectural intent:

- evidence categories are explicit and stable;
- evidence categories remain independent of persistence filenames;
- future evidence types require an intentional schema evolution;
- evidence type does not imply validity or acceptance.

The exact enumeration shall be confirmed against the implementation slice
before coding. No additional type should be added without a demonstrated
Phase 6A or Phase 6B requirement.

---

### 6.3 EvidenceRequirementStatus

Define:

```python
class EvidenceRequirementStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    NOT_APPLICABLE = "not_applicable"
```

Architectural intent:

- `PRESENT` means a reference was supplied;
- `ABSENT` means no reference was supplied;
- `NOT_APPLICABLE` means the composer was explicitly instructed that the
  evidence category does not apply to the candidate scope.

This status records composition facts only.

It must not determine whether absence is acceptable.

---

### 6.4 PreservationEvidenceReference

Define an immutable domain model:

```python
@dataclass(frozen=True, slots=True)
class PreservationEvidenceReference:
    evidence_type: PreservationEvidenceType
    source_root_id: str
    schema_version: str
    evidence_path: Path
    digest_path: Path
    sha256: str
    byte_count: int
```

Required invariants:

- `source_root_id` is normalized and non-empty;
- `schema_version` is normalized and non-empty;
- `evidence_path` is absolute;
- `digest_path` is absolute;
- `evidence_path` and `digest_path` are not identical;
- `sha256` is exactly 64 lowercase hexadecimal characters;
- `byte_count` is non-negative;
- no filesystem read occurs during model construction;
- the reference records publication metadata but does not verify it.

The model intentionally excludes:

- publication timestamp;
- idempotent replay status;
- validation status;
- acceptance status;
- migration authority;
- mutable source observations.

---

### 6.5 EvidenceRequirementObservation

Define:

```python
@dataclass(frozen=True, slots=True)
class EvidenceRequirementObservation:
    source_root_id: str
    evidence_type: PreservationEvidenceType
    status: EvidenceRequirementStatus
    evidence_reference: PreservationEvidenceReference | None
    detail: str | None = None
```

Required invariants:

- `PRESENT` requires `evidence_reference`;
- `ABSENT` prohibits `evidence_reference`;
- `NOT_APPLICABLE` prohibits `evidence_reference`;
- a supplied reference must match both `source_root_id` and `evidence_type`;
- `ABSENT` and `NOT_APPLICABLE` may carry explanatory detail;
- `PRESENT` should not require detail;
- the object does not classify the observation as blocking or non-blocking.

This contract prevents missing evidence from being represented as an exception
or service failure.

---

### 6.6 PreservationBaselineCandidateScope

Define:

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineCandidateScope:
    baseline_id: str
    source_root_ids: tuple[str, ...]
```

Required invariants:

- `baseline_id` is normalized and non-empty;
- `source_root_ids` is non-empty;
- source-root identifiers are normalized;
- duplicates are prohibited;
- identifiers are supplied in deterministic ascending order;
- the model does not sort silently;
- partial-source and pilot semantics are not encoded here.

The scope records the exact source roots included in the candidate.

Acceptance mode is a later Phase 6B concern.

---

### 6.7 PreservationBaselineCandidateIdentity

Define:

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineCandidateIdentity:
    schema_version: str
    candidate_id: str
    baseline_id: str
    created_at_utc: datetime
```

Required invariants:

- `schema_version` must equal the supported candidate schema version;
- `candidate_id` is normalized and non-empty;
- `candidate_id` follows the governed candidate identifier format;
- `baseline_id` is normalized and non-empty;
- `created_at_utc` is timezone-aware UTC;
- identity is immutable.

Recommended candidate identifier format:

```text
pbc-<64 lowercase hexadecimal characters>
```

The exact prefix may be adjusted before implementation if repository naming
conventions demonstrate a stronger established pattern.

---

### 6.8 PreservationBaselineCandidate

Define:

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineCandidate:
    identity: PreservationBaselineCandidateIdentity
    scope: PreservationBaselineCandidateScope
    observations: tuple[EvidenceRequirementObservation, ...]
```

Required invariants:

- `identity.baseline_id` equals `scope.baseline_id`;
- observations are non-empty;
- every observation references a source root in scope;
- every scoped source root has an explicit observation for each configured
  evidence category;
- duplicate `(source_root_id, evidence_type)` observations are prohibited;
- observations are supplied in deterministic order;
- any `PRESENT` reference is structurally consistent with its observation;
- the candidate performs no digest validation;
- the candidate performs no evidence reconciliation;
- the candidate carries no acceptance status.

The candidate represents the complete composition record for later validation.

---

## 7. Candidate Identity Derivation

### 7.1 Responsibility

Candidate identity shall be derived deterministically from the semantic
composition of the candidate.

The recommended helper is:

```python
stable_preservation_baseline_candidate_id(...)
```

It should reside in the model layer if it is a pure deterministic identity
function and has no service dependency.

### 7.2 Canonical identity payload

The candidate identity payload shall include:

- candidate schema version;
- Phase 6A `baseline_id`;
- ordered source-root scope;
- ordered evidence observations;
- evidence type;
- requirement status;
- evidence schema version when present;
- evidence SHA-256 when present;
- evidence byte count when present.

The identity payload shall not include:

- `created_at_utc`;
- evidence publication paths;
- digest sidecar paths;
- publication timestamps;
- idempotent replay status;
- human-readable detail;
- runtime host data;
- mutable filesystem metadata.

### 7.3 Rationale

Candidate identity must answer:

> Is this the same semantic evidence composition?

It must not answer:

> Was this evidence stored at the same absolute path?

Byte-identical evidence publications in different approved locations should
produce the same candidate identifier.

### 7.4 Canonicalization

Identity derivation shall use:

- explicit field names;
- stable ordering;
- UTF-8 encoding;
- deterministic separators;
- lowercase SHA-256 hexadecimal output;
- no locale-sensitive formatting;
- no Python object representation;
- no unordered mapping iteration.

The candidate identifier is:

```text
pbc- + sha256(canonical_identity_payload).hexdigest()
```

---

## 8. Deterministic Ordering

### 8.1 Scope ordering

`source_root_ids` shall be ordered lexicographically by normalized source-root
identifier.

The model shall reject unordered input rather than silently sort it.

### 8.2 Observation ordering

Observations shall be ordered by:

```text
source_root_id
→ evidence_type.value
```

If future schema evolution permits multiple references per evidence type, the
ordering shall extend to:

```text
schema_version
→ sha256
→ byte_count
```

Slice 6B-1 should not introduce multiple references for one
`(source_root_id, evidence_type)` pair unless an existing requirement demands
it.

### 8.3 Evidence path ordering

Evidence paths shall not influence candidate identity.

Paths may be used only as a final deterministic tie-breaker for display or
serialization if future contracts permit multiple semantically distinct
references with identical evidence metadata.

---

## 9. Composition Service

The recommended service module is:

```text
src/poe_backup_orchestrator/services/storage_baseline_composition.py
```

### 9.1 PreservationBaselineComposer

Define a service boundary conceptually equivalent to:

```python
class PreservationBaselineComposer:
    def compose(
        self,
        *,
        baseline_identity: PreservationBaselineIdentity,
        source_root_ids: tuple[str, ...],
        evidence_inputs: tuple[...],
        requirement_policy: ...,
        clock: Clock | None = None,
    ) -> PreservationBaselineCandidate: ...
```

The exact public signature must be finalized during implementation design
against the established repository style.

The architecture requires the service to:

- accept immutable Phase 6A identities and publication metadata;
- normalize existing publication contracts into
  `PreservationEvidenceReference`;
- create explicit requirement observations;
- enforce deterministic scope and observation ordering;
- derive the stable candidate identifier;
- create the immutable candidate identity;
- return one immutable candidate;
- avoid all source-content and evidence-file reads.

### 9.2 Composition input strategy

The preferred strategy is explicit typed inputs rather than a generic mapping.

The composer should accept typed Phase 6A publication objects or narrow
Phase 6B adapter inputs.

It should not accept arbitrary dictionaries.

### 9.3 Requirement configuration

The composer requires an explicit configured set of evidence categories for
each source root.

This configuration determines which observations must exist.

It does not determine whether an absent observation is acceptable.

The requirement configuration may be represented by a small immutable model if
implementation review confirms that a reusable policy object is necessary.

### 9.4 Clock dependency

The composition service may accept an injected UTC clock for deterministic
testing.

Time contributes to the candidate identity object but not to the stable
candidate identifier.

---

## 10. Publication Adapter Boundary

Phase 6A publication objects are not structurally identical.

Slice 6B-1 shall adapt them without modifying them.

### Inventory evidence adaptation

Map:

```text
InventoryEvidencePublication.evidence_path
    → PreservationEvidenceReference.evidence_path

InventoryEvidencePublication.sha256_path
    → PreservationEvidenceReference.digest_path

InventoryEvidencePublication.sha256
    → PreservationEvidenceReference.sha256

InventoryEvidencePublication.byte_count
    → PreservationEvidenceReference.byte_count
```

Do not map `idempotent_replay` into candidate identity.

### Content-integrity evidence adaptation

Map:

```text
PersistedContentIntegrityEvidence.evidence_path
    → PreservationEvidenceReference.evidence_path

PersistedContentIntegrityEvidence.digest_path
    → PreservationEvidenceReference.digest_path

PersistedContentIntegrityEvidence.sha256
    → PreservationEvidenceReference.sha256

PersistedContentIntegrityEvidence.byte_count
    → PreservationEvidenceReference.byte_count
```

### Other evidence categories

Where Phase 6A does not yet expose a persisted publication object with path,
digest, and byte count, Slice 6B-1 must not fabricate one.

The implementation must either:

- accept an explicit typed persisted-reference input; or
- defer that evidence category until a separately approved persistence
  contract exists.

No evidence path or digest may be inferred from naming convention alone.

---

## 11. Composition-Time Checks

Slice 6B-1 may perform structural checks necessary to create a coherent
candidate.

Allowed checks include:

- non-empty identifiers;
- UTC timestamps;
- absolute publication paths;
- SHA-256 lexical format;
- non-negative byte counts;
- source-root membership in scope;
- evidence-type consistency;
- duplicate observation detection;
- deterministic ordering;
- stable identifier derivation;
- Phase 6A baseline identifier consistency where directly available.

Slice 6B-1 must not perform semantic validation, including:

- reading evidence artifacts;
- verifying digest content;
- confirming sidecar content;
- comparing inventory and integrity totals;
- determining schema compatibility;
- deciding whether an absent category is blocking;
- determining whether an exception is acceptable.

Those responsibilities belong to Slice 6B-2 and later slices.

---

## 12. Exception and Unsupported-Object Treatment

The candidate shall not duplicate every unsupported inventory item, discovery
exception, capture exception, or integrity failure.

Instead:

- detailed evidence remains in the Phase 6A artifact;
- the candidate references the artifact;
- evidence requirement observations record whether the artifact is present;
- later validation reads and evaluates the detailed evidence.

If a deterministic summary is already part of an existing Phase 6A contract,
the candidate may reference that contract but should not reproduce the summary
unless a later validation requirement demonstrates the need.

The candidate is an evidence graph, not a replacement manifest or inventory.

---

## 13. Public Export Surface

The following new model-layer exports are recommended:

```python
STORAGE_BASELINE_CANDIDATE_SCHEMA_VERSION
EvidenceRequirementObservation
EvidenceRequirementStatus
PreservationBaselineCandidate
PreservationBaselineCandidateIdentity
PreservationBaselineCandidateScope
PreservationEvidenceReference
PreservationEvidenceType
stable_preservation_baseline_candidate_id
```

The following service-layer exports are recommended:

```python
PreservationBaselineComposer
PreservationBaselineCompositionError
```

Any model imported by a service must come from the defining model module.

Phase 6B code shall not import model contracts through
`services/__init__.py`.

---

## 14. Dependency Direction

Required dependency direction:

```text
storage_baseline_candidate models
    → standard library
    → existing Phase 6A model contracts when required

storage_baseline_composition service
    → Phase 6A model contracts
    → Phase 6A publication contracts
    → Phase 6B candidate models
```

Prohibited dependencies:

```text
Phase 6B candidate models
    ✗ Phase 6A services
    ✗ Phase 6B services
    ✗ filesystem adapters
    ✗ persistence services
```

The service may adapt Phase 6A publication objects but must not call Phase 6A
persistence services during composition.

---

## 15. Error Model

Define a service-layer error:

```python
class PreservationBaselineCompositionError(RuntimeError): ...
```

It should be used only for composition failures that cannot be represented as
candidate observations, such as:

- contradictory typed inputs;
- evidence reference assigned to the wrong source root;
- duplicate evidence input for one required pair;
- candidate identifier derivation failure;
- unsupported publication input type;
- inconsistent baseline identifiers.

Missing evidence should normally produce an `ABSENT` observation rather than a
service exception.

Model invariant failures should remain `ValueError` unless repository
conventions demonstrate a different established model-layer pattern.

---

## 16. Test Strategy

The recommended test modules are:

```text
tests/unit/test_storage_baseline_candidate_models.py
tests/unit/test_storage_baseline_composition.py
```

### 16.1 Model tests

Required model tests include:

- schema version is enforced;
- candidate identifier format is enforced;
- timestamps require UTC;
- scope requires at least one source root;
- duplicate source roots are rejected;
- unordered source roots are rejected;
- evidence paths must be absolute;
- digest paths must be absolute;
- SHA-256 values are normalized and validated;
- negative byte counts are rejected;
- `PRESENT` requires a reference;
- `ABSENT` prohibits a reference;
- `NOT_APPLICABLE` prohibits a reference;
- observation and reference source roots must match;
- observation and reference evidence types must match;
- duplicate observation keys are rejected;
- unordered observations are rejected;
- observations outside scope are rejected;
- identity and scope baseline identifiers must match;
- candidate models are immutable.

### 16.2 Identity tests

Required identity tests include:

- identical semantic composition produces the same identifier;
- creation timestamp does not affect the identifier;
- evidence path does not affect the identifier;
- digest path does not affect the identifier;
- idempotent replay status does not affect the identifier;
- source-root scope changes the identifier;
- evidence type changes the identifier;
- requirement status changes the identifier;
- evidence digest changes the identifier;
- evidence byte count changes the identifier;
- evidence schema version changes the identifier;
- canonical ordering produces repeatable output.

### 16.3 Composition tests

Required service tests include:

- inventory publication adapts correctly;
- integrity publication adapts correctly;
- missing evidence creates `ABSENT`;
- explicitly non-applicable evidence creates `NOT_APPLICABLE`;
- supplied evidence creates `PRESENT`;
- scope and observations are deterministic;
- duplicate evidence input is rejected;
- mismatched source root is rejected;
- mismatched baseline identity is rejected;
- composition does not open evidence files;
- composition does not read source content;
- composition does not write repository or evidence files;
- composition does not validate digest sidecars;
- composition does not reconcile totals;
- identical inputs produce equivalent candidates apart from creation time;
- injected clock controls candidate creation time.

### 16.4 Architectural tests

At minimum, implementation review shall verify:

- the model module imports no service module;
- the composition service does not depend on filesystem discovery adapters;
- no migration, redirection, duplicate deletion, or cleanup behavior is
  introduced;
- existing 656-test certified baseline remains passing before new tests are
  counted.

---

## 17. Implementation Sequence

The recommended Slice 6B-1 implementation order is:

1. Add the Slice 6B-1 architecture-intent document.
2. Review and approve the document.
3. Add candidate schema constant and enumerations.
4. Add immutable evidence-reference and observation models.
5. Add immutable candidate scope and identity models.
6. Add deterministic candidate identifier derivation.
7. Add the immutable candidate aggregate.
8. Add model exports.
9. Add model tests.
10. Add composition service and typed publication adapters.
11. Add service exports.
12. Add composition tests.
13. Run formatting, Ruff, and the full test suite.
14. Review worktree scope and architecture conformance.
15. Commit only after explicit approval.

No persistence service is part of Slice 6B-1.

---

## 18. Implementation Acceptance Criteria

Slice 6B-1 is complete only when:

- all approved domain contracts are implemented as immutable models;
- existing Phase 6A identities are reused;
- existing publication contracts are adapted without modification;
- candidate scope is explicit and deterministic;
- evidence observations are complete for configured requirements;
- missing evidence is represented without validation judgment;
- candidate identity is deterministic and path-independent;
- candidate composition performs no source or evidence-file reads;
- candidate composition performs no persistence;
- candidate composition performs no validation or acceptance evaluation;
- model-to-service dependency direction is preserved;
- public exports are intentional;
- unit tests cover invariants, ordering, identity, and negative boundaries;
- Ruff formatting passes;
- Ruff checks pass;
- all existing and new tests pass;
- `git diff --check` passes;
- worktree scope matches the approved slice;
- no migration or cleanup capability is introduced;
- no commit occurs before final review and approval.

---

## 19. Deferred Decisions

The following decisions are explicitly deferred:

### To Slice 6B-2

- evidence artifact loading;
- digest verification;
- sidecar verification;
- schema compatibility;
- cross-evidence identity validation;
- totals reconciliation;
- blocking-condition classification.

### To Slice 6B-3

- deterministic acceptance recommendation;
- strict acceptance policy;
- exception-eligible policy;
- partial and pilot recommendation semantics.

### To Slice 6B-4

- human authority identity;
- authority role;
- approval and rejection decisions;
- exception approvals.

### To Slice 6B-5

- canonical acceptance persistence;
- locking;
- idempotent replay;
- conflict handling;
- immutable decision publication.

### To Slice 6B-6

- accepted-baseline publication reference;
- downstream consumption boundary;
- supersession publication.

### To Slice 6B-7

- operational certification;
- end-to-end evidence verification;
- negative authority-boundary certification.

---

## 20. Approval Effect

Approval of this document authorizes implementation planning and production
implementation of Slice 6B-1 only.

It does not authorize:

- Slice 6B-2 or later implementation;
- evidence validation;
- acceptance recommendation;
- human authorization;
- accepted-baseline persistence;
- storage classification;
- destination mapping;
- duplicate analysis;
- migration planning;
- migration execution;
- client redirection;
- source cleanup;
- any destructive operation.
