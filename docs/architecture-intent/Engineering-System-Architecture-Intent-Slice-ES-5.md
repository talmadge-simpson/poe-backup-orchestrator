# Engineering System Architecture Intent — Slice ES-5

## Model Routing and Context-Economics Standard

**Document ID:** Engineering-System-Architecture-Intent-Slice-ES-5
**Status:** Approved architecture; implementation not authorized
**System:** POE Engineering System
**Slice:** ES-5 — Model Routing and Context-Economics Standard
**Parent context:** Engineering System roadmap
**Predecessor:** ES-2 — Repository Knowledge Foundation
**Governing kernel:** `Engineering-System-Kernel` version `1.0`
**Architecture-preparation authority:** Explicit accountable-human authorization limited to this document
**Architecture approval:** Granted by explicit accountable-human review
**Implementation authorization:** Not granted
**Repository authority:** Exact ES-5 architecture commit and feature-branch publication authorized; merge, closeout, and certification not authorized
**Other-slice authority:** ES-3, ES-4, ES-6, ES-9, and all other Engineering System work remain unauthorized

---

## 1. Purpose

Engineering System ES-5 prepares the architecture for a documentation-only
Model Routing and Context-Economics Standard. The future standard will govern
human-controlled selection and escalation among stable AI capability tiers so
that engineering work uses the lowest capability tier sufficient for correct
execution while preserving quality, evidence, and accountable-human authority.

Model routing is ES-5's primary concern. Context economics is a supporting
execution concern that helps routing and lifecycle work use sessions, evidence,
and model capacity efficiently; it is not a separate co-equal architecture
domain or an independent source of task classification.

Model routing affects execution strategy only. It does not create or expand
repository authority, architecture approval, implementation authorization,
lifecycle state, certification, migration authority, cleanup authority,
destructive authority, or operational authority.

This document prepares architecture only. It does not create the standard or
any executable routing behavior.

## 2. Architectural Motivation

The Engineering System establishes durable semantics for evidence, authority,
lifecycle, repository knowledge, and bounded slices. Model names, commercial
offerings, relative costs, and quotas are operationally useful but replaceable.
Embedding them as permanent architecture would couple stable engineering
governance to temporary vendor configuration.

Without a routing standard, routine procedural work may consume unnecessarily
strong capability, while difficult or high-consequence work may continue at an
insufficient tier without a clear escalation boundary. Long-lived sessions may
also repeatedly ingest unchanged history, combine unrelated lifecycle stages,
or rely on memory where current Git evidence is required.

ES-5 therefore separates stable capability tiers from current model mappings,
defines conservative classification and advisory escalation, and establishes
supporting context-economics rules for efficient routing and lifecycle execution
without automating selection or transferring authority.

## 3. Scope

ES-5 architecture includes:

- a stable three-tier capability model;
- a replaceable current-model mapping;
- task-classification criteria and default routing rules;
- explicit escalation and de-escalation principles;
- accountable-human control of model selection and continuation;
- supporting session-boundary and context-economics rules for efficient routing
  and lifecycle execution;
- memory and repository-evidence boundaries;
- quality, cost, quota, failure, and uncertainty principles;
- low-overhead observability and success measures;
- review and maintenance responsibilities;
- the relationship to reusable human-directed workflows; and
- the boundary around any future automatic-routing proposal.

The scope is documentation governance for engineering execution strategy. It
does not include product-runtime behavior or executable Engineering System
behavior.

## 4. Responsibilities

ES-5 shall define a future Model Routing and Context-Economics Standard that:

1. defines stable capability tiers independently from vendor and model names;
2. records the current mapping as replaceable operational configuration;
3. classifies tasks using evidence about complexity, consequence, ambiguity,
   and required judgment;
