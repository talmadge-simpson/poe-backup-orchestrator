# Engineering System Architecture Intent — Slice ES-6

## Engineering Lifecycle Standard

**Document ID:** Engineering-System-Architecture-Intent-Slice-ES-6
**Status:** Approved architecture; implementation authorization withheld
**System:** POE Engineering System
**Slice:** ES-6 — Engineering Lifecycle Standard
**Baseline:** `b4048299a8525ac9405f98dcf180352a1a225087`
**Architecture authority:** Accountable-human architecture approval recorded; authority limited to the approved ES-6 architecture candidate
**Implementation authorization:** Remains withheld
**Repository authority:** Commit and publication of the approved architecture candidate on this feature branch are authorized; main integration remains unauthorized
**Other authority:** ES-6 implementation, certification, closeout, product, Phase 6, workflow, tooling, operational, migration, redirection, cleanup, destructive, ES-3, ES-4, ES-7, ES-9, and all other Engineering System authority remain unauthorized

---

## 1. Purpose

ES-6 prepares the architecture for a documentation-only Engineering Lifecycle
Standard. The future standard shall define the governed progression of
engineering work and the recommended begin, continue, checkpoint, resume, and
end boundaries for Codex sessions. It shall reduce repetitive prompting withou
weakening architecture-first governance, exact scope, evidence, quality gates,
independent review, interruption recovery, or accountable-human authority.

This architecture defines process semantics only. It does not execute,
automate, or authorize any lifecycle action.

## 2. Architectural Motivation

The Engineering Kernel defines a conceptual lifecycle, ES-1 defines slice
status and transition evidence, ES-2 defines repository-knowledge and
discrepancy semantics, and ES-5 defines capability tiers and context economics.
They do not yet define a complete session-oriented engineering lifecycle with
durable checkpoints and interrupted-work recovery.

Repository history demonstrates distinct architecture, implementation,
publication, integration, certification, and closeout events, but repeated
prompts often reconstruct this history and may mix responsibilities. ES-6 shall
provide a stable semantic reference so short authorizations can name an exact
state, responsibility, repository identity, and checkpoint. Efficiency shall
come from reuse of governed semantics, never from omitted verification or
inferred authority.

## 3. Scope

ES-6 architecture includes:

- one Engineering Responsibility State Model for governed engineering efforts,
  reconciled with the normative ES-1 lifecycle status vocabulary;
- state-specific purpose, inputs, entry and exit conditions, permissions,
  prohibitions, outputs, evidence, gates, checkpoints, authority, and recovery;
- explicit, non-transitive transition semantics;
- Codex session begin, continue, checkpoint, end, resume, abandonment, and
  capability-tier guidance;
- durable human-readable checkpoint requirements;
- interrupted-work recovery classes A through M;
- safe-stop, failure, discrepancy, repository-verification, and evidence rules;
- the relationship to future reusable human-directed workflows; and
- low-overhead context and prompt-economics measures.

The governed subject is engineering process documentation. Product lifecycle
state machines and runtime behavior are outside scope.

## 4. Responsibilities

The future standard shall:

1. require one current canonical ES-1 lifecycle status and one exact ES-6
   responsibility state;
2. bind work to one exact repository and worktree context;
3. name governing evidence, entry criteria, permitted and prohibited actions,
   required outputs, exit criteria, and transition authority;
4. make every state safely observable and recoverable;
5. distinguish state observation, successful work, approval, repository action,
   integration, certification, operations, and closeout;
6. define fresh-session and continuation defaults without controlling sessions;
7. relate lifecycle responsibilities to the advisory ES-5 capability tiers;
8. preserve failures, discrepancies, uncertainty, and incomplete work; and
9. enable later workflows to reference stable semantics without expanding them.

## 5. Non-Responsibilities

ES-6 does not execute work, maintain lifecycle state, decide that a transition
occurred, select or switch a model, create a session, validate conformance,
perform Git operations, approve any subject, or grant authority. It does no
replace the Engineering Kernel, a slice architecture, task-specific human
authorization, repository evidence, independent review, or certification.

## 6. Inputs

Governing inputs are:

- `AGENTS.md`;
- `docs/engineering-system/kernel/Engineering-Kernel.md`;
- `docs/engineering-system/standards/Slice-Specification-Standard.md`;
- `docs/engineering-system/standards/Model-Routing-Standard.md`;
- `docs/engineering-system/knowledge/Repository-Knowledge-Foundation.md`;
- `docs/engineering-system/knowledge/Repository-Knowledge-Index.md`;
- Engineering System architecture through ES-5;
- exact Git history through baseline
  `b4048299a8525ac9405f98dcf180352a1a225087`;
- applicable product architecture, standards, roadmaps, certification, and
  closeout evidence; and
- attributable task-specific accountable-human decisions.

Repository files and Git evidence remain authoritative within their scopes.
Derived knowledge aids orientation but does not replace current verification.
Contradictions shall remain visible.

## 7. Outputs

This architecture produces exactly one candidate:

