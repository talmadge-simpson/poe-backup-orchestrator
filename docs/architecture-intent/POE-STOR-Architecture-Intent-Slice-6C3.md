# POE Storage Architecture Intent — Slice 6C-3

## Deterministic Classification Finding Generation and Result Assembly

**Lifecycle state:** Proposed for architectural review

**Engineering lifecycle state:** `ARCHITECTURE_IN_REVIEW`

**Predecessor:** Slice 6C-2 Deterministic Classification Policy and Observation

**Governing parent:** Phase 6C Classification and Destination Design

**Implementation authorization:** Not granted by this document

**Authority effect:** None beyond deterministic non-authoritative finding generation

**Architecture-only changed-file scope:**
`docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C3.md`

**Proposed later implementation scope:** Exactly the seven files in Section 24

## 1. Governance and architectural posture

This product-slice specification is governed by `AGENTS.md`, the Engineering Kernel,
the Slice Specification Standard, the approved Phase 6C parent architecture, and the
approved Slice 6C-1 and Slice 6C-2 architectures. Engineering System ES-1 and ES-2
conventions supplement specification quality, evidence traceability, discrepancy
handling, and lifecycle clarity. They create no product-runtime dependency and grant
no product authority.

Architecture governs implementation. Evidence precedes evaluation and authority.
Deterministic behavior is preferred to heuristic interpretation; uncertainty and
contradiction remain explicit; verification fails closed; semantic identity is
independent of implementation presentation; immutable evidence is preferred to
mutable operational state; provenance is never collapsed; and transport verification
is distinct from semantic meaning. Tests provide evidence but do not grant approval.
Certification precedes operational-readiness claims. A result from one stage grants
no authority assigned to a later stage. We do not restructure the only copy of
anything.

## 2. Slice responsibility

Slice 6C-3 consumes exactly one valid immutable
`AcceptedBaselineClassificationObservationSet`, revalidates its complete semantic and
predecessor identity chain, applies exactly one immutable constructor-supplied finding
policy, generates deterministic observation-level findings, and returns exactly one
immutable `AcceptedBaselineClassificationFindingResult`.

It must not rerun Slice 6C-1 intake or Slice 6C-2 classification; reopen accepted-
baseline or evidence artifacts; inspect source content; create readiness or pass/fail
decisions; create recommendations or action codes; persist or publish; perform human
approval; define destinations; analyze duplicates; plan or execute migration;
authorize cleanup; mutate source or NAS state; release retention; execute
supersession; certify the phase; or invoke AI or external integrations.

## 3. Public boundary

The one public method input is exactly:

`AcceptedBaselineClassificationObservationSet`

The service rejects an `AcceptedBaselineAnalysisContext`, accepted-baseline artifact
or model, raw evidence, mappings, caller-assembled observations, mutable structures,
per-call policies, category or severity overrides, suppression lists, blocking
overrides, and runtime rule tables.

Before generation it revalidates the observation-set identity, classification-policy
identity, classification behavior-manifest identity, analysis-context identity,
analysis-profile identity, authenticated evidence identities, accepted-baseline
lineage relationships, observation uniqueness, and structural invariants. Semantic
revalidation proves model conformance; it does not attest which service invocation
created the public object. No token, signature, private constructor, or attestation
mechanism is introduced.

The direct public output is exactly:

`AcceptedBaselineClassificationFindingResult`

It retains the exact predecessor observation set, exact finding policy, and
canonically ordered findings. No operational wrapper is approved. It contains no
timestamp, host, persistence or publication path, replay flag, cache or lock state,
approval state, readiness state, or report path.

## 4. Finding semantics

A finding is a deterministic, policy-defined, non-authoritative statement that one
exact Slice 6C-2 observation requires analytical attention because it expresses
governed uncertainty, conflict, insufficiency, unsupported classification, an
approved review condition, or a concerning capture or integrity condition.