4. defaults routine implementation to Tier 2 unless clearly Tier 1 or Tier 3;
5. defines Tier 1-to-Tier 2 and Tier 2-to-Tier 3 escalation triggers;
6. makes escalation advisory pending explicit accountable-human continuation;
7. requires a safe boundary and preserved worktree before escalation;
8. defines conservative de-escalation without silent in-session switching;
9. preserves human control over initial selection, escalation, and continuation;
10. defines fresh-session and genuine-resumption rules;
11. constrains memory to orientation rather than current-state or authority
    evidence;
12. requires direct Git and governed repository evidence when current state
    matters;
13. keeps routing neutral to all approval and authority transitions;
14. preserves the same acceptance criteria and quality gates across tiers;
15. promotes cost and quota stewardship without sacrificing correctness;
16. defines handling for failure, uncertainty, contradiction, and insufficient
    capability;
17. defines low-overhead evidence and observability expectations;
18. assigns review and mapping-maintenance responsibilities;
19. describes compatibility with reusable human-directed workflows;
20. bounds any future automatic-routing relationship; and
21. state explicit exclusions and deferred capabilities.

## 5. Non-Responsibilities

ES-5 does not:

- implement the Model Routing and Context-Economics Standard;
- select or switch a model automatically;
- create executable routing logic, scripts, hooks, CI, validators, or tooling;
- modify shell configuration or verify supplied aliases through user files;
- benchmark models or adjudicate quality automatically;
- delegate work or orchestrate one or more agents;
- compare outputs through voting or consensus;
- purchase quota, change subscriptions, or control vendor accounts;
- modify `AGENTS.md`;
- alter product architecture, source, tests, CLI, runtime, or Phase 6 artifacts;
- approve architecture or implementation;
- infer lifecycle state, acceptance, certification, or repository authority;
- authorize operational, migration, redirection, cleanup, preservation-release,
  or destructive activity; or
- prepare or implement ES-3, ES-4, ES-6, ES-9, or another slice.

## 6. Inputs

The architecture is based on:

- `AGENTS.md`;
- `docs/engineering-system/kernel/Engineering-Kernel.md`;
- `docs/engineering-system/standards/Slice-Specification-Standard.md`;
- `docs/engineering-system/knowledge/Repository-Knowledge-Foundation.md`;
- `docs/engineering-system/knowledge/Repository-Knowledge-Index.md`;
- Engineering System architecture-intent documents through ES-2;
- repository evidence assigning ES-3 to Repository Playbooks and Static
  Templates, ES-4 to machine-checkable architecture validation, and ES-9 to
  multi-agent readiness; and
- accountable-human supplied operational context that `codex-luna`,
  `codex-terra`, and `codex-sol` launch the current Luna, Terra, and Sol models.

Repository artifacts remain authoritative for Engineering System semantics.
The supplied shell conventions are current operational context, not repository
authority or permanent architecture. Their absence from a non-interactive shell
would not contradict the accountable-human observation.

## 7. Outputs

Architecture preparation produces exactly:

`docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-5.md`

Following architecture approval and separate explicit implementation
authorization, ES-5 is expected to produce exactly one documentation-only
standard:

`docs/engineering-system/standards/Model-Routing-Standard.md`

This architecture does not create that standard, executable behavior, or any
other output.

## 8. Capability-Tier Model

Capability tiers express durable categories of reasoning and execution. They do
not identify a permanent vendor, product, model family, price, or entitlement.

### 8.1 Tier 1 — Procedural Execution

Tier 1 is intended for deterministic, mechanical, bounded, and high-volume work
whose procedure and expected evidence are already known. Typical work includes:

- Git and worktree inspection;
- exact changed-file verification;
- known-command and quality-gate execution;
- whitespace and final-newline correction;
- routine documentation edits within an approved scope;
- approved commit and push procedures;
- output summarization; and
- temporary or isolated-worktree housekeeping.

Tier 1 may execute a known procedure but shall not invent implementation design,
resolve contradictory authority, or substitute mechanical completion for review.

### 8.2 Tier 2 — Engineering Implementation

Tier 2 is the normal implementation tier. Typical work includes:

