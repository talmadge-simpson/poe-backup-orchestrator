# Engineering System Architecture Intent — Slice ES-2

## Repository Knowledge Foundation

**Document ID:** Engineering-System-Architecture-Intent-Slice-ES-2
**Status:** Approved architecture; implementation not authorized
**System:** POE Engineering System
**Slice:** ES-2 — Repository Knowledge Foundation
**Specification version:** `1.0`
**Governed subject:** Architecture for traceable repository knowledge records and
an initial curated repository knowledge index
**Current lifecycle state:** `ARCHITECTURE_APPROVED`
**Parent context:** Engineering System roadmap
**Predecessor:** ES-1 — Slice Specification Standard
**Governing kernel:** `Engineering-System-Kernel` version `1.0`
**Repository baseline:** `d4ae9b0effa1deb9ebf7dda6f3461d20effda8cf`
**Architecture-preparation authority:** Granted only for this one documentation
artifact
**Architecture approval:** Granted by explicit accountable-human review
**Implementation authorization:** Withheld
**Repository authority:** Exact ES-2 architecture commit and feature-branch push
authorized separately; merge, closeout, and certification are withheld
**Later-slice authority:** ES-3 and all later slices remain unauthorized

---

## 1. Purpose

ES-2 defines the architecture for a Repository Knowledge Foundation: a
documentation-only, traceable view of facts, observations, decisions,
discrepancies, and relationships already evidenced by the repository.

The foundation shall let a reviewer locate what is known, why it is claimed,
which exact repository state was observed, which source remains authoritative,
and which uncertainty or contradiction remains. It shall not replace source
artifacts, manufacture authority, reinterpret historical evidence, or make a
current-state claim without an exact observation commit.

This document prepares architecture only. It does not implement ES-2 or
authorize creation of the proposed knowledge foundation or index.

## 2. Architectural Motivation

The repository contains governance, architecture, implementation, tests,
reports, decisions, and Git history whose relationships must presently be
reconstructed across many paths and commits. Those sources remain the evidence
of actual state, but their distributed form makes independent orientation and
discrepancy discovery costly.

A repository knowledge layer can provide a curated map without becoming a new
source of product, governance, or human authority. To be trustworthy, every
substantive claim must retain source citations, repository-state context,
lineage, status semantics, and visible uncertainty. A newer summary cannot
silently correct an older record, and a successful lifecycle observation cannot
grant a later authority transition.

ES-2 establishes those meanings and boundaries before any knowledge document,
index, template, schema, validator, generator, or automation is created.

## 3. Scope

This architecture includes:

- the purpose and boundary of repository knowledge;
- a conceptual knowledge-record taxonomy;
- stable semantic identity and revision identity;
- artifact references and attributable source citations;
- exact repository-state references and observation boundaries;
- lifecycle observations separated from authority and decision records;
- explicit uncertainty, discrepancy, lineage, and supersession semantics;
- current-state and historical-state interpretation;
- an authoritative-source hierarchy with conflict-preservation rules;
- deterministic record and initial-index ordering;
- the curated boundary of a prospective initial index;
- review and maintenance responsibilities;
- proposed documentation-only ES-2 outputs; and
- negative authority and non-replacement rules.

Architecture preparation changes exactly this file. The prospective ES-2
implementation remains separately reviewable and separately authorizable.

## 4. Responsibilities

ES-2 shall define a foundation that:

1. represents repository knowledge as individually identifiable records;
2. distinguishes source evidence, observation, interpretation, and decision;
3. cites exact artifacts and immutable repository states where claims depend on
   repository content;
4. distinguishes current-state observations from historical-state records;
5. records lifecycle observations without inferring lifecycle transitions;
6. represents human authority and decisions only by citing attributable source
   evidence;
7. preserves missing, unverified, unresolved, contradictory, stale,
   superseded, and not-applicable states explicitly;