Authenticated fact ≠ classification observation ≠ finding ≠ recommendation ≠
readiness decision ≠ human approval ≠ destination authority ≠ migration authority.
Structural corruption, invalid lineage, and impossible model states are failures,
not findings. Data presence alone does not create a finding.

## 5. Category and severity vocabularies

The closed initial finding-category vocabulary is:

- `POLICY_NONCOVERAGE`
- `CLASSIFICATION_UNCERTAINTY`
- `CLASSIFICATION_CONFLICT`
- `INSUFFICIENT_EVIDENCE`
- `UNSUPPORTED_CLASSIFICATION`
- `CLASSIFICATION_REVIEW`
- `CAPTURE_CONDITION`
- `INTEGRITY_CONDITION`

`STRUCTURAL_INCONSISTENCY` and `LINEAGE_CONTRADICTION` are exceptions, not categories.
`READINESS`, `APPROVAL`, `DESTINATION`, `MIGRATION`, `CLEANUP`, and `CERTIFICATION` are
not finding categories.

The closed severity vocabulary is `WARNING` and `ERROR`. Severity is descriptive,
policy-derived, nonnumeric, non-authoritative, and neither hidden priority, pass/fail,
readiness, approval, nor migration authority. Phase 6B validation severity does not
govern this vocabulary. `INFORMATIONAL`, `CRITICAL`, and `BLOCKING` are prohibited.

No `blocking` field, overall status, pass/fail, readiness, recommendation, approval
recommendation, destination readiness, or migration readiness is approved. Absence
of findings means only that no finding rule emitted a finding.

## 6. Public model surface

The minimal public model surface is:

- `STORAGE_BASELINE_CLASSIFICATION_FINDING_POLICY_SCHEMA_VERSION`
- `STORAGE_BASELINE_CLASSIFICATION_FINDING_SCHEMA_VERSION`
- `AcceptedBaselineClassificationFindingPolicyIdentity`
- `AcceptedBaselineClassificationFindingIdentity`
- `AcceptedBaselineClassificationFindingResultIdentity`
- `AcceptedBaselineClassificationFindingCategory`
- `AcceptedBaselineClassificationFindingSeverity`
- `AcceptedBaselineClassificationFindingRule`
- `AcceptedBaselineClassificationFindingPolicy`
- `AcceptedBaselineClassificationObservationReference`
- `AcceptedBaselineClassificationFinding`
- `AcceptedBaselineClassificationFindingResult`
- `stable_accepted_baseline_classification_finding_policy_id`
- `stable_accepted_baseline_classification_finding_id`
- `stable_accepted_baseline_classification_finding_result_id`

Models are frozen, slotted, immutable, service-independent, canonically ordered, and
strictly validated. Mutable mappings and lists, registries, services, handles,
clocks, locks, caches, persistence, and runtime configuration are prohibited. No
public disposition, blocking, readiness, recommendation, action, approval,
persistence, publication, destination, or migration model is approved.

## 7. Finding policy and rule contract

One repository-default immutable policy is constructed in code. Each rule contains a
stable `rule_code`, accepted observation states, accepted dimensions or explicit
any-dimension applicability, accepted selected values or explicit any-value
applicability, an optional required review value, category, severity, stable
`finding_code`, and stable `rationale_code`.

Predicates are typed exact conjunctions. Empty accepted-dimension or selected-value
tuples mean explicit any-dimension or any-value applicability, respectively; they do
not mean missing policy data. A null required-review value means either Boolean value
is accepted. Generic DSLs, callables, scripts, dynamic imports, regular expressions,
path inference, content inspection, probability, scoring, external taxonomies,
runtime configuration, environment overrides, and AI/LLM processing are prohibited.

### Exact initial rule table

The following 12 rules are complete and normative. Selected-value sets are exact.