- product-slice implementation against approved architecture;
- model and service contracts;
- unit tests and routine refactoring;
- package exports;
- bounded debugging;
- interrupted-work recovery;
- implementation review; and
- conformance assessment against approved architecture.

Tier 2 may exercise bounded engineering judgment. It does not prepare or
materially revise architecture and does not adjudicate constitutional or
high-consequence uncertainty.

### 8.3 Tier 3 — Architecture and Adjudication

Tier 3 is intended for work requiring extensive system reasoning, adjudication,
novel design, or high-consequence review. Typical work includes:

- architecture preparation and review;
- constitutional Engineering System design;
- authority and lifecycle reconciliation;
- complex cross-slice reasoning;
- difficult debugging after a focused lower-tier attempt;
- security-sensitive review;
- preservation, integrity, recovery, or irreversible-operation reasoning;
- novel system design; and
- final high-consequence review.

Tier 3 is not a prestige default. It shall be reserved for architecture,
adjudication, demonstrated complexity, or material consequence.

### 8.4 Tier extensibility

This architecture defines exactly three tiers. A future revision may add tiers,
but an addition shall not silently redefine the identity, meaning, or expected
uses of Tier 1, Tier 2, or Tier 3. Adding a tier requires separately reviewed
architecture or a separately authorized and reviewed standard revision. ES-5
adds no fourth tier now.

### 8.5 Illustrative POE repository examples

The following examples are illustrative. They do not override classification of
the actual task, its evidence, ambiguity, consequence, or authority boundary.

- Tier 1: inspect Git status and worktree scope; run Ruff and `pytest`; verify
  exact changed-file scope; correct trailing-whitespace or final-newline defects;
  or execute an already approved commit or push procedure.
- Tier 2: implement an approved Phase 6C slice; write or revise unit tests;
  implement model and service contracts; perform routine refactoring; or recover
  an interrupted implementation against approved architecture.
- Tier 3: prepare a new phase or Engineering System architecture; reconcile
  contradictory authority evidence; evaluate preservation, recovery, migration,
  or destructive-operation boundaries; adjudicate cross-slice architecture
  tradeoffs; or conduct final review of high-consequence design.

## 9. Current Model Mapping

The current replaceable operational mapping is:

| Stable capability tier | Current model | Current shell convention |
| --- | --- | --- |
| Tier 1 — Procedural Execution | GPT-5.6 Luna | `codex-luna` |
| Tier 2 — Engineering Implementation | GPT-5.6 Terra | `codex-terra` |
| Tier 3 — Architecture and Adjudication | GPT-5.6 Sol | `codex-sol` |

The tier definitions are architecture. The model and shell mapping is
operational configuration documented for usability. A mapping change shall not
redefine the tiers, change repository scope, imply constitutional revision, or
create authority.

The accountable human controls mapping acceptance and use. Future maintenance
may update the mapping in the implemented standard through separately authorized
documentation work, based on current availability, capability, cost, and quota.

## 10. Task Classification

Classification shall consider the whole authorized task and the next safe unit
of work, using:

- determinism and procedural boundedness;
- need for semantic interpretation or design;
- number and materiality of plausible approaches;
- repository and cross-slice scope;
- evidence consistency and completeness;
- test-design complexity;
- novelty and defect difficulty;
- security, integrity, preservation, recovery, and irreversibility consequence;
- constitutional or authority significance; and
- quality risk if the task is attempted at an insufficient tier.

Task labels, file counts, or apparent brevity shall not override consequence or
ambiguity. A routine command remains Tier 1 even inside a high-consequence
project when the command itself is bounded and authorized. Conversely, a short
document may require Tier 3 if it establishes architecture or reconciles
authority.

When one authorized task contains separable work at different tiers, the human
may start distinct sessions at safe boundaries. This is not automatic routing
or agent delegation.

## 11. Routing Rules

1. Use the lowest capability tier sufficient for correct execution. Cost and
   quota inform stewardship only after capability, correctness, evidence, safety,
   and authority requirements are satisfied.
