# POE Storage Architecture Intent — Slice 6B-2

## Preservation Baseline Evidence Validation

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B2  
**Status:** Approved architecture; implementation not yet authorized  
**Phase:** 6B — Preservation Baseline Acceptance  
**Slice:** 6B-2 — Preservation Baseline Evidence Validation  
**Parent architecture:** `POE-STOR-Architecture-Intent-Phase-6B.md`  
**Predecessor:** Slice 6B-1 — Preservation Baseline Candidate Composition  
**Repository:** `~/poe-backup-orchestrator`  
**Certified predecessor baseline:** `main` at `d03d590`  
**Implementation authorization:** Not granted by this document  

---

## 1. Purpose

Slice 6B-2 introduces the first semantic evaluation layer for a composed
`PreservationBaselineCandidate`.

The slice determines whether the candidate and its referenced evidence are:

- resolvable;
- readable;
- byte-count verified;
- digest verified;
- schema compatible;
- structurally consistent;
- identity consistent;
- internally reconcilable; and
- explicit about exceptions, unsupported conditions, missing evidence,
  malformed evidence, and contradictions.

The slice must answer:

> Can the candidate and its evidence graph be trusted as an authentic,
> understandable, and internally consistent basis for later acceptance-policy
> evaluation?

The slice must not answer:

> Should the candidate be accepted?

Acceptance recommendation is reserved for a later slice. Human authorization,
acceptance persistence, migration authority, client redirection, source cleanup,
and destructive activity remain outside this slice.

---

## 2. Architectural Context

The certified preservation-governance pipeline entering Slice 6B-2 is:

```text
Discovery
→ Inventory Assembly
→ Inventory Evidence
→ Source Content Capture
→ Content Integrity Evidence
→ Preservation Baseline Candidate Composition
```

Slice 6B-2 extends the pipeline as follows:

```text
Discovery
→ Inventory Assembly
→ Inventory Evidence
→ Source Content Capture
→ Content Integrity Evidence
→ Preservation Baseline Candidate Composition
→ Preservation Baseline Evidence Validation
```

The broader Phase 6B lifecycle remains:

```text
PreservationBaselineCandidate
        ↓
PreservationBaselineValidationResult
        ↓
Later Acceptance Recommendation
        ↓
Later Human Authorization
        ↓
Later Accepted-Baseline Persistence
```

No Phase 6B result grants migration or cleanup authority unless a later,
separately approved architecture explicitly introduces that authority.

---

## 3. Governing Principles

1. Composition facts are not validation conclusions.
2. Validation consumes an immutable candidate and its referenced evidence.
3. Evidence must be authenticated before semantic conclusions are derived.
4. Validation behavior must be deterministic and policy-explicit.
5. Missing evidence must remain distinct from invalid evidence.
6. Missing referenced artifacts must remain distinct from composition-level
   absence.
7. Unreadable evidence must remain distinct from malformed evidence.
8. Unsupported schema must remain distinct from incompatible schema.
9. Unsupported objects and explicit exceptions must remain visible.
10. Contradictory evidence must not be normalized away.
11. Validation severity must not encode acceptance or overridability policy.
12. Validation must not authorize migration or destructive activity.
13. Existing Phase 6A and Slice 6B-1 contracts must be reused.
14. Models must not depend on services.
15. Evidence-loading failures should normally become validation findings rather
    than aborting validation of independent evidence.
16. Validation must never repair, regenerate, rewrite, or replace evidence.
17. No implementation may begin until this architecture is reviewed and
    explicitly authorized.

---

## 4. Scope

### 4.1 Included responsibilities

Slice 6B-2 includes:

- immutable validation-result models;
- validation finding categories;
- validation finding severity;
- deterministic validation ordering;
- evidence artifact resolution;
- evidence readability checks;
- evidence byte-count verification;
- evidence SHA-256 verification;
- digest-sidecar loading and verification;
- evidence deserialization;
- schema-name and schema-version compatibility checks;
- candidate-to-reference consistency checks;
- candidate-to-evidence identity checks;
- baseline-identity consistency checks;
- source-device, source-volume, and source-root consistency checks where exposed;
- capture-session consistency checks where exposed;
- duplicate evidence detection;
- contradictory evidence detection;
- cross-evidence quantitative reconciliation;
- unsupported-object and exception observation extraction;
- immutable validation output;
- deterministic validation-result identity;
- service-level failure behavior;
- unit tests;
- determinism tests;
- failure-isolation tests; and
- negative authority-boundary tests.

### 4.2 Excluded responsibilities

Slice 6B-2 excludes:

- acceptance recommendations;
- acceptance modes;
- exception approval;
- determination that a finding is overridable;
- human authorization;
- authorization identity or role;
- acceptance persistence;
- accepted-baseline publication;
- baseline supersession;
- migration planning;
- migration execution;
- client redirection;
- duplicate deletion;
- source cleanup;
- source-content modification;
- repairing malformed evidence;
- regenerating Phase 6A evidence;
- replacing missing evidence;
- inferring evidence paths from naming conventions;
- adding unsupported evidence categories without persisted Phase 6A contracts;
- operational CLI commands unless separately approved; and
- production implementation before architecture approval.

---

## 5. Existing Contracts to Reuse

Implementation must inspect and reuse the certified contracts at the approved
predecessor baseline.

Expected Slice 6B-1 contracts include:

- `PreservationBaselineCandidate`;
- candidate identity;
- candidate source-root scope;
- `EvidenceRequirementObservation`;
- `EvidenceRequirementStatus`;
- `PreservationEvidenceReference`;
- `PreservationEvidenceType`;
- canonical candidate ordering;
- candidate identifier derivation; and
- candidate composition service boundaries.

Expected Phase 6A contracts include:

- persisted inventory evidence;
- persisted content-integrity evidence;
- evidence serializers and deserializers;
- schema identifiers and versions;
- source identity contracts;
- capture-session identity contracts;
- baseline identifiers where present;
- count and byte-total semantics;
- SHA-256 utilities;
- digest-sidecar conventions;
- persistence publication objects;
- immutable evidence models; and
- clock abstractions.

No Slice 6B-2 model may duplicate a Phase 6A or Slice 6B-1 contract merely to
avoid importing the correct model-layer definition.

---

## 6. Responsibility Separation

The architecture recognizes four separate responsibility layers:

```text
Composition fact
    “The candidate contains this evidence requirement and reference state.”

Validation conclusion
    “The evidence is missing, unreadable, malformed, unsupported,
     inconsistent, contradictory, or verified.”

Acceptance recommendation
    “Policy recommends acceptance, rejection, partial acceptance,
     or exception review.”

Authorization decision
    “An accountable human authority accepts or rejects the candidate.”
```

A successfully composed candidate does not imply valid evidence.

A validation result without severe findings does not imply acceptance.

An acceptance recommendation does not imply human authorization.

Human authorization does not imply migration authority.

---

## 7. Proposed Domain Contracts

Recommended model module:

```text
src/poe_backup_orchestrator/models/storage_baseline_validation.py
```

### 7.1 Validation schema version

```python
STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION: Final[str] = "1.0"
```

This version governs the Slice 6B-2 validation-result contract. It does not
replace candidate or Phase 6A evidence schema versions.

### 7.2 Validation finding severity

```python
class ValidationFindingSeverity(StrEnum):
    INFORMATIONAL = "informational"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

Severity semantics:

- `INFORMATIONAL` — a verified or non-adverse audit observation;
- `WARNING` — usable evidence with an exception, unsupported condition, or
  limitation that later policy must evaluate;
- `ERROR` — a material evidence requirement, schema, or reconciliation failure;
- `CRITICAL` — authenticity, identity, or deterministic interpretation cannot be
  trusted.

`BLOCKING` must not be a severity. Blocking and overridability are acceptance
policy concepts reserved for a later slice.

### 7.3 Validation finding categories

The initial enumeration should be limited to categories supported by certified
contracts.

Proposed categories:

```python
class ValidationFindingCategory(StrEnum):
    EVIDENCE_MISSING = "evidence_missing"
    EVIDENCE_NOT_APPLICABLE = "evidence_not_applicable"
    EVIDENCE_ARTIFACT_MISSING = "evidence_artifact_missing"
    EVIDENCE_UNREADABLE = "evidence_unreadable"
    EVIDENCE_SIZE_MISMATCH = "evidence_size_mismatch"
    EVIDENCE_DIGEST_MISMATCH = "evidence_digest_mismatch"
    DIGEST_SIDECAR_MISSING = "digest_sidecar_missing"
    DIGEST_SIDECAR_UNREADABLE = "digest_sidecar_unreadable"
    DIGEST_SIDECAR_MALFORMED = "digest_sidecar_malformed"
    DIGEST_SIDECAR_MISMATCH = "digest_sidecar_mismatch"
    EVIDENCE_MALFORMED = "evidence_malformed"
    EVIDENCE_SCHEMA_UNSUPPORTED = "evidence_schema_unsupported"
    EVIDENCE_SCHEMA_INCOMPATIBLE = "evidence_schema_incompatible"
    CANDIDATE_REFERENCE_INCONSISTENT = "candidate_reference_inconsistent"
    BASELINE_IDENTITY_MISMATCH = "baseline_identity_mismatch"
    SOURCE_DEVICE_IDENTITY_MISMATCH = "source_device_identity_mismatch"
    SOURCE_VOLUME_IDENTITY_MISMATCH = "source_volume_identity_mismatch"
    SOURCE_ROOT_IDENTITY_MISMATCH = "source_root_identity_mismatch"
    CAPTURE_SESSION_IDENTITY_MISMATCH = "capture_session_identity_mismatch"
    DUPLICATE_EVIDENCE = "duplicate_evidence"
    CONTRADICTORY_EVIDENCE = "contradictory_evidence"
    INVENTORY_RECONCILIATION_MISMATCH = "inventory_reconciliation_mismatch"
    CONTENT_CAPTURE_RECONCILIATION_MISMATCH = "content_capture_reconciliation_mismatch"
    CONTENT_INTEGRITY_RECONCILIATION_MISMATCH = "content_integrity_reconciliation_mismatch"
    UNSUPPORTED_OBJECTS_PRESENT = "unsupported_objects_present"
    EVIDENCE_EXCEPTIONS_PRESENT = "evidence_exceptions_present"
    SOURCE_CHANGE_OBSERVED = "source_change_observed"
    CAPTURE_INCOMPLETE = "capture_incomplete"
