# Model Routing and Context-Economics Standard

**Document ID:** `Model-Routing-Standard`
**Status:** Approved documentation standard
**System:** POE Engineering System
**Slice:** ES-5 — Model Routing and Context-Economics Standard
**Governing architecture:** `Engineering-System-Architecture-Intent-Slice-ES-5`

## 1. Purpose and Boundary

This standard governs human-controlled selection and escalation among stable AI capability tiers for engineering execution. It uses the lowest capability tier sufficient for correct execution while preserving quality, repository evidence, and accountable-human authority.

Routing affects execution strategy only. It is advisory, documentation-only, and subordinate to Git and governed repository evidence. It does not create, infer, transfer, or expand approval, implementation, lifecycle, repository, certification, operational, migration, redirection, cleanup, preservation-release, destructive, or other authority.

This standard creates no automatic routing, model switching, agent delegation, tooling, scripts, hooks, CI, validators, shell configuration, product behavior, or Phase 6 behavior.

## 2. Stable Capability Tiers

Tiers are stable capability categories, independent of vendor, product, model family, price, entitlement, or availability. This standard defines exactly the following tiers. A future tier change requires separately reviewed architecture or a separately authorized and reviewed revision; it shall not silently redefine these tiers.

### Tier 1 — Procedural Execution

Tier 1 is for deterministic, mechanical, bounded, often high-volume work with a known procedure and expected evidence. Typical work includes Git and worktree inspection; exact changed-file verification; known quality-gate commands; trailing-whitespace or final-newline correction; routine approved documentation edits; approved commit or push procedures; output summarization; and isolated-worktree housekeeping.

Tier 1 may execute a known procedure. It shall not invent implementation design, resolve contradictory authority, or treat mechanical completion as review.

### Tier 2 — Engineering Implementation

Tier 2 is the normal implementation tier. Typical work includes approved product-slice implementation; model and service contracts; unit tests; routine refactoring; package exports; bounded debugging; interrupted-work recovery; implementation review; and conformance assessment against approved architecture.

Tier 2 may exercise bounded engineering judgment. It shall not prepare or materially revise architecture or adjudicate constitutional or high-consequence uncertainty.

### Tier 3 — Architecture and Adjudication

Tier 3 is for extensive system reasoning, adjudication, novel design, or high-consequence review. Typical work includes architecture preparation and review; constitutional Engineering System design; authority and lifecycle reconciliation; complex cross-slice reasoning; difficult debugging after a focused lower-tier attempt; security-sensitive review; preservation, integrity, recovery, or irreversible-operation reasoning; novel system design; and final high-consequence review.

Tier 3 is not a prestige default or a quality shortcut. It is reserved for architecture, adjudication, demonstrated complexity, or material consequence. Tier 1 is not lower quality when its work is procedurally bounded. Every tier remains subject to the same governing requirements and quality gates.

## 3. Replaceable Current Model Mapping

The current operational mapping is for usability only. It is not a permanent architectural dependency and does not change tier semantics, repository scope, or authority.

| Stable capability tier | Current model | Current shell convention |
| --- | --- | --- |
| Tier 1 — Procedural Execution | GPT-5.6 Luna | `codex-luna` |
| Tier 2 — Engineering Implementation | GPT-5.6 Terra | `codex-terra` |
| Tier 3 — Architecture and Adjudication | GPT-5.6 Sol | `codex-sol` |

The accountable human controls mapping acceptance and use. A future mapping update requires separately authorized documentation work based on current availability, capability, cost, and quota. Shell conventions are operational context, not repository authority; their absence in a non-interactive shell does not contradict accountable-human observation.

## 4. Classification and Routing

Classify the whole authorized task and the next safe unit using determinism and procedural boundedness; semantic interpretation or design; materially different approaches; repository and cross-slice scope; evidence consistency and completeness; test-design complexity; novelty and defect difficulty; security, integrity, preservation, recovery, or irreversibility consequence; constitutional or authority significance; and risk from an insufficient tier.

Task labels, file counts, and apparent brevity do not override consequence or ambiguity. A routine command can remain Tier 1 in a high-consequence project when it is bounded and authorized. A short document can require Tier 3 when it establishes architecture or reconciles authority. Separable authorized work may use distinct human-started sessions at safe boundaries; this is not automatic routing or delegation.