2. Begin routine implementation work at Tier 2 unless it is clearly procedural
   Tier 1 work or architecture/high-consequence Tier 3 work.
3. Use Tier 1 for bounded procedural work with known commands, outputs, and
   acceptance evidence.
4. Reserve Tier 3 for architecture, adjudication, demonstrated complexity, or
   high-consequence work.
5. Do not use Tier 3 merely for routine Git inspection, standard quality gates,
   ordinary whitespace correction, or normal authorized commit and push work.
6. Do not silently change model tier during an authorized task.
7. A selected tier changes execution strategy only; it does not change scope,
   lifecycle, evidence requirements, or authority.
8. Every tier must obey the same governing architecture, repository
   instructions, acceptance criteria, and required quality gates.
9. Model success is execution evidence only. It is not approval, acceptance,
   certification, or permission for a repository or operational transition.
10. Human selection may be more conservative than the default when current
    evidence supports additional consequence or uncertainty.

### 11.1 Human Override

Routing recommendations are advisory. The accountable human may select a higher
or lower tier than the default recommendation, subject to these rules:

- override shall not weaken quality, evidence, safety, or authority boundaries;
- selecting a lower tier does not authorize continuation when available evidence
  demonstrates that the tier's capability is insufficient;
- selecting a higher tier does not expand scope or authority; and
- an override should be stated when it materially differs from the default
  recommendation.

Accountable-human selection remains authoritative as a routing decision, but it
does not replace any separately required approval or authority transition.

## 12. Escalation Rules

Escalation is a recommendation, not an automatic transition. Before recommending
escalation, work shall stop at a safe boundary, preserve the worktree, retain
relevant failure evidence, and state the trigger. The task continues at the
recommended tier only after the accountable human explicitly chooses to do so.

A **bounded attempt** is one authorized engineering effort directed at the
current problem, limited to the approved scope, with a clear hypothesis or
procedure, preserved evidence, and an explicit success or stop condition. This
definition applies equally to a Tier 1 procedural attempt, a Tier 2 engineering
attempt, and any escalation decision based on the outcome.

A stronger tier inherits the exact authorized scope and constraints. Escalation
does not authorize adjacent changes, cleanup, destructive action, repository
transitions, or later lifecycle stages.

### 12.1 Tier 1 to Tier 2

Recommend Tier 2 when any of these conditions occurs:

- repository or task evidence conflicts;
- correct completion requires semantic interpretation;
- multiple materially different implementation approaches exist;
- one bounded Tier 1 procedural attempt fails;
- implementation design is required;
- nontrivial test construction is required; or
- proceeding mechanically would risk changing meaning or exceeding scope.

The bounded-attempt rule prevents repeated low-tier retries from obscuring an
engineering problem. A failed environmental command may instead be reported as
an environment or authority blocker when stronger reasoning would not resolve
it.

### 12.2 Tier 2 to Tier 3

Recommend Tier 3 when any of these conditions occurs:

- architecture must be created or materially revised;
- authority evidence is contradictory or unknown;
- cross-slice dependencies are unclear;
- integrity, preservation, recovery, security, or irreversible behavior is
  materially involved;
- a complex defect survives one bounded Tier 2 engineering attempt;
- constitutional Engineering System interpretation is required;
- multiple system-level tradeoffs require adjudication; or
- the consequence of an incorrect resolution requires final high-consequence
  review.

Tier 3 shall not be used to bypass missing human authority or unavailable
external facts. When no model can safely resolve the condition, report the
blocker and request accountable-human direction.

## 13. De-Escalation Principles

De-escalation is appropriate when the higher-tier work has produced a stable,
approved, and bounded procedure that a lower tier can execute correctly.

- De-escalate only at an explicit safe boundary, normally through a fresh
  session for the new unit of work.
- Preserve the governing architecture, exact scope, decisions, unresolved
  questions, and required evidence in repository artifacts or a concise
  handoff.
- Do not silently switch tiers within the active task.
- Do not de-escalate unresolved ambiguity, contradictory authority, security or
  integrity uncertainty, or irreversible-operation reasoning.
