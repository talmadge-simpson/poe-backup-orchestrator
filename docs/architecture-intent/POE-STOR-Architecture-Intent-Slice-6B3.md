# POE Storage Architecture Intent — Slice 6B-3

## Preservation Baseline Acceptance Policy Evaluation

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B3  
**Status:** Proposed for architectural review  
**Phase:** 6B — Preservation Baseline Acceptance  
**Slice:** 6B-3 — Preservation Baseline Acceptance Policy Evaluation  
**Parent architecture:** `POE-STOR-Architecture-Intent-Phase-6B.md`  
**Predecessor:** Slice 6B-2 — Preservation Baseline Evidence Validation  
**Repository:** `~/poe-backup-orchestrator`  
**Implementation branch baseline:** `feature/phase-6b3-acceptance-evaluation` at `84f3fee`  
**Implementation authorization:** Not granted by this document  

---

## 1. Purpose

Slice 6B-3 defines the deterministic policy boundary that transforms an
immutable:

```python
PreservationBaselineValidationResult
```

into an immutable:

```python
PreservationBaselineAcceptanceRecommendation
```

The slice answers:

> Given this exact validation result and this exact acceptance policy, what
> recommendation follows deterministically?

The slice does not answer:

> Has the preservation baseline been accepted by an accountable authority?

The output is evaluative evidence only. It is not approval, authorization,
publication, an accepted baseline, migration authority, client-redirection
authority, cleanup authority, or destructive authority.

---

## 2. Architectural Position

The Phase 6 preservation-governance pipeline entering this slice is:

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
Preservation Baseline Candidate Composition
    ↓
Preservation Baseline Evidence Validation
    ↓
Preservation Baseline Validation Result Assembly
```

Slice 6B-3 extends the pipeline as follows:

```text
PreservationBaselineValidationResult
        ↓
Deterministic Acceptance Policy Evaluation
        ↓
PreservationBaselineAcceptanceRecommendation
```

Later, separately authorized slices may introduce:

```text
PreservationBaselineAcceptanceRecommendation
        ↓
Human Authorization or Exception Decision
        ↓
Accepted-Baseline Decision Evidence
        ↓
Accepted-Baseline Persistence and Publication
```

No result produced by Slice 6B-3 authorizes migration or destructive activity.

---

## 3. Governing Distinctions

The architecture shall preserve these distinctions:

1. A validation finding is a technical fact.
2. An acceptance condition is a policy interpretation of one or more technical
   facts.
3. An acceptance decision is an automated recommendation.
4. A recommendation is not human authorization.
5. A conditional recommendation is not exception approval.
6. A rejection recommendation is not a persisted governance decision.
7. A successful recommendation is not an accepted baseline.
8. An accepted baseline is not migration authority.
9. Migration completion is not cleanup authority.
10. No authority transition may be inferred from deterministic evaluation.

---

## 4. Scope

### 4.1 Included responsibilities

Slice 6B-3 includes:

- immutable acceptance-policy contracts;
- immutable acceptance-condition contracts;
- immutable recommendation contracts;
- deterministic evaluation identity;
- deterministic condition derivation from validation results;
- explicit policy classification of validation categories and severities;
- explicit blocking and review-required condition semantics;
- strict and review-oriented evaluation modes where approved by policy;
- canonical condition ordering;
- canonical rationale ordering;
- stable recommendation identity;
- a side-effect-free acceptance evaluator;
- public model and service exports;
- unit tests for invariants, policy matrices, determinism, and authority
  boundaries.

### 4.2 Excluded responsibilities

Slice 6B-3 excludes:

- filesystem access;
- evidence loading;
- evidence deserialization;
- evidence validation;
- evidence reconciliation;
- persistence of recommendations;
- approval requests;
- approval workflow;
- approval signatures;
- approver identity;
- exception requests;
- exception authorization;
- authorization timestamps;
- accepted-baseline decision records;
- accepted-baseline persistence;
- accepted-baseline publication;
- baseline supersession;
- migration planning;
- migration authorization;
- migration execution;
- client redirection;
- source cleanup;
- source modification;
- duplicate deletion;
- CLI commands unless separately approved.

---

## 5. Existing Contracts to Reuse

The implementation shall consume, without redefining:

```python
PreservationBaselineValidationResult
PreservationBaselineValidationIdentity
ValidationFinding
ValidationFindingCategory
ValidationFindingSeverity
ValidatedEvidenceReference
EvidenceValidationStatus
PreservationBaselineCandidate
PreservationBaselineCandidateIdentity
```

The evaluator shall use the validation result as its complete technical input.

It shall not:

- reopen evidence artifacts;
- recalculate evidence digests;
- inspect source content;
- consult the filesystem;
- regenerate validation findings;
- repair validation evidence;
- infer facts absent from the validation result.

---

## 6. Proposed Domain Module

The preferred model module is:

```text
src/poe_backup_orchestrator/models/storage_baseline_acceptance.py
```

The module shall contain only immutable domain contracts, deterministic
normalization helpers, canonical ordering helpers, and stable identity
derivation.

The model module must not import from the service layer.

---

## 7. Acceptance Mode

```python
class AcceptanceMode(StrEnum):
    STRICT = "strict"
    REVIEW_PERMITTED = "review_permitted"
