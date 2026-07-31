# POE Engineering System — Repository Knowledge Foundation

**Foundation identity:** `Engineering-System-Repository-Knowledge-Foundation`
**Foundation version:** `1.0`
**Status:** Normative documentation
**System:** POE Engineering System
**Governing architecture:** `Engineering-System-Architecture-Intent-Slice-ES-2`

---

## 1. Purpose and limits

The Repository Knowledge Foundation defines how manually curated repository
knowledge records represent existing evidence. Its purpose is to make the
identity, source, observation boundary, state, lineage, limitations, and ordering
of a claim independently reviewable.

Repository knowledge is a derived view. It does not replace governance,
architecture, decisions, implementation, tests, reports, certification records,
or Git history. It does not approve, authorize, certify, reconcile, normalize, or
modify its sources. A complete or `KNOWN` record grants no authority to act.

This foundation is documentation only. It defines no executable schema, parser,
validator, crawler, indexer, generator, query service, database, API, CLI,
automation, synchronization, inference, or product-runtime behavior.

## 2. Normative language

`Shall`, `shall not`, `required`, and `prohibited` are normative. `May` identifies
a permitted choice that does not weaken a requirement. An absent value shall not
be silently treated as `NONE`, known, verified, resolved, or not applicable.

## 3. Knowledge-record taxonomy

Every record shall have exactly one primary type:

1. **Artifact** — identifies a governed repository artifact and its class,
   subject, location, state, and lineage.
2. **Citation** — identifies the bounded source evidence supporting, limiting,
   contradicting, or contextualizing a claim.
3. **Repository State** — records an immutable commit, tree, ancestry relation,
   integration observation, or explicitly time-bounded mutable reference.
4. **Lifecycle Observation** — reports evidence of a subject's lifecycle state
   without creating or inferring a transition.
5. **Authority** — represents an attributable authority assertion and its exact
   subject, scope, effect, limitations, and evidence.
6. **Decision** — represents an attributable human decision, its inputs, outcome,
   effect, limitations, and evidence.
7. **Discrepancy** — preserves incompatible, missing, ambiguous, stale, or
   temporally divergent evidence and any separately evidenced disposition.
8. **Lineage** — represents governing, predecessor, derived-from, revision, or
   supersession relationships.
9. **Knowledge Claim** — states one bounded proposition derived from citations.

One record type shall not silently substitute for another. In particular,
lifecycle observation is not authority, validation is not decision, and a
knowledge claim is not authoritative source evidence.

## 4. Required record fields

Every record shall declare:

- one stable record identity;
- one exact governed subject identity;
- one record type;
- one knowledge state;
- temporal mode and observation boundary;
- one or more source citations, or explicit `UNKNOWN` or `UNVERIFIED` support;
- lineage where applicable, otherwise justified `NOT_APPLICABLE`;
- explicit limitations;
- deterministic placement and ordering keys; and
- revision identity when the representation materially changes.

Record identities, governed subjects, artifact identities, paths, titles,
branches, commits, content digests, lifecycle states, authority identities, and
revision identities are distinct fields.

## 5. Knowledge states

The closed knowledge-state vocabulary is:

- `KNOWN` — sufficient cited evidence supports the bounded claim at its declared
  observation boundary.
- `UNKNOWN` — required information is absent or cannot be determined from the
  inspected evidence.
- `UNVERIFIED` — information is asserted or assumed but has not been checked
  against the required evidence.
- `UNRESOLVED` — a question, discrepancy, or required disposition remains open.
- `CONTRADICTORY` — applicable evidence makes claims that cannot simultaneously
  hold for the stated subject, scope, and time.
- `STALE` — a claim supported at an earlier boundary is not a reliable statement
  of the selected current boundary.
- `SUPERSEDED` — explicit evidence replaces prospective meaning while retaining
  the earlier claim as historical evidence.
- `NOT_APPLICABLE` — the field or question does not apply to the exact subject
  and scope, with a stated rationale.

States shall not be silently converted. No state implies approval, truth beyond
its boundary, or authority to act. Age alone does not establish `STALE`, and a
newer artifact alone does not establish `SUPERSEDED`.

## 6. Stable record identity

The conceptual identifier form is:

```text
ES-KNOW-<RECORD-TYPE>-<STABLE-SUBJECT-KEY>
```

Canonical record-type tokens are `ARTIFACT`, `CITATION`, `REPOSITORY-STATE`,
`LIFECYCLE-OBSERVATION`, `AUTHORITY`, `DECISION`, `DISCREPANCY`, `LINEAGE`, and
`KNOWLEDGE-CLAIM`.