- Re-escalate if a lower-tier trigger recurs; do not repeatedly cycle tiers to
  avoid reporting uncertainty.
- A lower tier may execute an approved high-consequence procedure only when its
  bounded role is clear and all separately required human approvals remain in
  force.

De-escalation reduces execution cost, not review rigor or evidence obligations.

## 14. Session and Context-Economics Rules

The model capability-tier recommendation and the session recommendation are
distinct decisions. A task may remain at the same tier but require a fresh
session, change tier and require a fresh session, or change tier only at a safe
boundary without implying that the tier and session decisions are identical.
An existing session may resume only when scope, evidence, repository state, and
authority all remain current.

The future standard shall require:

1. start a fresh Codex session at material lifecycle boundaries, including the
   transition from architecture preparation to implementation, implementation
   to review, and review to separately authorized repository action;
2. resume a session only for a genuinely unfinished task whose scope, evidence,
   and authority remain current;
3. avoid carrying unrelated work or later lifecycle stages in a long-lived
   session;
4. consult Repository Knowledge before reconstructing established historical
   context;
5. verify current branch, HEAD, worktree, diffs, ancestry, and remote state
   directly through Git whenever current state matters;
6. avoid repeated ingestion of unchanged repository history;
7. select bounded commands and narrow output before ingesting large logs or
   documents;
8. retain complete evidence in repository artifacts, command logs, or other
   governed locations when conversational context need only carry a summary;
9. summarize successful quality gates while retaining detailed failure evidence
   sufficient for diagnosis and review;
10. keep authorization prompts short by referring to stable governed workflows,
    exact artifacts, commits, and changed-file scope; and
11. preserve unresolved discrepancies and assumptions explicitly rather than
    allowing context compression to normalize them.

Fresh sessions do not erase authority requirements. Resumed sessions do not
inherit stale authorization when repository state, scope, or lifecycle has
changed.

## 15. Memory Boundaries

Memory may suggest an initial tier, identify likely governing artifacts, recall
prior decisions, or reduce unnecessary historical reconstruction. It is
orientation evidence only until verified against applicable current sources.

Memory shall not establish:

- current branch, HEAD, remote, worktree, or changed-file state;
- present task scope or authorization;
- architecture approval or implementation authorization;
- lifecycle state, acceptance, repository authority, or certification;
- current operational conditions; or
- migration, cleanup, destructive, or operational authority.

When current state matters, direct Git and governed repository evidence are
authoritative. When memory and current evidence disagree, preserve and report
the discrepancy; do not silently choose, repair, or merge the claims.

## 16. Authority Neutrality

Routing is authority-neutral:

```text
Authorized task and governing evidence
→ human-selected capability tier
→ execution evidence
→ separately required evaluation and human authority transitions
```

No tier may approve its own architecture, authorize implementation, change
lifecycle state, accept work, commit, push, merge, close out, certify, migrate,
redirect, clean up, destroy, or operate merely because it completed a task.

Changing to a stronger model does not broaden the authorized task. Changing to
a less expensive model does not lower quality gates or evidence requirements.
Human-controlled selection is a choice of execution capability, not a delegation
of accountable authority.

## 17. Evidence and Observability

Routing evidence shall be useful and proportionate. The future standard should
support concise recording or reporting of:

- selected tier and, when relevant, current model mapping;
- task category and material classification factors;
- escalation trigger and preserved boundary;
- human decision to continue after an escalation recommendation;
- relevant repository identities and exact changed-file scope;
- quality-gate summary and retained failure evidence; and
- unresolved uncertainty or mapping limitation.

Routine Tier 1 and Tier 2 work need not create a dedicated metrics artifact or
duplicate evidence already present in Git, architecture, review, or command
output. Tier selection may be reported in normal work summaries. Evidence shall
not include unnecessary conversational transcripts, secrets, credentials, or
unbounded command output.