| Canonical order | Rule code | State | Dimension | Selected value(s) | Review | Category | Severity | Finding code | Rationale code |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | `finding-state-ambiguous` | `AMBIGUOUS` | any | any | any | `CLASSIFICATION_UNCERTAINTY` | `WARNING` | `classification_ambiguous` | `ambiguous_classification_requires_attention` |
| 2 | `finding-capture-attention` | `CLASSIFIED` | `CAPTURE_STATE` | `EXCLUDED`, `PENDING` | true | `CAPTURE_CONDITION` | `WARNING` | `capture_requires_attention` | `capture_state_requires_attention` |
| 3 | `finding-capture-failure` | `CLASSIFIED` | `CAPTURE_STATE` | `ERROR`, `INACCESSIBLE` | true | `CAPTURE_CONDITION` | `ERROR` | `capture_failure_observed` | `capture_failure_requires_attention` |
| 4 | `finding-integrity-failure` | `CLASSIFIED` | `CONTENT_INTEGRITY_STATE` | `DIGEST_MISMATCH`, `FILESYSTEM_ERROR`, `INACCESSIBLE`, `MISSING`, `NOT_REGULAR_FILE`, `SIZE_MISMATCH`, `SOURCE_CHANGED` | true | `INTEGRITY_CONDITION` | `ERROR` | `integrity_failure_observed` | `integrity_failure_requires_attention` |
| 5 | `finding-content-other` | `CLASSIFIED` | `CONTENT_TYPE` | `OTHER` | true | `CLASSIFICATION_REVIEW` | `WARNING` | `other_content_type_review` | `other_content_type_requires_review` |
| 6 | `finding-content-unsupported` | `CLASSIFIED` | `CONTENT_TYPE` | `UNSUPPORTED_OBJECT` | true | `UNSUPPORTED_CLASSIFICATION` | `WARNING` | `unsupported_content_object` | `unsupported_content_object_requires_attention` |
| 7 | `finding-inventory-unsupported` | `CLASSIFIED` | `INVENTORY_SUPPORT_STATE` | `UNSUPPORTED` | true | `UNSUPPORTED_CLASSIFICATION` | `WARNING` | `unsupported_inventory_record` | `unsupported_inventory_record_requires_attention` |
| 8 | `finding-state-conflicting` | `CONFLICTING` | any | any | any | `CLASSIFICATION_CONFLICT` | `ERROR` | `classification_conflicting` | `conflicting_classification_requires_attention` |
| 9 | `finding-state-insufficient` | `INSUFFICIENT_EVIDENCE` | any | any | any | `INSUFFICIENT_EVIDENCE` | `ERROR` | `classification_insufficient_evidence` | `insufficient_classification_evidence` |
| 10 | `finding-state-unclassified` | `UNCLASSIFIED` | any | any | any | `POLICY_NONCOVERAGE` | `WARNING` | `classification_unclassified` | `classification_policy_did_not_cover_observation` |
| 11 | `finding-state-unknown` | `UNKNOWN` | any | any | any | `CLASSIFICATION_UNCERTAINTY` | `WARNING` | `classification_unknown` | `unknown_classification_requires_attention` |
| 12 | `finding-state-unsupported` | `UNSUPPORTED` | any | any | any | `UNSUPPORTED_CLASSIFICATION` | `WARNING` | `classification_unsupported` | `unsupported_classification_requires_attention` |

No rule may be added or omitted.

### Benign no-finding mappings

No finding is emitted for `CLASSIFIED` without an approved concerning selected-value
rule, `NOT_APPLICABLE`, `CAPTURE_STATE=CAPTURED`,
`CONTENT_INTEGRITY_STATE=VERIFIED`, or directory integrity `NOT_APPLICABLE`. These
mappings grant no authority.

### Review behavior and overlap invariant

`review_required=True` never independently creates a second finding. It remains in
the source-observation reference. Every review-required observation producible by the
approved Slice 6C-2 behavior is covered by one of the 12 rules. A future uncovered
review-required observation fails as unsupported finding-policy behavior.

At most one rule may match an observation. The table is pairwise non-overlapping;
policy construction rejects statically detectable overlap, and runtime multiple
matches raise `AcceptedBaselineClassificationFindingEvaluationError`. Priority,
first-match, insertion order, and dominant severity cannot resolve overlap.