1. Use the lowest capability tier sufficient for correct execution.
2. Start routine implementation at Tier 2 unless it is clearly Tier 1 or Tier 3.
3. Use Tier 1 only for bounded procedures with known commands, outputs, and acceptance evidence.
4. Reserve Tier 3 for architecture, adjudication, demonstrated complexity, or high consequence.
5. Do not select Tier 3 merely for routine inspection, normal quality gates, ordinary whitespace correction, or an authorized routine commit or push.
6. Do not silently change tiers. A tier changes execution strategy only; it never changes scope, lifecycle, evidence requirements, or authority.
7. Human selection may conservatively exceed the default when current evidence supports additional uncertainty or consequence.

## 5. Human Override and Bounded Attempts

Routing recommendations are advisory. The accountable human selects the initial tier and any continuation. A Human Override may select a higher or lower tier than the default, but shall not weaken quality, evidence, safety, or authority boundaries. Selecting lower does not permit continuation when evidence shows insufficient capability; selecting higher does not expand scope or authority. State a material override in the work summary.

A bounded attempt is one authorized effort on the current problem, within approved scope, with a clear hypothesis or procedure, retained evidence, and an explicit success or stop condition. This applies equally to Tier 1, Tier 2, and escalation decisions. A tier change inherits the exact authorized scope and constraints; it does not authorize adjacent changes or later lifecycle stages.

## 6. Escalation and De-Escalation

Escalation is a recommendation, never an automatic transition. Before recommending it, stop at a safe boundary, preserve the worktree, retain relevant failure evidence, and state the trigger. Continue at the recommended tier only after accountable-human choice.

Recommend Tier 1 → Tier 2 when evidence conflicts; semantic interpretation is needed; materially different implementation approaches exist; one bounded Tier 1 attempt fails; implementation design or nontrivial test construction is needed; or mechanical continuation risks changing meaning or exceeding scope. A failed environmental command can instead be an environment or authority blocker when stronger reasoning cannot resolve it.

Recommend Tier 2 → Tier 3 when architecture must be created or materially revised; authority evidence is contradictory or unknown; cross-slice dependencies are unclear; integrity, preservation, recovery, security, or irreversible behavior is materially involved; a complex defect survives one bounded Tier 2 attempt; constitutional interpretation is required; system-level tradeoffs need adjudication; or incorrect resolution requires final high-consequence review. Do not use Tier 3 to bypass missing human authority or unavailable external facts; report those blockers.

De-escalate only when higher-tier work has produced a stable, approved, bounded procedure suitable for lower-tier execution. Do so at an explicit safe boundary, normally in a fresh session, with the governing architecture, exact scope, decisions, unresolved questions, and required evidence preserved in governed artifacts or a concise handoff. Never silently switch tiers, de-escalate unresolved ambiguity or authority, security, integrity, or irreversible-action uncertainty, or cycle tiers to conceal uncertainty. Re-escalate when a trigger recurs. De-escalation reduces cost, never review rigor or evidence obligations.

## 7. Sessions, Context, and Memory

Tier recommendation and session recommendation are separate decisions. A task may retain its tier but need a fresh session, change both, or change tier only at a safe boundary. Resume only a genuinely unfinished task whose scope, evidence, repository state, and authority remain current.

Start a fresh session at material lifecycle boundaries, including architecture preparation to implementation, implementation to review, and review to a separately authorized repository action. Do not carry unrelated work or later lifecycle stages across long sessions. Fresh sessions do not erase authority requirements, and resumed sessions do not inherit stale authorization.

Consult Repository Knowledge before reconstructing established history, but use memory only for orientation: it may suggest an initial tier, likely governing artifacts, or prior decisions. Memory never establishes current branch, HEAD, remote, worktree, changed-file state, scope, authorization, lifecycle, acceptance, repository authority, certification, operational condition, or migration, cleanup, destructive, or operational authority.

When current state matters, directly verify branch, HEAD, worktree, diffs, ancestry, remote state, and governed artifacts through Git and the repository. If memory and current evidence conflict, retain and report the discrepancy; do not silently choose, repair, or merge claims.

Use bounded commands and narrow output before ingesting large logs or documents; avoid repeated ingestion of unchanged history; retain complete evidence in governed artifacts or command logs while conversational context carries only a summary; summarize successful gates while retaining diagnostic failure evidence; keep authorization prompts short by citing stable workflows, exact artifacts, commits, and changed-file scope; and preserve unresolved discrepancies and assumptions explicitly.

### Reusable Human-Directed Workflows

