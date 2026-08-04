# POE Storage Architecture Intent — Slice 6C-3

## Classification Findings and Result Assembly

**Document ID:** `POE-STOR-Architecture-Intent-Slice-6C3`

**Status:** Architecture draft; implementation authorization withheld

**Artifact class:** Product architecture artifact

**System:** POE Backup Orchestrator

**Governed subject:** Slice 6C-3 classification findings and result assembly

**Phase:** 6C — Classification and Destination Design

**Governing parent:** `POE-STOR-Architecture-Intent-Phase-6C`

**Predecessor:** Slice 6C-2 — Deterministic Classification Policy and Observation

**Repository baseline:** `main` at
`5205b04a69214a1f13bbe2262f75d011518290e1`

**ES-1 lifecycle state:** `ARCHITECTURE_DRAFT`

**ES-6 responsibility state:** `ARCHITECTURE_REVISION`

**Architecture-preparation authority:** Granted by accountable-human direction for
this document only

**Implementation authorization:** Withheld

---

## 1. Purpose and Independently Useful Outcome

Slice 6C-3 consumes exactly one immutable, semantically valid
`AcceptedBaselineClassificationObservationSet`, derives typed findings from its
already-computed observations according to the complete mapping in this
architecture, and returns exactly one immutable deterministic
`AcceptedBaselineClassificationResult`.

The result is independently useful because it makes uncertainty, conflict,
insufficient evidence, unsupported state, and required human review explicit in a
single reviewable analytical boundary. It preserves the exact observation set and
therefore its complete context, policy, accepted-baseline, evidence, scope, and
provenance lineage.

The result reports analytical completeness only. It is not classification approval,
an authoritative assignment, destination approval, migration readiness, operational
readiness, certification, or destructive authority.

---

## 2. Governance, Ownership, and Lifecycle

This architecture is governed, in precedence order, by:

- `AGENTS.md`;
- the Engineering Kernel;
- the Engineering Lifecycle Standard;
- the Slice Specification Standard;
- the Model Routing Standard;
- the Repository Knowledge Foundation and applicable repository-knowledge records;
- `POE-STOR-MIG-001-Preservation-Baseline-Standard.md`;
- the Phase 6 and Phase 6C parent architectures;
- the approved and integrated Slice 6C-1 architecture and implementation; and
- the approved and integrated Slice 6C-2 architecture and implementation.

The Engineering System governs engineering work and shall not enter product models,
services, imports, configuration, CLI behavior, or runtime dependencies.

This document is an architecture candidate only. Architecture review, architecture
approval, implementation authorization, implementation, implementation review,
repository transition, integration, closeout, and certification remain distinct
human-governed responsibilities.

---

## 3. Parent Context and Architectural Position

```text
AcceptedBaselineAnalysisContext — Slice 6C-1
        ↓ deterministic classification
AcceptedBaselineClassificationObservationSet — Slice 6C-2
        ↓ structural and semantic-identity validation, then finding derivation
AcceptedBaselineClassificationResult — Slice 6C-3
        ↓ later governed dependency
Classification Evidence Persistence and Reference Publication — Slice 6C-4
```

Authentication is not classification. Classification observation is not a finding.
A finding is not a human decision. An analytical result is not approval. Publication
is not approval. Approval is not destination, migration, redirection, cleanup, or
destructive authority.

Slice 6C-3 does not redefine the Phase 6 strategy, Phase 6C sequence, Slice 6C-1
context contract, or Slice 6C-2 policy and observation contracts.

---

## 4. Predecessor, Dependencies, Lineage, and Assumptions

### 4.1 Immediate predecessor

The immediate predecessor is integrated Slice 6C-2. This slice consumes its public
contracts:

- `STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION`;
- `STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION`;
- `AcceptedBaselineClassificationDimension`;
- `AcceptedBaselineClassificationObservationKind`;
- `AcceptedBaselineClassificationState`;
- `AcceptedBaselineClassificationPolicyIdentity`;
- `AcceptedBaselineClassificationObservationSetIdentity`;
- `AcceptedBaselineClassificationSubject`;
- `AcceptedBaselineClassificationFactReference`;
- `AcceptedBaselineClassificationCandidate`;
- `AcceptedBaselineClassificationPolicy`;
- `AcceptedBaselineClassificationObservation`;
- `AcceptedBaselineClassificationObservationSet`; and
- `stable_accepted_baseline_classification_observation_set_id`.

The supplied observation set must satisfy the predecessor's exact schema, identity,
ordering, state, scope, and lineage invariants. Missing, malformed, stale,
contradictory, or unsupported predecessor state fails closed.

### 4.2 Transitive predecessor lineage

The observation set directly retains its exact `AcceptedBaselineAnalysisContext` and
classification policy. The context remains the authoritative complete lineage source
for the accepted baseline, authorization, evaluation, validation, candidate,
original baseline, accepted and excluded scope, conditions, pilot constraints,
retention obligations, supersession eligibility, authenticated evidence, capture,
inventory, integrity, source device, volume, and item provenance.

Slice 6C-3 shall preserve that object graph. It shall not flatten, replace, copy
selectively, or reconstruct predecessor lineage.

### 4.3 Public predecessor identity functions and attainable validation

Validation shall use only these integrated public predecessor identity functions:

- `stable_accepted_baseline_analysis_profile_id`;
- `stable_accepted_baseline_analysis_context_id`;
- `stable_accepted_baseline_classification_policy_id`; and
- `stable_accepted_baseline_classification_observation_set_id`.

