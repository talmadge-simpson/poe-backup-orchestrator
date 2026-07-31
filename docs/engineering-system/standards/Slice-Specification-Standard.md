# POE Engineering System — Slice Specification Standard

**Standard identity:** `Engineering-System-Slice-Specification-Standard`
**Standard version:** `1.0`
**Status:** Normative
**System:** POE Engineering System
**Governing kernel:** `Engineering-System-Kernel` version `1.0`
**Governing architecture:** `Engineering-System-Architecture-Intent-Slice-ES-1`

---

## 1. Standard

Every future POE Engineering System slice shall have a slice specification that
conforms to this standard.

A conforming slice is a bounded, deterministic, independently useful,
independently reviewable, and independently mergeable unit of engineering work.
Its specification states the exact responsibility, evidence, repository scope,
and authority boundaries governing that work.

Conformance to this standard does not approve architecture, authorize
implementation, accept an implementation, grant repository authority, close a
slice, or certify a result. Those effects require separate attributable decisions
from an accountable human.

---

## 2. Normative Language

The terms **shall**, **shall not**, **required**, and **prohibited** state
normative requirements. **May** identifies a permitted choice that does not
weaken a requirement. **Should** identifies a preferred practice whose omission
requires an explicit rationale.

An explicit value of `NONE`, `NOT APPLICABLE`, `UNKNOWN`, or `UNVERIFIED` may be
used only where this standard permits it. An empty or omitted declaration is not
equivalent to an explicit value.

This standard governs semantic content. A specification may organize its
presentation differently only when every required field remains uniquely
identifiable and its meaning is unchanged.

---

## 3. Constitutional Conformance

Every slice specification shall preserve the Engineering Kernel, including:

1. architecture precedes implementation;
2. evidence does not grant authority;
3. evaluation does not grant approval;
4. passing validation does not grant implementation, repository, or
   certification authority;
5. authority transitions are explicit, bounded, attributable, and independently
   reviewable;
6. approval or authorization for one slice does not authorize another slice;
7. product authority and Engineering System authority remain distinct;
8. Engineering System behavior does not enter product CLI or runtime;
9. historical evidence is not silently modified to remove discrepancy;
10. unknown, unsupported, incomplete, and contradictory states remain explicit;
11. artifact identities and lineage are not inferred from filenames or prose
    alone;
12. derived knowledge does not replace authoritative source evidence;
13. repository changes remain within explicitly authorized file and
    responsibility boundaries;
14. no Engineering System capability approves or certifies itself; and
15. changes to constitutional invariants require separate constitutional
    architecture, evidence, review, and accountable human approval.

A slice specification shall not weaken or silently reinterpret a constitutional
principle. A proposed constitutional change is outside ordinary slice
conformance and shall be governed separately.

---

## 4. Required Slice Identity

### 4.1 Identity fields

Every slice specification shall declare:

- **system identifier:** the system owning the slice;
- **slice identifier:** a stable identifier unique within that system;
- **slice title:** a concise human-readable name;
- **specification identifier:** the stable identity of the specification;
- **specification version:** a version distinguishing semantic revisions;
- **governed subject:** the exact architecture, implementation, review,
  repository transition, closeout, or certification subject; and
- **current lifecycle state:** exactly one state defined in Section 9.

Engineering System slices shall use the `ES-<number>` slice namespace unless a
separately approved parent architecture defines a subordinate identity form.
Product identifiers shall remain in their product namespaces.

### 4.2 Identity distinctions

The following are distinct and shall not be substituted for one another:

- system identity;
- slice identity;
- specification identity;
- title;
- file path;
- branch identity;
- commit identity;
- content digest;
- lifecycle state; and
- authority-decision identity.

Mutable presentation metadata shall not silently change semantic identity.
Missing or ambiguous identity shall be reported as a discrepancy rather than
inferred.

---

## 5. Purpose and Independently Useful Outcome

Every slice specification shall state:

