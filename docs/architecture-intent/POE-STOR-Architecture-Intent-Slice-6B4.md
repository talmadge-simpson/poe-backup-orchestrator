# POE Storage Architecture Intent — Slice 6B-4

## Preservation Baseline Human Authorization

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B4  
**Status:** Approved architecture; implementation in review  
**Phase:** 6B — Preservation Baseline Acceptance  
**Slice:** 6B-4 — Preservation Baseline Human Authorization  
**Parent architecture:** `POE-STOR-Architecture-Intent-Phase-6B.md`  
**Predecessor:** Slice 6B-3 — Preservation Baseline Acceptance Policy Evaluation  
**Repository:** `~/poe-backup-orchestrator`  
**Certified predecessor baseline:** `main` at `a633ab9`  
**Implementation authorization:** Limited to this approved slice  

---

## 1. Purpose

Slice 6B-4 introduces the explicit human-governance boundary that converts an
immutable:

```python
PreservationBaselineAcceptanceRecommendation
```

into immutable authorization decision evidence.

The slice answers:

> What explicit decision did an identified accountable authority make about this
> exact preservation-baseline acceptance recommendation?

The slice does not answer:

> Has the decision been persisted or published as an accepted preservation
> baseline?

Persistence, publication, supersession, migration authority, client
redirection, source cleanup, and destructive operations remain outside this
slice.

---

## 2. Architectural Position

The Phase 6B pipeline entering this slice is:

```text
PreservationBaselineCandidate
        ↓
PreservationBaselineValidationResult
        ↓
PreservationBaselineAcceptanceRecommendation
```

Slice 6B-4 extends the pipeline as follows:

```text
PreservationBaselineAcceptanceRecommendation
        ↓
Explicit Accountable Human Decision
        ↓
PreservationBaselineAuthorizationDecision
```

Later slices may introduce:

```text
PreservationBaselineAuthorizationDecision
        ↓
Canonical Persistence
        ↓
Accepted-Baseline Publication
```

Human authorization does not itself persist, publish, migrate, redirect, clean,
delete, or modify source content.

---

## 3. Governing Distinctions

The architecture shall preserve these distinctions:

1. A validation finding is a technical fact.
2. An acceptance condition is a policy interpretation.
3. An acceptance recommendation is an automated evaluative result.
4. An authorization decision is an accountable human governance decision.
5. Exception approval applies to policy conditions, not raw technical findings.
6. Authorization evidence is not persistence evidence.
7. A rejected recommendation does not become an accepted baseline.
8. An accepted recommendation does not grant migration authority.
9. Migration completion does not grant cleanup authority.
10. No later authority may be inferred from this decision.

---

## 4. Scope

### 4.1 Included responsibilities

Slice 6B-4 includes:

- immutable authorization schema contracts;
- explicit authority identity;
- explicit authority role or basis;
- immutable authorization outcomes;
- explicit authorization rationale;
- explicit rejection rationale;
- explicit approved-condition references;
- explicit rejected-condition references;
- exact recommendation lineage;
- exact validation, candidate, and baseline lineage;
- deterministic authorization identity;
- UTC decision timestamp;
- partial-scope declarations;
- pilot-purpose declarations;
- retention-obligation declarations;
- supersession-eligibility declaration;
- a side-effect-free authorization decision assembler;
- public model and service exports;
- invariant tests;
- deterministic identity tests;
- decision-matrix tests;
- negative authority-boundary tests.

### 4.2 Excluded responsibilities

Slice 6B-4 excludes:

- persistence;
- serialization files;
- filesystem access;
- publication;
- accepted-baseline creation;
- accepted-baseline reference publication;
- baseline supersession execution;
- locking;
- concurrent publication;
- digital signatures;
- cryptographic attestations;
- identity-provider integration;
- directory lookup;
- authentication;
- authorization workflow;
- approval requests;
- notification;
- CLI commands;
- migration planning;
- migration authorization;
- migration execution;
- client redirection;
- source cleanup;
- duplicate deletion;
- source-content modification;
- destructive operations.

---

## 5. Existing Contracts to Reuse

Implementation shall consume, without redefining:

```python
PreservationBaselineAcceptanceRecommendation
AcceptanceEvaluationIdentity
AcceptanceDecision
AcceptanceCondition
AcceptanceConditionDisposition
AcceptanceMode
PreservationBaselineValidationResult
PreservationBaselineCandidate
```

The authorization layer shall not:

- reopen evidence artifacts;
- recompute validation;
- reevaluate acceptance policy;
- regenerate recommendation conditions;
- reinterpret validation findings;
- inspect source content;
- consult the filesystem.