The assembler shall recompute, in that order:

1. the analysis-profile ID from every public profile field accepted by
   `stable_accepted_baseline_analysis_profile_id`;
2. the analysis-context ID from the accepted-baseline ID, the validated profile,
   and the complete retained authenticated- and lineage-only-evidence tuples;
3. the classification-policy ID from every public policy field accepted by
   `stable_accepted_baseline_classification_policy_id`; and
4. the classification-observation-set ID from the recomputed context identity
   keys, validated policy, and complete retained observation tuple.

It shall also compare all repeated identity relationships: observation-set to
context for analysis-context, accepted-baseline, and analysis-profile IDs; context
to profile and accepted baseline for their IDs; observation-set to policy for the
classification-policy ID; and policy behavior-manifest identity and version to the
integrated public constants.

This validation proves structural conformance of the retained public object graph
and agreement between its current semantic payloads and current stored identities.
It does not prove which historical service invocation constructed the objects,
independently prove that authenticated observations were correctly derived from
source facts, or attest transport authentication. It shall not invoke the
classification service, evaluate predicates, match rules against facts, reconstruct
observations, or otherwise re-execute classification policy. It shall not import or
reproduce predecessor private helpers, canonical serializers, behavior-manifest
builders, observation-key helpers, or evidence-digest helpers.

### 4.4 Other dependencies

The slice has no filesystem, evidence-loader, publisher, persistence, lock, clock,
network, database, taxonomy registry, AI, CLI, bootstrap, or configuration dependency.

Python standard-library facilities used for immutable data contracts, regular
expressions, canonical JSON, enumeration, and SHA-256 are technical dependencies,
not additional product authorities.

### 4.5 Assumptions

No hidden input is assumed. Slice 6C-3 assumes only the validation boundary in
Section 4.3. Signatures, tokens, private constructors, private-helper dependencies,
and invocation attestation are not required and are not authorized.

---

## 5. Exact Responsibility

Slice 6C-3 shall:

1. accept exactly one `AcceptedBaselineClassificationObservationSet`;
2. perform exactly the structural and semantic-identity validation in Section 4.3;
3. validate the complete state/review matrix in Section 9 without rerunning
   classification;
4. inspect every observation exactly once in canonical observation order;
5. apply the complete state-to-finding mapping in this architecture;
6. produce zero or one finding for each observation;
7. preserve exact subject, state, candidate, rule, rationale, review, and fact
   references in every finding and bind it to its predecessor observation key;
8. derive one authority-neutral analytical result status from the complete finding
   set;
9. compute deterministic finding and result identities from complete semantic
   payloads;
10. retain the exact input observation set in the result;
11. return exactly one in-memory immutable result; and
12. grant no authority assigned to later slices or operational phases.

---

## 6. Explicit Non-Responsibilities and Exclusions

Slice 6C-3 shall not:

- accept an analysis context, policy, individual observation, collection of
  observations, filesystem path, or persisted artifact as an alternate input;
- invoke `AcceptedBaselineClassificationService.classify` or otherwise rerun,
  revise, supplement, normalize, or reinterpret classification policy evaluation;
- reopen an accepted-baseline reference, accepted baseline, evidence artifact,
  sidecar, live source, or captured content;
- mutate the input observation set or any predecessor object;
- create a classification observation, recommendation, approved assignment, human
  decision, destination recommendation, or target design;
- infer facts that are absent from the predecessor output;
- inspect file contents or use external AI or heuristic enrichment;
- persist, serialize for publication, publish, lock, replay, or create sidecars or
  authoritative references;
- use time, host, object identity, input insertion order, filesystem order, logging,
  or execution state as semantic input;
- assign ownership, stewardship, sensitivity, retention, lifecycle, backup,
  recovery, indexing, external-AI eligibility, logical collection, or destination;
- adjudicate duplicates or equivalence;
- create directories, shares, paths, migration units, plans, waves, or runbooks;
- migrate, reconcile, redirect, clean up, delete, deduplicate, supersede, or release
  preservation retention;
- claim classification approval, target-architecture approval, phase readiness,
  production readiness, operational readiness, closeout, or certification; or
- add CLI, bootstrap, configuration, persistence, integration, authentication,
  signature, or external-service surfaces.

An excluded responsibility shall not enter implementation because it is useful to a
later slice.

---

## 7. Exact Public Input Boundary

The only public method input is:

```python
AcceptedBaselineClassificationObservationSet
```

Following the integrated predecessor service convention, the service shall accept
the declared class and its subclasses by using
`isinstance(observation_set, AcceptedBaselineClassificationObservationSet)`. It
shall reject unrelated mappings, collections, mutable substitutes, and duck-typed
values. It shall not use exact-type rejection and shall not accept raw observations
or optional override parameters.

The input carries:

- one exact observation-set identity;
- one exact accepted-baseline analysis context;
- one exact classification policy; and
- one non-empty canonically ordered tuple of observations.

The service shall perform the exact public-contract validation in Section 4.3 and
shall validate canonical observation uniqueness and ordering before generating
findings.

No external access is required or permitted.

---

## 8. Public Finding Model

The model module shall define:

```python
STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION = "1.0"
STORAGE_BASELINE_CLASSIFICATION_RESULT_SCHEMA_VERSION = "1.0"
```

### 8.1 Finding category

