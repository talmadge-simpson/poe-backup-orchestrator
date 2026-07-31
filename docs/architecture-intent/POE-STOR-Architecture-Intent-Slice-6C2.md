# POE Storage Architecture Intent — Slice 6C-2

## Deterministic Classification Policy and Observation

**System identifier:** `POE-STOR`

**Slice identifier:** `6C-2`

**Specification identifier:** `POE-STOR-Architecture-Intent-Slice-6C2`

**Specification version:** `1.0`

**Document status:** Approved architecture; implementation in review

**ES-1-aligned lifecycle state:** `IMPLEMENTATION_IN_REVIEW`

**Artifact class:** Product architecture artifact

**Governed subject:** Deterministic classification policy and observation

**Governing parent:** Phase 6C — Classification and Destination Design

**Predecessor:** Slice 6C-1 — Accepted-Baseline Analytical Intake and Evidence
Authentication

**Repository baseline inspected:** `main` at
`d4ae9b0effa1deb9ebf7dda6f3461d20effda8cf`

**Regression baseline:** 944 tests passing

**Implementation authorization:** Granted by explicit human approval

---

## 1. Purpose and Independently Useful Outcome

Slice 6C-2 consumes exactly one valid immutable
`AcceptedBaselineAnalysisContext`, validates its semantic identity and profile
identity, applies one constructor-supplied immutable deterministic classification
policy, and returns one immutable deterministic
`AcceptedBaselineClassificationObservationSet`.

The output provides item-level descriptive classification observations, explicit
uncertainty and conflict states, review requirements, rule lineage, fact lineage,
and complete predecessor-context lineage. It is independently useful because Slice
6C-3 can generate findings from the retained observations without reopening
evidence or rerunning classification. It is independently reviewable and mergeable
because it is in-memory computation only and grants no persistence, approval,
destination, migration, cleanup, or destructive authority.

The governing preservation rule remains:

> We do not restructure the only copy of anything.

---

## 2. Governance, Ownership, and Lifecycle

This product slice is governed by:

- `AGENTS.md`;
- `Engineering-Kernel.md` version 1.0;
- `Slice-Specification-Standard.md` version 1.0, applied as specification
  discipline without creating a product-runtime dependency;
- `POE-STOR-MIG-001-Preservation-Baseline-Standard.md`;
- the Phase 6 and Phase 6C parent architectures; and
- the approved and integrated Slice 6C-1 architecture and implementation.

The Engineering System governs engineering work and does not enter product models,
services, imports, configuration, CLI, or runtime behavior. This document adopts
ES-1 conventions for identity, lifecycle, dependencies, exact repository scope,
discrepancy handling, authority effect, review, and closeout. It remains a
product-owned architecture artifact.

Architecture preparation creates review evidence only. The current lifecycle state
grants no implementation, commit, push, merge, closeout, certification, migration,
or operational authority.

---

## 3. Parent Context and Architectural Position

```text
AcceptedPreservationBaselineArtifact
        ↓ governed dependency, not authority transfer
AcceptedBaselineAnalysisContext — Slice 6C-1
        ↓ semantic revalidation and deterministic policy application
AcceptedBaselineClassificationObservationSet — Slice 6C-2
        ↓ later governed dependency
Classification Findings and Result — Slice 6C-3
```

Authentication is not classification. Classification observation is not a finding.
A finding is not approval. Approval is not destination authority. Destination
approval is not migration authority. Migration is not cleanup authority.

---

## 4. Predecessor, Dependencies, and Assumptions

### 4.1 Predecessor evidence

The immediate predecessor is Slice 6C-1. This slice relies on its public contracts:

- `AcceptedBaselineAnalysisContext`;
- `AcceptedBaselineAnalysisProfile`;
- `AcceptedBaselineAnalysisEvidence`;
- `FrozenJsonObject` and `FrozenJsonArray` semantics;
- `stable_accepted_baseline_analysis_profile_id`; and
- `stable_accepted_baseline_analysis_context_id`.

The predecessor must be present in the repository state and the supplied context
must satisfy its exact schema, ordering, identity, scope, and lineage invariants. A
missing, malformed, stale, contradictory, or unsupported dependency fails closed.

### 4.2 Other dependencies

The policy depends only on semantic fields authenticated and projected by Slice
6C-1. It has no filesystem, evidence-loader, publisher, registry, clock, taxonomy,
network, AI, database, CLI, or configuration dependency.

### 4.3 Assumptions

No hidden input is assumed. The public context's semantic validity does not
cryptographically attest which service invocation constructed it. This slice
recomputes its governed identities but introduces no signature, token, private
constructor, authentication, or attestation mechanism. If invocation attestation
becomes required, implementation must stop for new architecture.

---

## 5. Exact Responsibility

Slice 6C-2 shall:

1. accept exactly one `AcceptedBaselineAnalysisContext`;
2. recompute and validate its analysis-context and analysis-profile identities;
3. validate nested semantic evidence identities required by Slice 6C-1;
4. apply exactly one immutable constructor-supplied classification policy;
5. derive subjects only from authenticated inventory semantic facts;
6. reconcile file subjects to authenticated integrity facts already in memory;
7. apply the normative rules in deterministic order;
8. preserve explicit uncertainty, conflict, and review states;
9. preserve complete subject, fact, rule, policy, context, and predecessor lineage;
10. construct exactly one deterministic observation set for one context/policy pair;
    and
11. return the observation set directly.

---

## 6. Explicit Non-Responsibilities and Exclusions

Slice 6C-2 shall not:

- reopen accepted-baseline or evidence artifacts;
- inspect source or captured content;
- accept caller-assembled facts, mappings, mutable models, per-call policies,
  per-call dimensions, thresholds, or overrides;
- create findings, severities, pass/fail results, readiness decisions, or phase
  status;
- assign authoritative classifications;
- persist, publish, serialize publication artifacts, write sidecars, create
  references, use locks, or claim replay;
- perform human approval;
- define logical or physical destinations;
- create directories, shares, reservation files, or NAS state;
- analyze duplicates, equivalence, or canonical copies;
- plan or execute preservation or migration;
- redirect clients;
- authorize or execute cleanup;
- delete, move, rename, deduplicate, restructure, or mutate source data;
- release retention or execute supersession; or
- use AI, LLMs, networks, cloud services, databases, subprocesses, CLI,
  configuration, dynamic imports, or external integrations.

---

## 7. Exact Public Input Boundary

The public method accepts exactly one:

```python
AcceptedBaselineAnalysisContext
```

It must reject:

- `AcceptedPreservationBaselineArtifact`;
- `AcceptedPreservationBaseline`;
- raw inventory or content-integrity evidence;
- mappings, lists, or caller-assembled fact structures;
- mutable or duck-typed substitutes;
- per-call policy, dimension, threshold, or override inputs; and
- filesystem or source-content paths.

Before evaluation, the service must independently reproduce:

1. the nested analysis-profile identity from its complete semantic profile;
2. each authenticated evidence semantic identity from its explicit frozen semantic
   JSON value;
3. the analysis-context identity from the complete governed semantic payload; and
4. the exact relationship among context, profile, accepted baseline, evidence, and
   lineage identities.

A mismatch raises `AcceptedBaselineClassificationContextError` before any rule is
evaluated. Revalidation proves model conformance, not historical service invocation.

---

## 8. Exact Public Output

The service returns directly:

```python
AcceptedBaselineClassificationObservationSet
```

The result contains:

- the exact predecessor `AcceptedBaselineAnalysisContext`;
- the exact `AcceptedBaselineClassificationPolicy`; and
- canonically ordered observations.

It contains no execution timestamp, host, persistence or publication path, replay
or cache indicator, lock result, approval result, or report path. No operational
result wrapper is approved.

---

## 9. Observation, Recommendation, Finding, and Authority

- A **source fact** is an authenticated Slice 6C-1 semantic value.
- A **classification observation** is a deterministic policy-governed
  interpretation of authenticated facts.
- A **classification recommendation** is a non-authoritative proposed value.
- A **finding** is a Slice 6C-3 output.
- An **approval** is a Slice 6C-6 accountable-human decision.
- An **assignment** is authoritative state not produced by Slice 6C-2.

The initial four dimensions produce descriptive observations only. No ownership,
retention, sensitivity, destination, migration, cleanup, or other recommendation is
approved by this slice.

Each observation contains:

- subject identity;
- dimension;
- observation kind;
- classification state;
- retained candidate values;
- selected value only when exactly one approved value exists;
- applied rule codes;
- semantic fact references;
- rationale codes;
- `review_required`; and
- ordered `review_rationale_codes`.

---

## 10. Initial Classification Taxonomy

Exactly four dimensions are approved.

### 10.1 `CONTENT_TYPE`

Descriptive observation only. Closed values:

- `FILE`;
- `DIRECTORY`;
- `UNSUPPORTED_OBJECT`; and
- `OTHER`.

This dimension describes evidence-declared inventory object form only. It does not
infer MIME type, business meaning, file format from extension, information domain,
or application ownership.

### 10.2 `INVENTORY_SUPPORT_STATE`

Descriptive observation only. Closed values:

- `SUPPORTED`; and
- `UNSUPPORTED`.

### 10.3 `CAPTURE_STATE`

Descriptive observation only. Closed values preserve the exact inventory vocabulary:

- `CAPTURED`;
- `EXCLUDED`;
- `INACCESSIBLE`;
- `ERROR`;
- `PENDING`; and
- `NOT_APPLICABLE`.

No capture status may be normalized, collapsed, or reinterpreted.

### 10.4 `CONTENT_INTEGRITY_STATE`

Descriptive observation only. Closed values preserve the exact integrity vocabulary:

- `VERIFIED`;
- `SOURCE_CHANGED`;
- `SIZE_MISMATCH`;
- `DIGEST_MISMATCH`;
- `MISSING`;
- `INACCESSIBLE`;
- `NOT_REGULAR_FILE`;
- `FILESYSTEM_ERROR`;
- `NOT_APPLICABLE`; and
- `INSUFFICIENT_EVIDENCE`.

Integrity describes preservation evidence condition only and authorizes no
exclusion, deletion, migration, cleanup, or source mutation.

---

## 11. Review Requirement Is Orthogonal

`POLICY_REVIEW_SIGNAL` is not a classification dimension. Review is represented by:

```text
review_required: bool
review_rationale_codes: tuple[str, ...]
```

Review may coexist with `CLASSIFIED`, `UNKNOWN`, `AMBIGUOUS`, `CONFLICTING`,
`INSUFFICIENT_EVIDENCE`, or `UNSUPPORTED`. `NOT_APPLICABLE` normally has
`review_required=False`. Review-required state does not record that review occurred
and grants no approval authority.

---

## 12. Classification States

The closed states are:

- `CLASSIFIED`: exactly one approved candidate value is supported;
- `UNCLASSIFIED`: subject and dimension are supported and applicable, required
  facts exist, but no approved rule yields a candidate;