The stable subject key shall be lower-case, hyphen-separated, semantically
meaningful, and unique within its record type. Identity is curated rather than
inferred from filename, title, prose, branch, date, or position.

A stable record identity names an enduring semantic subject. A material revision
shall carry a distinct revision identity and `revision-of` lineage. A different
subject, scope, or proposition requires a different stable record identity.
Duplicate or ambiguous identities are explicit discrepancies.

## 7. Artifact references

An artifact reference shall identify:

- stable artifact identity and artifact class;
- exact governed subject;
- repository-relative path when applicable;
- immutable commit, tree, or blob boundary when repository content is claimed;
- document or schema version when applicable;
- lifecycle wording as source evidence, not inferred authority; and
- applicable lineage and limitations.

A path is a locator, not artifact identity. A mutable branch is not immutable
repository identity. Content at two commits shall not be assumed identical
without evidence.

## 8. Source citations

Every substantive claim shall cite exact evidence or explicitly declare its
support `UNKNOWN` or `UNVERIFIED`. Each citation shall include:

- stable citation identity;
- source artifact identity;
- source class;
- repository-relative path, or justified `NOT_APPLICABLE`;
- immutable observation commit;
- bounded locator such as a unique section, table, record, or commit identity;
- exact claim supported, limited, contradicted, or contextualized;
- citation role: `SUPPORTS`, `LIMITS`, `CONTRADICTS`, or `CONTEXT`;
- subject, scope, and time applicability; and
- verification state.

Line numbers may aid navigation but are not stable identity. A title, mutable
branch, or worktree path alone is insufficient for a historical repository claim.
A citation links evidence; it does not endorse the source or grant its authority.

## 9. Repository-state references

Repository-state records shall distinguish:

- full immutable commit identity;
- tree or blob identity when required;
- branch or tag as a mutable reference observed at a stated boundary;
- ancestry, parentage, containment, and integration evidence;
- upstream configuration as an observation; and
- worktree state as time-bounded and non-reproducible from a commit alone.

Abbreviated commit names are navigation aids only. Repository-state claims shall
use full commit identities. Branch movement after observation does not alter the
retained record.

## 10. Observation-commit boundary

`CURRENT_AT_COMMIT` means current only relative to one exact full commit and the
reference observations explicitly recorded for it. It does not mean current at
read time or after later commits.

All current-state records in one index revision shall share one observation
commit. Historical records may cite earlier commits and shall state their
relationship to that boundary. Later repository changes may cause a new revision
or a `STALE` assessment; they shall not rewrite the earlier observation.

Uncommitted-state claims shall identify their base commit and exact staged,
unstaged, and untracked evidence. They shall never be represented as committed
repository state.

## 11. Lifecycle observations

A lifecycle observation shall identify the exact subject, source status wording,
observed lifecycle state, observation commit, transition evidence found or absent,
knowledge state, discrepancy references, and temporal scope.

Document wording, branch presence, commits, merge containment, passing checks,
closeout, and certification are separate observations. None alone authorizes a
transition. When historical prose differs from later Git evidence, both remain
visible and a discrepancy record is required.

## 12. Authority records

An authority record shall identify authority class, accountable issuer or
`UNKNOWN`, decision, exact subject and scope, evidence, effective transition when
explicit, limitations, authority withheld, and temporal applicability.

The foundation records only attributable authority evidence. It shall not infer,
validate, delegate, expand, or create authority from record presence, lifecycle
labels, dependencies, successful checks, commits, merges, publication, or
certification-like wording.

## 13. Decision records

A decision record shall distinguish the accountable decision from its supporting
evidence and shall identify issuer, subject, inputs, outcome, effect, limitations,
affected records, discrepancy disposition if any, and temporal boundary.

Missing decision evidence remains `UNKNOWN` or `UNVERIFIED`. A knowledge curator
shall not manufacture a decision to make history appear complete.

## 14. Discrepancy records

A discrepancy record shall identify its stable identity, subject, boundary, all
available conflicting or missing claims, citations for every source, discrepancy
class, current knowledge state, review significance, attributable disposition if
one exists, and unresolved questions.

Permitted disposition descriptions are `UNRESOLVED`, `ACCEPTED`, `CORRECTED`,
`SUPERSEDED`, and `NOT_APPLICABLE`, each requiring explicit evidence. `CORRECTED`
does not rewrite historical evidence. Source hierarchy guides review but never
silently resolves a discrepancy.