```

A generic `VERIFIED` finding is not recommended. Successful verification should
be represented by the per-reference validation status to avoid producing
high-volume routine findings.

### 7.4 Per-reference validation status

```python
class EvidenceValidationStatus(StrEnum):
    VERIFIED = "verified"
    MISSING = "missing"
    UNREADABLE = "unreadable"
    SIZE_MISMATCH = "size_mismatch"
    DIGEST_MISMATCH = "digest_mismatch"
    MALFORMED = "malformed"
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    INCOMPATIBLE_SCHEMA = "incompatible_schema"
```

This status is distinct from Slice 6B-1 `EvidenceRequirementStatus`.

Slice 6B-1 records composition state:

```text
PRESENT
ABSENT
NOT_APPLICABLE
```

Slice 6B-2 records the outcome of validating a present evidence reference.

### 7.5 Validation finding

```python
@dataclass(frozen=True, slots=True)
class ValidationFinding:
    sequence: int
    category: ValidationFindingCategory
    severity: ValidationFindingSeverity
    source_root_id: str | None
    evidence_type: PreservationEvidenceType | None
    evidence_path: Path | None
    field_name: str | None
    expected: str | None
    observed: str | None
    detail: str
```

Required invariants:

- `sequence` is positive;
- sequences are contiguous beginning with one;
- `detail` is normalized and non-empty;
- `source_root_id` is required for source-scoped findings;
- `evidence_path` is absolute when present;
- expected and observed values use deterministic string representations;
- mutable mappings are not stored;
- raw exception objects are not stored;
- platform-dependent traceback text is not stored;
- acceptance recommendations are not represented;
- authorization outcomes are not represented; and
- migration authority is not represented.

### 7.6 Validated evidence reference

```python
@dataclass(frozen=True, slots=True)
class ValidatedEvidenceReference:
    evidence_reference: PreservationEvidenceReference
    status: EvidenceValidationStatus
    calculated_sha256: str | None
    calculated_byte_count: int | None
    sidecar_sha256: str | None
    resolved_schema_name: str | None
    resolved_schema_version: str | None
```

The model records the validation outcome for one `PRESENT` reference.

The complete deserialized evidence artifact should not be embedded unless a
later demonstrated requirement justifies it. The validation result must not
become a duplicate evidence repository.

### 7.7 Validation identity

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineValidationIdentity:
    schema_version: str
    validation_id: str
    candidate_id: str
    baseline_id: str
    validated_at_utc: datetime
```

Recommended identifier:

```text
pbv-<64 lowercase hexadecimal characters>
```

The stable identifier should derive from:

- validation schema version;
- candidate identifier;
- validation-policy profile identifier;
- ordered validated-reference outcomes;
- ordered validation findings; and
- deterministic reconciliation observations.

The identifier must exclude:

- validation timestamp;
- host identity;
- process identifier;
- temporary paths;
- operating-system-specific error text;
- unordered mappings;
- human authorization; and
- acceptance recommendation data.

### 7.8 Validation result

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineValidationResult:
    identity: PreservationBaselineValidationIdentity
    candidate: PreservationBaselineCandidate
    policy_profile_id: str
    validated_evidence: tuple[ValidatedEvidenceReference, ...]
    findings: tuple[ValidationFinding, ...]
```

Required invariants:

- result candidate identity matches the embedded candidate;
- result baseline identity matches the embedded candidate;
- policy profile identifier is normalized and non-empty;
- every `PRESENT` reference has exactly one validation result;
- `ABSENT` and `NOT_APPLICABLE` observations do not fabricate references;
- validated evidence follows canonical candidate ordering;
- findings follow canonical deterministic ordering;
- finding sequences are contiguous;
- duplicate validated references are prohibited;
- no acceptance recommendation is present;
- no human authorization is present;
- no persistence status is present; and
- no migration or cleanup authority is present.

Embedding the immutable candidate is recommended for the initial slice because it
preserves lineage without introducing candidate persistence dependencies.

---

## 8. Technical Validation Policy

Validation must be policy-explicit, but the policy is technical rather than
authoritative.

Recommended model:

```python
@dataclass(frozen=True, slots=True)
class PreservationEvidenceValidationPolicy:
    profile_id: str
    supported_schema_versions: tuple[EvidenceSchemaCompatibilityRule, ...]
    require_digest_sidecars: bool = True
    verify_reference_byte_count: bool = True
    verify_reference_sha256: bool = True
```

Schema compatibility rule:

```python
@dataclass(frozen=True, slots=True)
class EvidenceSchemaCompatibilityRule:
    evidence_type: PreservationEvidenceType
    schema_name: str
    supported_versions: tuple[str, ...]
```

The policy may determine:

- supported evidence schemas;
- supported schema versions;
- required digest algorithm;
- whether digest sidecars are mandatory;
- whether reference byte counts are verified;
- whether reference SHA-256 values are verified; and
- which technical reconciliation rules are available.

The policy must not determine:

- whether missing evidence is acceptable;
- whether a warning may be approved;
- whether partial acceptance is allowed;
- whether a finding is overridable;
- whether an exception is authorized;
- whether the candidate should be accepted or rejected; or
- whether migration may proceed.

---

## 9. Evidence Loading Boundary

Recommended service-layer protocol:

```python
class PreservationEvidenceLoader(Protocol):
    def load(
        self,
        reference: PreservationEvidenceReference,
    ) -> LoadedPreservationEvidence: ...