```tex
docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-6.md
```

If this architecture is separately approved and implementation is separately
authorized, the expected future implementation artifact is:

```tex
docs/engineering-system/standards/Engineering-Lifecycle-Standard.md
```

That future file is not created or authorized by this architecture preparation.

## 8. Engineering Responsibility State Model

ES-1 remains normative for the canonical lifecycle status of a governed slice.
ES-6 does not redefine, replace, or advance that vocabulary. ES-6 responsibility
state identifies the exact engineering responsibility, session posture,
checkpoint, and recovery context currently being executed. One ES-1 lifecycle
status may contain or correspond to multiple ES-6 responsibility states. An
ES-6 responsibility state never changes ES-1 lifecycle status by itself.
Neither vocabulary creates authority: attributable accountable-human decisions
and exact repository evidence remain required for both.

Every governed effort shall declare its current ES-1 lifecycle status and
exactly one current ES-6 responsibility state:

1. `DISCOVERY_CURRENT_STATE_ASSESSMENT`
2. `ARCHITECTURE_PREPARATION`
3. `ARCHITECTURE_REVIEW`
4. `ARCHITECTURE_REVISION`
5. `ARCHITECTURE_APPROVAL`
6. `ARCHITECTURE_COMMIT`
7. `ARCHITECTURE_PUBLICATION`
8. `ARCHITECTURE_INTEGRATION_PREPARATION`
9. `ARCHITECTURE_MERGE_CREATION`
10. `ARCHITECTURE_INTEGRATION_VALIDATION`
11. `ARCHITECTURE_MAIN_PUSH`
12. `ARCHITECTURE_INTEGRATION_CLEANUP`
13. `IMPLEMENTATION_AUTHORIZATION`
14. `IMPLEMENTATION`
15. `IMPLEMENTATION_REVIEW`
16. `TARGETED_IMPLEMENTATION_REVISION`
17. `IMPLEMENTATION_APPROVAL`
18. `IMPLEMENTATION_COMMIT`
19. `IMPLEMENTATION_PUBLICATION`
20. `IMPLEMENTATION_INTEGRATION_PREPARATION`
21. `IMPLEMENTATION_MERGE_CREATION`
22. `IMPLEMENTATION_INTEGRATION_VALIDATION`
23. `IMPLEMENTATION_MAIN_PUSH`
24. `IMPLEMENTATION_INTEGRATION_CLEANUP`
25. `CERTIFICATION`
26. `OPERATIONAL_ACCEPTANCE`
27. `CLOSEOUT`
28. `INTERRUPTED_WORK_RECOVERY`
29. `BLOCKED_DISCREPANT`
30. `DEFERRED`
31. `ABANDONED`
32. `SUPERSEDED`

The sequence is conceptual, not automatic. Recovery and disposition states may
be entered only when supported by evidence and applicable authority. Each state
names one coherent responsibility and one authority boundary. Completion does
not authorize the next responsibility or change the ES-1 lifecycle status.

### 8.1 Non-Authorizing ES-1 Compatibility Mapping

The declared ES-1 status, ES-6 responsibility, and exact subject shall be
recorded together and checked against this mapping. A listed pairing means only
that the responsibility can be compatible with that observed status; it grants
no transition or authority.

| ES-6 responsibility state | Compatible ES-1 lifecycle status or status set |
| --- | --- |
| `DISCOVERY_CURRENT_STATE_ASSESSMENT`, `INTERRUPTED_WORK_RECOVERY`, `BLOCKED_DISCREPANT` | Any currently evidenced ES-1 status; do not change it |
| `ARCHITECTURE_PREPARATION` | `ARCHITECTURE_DRAFT` |
| `ARCHITECTURE_REVIEW`, `ARCHITECTURE_REVISION`, `ARCHITECTURE_APPROVAL` | `ARCHITECTURE_IN_REVIEW`; after an approval decision is recorded, `ARCHITECTURE_APPROVED` |
| `ARCHITECTURE_COMMIT`, `ARCHITECTURE_PUBLICATION`, `ARCHITECTURE_INTEGRATION_PREPARATION`, `ARCHITECTURE_MERGE_CREATION`, `ARCHITECTURE_INTEGRATION_VALIDATION`, `ARCHITECTURE_MAIN_PUSH`, `ARCHITECTURE_INTEGRATION_CLEANUP` | `ARCHITECTURE_APPROVED` or `REPOSITORY_TRANSITION_AUTHORIZED`, as established independently |
| `IMPLEMENTATION_AUTHORIZATION` | `ARCHITECTURE_APPROVED`; after the decision is recorded, `IMPLEMENTATION_AUTHORIZED` |
| `IMPLEMENTATION` | `IMPLEMENTATION_AUTHORIZED` or `IMPLEMENTATION_IN_PROGRESS` |
| `IMPLEMENTATION_REVIEW`, `TARGETED_IMPLEMENTATION_REVISION`, `IMPLEMENTATION_APPROVAL` | `IMPLEMENTATION_IN_REVIEW`; after approval is recorded, `IMPLEMENTATION_APPROVED` |
| `IMPLEMENTATION_COMMIT`, `IMPLEMENTATION_PUBLICATION`, `IMPLEMENTATION_INTEGRATION_PREPARATION`, `IMPLEMENTATION_MERGE_CREATION`, `IMPLEMENTATION_INTEGRATION_VALIDATION`, `IMPLEMENTATION_MAIN_PUSH`, `IMPLEMENTATION_INTEGRATION_CLEANUP` | `IMPLEMENTATION_APPROVED` or `REPOSITORY_TRANSITION_AUTHORIZED`; after verified integration, `INTEGRATED` |
| `CERTIFICATION` | `INTEGRATED`; after the certification decision is recorded, `CERTIFIED` |
| `OPERATIONAL_ACCEPTANCE` | The exact current ES-1 status established by governing evidence; ES-1 has no operational-acceptance status |
| `CLOSEOUT` | `INTEGRATED` or `CERTIFIED`; after the closeout decision is recorded, `CLOSED` |
| `DEFERRED`, `ABANDONED` | Last valid ES-1 status with an attributable outcome qualifier; neither is an ES-1 status |
| `SUPERSEDED` | Last valid ES-1 status; after the supersession decision is recorded, `SUPERSEDED` |