- `UNKNOWN`: an authenticated source fact explicitly records an unknown value;
- `AMBIGUOUS`: multiple compatible candidates remain and policy cannot select one;
- `CONFLICTING`: mutually exclusive candidates are supported;
- `INSUFFICIENT_EVIDENCE`: required semantic facts or cross-evidence linkage are
  absent;
- `UNSUPPORTED`: subject form or source value lies outside approved policy support;
  and
- `NOT_APPLICABLE`: the dimension does not apply to the subject.

`UNCLASSIFIED` must not substitute for another state. Governed uncertainty and
policy conflict normally produce valid explicit observations, not exceptions.

---

## 13. Deferred Dimensions

The following are explicitly deferred and no placeholder defaults may be emitted:

- information domain;
- business or personal purpose;
- project or system affiliation;
- authoritative status;
- lifecycle recommendation beyond exact recorded state;
- sensitivity and handling;
- retention recommendation;
- recovery priority;
- backup policy;
- indexing eligibility;
- external-AI eligibility;
- ownership and stewardship;
- logical collection;
- destination domain; and
- quarantine assignment.

Current authenticated facts cannot safely establish these values, governed
taxonomies and approval policies do not yet exist, several belong to Slice 6C-5,
and content inspection and external AI remain prohibited. Filesystem owner metadata
does not establish accountable ownership. Inherited retention remains lineage and
cannot be shortened or released. Unknown sensitivity must not become low
sensitivity.

---

## 14. Classification Granularity and Cardinality

Classification occurs at inventory-item granularity. Subjects are derived only from
authenticated inventory semantic facts.

- Supported files receive all applicable observations.
- Directories receive inventory observations and `NOT_APPLICABLE` integrity.
- Unsupported inventory objects receive explicit supported-form and unsupported
  policy states as defined by the rule table.
- File integrity requires exact inventory/integrity item and path linkage.
- Lineage-only evidence is not classified.
- No logical group or synthetic collection is created.

The cardinality invariant is:

```text
one analysis_context_id
+ one exact classification_policy_id
→ one classification_observation_set_id
```

Repeated application performs deterministic recomputation and returns equal objects.
It is not persistence replay.

---

## 15. Public Model Surface

The approved public model surface is:

- `STORAGE_BASELINE_CLASSIFICATION_POLICY_SCHEMA_VERSION`;
- `STORAGE_BASELINE_CLASSIFICATION_SCHEMA_VERSION`;
- `AcceptedBaselineClassificationPolicyIdentity`;
- `AcceptedBaselineClassificationObservationSetIdentity`;
- `AcceptedBaselineClassificationDimension`;
- `AcceptedBaselineClassificationObservationKind`;
- `AcceptedBaselineClassificationState`;
- `AcceptedBaselineClassificationSubject`;
- `AcceptedBaselineClassificationFactReference`;
- `AcceptedBaselineClassificationCandidate`;
- `AcceptedBaselineClassificationPredicate`;
- `AcceptedBaselineClassificationRule`;
- `AcceptedBaselineClassificationPolicy`;
- `AcceptedBaselineClassificationObservation`;
- `AcceptedBaselineClassificationObservationSet`;
- `stable_accepted_baseline_classification_policy_id`; and
- `stable_accepted_baseline_classification_observation_set_id`.

Models shall be frozen, slotted, immutable, service-independent, strictly validated,
and canonically ordered. No public finding, severity, persistence, publication,
reference, approval, destination, migration, or operational-result model is allowed.

### 15.1 Predicate contract

`AcceptedBaselineClassificationPredicate` contains:

- semantic field path;
- operator from `EXACT`, `MEMBER_OF`, `PRESENT`, or `ABSENT`; and
- a canonically ordered tuple of exact values when the operator requires values.

`EXACT` requires one value. `MEMBER_OF` requires at least one unique lexically
ordered value. `PRESENT` and `ABSENT` require no values. All predicates in one rule
are combined by fixed boolean conjunction.

### 15.2 Subject contract

The subject identity contains exact `source_root_id`, POSIX `relative_path`,
`item_id`, and evidence-declared item type. It contains no absolute or inferred
path.

---

## 16. Rule Semantics

Only typed fixed predicates are approved:

- exact field equality;
- exact enumerated membership;
- semantic fact presence or absence;
- fixed boolean conjunction;
- subject kind;
- inventory support state;
- capture status; and
- integrity outcome.

Each rule contains stable rule code, dimension, subject applicability through
predicates, ordered predicates, observation kind, candidate value, result state,
review requirement, rationale code, and review-rationale codes.

Prohibited mechanisms include scripts, generic DSLs, arbitrary callables, dynamic
imports, regex, case folding, Unicode or path normalization, suffix or extension
inference, filename parsing, MIME inference, content inspection, confidence scores,
external taxonomies, locale-dependent behavior, runtime rule injection, AI, and
LLMs.

---

## 17. Normative Initial Rule Table

All field paths are relative to one Slice 6C-1 inventory subject unless prefixed
with `integrity.`. `inventory.support_status` and `inventory.item_type` refer to the
inventory envelope. `inventory.capture_status` refers to the supported record.
`integrity.outcome` refers to the uniquely linked content-integrity item.