```

Recommended concrete implementation:

```python
FilesystemPreservationEvidenceLoader
```

The loader is responsible for:

- using the exact referenced evidence path;
- refusing path inference;
- confirming file existence;
- confirming the path represents a readable regular file;
- reading evidence bytes using streaming I/O;
- calculating actual byte count;
- calculating actual SHA-256;
- loading the exact referenced digest sidecar;
- parsing the established repository sidecar format;
- returning deterministic immutable loading facts; and
- never modifying evidence or sidecars.

Expected validation conditions should not normally escape as service exceptions:

- missing evidence file;
- missing sidecar;
- permission denied;
- unreadable evidence;
- malformed sidecar;
- size mismatch;
- digest mismatch;
- malformed serialization;
- unsupported schema;
- incompatible schema; and
- contradictory evidence.

These should become findings so independent evidence can continue to be
validated.

---

## 10. Evidence Verification Sequence

For each `PRESENT` evidence reference, validation must execute in this order:

```text
1. Confirm the referenced evidence path exists.
2. Confirm the path represents a readable regular file.
3. Stream the evidence bytes.
4. Calculate actual byte count.
5. Compare actual byte count with the reference byte count.
6. Calculate actual SHA-256.
7. Compare actual SHA-256 with the reference SHA-256.
8. Confirm the referenced digest sidecar exists.
9. Read and parse the digest sidecar.
10. Confirm the sidecar identifies the referenced evidence artifact according
    to the established repository convention.
11. Compare sidecar SHA-256 with the reference SHA-256.
12. Compare sidecar SHA-256 with the calculated SHA-256.
13. Only after authenticity succeeds, deserialize the evidence.
14. Resolve schema name and schema version.
15. Apply schema compatibility validation.
16. Apply semantic identity checks.
17. Apply cross-evidence reconciliation where prerequisites are satisfied.
```

Evidence that fails digest verification must not be semantically trusted.

The recommended default is:

> Do not perform semantic reconciliation using evidence whose authenticity has
> failed.

Diagnostic parsing of unauthenticated evidence should not be added without
separate review because it risks accidentally deriving conclusions from
untrusted content.

---

## 11. Schema Compatibility

Validation must distinguish the following outcomes.

### 11.1 Malformed evidence

The authenticated bytes cannot be parsed under the expected serialization
format.

Outcome:

```text
EVIDENCE_MALFORMED
```

### 11.2 Unknown schema

The evidence declares a schema name that has no registered adapter.

Outcome:

```text
EVIDENCE_SCHEMA_UNSUPPORTED
```

### 11.3 Unsupported version

The schema name is known, but the declared version has no supported adapter.

Outcome:

```text
EVIDENCE_SCHEMA_UNSUPPORTED
```

### 11.4 Incompatible version

The schema and version are recognized, but the artifact is explicitly
incompatible with the candidate, policy profile, or another required evidence
contract.

Outcome:

```text
EVIDENCE_SCHEMA_INCOMPATIBLE
```

### 11.5 Compatible schema

The schema name and version match an explicit registered adapter.

No best-effort interpretation is permitted.

No validator may silently treat a newer version as equivalent to an older
version.

No generic dictionary traversal may replace a typed schema adapter where a
certified model contract exists.

---

## 12. Evidence Adapter Boundary

Each supported evidence schema should have a narrow typed adapter.

Conceptual protocol:

```python
class PreservationEvidenceAdapter(Protocol):
    evidence_type: PreservationEvidenceType
    schema_name: str
    supported_versions: tuple[str, ...]

    def parse(self, evidence_bytes: bytes) -> object: ...

    def extract_validation_facts(
        self,
        parsed_evidence: object,
    ) -> EvidenceValidationFacts: ...
```

Adapters may extract only facts required for validation, including:

- baseline identifier;
- capture-session identifier;
- source-device identifier;
- source-volume identifier;
- source-root identifier;
- inventory item count;
- inventory file count;
- inventory directory count;
- aggregate source byte count;
- captured item count;
- captured byte count;
- integrity-success count;
- integrity-failure count;
- unsupported-object count;
- exception count;
- completion status; and
- source-change observations.

### 12.1 Validation adapter registry

Adapter discovery and resolution must occur through an explicit immutable
registry:

```python
@dataclass(frozen=True)
class ValidationAdapterRegistry:
    adapters: tuple[PreservationEvidenceAdapter, ...]

    def resolve(
        self,
        *,
        evidence_type: PreservationEvidenceType,
        schema_name: str,
        schema_version: str,
    ) -> PreservationEvidenceAdapter: ...