## 15. Lineage and supersession

Canonical relationships are `governed-by`, `parent-of`, `child-of`,
`predecessor-of`, `successor-of`, `derived-from`, `revision-of`, `cites`,
`contradicts`, `supersedes`, and `superseded-by`.

Every relationship shall identify both subjects and source evidence. It shall not
be inferred from names, numbers, dates, proximity, or Git ancestry alone.

Supersession requires explicit evidence naming both subjects, the prospective
meaning replaced, effective boundary, compatibility consequences, and retained
historical lineage. Newness alone does not supersede.

## 16. Current and historical semantics

Every claim shall declare one temporal mode:

- `CURRENT_AT_COMMIT` — bounded current observation at one exact commit;
- `HISTORICAL_AT_COMMIT` — evidence or state at an earlier exact commit;
- `TIME_INDEPENDENT` — a semantic definition independent of changing repository
  state; or
- `UNBOUNDED` — prohibited for repository-state claims and retained only as an
  explicit defect pending correction.

Historical wording remains historical even when later evidence establishes a new
integrated state. A current view shall cite both the historical source and the
later repository evidence rather than editing either.

## 17. Authoritative-source hierarchy

Review shall consider sources in this order, subject to applicability, scope,
time, and authority class:

1. repository governance and the constitutional Engineering Kernel;
2. attributable accountable-human authority and decision records;
3. approved scope-specific architecture and normative standards;
4. exact Git identities, trees, tracked content, ancestry, and integration state;
5. implementation and tests as evidence of actual implemented behavior;
6. validation, review, closeout, and certification records within their bounds;
7. roadmaps, plans, and prospective descriptions; and
8. derived summaries, indexes, and knowledge records.

This ordering is not a universal conflict-resolution algorithm. Architecture may
govern intended scope while implementation evidences actual behavior. A lower
category may expose stale wording in a higher artifact. Conflicts remain explicit
until an attributable disposition exists.

## 18. Deterministic record ordering

Record-type order is the taxonomy order in Section 3. Within a record collection,
sort by:

1. canonical record-type ordinal;
2. stable subject key by Unicode code-point order;
3. stable record identity by Unicode code-point order; and
4. revision identity by Unicode code-point order.

Missing or duplicate ordering keys are discrepancies. Filesystem order, locale,
timestamps, dictionary order, and authoring order shall not determine placement.

Citations sort by source artifact identity, observation commit, bounded locator,
and citation identity. Relationships sort by relationship type, target identity,
and citation identity.

## 19. Deterministic index ordering

An initial index shall use this section order:

1. Repository governance and preservation principles
2. Engineering Kernel
3. Engineering System architecture and standards through ES-2
4. Integrated product phase and slice architecture
5. Certification and closeout identities
6. Repository-state identities
7. Authority and decision records
8. Discrepancy records
9. Lineage and supersession relationships

Within sections, records shall use Section 18 ordering. Intentional omissions and
the non-exhaustive boundary shall be explicit.

## 20. Curation responsibilities

The curator shall select one exact observation commit; inspect sources without
modifying them; assign stable identities; cite every substantive claim; distinguish
source text from interpretation; preserve uncertainty and contradiction; apply
canonical ordering; document omissions; and submit the candidate for accountable
review.

Curation authority permits representation only. It grants no authority belonging
to the represented artifacts or accountable humans.

## 21. Maintenance responsibilities

The maintainer shall treat each accepted index as a historical snapshot; use a new
observation commit for a new current view; preserve revision lineage; reassess
`STALE`, `CONTRADICTORY`, and `UNRESOLVED` records; retain citations to historical
sources; and never silently refresh, normalize, or delete prior evidence.

Maintenance is manual under this foundation. Automation, synchronization, and
generated indexes require separate architecture and authorization.

## 22. Non-authority and non-replacement rules

Repository knowledge shall not:

- approve architecture or implementation;
- authorize commit, push, merge, closeout, certification, or operations;
- assign classification, destination, migration, cleanup, or destructive authority;
- infer human authority from repository state;
- replace or rewrite cited sources;
- conceal contradictory or missing evidence;
- make a derived index authoritative over Git history; or
- authorize ES-3 or later work.

Passing checks establish validation evidence only. Publication of knowledge does
not establish truth beyond its boundary, acceptance, or authority.

## 23. Foundation boundary

This foundation is normative documentation implementing only ES-2. It remains
independent of product code and runtime. It creates no executable representation,
tool, template, playbook, workflow, integration, or later-slice authority.