8. preserves discrepancies rather than silently resolving them;
9. retains lineage and supersession without rewriting history;
10. defines deterministic ordering for records and the initial index;
11. limits the initial index to a curated, reviewable repository scope;
12. assigns accountable review and maintenance responsibilities; and
13. remains documentation-only and independent of product runtime.

## 5. Non-Responsibilities

ES-2 does not:

- approve its own architecture or authorize its implementation;
- declare a knowledge summary authoritative over its cited source;
- create, delegate, expand, or transfer human authority;
- decide that an observed lifecycle event grants a later transition;
- resolve a discrepancy merely by choosing the newest or highest-ranked source;
- rewrite governance, architecture, reports, certification, or Git history;
- create a repository crawler, knowledge extractor, validator, linter, schema,
  generator, indexer, query service, CLI, or API;
- define automation, CI, hosted-repository integration, or synchronization;
- define product behavior, product runtime dependencies, or Phase 6 behavior;
- inventory operational data or act on preservation, migration, redirection,
  cleanup, or certification; or
- implement ES-3, ES-4, ES-9, or any other later capability.

## 6. Inputs

The architecture is informed by these read-only inputs:

- `AGENTS.md` and repository governance;
- `Engineering-System-Kernel` version `1.0`;
- `Engineering-System-Architecture-Intent-Slice-ES-0`;
- `Engineering-System-Architecture-Intent-Slice-ES-1`;
- `Engineering-System-Slice-Specification-Standard` version `1.0`;
- relevant product architecture, preservation standards, roadmaps,
  certification and closeout records;
- repository paths, implementation, tests, and configuration as evidence of
  actual content; and
- Git commits, trees, branches, ancestry, and integration history.

Inputs retain their own identities and authority. An unavailable, ambiguous, or
contradictory input shall be reported with an explicit knowledge state rather
than inferred or repaired.

## 7. Outputs

Architecture preparation produces exactly:

```text
docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-2.md
```

A later, separately authorized ES-2 implementation may propose creating exactly:

```text
docs/engineering-system/knowledge/Repository-Knowledge-Foundation.md
docs/engineering-system/knowledge/Repository-Knowledge-Index.md
```

The foundation would define the normative documentation semantics. The index
would contain the initial curated records. Neither file is created or authorized
by this architecture-preparation work.

## 8. Knowledge Record Taxonomy

Each record shall have exactly one primary record type. Relationships to other
types shall be explicit references, not implicit type conversion.

1. **Artifact record** — identifies a governed repository artifact, its class,
   path or repository identity, scope, and relevant lineage.
2. **Citation record** — identifies the bounded source location supporting or
   contradicting a claim and the observation context in which it was read.
3. **Repository-state record** — identifies a commit, tree, branch observation,
   ancestry relationship, or worktree observation without treating a mutable
   branch name as immutable identity.
4. **Lifecycle-observation record** — reports evidence that a governed subject
   occupied or appeared to occupy a lifecycle state at an observation boundary.
5. **Authority record** — represents an attributable authority assertion found
   in source evidence, including its issuer, subject, scope, effect, limitations,
   and evidence; it does not create that authority.
6. **Decision record** — represents an attributable human decision, its exact
   subject, inputs, outcome, effect, limitations, and evidence.
7. **Discrepancy record** — preserves incompatible, missing, ambiguous, or
   temporally divergent claims and any separately evidenced disposition.
8. **Lineage record** — identifies governing, predecessor, derived-from,
   revision-of, or supersession relationships among stable identities.
9. **Knowledge-claim record** — states one bounded proposition derived from
   cited evidence, with its knowledge state, temporal meaning, and applicability.

Records shall use one of these explicit knowledge states:

- `KNOWN` — directly supported by sufficient cited evidence at the stated
  observation boundary;
- `UNKNOWN` — required information is absent or cannot be determined from the
  inspected evidence;
- `UNVERIFIED` — information is asserted or assumed but has not been checked
  against the evidence required to support it;