Reviewers maintain the semantic tier definitions. The accountable human controls
operational mapping changes and authority decisions. Standard maintenance shall
preserve prior repository history and state why a mapping or rule changed.

## 18. Cost and Quota Stewardship

Cost and quota are consequences and engineering constraints, not primary task-
classification authority or authority signals. Capability sufficient for
correct execution comes first. Stewardship then requires:

- choosing the least costly available tier among those sufficient for correct
  execution;
- reserving Tier 3 capacity for architecture, adjudication, demonstrated
  complexity, and high-consequence review;
- using fresh, bounded context instead of repeatedly carrying unrelated history;
- avoiding repeated failed attempts at an insufficient tier;
- avoiding premature escalation where a known bounded procedure is sufficient;
- separating procedural follow-through from higher-tier design work when safe;
  and
- measuring trends with low-overhead evidence rather than building a metrics
  platform.

Cost reduction shall not justify skipped evidence, reduced tests, weakened
review, concealed failures, scope expansion, or unsafe continuation. If quota
limits prevent use of the reasonably capable tier, the task shall stop safely
and the limitation shall be reported.

## 19. Failure and Uncertainty Handling

- Unknown or contradictory evidence shall be reported, not normalized.
- A lower-tier failure shall be retained with enough detail to support the
  escalation decision.
- One bounded Tier 1 procedural attempt that fails triggers Tier 2 consideration rather than
  repeated mechanical retries.
- One bounded Tier 2 engineering attempt at a complex defect triggers Tier 3 consideration
  rather than indefinite context accumulation.
- Environmental, permission, network, or human-authority blockers shall not be
  misclassified as model-capability failures.
- Missing authority cannot be cured through escalation.
- If classification itself is uncertain, select the more conservative tier or
  stop for accountable-human selection, proportionate to consequence.
- If safe continuation is impossible, preserve the worktree and report the
  exact blocker without inventing a resolution.

## 20. Assumptions

ES-5 assumes:

- accountable humans retain control of model selection and all authority
  transitions;
- the three capability tiers can remain meaningful as model offerings change;
- the supplied shell aliases are valid in the accountable human's interactive
  Bash environment;
- model availability, pricing, capability, and quotas may change;
- Repository Knowledge can reduce historical reconstruction but is not a
  substitute for current Git verification;
- normal Git, review, and quality-gate evidence can support observability without
  a metrics platform; and
- a separately reviewed documentation standard can govern human practice before
  any automatic-routing capability is considered.

If an assumption becomes false, reviewers shall assess the effect explicitly.
No assumption creates permission to alter scope or authority.

## 21. Invariants

1. Stable capability tiers remain independent from vendor and model names.
2. Routing affects execution strategy only.
3. The lowest capability tier sufficient for correct execution is preferred;
   cost and quota stewardship follow capability classification.
4. Routine implementation defaults to Tier 2 unless clearly Tier 1 or Tier 3.
5. Tier 3 remains reserved for architecture, adjudication, demonstrated
   complexity, or high-consequence work.
6. Tier changes are never silent.
7. Escalation stops at a safe boundary and remains advisory until explicitly
   continued by the accountable human.
8. Escalation and de-escalation never expand scope or authority.
9. Every tier preserves the same governing requirements and quality gates.
10. Model success never implies approval, acceptance, certification, or later
    authority.
11. Memory never establishes current repository state, lifecycle, scope, or
    authority.
12. Git and governed repository evidence remain authoritative for current state.
13. Contradictory or unknown evidence is preserved and reported.
14. Cost stewardship never overrides quality, evidence, safety, or authority.
15. No Engineering System capability approves or certifies itself.
16. The current architecture defines exactly three tiers; a future tier addition
    requires separate review and shall not silently redefine existing tiers.
17. Higher tiers are specialized for different levels of ambiguity, consequence,
    and reasoning. They are not inherently preferable for all work.
18. Tier 3 is not a quality shortcut, and Tier 1 is not lower quality when the
    task is procedurally bounded; every tier remains subject to the same governing
    quality and authority rules.