- the problem or responsibility addressed;
- the outcome the slice is intended to produce;
- why that outcome is independently useful;
- why the outcome can be reviewed independently; and
- why the slice can be merged without requiring unauthorized adjacent work.

Purpose shall describe the governed effect, not merely the act of editing or
creating files. A slice that cannot produce independently useful value shall be
reduced, re-bounded, or explicitly justified by accountable human review.

---

## 6. System and Parent Context

Every slice specification shall identify:

- the owning system;
- the governing parent phase, program, roadmap, or architecture;
- applicable governance and constitutional artifacts;
- its relationship to product and Engineering System ownership; and
- every repository-ownership boundary it crosses.

When no parent exists, the specification shall declare `NONE` and explain the
source of governing authority. A parent relationship does not grant authority
to the child slice.

---

## 7. Predecessor, Dependencies, and Lineage

### 7.1 Predecessor

The specification shall identify the immediately preceding governed slice or
declare `NONE`. It shall state the predecessor evidence on which the slice
relies.

A predecessor is a lineage relationship. Its completion does not authorize the
successor.

### 7.2 Dependencies

The specification shall list every other artifact, decision, repository state,
external condition, or capability required for the slice. Each dependency shall
identify:

- stable identity;
- required state or property;
- evidence source;
- effect on the slice; and
- behavior when the dependency is missing, stale, contradictory, or
  unsupported.

A slice with no dependencies shall declare `NONE`.

### 7.3 Governing lineage

The specification shall identify the governance, constitutional, architecture,
decision, and repository-state lineage applicable to its claims. When an
implementation, review, closeout, or certification claim attaches to repository
content, the exact commit or equivalent immutable repository identity shall be
recorded.

Later documentation does not retroactively become the tested or reviewed
repository identity merely because it records an earlier result.

---

## 8. Architectural Boundary

Every specification shall define the smallest responsibility boundary within
which the slice outcome is complete. It shall state:

- where responsibility begins;
- where responsibility ends;
- the authority class exercised;
- the repository owner or owners affected;
- applicable dependency direction;
- adjacent responsibilities outside the boundary; and
- why the boundary is independently reviewable and mergeable.

The boundary shall not expand merely because adjacent work is convenient,
technically available, or likely to occur later.

---

## 9. Canonical Lifecycle Model

### 9.1 Lifecycle states

A slice specification shall declare exactly one current lifecycle state:

1. `ARCHITECTURE_DRAFT` — architecture is being prepared and carries no
   approval.
2. `ARCHITECTURE_IN_REVIEW` — architecture is under accountable human review;
   no decision is implied.
3. `ARCHITECTURE_APPROVED` — architecture is accepted as governing intent;
   implementation authority remains separate.
4. `IMPLEMENTATION_AUTHORIZED` — explicit accountable human authority exists for
   the exact approved implementation scope.
5. `IMPLEMENTATION_IN_PROGRESS` — authorized implementation evidence is being
   produced.
6. `IMPLEMENTATION_IN_REVIEW` — an implementation candidate is awaiting or
   undergoing accountable human review.
7. `IMPLEMENTATION_APPROVED` — the exact implementation candidate passed
   accountable human review; repository authority remains separate.
8. `REPOSITORY_TRANSITION_AUTHORIZED` — an exact commit, push, merge, or other
   named repository transition is authorized.
9. `INTEGRATED` — the exact approved change is present in its authorized target
   repository state.
10. `CLOSED` — the bounded slice responsibility has an accountable human
    closeout decision.
11. `CERTIFIED` — the exact governed subject has a separate accountable human
    certification decision when certification is required.
12. `SUPERSEDED` — prospective authority or meaning has been explicitly replaced
    while historical evidence remains retained.

`BLOCKED`, `REJECTED`, and `FAILED` are outcome qualifiers. They shall identify
the lifecycle state at which the outcome occurred and shall not replace that
state.

### 9.2 Transition requirements

Lifecycle transitions shall follow this conceptual order:

```text
Repository Inspection
→ Architecture Preparation
→ Architecture Review
→ Architecture Decision
→ Implementation Authorization
→ Bounded Implementation
→ Validation Evidence
→ Implementation Review
→ Repository Decision
→ Integration
→ Closeout or Certification
```

Each transition shall have attributable evidence. A state may be declared `NOT
APPLICABLE` only when governing architecture explicitly permits omission and an
accountable human accepts the rationale.

The following transitions shall remain distinct:

- architecture approval and implementation authorization;
- implementation completion and implementation approval;
- implementation approval and repository-transition authorization;
- commit, push, and merge authority when separately governed;
- integration and closeout; and
- closeout and certification.

A later state shall not be inferred from elapsed time, branch existence, file
content, successful execution, passing gates, or an earlier authority decision.
A failed or rejected attempt shall remain in lineage and shall not be relabeled
as successful.

### 9.3 Status and authority

Lifecycle status records observed state. Authority is an attributable human
decision. A specification shall carry them separately.

When declared status conflicts with repository, decision, or historical
evidence, the conflict shall be recorded under discrepancy handling. Neither
source shall be silently rewritten to agree with the other.

---

## 10. Inputs and Outputs

### 10.1 Inputs

Every governed artifact, decision, declared value, repository state, or external
condition consumed by the slice shall be listed as an input. Each input shall
identify:

- identity;
- source;
- required state or version;
- whether it is mandatory or optional;
- how its integrity or applicability is established; and
- the effect of absence, contradiction, or unsupported form.

Implicit inputs are prohibited. A slice with no inputs shall declare `NONE`.

### 10.2 Outputs

Every artifact or state the slice is permitted to produce shall be listed as an
output. Each output shall identify:

- identity or identity rule;
- artifact class;
- intended repository or evidence boundary;
- relationship to inputs and governing lineage; and
- authority the output explicitly does not grant.

An output declaration does not authorize its creation. Creation requires the
applicable lifecycle authority.

---

## 11. Responsibilities and Non-Responsibilities

### 11.1 Responsibilities

Responsibilities shall state every behavior, artifact, decision preparation, or
state transition the slice is required to perform or produce. They shall be:

- bounded;
- testable or reviewable;
- attributable to the slice purpose;
- consistent with the architectural boundary; and
- traceable to acceptance evidence.

### 11.2 Non-responsibilities

Non-responsibilities shall state related behaviors, artifacts, decisions, and
state transitions that the slice shall not perform. They shall include
activities that are technically adjacent or convenient but governed elsewhere.

Responsibilities and non-responsibilities are independently required. Silence
shall not be treated as an exclusion.

---

## 12. Inclusions, Exclusions, and Deferred Responsibilities

### 12.1 Inclusions

Inclusions shall enumerate every capability, artifact class, repository area,
and lifecycle effect inside the approved boundary.

### 12.2 Exclusions

Exclusions shall enumerate prohibited capabilities, artifacts, repository
areas, authority effects, and lifecycle transitions. Exclusions shall include
negative-authority boundaries applicable to the slice.

An excluded responsibility shall not enter implementation merely because it is
required by a future slice.

### 12.3 Deferred responsibilities

Deferred responsibilities shall identify known adjacent work reserved for
separately governed future consideration. Each deferral shall state why it is
outside the current boundary.

Deferral does not select a future design, promise implementation, establish
sequence, approve architecture, or grant authority. A slice with no known
deferrals shall declare `NONE`.

---

## 13. Assumptions

Every condition treated as true without being established by the slice shall be
declared as an assumption. Each assumption shall identify:

- the assumed condition;
- supporting evidence or `UNVERIFIED`;
- the consequence if false;
- the responsible reviewer; and
- whether it must be resolved before a named lifecycle transition.

An assumption shall not conceal a prerequisite, discrepancy, unsupported state,
or authority decision. A slice with no assumptions shall declare `NONE`.

---

## 14. Invariants

Every specification shall identify:

- applicable Engineering Kernel invariants;
- applicable parent and predecessor invariants; and
- slice-specific invariants.

Slice-specific invariants shall cover, where applicable:

- identity and lineage;
- deterministic ordering;
- immutability;
- ownership and dependency direction;
- conservative failure behavior;
- evidence completeness;
- authority separation; and
- prohibited side effects.

An invariant shall state the scope in which it must remain true and the evidence
used to evaluate it. A slice may refine but shall not weaken a governing
invariant without separately approved constitutional architecture.

---

## 15. Repository Scope

### 15.1 Affected repository paths

The specification shall declare every path or bounded path pattern an authorized
implementation may affect. This declaration is the permitted ownership envelope;
it is not evidence that every declared path changed.

Each declaration shall identify:

- path or bounded pattern;
- owning system or repository responsibility;
- permitted change kinds;
- reason the path is required; and
- cross-boundary approval when the path has another owner.

Repository-wide or otherwise unbounded declarations require explicit rationale
and accountable human review.

### 15.2 Declared changed-file scope

Architecture preparation and implementation shall each declare their own exact
expected changed-file scope. Every file shall have one expected change kind:

- `ADD`;
- `MODIFY`;
- `RENAME` with source and destination; or
- `DELETE` when destructive repository action is explicitly governed.

The observed change set shall be compared with the declaration before
implementation approval and every authorized repository transition. An
unexpected file, missing declared file, or different change kind is a
discrepancy requiring disposition.

A path envelope shall not substitute for exact changed-file scope. Untracked,
staged, unstaged, ignored-but-relevant, generated, and repository-metadata state
shall be considered when applicable.

---

## 16. Acceptance Criteria

Every acceptance criterion shall:

- trace to a responsibility, invariant, exclusion, or boundary;
- identify the governed subject and named lifecycle review;
- identify observable supporting evidence;
- state an unambiguous required outcome where objective evaluation is possible;
- include applicable negative behavior;
- identify the accountable reviewer for judgment-based acceptance; and
- state that satisfaction grants no authority by itself.

Acceptance criteria shall cover exact changed-file scope, exclusions, quality
gates, dependencies, lineage, and authority boundaries in addition to the
slice's positive outcome.

Criteria shall not claim that absence of a finding proves an unexamined property.

---

## 17. Test Strategy

Every specification shall state whether executable tests are applicable.

When executable tests are applicable, the strategy shall identify required:

- unit or contract coverage;
- positive behavior;
- negative and prohibited behavior;
- boundary and failure behavior;
- missing, malformed, unsupported, and contradictory inputs;
- deterministic identity and ordering;
- lineage preservation;
- authority-boundary behavior; and
- regression scope.

When executable tests are not applicable, the specification shall state why and
shall identify the inspection, consistency, traceability, or other evidence used
for review. Documentation-only status shall not be used to claim executable
coverage that does not exist.

Test success is validation evidence and grants no approval or authority.

---

## 18. Quality Gates

Every specification shall declare:

- exact quality-gate commands;
- required execution environment;
- required working directory or repository identity;
- ordering or stop conditions when relevant;
- scope-specific inspections;
- expected result semantics; and
- required recording of results.

Gate evidence shall preserve the exact command, completion state, exit result,
and relevant output. A skipped, unavailable, failed, interrupted, or partially
executed gate shall remain explicit and shall not be represented as passing.

When a gate cannot observe untracked or generated content, the specification
shall require an additional scope-appropriate inspection rather than infer
coverage.

Passing gates do not establish architectural conformance, implementation
approval, repository authority, closeout, or certification.

---

## 19. Review Requirements

The specification shall identify the accountable review required at each
applicable lifecycle boundary.

Implementation review shall consider at least:

- the approved architecture and exact implementation authorization;
- exact repository baseline and observed changed-file scope;
- conformance of responsibilities, inclusions, and outputs;
- preservation of non-responsibilities, exclusions, and deferred boundaries;
- dependency direction and repository ownership;
- assumptions and invariants;
- acceptance, test, and quality-gate evidence;
- negative-authority evidence;
- discrepancies, deferrals, and residual risks; and
- the exact implementation identity to which the decision applies.