- `UNRESOLVED` — a question, discrepancy, or required disposition remains open;
- `CONTRADICTORY` — applicable sources make claims that cannot simultaneously be
  accepted under the stated scope and time boundary;
- `STALE` — a claim was accurate or supported at an earlier boundary but is not
  a reliable statement of the selected current boundary;
- `SUPERSEDED` — a separately evidenced supersession decision replaced the
  claim's prospective meaning while retaining it as historical evidence; and
- `NOT_APPLICABLE` — the field or question does not apply to the exact record
  subject and scope, with a stated rationale.

No state is equivalent to approval. `KNOWN` describes evidentiary support, not
truth beyond the declared boundary or authority to act.

## 9. Stable Identity Model

Every record shall declare:

- Engineering System identity;
- record type;
- stable record identifier;
- record semantic version or revision identity where applicable;
- exact governed subject identity;
- knowledge state;
- observation commit when the claim concerns repository state;
- predecessor or parent lineage where applicable; and
- citations supporting, limiting, or contradicting the record.

The conceptual identifier form is:

```text
ES-KNOW-<RECORD-TYPE>-<STABLE-SUBJECT-KEY>
```

`<RECORD-TYPE>` shall be selected from a documented canonical token set derived
from Section 8. `<STABLE-SUBJECT-KEY>` shall be a lower-case, hyphen-separated
semantic key unique within the record type. Identity is assigned through
accountable curation, not generated or inferred by this architecture.

A stable record identifier identifies the enduring semantic subject. A
materially revised representation shall also carry a distinct revision identity
and explicit `revision-of` lineage. A claim about a different subject, scope, or
semantic proposition requires a different stable identifier.

Titles, headings, paths, branch names, commit identities, content digests,
versions, states, and record identifiers are distinct. Moving a cited artifact
does not silently change record identity; changing a record's subject does.
Duplicate identifiers or ambiguous subjects are `CONTRADICTORY` or `UNRESOLVED`
and shall not be silently deduplicated.

## 10. Source Citation Model

Every substantive knowledge claim shall cite at least one source or explicitly
state why its source is `UNKNOWN` or `UNVERIFIED`. A citation shall identify:

- citation identity;
- source artifact identity and artifact class;
- repository-relative path, when the source is a repository file;
- immutable observation commit and, when needed, blob or tree identity;
- bounded locator such as a uniquely named section, record identity, or line
  range recorded for the observation commit;
- the exact claim supported, limited, or contradicted;
- citation role: `SUPPORTS`, `LIMITS`, `CONTRADICTS`, or `CONTEXT`;
- applicability in subject, scope, and time; and
- observation method or explicit inability to verify.

Line numbers are navigation aids and not stable source identity. A citation to
a mutable branch, worktree path, or prose title alone is insufficient for an
immutable historical claim. External or human decision evidence shall identify
its attributable retained record; absence of such evidence remains explicit.

A citation is evidence linkage, not an endorsement or authority grant.

## 11. Repository State References

Repository-state claims shall distinguish:

- immutable commit identity;
- tree or blob identity when content-level distinction is required;
- branch or tag name as an observed mutable reference;
- upstream relationship as observed configuration;
- ancestry or containment established at the observation commit; and
- worktree state as a time-bounded observation, never an immutable state.

The exact observation-commit boundary is the full Git commit identity declared
by a record. `Current` means current relative to that commit's tree and the
explicitly recorded reference observations made during curation. It does not
mean current at read time, at review time, or after later commits.

Claims involving uncommitted content shall identify the base commit, exact
changed-file evidence, staged/unstaged/untracked classification, and observation
time. Such claims cannot be reproduced from a commit alone and shall never be
represented as committed repository state.

A later commit does not mutate an existing observation. It may require a new
record revision, a `STALE` current-state assessment, or a new discrepancy.

## 12. Lifecycle Observation Model