The non-overlap proof is exhaustive: six state-wide rules accept six distinct
non-`CLASSIFIED` states; none can intersect a `CLASSIFIED` rule. The six
`CLASSIFIED` rules either address different dimensions or, within `CAPTURE_STATE` and
`CONTENT_TYPE`, use disjoint selected-value sets. Required-review constraints narrow
rather than expand those sets. Therefore no supported observation shape belongs to
two rule domains.

## 8. Finding granularity and aggregation

Granularity is observation-level only: one finding maps to exactly one concerning
classification observation. Subject-, root-, category-, and result-level summaries
are prohibited initially. Findings for different observations or dimensions remain
separate even when their subject is the same. Provenance never merges across
observations.

Within a finding, finding-rule codes and rationale codes are unique and lexically
ordered. Candidate and fact-reference ordering preserves Slice 6C-2 canonical order.
Duplicate finding keys fail construction; no suppression or dominant finding exists.

## 9. Canonical behavior manifest

### Canonical semantic-manifest serialization

The following rules are normative and language-neutral. The semantic payload is the
architecture-defined JSON object below. Object keys are ordered lexically by Unicode
code point; array order is exactly the architecture-defined order. Strings use UTF-8
with non-ASCII emitted directly. Separators are comma and colon with no added
whitespace. JSON nulls, Booleans, strings, and integers use canonical JSON forms;
floating-point values are prohibited. There is no BOM, surrounding whitespace, or
final newline. SHA-256 is calculated over those exact bytes and rendered as 64
lowercase hexadecimal characters. An implementation must independently reproduce the
recorded digest before use; mismatch is architectural nonconformance and fails closed.

Language-neutral notation:

```text
canonical_bytes = UTF8(JSON(payload,
    object_keys=lexical_unicode_order,
    arrays=architecture_defined_order,
    separators=(",", ":"),
    ensure_ascii=false,
    floating_point=prohibited,
    bom=false,
    trailing_newline=false))
behavior_id = lowercase_hex(SHA256(canonical_bytes))
```

Manifest version:
`poe.storage.baseline-classification.finding-policy-behavior/1.0`.

The next code block contains the complete canonical JSON bytes, except that the code
fence delimiters and their line endings are presentation only and are not hashed.