Future artifacts shall reject an unlisted pairing as incompatible and enter
`BLOCKED_DISCREPANT` without changing either declaration. Even a compatible,
completed responsibility requires separate evidence and accountable-human
authority for any ES-1 transition.

## 9. Responsibility-State Definitions

Each responsibility state exposes all 16 stable fields separately. Each state
names one coherent responsibility and one authority boundary.

### 9.1 Discovery and Current-State Assessment

- **Purpose:** Execute only the `DISCOVERY_CURRENT_STATE_ASSESSMENT` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `DISCOVERY_CURRENT_STATE_ASSESSMENT` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `DISCOVERY_CURRENT_STATE_ASSESSMENT` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `discovery_current_state_assessment checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.2 Architecture Preparation

- **Purpose:** Execute only the `ARCHITECTURE_PREPARATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_PREPARATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_PREPARATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_preparation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.3 Architecture Review

- **Purpose:** Execute only the `ARCHITECTURE_REVIEW` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** A fresh independent session is mandatory.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_REVIEW` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Modify or approve the subject, or combine candidate production with independent review.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_REVIEW` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_review checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.4 Architecture Revision

- **Purpose:** Execute only the `ARCHITECTURE_REVISION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Begin a fresh revision session; the reviser cannot perform renewed independent review.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_REVISION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Broaden scope, approve the subject, or serve as renewed independent reviewer.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_REVISION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_revision checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.5 Architecture Approval

- **Purpose:** Execute only the `ARCHITECTURE_APPROVAL` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_APPROVAL` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_APPROVAL` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_approval checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.6 Architecture Commit

- **Purpose:** Execute only the `ARCHITECTURE_COMMIT` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_COMMIT` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_COMMIT` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_commit checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.7 Architecture Publication

- **Purpose:** Execute only the `ARCHITECTURE_PUBLICATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_PUBLICATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_PUBLICATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_publication checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.8 Architecture Integration Preparation

- **Purpose:** Execute only the `ARCHITECTURE_INTEGRATION_PREPARATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_INTEGRATION_PREPARATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_INTEGRATION_PREPARATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_integration_preparation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.9 Architecture Merge Creation

- **Purpose:** Execute only the `ARCHITECTURE_MERGE_CREATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_MERGE_CREATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_MERGE_CREATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_merge_creation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.10 Architecture Integration Validation

- **Purpose:** Execute only the `ARCHITECTURE_INTEGRATION_VALIDATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_INTEGRATION_VALIDATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_INTEGRATION_VALIDATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_integration_validation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.11 Architecture Main Push

- **Purpose:** Execute only the `ARCHITECTURE_MAIN_PUSH` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_MAIN_PUSH` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_MAIN_PUSH` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_main_push checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.12 Architecture Integration Cleanup

- **Purpose:** Execute only the `ARCHITECTURE_INTEGRATION_CLEANUP` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ARCHITECTURE_INTEGRATION_CLEANUP` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ARCHITECTURE_INTEGRATION_CLEANUP` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `architecture_integration_cleanup checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.13 Implementation Authorization

- **Purpose:** Execute only the `IMPLEMENTATION_AUTHORIZATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_AUTHORIZATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_AUTHORIZATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_authorization checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.14 Implementation

- **Purpose:** Execute only the `IMPLEMENTATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.15 Implementation Review

- **Purpose:** Execute only the `IMPLEMENTATION_REVIEW` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** A fresh independent session is mandatory.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_REVIEW` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Modify or approve the subject, or combine candidate production with independent review.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_REVIEW` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_review checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.16 Targeted Implementation Revision