```

`STRICT` means every policy-classified acceptance condition must be satisfied
for an acceptance recommendation.

`REVIEW_PERMITTED` means policy-classified review conditions may produce a
recommendation for accountable later review rather than immediate rejection.

An acceptance mode changes automated evaluation semantics only. It does not
grant approval or exception authority.

The slice shall not introduce modes named `APPROVED`, `AUTHORIZED`,
`EXCEPTION_GRANTED`, or equivalent authority-bearing terms.

---

## 8. Acceptance Decision

```python
class AcceptanceDecision(StrEnum):
    RECOMMEND_ACCEPTANCE = "recommend_acceptance"
    RECOMMEND_REVIEW = "recommend_review"
    RECOMMEND_REJECTION = "recommend_rejection"
```

Semantics:

### 8.1 `RECOMMEND_ACCEPTANCE`

All policy-required conditions are satisfied and no policy-classified blocking
or review-required condition remains.

This is still only a recommendation.

### 8.2 `RECOMMEND_REVIEW`

No non-reviewable blocking condition exists, but at least one condition
requires later accountable review under the supplied policy.

This is not exception approval and does not imply that the condition is
overridden.

### 8.3 `RECOMMEND_REJECTION`

At least one policy-classified non-reviewable blocking condition exists, or the
validation result cannot be safely evaluated under the supplied policy.

This is an automated recommendation, not a persisted governance decision.

---

## 9. Acceptance Condition Classification

```python
class AcceptanceConditionDisposition(StrEnum):
    SATISFIED = "satisfied"
    REVIEW_REQUIRED = "review_required"
    BLOCKING = "blocking"
```

A condition disposition is the policy result for one deterministic condition.

The term `OVERRIDDEN` is prohibited in this slice because override authority
belongs to a later governance boundary.

---

## 10. Acceptance Condition

```python
@dataclass(frozen=True, slots=True)
class AcceptanceCondition:
    sequence: int
    condition_code: str
    disposition: AcceptanceConditionDisposition
    finding_categories: tuple[ValidationFindingCategory, ...]
    finding_sequences: tuple[int, ...]
    detail: str
```

Required invariants:

- `sequence` is one-based and contiguous within a recommendation;
- `condition_code` is normalized and non-empty;
- finding categories use canonical ordering;
- finding sequences use canonical ascending ordering;
- duplicate categories and duplicate finding sequences are rejected;
- `detail` is normalized and non-empty;
- a condition references only findings present in the supplied validation
  result;
- conditions contain no approval, approver, exception, persistence, or
  migration fields.

Conditions shall be compact policy conclusions, not copies of the complete
validation finding payload.

---

## 11. Acceptance Policy Rule

```python
@dataclass(frozen=True, slots=True)
class AcceptancePolicyRule:
    finding_category: ValidationFindingCategory
    minimum_severity: ValidationFindingSeverity
    strict_disposition: AcceptanceConditionDisposition
    review_permitted_disposition: AcceptanceConditionDisposition
    condition_code: str