```python
class AcceptedBaselineClassificationFindingCategory(StrEnum):
    REVIEW_REQUIRED = "review_required"
    UNCLASSIFIED = "unclassified"
    UNKNOWN = "unknown"
    AMBIGUOUS = "ambiguous"
    CONFLICTING = "conflicting"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    UNSUPPORTED = "unsupported"
```

There is deliberately no category for `CLASSIFIED` without review or
`NOT_APPLICABLE`. Those states produce no finding.

### 8.2 Finding severity

```python
class AcceptedBaselineClassificationFindingSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"
```

Severity is analytical triage only:

- `WARNING` means human review is required but the predecessor supplied a single
  deterministic selected classification value;
- `ERROR` means the observation does not contain one unqualified deterministic
  classification value suitable for an analytically complete result.

Severity is not urgency, security impact, retention priority, operational impact,
approval outcome, or destructive authority.

### 8.3 Finding identity

```python
@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFindingIdentity:
    schema_version: str
    classification_finding_id: str
    classification_observation_set_id: str
```

The identifier format is:

```text
pbcf-<64 lowercase hexadecimal characters>
```

### 8.4 Finding

```python
@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationFinding:
    identity: AcceptedBaselineClassificationFindingIdentity
    category: AcceptedBaselineClassificationFindingCategory
    severity: AcceptedBaselineClassificationFindingSeverity
    subject: AcceptedBaselineClassificationSubject
    dimension: AcceptedBaselineClassificationDimension
    observation_kind: AcceptedBaselineClassificationObservationKind
    observation_state: AcceptedBaselineClassificationState
    candidates: tuple[AcceptedBaselineClassificationCandidate, ...]
    selected_value: str | None
    applied_rule_codes: tuple[str, ...]
    fact_references: tuple[AcceptedBaselineClassificationFactReference, ...]
    rationale_codes: tuple[str, ...]
    review_required: bool
    review_rationale_codes: tuple[str, ...]
    finding_code: str
```

Every field after severity is copied exactly from the triggering observation except
`finding_code`, which is the exact category value. No observation semantics are
normalized or discarded. A finding shall validate that its category, severity,
code, observation state, and review fields are locally permitted by the normative
mapping. Standalone finding construction proves only that local structural
validity. It cannot prove that the finding corresponds to a retained observation or
that the result contains the exhaustive finding derivation; those are result-level
invariants in Section 10.3.

---

## 9. Normative Observation-to-Finding Mapping

The mapping is exhaustive and ordered by predecessor state value:

| Observation state | Slice-semantic review treatment | Finding category | Severity | Finding code | Result contribution |
| --- | --- | --- | --- | --- | --- |
| `AMBIGUOUS` | must be true with non-empty codes | `AMBIGUOUS` | `ERROR` | `ambiguous` | blocking |
| `CLASSIFIED` | false with empty codes | none | none | none | complete |
| `CLASSIFIED` | true with non-empty codes | `REVIEW_REQUIRED` | `WARNING` | `review_required` | review |
| `CONFLICTING` | must be true with non-empty codes | `CONFLICTING` | `ERROR` | `conflicting` | blocking |
| `INSUFFICIENT_EVIDENCE` | must be true with non-empty codes | `INSUFFICIENT_EVIDENCE` | `ERROR` | `insufficient_evidence` | blocking |
| `NOT_APPLICABLE` | must be false with empty codes | none | none | none | complete |
| `UNCLASSIFIED` | must be true with non-empty codes | `UNCLASSIFIED` | `ERROR` | `unclassified` | blocking |
| `UNKNOWN` | must be true with non-empty codes | `UNKNOWN` | `ERROR` | `unknown` | blocking |
| `UNSUPPORTED` | must be true with non-empty codes | `UNSUPPORTED` | `ERROR` | `unsupported` | blocking |

Model construction and slice-semantic validation are distinct. The public
`AcceptedBaselineClassificationObservation` contract permits exactly these two
model-valid review shapes for every state:

- `review_required is false` with an empty `review_rationale_codes` tuple; or
- `review_required is true` with a non-empty, unique, lexically ordered
  `review_rationale_codes` tuple.

For every state, `false` with non-empty codes and `true` with empty codes are model-
construction failures and therefore cannot be conforming service inputs. Among the
two model-valid shapes, the table above is exhaustive: `CLASSIFIED` accepts either;
`NOT_APPLICABLE` accepts only false/empty; and every uncertainty, ambiguity,
conflict, insufficiency, or unsupported state accepts only true/non-empty. A model-
valid shape forbidden by that table is a slice-semantic structural input failure,
not a finding.

The stricter rule is supported by the integrated public policy's
`review_semantics`: classified failure or nonterminal values may require review,
verified or captured classified values need not; not-applicable does not indicate
review; and uncertainty, conflict, or unsupported states require review. Slice
6C-2's public architecture also defines review as coexisting with classified and
uncertain states while normally excluding it for not-applicable. Slice 6C-3 does
not validate the business correctness of the particular non-empty rationale codes
or derive them again from rules; it preserves them exactly and relies on the
recomputed policy and observation-set identities.

Consequently every possible `(observation_state, review_required,
review_rationale_codes emptiness)` combination has one treatment: predecessor model
failure, slice-semantic structural failure, no finding, warning finding, or the
state-specific error finding. Every conforming implementation shall make that same
derivation or raise the same public structural failure category.

There is at most one finding per observation. Multiple review rationale codes remain
inside that finding and do not produce duplicate findings. Finding derivation shall
not vary by dimension or candidate value beyond the state and review rules above.

---

## 10. Result Model and Assembly Semantics

### 10.1 Result status