A lifecycle observation shall identify:

- the governed subject and its stable identity;
- the lifecycle state asserted or observed;
- the observation commit and cited evidence;
- the source's own status language;
- whether required transition evidence was found;
- the knowledge state and any discrepancy reference; and
- the observation's temporal scope.

Document status, branch existence, commit history, merge containment, successful
checks, and certification wording are separate observations. None alone permits
the foundation to infer an authority transition. When source status and Git
history differ, both remain visible and a discrepancy record is required.

Historical status text shall remain historical. A current lifecycle view may
summarize later evidence only through a new, cited observation.

## 13. Authority and Decision Records

Authority and decision records are distinct from lifecycle observations.

An authority record shall identify:

- authority class;
- accountable issuer, or `UNKNOWN` when the retained evidence does not identify
  one;
- exact decision or permission;
- exact subject and scope;
- evidence reference;
- effective lifecycle transition, if explicitly stated;
- limitations and authority explicitly withheld; and
- temporal and repository applicability.

A decision record shall additionally distinguish the decision outcome from its
supporting evidence and identify any affected records or discrepancies.

The foundation records authority; it does not create, validate, delegate, or
extend it. Authority is not inferred from record presence, wording authored by
the foundation, a lifecycle label, dependency completion, passing gates, a
commit, branch, merge, publication, or certification-like terminology.

## 14. Discrepancy Model

A discrepancy record shall identify:

- stable discrepancy identity;
- exact subject and observation boundary;
- each conflicting, missing, ambiguous, or stale claim;
- citations for every available source;
- discrepancy class;
- current knowledge state;
- operational or review significance without inventing authority;
- any attributable disposition and its evidence; and
- retained unresolved questions.

Disposition values may describe `UNRESOLVED`, `ACCEPTED`, `CORRECTED`,
`SUPERSEDED`, or `NOT_APPLICABLE` only when their meaning and evidence are
explicit. `CORRECTED` describes prospective current knowledge; it does not
rewrite the historical source. Source hierarchy guides interpretation but does
not silently resolve a contradiction.

## 15. Lineage and Supersession

Records may declare these directed relationships:

- `governed-by`;
- `parent-of` / `child-of`;
- `predecessor-of` / `successor-of`;
- `derived-from`;
- `revision-of`;
- `cites`;
- `contradicts`; and
- `supersedes` / `superseded-by`.

Every relationship shall identify both stable subjects and its source evidence.
Relationships are not inferred from filenames, dates, numbering, proximity, or
Git ancestry alone.

Supersession requires explicit evidence identifying the superseding and
superseded subjects, the prospective meaning or authority replaced, effective
boundary, compatibility consequences, and retained historical lineage. A newer
record without that evidence is merely newer; it does not supersede another.

## 16. Current versus Historical State

Each knowledge claim shall declare one temporal mode:

- **CURRENT_AT_COMMIT** — a bounded statement about the selected observation
  commit and recorded reference observations;
- **HISTORICAL_AT_COMMIT** — a statement about evidence or state at an earlier
  identified commit;
- **TIME_INDEPENDENT** — a semantic definition whose claim does not depend on a
  changing repository state; or
- **UNBOUNDED** — prohibited for repository-state claims and permitted only as
  an explicit defect awaiting correction.

The initial index's current-state boundary shall be one exact full commit shared
by its current-state records. Historical records may cite earlier commits but
shall state their relationship to the index observation commit.

When the repository advances, the existing index remains a historical snapshot.
Maintenance may create a reviewed revision observed at a later commit. It shall
not edit earlier claims so they appear to have been made at the later boundary.
`STALE` is assessed relative to a declared newer boundary; it is not inferred
merely from age.

## 17. Authoritative Source Hierarchy

Knowledge records are derived views. For a claim within an applicable scope,
review shall consider sources in this order:

1. repository-wide governance and constitutional Engineering Kernel rules;
2. attributable accountable-human authority and decision records;
3. approved scope-specific architecture and normative standards;
4. exact repository identity and content: commits, trees, tracked files, and
   observed Git relationships;
5. implementation and tests as evidence of actual implemented behavior;
6. validation, review, closeout, and certification records within their exact
   subjects and boundaries;
7. roadmaps, plans, and prospective descriptions; and
8. derived summaries, indexes, and repository knowledge records.

This hierarchy is constrained by applicability, subject, scope, time, and
authority class. It is not a universal conflict-resolution algorithm. For
example, implementation is stronger evidence of actual behavior than a plan,
while approved architecture remains the authority for intended scope. A lower
item may expose that a higher item's current-state claim is stale. Conflicts
shall remain explicit until an attributable disposition resolves them.

The knowledge foundation and index are always secondary and never replace a
cited source.

## 18. Deterministic Ordering

The canonical order of knowledge states is:

```text
KNOWN
UNKNOWN
UNVERIFIED
UNRESOLVED
CONTRADICTORY
STALE
SUPERSEDED
NOT_APPLICABLE
```

The canonical order of record types follows their numbered order in Section 8.
Within a record collection, records shall sort by:

1. canonical record-type ordinal;
2. normalized stable subject key, compared as Unicode code points;
3. stable record identifier, compared as Unicode code points; and
4. revision identity, compared as Unicode code points.

All identifiers used as sort keys shall be unique. Missing or duplicate keys are
discrepancies, not permission to use filesystem, locale, creation-time, or
incidental authoring order.

The initial index shall sort sections in the scope order defined in Section 19.
Within each section, it shall use the canonical record ordering above. Citations
within a record shall sort by source artifact identity, observation commit,
bounded locator, and citation identity. Relationships shall sort by relationship
type, target identity, and source citation identity.

## 19. Initial Index Boundary

The prospective initial index shall be manually curated and documentation-only.
Its observation commit shall be the exact implementation baseline approved for
the future ES-2 implementation, not assumed from this architecture-preparation
branch.

The initial index shall include, in this deterministic section order:

1. repository governance and preservation principles;
2. Engineering Kernel identity, authority model, lifecycle, ownership, and
   invariants;
3. Engineering System slice architecture and normative standards through ES-2;
4. currently integrated product phase and slice architecture identities;
5. current certification and closeout identities;
6. repository-state identities needed to support integration and lifecycle
   observations;
7. attributable authority and decision records cited by included subjects;
8. unresolved or contradictory records affecting included subjects; and
9. lineage and supersession relationships among included records.

The initial index shall not attempt exhaustive indexing of every source file,
test, commit, branch, report, operational artifact, historical intermediate, or
external system. Selection shall favor constitutionally significant artifacts,
current integrated architecture, certification boundaries, and discrepancies
needed for accurate orientation. Every inclusion and intentional omission class
shall be stated.

No live repository scan, generation, inference, or automatic refresh is within
the initial index boundary.

## 20. Assumptions

1. Git commit identities and repository files provide evidence of repository
   state but do not independently establish human authority.
2. The Engineering Kernel and merged ES-1 standard remain governing inputs at
   the architecture observation baseline.
3. A future implementation can select one exact observation commit and curate a
   useful initial index without claiming exhaustive repository knowledge.
4. Human decisions not retained in attributable evidence cannot be represented
   as `KNOWN` authority.
5. Markdown can express the proposed conceptual records without becoming an
   executable schema.

If review cannot verify an assumption, it shall remain `UNVERIFIED` or become an
explicit discrepancy. Assumptions grant no implementation or repository
authority.

## 21. Invariants

1. Architecture precedes ES-2 implementation.
2. Evidence, evaluation, lifecycle observation, authority, and decision remain
   distinct.