The recommendation is the complete evaluative input.

---

## 6. Proposed Domain Module

Preferred module:

```text
src/poe_backup_orchestrator/models/storage_baseline_authorization.py
```

The module shall contain only:

- immutable domain contracts;
- deterministic normalization helpers;
- canonical ordering helpers;
- stable authorization identity derivation.

The model module must not import from services.

---

## 7. Authorization Schema Version

```python
STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION: Final[str] = "1.0"
```

This version governs authorization decision evidence only.

It does not replace candidate, validation, or acceptance-evaluation schema
versions.

---

## 8. Authorization Decision Outcome

```python
class AuthorizationDecisionOutcome(StrEnum):
    AUTHORIZE = "authorize"
    AUTHORIZE_WITH_EXCEPTIONS = "authorize_with_exceptions"
    AUTHORIZE_PARTIAL_SCOPE = "authorize_partial_scope"
    AUTHORIZE_PILOT = "authorize_pilot"
    REJECT = "reject"
```

Semantics:

### 8.1 `AUTHORIZE`

The authority accepts the recommendation without approved exceptions, scope
reductions, or pilot limitation.

### 8.2 `AUTHORIZE_WITH_EXCEPTIONS`

The authority explicitly approves one or more review-required acceptance
conditions.

### 8.3 `AUTHORIZE_PARTIAL_SCOPE`

The authority accepts only an explicit subset of candidate source roots.

### 8.4 `AUTHORIZE_PILOT`

The authority accepts the recommendation for an explicit constrained pilot
purpose.

### 8.5 `REJECT`

The authority rejects the recommendation.

A rejection is immutable decision evidence. It does not alter the candidate,
validation result, or recommendation.

---

## 9. Authority Identity

```python
@dataclass(frozen=True, slots=True)
class AuthorizationAuthority:
    authority_id: str
    display_name: str
    authority_role: str
    authority_basis: str
    organization: str | None = None
```

Required invariants:

- `authority_id` is normalized, non-empty, and contains no whitespace;
- `display_name` is normalized and non-empty;
- `authority_role` is normalized and non-empty;
- `authority_basis` is normalized and non-empty;
- `organization` is normalized when present;
- no password, token, credential, certificate, or secret is stored;
- no authentication claim is inferred;
- no directory identity is resolved by this model;
- no mutable mappings are stored.

The authority object records accountability evidence only.

It is not an authentication result.

---

## 10. Condition Decision Reference

The authorization layer shall reference acceptance conditions rather than raw
validation findings.

```python
class AuthorizationConditionDisposition(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"
```

```python
@dataclass(frozen=True, slots=True)
class AuthorizationConditionDecision:
    condition_sequence: int
    condition_code: str
    disposition: AuthorizationConditionDisposition
    rationale: str
```

Required invariants:

- sequence is positive;
- sequence references an existing recommendation condition;
- condition code exactly matches the referenced recommendation condition;
- rationale is normalized and non-empty;
- duplicate condition sequences are prohibited;
- decision references use canonical ascending condition-sequence ordering;
- only `REVIEW_REQUIRED` conditions may be approved;
- blocking conditions may not be approved;
- satisfied conditions do not require approval;
- rejected condition decisions are allowed for explicit rejection evidence.

This boundary preserves the pipeline:

```text
ValidationFinding
        ↓
AcceptanceCondition
        ↓
AuthorizationConditionDecision
```

---

## 11. Authorization Scope

```python
@dataclass(frozen=True, slots=True)
class AuthorizationScope:
    accepted_source_root_ids: tuple[str, ...]
    excluded_source_root_ids: tuple[str, ...]
    scope_limitations: tuple[str, ...]
```

Required invariants:

- accepted and excluded root identifiers are normalized;
- each collection is unique and canonically ordered;
- accepted and excluded roots do not overlap;
- every referenced source root belongs to candidate scope;
- strict and exception authorization cover the complete candidate scope;
- partial authorization accepts a non-empty proper subset;
- rejection accepts no source roots;
- scope limitations are normalized, unique, and canonically ordered.

---

## 12. Pilot Authorization

```python
@dataclass(frozen=True, slots=True)
class PilotAuthorization:
    purpose: str
    limitations: tuple[str, ...]
```

Required invariants:

- purpose is normalized and non-empty;
- limitations are normalized, unique, and canonically ordered;
- pilot authorization requires at least one explicit limitation;
- pilot metadata is present only for `AUTHORIZE_PILOT`.