```

A rule explicitly maps technical validation facts into acceptance-policy
semantics.

Required invariants:

- exactly one rule exists for each policy-governed finding category;
- duplicate category rules are rejected;
- rule order is canonical by finding-category value;
- `strict_disposition` must not be less conservative than
  `review_permitted_disposition`;
- a rule may never produce an authority-bearing state;
- policy evaluation may group findings only when the rule explicitly shares a
  condition code.

Severity comparison shall use a fixed domain ordering defined in this module:

```text
informational < warning < error < critical
```

The evaluator must not rely on lexical enum ordering.

---

## 12. Acceptance Policy

```python
@dataclass(frozen=True, slots=True)
class AcceptancePolicy:
    policy_id: str
    policy_version: str
    mode: AcceptanceMode
    rules: tuple[AcceptancePolicyRule, ...]
    unmapped_finding_disposition: AcceptanceConditionDisposition
```

Required invariants:

- policy identity fields are normalized and non-empty;
- policy version is explicit;
- rules use canonical ordering;
- duplicate rules are rejected;
- missing or unmapped findings cannot silently become satisfied;
- the default unmapped disposition must be conservative;
- policy configuration contains no callbacks, clocks, filesystem paths,
  repositories, persistence services, approver identities, or mutable
  collections.

A policy is supplied explicitly to the evaluator. No function-call object shall
be used as a constructor default.

---

## 13. Evaluation Identity

```python
@dataclass(frozen=True, slots=True)
class AcceptanceEvaluationIdentity:
    schema_version: str
    evaluation_id: str
    validation_id: str
    candidate_id: str
    baseline_id: str
    policy_id: str
    policy_version: str
```

The identity records exact lineage to:

- the validation result;
- the preservation baseline candidate;
- the preservation baseline;
- the acceptance policy;
- the acceptance policy version.

The identity shall not include:

- current time;
- random UUIDs;
- process-local counters;
- persistence-generated values;
- approver identity;
- authorization identity.

---

## 14. Stable Evaluation Identity

The module shall expose:

```python
stable_preservation_baseline_acceptance_evaluation_id(...)
```

The stable identifier shall be derived from canonical semantic input including:

- acceptance schema version;
- validation ID;
- candidate ID;
- baseline ID;
- policy ID;
- policy version;
- acceptance mode;
- ordered conditions;
- final recommendation decision;
- ordered rationale codes.

The identifier shall use canonical JSON and SHA-256, following existing
repository conventions.

The identifier prefix should be governed and distinct, for example:

```text
pba-
```

Equivalent validation results and equivalent policies must produce identical
evaluation identities.

Audit timestamps are deliberately excluded from this slice.

---

## 15. Acceptance Recommendation

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineAcceptanceRecommendation:
    identity: AcceptanceEvaluationIdentity
    validation_result: PreservationBaselineValidationResult
    mode: AcceptanceMode
    decision: AcceptanceDecision
    conditions: tuple[AcceptanceCondition, ...]
    rationale_codes: tuple[str, ...]
```

Required invariants:

- identity lineage matches the embedded validation result;
- mode matches the evaluated policy;
- conditions use canonical one-based contiguous ordering;
- rationale codes are normalized, unique, and canonically ordered;
- `RECOMMEND_ACCEPTANCE` has no blocking or review-required conditions;
- `RECOMMEND_REVIEW` has at least one review-required condition and no blocking
  conditions;
- `RECOMMEND_REJECTION` has at least one blocking condition;
- the validation result remains immutable and unchanged;
- the recommendation contains no approval, authorization, exception approval,
  persistence, accepted-baseline, migration, or cleanup fields.

Embedding the immutable validation result preserves complete lineage and avoids
reconstructing technical facts from identifiers alone.

---

## 16. Proposed Service Module

The preferred service module is:

```text
src/poe_backup_orchestrator/services/storage_baseline_acceptance.py
```

The primary service is:

```python
class PreservationBaselineAcceptanceEvaluator:
    def evaluate(
        self,
        *,
        validation_result: PreservationBaselineValidationResult,
        policy: AcceptancePolicy,
    ) -> PreservationBaselineAcceptanceRecommendation: ...
```

The evaluator shall be stateless and side-effect free.

---

## 17. Evaluator Responsibility

The evaluator's sole responsibility is:

1. verify that the supplied policy can deterministically classify the supplied
   validation result;
2. map validation findings to policy rules;
3. derive canonical acceptance conditions;
4. determine the recommendation decision;
5. derive ordered rationale codes;
6. derive stable evaluation identity;
7. return one immutable recommendation.

The evaluator shall not:

- read or write files;
- access repositories;
- access persistence;
- consult a clock;
- generate random values;
- mutate the policy;
- mutate the validation result;
- load evidence;
- add technical findings;
- approve exceptions;
- request human approval;
- publish an accepted baseline;
- authorize migration;
- perform cleanup.

---

## 18. Deterministic Decision Algorithm

The evaluator shall use this decision precedence:

```text
Any BLOCKING condition
    → RECOMMEND_REJECTION

Else any REVIEW_REQUIRED condition
    → RECOMMEND_REVIEW

Else
    → RECOMMEND_ACCEPTANCE
```

The precedence is fixed and not configurable.

Policy controls condition disposition. It does not control the semantic meaning
of the three recommendation decisions.

---

## 19. Finding Evaluation

For each validation finding:

1. resolve the policy rule by finding category;
2. compare finding severity against the rule's minimum severity;
3. when below threshold, classify the finding as satisfied or omit it according
   to one explicitly documented implementation convention;
4. when at or above threshold, select the disposition for the policy mode;
5. group findings by condition code only where the rule explicitly directs;
6. emit conditions in canonical order;
7. retain exact finding sequence references.

The implementation shall choose one consistent representation for below-
threshold findings:

- emit explicit `SATISFIED` conditions; or
- omit routine satisfied conditions and reserve conditions for policy-relevant
  findings.

The preferred approach is to emit explicit satisfied conditions for all
policy-governed categories represented by findings, because this improves
auditability without reopening technical evidence.

---

## 20. Unmapped and Unsupported Findings

Every validation finding must be accounted for.

If a finding category is not mapped by an explicit policy rule, the evaluator
shall apply `unmapped_finding_disposition`.

The policy must default conservatively. Unmapped findings must never silently
produce `RECOMMEND_ACCEPTANCE`.

The recommendation shall include an explicit rationale code such as:

```text
unmapped_validation_finding
```

---

## 21. Canonical Ordering

Canonical ordering is required for equality, identity derivation, serialization,
and testing.

Recommended condition ordering key:

```text
disposition precedence
→ condition_code
→ finding category values
→ finding sequence numbers
```

Recommended disposition precedence:

```text
blocking
→ review_required
→ satisfied
```

Rationale codes shall be unique and lexically ordered.

The evaluator must not depend on input iteration order except where the
validation contract already defines canonical finding order.

---

## 22. Conservative Failure Behavior

The evaluator must fail closed.

The evaluator shall never recommend acceptance when:

- validation identity lineage is inconsistent;
- policy identity is invalid;
- policy rules are contradictory;
- duplicate category rules exist;
- a finding is unclassifiable and unmapped disposition is not explicit;
- a condition references a nonexistent finding;
- canonical identity cannot be derived;
- the validation result is structurally invalid.

Model invariant violations should raise `ValueError`.

A service-specific exception may be introduced only for an evaluation failure
that cannot be represented as a valid recommendation:

```python
class PreservationBaselineAcceptanceEvaluationError(Exception): ...
```

The evaluator must not convert programming defects into an acceptance
recommendation.

---

## 23. Default Policy

A canonical strict policy may be introduced only when every existing
`ValidationFindingCategory` has been deliberately classified.