```json
{"category_vocabulary":["capture_condition","classification_conflict","classification_review","classification_uncertainty","insufficient_evidence","integrity_condition","policy_noncoverage","unsupported_classification"],"deduplication":"duplicate finding keys fail; findings from distinct observations never merge","finding_granularity":"one finding per concerning classification observation","manifest_schema_version":"poe.storage.baseline-classification.finding-policy-behavior/1.0","no_finding_mappings":[{"code":"benign_capture_captured","condition":"capture_state classified captured"},{"code":"benign_classified_unmapped","condition":"classified observation without an approved concerning selected-value rule"},{"code":"benign_directory_integrity_not_applicable","condition":"content_integrity_state not_applicable for directory"},{"code":"benign_integrity_verified","condition":"content_integrity_state classified verified"},{"code":"benign_not_applicable","condition":"not_applicable observation"}],"one_rule_per_observation":"at most one rule may match; static overlap is invalid; runtime overlap fails","operational_exclusions":["approval","blocking","cache_state","destination","execution_host","execution_timestamp","filesystem_transport_path","lock_state","logging_detail","memory_identity","migration","object_identity","persistence_path","publication_path","readiness","recommendation","replay_state","service_instance"],"ordering":{"finding_rule_codes":"lexical","findings":"(source_root_id,relative_path,item_id,dimension,observation_kind,category,finding_code)","policy_rules":"(accepted_state,dimension-or-empty,rule_code)","rationale_codes":"lexical"},"overlap_failure":"accepted-baseline classification finding evaluation error","policy_version":"1.0","required_classification_behavior_id":"bea4cfe1132683da9c06988bdd361d7ef53361b760e1b94da8f30abe8a71ace5","review_required_behavior":"review_required does not create a second finding; unmatched review-required observations fail as unsupported behavior","rules":[{"accepted_dimensions":[],"accepted_selected_values":[],"accepted_states":["ambiguous"],"category":"classification_uncertainty","finding_code":"classification_ambiguous","rationale_code":"ambiguous_classification_requires_attention","required_review":null,"rule_code":"finding-state-ambiguous","severity":"warning"},{"accepted_dimensions":["capture_state"],"accepted_selected_values":["excluded","pending"],"accepted_states":["classified"],"category":"capture_condition","finding_code":"capture_requires_attention","rationale_code":"capture_state_requires_attention","required_review":true,"rule_code":"finding-capture-attention","severity":"warning"},{"accepted_dimensions":["capture_state"],"accepted_selected_values":["error","inaccessible"],"accepted_states":["classified"],"category":"capture_condition","finding_code":"capture_failure_observed","rationale_code":"capture_failure_requires_attention","required_review":true,"rule_code":"finding-capture-failure","severity":"error"},{"accepted_dimensions":["content_integrity_state"],"accepted_selected_values":["digest_mismatch","filesystem_error","inaccessible","missing","not_regular_file","size_mismatch","source_changed"],"accepted_states":["classified"],"category":"integrity_condition","finding_code":"integrity_failure_observed","rationale_code":"integrity_failure_requires_attention","required_review":true,"rule_code":"finding-integrity-failure","severity":"error"},{"accepted_dimensions":["content_type"],"accepted_selected_values":["other"],"accepted_states":["classified"],"category":"classification_review","finding_code":"other_content_type_review","rationale_code":"other_content_type_requires_review","required_review":true,"rule_code":"finding-content-other","severity":"warning"},{"accepted_dimensions":["content_type"],"accepted_selected_values":["unsupported_object"],"accepted_states":["classified"],"category":"unsupported_classification","finding_code":"unsupported_content_object","rationale_code":"unsupported_content_object_requires_attention","required_review":true,"rule_code":"finding-content-unsupported","severity":"warning"},{"accepted_dimensions":["inventory_support_state"],"accepted_selected_values":["unsupported"],"accepted_states":["classified"],"category":"unsupported_classification","finding_code":"unsupported_inventory_record","rationale_code":"unsupported_inventory_record_requires_attention","required_review":true,"rule_code":"finding-inventory-unsupported","severity":"warning"},{"accepted_dimensions":[],"accepted_selected_values":[],"accepted_states":["conflicting"],"category":"classification_conflict","finding_code":"classification_conflicting","rationale_code":"conflicting_classification_requires_attention","required_review":null,"rule_code":"finding-state-conflicting","severity":"error"},{"accepted_dimensions":[],"accepted_selected_values":[],"accepted_states":["insufficient_evidence"],"category":"insufficient_evidence","finding_code":"classification_insufficient_evidence","rationale_code":"insufficient_classification_evidence","required_review":null,"rule_code":"finding-state-insufficient","severity":"error"},{"accepted_dimensions":[],"accepted_selected_values":[],"accepted_states":["unclassified"],"category":"policy_noncoverage","finding_code":"classification_unclassified","rationale_code":"classification_policy_did_not_cover_observation","required_review":null,"rule_code":"finding-state-unclassified","severity":"warning"},{"accepted_dimensions":[],"accepted_selected_values":[],"accepted_states":["unknown"],"category":"classification_uncertainty","finding_code":"classification_unknown","rationale_code":"unknown_classification_requires_attention","required_review":null,"rule_code":"finding-state-unknown","severity":"warning"},{"accepted_dimensions":[],"accepted_selected_values":[],"accepted_states":["unsupported"],"category":"unsupported_classification","finding_code":"classification_unsupported","rationale_code":"unsupported_classification_requires_attention","required_review":null,"rule_code":"finding-state-unsupported","severity":"warning"}],"severity_vocabulary":["error","warning"],"structural_condition_semantics":"identity, lineage, model, reference, overlap, and evaluator defects are failures, not findings","supported_input_classification_schema":"1.0"}
```

The independently calculated behavior digest is:

`5fb9bef7fdbcf63b2bab8347e088a01fad9b35c2bb5f89ccee321f938f2fa9fa`

The manifest includes the required Slice 6C-2 behavior ID
`bea4cfe1132683da9c06988bdd361d7ef53361b760e1b94da8f30abe8a71ace5`.
Neither identity derives from class names, modules, source paths, instances, memory,
representation, or registration order.

## 10. Semantic identities

Identity formats are:

- finding policy: `pbcfp-<64 lowercase hexadecimal characters>`;
- finding: `pbcf-<64 lowercase hexadecimal characters>`;
- finding result: `pbcfr-<64 lowercase hexadecimal characters>`.

The finding-policy identity includes every policy schema/version field, behavior ID,
vocabulary, rule, benign mapping, ordering rule, overlap rule, no-finding rule,
structural-condition semantic, and operational exclusion.

The finding identity includes finding schema version, observation-set ID, finding-
policy ID and behavior digest, exact source-observation key, state, candidates,
selected value, review semantics, category, severity, finding code, rationale codes,
contributing finding-rule codes, and semantic fact references.

The finding-result identity includes result schema version, observation-set ID,
analysis-context ID, accepted-baseline ID, analysis-profile ID, classification-policy
ID, classification behavior ID, finding-policy ID and version, finding behavior ID,
and all ordered findings.

Execution time, host, memory or object identity, service instance, logging, transport
paths, persistence/publication paths, cache, replay, and lock state are excluded.

One exact `classification_observation_set_id` plus one exact `finding_policy_id`
produces exactly one `classification_finding_result_id`. Repeated generation returns
equal objects with identical identities.

## 11. Ordering

Canonical order is:

- finding-policy rules: `(accepted_state.value, dimension-or-empty, rule_code)`;
- findings: `(source_root_id, relative_path, item_id, dimension.value,
  observation_kind.value, category.value, finding_code)`;
- finding-rule and rationale codes: lexical order;
- candidates and fact references: preserve Slice 6C-2 canonical order.

Severity is not an ordering priority. Duplicate semantic keys fail. Input order,
mapping insertion order, hash/set iteration, object representation, registry order,
and memory identity cannot affect output.

## 12. Complete lineage

The result directly retains the exact input observation set, exact finding policy,
and ordered findings. Every finding holds an immutable compact
`AcceptedBaselineClassificationObservationReference` containing observation-set ID,
source-root ID, relative path, item ID, dimension, observation kind, classification
state, selected value, candidates, applied classification-rule codes, rationale
codes, `review_required`, review-rationale codes, semantic fact references, and
contributing finding-rule codes.

The predecessor observation set remains the authoritative complete lineage source.
Raw evidence, entire fact graphs, owners, permissions, timestamps, hashes, artifact
paths, and transport metadata are not copied into findings. Provenance is never
collapsed, and every compact reference must resolve to exactly one source observation.

## 13. Structural failures and governed findings

Errors, not findings, represent wrong input type; invalid observation-set,
classification-policy, classification-behavior, analysis-context, analysis-profile,
or evidence identity; invalid accepted-baseline lineage; unsupported predecessor
behavior; duplicate or missing observation keys; impossible state/value combinations;
invalid finding-policy or finding-behavior identity; unresolved references;
overlapping finding rules; duplicate finding keys; and evaluator defects.

Findings represent `UNCLASSIFIED`, `UNKNOWN`, `AMBIGUOUS`, `CONFLICTING`,
`INSUFFICIENT_EVIDENCE`, `UNSUPPORTED`, approved classified review conditions,
capture conditions, and integrity conditions. Structural corruption is never
normalized into a finding, and governed conditions are not avoided with exceptions.

## 14. Findings, recommendations, and authority

Slice 6C-3 produces no recommendation or action code, including `REVIEW`,
`INVESTIGATE`, `RECAPTURE`, or `REVERIFY`. Destination, ownership, retention,
migration, cleanup, and deletion recommendations are prohibited. Future action
recommendations require separate architecture and approval.