```

The registry is the deterministic resolution boundary between the validator and
typed evidence adapters.

Registry construction must:

- normalize adapters into canonical order;
- reject duplicate registrations;
- reject overlapping registrations;
- reject ambiguous resolution keys;
- reject adapters that do not declare an exact supported evidence type;
- reject adapters that do not declare an exact schema name;
- reject adapters that do not declare explicit supported schema versions; and
- remain immutable after construction.

Registry resolution must use the exact key:

```text
evidence_type
→ schema_name
→ schema_version
```

The registry must not:

- inspect candidate scope;
- load evidence bytes;
- verify evidence authenticity;
- parse evidence;
- perform reconciliation;
- apply validation severity;
- apply acceptance policy;
- approve exceptions; or
- grant authority.

The validator depends on the registry abstraction rather than iterating or
selecting directly from an arbitrary adapter tuple. Adapter registration order
must never affect resolution or validation output.

Adapters must not:

- repair evidence;
- rewrite evidence;
- infer missing identity;
- normalize contradictions;
- apply acceptance policy;
- approve exceptions;
- grant authority; or
- initiate migration or cleanup.

`EvidenceValidationFacts` should remain internal unless implementation proves it
is a reusable domain contract.

---

## 13. Candidate and Reference Consistency

Validation must confirm:

- every `PRESENT` observation has exactly one evidence reference;
- every validated reference corresponds to one `PRESENT` observation;
- reference evidence type matches observation evidence type;
- reference source root matches observation source root;
- all referenced source roots exist within candidate scope;
- reference schema metadata agrees with loaded evidence metadata;
- reference byte count agrees with actual bytes;
- reference SHA-256 agrees with actual bytes;
- sidecar SHA-256 agrees with the reference and calculated digest;
- no evidence artifact is reused under conflicting identities;
- no evidence path is reused for contradictory evidence types;
- no digest path is reused for contradictory artifacts;
- candidate baseline identity agrees with evidence baseline identity where
  exposed;
- candidate source-root identity agrees with evidence source-root identity;
- source-device and source-volume identity agree where exposed; and
- capture-session identity reconciles across related evidence.

Candidate model invariants establish structural coherence. Slice 6B-2 verifies
whether persisted artifacts support those structural claims.

---

## 14. Cross-Evidence Reconciliation

Reconciliation may only use evidence that has passed:

- path resolution;
- readability;
- byte-count verification;
- digest verification;
- sidecar verification;
- deserialization; and
- schema compatibility.

### 14.1 Discovery-to-inventory boundary

Where a persisted discovery evidence contract exists, validation may confirm:

- discovered source-root identity equals inventory source-root identity;
- discovered supported entries reconcile with inventory coverage;
- discovery exceptions remain represented;
- inaccessible entries remain explicit; and
- unsupported discovered object types remain explicit.

Where no persisted discovery publication contract exists, the validator must not
infer discovery evidence from inventory content.

### 14.2 Inventory-to-capture reconciliation

Where the certified contracts expose comparable populations, validation may
confirm:

- inventory source-root identity equals capture source-root identity;
- eligible inventory item counts reconcile with captured and explicitly
  uncaptured items;
- source byte totals reconcile with captured bytes and explicit exceptions;
- every uncaptured item has explicit evidence;
- unsupported objects are not silently treated as captured or absent; and
- capture completion state is explicit.

### 14.3 Capture-to-integrity reconciliation

Where the certified contracts expose comparable populations, validation may
confirm:

- captured content identities reconcile with integrity evidence;
- captured item count equals integrity success, integrity failure, and explicitly
  unsupported verification outcomes according to Phase 6A semantics;
- captured byte counts reconcile with certified and failed byte totals where
  available;
- every integrity failure remains explicit;
- no integrity evidence belongs to an unrelated capture session or source root;
  and
- no captured certification is silently omitted.

### 14.4 Exception reconciliation

Validation should confirm:

- aggregate exception counts match detailed exception records where both exist;
- unsupported-object counts match detailed unsupported records where both exist;
- contradictory completion and exception claims become findings; and
- a complete status does not silently coexist with unresolved missing-item
  evidence unless the governing Phase 6A schema explicitly permits it.

The validator reports contradictions. A later acceptance-policy slice determines
their consequence.

---

## 15. Outcome Semantics

### 15.1 Composition-level missing evidence

The candidate records `ABSENT` and contains no reference.

Outcome:

```text
EVIDENCE_MISSING
```

The validator must not fabricate or infer a path.

### 15.2 Not-applicable evidence

The candidate records `NOT_APPLICABLE`.

Outcome:

```text
EVIDENCE_NOT_APPLICABLE
```

The validator records the declaration but does not decide whether the
declaration is acceptable.

### 15.3 Missing referenced artifact

The candidate records `PRESENT`, but the referenced evidence file does not
exist.

Outcome:

```text
EVIDENCE_ARTIFACT_MISSING
```

This is distinct from composition-level absence.

### 15.4 Unreadable evidence

The artifact exists but cannot be read.

Outcome:

```text
EVIDENCE_UNREADABLE
```

### 15.5 Malformed evidence

The artifact is authentic but cannot be parsed under its expected format.

Outcome:

```text
EVIDENCE_MALFORMED
```

### 15.6 Unsupported evidence

The artifact is authentic and parseable, but no compatible adapter exists.

Outcome:

```text
EVIDENCE_SCHEMA_UNSUPPORTED
```

### 15.7 Invalid or incompatible evidence

The artifact is authentic and understood but violates its schema, identity, or
semantic invariants.

Outcome:

```text
EVIDENCE_SCHEMA_INCOMPATIBLE
```

or a more specific consistency or reconciliation category.

### 15.8 Contradictory evidence

Two individually authentic artifacts make incompatible claims.

Outcome:

```text
CONTRADICTORY_EVIDENCE
```

The finding must identify the conflicting fields, expected values, observed
values, evidence types, and relevant paths.

### 15.9 Unsupported objects and explicit exceptions

Unsupported objects and explicit exceptions do not automatically mean the
evidence is invalid.

Outcomes:

```text
UNSUPPORTED_OBJECTS_PRESENT
EVIDENCE_EXCEPTIONS_PRESENT
```

Recommended default severity is `WARNING` unless the evidence is itself
contradictory, malformed, or unauthenticated.

Later acceptance policy determines whether these conditions are permissible,
exception-eligible, or blocking.

---

## 16. Deterministic Validation Ordering

### 16.1 Candidate observation order

Reuse Slice 6B-1 canonical ordering:

```text
source_root_id
→ evidence_type
```

### 16.2 Validation phase order

Validation phases execute in this order:

```text
1. Candidate-level invariant confirmation
2. Composition absence and not-applicable observations
3. Evidence reference resolution
4. Evidence size verification
5. Evidence digest verification
6. Digest-sidecar verification
7. Evidence deserialization
8. Schema compatibility
9. Candidate/reference identity consistency
10. Cross-evidence identity consistency
11. Cross-evidence quantitative reconciliation
12. Exception and unsupported-condition extraction
13. Validation-result identity derivation
```

### 16.3 Finding ordering

Recommended canonical finding sort key:

```python
(
    source_root_id or "",
    evidence_type.value if evidence_type is not None else "",
    validation_phase_rank,
    category.value,
    evidence_path.as_posix() if evidence_path is not None else "",
    field_name or "",
    expected or "",
    observed or "",
    detail,
)
```

After canonical sorting, contiguous sequence values are assigned beginning with
one.

Implementation must not depend on:

- filesystem enumeration order;
- dictionary insertion order from deserialized evidence;
- adapter registration order;
- thread completion order;
- operating-system-specific exception text; or
- temporary path names.

Parallel loading may be considered later, but output must remain identical to
sequential execution.

---

## 17. Validation Service Interface

Recommended service module:

```text
src/poe_backup_orchestrator/services/storage_baseline_validation.py
```

Recommended service:

```python
class PreservationBaselineValidator:
    def __init__(
        self,
        *,
        evidence_loader: PreservationEvidenceLoader,
        validation_policy: PreservationEvidenceValidationPolicy,
        adapter_registry: ValidationAdapterRegistry,
        clock: Clock | None = None,
    ) -> None: ...

    def validate(
        self,
        *,
        candidate: PreservationBaselineCandidate,
    ) -> PreservationBaselineValidationResult: ...