---

## 13. Authorization Identity

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationIdentity:
    schema_version: str
    authorization_id: str
    evaluation_id: str
    validation_id: str
    candidate_id: str
    baseline_id: str
```

Recommended identifier:

```text
pbd-<64 lowercase hexadecimal characters>
```

The identity shall preserve exact lineage to:

- acceptance evaluation;
- validation result;
- candidate;
- baseline.

The stable identity shall not include the decision timestamp.

---

## 14. Stable Authorization Identity

The model module shall expose:

```python
stable_preservation_baseline_authorization_id(...)
```

Canonical semantic inputs shall include:

- authorization schema version;
- recommendation evaluation ID;
- validation ID;
- candidate ID;
- baseline ID;
- authorization outcome;
- authority identity fields;
- ordered condition decisions;
- authorization scope;
- pilot authorization;
- ordered retention obligations;
- supersession eligibility;
- decision rationale.

The identity shall exclude:

- decision timestamp;
- host identity;
- process identity;
- random UUIDs;
- persistence paths;
- file digests created by later persistence;
- authentication state;
- external directory state.

Equivalent semantic decisions must produce identical authorization identities.

---

## 15. Authorization Decision

```python
@dataclass(frozen=True, slots=True)
class PreservationBaselineAuthorizationDecision:
    identity: PreservationBaselineAuthorizationIdentity
    recommendation: PreservationBaselineAcceptanceRecommendation
    outcome: AuthorizationDecisionOutcome
    authority: AuthorizationAuthority
    decided_at_utc: datetime
    condition_decisions: tuple[AuthorizationConditionDecision, ...]
    scope: AuthorizationScope
    pilot: PilotAuthorization | None
    retention_obligations: tuple[str, ...]
    supersession_eligible: bool
    rationale: str
```

Required invariants:

- recommendation lineage matches authorization identity;
- decision timestamp is timezone-aware UTC;
- condition decisions use canonical ordering;
- condition decisions reference only recommendation conditions;
- all recommendation conditions are accounted for by decision invariants;
- blocking conditions can never be approved;
- `AUTHORIZE` requires `RECOMMEND_ACCEPTANCE`;
- `AUTHORIZE_WITH_EXCEPTIONS` requires `RECOMMEND_REVIEW`;
- every review-required condition must be explicitly approved for
  `AUTHORIZE_WITH_EXCEPTIONS`;
- `AUTHORIZE_PARTIAL_SCOPE` requires explicit proper-subset scope;
- `AUTHORIZE_PILOT` requires pilot metadata;
- `REJECT` accepts no source roots;
- rejection may reference rejected review or blocking conditions;
- retention obligations are normalized, unique, and canonically ordered;
- rationale is normalized and non-empty;
- stable authorization identity matches semantic content;
- recommendation remains immutable and unchanged;
- no persistence status is represented;
- no publication status is represented;
- no migration authority is represented;
- no cleanup authority is represented.

---

## 16. Decision Compatibility Matrix

The service shall enforce:

```text
RECOMMEND_ACCEPTANCE
    → AUTHORIZE
    → AUTHORIZE_PARTIAL_SCOPE
    → AUTHORIZE_PILOT
    → REJECT

RECOMMEND_REVIEW
    → AUTHORIZE_WITH_EXCEPTIONS
    → AUTHORIZE_PARTIAL_SCOPE
    → AUTHORIZE_PILOT
    → REJECT

RECOMMEND_REJECTION
    → REJECT only
```

An automated rejection recommendation cannot be converted into authorization by
Slice 6B-4.

A later separately approved exception-governance architecture would be required
to reconsider non-reviewable blocking conditions.

---

## 17. Proposed Service Module

Preferred module:

```text
src/poe_backup_orchestrator/services/storage_baseline_authorization.py
```

Recommended service:

```python
class PreservationBaselineAuthorizationDecisionAssembler:
    def assemble(
        self,
        *,
        recommendation: PreservationBaselineAcceptanceRecommendation,
        outcome: AuthorizationDecisionOutcome,
        authority: AuthorizationAuthority,
        decided_at_utc: datetime,
        condition_decisions: tuple[AuthorizationConditionDecision, ...],
        scope: AuthorizationScope,
        pilot: PilotAuthorization | None,
        retention_obligations: tuple[str, ...],
        supersession_eligible: bool,
        rationale: str,
    ) -> PreservationBaselineAuthorizationDecision: ...