The policy should be a module-level immutable singleton, for example:

```python
DEFAULT_STRICT_ACCEPTANCE_POLICY
```

It must not be instantiated through a function call in a method or constructor
default.

A default review-permitted policy should not be introduced until the
architecture explicitly approves which conditions are eligible for later human
review.

The evaluator should still require an explicit policy argument in Slice 6B-3.

---

## 24. Initial Policy Posture

The initial implementation should be conservative.

Recommended initial posture:

- informational findings below a governed threshold may remain satisfied;
- warnings should normally require review or rejection according to explicit
  category rules;
- errors should be blocking;
- critical findings should be blocking;
- missing, unreadable, malformed, digest-mismatched, schema-incompatible,
  identity-mismatched, contradictory, reconciliation-mismatched, source-change,
  and capture-incomplete findings should be blocking under strict mode;
- review eligibility must be category-specific and never inferred solely from
  severity.

The final policy matrix must be approved during implementation review.

---

## 25. Public Export Surface

Recommended model exports:

```python
STORAGE_BASELINE_ACCEPTANCE_SCHEMA_VERSION
AcceptanceCondition
AcceptanceConditionDisposition
AcceptanceDecision
AcceptanceEvaluationIdentity
AcceptanceMode
AcceptancePolicy
AcceptancePolicyRule
PreservationBaselineAcceptanceRecommendation
stable_preservation_baseline_acceptance_evaluation_id
```

Recommended service exports:

```python
PreservationBaselineAcceptanceEvaluationError
PreservationBaselineAcceptanceEvaluator
```

Exports shall be added to:

```text
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/__init__.py
```

Imports shall remain layered:

```text
models → models only
services → models and services as required
```

The model module must not import from `services`.

---

## 26. Test Strategy

### 26.1 Model tests

Tests shall verify:

- frozen dataclasses;
- slots-enabled contracts;
- normalized identifiers;
- schema-version enforcement;
- canonical policy-rule ordering;
- duplicate policy-rule rejection;
- canonical condition ordering;
- duplicate condition-reference rejection;
- decision-to-condition invariants;
- lineage consistency;
- stable identity repeatability;
- stable identity sensitivity to policy version;
- stable identity sensitivity to decision;
- stable identity sensitivity to condition disposition;
- timestamp and randomness absence.

### 26.2 Evaluator tests

Tests shall verify:

- empty findings under a complete policy;
- informational-only findings;
- warning findings;
- error findings;
- critical findings;
- one blocking condition;
- multiple blocking conditions;
- review-required findings;
- blocking precedence over review;
- strict versus review-permitted evaluation;
- category-specific review behavior;
- severity-threshold behavior;
- multiple findings grouped under one condition code;
- unmapped finding behavior;
- deterministic condition ordering;
- deterministic rationale ordering;
- repeated evaluation equality;
- semantically equivalent input equality;
- input mutation does not occur;
- policy mutation is impossible;
- no filesystem dependency;
- no persistence dependency;
- no clock dependency;
- no random-ID dependency.

### 26.3 Authority-boundary tests

Tests shall verify that the new model and service surfaces contain no fields or
methods representing:

- approval;
- approver;
- signature;
- authorization;
- exception approval;
- accepted baseline;
- persistence;
- publication;
- migration authority;
- cleanup authority.

Tests shall also verify that a recommendation cannot be mistaken for a human
decision through enum naming or result fields.

---

## 27. Planned Files