19. Routing recommendations are advisory. Accountable-human decisions remain
    authoritative, without allowing any model or selection to create approval or
    authority.

## 22. Dependencies

ES-5 depends on:

- ES-0 for constitutional mission, evidence, authority, lifecycle, ownership,
  and invariant semantics;
- ES-1 for bounded slice identity, scope, acceptance, quality-gate, review, and
  authority declarations; and
- ES-2 for traceable, commit-scoped repository knowledge and conservative
  treatment of stale, unknown, or contradictory claims.

ES-5 does not depend on ES-3, ES-4, ES-6, ES-9, product runtime, automatic
routing, shell implementation, or multi-agent capability. The supplied current
model mapping is operational context rather than an architectural dependency.

## 23. Exclusions

This architecture explicitly excludes:

- automatic model selection or switching;
- programmatic routing and routing scripts;
- shell configuration changes;
- hooks, CI, validators, generators, and scaffolds;
- model benchmarking automation;
- agent delegation and multi-agent orchestration;
- model-output voting or consensus;
- automated quality adjudication;
- quota purchasing and subscription changes;
- `AGENTS.md` modification;
- product architecture, source, tests, CLI, or runtime behavior;
- Phase 6 architecture, implementation, evidence, or operational changes;
- implementation of the ES-5 standard;
- ES-3 playbooks or templates;
- ES-4 machine-checkable validation;
- ES-6 or any unassigned later capability;
- ES-9 multi-agent readiness; and
- commit, push, merge, closeout, or certification.

## 24. Deferred Responsibilities

Subject to separate architecture and explicit authority, future work may
consider:

- implementation of the documentation-only Model Routing Standard;
- maintenance of the replaceable current-model mapping;
- reusable human-directed workflow guidance that references the standard;
- non-executable review aids;
- a separately scoped assessment of whether automatic routing is desirable; and
- low-overhead aggregate reporting derived from already available evidence.

Deferral does not reserve a slice identifier, approve a design, or authorize
implementation. Automatic routing, executable tooling, and multi-agent behavior
require their own architecture and are not implied future ES-5 work.

## 25. Repository Impact

Architecture preparation changes exactly one file:

`docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-5.md`

No existing file may be modified. In particular, this slice does not modify
`AGENTS.md`, Engineering System predecessors, product or Phase 6 artifacts,
source, tests, CLI, configuration, shell files, tooling, or Git history.

The expected future implementation path is proposed as
`docs/engineering-system/standards/Model-Routing-Standard.md`, but this
architecture does not create it.

## 26. Acceptance Criteria

ES-5 architecture is ready for accountable-human review only when:

1. exactly this one architecture-intent document is added and no existing file
   changes;
2. the purpose and documentation-only boundary are explicit;
3. stable capability tiers are independent from current model names;
4. Tier 1, Tier 2, and Tier 3 responsibilities are complete and distinct;
5. the Luna, Terra, and Sol mapping is clearly replaceable operational
   configuration;
6. task classification and default routing prefer the lowest capability tier
   sufficient for correct execution, with cost and quota treated as subsequent
   stewardship concerns;
7. all required escalation triggers and safe-boundary rules are defined;
8. escalation remains advisory pending explicit accountable-human continuation;
9. de-escalation preserves scope, evidence, quality, and authority;
10. session, context-economics, and memory boundaries are explicit, and session
    recommendations remain distinct from tier recommendations;
11. direct Git and governed repository evidence remain authoritative for current
    state;
12. routing is neutral to approval, lifecycle, repository, certification,
    operational, migration, cleanup, and destructive authority;
13. quality requirements are invariant across tiers;
14. cost and quota stewardship cannot override correctness or safety;
15. observability remains low overhead and requires no metrics platform;
16. ES-3, ES-4, and ES-9 reservations remain intact;
17. automatic routing and every other explicit exclusion remain absent;
18. the future standard is proposed but not created;
19. no executable behavior is introduced; and
20. all quality gates pass.