```

The assembler shall be stateless and side-effect free.

---

## 18. Service Responsibility

The assembler shall:

1. verify the recommendation contract;
2. verify authority identity;
3. verify decision compatibility;
4. verify exact condition references;
5. verify review-condition approval completeness;
6. verify scope semantics;
7. verify pilot semantics;
8. canonicalize allowed ordered collections;
9. derive stable authorization identity;
10. construct one immutable authorization decision.

The assembler shall not:

- persist;
- publish;
- write files;
- read files;
- consult repositories;
- acquire locks;
- authenticate the authority;
- resolve directory identities;
- send approval requests;
- notify users;
- modify recommendation data;
- reevaluate acceptance policy;
- approve blocking conditions;
- create an accepted baseline;
- authorize migration;
- authorize cleanup.

---

## 19. Conservative Failure Behavior

Model invariant violations shall raise `ValueError`.

Service-level assembly failures may use:

```python
class PreservationBaselineAuthorizationError(Exception): ...
```

The assembler must fail closed when:

- recommendation lineage is inconsistent;
- outcome is incompatible with recommendation decision;
- authority identity is invalid;
- condition references are missing or contradictory;
- review-required conditions are not explicitly approved;
- blocking conditions are approved;
- scope is invalid;
- pilot metadata is missing or extraneous;
- stable identity cannot be derived;
- an invalid authorization decision would otherwise be produced.

The service must not convert programmer errors into authorization.

---

## 20. Canonical Ordering

Canonical ordering is required for deterministic equality, stable identity, and
later persistence.

Required ordering:

```text
condition decisions
    → ascending condition sequence

accepted source roots
    → lexical ascending

excluded source roots
    → lexical ascending

scope limitations
    → lexical ascending

pilot limitations
    → lexical ascending

retention obligations
    → lexical ascending
```

Duplicate values are prohibited.

Input ordering must not affect semantic identity.

---

## 21. Timestamp Semantics

`decided_at_utc` is audit evidence.

It must be timezone-aware UTC.

The decision timestamp shall not participate in stable identity derivation.

This preserves:

- semantic identity across equivalent replay;
- independent audit timing;
- later persistence idempotency.

---

## 22. Public Export Surface

Recommended model exports:

```python
STORAGE_BASELINE_AUTHORIZATION_SCHEMA_VERSION
AuthorizationAuthority
AuthorizationConditionDecision
AuthorizationConditionDisposition
AuthorizationDecisionOutcome
AuthorizationScope
PilotAuthorization
PreservationBaselineAuthorizationDecision
PreservationBaselineAuthorizationIdentity
stable_preservation_baseline_authorization_id
```

Recommended service exports:

```python
PreservationBaselineAuthorizationDecisionAssembler
PreservationBaselineAuthorizationError
```

Exports shall be added to:

```text
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/__init__.py
```

Dependency direction:

```text
authorization models
    → standard library
    → acceptance models

authorization service
    → authorization models
    → acceptance models
```

Prohibited:

```text
authorization models
    ✗ services
    ✗ filesystem
    ✗ persistence
    ✗ CLI
```

---

## 23. Planned Implementation Files

Implementation is expected to modify only:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6B4.md
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/models/storage_baseline_authorization.py
src/poe_backup_orchestrator/services/__init__.py
src/poe_backup_orchestrator/services/storage_baseline_authorization.py
tests/unit/test_storage_baseline_authorization_models.py
tests/unit/test_storage_baseline_authorization.py
```

Any additional production file requires explicit review.

---

## 24. Test Strategy

### 24.1 Model tests

Required coverage:

- schema version;
- frozen dataclasses;
- slots-enabled contracts;
- normalized authority identity;
- optional organization normalization;
- invalid empty authority fields;
- authorization identifier format;
- UTC timestamp enforcement;
- canonical condition-decision ordering;
- duplicate condition-reference rejection;
- canonical source-root ordering;
- overlapping accepted and excluded roots rejected;
- canonical limitation ordering;
- canonical retention-obligation ordering;
- stable identifier repeatability;
- stable identifier excludes timestamp;
- stable identifier changes with authority identity;
- stable identifier changes with outcome;
- stable identifier changes with approved conditions;
- stable identifier changes with scope;
- stable identifier changes with pilot purpose;
- stable identifier changes with rationale;
- lineage consistency;
- no persistence fields;
- no publication fields;
- no migration authority fields;
- no cleanup authority fields.

### 24.2 Service tests

Required coverage:

- acceptance recommendation authorized;
- acceptance recommendation rejected;
- review recommendation authorized with all exceptions approved;
- review recommendation rejected;
- missing review-condition decision rejected;
- blocking condition approval rejected;
- rejection recommendation can only be rejected;
- partial authorization requires proper subset;
- pilot authorization requires pilot metadata;
- non-pilot authorization rejects pilot metadata;
- rejection accepts no source roots;
- condition code mismatch rejected;
- nonexistent condition sequence rejected;
- duplicate condition decisions rejected;
- authority object preserved;
- recommendation preserved;
- repeated assembly equality except audit timestamp;
- semantic identity stable across timestamp changes;
- shuffled semantically equivalent input produces same identity;
- no filesystem dependency;
- no persistence dependency;
- no random-ID dependency;
- no clock default dependency.

### 24.3 Authority-boundary tests

Tests shall verify that the service and model surfaces contain no fields or
methods representing:

- persistence;
- publication;
- accepted-baseline file path;
- migration authorization;
- cleanup authorization;
- source modification;
- client redirection;
- deletion;
- credential verification;
- token validation;
- signature validation;
- directory lookup.

Tests shall also verify that human authorization does not imply migration or
cleanup authority.

---

## 25. Implementation Sequence

After architecture approval:

1. implement authorization schema constants and enums;
2. implement authority identity;
3. implement condition-decision references;
4. implement scope and pilot contracts;
5. implement stable authorization identity;
6. implement immutable authorization decision;
7. add model invariant tests;
8. implement the stateless decision assembler;
9. add compatibility-matrix tests;
10. add scope and exception tests;
11. add authority-boundary tests;
12. add approved public exports;
13. run formatting, static analysis, and the full test suite;
14. inspect exact worktree scope;
15. review before commit;
16. commit only after explicit approval.

---

## 26. Quality Gates

Implementation shall not be accepted unless all of the following pass:

```bash
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Review shall also verify:

- model-to-service dependency direction;
- stable deterministic authorization identity;
- explicit authority identity;
- exact recommendation lineage;
- exact condition references;
- no blocking-condition approval;
- complete review-condition approval;
- no filesystem access;
- no persistence;
- no publication;
- no migration authority;
- no cleanup authority.

---

## 27. Acceptance Criteria

Slice 6B-4 architecture is ready for implementation review when:

1. input is exactly one immutable acceptance recommendation;
2. output is exactly one immutable authorization decision;
3. authority identity is explicit;
4. authority role and basis are explicit;
5. decision outcome is explicit;
6. exception approval references acceptance conditions;
7. blocking conditions cannot be approved;
8. recommendation decision and authorization outcome are compatible;
9. partial authorization scope is explicit;
10. pilot authorization purpose and limitations are explicit;
11. rejection evidence is immutable;
12. stable identity preserves complete lineage;
13. timestamp is excluded from stable identity;
14. no persistence is introduced;
15. no publication is introduced;
16. no accepted-baseline object is introduced;
17. no migration authority is introduced;
18. no cleanup authority is introduced;
19. planned implementation scope remains narrow;
20. no commit occurs before implementation review and approval.

---

## 28. Resolved Architectural Decisions

1. Authorization consumes the immutable acceptance recommendation.
2. Authorization does not bypass the recommendation layer.
3. Exception decisions reference acceptance conditions, not raw findings.
4. Only review-required conditions may be approved.
5. Blocking conditions are non-approvable in this slice.
6. Rejection recommendations may only be rejected.
7. Authority identity is evidence, not authentication.
8. Decision timestamp is audit evidence and is excluded from stable identity.
9. Authorization remains independent of persistence.
10. Authorization remains independent of accepted-baseline publication.
11. Authorization never grants migration authority.
12. Authorization never grants cleanup authority.
13. The initial slice has no CLI.
14. The initial slice has no digital signature or cryptographic attestation.
15. The authorization decision embeds the immutable recommendation for complete
    lineage.

---

## 29. Deferred Architecture

Later slices must separately define:

- canonical authorization serialization;
- authorization persistence;
- SHA-256 sidecars;
- atomic replacement;
- idempotency;
- conflict handling;
- accepted-baseline construction;
- accepted-baseline publication;
- supersession publication;
- CLI or report surfaces;
- digital signatures, if required;
- identity-provider integration, if required;
- migration authority;
- client-redirection authority;
- source-cleanup authority.

None of those capabilities is implicitly authorized by this document.

---

## 30. Architectural Decision

Slice 6B-4 establishes the explicit accountable human-decision boundary.

The governing rule is:

> Evaluation may recommend. An identified authority may decide. Persistence and
> publication remain separate later responsibilities.