- **Purpose:** Execute only the `TARGETED_IMPLEMENTATION_REVISION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin a fresh revision session; the reviser cannot perform renewed independent review.
- **Authorized Actions:** Perform only actions intrinsic to `TARGETED_IMPLEMENTATION_REVISION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Broaden scope, approve the subject, or serve as renewed independent reviewer.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `TARGETED_IMPLEMENTATION_REVISION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `targeted_implementation_revision checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.17 Implementation Approval

- **Purpose:** Execute only the `IMPLEMENTATION_APPROVAL` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_APPROVAL` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_APPROVAL` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_approval checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.18 Implementation Commit

- **Purpose:** Execute only the `IMPLEMENTATION_COMMIT` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_COMMIT` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_COMMIT` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_commit checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.19 Implementation Publication

- **Purpose:** Execute only the `IMPLEMENTATION_PUBLICATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_PUBLICATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_PUBLICATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_publication checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.20 Implementation Integration Preparation

- **Purpose:** Execute only the `IMPLEMENTATION_INTEGRATION_PREPARATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_INTEGRATION_PREPARATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_INTEGRATION_PREPARATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_integration_preparation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.21 Implementation Merge Creation

- **Purpose:** Execute only the `IMPLEMENTATION_MERGE_CREATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_MERGE_CREATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_MERGE_CREATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_merge_creation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.22 Implementation Integration Validation

- **Purpose:** Execute only the `IMPLEMENTATION_INTEGRATION_VALIDATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_INTEGRATION_VALIDATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_INTEGRATION_VALIDATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_integration_validation checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.23 Implementation Main Push

- **Purpose:** Execute only the `IMPLEMENTATION_MAIN_PUSH` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_MAIN_PUSH` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_MAIN_PUSH` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_main_push checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.24 Implementation Integration Cleanup

- **Purpose:** Execute only the `IMPLEMENTATION_INTEGRATION_CLEANUP` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 1, escalating under ES-5 only for qualifying ambiguity.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `IMPLEMENTATION_INTEGRATION_CLEANUP` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `IMPLEMENTATION_INTEGRATION_CLEANUP` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `implementation_integration_cleanup checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.25 Certification

- **Purpose:** Execute only the `CERTIFICATION` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `CERTIFICATION` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `CERTIFICATION` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `certification checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.26 Operational Acceptance

- **Purpose:** Execute only the `OPERATIONAL_ACCEPTANCE` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `OPERATIONAL_ACCEPTANCE` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `OPERATIONAL_ACCEPTANCE` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `operational_acceptance checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.27 Closeout

- **Purpose:** Execute only the `CLOSEOUT` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `CLOSEOUT` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `CLOSEOUT` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `closeout checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.28 Interrupted-Work Recovery

- **Purpose:** Execute only the `INTERRUPTED_WORK_RECOVERY` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `INTERRUPTED_WORK_RECOVERY` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `INTERRUPTED_WORK_RECOVERY` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `interrupted_work_recovery checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.29 Blocked or Discrepant

- **Purpose:** Execute only the `BLOCKED_DISCREPANT` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2 for bounded diagnosis; Tier 3 for contradictory governance, authority, ancestry, or high-consequence ambiguity; Tier 1 only for prescribed read-only verification.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `BLOCKED_DISCREPANT` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `BLOCKED_DISCREPANT` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `blocked_discrepant checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.30 Deferred

- **Purpose:** Execute only the `DEFERRED` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `DEFERRED` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `DEFERRED` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `deferred checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.31 Abandoned

- **Purpose:** Execute only the `ABANDONED` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `ABANDONED` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `ABANDONED` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `abandoned checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.

### 9.32 Superseded

- **Purpose:** Execute only the `SUPERSEDED` engineering responsibility for one exact subject.
- **Authoritative Inputs:** Exact governed subject; current ES-1 status; governing artifacts; attributable authority; repository evidence; and preceding checkpoint.
- **Entry Criteria:** Inputs are current, the ES-1/ES-6 pairing is compatible, scope is exact, and no unresolved blocker prevents safe entry.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Perform only actions intrinsic to `SUPERSEDED` and explicitly authorized for the exact subject.
- **Prohibited Actions:** Perform any adjacent responsibility, infer authority, change another subject, or cross an excluded boundary.
- **Required Repository Verification:** Verify repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, immutable subject identity, and expected versus actual scope.
- **Required Evidence:** Retain authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld.
- **Required Outputs:** A bounded `SUPERSEDED` result and evidence package containing no adjacent responsibility.
- **Quality Gates:** Run state-applicable gates against the exact subject; incomplete or failed gates remain explicit and reuse must satisfy Section 20.
- **Safe Interruption Checkpoint:** Record `superseded checkpoint` with every identity required by Section 14.
- **Exit Criteria:** The bounded responsibility is complete or safely stopped, with exact outputs, gates, scope, and residual findings recorded; exit does not advance ES-1.
- **Accountable-Human Transition Authority:** Entry to any different responsibility requires an attributable decision naming that responsibility and exact subject.
- **Recovery Behavior:** Begin read-only, preserve completed evidence, classify under A through M, and resume only unfinished work whose authority remains current.
- **Invalid-Transition Behavior:** Stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M when exact compatibility cannot be established.