Implementation is expected to modify only:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6B3.md
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/models/storage_baseline_acceptance.py
src/poe_backup_orchestrator/services/__init__.py
src/poe_backup_orchestrator/services/storage_baseline_acceptance.py
tests/unit/test_storage_baseline_acceptance_models.py
tests/unit/test_storage_baseline_acceptance.py
```

Any additional production file requires explicit review.

---

## 28. Quality Gates

Implementation shall not be accepted unless all of the following pass:

```bash
ruff format --check .
ruff check .
pytest -q
```

The implementation review shall also verify:

- clean model-to-service dependency direction;
- deterministic stable identity;
- canonical ordering;
- no filesystem or persistence access;
- no clock or random dependency;
- no authority-bearing fields;
- no accepted-baseline publication;
- no migration or cleanup authority.

---

## 29. Implementation Sequence

After architecture approval:

1. create a dedicated implementation branch;
2. add immutable acceptance models;
3. add stable evaluation identity derivation;
4. add model invariant tests;
5. add the stateless evaluator;
6. add the explicit policy matrix;
7. add evaluator decision-matrix tests;
8. add authority-boundary tests;
9. export the approved public contracts;
10. run formatting, static analysis, and the full test suite;
11. inspect the exact worktree scope;
12. review before commit;
13. commit only after explicit approval.

---

## 30. Deferred Architecture

Later slices must separately define:

- recommendation persistence, if needed;
- human authorization requests;
- accountable decision identity;
- signatures or attestations;
- exception requests;
- exception authorization;
- rejection recording;
- accepted-baseline decision evidence;
- accepted-baseline persistence;
- accepted-baseline publication;
- baseline lineage and supersession;
- migration planning and authority.

None of those capabilities is implicitly authorized by this document.

---

## 31. Acceptance Criteria

Slice 6B-3 architecture is ready for implementation review when:

1. the input is exactly `PreservationBaselineValidationResult`;
2. the output is exactly an immutable acceptance recommendation;
3. policy is explicit, immutable, and versioned;
4. evaluation is deterministic and side-effect free;
5. every validation finding is accounted for;
6. unmapped findings fail conservatively;
7. recommendation decisions use authority-neutral names;
8. stable identity contains complete validation and policy lineage;
9. no timestamp or randomness participates in identity;
10. no persistence is introduced;
11. no human approval is introduced;
12. no exception authorization is introduced;
13. no accepted baseline is introduced;
14. no migration authority is introduced;
15. no cleanup authority is introduced;
16. the planned implementation surface remains narrow and reviewable.

---

## 32. Architectural Decision

Slice 6B-3 establishes a pure policy-evaluation boundary.

It transforms validated technical evidence into a deterministic recommendation
while deliberately stopping before any governance authority transition.

The governing rule is:

> Evaluation may recommend. Only a later accountable authority may decide.

## Implementation Closeout

Slice 6B-3 is implemented and validated.

### Delivered capability

The slice introduces an immutable, deterministic acceptance-evaluation domain for
preservation-baseline validation results.

The implementation provides:

- explicit acceptance-policy rules;
- strict and review-permitted evaluation modes;
- satisfied, review-required, and blocking acceptance conditions;
- deterministic `pba-` evaluation identities;
- complete candidate, baseline, validation, and policy lineage;
- conservative treatment of unmapped validation findings;
- authority-neutral acceptance, review, and rejection recommendations.

### Architectural boundaries preserved

The evaluator:

- consumes only an immutable `PreservationBaselineValidationResult`;
- does not reopen evidence artifacts;
- does not access the filesystem;
- does not recompute digests;
- does not perform persistence or publication;
- does not approve exceptions;
- does not authorize migration;
- does not authorize cleanup.

### Implementation evidence

Feature implementation commit:

- `054e17c` — `Implement Slice 6B-3 acceptance evaluation`

Implemented files:

- `src/poe_backup_orchestrator/models/storage_baseline_acceptance.py`
- `src/poe_backup_orchestrator/services/storage_baseline_acceptance.py`
- `tests/unit/test_storage_baseline_acceptance_models.py`
- `tests/unit/test_storage_baseline_acceptance.py`

Public exports were added through the model and service package initializers.

### Validation evidence

The merged baseline passed:

- Ruff formatting validation;
- Ruff static analysis;
- focused Slice 6B-3 unit tests;
- the complete repository test suite.

The certified full-suite baseline is **778 passing tests**.

### Closeout conclusion

Slice 6B-3 is complete. The repository now supports deterministic,
policy-driven preservation-baseline acceptance recommendations while preserving
the separation between technical evaluation and human governance authority.