```python
class AcceptedBaselineClassificationResultStatus(StrEnum):
    COMPLETE = "complete"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
```

These statuses mean only:

- `COMPLETE`: no finding was generated;
- `REVIEW_REQUIRED`: one or more `WARNING` findings and no `ERROR` finding exist;
- `BLOCKED`: one or more `ERROR` findings exist.

`BLOCKED` takes precedence over `REVIEW_REQUIRED`, which takes precedence over
`COMPLETE`. This precedence applies only after the complete finding set has been
derived. It is not rule priority and shall not suppress any finding.

The status is not an ES-1 or ES-6 lifecycle state, approval, rejection, pass/fail
certification result, migration-readiness decision, or operational-readiness result.

### 10.2 Result identity

```python
@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationResultIdentity:
    schema_version: str
    classification_result_id: str
    classification_observation_set_id: str
    analysis_context_id: str
    accepted_baseline_id: str
    analysis_profile_id: str
    classification_policy_id: str
```

The identifier format is:

```text
pbcr-<64 lowercase hexadecimal characters>
```

### 10.3 Result

```python
@dataclass(frozen=True, slots=True)
class AcceptedBaselineClassificationResult:
    identity: AcceptedBaselineClassificationResultIdentity
    status: AcceptedBaselineClassificationResultStatus
    observation_set: AcceptedBaselineClassificationObservationSet
    findings: tuple[AcceptedBaselineClassificationFinding, ...]
    warning_count: int
    error_count: int
```

The result directly retains the exact observation set. Counts are deterministic
derived summaries and must equal the number of findings with the corresponding
severity. No finding-free result may have a nonzero count. A result may contain an
empty findings tuple only when its status is `COMPLETE`.

The result boundary shall additionally enforce all of these invariants:

1. each finding maps to exactly one retained observation by the predecessor key
   `(source_root_id, relative_path, item_id, dimension, observation_kind)`;
2. the finding's subject, dimension, observation kind, observation state,
   candidates, selected value, applied rule codes, fact references, rationale
   codes, review-required flag, and review-rationale codes equal the triggering
   observation fields exactly;
3. each retained observation produces exactly the Section 9 zero-or-one finding;
4. no finding exists for a non-triggering observation and no triggering observation
   is omitted or represented more than once; and
5. the result's complete findings tuple equals the canonically ordered exhaustive
   derivation from the result's complete retained observation tuple.

These invariants, including linkage and exhaustive completeness, shall be checked
when constructing any result, not only by the assembler's procedural path.

### 10.4 Assembly behavior

Assembly shall:

1. validate the entire observation set before deriving any output;
2. traverse observations in their already-canonical order;
3. derive findings using only Section 9;
4. sort findings by the canonical key in Section 13;
5. calculate warning and error counts;
6. derive status using Section 10.1;
7. calculate the result identity; and
8. construct and return the immutable result.

No partial result is returned. Structural or identity failure raises a typed error
and preserves the cause.

---

## 11. Deterministic Finding Identity

`stable_accepted_baseline_classification_finding_id` shall compute SHA-256 over
compact canonical JSON with UTF-8 encoding, sorted object keys, no insignificant
whitespace, and no ASCII coercion. The semantic payload shall include:

- finding schema version;
- classification observation-set ID;
- category;
- severity;
- complete subject tuple;
- dimension;
- observation kind;
- observation state;
- complete ordered candidates and candidate rule codes;
- selected value including explicit null;
- complete applied rule codes;
- complete ordered fact references and every fact-reference field;
- complete rationale codes;
- review-required Boolean;
- complete review rationale codes; and
- finding code.

The function returns `pbcf-` followed by the lowercase digest.

No timestamp, host, object identity, service identity, path outside the subject's
semantic relative path, transport digest, log value, persistence state, or output
position enters the identity.

Two semantically equal findings must have equal identities. Any change to finding
semantics or predecessor identity must change the finding identity.

---

## 12. Deterministic Result Identity

`stable_accepted_baseline_classification_result_id` shall use the same compact
canonical JSON rules. Its semantic payload shall include:

- result schema version;
- classification observation-set ID;
- analysis-context ID;
- accepted-baseline ID;
- analysis-profile ID;
- classification-policy ID;
- result status;
- ordered finding IDs; and
- warning and error counts.

The complete observation semantics remain bound through the independently
recomputed observation-set ID; each finding additionally binds its triggering
observation semantics. The function returns `pbcr-` followed by the lowercase
digest.

No operational metadata enters the identity. Equal validated observation sets shall
produce equal results and identities across repeated construction and process runs.

---

## 13. Canonical Ordering

Predecessor observation order remains:

```text
(source_root_id, relative_path, item_id, dimension.value, observation_kind.value)
```

Finding order is:

```text
(
  source_root_id,
  relative_path,
  item_id,
  dimension.value,
  observation_kind.value,
  category.value,
  severity.value,
  classification_finding_id,
)
```

Candidates, rule codes, fact references, rationale codes, and review rationale codes
must retain the canonical order validated by Slice 6C-2. Slice 6C-3 shall not resort
or normalize nested predecessor collections except to verify their exact ordering.

Duplicate finding semantic keys or duplicate finding identities fail construction.
Dictionary iteration, set iteration, locale, filesystem order, execution order, and
object identity shall never determine output order.

---

## 14. Complete Lineage and Scope Preservation

The result retains the exact input observation set. Each finding retains the exact
subject and compact fact, rule, rationale, candidate, state, and review lineage of
its triggering observation.