## 10. Entry and Exit Criteria

Entry to every state requires:

1. exact governed subject, canonical ES-1 lifecycle status, and current ES-6
   responsibility state;
2. exact authorized responsibility and accountable issuer;
3. exact repository, worktree, branch, HEAD, baseline, and relevant remote refs;
4. applicable governing architecture, standards, decisions, and checkpoints;
5. stated inclusions, exclusions, affected paths, and expected outputs;
6. current authority whose scope covers the state but no later state; and
7. no unresolved condition that makes safe entry impossible.

Exit requires all state-specific outputs, gates, checkpoint evidence, exact
changed scope, residual failures/discrepancies, and a safe-stop repository state.
Exit means the current responsibility is complete or safely stopped. It does no
authorize entry to another state.

## 11. Authority Transitions

Transitions are explicit, attributable, bounded, independently verifiable, and
non-transitive. At minimum:

- architecture approval precedes implementation authorization;
- implementation review precedes implementation approval and commit;
- explicit approval precedes every commit;
- feature publication is separate from main integration;
- merge creation is separate from validation and push;
- main integration is separate from certification or operational acceptance;
- certification or operational acceptance is separate from closeout;
- product certification is separate from operational authority; and
- cleanup or destructive work always requires its own applicable authority.

Passing tests never authorizes commit, merge, push, certification, migration,
redirection, cleanup, destruction, or operations. Merge success never implies
push authority. Push success never implies cleanup, certification, operations,
or closeout. An agent may recommend a transition but shall not self-authorize it.

## 12. Session-Orchestration Model

A fresh Codex session is the default for architecture preparation;
implementation after architecture approval; independent architecture or
implementation review; targeted revision after review; commit and publication;
main integration; certification or operational acceptance; closeout; and
recovery when earlier session state is unreliable.

After architecture revision or targeted implementation revision, renewed
independent review shall occur in a fresh session. The reviser shall not serve
as renewed independent reviewer of the revised subject, and the renewed
reviewer shall not be responsible for producing that revised candidate. A
prior reviewer may supply factual clarification, but clarification neither
substitutes for renewed independent review nor permits the reviser to perform
it. Accountable-human approval remains separate from revision and review.

Continuation is acceptable only when all are true:

- lifecycle responsibility and authorized scope are unchanged;
- repository, governing evidence, and authority remain current;
- exact worktree context is verified;
- context remains focused and sufficient;
- no unrelated work has entered the session; and
- continuation does not compromise independent review.

Checkpoint before a long operation, context compaction, interruption risk,
authority boundary, tier change, session end, or handoff. End at a completed
responsibility, material lifecycle boundary, reliable safe stop, unresolved
blocker, deferral, abandonment, or context contamination. Resume only from
verified repository and checkpoint evidence. Abandon a session when its contex
is unreliable, scope is mixed, authority is stale, or the repository has
advanced incompatibly; preserve the work and start recovery rather than blindly
restarting.

A tier change and a session change are independent. Work may change tiers in one
focused session after preserving evidence, or retain its tier but start fresh a
a material lifecycle or independence boundary.

## 13. Capability-Tier Relationship

ES-6 consumes ES-5 tiers without redefining their names or model mapping:

- Tier 1 — Procedural Execution: exact repository verification, approved gates,
  and prescribed commit, publication, integration, or cleanup steps;
- Tier 2 — Engineering Implementation: bounded implementation, routine recovery,
  targeted revision, and ordinary closeout analysis; and
- Tier 3 — Architecture and Adjudication: architecture, high-consequence review,
  contradictory authority, novel design, certification, and ambiguous recovery.

The least costly sufficient available tier is recommended after correctness and
consequence. A tier never changes scope, quality, evidence, or authority. A
human may override a recommendation. Capability insufficiency is distinct from
network, permission, environment, dependency, evidence, and authority failure.

## 14. Checkpoint Model

A checkpoint is durable, human-readable evidence sufficient for a fresh session
to identify the exact subject, completed responsibility, repository state,
evidence, gates, authority boundary, remaining work, and safe next action.
Conversation history alone is never authoritative.

Every checkpoint use or citation shall include:

- stable checkpoint name and exact governed subject;
- canonical ES-1 lifecycle status and current ES-6 responsibility state;
- immutable commit, tree, diff, or worktree observation identity as applicable;
- decision identity when the checkpoint records approval or disposition;
- repository path and worktree identity, branch, full HEAD, baseline, relevant
  remote identities, status, and exact scope;
- checkpoint payload location or retained evidence reference;
- governing architecture and authority evidence;
- outputs and their paths or immutable identities;
- gates, exact commands and arguments, results, subjects, and retained failures;
- discrepancies, blockers, temporary resources, and external side effects;
- authority explicitly withheld; and
- recommended next responsibility without claiming authorization.