A separately authorized reusable human-directed workflow may reference this standard to recommend an initial capability tier; identify safe escalation and de-escalation boundaries; distinguish tier recommendations from session recommendations; reduce repeated repository-history and context ingestion; and identify evidence to retain in a handoff or work summary. Such reference remains documentation-level unless separately authorized otherwise; it cannot automate model selection or switching, expand repository, lifecycle, implementation, operational, migration, cleanup, destructive, or certification authority, override its governing architecture, exact scope, quality gates, repository-evidence requirements, or accountable-human approval boundaries, or treat routing success as approval or lifecycle progression. The workflow shall preserve this standard's Human Override and advisory-routing rules.

## 8. Evidence, Quality, Cost, and Quota

Every tier obeys the same governing architecture, repository instructions, acceptance criteria, and required quality gates. Model success is execution evidence only, not approval, acceptance, certification, or permission for a repository or operational transition.

Keep routing evidence useful and proportionate. Normal work summaries may record selected tier and, when relevant, mapping; task category and material classification factors; escalation trigger and preserved boundary; human continuation decision; relevant repository identities and exact changed-file scope; gate summary and retained failure evidence; and unresolved uncertainty or mapping limitation. Do not require a dedicated metrics artifact, duplicate existing Git, architecture, review, or command evidence, retain unnecessary conversation transcripts, secrets, credentials, or unbounded output. Reviewers maintain tier semantics; the accountable human controls mapping and authority decisions, preserving history and reason for a changed mapping or rule.

Capability sufficient for correct execution comes before cost and quota. Then choose the least costly sufficient available tier; reserve Tier 3 for its stated uses; use bounded fresh context; avoid repeated insufficient-tier retries and premature escalation; and split safe procedural follow-through from higher-tier design. Low-overhead trend review may use existing session, Git, gate, and work-summary evidence; no metrics platform or automated collection is required.

Cost or quota never justifies reduced tests, skipped evidence or review, concealed failure, scope expansion, or unsafe continuation. If quota prevents the reasonably capable tier, stop safely and report the limitation.

Unknown or contradictory evidence must be reported, never normalized. Retain a lower-tier failure sufficiently to support escalation. Do not misclassify environmental, permission, network, or human-authority blockers as capability failures. Missing authority cannot be cured through escalation. If classification is uncertain, choose the more conservative tier or stop for accountable-human selection in proportion to consequence; if safe continuation is impossible, preserve the worktree and report the exact blocker.

## 9. Authority Neutrality

Routing remains authority-neutral:

```text
Authorized task and governing evidence
→ human-selected capability tier
→ execution evidence
→ separately required evaluation and human authority transitions
```

No tier may approve its architecture, authorize implementation, change lifecycle state, accept work, commit, push, merge, close out, certify, migrate, redirect, clean up, destroy, or operate merely because it completed a task. A stronger model does not broaden the task; a less expensive model does not reduce quality or evidence obligations. Human-controlled selection chooses execution capability; it does not delegate accountable authority.

## 10. Illustrative POE Examples

- Tier 1: inspect Git status and scope, run Ruff and `pytest`, verify exact changed-file scope, correct whitespace or final-newline defects, or execute an already approved commit or push procedure.
- Tier 2: implement an approved Phase 6C slice, write or revise unit tests, implement model and service contracts, perform routine refactoring, or recover an interrupted implementation against approved architecture.
- Tier 3: prepare a phase or Engineering System architecture, reconcile contradictory authority evidence, evaluate preservation, recovery, migration, or destructive-operation boundaries, adjudicate cross-slice tradeoffs, or conduct final high-consequence design review.

Examples do not override the actual task's evidence, ambiguity, consequence, or authority boundary.

## 11. Exclusions and Deferred Capabilities

This standard does not authorize or create automatic selection or switching, programmatic routing, scripts, shell changes, hooks, CI, validators, generators, scaffolds, benchmarking automation, agent delegation or multi-agent orchestration, output voting or consensus, automated quality adjudication, quota purchases or subscription changes, `AGENTS.md` changes, product or Phase 6 changes, commit/push/merge/closeout/certification, or ES-3, ES-4, ES-6, ES-9, or other Engineering System work.

Future work may, only with separate architecture, review, and explicit authorization, maintain the mapping; create reusable human-directed workflow guidance or non-executable review aids; assess automatic routing; or derive low-overhead aggregate reporting from existing evidence. Any automatic-routing proposal must independently preserve human authority, stable tiers, safe boundaries, observable reasons, uncertainty handling, quality invariance, manual override, and no scope expansion. This standard defines no executable schema, algorithm, switch mechanism, hook, script, CI integration, or validator.