The result identity repeats the predecessor's principal identity keys for direct
review:

- classification observation-set ID;
- analysis-context ID;
- accepted-baseline ID;
- analysis-profile ID; and
- classification-policy ID.

Those keys must agree with the nested object graph. A repeated key is a consistency
check, not a substitute for retained lineage.

Accepted and excluded source-root scope remains governed by the retained analysis
context. Slice 6C-3 shall neither widen accepted scope nor create findings for
excluded-root content absent from the observation set. It shall not collapse
provenance for byte-identical items.

---

## 15. Public Service Contract

The public service is:

```python
AcceptedBaselineClassificationResultAssembler
```

with exactly one public method:

```python
def assemble(
    self,
    observation_set: AcceptedBaselineClassificationObservationSet,
) -> AcceptedBaselineClassificationResult: ...
```

The service constructor accepts no policy, registry, publisher, loader, clock,
filesystem, configuration, network, database, AI, or other dependency. The complete
finding policy is fixed by this architecture and implemented deterministically in
code.

The assembler has no alternative public method for findings alone. Findings and the
result are produced atomically in memory from one input.

---

## 16. Failure Taxonomy

The public service hierarchy is:

```python
AcceptedBaselineClassificationResultError(RuntimeError)
AcceptedBaselineClassificationObservationSetError(AcceptedBaselineClassificationResultError)
AcceptedBaselineClassificationFindingError(AcceptedBaselineClassificationResultError)
AcceptedBaselineClassificationResultAssemblyError(AcceptedBaselineClassificationResultError)
```

Use:

- `AcceptedBaselineClassificationObservationSetError` for wrong input type,
  predecessor identity mismatch, malformed ordering, duplicate observation keys,
  nested context or policy inconsistency, or impossible observation state;
- `AcceptedBaselineClassificationFindingError` when a structurally valid
  observation cannot produce the architecture-required finding consistently; and
- `AcceptedBaselineClassificationResultAssemblyError` for impossible finding-set,
  count, status, or result-identity combinations.

Known public errors pass through unchanged. Wrapped `TypeError` and `ValueError`
failures shall preserve their causal chain. Errors shall not include absolute paths,
content, or unnecessary sensitive lineage.

No fallback result, partial result, guessed category, default success status, or
silently omitted finding is allowed.

---

## 17. Package Exports

Only these new model names may be exported from
`poe_backup_orchestrator.models`:

- `STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION`;
- `STORAGE_BASELINE_CLASSIFICATION_RESULT_SCHEMA_VERSION`;
- `AcceptedBaselineClassificationFindingCategory`;
- `AcceptedBaselineClassificationFindingSeverity`;
- `AcceptedBaselineClassificationResultStatus`;
- `AcceptedBaselineClassificationFindingIdentity`;
- `AcceptedBaselineClassificationFinding`;
- `AcceptedBaselineClassificationResultIdentity`;
- `AcceptedBaselineClassificationResult`;
- `stable_accepted_baseline_classification_finding_id`; and
- `stable_accepted_baseline_classification_result_id`.

Only these new service names may be exported from
`poe_backup_orchestrator.services`:

- `AcceptedBaselineClassificationResultError`;
- `AcceptedBaselineClassificationObservationSetError`;
- `AcceptedBaselineClassificationFindingError`;
- `AcceptedBaselineClassificationResultAssemblyError`; and
- `AcceptedBaselineClassificationResultAssembler`.

Private helpers, ordering keys, canonical serializers, mapping tables, regular
expressions, and behavior constants shall not be package exports.

The package root, CLI, bootstrap, and configuration surfaces shall not change.

---

## 18. Domain and Dependency Direction

The finding and result models belong in the domain-model layer. They may import
immutable public models from `storage_baseline_classification` but shall not import
services, filesystem facilities, CLI code, bootstrap code, persistence adapters, or
external integrations.

The result assembler belongs in the service layer and may consume the immutable
domain models and stable identity functions. It shall not duplicate predecessor
classification logic or introduce domain behavior into package initializers.

Dependency direction remains:

```text
storage_baseline_analysis models
        ↓
storage_baseline_classification models
        ↓
storage_baseline_classification_findings models
        ↓
storage_baseline_classification_findings service
```

No reverse dependency is authorized.

---

## 19. Persistence and Publication Boundary

Slice 6C-3 is computation-only. It writes no result artifact, finding report,
sidecar, reference, database row, cache, log record, or NAS state. It uses no lock
and makes no idempotent-replay claim. Repeated assembly is deterministic
recomputation.

Slice 6C-4 separately owns canonical serialization, persistence, SHA-256 sidecars,
authoritative reference publication, replay, locking, durability, permissions,
partial-state recovery, and immutable conflicts. Nothing in this architecture
selects 6C-4 filenames or persistence paths.

---

## 20. Human Approval and Negative Authority

All outputs are non-authoritative analytical evidence:

- a finding is not a human review disposition;
- `WARNING` is not approval or rejection;
- `ERROR` is not a certification failure or operational incident;
- `COMPLETE` is not classification approval or readiness;
- `REVIEW_REQUIRED` does not record that review occurred;
- `BLOCKED` does not change ES-1 or ES-6 lifecycle state;
- result assembly does not assign an owner, retention period, sensitivity,
  destination, or authoritative copy;
- result assembly does not authorize persistence or publication; and
- no finding or result grants migration, redirection, cleanup, deletion,
  deduplication, supersession, or retention-release authority.