```

The validator must:

- accept exactly one immutable candidate;
- use an explicit technical validation policy;
- resolve typed evidence adapters through an explicit immutable validation
  adapter registry;
- load only candidate-referenced artifacts;
- verify authenticity before semantic interpretation;
- continue after localized evidence failures;
- produce one immutable validation result;
- preserve the candidate unchanged;
- avoid persistence;
- avoid acceptance recommendation;
- avoid authorization; and
- avoid migration or cleanup authority.

The interface must not accept arbitrary dictionaries, generic JSON objects, or
untyped policy mappings.

---

## 18. Failure Model

Recommended service exception:

```python
class PreservationBaselineValidationError(Exception): ...
```

This exception is reserved for conditions where a deterministic result cannot
safely be produced, including:

- unsupported candidate object type;
- validator internal invariant failure;
- contradictory validation-policy configuration;
- duplicate adapter registration;
- adapter registry ambiguity;
- candidate mutation detected during validation;
- failure deriving the stable validation identifier;
- non-deterministic adapter output detected; and
- programmer error in an evidence adapter.

The following should become findings rather than aborting validation:

- missing artifacts;
- unreadable artifacts;
- malformed artifacts;
- unsupported schemas;
- incompatible schemas;
- digest mismatches;
- sidecar failures;
- identity mismatches;
- reconciliation mismatches;
- unsupported objects;
- explicit evidence exceptions; and
- contradictory evidence.

One source-root failure must not prevent validation of independent source roots.

---

## 19. Dependency Direction

Required dependency direction:

```text
storage_baseline_validation models
    → standard library
    → storage_baseline_candidate models
    → existing Phase 6A model contracts only when necessary

storage_baseline_validation service
    → storage_baseline_candidate models
    → storage_baseline_validation models
    → Phase 6A evidence models and serializers
    → narrow loader and adapter protocols
    → existing hash, sidecar, and clock abstractions
```

Prohibited dependency direction:

```text
storage_baseline_validation models
    ✗ Phase 6A services
    ✗ Phase 6B services
    ✗ filesystem implementations
    ✗ persistence services
    ✗ CLI modules

Phase 6A models
    ✗ Phase 6B models
    ✗ Phase 6B services