| Rule code | Dimension | Predicate conjunction | Candidate/state | Review | Rationale |
|---|---|---|---|---|---|
| `content-type-file` | `CONTENT_TYPE` | support=`supported`; item_type=`file` | `FILE` / `CLASSIFIED` | no | `evidence_declares_file` |
| `content-type-directory` | `CONTENT_TYPE` | support=`supported`; item_type=`directory` | `DIRECTORY` / `CLASSIFIED` | no | `evidence_declares_directory` |
| `content-type-unsupported` | `CONTENT_TYPE` | support=`unsupported` | `UNSUPPORTED_OBJECT` / `CLASSIFIED` | yes | `unsupported_inventory_object` |
| `content-type-other` | `CONTENT_TYPE` | support=`supported`; item_type in symbolic_link,junction,other | `OTHER` / `CLASSIFIED` | yes | `supported_other_object` |
| `inventory-support-supported` | `INVENTORY_SUPPORT_STATE` | support=`supported` | `SUPPORTED` / `CLASSIFIED` | no | `inventory_record_supported` |
| `inventory-support-unsupported` | `INVENTORY_SUPPORT_STATE` | support=`unsupported` | `UNSUPPORTED` / `CLASSIFIED` | yes | `inventory_record_unsupported` |
| `capture-captured` | `CAPTURE_STATE` | support=`supported`; capture=`captured` | `CAPTURED` / `CLASSIFIED` | no | `capture_status_preserved` |
| `capture-excluded` | `CAPTURE_STATE` | support=`supported`; capture=`excluded` | `EXCLUDED` / `CLASSIFIED` | yes | `capture_excluded_review` |
| `capture-inaccessible` | `CAPTURE_STATE` | support=`supported`; capture=`inaccessible` | `INACCESSIBLE` / `CLASSIFIED` | yes | `capture_inaccessible_review` |
| `capture-error` | `CAPTURE_STATE` | support=`supported`; capture=`error` | `ERROR` / `CLASSIFIED` | yes | `capture_error_review` |
| `capture-pending` | `CAPTURE_STATE` | support=`supported`; capture=`pending` | `PENDING` / `CLASSIFIED` | yes | `capture_pending_review` |
| `capture-unsupported` | `CAPTURE_STATE` | support=`unsupported` | none / `UNSUPPORTED` | yes | `capture_state_unsupported` |
| `integrity-directory-na` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`directory` | `NOT_APPLICABLE` / `NOT_APPLICABLE` | no | `integrity_not_applicable_directory` |
| `integrity-unsupported` | `CONTENT_INTEGRITY_STATE` | support=`unsupported` | none / `UNSUPPORTED` | yes | `integrity_state_unsupported` |
| `integrity-missing-link` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; integrity.outcome absent | `INSUFFICIENT_EVIDENCE` / `INSUFFICIENT_EVIDENCE` | yes | `integrity_linkage_missing` |
| `integrity-verified` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`verified` | `VERIFIED` / `CLASSIFIED` | no | `integrity_outcome_preserved` |
| `integrity-source-changed` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`source_changed` | `SOURCE_CHANGED` / `CLASSIFIED` | yes | `integrity_failure_review` |
| `integrity-size-mismatch` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`size_mismatch` | `SIZE_MISMATCH` / `CLASSIFIED` | yes | `integrity_failure_review` |
| `integrity-digest-mismatch` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`digest_mismatch` | `DIGEST_MISMATCH` / `CLASSIFIED` | yes | `integrity_failure_review` |
| `integrity-missing` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`missing` | `MISSING` / `CLASSIFIED` | yes | `integrity_failure_review` |
| `integrity-inaccessible` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`inaccessible` | `INACCESSIBLE` / `CLASSIFIED` | yes | `integrity_failure_review` |
| `integrity-not-regular` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`not_regular_file` | `NOT_REGULAR_FILE` / `CLASSIFIED` | yes | `integrity_failure_review` |
| `integrity-filesystem-error` | `CONTENT_INTEGRITY_STATE` | support=`supported`; item_type=`file`; outcome=`filesystem_error` | `FILESYSTEM_ERROR` / `CLASSIFIED` | yes | `integrity_failure_review` |

The initial default policy contains exactly these 23 rules. No additional or omitted
rule is conforming to behavior version 1.0.

---

## 18. Conflict, Ambiguity, and State Resolution

Rules are evaluated in canonical `(dimension.value, rule_code)` order.

- Multiple matches selecting the same value combine unique rule and fact provenance.
- Different mutually exclusive values produce `CONFLICTING` and retain all
  candidates.
- Different compatible unresolved values produce `AMBIGUOUS` and retain all
  candidates.
- No match produces `UNCLASSIFIED` only when subject, dimension, and required facts
  are otherwise supported.
- Missing required facts produce `INSUFFICIENT_EVIDENCE`.
- Unsupported source values or forms produce `UNSUPPORTED`.
- An explicit authenticated `unknown` value produces `UNKNOWN` when a governed
  source vocabulary supports that value.

No priority, insertion order, first match, implicit default, or normalization may
choose a winner. Candidates are retained in lexical `(value, rule_codes)` order.

---

## 19. Canonical Semantic Manifest Serialization

Every architecture-defined semantic manifest identity is calculated as follows:

1. The payload is the JSON object defined by this architecture.
2. Object keys use lexical Unicode code-point order.
3. Array order is exactly the normative order below.
4. Strings use UTF-8 with non-ASCII characters emitted directly.
5. Separators are comma and colon with no additional whitespace.
6. JSON booleans, null, strings, and integers use canonical JSON representations.
7. Floating-point values are prohibited.
8. There is no byte-order mark, leading/trailing whitespace, or final newline.
9. SHA-256 is calculated over the exact serialized bytes.
10. The identity is 64 lowercase hexadecimal characters.
11. Implementations must reproduce the recorded digest or fail closed.

Language-neutral formulation:

```text
canonical_bytes = UTF8(JSON(payload,
    object_keys=lexical_unicode_order,
    arrays=architecture_defined_order,
    separators=(",", ":"),
    ensure_ascii=false,
    trailing_newline=false))

behavior_id = lowercase_hex(SHA256(canonical_bytes))
```

---

## 20. Normative Policy Behavior Manifest

The manifest version is:

`poe.storage.baseline-classification.policy-behavior/1.0`

The following JSON is the complete normative payload. Rule array order is
`(dimension, rule_code)`. Predicate array order is lexical by `(field_path,
operator, values)`.

<!-- BEGIN NORMATIVE POLICY BEHAVIOR MANIFEST -->
```json
{"conflict_semantics":{"ambiguous":"different compatible candidates are retained without selection","conflicting":"different mutually exclusive candidates are retained without selection","same_value":"combine unique rule and fact provenance"},"dimensions":{"capture_state":["captured","error","excluded","inaccessible","not_applicable","pending"],"content_integrity_state":["digest_mismatch","filesystem_error","inaccessible","insufficient_evidence","missing","not_applicable","not_regular_file","size_mismatch","source_changed","verified"],"content_type":["directory","file","other","unsupported_object"],"inventory_support_state":["supported","unsupported"]},"manifest_schema_version":"poe.storage.baseline-classification.policy-behavior/1.0","normalization":"none","observation_kind":"descriptive_observation","operational_exclusions":["cache_state","execution_host","execution_timestamp","filesystem_transport_path","lock_state","logging_detail","memory_identity","object_identity","persistence_path","publication_path","replay_state","service_instance"],"ordering":{"candidates":"(value,rule_codes)","fact_references":"(evidence_semantic_id,subject_id,field_path)","observations":"(source_root_id,relative_path,item_id,dimension,kind)","rationale_codes":"lexical","review_rationale_codes":"lexical","rule_codes":"lexical","rules":"(dimension,rule_code)","subjects":"(source_root_id,relative_path,item_id)"},"policy_version":"1.0","predicate_semantics":{"absent":"field path does not resolve","conjunction":"all ordered predicates must match","exact":"resolved scalar equals the one declared value without normalization","member_of":"resolved scalar equals one declared value without normalization","present":"field path resolves"},"review_semantics":{"classified_failure_or_nonterminal_state":"review required","classified_verified_or_captured_state":"review not indicated","not_applicable":"review not indicated","uncertainty_conflict_or_unsupported":"review required"},"rules":[{"candidate":"captured","dimension":"capture_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.capture_status","operator":"exact","values":["captured"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"capture_status_preserved","result_state":"classified","review_rationale_codes":[],"review_required":false,"rule_code":"capture-captured"},{"candidate":"error","dimension":"capture_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.capture_status","operator":"exact","values":["error"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"capture_error_review","result_state":"classified","review_rationale_codes":["capture_error_review"],"review_required":true,"rule_code":"capture-error"},{"candidate":"excluded","dimension":"capture_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.capture_status","operator":"exact","values":["excluded"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"capture_excluded_review","result_state":"classified","review_rationale_codes":["capture_excluded_review"],"review_required":true,"rule_code":"capture-excluded"},{"candidate":"inaccessible","dimension":"capture_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.capture_status","operator":"exact","values":["inaccessible"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"capture_inaccessible_review","result_state":"classified","review_rationale_codes":["capture_inaccessible_review"],"review_required":true,"rule_code":"capture-inaccessible"},{"candidate":"pending","dimension":"capture_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.capture_status","operator":"exact","values":["pending"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"capture_pending_review","result_state":"classified","review_rationale_codes":["capture_pending_review"],"review_required":true,"rule_code":"capture-pending"},{"candidate":null,"dimension":"capture_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.support_status","operator":"exact","values":["unsupported"]}],"rationale_code":"capture_state_unsupported","result_state":"unsupported","review_rationale_codes":["capture_state_unsupported"],"review_required":true,"rule_code":"capture-unsupported"},{"candidate":"digest_mismatch","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["digest_mismatch"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-digest-mismatch"},{"candidate":"not_applicable","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.item_type","operator":"exact","values":["directory"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_not_applicable_directory","result_state":"not_applicable","review_rationale_codes":[],"review_required":false,"rule_code":"integrity-directory-na"},{"candidate":"filesystem_error","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["filesystem_error"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-filesystem-error"},{"candidate":"inaccessible","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["inaccessible"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-inaccessible"},{"candidate":"missing","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["missing"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-missing"},{"candidate":"insufficient_evidence","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"absent","values":[]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_linkage_missing","result_state":"insufficient_evidence","review_rationale_codes":["integrity_linkage_missing"],"review_required":true,"rule_code":"integrity-missing-link"},{"candidate":"not_regular_file","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["not_regular_file"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-not-regular"},{"candidate":"size_mismatch","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["size_mismatch"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-size-mismatch"},{"candidate":"source_changed","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["source_changed"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_failure_review","result_state":"classified","review_rationale_codes":["integrity_failure_review"],"review_required":true,"rule_code":"integrity-source-changed"},{"candidate":null,"dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.support_status","operator":"exact","values":["unsupported"]}],"rationale_code":"integrity_state_unsupported","result_state":"unsupported","review_rationale_codes":["integrity_state_unsupported"],"review_required":true,"rule_code":"integrity-unsupported"},{"candidate":"verified","dimension":"content_integrity_state","kind":"descriptive_observation","predicates":[{"field_path":"integrity.outcome","operator":"exact","values":["verified"]},{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"integrity_outcome_preserved","result_state":"classified","review_rationale_codes":[],"review_required":false,"rule_code":"integrity-verified"},{"candidate":"directory","dimension":"content_type","kind":"descriptive_observation","predicates":[{"field_path":"inventory.item_type","operator":"exact","values":["directory"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"evidence_declares_directory","result_state":"classified","review_rationale_codes":[],"review_required":false,"rule_code":"content-type-directory"},{"candidate":"file","dimension":"content_type","kind":"descriptive_observation","predicates":[{"field_path":"inventory.item_type","operator":"exact","values":["file"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"evidence_declares_file","result_state":"classified","review_rationale_codes":[],"review_required":false,"rule_code":"content-type-file"},{"candidate":"other","dimension":"content_type","kind":"descriptive_observation","predicates":[{"field_path":"inventory.item_type","operator":"member_of","values":["junction","other","symbolic_link"]},{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"supported_other_object","result_state":"classified","review_rationale_codes":["supported_other_object"],"review_required":true,"rule_code":"content-type-other"},{"candidate":"unsupported_object","dimension":"content_type","kind":"descriptive_observation","predicates":[{"field_path":"inventory.support_status","operator":"exact","values":["unsupported"]}],"rationale_code":"unsupported_inventory_object","result_state":"classified","review_rationale_codes":["unsupported_inventory_object"],"review_required":true,"rule_code":"content-type-unsupported"},{"candidate":"supported","dimension":"inventory_support_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.support_status","operator":"exact","values":["supported"]}],"rationale_code":"inventory_record_supported","result_state":"classified","review_rationale_codes":[],"review_required":false,"rule_code":"inventory-support-supported"},{"candidate":"unsupported","dimension":"inventory_support_state","kind":"descriptive_observation","predicates":[{"field_path":"inventory.support_status","operator":"exact","values":["unsupported"]}],"rationale_code":"inventory_record_unsupported","result_state":"classified","review_rationale_codes":["inventory_record_unsupported"],"review_required":true,"rule_code":"inventory-support-unsupported"}],"source_field_bindings":{"integrity.outcome":"content_integrity_evidence.evidence[].outcome","inventory.capture_status":"inventory_evidence.records[].record.capture_status","inventory.item_type":"inventory_evidence.records[].item_type","inventory.support_status":"inventory_evidence.records[].support_status"},"source_field_paths":["integrity.outcome","inventory.capture_status","inventory.item_type","inventory.support_status"],"state_resolution":{"explicit_unknown":"unknown","missing_required_fact":"insufficient_evidence","no_matching_supported_rule":"unclassified","not_applicable":"not_applicable","unsupported_source_value":"unsupported"}}
```
<!-- END NORMATIVE POLICY BEHAVIOR MANIFEST -->