3. Every substantive claim is cited or explicitly uncertain.
4. Every current repository-state claim has one exact observation commit.
5. Mutable references never substitute for immutable repository identity.
6. Knowledge records remain secondary to their authoritative sources.
7. Missing, unsupported, stale, and contradictory evidence remains visible.
8. Historical evidence is not silently rewritten, normalized, or deleted.
9. Supersession is explicit and retains prior identity and lineage.
10. Ordering is deterministic and independent of filesystem, locale, timestamps,
    and authoring accident.
11. A record or index creates no approval, implementation, repository,
    operational, or certification authority.
12. Engineering System knowledge does not enter product CLI or runtime.
13. No product, Phase 6, operational, or authoritative data is changed.
14. Repository changes remain within the exact separately authorized scope.
15. ES-2 does not authorize ES-3 or any later slice.

## 22. Dependencies

ES-2 depends on:

- `Engineering-System-Kernel` version `1.0` for constitutional semantics;
- the merged ES-1 Slice Specification Standard for identity, lifecycle,
  lineage, discrepancy, repository-scope, and authority distinctions;
- repository governance for preservation and approval boundaries;
- exact Git evidence for repository-state claims; and
- accountable-human architecture review before any implementation request.

Missing, stale, or contradictory dependency evidence blocks a `KNOWN` claim and
shall be represented explicitly. ES-2 has no dependency on product runtime,
product code, external services, or future Engineering System slices.

## 23. Exclusions

This architecture and any future implementation require separate scope review;
the present architecture preparation explicitly excludes:

- implementation of the proposed foundation or index;
- executable or machine-readable schemas;
- validators, linters, crawlers, parsers, generators, or scaffolds;
- query engines, databases, search services, APIs, or CLI commands;
- automated discovery, synchronization, refresh, or discrepancy resolution;
- automation, CI, hosted-repository workflows, and external integrations;
- templates and playbooks assigned to ES-3;
- product source, tests, runtime, configuration, and operational scripts;
- Phase 6 architecture, implementation, evidence, and authoritative data
  changes;
- historical-document rewriting or metadata migration;
- authority creation, approval inference, certification, or repository actions;
- AI or multi-agent behavior; and
- ES-3, ES-4, ES-9, or any later-slice implementation.

## 24. Deferred Responsibilities

Subject to separate architecture and authority, future slices may consider:

- ES-3 repository playbooks and static templates;
- ES-4 machine-checkable architecture validation;
- expanded or domain-specific knowledge collections;
- an executable representation of knowledge records;
- validators, generation, maintenance tooling, and automated refresh;
- query, reporting, or hosted-repository integration;
- discrepancy workflow and accountable disposition support; and
- ES-9 multi-agent readiness.

Deferral does not select a design, sequence, format, implementation, or authority.
ES-2 shall remain independently meaningful without any deferred capability.

## 25. Repository Impact

The authorized architecture-preparation impact is exactly one new file:

```text
docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-2.md
```

No existing file may be modified. No product, Phase 6, test, configuration,
tooling, automation, or operational artifact may change.

A future implementation may propose the two documentation paths listed in
Section 7, but their creation requires architecture approval and separate
implementation authorization. This document creates no package, import,
executable interface, or runtime dependency.

## 26. Acceptance Criteria

ES-2 architecture is ready for accountable-human architecture review only when:

1. exactly this one architecture-intent document is added and no existing file
   changes;
2. purpose, scope, responsibilities, boundaries, dependencies, assumptions,
   invariants, exclusions, deferrals, impact, and decision are explicit;
3. the taxonomy covers artifacts, citations, repository state, lifecycle,
   authority, decisions, discrepancies, lineage, and bounded claims;
4. all eight required knowledge states have precise, non-authorizing semantics;
5. stable identity is distinct from title, path, branch, commit, version, state,
   and revision identity;
6. every substantive claim is attributable to a source or explicitly uncertain;
7. repository-state claims use an exact observation-commit boundary;
8. current and historical state remain distinct and reproducible;
9. authority and decisions are recorded only from attributable evidence and are
   not manufactured by the knowledge layer;