```

The service should import models from their defining modules rather than through
service package export modules.

---

## 20. Proposed Public Export Surface

Model-layer exports:

```python
STORAGE_BASELINE_VALIDATION_SCHEMA_VERSION
EvidenceSchemaCompatibilityRule
EvidenceValidationStatus
PreservationBaselineValidationIdentity
PreservationBaselineValidationResult
PreservationEvidenceValidationPolicy
ValidatedEvidenceReference
ValidationFinding
ValidationFindingCategory
ValidationFindingSeverity
stable_preservation_baseline_validation_id
```

Service-layer exports:

```python
FilesystemPreservationEvidenceLoader
PreservationBaselineValidationError
PreservationBaselineValidator
PreservationEvidenceAdapter
PreservationEvidenceLoader
ValidationAdapterRegistry
```

Concrete evidence adapters should remain internal initially unless another
approved component requires direct import.

---

## 21. Implementation Sequence

### Step 1 — Inspect certified predecessor contracts

Inspect the implemented Slice 6B-1 contracts at certified predecessor HEAD
`d03d590`, including candidate models, composition services, exports, and tests.

Inspect every referenced Phase 6A evidence model, serializer, persistence
publication object, and sidecar implementation.

Confirm:

- exact schema fields;
- exact serialization formats;
- schema metadata location;
- sidecar syntax;
- identity locations;
- count semantics;
- byte semantics;
- canonical hash utilities;
- clock abstraction;
- error conventions; and
- actual evidence types with persisted publication references.

### Step 2 — Implement validation domain models

Implement:

- severity enumeration;
- finding categories;
- per-reference validation status;
- validation finding;
- validated evidence reference;
- technical validation policy;
- validation identity;
- validation result; and
- stable validation identifier.

No filesystem dependency may enter the model layer.

### Step 3 — Implement evidence loader

Implement the narrow loader protocol and filesystem implementation.

Reuse established hashing and digest-sidecar conventions.

### Step 4 — Implement validation adapter registry and typed evidence adapters

Implement the immutable `ValidationAdapterRegistry` first, including canonical
registration, duplicate rejection, ambiguity rejection, and exact
`(evidence_type, schema_name, schema_version)` resolution.

Implement adapters only for evidence types with certified persisted publication
contracts.

Do not fabricate support for conceptual evidence types lacking:

- exact evidence path;
- exact digest path;
- expected SHA-256;
- expected byte count; and
- declared or deterministically resolvable schema identity.

### Step 5 — Implement reference and authenticity validation

Implement:

- path checks;
- readability;
- byte-count verification;
- SHA-256 verification;
- digest-sidecar verification;
- deterministic loading outcomes; and
- failure isolation.

### Step 6 — Implement schema validation

Implement:

- deserialization;
- schema resolution;
- supported-version lookup;
- incompatible-version detection; and
- typed fact extraction.

### Step 7 — Implement identity consistency

Implement only checks supported by actual certified fields:

- baseline identity;
- source-device identity;
- source-volume identity;
- source-root identity; and
- capture-session identity.

### Step 8 — Implement cross-evidence reconciliation

Implement only equations whose populations and semantics are proven equivalent
by existing Phase 6A contracts.

Do not invent equality between differently scoped counts.

### Step 9 — Assemble deterministic result

Implement:

- canonical validated-reference ordering;
- canonical finding ordering;
- sequence assignment;
- stable validation identity; and
- immutable result construction.

### Step 10 — Add public exports

Add narrowly governed exports to model and service package surfaces.

### Step 11 — Execute quality gates

Required commands:

```bash
ruff format .
ruff check .
pytest -q
git diff --check
```

Verify that the worktree contains only approved Slice 6B-2 changes.

No commit may occur before implementation review and explicit approval.

---

## 22. Test Strategy

Recommended test modules:

```text
tests/unit/test_storage_baseline_validation_models.py
tests/unit/test_storage_baseline_validation_loader.py
tests/unit/test_storage_baseline_validation.py
```

Adapter-specific test modules may be added where schema complexity justifies
them.

### 22.1 Model tests

Required coverage:

- supported validation schema version;
- validation identifier format;
- UTC timestamp enforcement;
- normalized policy profile identifier;
- valid finding severity and category;
- required finding detail;
- absolute evidence paths;
- contiguous finding sequences;
- candidate and result identity agreement;
- duplicate validated-reference rejection;
- canonical validated-reference ordering;
- canonical finding ordering;
- stable identifier excludes timestamp;
- stable identifier changes with semantic changes;
- semantically identical inputs produce identical identifiers;
- acceptance fields are absent;
- authorization fields are absent; and
- migration authority fields are absent.

### 22.2 Loader tests

Required coverage:

- exact evidence path is used;
- no path inference occurs;
- missing file is distinguished from unreadable file;
- actual byte count is calculated;
- reference byte count is verified;
- streaming SHA-256 is calculated;
- reference SHA-256 is verified;
- missing sidecar is explicit;
- unreadable sidecar is explicit;
- malformed sidecar is explicit;
- sidecar digest mismatch is explicit;
- calculated, referenced, and sidecar digests reconcile;
- evidence is never modified;
- source content is never accessed; and
- platform-specific error text is normalized.

### 22.3 Schema tests

Required coverage:

- supported schema accepted;
- malformed serialization detected;
- missing schema metadata detected;
- unknown schema detected;
- unsupported version detected;
- incompatible version detected;
- no best-effort parsing occurs;
- explicit adapter registration required;
- duplicate adapter registration rejected; and
- ambiguous adapter resolution rejected.

### 22.4 Candidate consistency tests

Required coverage:

- source-root mismatch;
- evidence-type mismatch;
- baseline-identity mismatch;
- source-device mismatch where supported;
- source-volume mismatch where supported;
- capture-session mismatch;
- evidence-path reuse under contradictory references;
- digest-path reuse under contradictory references;
- duplicate evidence;
- candidate immutability; and
- present observation without exactly one validation result.

### 22.5 Reconciliation tests

Required coverage:

- matching counts reconcile;
- mismatching counts create deterministic findings;
- matching byte totals reconcile;
- mismatching byte totals create deterministic findings;
- integrity success and failure totals reconcile;
- unsupported-object totals remain explicit;
- exception totals remain explicit;
- contradictory completion claims are detected;
- reconciliation is skipped after authentication failure;
- unrelated evidence is not reconciled; and
- one source-root failure does not block independent roots.

### 22.6 Determinism tests

Required coverage:

- shuffled input observations produce the same result;
- shuffled adapter registration produces the same result;
- repeated validation produces the same validation identifier;
- repeated validation produces identical finding order;
- filesystem enumeration order cannot affect output;
- timestamp does not affect stable identity; and
- normalized error findings are platform-independent.

### 22.7 Authority-boundary tests

Required negative coverage:

- validator does not return acceptance recommendation;
- validator does not return acceptance mode;
- validator does not approve exceptions;
- validator does not record human authorization;
- validator does not persist accepted baselines;
- validator does not supersede baselines;
- validator does not grant migration authority;
- validator does not redirect clients;
- validator does not modify source content;
- validator does not delete or clean content; and
- successful validation is not represented as authorization.

---

## 23. Acceptance Criteria

Slice 6B-2 is complete when:

1. An immutable `PreservationBaselineValidationResult` exists.
2. The validator consumes an immutable `PreservationBaselineCandidate`.
3. Composition observations remain distinct from validation conclusions.
4. Every present evidence reference receives exactly one deterministic outcome.
5. Composition-level absence remains distinct from a missing referenced file.
6. Unreadable evidence remains distinct from malformed evidence.
7. Malformed evidence remains distinct from unsupported schema.
8. Unsupported schema remains distinct from incompatible schema.
9. Unsupported evidence remains distinct from contradictory evidence.
10. Evidence byte counts are independently verified.
11. Evidence SHA-256 values are independently verified.
12. Digest sidecars are independently loaded, parsed, and verified.
13. Semantic interpretation occurs only after authenticity succeeds.
14. Supported schemas and versions are explicit.
15. Candidate, baseline, source-root, and capture-session consistency checks are
    explicit where certified fields support them.
16. Cross-evidence reconciliation is deterministic.
17. Reconciliation uses only established Phase 6A semantics.
18. Unsupported objects and exceptions remain visible.
19. Independent evidence failures do not prevent completion of the overall
    validation result.
20. Findings have deterministic ordering.
21. Finding sequences are contiguous.
22. Validation identity is stable for semantically identical results.
23. Models have no service dependency.
24. No acceptance recommendation enters the slice.
25. No exception approval enters the slice.
26. No human authorization enters the slice.
27. No acceptance persistence enters the slice.
28. No migration or cleanup authority enters the slice.
29. Ruff formatting passes.
30. Ruff checks pass.
31. All existing and new tests pass.
32. `git diff --check` passes.
33. The worktree scope matches the approved slice.
34. No commit occurs before implementation review and approval.

---

## 24. Resolved Architectural Decisions

1. The validation result is immutable.
2. The candidate remains immutable and unchanged.
3. Findings are separate from acceptance policy.
4. Severity does not encode overridability.
5. Evidence authentication precedes semantic interpretation.
6. Digest failure prevents use of the artifact in semantic reconciliation.
7. Local evidence failures do not abort validation of independent evidence.
8. Successful verification is represented by per-reference status, not routine
   `VERIFIED` findings.
9. `NOT_APPLICABLE` is recorded but not judged as acceptable.
10. The initial validation result embeds the immutable candidate.
11. Validation-result persistence is not part of Slice 6B-2.
12. A CLI is not part of Slice 6B-2.
13. No migration, redirection, cleanup, or destructive authority enters the
    slice.
14. Evidence adapters are typed and explicit.
15. Adapter registration and resolution occur through an explicit immutable
    `ValidationAdapterRegistry`.
16. Adapter resolution uses the exact
    `(evidence_type, schema_name, schema_version)` key.
17. Unsupported schema versions are never interpreted best-effort.

---

## 25. Repository-Inspection Questions to Resolve Before Coding

These are implementation preconditions rather than unresolved architecture
choices.

### 25.1 Persisted evidence categories

Confirm which `PreservationEvidenceType` values have certified persisted
publication contracts containing:

- evidence path;
- digest path;
- expected SHA-256;
- expected byte count; and
- schema identity.

Only those types may be implemented initially.

### 25.2 Schema metadata location

Confirm whether schema name and version are:

- embedded in the artifact;
- provided by a typed serializer contract; or
- carried only by the candidate reference.

Loaded evidence must independently establish or deterministically resolve its
schema.

### 25.3 Digest-sidecar syntax

Confirm the exact Phase 6A sidecar format and filename semantics.

Slice 6B-2 must reuse that convention exactly.

### 25.4 Reconciliation populations

Confirm inclusion rules for:

- inventory item counts;
- file counts;
- directory counts;
- unsupported-object counts;
- captured-item counts;
- capture-exception counts;
- integrity-success counts;
- integrity-failure counts; and
- byte totals.

No equality may be implemented until both values are known to describe the same
population.

### 25.5 Identity availability

Confirm which persisted evidence artifacts expose:

- baseline identity;
- source-device identity;
- source-volume identity;
- source-root identity; and
- capture-session identity.

Checks must be limited to identities actually persisted in certified contracts.

---

## 26. Quality and Review Gates

Before implementation:

- inspect the certified predecessor contracts;
- verify actual persisted schemas;
- verify sidecar conventions;
- verify reconciliation semantics;
- verify exact adapter registry resolution keys;
- confirm approved file scope; and
- obtain explicit implementation approval.

During implementation:

- preserve model-to-service dependency direction;
- avoid duplicate contracts;
- preserve candidate immutability;
- isolate evidence failures;
- maintain deterministic ordering; and
- add negative authority tests.

Before commit:

```bash
ruff format .
ruff check .
pytest -q
git diff --check
git status --short
```

The implementation diff must be reviewed before any commit is created.

---

## 27. Approval Effect

Approval of this document authorizes architecture for Slice 6B-2 only.

It does not authorize production implementation until the user explicitly
approves implementation after repository contract inspection.

It does not authorize:

- Slice 6B-3 acceptance recommendation;
- exception approval;
- human authorization;
- acceptance persistence;
- accepted-baseline publication;
- migration planning;
- migration execution;
- client redirection;
- source cleanup;
- duplicate deletion; or
- destructive activity.