Review shall also confirm that bounded attempts, Human Override, tier
extensibility, no-prestige bias, and illustrative POE examples retain the
architecture's quality and authority boundaries.

Architecture review does not authorize implementation, commit, push, merge,
closeout, certification, or another slice.

## 27. Quality Gates

Architecture review shall run exactly:

```bash
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Review shall additionally verify:

- exactly one new ES-5 architecture document;
- no existing file modified;
- no trailing whitespace and a final newline;
- no `AGENTS.md`, product, or Phase 6 change;
- no standard implementation;
- no executable or automatic-routing capability; and
- no work on another Engineering System slice.

Passing gates are validation evidence only. They do not establish architectural
approval or any later authority.

## 28. Success Measures

The future standard should support low-overhead trend review using normal session,
Git, gate, and work-summary evidence. Measures include:

- percentage of sessions started on Tier 1 or Tier 2;
- reduced Tier 3 use for procedural work;
- fewer repeated repository-history reconstructions;
- shorter authorization prompts that reference stable governed artifacts;
- fewer context-heavy continuations across lifecycle boundaries;
- correct escalation when lower tiers encounter demonstrated complexity;
- no increase in escaped defects or failed quality gates;
- no authority expansion caused by model selection;
- reduced weekly Codex capacity consumption per completed slice; and
- preserved or improved implementation and review quality.

No target may encourage under-classification, concealed failure, skipped review,
or unnecessary tier churn. The standard shall not require a metrics platform,
new telemetry, or automated collection.

## 29. Future Automatic-Routing Relationship

ES-5 establishes semantic inputs that a future architecture might consider, but
it neither recommends nor authorizes automatic routing. Any future proposal must
be separately identified, architected, reviewed, and explicitly authorized.

Such a proposal would have to preserve human authority, stable tier semantics,
safe boundaries, observable reasons, uncertainty handling, quality invariance,
manual override, and the prohibition against scope expansion. It could not infer
approval or authority from model choice, task classification, or successful
execution.

No executable schema, selection algorithm, switch mechanism, hook, script, CI
integration, or validator is defined here.

## 30. Relationship to Reusable Workflows

Reusable human-directed workflows may reference the future ES-5 standard to
recommend an initial tier, identify a safe escalation boundary, reduce repeated
context ingestion, or describe evidence to retain. A workflow reference shall
not make routing automatic or override the workflow's own architecture, scope,
quality gates, and human approval boundaries.

ES-5 does not create a workflow, template, playbook, command, or delegation
mechanism. Reuse remains documentation-level guidance until separately
architected and authorized.

## 31. Relationship to ES-3, ES-4, and ES-9

ES-5 preserves the existing reservations:

- ES-3 remains Repository Playbooks and Static Templates. It may eventually
  reference an approved ES-5 standard, but ES-5 creates no ES-3 artifact or
  authority.
- ES-4 remains machine-checkable architecture validation. Structural validation
  cannot select a model, adjudicate quality, or infer authority, and ES-5 creates
  no ES-4 behavior.
- ES-9 remains multi-agent readiness. ES-5 defines no delegation, orchestration,
  shared-agent routing, voting, or multi-agent authority.

ES-5 is independently useful and does not depend on any of these capabilities.
Approval or later implementation of ES-5 shall not prepare, implement, or
authorize ES-3, ES-4, or ES-9.

## 32. Architectural Decision

Engineering System ES-5 is proposed as the architecture for a
documentation-only Model Routing and Context-Economics Standard built on three
stable capability tiers with a replaceable current-model mapping.

The standard shall govern human-controlled execution strategy, advisory
escalation, safe de-escalation, session boundaries, repository evidence, memory
use, quality preservation, and cost stewardship. It shall remain neutral to all
approval, lifecycle, repository, certification, operational, migration, cleanup,
and destructive authority.

This architectural decision is submitted for accountable-human architecture
review. It does not authorize the future standard, tooling, repository action,
automatic routing, or work on any other Engineering System slice.