10. discrepancies and supersession preserve all conflicting and historical
    evidence;
11. authoritative-source hierarchy preserves applicability and does not become
    silent conflict resolution;
12. record and initial-index ordering are deterministic;
13. initial-index scope is curated, bounded, ordered, and non-exhaustive;
14. the foundation and index remain secondary documentation;
15. tooling, schemas, validation, generation, automation, CI, product and Phase
    6 changes, historical rewriting, multi-agent behavior, and later-slice work
    remain excluded;
16. implementation, commit, push, merge, closeout, and certification authority
    remain explicitly withheld; and
17. all required quality gates and scope inspections pass.

Architecture review requires accountable-human judgment. Satisfaction of these
criteria does not approve architecture or authorize implementation.

## 27. Quality Gates

Architecture preparation shall run in the repository virtual environment:

```bash
source /home/talmadge/poe-backup-orchestrator/.venv/bin/activate
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Review shall also verify:

- exact one-file added scope;
- no staged or modified existing file;
- no trailing whitespace and a final newline;
- completeness and internal consistency of all required sections;
- preservation of source, identity, lifecycle, authority, and temporal
  distinctions;
- absence of executable schemas, tools, generators, automation, and CI;
- absence of product or Phase 6 changes; and
- explicit withholding of implementation and later authority.

Passing gates provide validation evidence only. They do not approve this
architecture or authorize implementation, commit, push, merge, closeout, or
certification.

## 28. Success Measures

ES-2 architecture succeeds when an accountable reviewer can determine, without
unstated context:

1. what a repository knowledge record means and does not mean;
2. how each record is stably identified, revised, cited, and ordered;
3. which exact commit bounds every current-state claim;
4. whether a claim is known, uncertain, contradictory, stale, superseded, or
   inapplicable;
5. how lifecycle observations differ from authority and decision evidence;
6. how current views retain historical state and supersession lineage;
7. which source remains authoritative for each kind of claim;
8. what the initial index includes and intentionally omits;
9. who must review and maintain the future documentation; and
10. why the knowledge layer cannot replace evidence or authorize action.

The future foundation owner shall curate identities and semantics; the future
index maintainer shall cite exact observation commits and preserve ordering;
architecture reviewers shall assess boundary and source applicability; and
accountable humans alone shall decide authority and discrepancy dispositions.
These responsibilities are architectural definitions, not appointments or
implementation authorization.

## 29. Future Relationship to ES-3, ES-4, and ES-9

ES-3 may use approved ES-2 identities and citations to make repository playbooks
and static templates traceable to governing knowledge. ES-3 shall not treat the
index as authority or silently embed stale claims.

ES-4 may later propose machine-checkable architecture validation using explicit
knowledge identities and states. ES-4 shall not infer architectural sufficiency,
truth, approval, or authority from structural completeness.

ES-9 may later consider multi-agent readiness using bounded, cited repository
knowledge. ES-9 shall preserve the same evidence and authority boundaries and
must not treat shared knowledge as permission to act.

ES-2 defines no detailed design, data exchange, tooling, workflow, or authority
for these slices. Each requires separate architecture and explicit authorization.

## 30. Architectural Decision

Engineering System ES-2 is approved as a documentation-only Repository Knowledge
Foundation bounded to traceable, deterministic, commit-scoped representations of
existing repository evidence.

The proposed knowledge layer shall use stable identities, exact citations,
explicit uncertainty, retained discrepancies, lineage, supersession, and a
curated deterministic initial index. It shall remain secondary to authoritative
sources and shall never create authority or replace historical evidence.

Accountable-human architecture review approved this decision as governing intent.
Exact commit and feature-branch push actions for this architecture document were
authorized separately. This decision does not authorize ES-2 implementation,
the proposed foundation or index files, merge, closeout, certification, ES-3, or
any later work.