**Recorded policy behavior ID:**
`bea4cfe1132683da9c06988bdd361d7ef53361b760e1b94da8f30abe8a71ace5`

The behavior ID is part of the classification-policy semantic identity. A semantic
behavior change requires a new manifest version, new digest, new policy identity,
architecture review, and human approval. Class names, module paths, source paths,
object identity, registration order, `repr()`, and memory addresses never define
behavior identity.

---

## 21. Policy Model and Identity

The immutable policy contains:

- policy identity;
- policy version;
- behavior-manifest version and digest;
- exactly four supported dimensions and their closed value domains;
- exactly 23 ordered rules;
- state-resolution semantics;
- conflict and ambiguity semantics;
- review semantics;
- ordering semantics; and
- operational exclusions.

The policy identity format is:

```text
pbcp-<64 lowercase hexadecimal characters>
```

It is SHA-256 over compact canonical UTF-8 JSON containing the complete semantic
policy payload. The behavior digest alone is not the policy identity; both behavior
and the policy's complete public semantic representation participate.

Policy constructors reject empty rules, wrong behavior identity, unapproved
dimensions or values, duplicate rule codes, duplicate semantic rules, invalid
predicate/value combinations, noncanonical ordering, contradictory declarations,
and mutable rule structures.

---

## 22. Observation-Set Identity

The observation-set identity format is:

```text
pbcos-<64 lowercase hexadecimal characters>
```

Its canonical semantic payload includes:

- classification schema version;
- analysis-context ID;
- accepted-baseline ID;
- analysis-profile ID;
- classification-policy ID and version;
- behavior-manifest ID;
- complete ordered observations;
- subject identities;
- dimensions and kinds;
- classification states;
- candidate and selected values;
- applied rule codes;
- rationale and review-rationale codes;
- review flags; and
- semantic fact references.

It excludes execution time, host, object identity, transport paths used only
operationally, service instance, logging detail, registry order, cache or replay
state, and memory identity.

Individual observations require no independent hash identity. Their uniqueness key
is `(source_root_id, relative_path, item_id, dimension, observation_kind)`.

---

## 23. Deterministic Ordering

Canonical ordering is:

- rules: `(dimension.value, rule_code)`;
- subjects: `(source_root_id, relative_path, item_id)`;
- observations: `(source_root_id, relative_path, item_id, dimension.value,
  observation_kind.value)`;
- fact references: `(evidence_semantic_id, subject_id, field_path)`;
- candidates: `(value, rule_codes)`; and
- rule codes, rationale codes, and review-rationale codes: lexical order.

Duplicate semantic keys fail construction. Filesystem order, input tuple order,
dictionary insertion order, hash iteration, object representation, registry order,
and memory identity cannot affect output.

---

## 24. Complete Lineage

The observation set directly retains the exact input context and exact policy.
Each observation retains compact immutable fact references containing:

- authenticated evidence semantic ID;
- evidence type;
- schema name and version;
- source-root ID;
- item ID;
- relative path;
- exact semantic field path; and
- applied rule codes.

The predecessor context remains the authoritative complete lineage source for the
accepted baseline, authorization, evaluation, validation, candidate, original
baseline, accepted/excluded scope, conditions, pilot constraints, retention,
supersession eligibility, evidence, capture, inventory, integrity, source device,
volume, and item provenance.

Compact references must let Slice 6C-3 generate findings without rerunning
classification. Transport metadata and whole fact graphs are not copied into every
observation. No provenance may be collapsed.

---

## 25. Public Service

The public service is:

```python
AcceptedBaselineClassificationService
```

with the method:

```python
def classify(
    self,
    context: AcceptedBaselineAnalysisContext,
) -> AcceptedBaselineClassificationObservationSet: ...
```

The constructor accepts exactly one immutable
`AcceptedBaselineClassificationPolicy`, with one repository-default policy built in
code. The method accepts exactly one public argument. No publisher, loader,
filesystem, clock, persistence, registry, taxonomy, network, AI, CLI, or
configuration dependency is approved.

---

## 26. Findings Boundary

Slice 6C-2 creates no finding, severity, pass/fail decision, readiness decision,
approval recommendation, or phase status. Its output retains explicit state, all
candidates, selected value, rule codes, rationale codes, review requirement, and fact
references. Slice 6C-3 owns deterministic finding generation and result assembly.

---

## 27. Persistence and Publication Boundary

Slice 6C-2 is computation-only. It writes no observation artifact, sidecar,
reference, database row, report, or NAS state. It uses no lock and claims no replay.
Repeated evaluation is deterministic recomputation.

---

## 28. Human Approval and Authority Boundary

All outputs are non-authoritative:

- observation is not assignment;
- recommendation is not approval;
- review-required does not record review;
- owner metadata does not assign accountable ownership;
- retention lineage does not change retention;
- integrity observation does not authorize exclusion or cleanup;
- classification does not authorize destination creation or migration; and
- no result grants deletion, cleanup, redirection, retention release, or
  supersession authority.

Human classification and target-architecture approval remains Slice 6C-6.

---

## 29. Failure Taxonomy

The narrow public hierarchy is:

```text
AcceptedBaselineClassificationError
├── AcceptedBaselineClassificationContextError
├── AcceptedBaselineClassificationPolicyError
└── AcceptedBaselineClassificationEvaluationError
```

Model-boundary violations raise `ValueError`. Service errors cover tampered context
or profile identity, invalid policy identity, unsupported behavior, duplicate
subjects or observation keys, evaluator defects, and impossible result combinations.

Missing facts, unsupported source values, no match, ambiguity, conflict, and
not-applicable dimensions become explicit observations. Structural failures fail
fast in canonical subject/rule order. Wrapped failures preserve causal chains with
`raise ... from exc`. Errors must not disclose owner strings, hashes, paths, or
other sensitive fact values unnecessarily.

---

## 30. Security, Privacy, and Negative Authority

The service operates only on immutable in-memory context semantics. It has no
filesystem import or API, artifact loader, source-path opening, network, subprocess,
cloud, database, AI, CLI, configuration, or external-service dependency. It performs
no locale-dependent transformation and does not mutate input.

Results may retain subject identity, relative path required for lineage, compact fact
references, and classification-relevant values. Owner strings, permissions,
timestamps, and hashes remain in the predecessor context unless an approved rule
requires them; behavior version 1.0 has no such rule.

Tests must prove no capability to reopen artifacts, inspect content, write files,
persist, publish, create findings, approve, design destinations, create directories
or shares, plan or execute migration, analyze duplicates, designate canonical
copies, redirect clients, authorize cleanup, delete or mutate data, release
retention, execute supersession, or invoke external integrations.

---

## 31. Test Strategy

### 31.1 Model tests

Tests shall cover frozen/slotted immutability, model-to-service dependency absence,
schema versions, exact `pbcp` and `pbcos` formats, identity sensitivity, operational
metadata exclusion, ordering, duplicate and contradictory rules, duplicate subjects
and observations, invalid dimension/value/state combinations, every explicit
uncertainty state, candidate preservation, observation/recommendation distinction,
orthogonal review state, complete lineage, and mutable-structure rejection.

### 31.2 Service success tests

Tests shall cover exact context input, context/profile/evidence identity
revalidation, the default policy, every initial dimension, files, directories,
unsupported subjects, every capture status and integrity outcome, exact rule/fact
provenance, deterministic application, one context/policy to one result identity,
repeated equality, ordering independence, nonmutation, and no filesystem access.

### 31.3 Boundary tests

Tests shall cover wrong input type, tampered context/profile/policy identities,
unsupported behavior ID, missing facts, explicit unknown values, unsupported source
values, no matching rule, same-value multiple matches, ambiguity, conflict,
not-applicable dimensions, unsupported objects, missing integrity linkage, every
integrity failure, duplicate subjects and observations, absence of priority or
insertion-order winners, evaluator failure with cause, and absence of findings.

### 31.4 Negative-authority tests

Source, import, export, and signature inspection, spies, and immutable input snapshots
shall prove absence of filesystem access, writes, persistence, publication, findings,
approval, destination design, migration, duplicate analysis, cleanup, supersession,
AI, network, subprocess, database, CLI, and configuration.

---

## 32. Quality Gates

From the repository root using `.venv`:

```bash
source .venv/bin/activate
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Before commit:

```bash
git diff --cached --check
```

Focused model and service tests must also pass. Untracked files require an explicit
whitespace and scope audit. Passing gates provide evidence but grant no approval,
repository authority, closeout, or certification.

---

## 33. Repository Scope

### 33.1 Architecture-only changed-file scope

```text
ADD docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C2.md
```

### 33.2 Proposed later implementation changed-file scope

Exactly seven files:

```text
MODIFY docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C2.md
ADD    src/poe_backup_orchestrator/models/storage_baseline_classification.py
MODIFY src/poe_backup_orchestrator/models/__init__.py
ADD    src/poe_backup_orchestrator/services/storage_baseline_classification.py
MODIFY src/poe_backup_orchestrator/services/__init__.py
ADD    tests/unit/test_storage_baseline_classification_models.py
ADD    tests/unit/test_storage_baseline_classification.py
```

No other file is presumed necessary. Scope expansion requires implementation to stop
and return for architecture review.

---

## 34. Acceptance Criteria

Implementation review must prove that:

1. exactly one authenticated analysis context is accepted;
2. context, profile, and evidence semantic identities are revalidated;
3. no artifact, evidence, or live source content is accessed;
4. exactly one immutable constructor-supplied policy governs evaluation;
5. the policy behavior manifest and digest match this architecture;
6. exactly four classification dimensions exist;
7. review-required is orthogonal and not a dimension;
8. state and value vocabularies are explicit and closed;
9. no uncertainty is silently defaulted;
10. observations remain distinct from recommendations and approval;
11. every result retains rule and semantic-fact lineage;
12. conflict is never hidden by priority or insertion order;
13. one context/policy pair yields one deterministic result identity;
14. repeated computation returns equal objects;
15. no findings are generated;
16. no persistence or publication occurs;
17. no destination, migration, cleanup, or later authority exists;
18. the exact seven-file scope is preserved;
19. focused and full quality gates pass; and
20. human review separately determines architectural conformance and implementation
    approval.

Criteria satisfaction is evidence and grants no later authority by itself.

---

## 35. Review, Authority Effect, and Closeout

Architecture review must evaluate the exact rule table, manifest, digest, identity,
scope, tests, exclusions, discrepancies, and residual risks. Architecture approval
and implementation authorization remain separate. Implementation approval and
repository-transition authority remain separate. Integration does not imply
closeout, and closeout does not imply certification or successor authority.

**Current authority effect:** none beyond proposing deterministic
non-authoritative observation architecture for accountable human review.

**Authority explicitly withheld:** implementation, commit, push, merge, closeout,
certification, findings, approval, destination design, migration, cleanup,
destructive action, and all later phase authority.

The next lifecycle transition requires explicit accountable-human architecture
approval. Implementation additionally requires separate explicit authorization for
the exact seven-file scope.

---

## 36. Certification Implications

Future Phase 6C certification must prove context-only input, identity revalidation,
deterministic policy identity, exact four-dimension behavior, deterministic
observations, every explicit uncertainty state, orthogonal review requirements,
complete fact and predecessor lineage, repeated equality, no artifact access, no
findings, no persistence, no approval, no destination or migration authority, and no
external AI. This document creates no certification procedure.

---

## 37. Known Discrepancies

1. The discovery request initially supplied `5322d5d986a2d6f2ae97306abb5103d9513f5c7a`;
   authoritative clean `main` had advanced to
   `d4ae9b0effa1deb9ebf7dda6f3461d20effda8cf` through the documentation-only ES-1
   merge. Classification: `ACCEPTED` for this architecture baseline; history remains
   unchanged.
2. The older roadmap assigns obsolete Phase 6B/6C numbering. Later Phase 6C
   architecture and Git history govern prospectively.
3. Phase 6C parent metadata says proposed despite later approval and merge.
4. Slice 6C-1 metadata says implementation in review despite integration.
5. Slice 6C-1 fact-projection prose uses earlier tuple terminology while the
   corrected implementation distinguishes frozen arrays and objects; its approved
   behavior identity remained unchanged.
6. Public context semantic validity does not cryptographically prove construction by
   a particular service invocation.
7. Filesystem owner metadata does not establish accountable ownership.
8. Path or extension does not establish business content type.
9. Integrity outcome is preservation-evidence condition, not business meaning.
10. ES-1 conventions supplement product-slice specification quality but grant no
    product-runtime authority.

These discrepancies are recorded without rewriting predecessor evidence.

---

## 38. Approved Deferrals and Residual Risks

Deferred dimensions, findings, persistence, publication, destination design, human
approval, duplicate analysis, migration, cleanup, retention release, supersession,
live content inspection, and external AI remain separately governed.

Residual risks include metadata-only classification limits, public-context
invocation non-attestation, retained sensitive lineage within the predecessor
context, and future taxonomy evolution. These do not justify expanding this slice.

---

## 39. Final Posture and Architectural Decision

**Document status:** Approved architecture; implementation in review

**ES-1-aligned lifecycle state:** `IMPLEMENTATION_IN_REVIEW`

**Implementation authorization:** Granted by explicit human approval

The complete rule table and behavior manifest have received human architecture
approval, the manifest digest has been independently reproduced, and implementation
is authorized within the exact seven-file scope. The implementation remains subject
to human review and grants no commit, publication, integration, certification, or
later product authority.

Architectural decision: Slice 6C-2 is a deterministic, immutable,
context-only classification-observation boundary with exactly four initial
descriptive dimensions, explicit uncertainty and review semantics, complete lineage,
and no finding, persistence, approval, destination, migration, cleanup, destructive,
or external-integration authority.