Human classification and target-architecture approval remains Slice 6C-6. Later
approval shall consume separately published evidence under separately approved
architecture; it shall not be inferred from this in-memory result.

---

## 21. Security and Privacy Controls

The slice shall:

- operate only on already-authenticated semantic objects in memory;
- perform no filesystem, source-content, captured-content, network, or external
  service access;
- retain only predecessor lineage already present in the input;
- avoid absolute transport paths and evidence content in error messages;
- avoid logging facts, paths, candidates, or findings as a required behavior;
- use no environment-derived semantic input;
- preserve immutable input objects; and
- fail closed on malformed, contradictory, or unsupported state.

Relative paths retained in subjects and fact references are governed semantic
lineage. Their presence does not authorize filesystem access.

---

## 22. Architecture-Traceable Test Strategy

### 22.1 Model tests

Focused model tests shall prove:

- both schema versions are exact;
- `pbcf-` and `pbcr-` formats are enforced;
- models are frozen and slotted;
- the finding category, severity, and result-status vocabularies are exact and
  closed;
- standalone findings validate only their locally normative category, severity,
  code, state, review, field shapes, and identity;
- result construction validates exact finding-to-observation linkage, copied-field
  equality, exhaustive zero-or-one derivation, canonical ordering, counts, and
  status;
- nested collections must be immutable tuples;
- canonical uniqueness and ordering are enforced;
- finding identity is stable and sensitive to every semantic field;
- result identity is stable and sensitive to status, predecessor identities,
  finding identities, and counts; and
- the model module has no service dependency.

### 22.2 Complete mapping tests

Parameterized tests shall exercise every row of Section 9, including:

- classified without review produces no finding;
- classified with review produces one warning finding;
- ambiguous, conflicting, insufficient-evidence, unclassified, unknown, and
  unsupported states each produce exactly one error finding;
- not-applicable without review produces no finding;
- impossible review/state combinations fail closed; and
- multiple review rationale codes remain one finding.

The matrix tests shall separately cover model-construction failure for false with
non-empty codes and true with empty codes, and slice-semantic failure for each
model-valid review shape forbidden by Section 9.

Every test shall verify retained subject, candidate, rule, rationale, review, and
fact-reference lineage.

### 22.3 Result-assembly tests

Service success tests shall prove:

- one exact observation set is accepted;
- an all-clear observation set produces `COMPLETE` with no findings;
- warning-only findings produce `REVIEW_REQUIRED`;
- any error finding produces `BLOCKED` without suppressing warnings;
- the complete retained observation tuple produces the exhaustive architecture-
  defined zero-or-one finding tuple;
- findings use canonical ordering;
- repeated assembly returns equal objects and identities;
- the exact input observation set is retained; and
- warning and error counts are exact.

### 22.4 Boundary and tamper tests

Tests shall prove failure for:

- wrong input type;
- tampered observation-set identity;
- mismatched context, baseline, profile, or policy identity;
- analysis-profile, analysis-context, classification-policy, and observation-set
  semantic payload tampering detectable by the four public identity functions in
  Section 4.3;
- every repeated nested identity relationship listed in Section 4.3;
- duplicate or noncanonical observations;
- duplicate finding keys or identities;
- invalid state/candidate/selected-value combinations;
- invalid review flag and review-code combinations;
- invalid category, severity, finding code, count, or status; and
- identity payload drift.

Wrapped failures shall retain their cause.

### 22.5 Negative-authority tests

Static and behavioral tests shall prove:

- no filesystem, publisher, loader, persistence, lock, clock, network, AI, CLI,
  configuration, or database dependency;
- classification is not rerun;
- no predecessor private-helper dependency or copied private-helper implementation;
- no input mutation;
- no raw-observation alternate API;
- declared input subclasses are accepted while unrelated duck-typed values are
  rejected;
- no persistence or publication method;
- no approval, assignment, destination, migration, cleanup, deletion,
  certification, or operational-readiness surface;
- only approved public package exports; and
- models do not depend on services.

### 22.6 Regression tests

Existing Slice 6C-1 and 6C-2 focused tests shall remain passing. The full repository
suite shall run because exports and package import boundaries are modified.

---

## 23. Quality Gates

During an authorized implementation, focused tests shall be:

```bash
source .venv/bin/activate
pytest -q tests/unit/test_storage_baseline_classification_findings_models.py
pytest -q tests/unit/test_storage_baseline_classification_findings.py
pytest -q \
  tests/unit/test_storage_baseline_analysis_models.py \
  tests/unit/test_storage_baseline_analysis.py \
  tests/unit/test_storage_baseline_classification_models.py \
  tests/unit/test_storage_baseline_classification.py \
  tests/unit/test_storage_baseline_classification_findings_models.py \
  tests/unit/test_storage_baseline_classification_findings.py
```

The full repository quality gate is:

```bash
source .venv/bin/activate
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Before any separately authorized commit, also run:

```bash
git diff --cached --check
```

Gate evidence shall identify exact commands, subjects, completion, and exit status.
Passing gates do not establish architecture conformance, approval, implementation
authority, repository authority, or certification.

---

## 24. Repository Scope

### 24.1 Architecture-revision changed-file scope

Exactly one file:

```text
ADD docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C3.md
```

No other mutation is authorized by the architecture-revision decision.

### 24.2 Proposed later implementation changed-file scope

Subject to architecture review, explicit architecture approval, and separate exact
implementation authorization, the complete proposed scope is exactly six files:

```text
ADD    src/poe_backup_orchestrator/models/storage_baseline_classification_findings.py
MODIFY src/poe_backup_orchestrator/models/__init__.py
ADD    src/poe_backup_orchestrator/services/storage_baseline_classification_findings.py
MODIFY src/poe_backup_orchestrator/services/__init__.py
ADD    tests/unit/test_storage_baseline_classification_findings_models.py
ADD    tests/unit/test_storage_baseline_classification_findings.py
```

No architecture-document modification is part of implementation. Semantic
architecture changes during implementation are prohibited. A later precisely
bounded metadata-only update would require a separately named lifecycle
responsibility and authority; none is presumed here. Any required implementation
scope expansion shall stop implementation and return to architecture review. This
proposed scope is not current implementation authorization.

---

## 25. Acceptance Criteria

Implementation may be accepted only when evidence proves:

1. exactly one valid `AcceptedBaselineClassificationObservationSet` is accepted;
2. the four public predecessor identities and every repeated relationship in
   Section 4.3 are recomputed and validated within the stated attainable boundary;
3. classification is not rerun and no external evidence is opened;
4. the complete mapping in Section 9 is implemented exactly;
5. every eligible observation produces exactly zero or one finding;
6. all triggering semantics and lineage are retained without normalization, every
   finding links to exactly one observation with exact copied fields, and the result
   enforces exhaustive zero-or-one derivation;
7. finding and result identities cover their complete semantic payloads;
8. findings are unique and canonically ordered;
9. result counts and status are deterministic and internally consistent;
10. `BLOCKED`, `REVIEW_REQUIRED`, and `COMPLETE` remain analytical and
    non-authoritative;
11. repeated assembly produces equal objects and identities;
12. malformed, tampered, contradictory, and impossible inputs fail closed with typed
    errors and preserved causes;
13. input objects are not mutated;
14. no persistence, publication, approval, destination, migration, cleanup,
    destructive, certification, or external-integration behavior exists;
15. only approved public exports are added;
16. dependency direction remains correct;
17. the exact six-file implementation scope is preserved and the architecture
    document is not changed during implementation;
18. focused and full quality gates pass; and
19. independent human review separately determines architectural conformance and
    implementation approval.

Criteria satisfaction is evidence only and grants no later authority.

---

## 26. Review Requirements

Architecture review shall determine whether:

- the result is independently useful without crossing into approval or readiness;
- the seven-category finding vocabulary is complete and minimal;
- warning and error meanings are conservative and authority-neutral;
- the Section 9 mapping is exhaustive and has no hidden default;
- zero-or-one finding cardinality preserves all review rationale;
- result status precedence is complete and non-lossy;
- identity payloads bind all semantic dependencies;
- canonical ordering is total and deterministic;
- retained lineage is sufficient for Slice 6C-4 without selecting persistence
  design;
- service and failure contracts are narrow;
- public exports are necessary and sufficient;
- tests cover positive, negative, tamper, lineage, and authority boundaries;
- the exact implementation scope is sufficient; and
- predecessor and later-slice boundaries remain unchanged.

A fresh independent architecture-review responsibility is required. The preparer
shall not treat this draft or successful quality gates as approval.

---

## 27. Authority Effect, Lifecycle, and Closeout

Approval of this architecture, if later granted, would approve only the design in
this document. It would not authorize implementation.

Separate accountable-human implementation authorization must name:

- this exact architecture revision;
- the exact repository and baseline;
- the exact six-file implementation scope;
- the `IMPLEMENTATION` ES-6 responsibility;
- permitted outputs and required gates; and
- all authority withheld.

Implementation completion would not approve implementation. Implementation review
would not authorize commit. Commit would not authorize publication. Publication
would not authorize integration. Integration would not close or certify the slice.

Slice closeout, if required, shall record the approved architecture, implementation
authority, exact integrated identity, review and gate evidence, residual risks,
discrepancies, and authority withheld. Phase 6C certification remains separate and
later.

---

## 28. Discrepancies and Historical Evidence

The following discrepancies remain visible:

1. The older Phase 6 roadmap labels classification and target architecture as Phase
   6B and controlled migration as Phase 6C. The later Phase 6C parent architecture
   and integrated product sequence govern this slice prospectively.
2. The Phase 6C parent metadata retains proposed-for-review wording despite later
   integration and successor implementation history.
3. Slice 6C-1 retains implementation-review wording despite integration.
4. Slice 6C-2 retains `IMPLEMENTATION_IN_REVIEW` wording despite its implementation
   and merge being reachable from the current baseline.
5. Repository Knowledge is bounded to an earlier observation commit and does not
   include later integrated ES-5 and ES-6 documentation.
6. A public observation set can receive the structural and semantic-identity
   validation in Section 4.3, but that validation does not attest the constructing
   service invocation or independently prove correct observation derivation.

These discrepancies do not authorize rewriting predecessor artifacts or Git history.
They shall remain evidence for architecture review. If review determines that one
prevents safe prospective use of the predecessor contract, the architecture shall be
blocked rather than silently reconciled.

---

## 29. Deferred Responsibilities and Residual Risks

Deferred responsibilities include:

- Slice 6C-4 persistence and publication;
- Slice 6C-5 logical architecture and destination recommendations;
- Slice 6C-6 human classification and target-architecture approval;
- Slice 6C-7 approved evidence publication;
- Phase 6C closeout and certification;
- Phase 6D duplicate analysis and migration planning;
- migration, redirection, cleanup, retention release, and operational work; and
- external AI, signatures, authentication, and external integrations.

Residual risks are:

- metadata-only predecessor classification may require substantial human review;
- a warning/error vocabulary can be misread as business urgency or operational
  severity outside its defined scope;
- `COMPLETE` can be misread as approval unless consumers preserve its explicit
  analytical meaning;
- retaining the complete predecessor object graph retains sensitive path and
  provenance metadata in memory; and
- future taxonomy evolution will require new architecture and schema identities.

These risks require clear naming, tests, review, and later controlled publication.
They do not justify expanding this slice.

---

## 30. Machine-Checkable Requirements

Machine-checkable implementation evidence shall establish:

- exact schema versions and identifier grammars;
- immutable tuple boundaries;
- closed enumeration values;
- exhaustive state mapping;
- category, severity, code, and state agreement;
- canonical identity serialization;
- exact identity recomputation;
- canonical ordering and uniqueness;
- exact warning/error counts and status derivation;
- `isinstance` input boundaries, subclass acceptance, duck-type rejection, and
  public signatures;
- approved package export sets;
- absence of service imports from models;
- absence of prohibited external and later-authority dependencies;
- exact changed-file scope; and
- focused and full quality-gate results.

Machine checks cannot decide architectural sufficiency, approve the architecture or
implementation, interpret business meaning, grant repository authority, or certify
the slice.

---

## 31. Accountable-Human Judgment Requirements

Accountable-human review and decisions remain required for:

- whether the finding taxonomy and mapping represent the intended product policy;
- whether warning, error, and result statuses are appropriately named and bounded;
- whether identity and lineage semantics are sufficient;
- whether the architecture preserves predecessor and parent intent;
- whether exclusions and deferred responsibilities are complete;
- whether test and review requirements are proportionate;
- whether this architecture should be approved;
- whether exact implementation should later be authorized;
- whether an implementation candidate conforms and should be approved;
- whether any repository transition should occur; and
- whether the slice should later close or enter phase certification evidence.

No automated result or model output substitutes for these decisions.

---

## 32. Deterministic Specification Invariants

This architecture preserves these invariants:

1. architecture precedes implementation;
2. evidence and evaluation never grant authority;
3. exactly one observation set is the public input;
4. predecessor classification semantics are not rerun or redefined;
5. every predecessor observation has exactly one architecture-defined mapping;
6. every triggering observation produces exactly one finding;
7. no non-triggering observation produces a finding;
8. findings preserve complete triggering semantics and lineage;
9. identities cover complete semantic payloads;
10. canonical order is independent of execution and input incidental order;
11. an error finding cannot be hidden by a warning or complete observation;
12. analytical status remains distinct from lifecycle, approval, readiness, and
    certification;
13. no persistence or later authority enters Slice 6C-3;
14. unknown and contradictory states fail visibly and conservatively;
15. product models do not depend on services; and
16. authority for one lifecycle responsibility grants no later responsibility.

---

## 33. Architecture-Revision Checkpoint

The targeted revision dispositions are:

- `F-6C3-001` — dispositioned by Sections 4.3, 4.5, 5, 7, 22, 25, 28, and 30:
  validation is limited to named public identity functions, explicit relationship
  checks, and structural rules; historical invocation, derivation attestation, and
  policy re-execution claims are excluded, as are private-helper dependencies.
- `F-6C3-002` — dispositioned by Section 9 and its tests: model validity is
  separated from slice-semantic validity, public policy evidence supports the
  stricter rules, and the state/review/code-emptiness matrix has one treatment for
  every combination.
- `F-6C3-003` — dispositioned by Sections 8.4, 10.3, 10.4, 22, and 25: standalone
  findings prove local structure only; the result proves unique observation-key
  linkage, exact copied fields, zero-or-one derivation, and exhaustive completeness.
- `F-6C3-004` — dispositioned by Sections 7, 22, and 30: the unconditional public
  rule is predecessor-conventional `isinstance` acceptance, including subclasses,
  with unrelated duck types rejected.
- `F-6C3-005` — dispositioned by Sections 24 through 27: later implementation is
  exactly six files, excludes this architecture document, and prohibits semantic
  architecture changes during implementation.

The architecture-revision responsibility is complete when:

- this single-file candidate exists;
- its exact diff is inspected;
- applicable documentation quality gates are recorded;
- no other repository file changed;
- unresolved review questions and discrepancies remain explicit;
- implementation authority remains withheld; and
- the next recommended responsibility is fresh independent
  `ARCHITECTURE_REVIEW`, without authorization implication.

This checkpoint is not architecture approval and does not change ES-1 beyond
`ARCHITECTURE_DRAFT`.

---

## 34. Final Posture and Architectural Decision

**Document status:** Revised architecture draft; prepared for fresh independent
review

**ES-1 lifecycle state:** `ARCHITECTURE_DRAFT`

**ES-6 responsibility state:** `ARCHITECTURE_REVISION`

**Implementation authorization:** Withheld

Revised architectural proposal: Slice 6C-3 is an immutable deterministic in-memory boundary
that consumes exactly one valid integrated Slice 6C-2 observation set, derives typed
findings through one exhaustive state mapping, assembles one authority-neutral
classification result, preserves complete policy, evidence, scope, and baseline
lineage, and performs no persistence, publication, approval, destination, migration,
cleanup, destructive, operational, or certification behavior.

This proposal governs no implementation until it receives fresh independent
architecture review, explicit accountable-human architecture approval, and a
separate accountable-human implementation authorization naming the exact approved
scope.