A finding is not approval; severity is neither blocking nor readiness; review-required
does not record review; absence of findings grants no authority. Successful generation
does not authorize persistence, destination design, migration, cleanup, or phase
certification. Human approval remains Slice 6C-6.

## 15. Public service

The public service is `AcceptedBaselineClassificationFindingService`:

```python
def generate_findings(
    self,
    observation_set: AcceptedBaselineClassificationObservationSet,
) -> AcceptedBaselineClassificationFindingResult: ...
```

Its sole constructor dependency is exactly one immutable
`AcceptedBaselineClassificationFindingPolicy`. One repository-default policy is
constructed in code without a function call as a default argument value. The service
has no Slice 6C-1 or Slice 6C-2 service, loader, filesystem, publisher, persistence,
clock, database, network, AI, CLI, or configuration dependency and never reruns its
predecessors.

## 16. Failure hierarchy

```text
AcceptedBaselineClassificationFindingError
├── AcceptedBaselineClassificationFindingInputError
├── AcceptedBaselineClassificationFindingPolicyError
└── AcceptedBaselineClassificationFindingEvaluationError
```

Model-boundary violations raise `ValueError`. `InputError` covers invalid or tampered
predecessor identity or lineage. `PolicyError` covers invalid policy identity,
behavior-manifest mismatch, unsupported predecessor behavior, or overlapping rules.
`EvaluationError` covers duplicate observations or findings, unresolved references,
impossible combinations, runtime multiple matches, and evaluator defects. Structural
failures are fail-fast in canonical observation and rule order. Causal chains use
`raise ... from exc`; errors do not disclose sensitive fact values.

## 17. Persistence and publication boundary

Slice 6C-3 is computation-only. It does not persist, serialize publication artifacts,
write sidecars, create references, use locks, claim replay, write reports or database
rows, or write to NAS. Repeated generation is deterministic recomputation. Slice 6C-4
owns persistence and publication.

## 18. Security, privacy, and negative authority

The service accepts the exact immutable public input, revalidates semantic identity,
and processes observations in memory. It has no artifact/evidence loader, filesystem
read, classification-service call, source-content inspection, network, subprocess,
cloud, database, AI, CLI, runtime configuration, or input mutation. It does not log
owners, hashes, paths, or sensitive facts. Findings retain only the minimum subject
and semantic lineage required by the approved model.

Tests must prove no capability to reopen artifacts/evidence; rerun classification;
inspect live content; write files; persist/publish; assign authoritative
classifications; record approval; decide readiness; define destinations; create
directories/shares; analyze duplicates; designate canonical copies; plan/execute
migration; redirect clients; authorize cleanup; delete/mutate data; release retention;
execute supersession; certify the phase; or invoke AI, network, cloud, database,
subprocess, CLI, or configuration.

## 19. Testing requirements

### Model tests

Require frozen/slotted immutability; no model-to-service imports; exact schema
constants and `pbcfp`, `pbcf`, `pbcfr` formats; closed category/severity vocabularies;
policy, finding, and result identity sensitivity; operational metadata exclusion;
canonical ordering; duplicate and overlapping rule rejection; duplicate finding
rejection; category/severity/code invariants; compact lineage resolution; and mutable-
structure rejection.

### Manifest tests

Require exact manifest version/digest, exactly 12 unique rules, canonical rule order,
exact state/review/capture/integrity/benign mappings, exact vocabularies, pairwise
non-overlap, runtime overlap failure, runtime manifest verification, no added/omitted
rule, and policy-identity sensitivity to every semantic behavior change.

### Service success tests

Require exact input, deep predecessor and finding-policy validation, every approved
state/classified-review/capture/integrity mapping, no findings for benign classified
or `NOT_APPLICABLE` observations, observation granularity, exact source-observation,
classification-rule, and fact lineage, canonical ordering, repeated equality,
nonmutation, no filesystem access, and no Slice 6C-2 service call.

### Boundary tests