A review record shall identify:

- accountable reviewer or reviewer role;
- decision;
- exact subject and scope;
- evidence considered;
- unresolved findings;
- limitations; and
- authority effect.

Review completeness and review approval are distinct. An artifact shall not
approve or certify itself.

---

## 20. Authority Effect

Every specification shall state:

- authority already granted;
- the attributable source of that authority;
- exact authorized subject and scope;
- authority explicitly withheld;
- the effect of any decision recorded in the specification;
- the next transition requiring separate accountable human authority; and
- later capabilities that remain unauthorized.

Authority assertions shall identify:

- authority class;
- accountable issuer;
- decision;
- exact subject;
- exact scope;
- evidence reference;
- effective lifecycle transition; and
- explicit limitations.

Authority is non-transitive. It shall not expand through dependency,
predecessor completion, delegation, summary, persistence, publication, successful
execution, passing validation, branch creation, commit, or merge.

A specification may record authority but cannot manufacture accountable human
authority through its own status or prose.

---

## 21. Closeout Requirements

Every specification shall state whether closeout and certification are required
and shall define their distinct evidence boundaries.

Slice closeout shall identify:

- exact reviewed or integrated subject;
- governing architecture and implementation authority;
- repository identity and integration state where applicable;
- acceptance, test, and quality-gate results;
- exact observed changed-file scope;
- discrepancies and dispositions;
- retained deferrals and residual risks;
- accountable human closeout decision; and
- authority explicitly not granted by closeout.

Certification, when required, shall identify its exact certified subject,
evidence package, accountable certifier, result, limitations, and relationship
to closeout.

Integration does not imply closeout. Closeout does not imply certification or
authorize a successor unless an explicit decision separately grants that
effect.

---

## 22. Discrepancy Handling

Differences among governance, architecture, decisions, implementation, tests,
reports, repository state, and Git history shall be recorded rather than
silently resolved.

Each discrepancy shall identify:

- discrepancy identity;
- governed subject;
- conflicting sources and exact observations;
- detection context;
- effect on scope, evidence, or authority;
- current classification;
- accountable disposition when one exists; and
- retained unresolved or residual consequences.

Permitted classifications are:

- `UNRESOLVED`;
- `ACCEPTED`;
- `CORRECTED`;
- `SUPERSEDED`; and
- `NOT_APPLICABLE`.

Correction shall not rewrite historical evidence when a supplemental or
superseding record is required. `ACCEPTED` means an accountable human accepted
the explicitly bounded consequence; it does not make conflicting evidence
identical or correct.

Unknown, malformed, incomplete, unsupported, and contradictory evidence shall
remain visible.

---

## 23. Supersession

Supersession shall be explicit. A supersession declaration shall identify:

- supersession decision identity;
- superseding artifact;
- superseded artifact;
- exact prospective authority or semantic meaning replaced;
- reason for supersession;
- effective lifecycle state and repository identity;
- compatibility and migration consequences;
- accountable human decision; and
- retained historical lineage.

Supersession shall not be inferred from a newer date, filename, version, branch,
commit, merge, or apparently more complete document. It shall not erase or
silently edit superseded evidence.

Supersession eligibility, analysis, or recommendation does not grant
supersession authority.

---

## 24. Machine-Checkable Requirements

A requirement is machine-checkable only when a result can be derived from
explicit bounded inputs without architectural judgment or inference of human
authority.

Objective checks may determine:

- presence and uniqueness of required fields;
- identifier and declared-version syntax;
- use of recognized lifecycle, outcome, discrepancy, and change-kind values;
- presence of explicit parent, predecessor, dependency, and lineage
  declarations;
- internal reference and repository-path syntax;
- duplicate and ordering violations where ordering is normative;
- presence and uniqueness of declared changed files;
- internal consistency between lifecycle state and required decision-reference
  fields;