Canonical checkpoints include: `repository state verified`, `architecture
candidate created`, `architecture review completed`, `architecture approval
decision recorded`, `architecture committed`, `architecture feature branch
published`, `architecture integration resources prepared`, `architecture merge
created`, `architecture integration validation completed`, `architecture main
push verified`, `architecture integration cleanup completed`, `implementation
authorization decision recorded`, `implementation candidate created`,
`implementation review completed`, `targeted implementation revision
completed`, `implementation approval decision recorded`, `implementation
committed`, `implementation feature branch published`, `implementation
integration resources prepared`, `implementation merge created`,
`implementation integration validation completed`, `implementation main push
verified`, `implementation integration cleanup completed`, `certification
decision recorded`, `operational-acceptance decision recorded`, `abandonment
decision recorded`, `supersession decision recorded`, and `closeout decision
recorded`. Checkpoint names alone never establish completion or authority.

## 15. Interrupted-Work Recovery

Recovery begins read-only and assigns exactly one top-level class:

| Class | Observed state | Required recovery posture |
| --- | --- | --- |
| A | No governed work began | Reverify entry criteria; begin only with current authority. |
| B | Branch exists but deliverable does not | Verify branch base and scope; create only if authority remains current. |
| C | Partial deliverable exists | Preserve valid content; resume only identified incomplete work. |
| D | Complete unreviewed deliverable exists | Verify scope and gates; proceed only to authorized review. |
| E | Reviewed deliverable awaits revision | Verify subject and findings; revise only selected findings when authorized. |
| F | Approved deliverable awaits commit | Verify approval subject equals current diff; commit only with authority. |
| G | Committed branch awaits publication | Verify commit and remote; push only with publication authority. |
| H | Published branch awaits integration | Verify remote commit and current main; integrate only with authority. |
| I | Merge exists and awaits complete current validation | Verify merge identity; complete gates without recreating it. |
| J | Validated merge awaits push | Verify no drift and gate subject; push only with authority. |
| K | Push completed and cleanup remains | Verify remote; clean only named resources with authority. |
| L | Repository state advanced independently | Compare ancestry and scope; preserve work pending authorized reconciliation. |
| M | Unexpected, contradictory, ambiguous, or inexact state | Preserve everything, record discrepancy, and stop for direction. |

Bounded substate handling is mandatory:

- staged but uncommitted candidates use C, D, E, or F according to completion,
  review, and approval evidence;
- a commit made from content different from the approved subject uses M;
- ambiguous push output or network failure after possible remote mutation uses M
  until remote verification establishes G, J, or K;
- partially completed quality gates and validation made stale by content,
  dependency, configuration, platform, or environment change use I;
- a removed temporary worktree with its branch remaining, a removed temporary
  branch with its merge commit reachable, and partially completed cleanup are K
  substates requiring independent inventory;
- repository-path or worktree mismatch uses M;
- unrelated active work in another worktree uses L when exact and reconcilable,
  otherwise M; and
- cleanup completes only after every authorized resource is reconciled without
  disturbing unrelated work or retained evidence.

Contradictory or unexpected evidence, or evidence unable to establish the exact
subject, takes precedence as class M. When remote mutation may have occurred,
verify the remote before retrying. When multiple recoverable substates apply,
use the most conservative class that preserves evidence and prevents duplicate
mutation. Recovery never authorizes the recovered responsibility.

## 16. Safe-Stop Rules

A safe stop shall cease mutation before an unapproved boundary; preserve valid
work without destructive cleanup; capture repository, worktree, authority, and
checkpoint evidence; identify completed, incomplete, and uncertain
responsibilities; retain diagnostic results; inventory temporary resources and
external effects; and state held and withheld authority. It shall assign a
recovery class or explain class M. A clean worktree is not required when
cleaning would discard evidence or exceed authority.

## 17. Failure and Discrepancy Handling

The future standard shall retain dirty or unexpected state; stale refs and
ancestry conflicts; missing architecture, authority, or checkpoints; failed,
partial, or stale gates; network, sandbox, permission, dependency, platform, and
environment failures; capability insufficiency; and incomplete cleanup.

Scope attribution precedes mutation. Remote advancement requires renewed
comparison. Failed gates remain failed until a permitted rerun succeeds against
the exact subject or a permitted waiver is recorded. Network ambiguity requires
remote verification before retry. Capability escalation cannot cure missing
authority. Contradictory evidence and invalid checkpoints enter
`BLOCKED_DISCREPANT` and class M.

## 18. Repository Verification

Verification shall include, as applicable: canonical repository and worktree
identity; branch, full HEAD, base, upstream, `origin/main`, and relevant refs;
ancestry, merge parents, tree identity, and first-parent diff; staged, unstaged,
untracked, ignored, and conflicted state; expected and actual file scope; other
worktrees and temporary branches; remote identities before and after mutation;
and confirmation that excluded scope did not enter the work.

Mutable facts shall be reverified at entry, before external or irreversible
actions, after failures, and at exit. Memory may orient inspection but never
establishes current repository state.