Require wrong type; tampered observation-set, classification-policy, classification-
behavior, context, profile, or evidence identity; unsupported predecessor behavior;
invalid finding-policy/behavior identity; duplicate observation; impossible state;
unresolved reference; overlapping rules; runtime multiple matches; duplicate finding;
unmatched review-required observation; evaluator failure with preserved cause; no
suppression or priority/insertion-order winner; and no finding for approved benign
observations.

### Negative-authority tests

Use import/source/export inspection, spies, method-signature inspection, and immutable
snapshots to prove every exclusion in Section 18 and that private manifest/evaluator
helpers are not exported.

## 20. Acceptance criteria

Acceptance requires proof that:

1. exactly one valid classification observation set is accepted;
2. the complete predecessor identity chain is revalidated;
3. classification is never rerun;
4. exactly one immutable constructor-supplied finding policy governs generation;
5. manifest and policy identities match this architecture;
6. exactly 12 rules exist;
7. the table is pairwise non-overlapping;
8. no observation matches more than one rule;
9. every finding maps to exactly one source observation;
10. structural corruption raises an error;
11. governed conditions produce explicit findings;
12. benign observations produce no findings;
13. findings do not duplicate or collapse provenance;
14. findings and result are canonically ordered;
15. repeated generation returns equal objects;
16. no blocking, readiness, recommendation, or approval exists;
17. no persistence or publication exists;
18. no destination, migration, cleanup, certification, or later authority exists;
19. focused and full quality gates pass; and
20. the exact approved seven-file scope is preserved.

## 21. Certification implications

Future Phase 6C certification must prove observation-set-only input; deep identity
revalidation; exact finding-policy manifest/digest and 12-rule behavior; deterministic
findings; pairwise non-overlap; one finding per concerning observation; governed-state
mappings; complete lineage; structural/governed separation; repeated equality; no
artifact access or classification rerun; no persistence/publication; no approval or
readiness; no destination/migration authority; and no external AI. This document does
not create a certification procedure.

## 22. Known discrepancies

These discrepancies are recorded without rewriting history:

- The supplied `a80e9997be30d3a3c5779a8a314f180b30c7f06c` discovery baseline was
  superseded by documentation-only ES-2 merge
  `ca413af6e0be7a9cc1f4c1fae424d0551a076943`.
- Phase 6C parent metadata says proposed despite later approval and merge.
- Slice 6C-1 and Slice 6C-2 metadata say implementation in review despite integration.
- The older roadmap uses obsolete Phase 6B/6C numbering.
- Phase 6B validation findings contain absolute evidence paths; Slice 6C-3 must not
  copy them.
- Phase 6B validation severity has four values and does not govern this vocabulary.
- Phase 6B split finding generation and result assembly; the Phase 6C parent combines
  them in Slice 6C-3.
- A semantically valid public Slice 6C-2 object cannot prove invocation attestation.
- ES-2 supplements evidence and discrepancy governance but grants no product-runtime
  authority.

## 23. Final authorization posture

**Document status:** Proposed for architectural review

**Implementation authorization:** Not granted by this document

The canonical finding-policy behavior manifest is complete, its behavior digest is
independently reproducible, and pairwise rule non-overlap is established. No known
technical architecture blocker remains. Implementation nevertheless remains blocked
until explicit human architecture approval and separate implementation authorization.
No branch, stage, commit, push, merge, or other repository transition is authorized by
this document.

## 24. Exact later implementation scope

Exactly these seven files are approved as the proposed later implementation scope:

1. `docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C3.md`
2. `src/poe_backup_orchestrator/models/storage_baseline_classification_findings.py`
3. `src/poe_backup_orchestrator/models/__init__.py`
4. `src/poe_backup_orchestrator/services/storage_baseline_classification_findings.py`
5. `src/poe_backup_orchestrator/services/__init__.py`
6. `tests/unit/test_storage_baseline_classification_findings_models.py`
7. `tests/unit/test_storage_baseline_classification_findings.py`

No other file is presumed necessary. Any expansion must stop implementation and
return for architecture review.