- use of permitted explicit absence or uncertainty values;
- exact observed-versus-declared changed-file differences when both bounded
  inputs are supplied; and
- contradictory declarations within the same bounded specification.

Machine evaluation may report structural facts and contradictions. It shall not:

- approve architecture;
- determine architectural sufficiency;
- establish that an assertion is true merely because it is present;
- authenticate a human identity;
- infer authority;
- accept risk or discrepancies;
- approve implementation;
- authorize repository transitions;
- close a slice; or
- certify a subject.

This standard defines semantic requirements only. It defines no schema,
validator, executable representation, or tooling.

---

## 25. Accountable-Human Judgment Requirements

Accountable human judgment is required to determine:

- whether the slice purpose delivers independently useful value;
- whether the architectural boundary is coherent, complete, and sufficiently
  narrow;
- whether responsibilities and non-responsibilities are sufficient;
- whether inclusions, exclusions, and deferrals preserve authority boundaries;
- whether assumptions are justified and risks are acceptable;
- whether invariants are correct and complete;
- whether predecessor, dependency, and lineage claims are semantically valid;
- whether affected paths respect repository ownership;
- whether acceptance criteria, tests, and gates are adequate and proportionate;
- whether implementation conforms to approved architecture;
- whether discrepancies and residual risks have acceptable dispositions;
- whether supersession is justified;
- whether an architecture or implementation should be approved;
- whether implementation or a repository transition should be authorized;
- whether a slice should be closed; and
- whether a governed subject should be certified.

Machine-produced evidence may inform but shall not replace accountable human
judgment. The accountable decision shall identify its subject, scope, evidence,
effect, and limitations.

---

## 26. Deterministic Specification Invariants

Every conforming slice specification shall preserve these invariants:

1. Every required semantic field has one identifiable meaning.
2. Equivalent declared facts do not change meaning because of heading order or
   presentation choice.
3. Ordering is explicit wherever order affects identity, interpretation, or
   output.
4. Missing and unknown values are explicit.
5. Identity, lineage, state, and authority are separate dimensions.
6. The same evidence is not silently assigned conflicting roles.
7. A derived statement retains its source attribution.
8. Contradictory evidence remains visible.
9. The exact repository scope is independently reviewable.
10. An earlier lifecycle result grants no later authority.
11. Historical evidence remains attributable after correction or supersession.
12. Product and Engineering System boundaries remain explicit.

When deterministic interpretation is not possible, the ambiguity shall be
recorded as a discrepancy rather than resolved through unstated context.

---

## 27. Conformance

A slice specification conforms to this standard only when:

- every required semantic field is present and uniquely identifiable;
- all explicit absence, uncertainty, and not-applicable declarations are
  permitted and justified;
- identity and lineage are internally consistent;
- lifecycle status and authority evidence remain separate;
- responsibilities and boundaries are reviewable;
- repository path and exact changed-file declarations are explicit;
- discrepancy and supersession rules are preserved;
- machine-checkable and accountable-human requirements are not conflated;
- Engineering Kernel principles and invariants remain intact; and
- an accountable human determines that the specification is architecturally
  sufficient for its named review.

Structural completeness is necessary but not sufficient for conformance. A
machine finding of structural completeness shall not be represented as
architecture approval or accountable-human conformance judgment.

Historical specifications created before this standard remain historical
evidence. They are not retroactively nonconforming, automatically migrated, or
silently normalized.

---

## 28. Standard Boundary

This standard is normative documentation. It defines no:

- template;
- validator;
- generator;
- playbook;
- schema;
- automation;
- continuous integration;
- executable tooling;
- CLI behavior;
- AI or multi-agent orchestration;
- Repository Knowledge capability;
- product behavior;
- product runtime behavior; or
- authority for ES-2 or any later slice.

Future slices may depend on this standard after receiving their own architecture
approval and implementation authorization. This standard shall not depend on a
future slice for its meaning, conformance, or authority.