## 19. Evidence Requirements

Evidence shall be attributable, exact, current for its claimed boundary, and
independently verifiable. It includes governing artifacts and decisions,
repository identities, diffs, file inventories, review findings and
dispositions, gate subjects and results, checkpoints, failures, discrepancies,
and observable publication or integration results. Summaries cite rather than
replace authoritative evidence.

## 20. Quality-Gate Model

Each responsibility shall name applicable gates, exact subjects, freshness, and
reuse conditions. Prior successful gate evidence may be reused only when an
explicit recorded comparison between prior and current subjects verifies all of
these predicates:

- exact content, commit, tree, or diff subject is identical;
- exact command and arguments are retained;
- complete result and exit status are retained;
- required tool versions remain applicable;
- dependencies have not materially changed;
- configuration has not materially changed;
- platform and environment assumptions remain applicable;
- repository state relevant to the gate has not changed;
- no affected file changed;
- the governing architecture or workflow explicitly permits reuse;
- no required final gate is skipped; and
- reuse is evidence only and never authority.

Focused gates may precede expensive full gates. Required final gates remain
mandatory. Gate success does not approve, authorize, commit, publish, merge,
certify, accept operationally, close, migrate, redirect, clean, destroy, or
operate.

## 21. Reusable Workflow Relationship

Later, separately authorized human-directed workflows or static templates may
reference the future standard. They shall not replace architecture, expand
scope, automate or infer a decision or transition, weaken evidence or gates,
control sessions, route models automatically, bypass repository verification,
or combine responsibilities. ES-6 creates no workflow, playbook, or template.

## 22. Context and Prompt Economics

Context economy may use verified Repository Knowledge, full immutable
identities, exact paths, governed summaries, retained failure detail, stable
semantics, fresh sessions at material boundaries, and compact checkpoint
references. It never permits omitted current-state verification, weaker gates,
hidden uncertainty, stale evidence, or authority inference.

Every compact lifecycle prompt or continuation request shall identify directly
or through an exact checkpoint reference:

- exact governed subject;
- current ES-1 lifecycle status;
- current ES-6 responsibility state;
- exact authority;
- repository and worktree context;
- checkpoint identity;
- authorized next responsibility; and
- explicit exclusions or authority withheld.

Prompt reduction shall not remove these minimum identifiers.

## 23. Human Direction, Authorization, Override, and Waiver

- **Human Direction:** Ordinary selection among permitted tier or session
  options. It does not authorize a responsibility transition.
- **Transition Authorization:** Explicit accountable-human authority to enter
  one named responsibility state for one exact subject, naming issuer, evidence,
  scope, effect, limits, and authority withheld.
- **Override:** Accountable-human selection different from the default
  recommendation while remaining within governing rules. It does not expand
  scope or create waiver authority.
- **Waiver or Exception:** Departure from a normally required rule only when a
  higher governing artifact permits waiver, retaining the exact rule, subject,
  rationale, limits, duration, and retained risk.

Human direction or override shall not create waiver authority. No waiver may
override constitutional invariants, manufacture evidence, expand scope,
transfer product and Engineering System authority, or authorize another subject.

## 24. Assumptions

ES-6 assumes its baseline and governing ES-0, ES-1, ES-2, and ES-5 artifacts
remain applicable unless evidence establishes otherwise; accountable-human
decisions can be retained independently; Git is available for verification;
work may be interrupted; and a documentation-only standard can reduce repeated
prompting without tooling. Failed assumptions remain explicit and may block the
affected responsibility.

## 25. Invariants

1. Every active effort declares exactly one canonical ES-1 lifecycle status and
   exactly one compatible ES-6 responsibility state.
2. Every responsibility has one exact subject, authority boundary, and
   repository context.
3. Architecture precedes implementation.
4. Evidence and evaluation do not grant authority.
5. Completion and gates do not authorize another responsibility or ES-1 status.
6. Transitions are explicit, attributable, and non-transitive.
7. Independent review is separate from candidate production and revision.
8. Product and Engineering System authority remain separate.
9. Tier and session treatment are separate advisory decisions.
10. Conversation history is not repository or checkpoint authority.
11. Unknown, stale, unsupported, and contradictory states remain visible.
12. Valid completed work is preserved during recovery.
13. Cleanup, destructive acts, migration, redirection, and operations are never
    inferred from engineering progress.
14. ES-6 remains documentation-only, human-controlled, advisory, and
    model-neutral.

## 26. Dependencies

ES-6 depends on ES-0 constitutional boundaries; ES-1 canonical lifecycle,
identity, scope, review, gate, and authority semantics; ES-2 source,
current-state, discrepancy, and lineage semantics; ES-5 advisory tier and
context semantics; repository governance; and exact task-specific architecture.
It does not depend on ES-3, ES-4, ES-7, ES-9, product runtime, automation, or
multi-agent capability.

## 27. Exclusions

ES-6 excludes workflow implementation, playbooks, templates, scripts,
executable state machines, schemas, validators, generators, scaffolding, hooks,
CI, automation, automatic transitions, automatic model routing, automatic
session control, delegation, multi-agent behavior, product or Phase 6 changes,
`AGENTS.md` changes, other Engineering System capabilities, and every
unauthorized repository, certification, operational, migration, redirection,
cleanup, destructive, or preservation-release action.

## 28. Deferred Responsibilities

Separate future architecture and authority are required for the documentation-
only Engineering Lifecycle Standard implementation; reusable human-directed
workflows, playbooks, and static templates; prompt packages; machine-checkable
representation; tooling, persistence, reporting, or metrics; automatic routing
or session orchestration; and Repository Knowledge changes. Deferral grants no
authority or preferred implementation.

## 29. Repository Impact

Architecture preparation creates exactly one non-executable Markdown document:

```text
docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-6.md
```

No existing file, source, test, configuration, standard, product, Phase 6,
workflow, automation, or `AGENTS.md` path is affected.

## 30. Acceptance Criteria

The architecture is review-ready only when ES-1 remains the normative canonical
lifecycle vocabulary; all 32 ES-6 responsibility states are atomic and mapped
non-authorizingly to compatible ES-1 statuses; every definition exposes all 16
required fields; architecture approval and implementation authorization remain
separate; implementation approval and commit remain separate; certification,
operational acceptance, and closeout remain separate; abandonment and
supersession remain separate; cleanup remains separately bounded; renewed review
is independent and fresh; checkpoint identity is immutable and subject-specific;
recovery classes A through M include the required bounded substates and
precedence; gate reuse satisfies every predicate; human direction, transition
authorization, override, and waiver remain distinct; compact prompts retain
minimum identifiers; repository verification, evidence, safe stops, and failures
are explicit; and exactly one documentation-only architecture candidate exists
with all required gates passing.


## 31. Quality Gates

Architecture preparation requires:

```bash
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Review shall also verify exactly one new architecture document; no existing file
modification; no trailing whitespace; exactly one final newline; no
`AGENTS.md`, product, or Phase 6 change; no executable workflow or lifecycle
automation; and no other Engineering System slice change. Passing these gates
does not approve the architecture or authorize implementation, commit,
publication, integration, certification, or closeout.

## 32. Success Measures

Low-overhead review of existing Git, session, checkpoint, gate, review, and
closeout evidence should observe:

- shorter authorization and continuation prompts;
- fewer repeated history reconstructions and blind workflow restarts;
- fewer sessions mixing lifecycle responsibilities;
- reduced unnecessary Tier 3 usage without capability-related quality loss;
- successful recovery from named checkpoints;
- fewer accidental repository-state conflicts;
- fewer unnecessary repeated full-suite runs where valid evidence reuse is
  explicitly permitted;
- no increase in escaped defects;
- completed independent review and every required final gate;
- prevention of stale evidence and preservation of authority boundaries;
- exact-scope conformance;
- no expansion of human or product authority; and
- improved completed-slice throughput per Codex usage allocation.

Throughput, reduced Tier 3 use, fewer full-suite reruns, shorter prompts, and
faster checkpoint recovery are interpretable only alongside escaped-defect
evidence, independent-review completion, required final-gate completion,
stale-evidence prevention, authority-preservation evidence, and exact-scope
conformance. No efficiency measure may reward omitted review, stale evidence,
weaker gates, mixed responsibility states, or authority inference. No metrics
platform, automated collection, target manipulation, or waiver of quality
evidence is required or authorized.

## 33. Relationship to ES-3, ES-4, ES-5, and ES-9

- **ES-3** remains Repository Playbooks and Static Templates. It may later
  reference an approved ES-6 standard, but ES-6 creates no ES-3 artifact.
- **ES-4** remains machine-checkable architecture validation. ES-6 defines no
  schema, validator, executable transition model, or ES-4 behavior.
- **ES-5** remains the Model Routing and Context-Economics Standard. ES-6
  consumes its stable tier semantics and preserves the separation between tier,
  session, scope, evidence, and authority. ES-6 does not change model mappings or
  create automatic routing.
- **ES-9** remains multi-agent readiness. ES-6 creates no delegation,
  orchestration, voting, shared-state, or multi-agent capability.

Approval or implementation of ES-6 shall not prepare, implement, approve, or
authorize any of those distinct capabilities.

## 34. Architectural Decision

ES-6 is proposed as the architecture for a documentation-only Engineering
Lifecycle Standard. The design establishes one-responsibility-at-a-time
engineering semantics reconciled with ES-1 lifecycle status, explicit entry and
exit criteria, non-transitive human authority,
session boundaries, ES-5-neutral capability recommendations, durable
checkpoints, and conservative interrupted-work recovery.

This candidate is ready only for independent architecture review. Architecture
approval, implementation of
`docs/engineering-system/standards/Engineering-Lifecycle-Standard.md`, commit,
publication, main integration, certification, closeout, product work, Phase 6
work, and all other Engineering System capabilities remain unauthorized.
