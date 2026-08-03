# Engineering Lifecycle Standard

**Document ID:** Engineering-Lifecycle-Standard
**Status:** Normative Engineering System standard
**System:** POE Engineering System
**Slice:** ES-6 — Engineering Lifecycle Standard

## Purpose

This standard operationalizes the approved ES-6 architecture as a documentation-only, human-governed Engineering Responsibility State Model. It makes one engineering responsibility, its evidence, its authority boundary, and its safe recovery posture explicit. It MUST reduce repeated context reconstruction without reducing verification, evidence, independent review, or accountable-human control.

## Normative Status

The words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative. This standard defines process semantics; it does not execute work, persist state, create sessions, select models, approve subjects, validate conformance, perform Git operations, or grant authority. Current repository and Git evidence are authoritative in their proper scope. Conversation history and model memory are orientation only.

## Scope

This standard applies to a governed engineering subject with one repository and worktree context. It defines responsibility states, human transitions, session recommendations, checkpoints, recovery, evidence, gate treatment, and compact lifecycle references. It does not govern product runtime state machines or operational behavior.

## Responsibilities

An effort MUST declare one exact governed subject, one current canonical ES-1 lifecycle status, one current ES-6 responsibility state, exact scope and exclusions, repository/worktree identity, governing inputs, and accountable-human authority. It MUST preserve incomplete, failed, discrepant, and uncertain work visibly.

## Non-Responsibilities

This standard MUST NOT replace the Engineering Kernel, applicable architecture, task-specific direction, repository evidence, independent review, certification, or product authority. It MUST NOT create workflows, playbooks, templates, scripts, schemas, validators, generators, hooks, CI, automation, automatic transitions, automatic session control, automatic routing, delegation, or multi-agent behavior.

## Governing Inputs

Governing inputs are `AGENTS.md`; the Engineering Kernel; the Slice Specification Standard; the Model Routing Standard; the Repository Knowledge Foundation and Index; applicable approved architecture, standards, roadmaps, certification and closeout records; current repository and Git evidence; exact checkpoints; and attributable task-specific accountable-human decisions. Contradictions MUST remain visible and MUST NOT be silently repaired.

## Outputs

Outputs are bounded state results, attributable decisions, repository observations, gate evidence, checkpoints, discrepancy records, and return packages. An output MUST identify what it does not authorize.

## Relationship to ES-1

ES-1 remains the canonical lifecycle-status vocabulary. ES-6 responsibility state is a separate statement of the exact engineering responsibility, session posture, checkpoint, and recovery context. One ES-1 status MAY correspond to multiple ES-6 responsibilities. Completion of an ES-6 responsibility MUST NOT advance ES-1, and a compatible ES-1/ES-6 pairing MUST NOT create authority. Lifecycle state, responsibility state, repository state, capability tier, session recommendation, checkpoint, approval, authorization, certification, and operational authority are separate concepts.

The following compatibility mapping is non-authorizing:

| ES-6 responsibility | Compatible ES-1 status |
| --- | --- |
| `DISCOVERY_CURRENT_STATE_ASSESSMENT`, `INTERRUPTED_WORK_RECOVERY`, `BLOCKED_DISCREPANT` | Any evidenced current status; do not change it |
| `ARCHITECTURE_PREPARATION` | `ARCHITECTURE_DRAFT` |
| `ARCHITECTURE_REVIEW`, `ARCHITECTURE_REVISION`, `ARCHITECTURE_APPROVAL` | `ARCHITECTURE_IN_REVIEW`, then `ARCHITECTURE_APPROVED` only after recorded decision |
| Architecture commit, publication, integration preparation, merge creation, integration validation, main push, cleanup | `ARCHITECTURE_APPROVED` or independently established `REPOSITORY_TRANSITION_AUTHORIZED` |
| `IMPLEMENTATION_AUTHORIZATION` | `ARCHITECTURE_APPROVED`, then `IMPLEMENTATION_AUTHORIZED` only after recorded decision |
| `IMPLEMENTATION` | `IMPLEMENTATION_AUTHORIZED` or `IMPLEMENTATION_IN_PROGRESS` |
| Implementation review, targeted revision, approval | `IMPLEMENTATION_IN_REVIEW`, then `IMPLEMENTATION_APPROVED` only after recorded decision |
| Implementation commit, publication, integration preparation, merge creation, integration validation, main push, cleanup | `IMPLEMENTATION_APPROVED` or independently established `REPOSITORY_TRANSITION_AUTHORIZED`, then `INTEGRATED` only after verified integration |
| `CERTIFICATION` | `INTEGRATED`, then `CERTIFIED` only after recorded decision |
| `OPERATIONAL_ACCEPTANCE` | Exact evidence-established current status; ES-1 has no operational-acceptance status |
| `CLOSEOUT` | `INTEGRATED` or `CERTIFIED`, then `CLOSED` only after recorded decision |
| `DEFERRED`, `ABANDONED` | Last valid status with attributable qualifier |
| `SUPERSEDED` | Last valid status, then `SUPERSEDED` only after recorded decision |

An unlisted pairing MUST enter `BLOCKED_DISCREPANT` without changing either declaration.

## Engineering Responsibility State Model

There are exactly 32 ES-6 responsibility states. The sequence is conceptual and never automatic. Completion of one responsibility never authorizes the next. Every state definition below exposes all 16 required fields separately.

### Common State Rules

Unless a state profile states a stricter rule, its authoritative inputs are the exact subject, current ES-1 status, governing artifacts, attributable authority, repository evidence, and preceding checkpoint. Entry requires current inputs, compatible pairing, exact scope, and no unresolved unsafe blocker. Repository verification requires repository and worktree paths, branch, full HEAD and baseline, relevant refs, status, subject identity, and expected-versus-actual scope. Required evidence includes authority, subject identity, observations, commands, complete results, discrepancies, and authority withheld. Gates are state-applicable gates on the exact subject; failures and incomplete gates remain explicit. Recovery begins read-only, preserves evidence, uses classes A–M, and resumes only unfinished work under current authority. Invalid transitions stop mutation, retain evidence, record the discrepancy, and enter `BLOCKED_DISCREPANT` or class M.

### Responsibility-State Definitions

#### `DISCOVERY_CURRENT_STATE_ASSESSMENT`

- **Purpose:** Establish current state for one exact subject.
- **Authoritative Inputs:** Common State Rules inputs.
- **Entry Criteria:** Common State Rules entry criteria.
- **Recommended Capability Tier:** Tier 2; Tier 3 for consequential ambiguity.
- **Recommended Session Treatment:** Fresh at authority or independence boundaries; otherwise continue only under Section Session-Orchestration Rules.
- **Authorized Actions:** Observe and assess only.
- **Prohibited Actions:** Adjacent work, inferred authority, scope change, or excluded boundaries.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Common State Rules evidence and observations.
- **Required Outputs:** Bounded assessment result and evidence package.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `discovery_current_state_assessment checkpoint`.
- **Exit Criteria:** Assessment complete or safely stopped with residual findings.
- **Accountable-Human Transition Authority:** Attributable decision for named next state and subject.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_PREPARATION`

- **Purpose:** Prepare one architecture candidate.
- **Authoritative Inputs:** Common State Rules inputs.
- **Entry Criteria:** Common State Rules entry criteria.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Fresh at an authority or independence boundary.
- **Authorized Actions:** Prepare only the authorized architecture candidate.
- **Prohibited Actions:** Review, approval, implementation, or scope expansion.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Common State Rules evidence.
- **Required Outputs:** Bounded architecture candidate.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_preparation checkpoint`.
- **Exit Criteria:** Candidate or safe stop is recorded; ES-1 does not advance.
- **Accountable-Human Transition Authority:** Attributable decision for named next state and subject.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_REVIEW`

- **Purpose:** Independently review one architecture candidate.
- **Authoritative Inputs:** Common State Rules inputs and candidate.
- **Entry Criteria:** Current, reviewable exact candidate and independent reviewer.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Fresh independent session is mandatory.
- **Authorized Actions:** Review and report findings only.
- **Prohibited Actions:** Modify or approve the subject, or combine production and review.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Findings, dispositions, and Common State Rules evidence.
- **Required Outputs:** Bounded independent review result.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_review checkpoint`.
- **Exit Criteria:** Findings and residual uncertainty are recorded.
- **Accountable-Human Transition Authority:** Attributable decision for named next state and subject.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_REVISION`

- **Purpose:** Revise an architecture only within authorized findings and scope.
- **Authoritative Inputs:** Common State Rules inputs and review findings.
- **Entry Criteria:** Exact revision scope and current authority.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Fresh revision session; reviser MUST NOT conduct renewed independent review.
- **Authorized Actions:** Targeted architecture revision.
- **Prohibited Actions:** Scope expansion, approval, or renewed independent review by reviser.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Common State Rules evidence and finding disposition.
- **Required Outputs:** Bounded revised candidate.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_revision checkpoint`.
- **Exit Criteria:** Revision and unresolved findings are recorded.
- **Accountable-Human Transition Authority:** Attributable decision for named next state and subject.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_APPROVAL`

- **Purpose:** Record accountable-human architecture decision.
- **Authoritative Inputs:** Common State Rules inputs, reviewed candidate, and decision evidence.
- **Entry Criteria:** Review evidence is current and approval authority is exact.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Fresh at an authority boundary.
- **Authorized Actions:** Record only the decision and its limits.
- **Prohibited Actions:** Implement, commit, publish, integrate, or infer later authority.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Decision identity, issuer, scope, limits, and authority withheld.
- **Required Outputs:** Attributable approval, rejection, or disposition record.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_approval_decision_recorded`.
- **Exit Criteria:** Decision is retained; implementation remains separately authorized.
- **Accountable-Human Transition Authority:** Separate attributable decision for each next state.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_COMMIT`

- **Purpose:** Create an approved architecture commit.
- **Authoritative Inputs:** Common State Rules inputs and exact approval-to-diff comparison.
- **Entry Criteria:** Exact approved subject equals candidate; commit authority is current.
- **Recommended Capability Tier:** Tier 1; escalate only for qualifying ambiguity.
- **Recommended Session Treatment:** Fresh at a repository-action boundary.
- **Authorized Actions:** Create only the authorized commit.
- **Prohibited Actions:** Publication, integration, cleanup, or content outside approval.
- **Required Repository Verification:** Common State Rules verification plus unstaged/staged diff identity.
- **Required Evidence:** Approval comparison and resulting commit identity.
- **Required Outputs:** One bounded commit observation.
- **Quality Gates:** Common State Rules gates and required final gate.
- **Safe Interruption Checkpoint:** `architecture_committed`.
- **Exit Criteria:** Commit result and remaining authority are recorded.
- **Accountable-Human Transition Authority:** Separate publication or integration-preparation authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_PUBLICATION`

- **Purpose:** Publish an exact approved architecture commit.
- **Authoritative Inputs:** Common State Rules inputs, commit, and publication authority.
- **Entry Criteria:** Local commit and intended remote target are verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh publication session.
- **Authorized Actions:** Publish only named commit and ref.
- **Prohibited Actions:** Merge, validate integration, main push, or cleanup.
- **Required Repository Verification:** Common State Rules verification and remote/ref comparison.
- **Required Evidence:** Push command, full result, remote identity, and ambiguity record.
- **Required Outputs:** Verified publication observation or discrepancy.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_feature_branch_published`.
- **Exit Criteria:** Remote state is verified; publication does not authorize integration.
- **Accountable-Human Transition Authority:** Separate integration-preparation authority.
- **Recovery Behavior:** Common State Rules recovery; ambiguous network result is M pending remote check.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_INTEGRATION_PREPARATION`

- **Purpose:** Prepare authorized architecture integration resources.
- **Authoritative Inputs:** Common State Rules inputs and integration authority.
- **Entry Criteria:** Published subject and current main are verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh isolated integration session.
- **Authorized Actions:** Prepare only bounded integration resources.
- **Prohibited Actions:** Create merge, validate, push main, or clean resources.
- **Required Repository Verification:** Common State Rules verification and ancestry/remote-main identity.
- **Required Evidence:** Preparation identities and temporary-resource inventory.
- **Required Outputs:** Prepared integration context.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_integration_resources_prepared`.
- **Exit Criteria:** Preparation evidence and withheld merge authority recorded.
- **Accountable-Human Transition Authority:** Separate merge-creation authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_MERGE_CREATION`

- **Purpose:** Create one authorized architecture merge.
- **Authoritative Inputs:** Common State Rules inputs and exact merge authority.
- **Entry Criteria:** Source, target, ancestry, and integration context are verified.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Create only the authorized merge.
- **Prohibited Actions:** Validate, push main, cleanup, or recreate an existing merge.
- **Required Repository Verification:** Common State Rules verification and parent/merge identities.
- **Required Evidence:** Merge command, parents, result, and exact merge identity.
- **Required Outputs:** Bounded merge observation.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_merge_created`.
- **Exit Criteria:** Merge identity and withheld validation authority recorded.
- **Accountable-Human Transition Authority:** Separate integration-validation authority.
- **Recovery Behavior:** Common State Rules recovery; existing merge awaiting gates is I.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_INTEGRATION_VALIDATION`

- **Purpose:** Validate the exact architecture merge.
- **Authoritative Inputs:** Common State Rules inputs and merge identity.
- **Entry Criteria:** Merge is exact and validation authority is current.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh isolated validation session.
- **Authorized Actions:** Execute and record validation only.
- **Prohibited Actions:** Recreate merge, push main, cleanup, certification, or closeout.
- **Required Repository Verification:** Common State Rules verification and exact merge/tree subject.
- **Required Evidence:** Complete gate command, arguments, environment, results, and exit statuses.
- **Required Outputs:** Validation result with failures preserved.
- **Quality Gates:** Required integration gates on exact merge.
- **Safe Interruption Checkpoint:** `architecture_integration_validation_completed`.
- **Exit Criteria:** Current validation evidence is retained; no main-push authority inferred.
- **Accountable-Human Transition Authority:** Separate main-push authority.
- **Recovery Behavior:** Common State Rules recovery; stale/partial validation is I.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_MAIN_PUSH`

- **Purpose:** Push one validated architecture merge to main.
- **Authoritative Inputs:** Common State Rules inputs, validation evidence, and main-push authority.
- **Entry Criteria:** Exact merge and current main target are verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh main-push session.
- **Authorized Actions:** Push only named merge to named main ref.
- **Prohibited Actions:** Cleanup, certification, operational acceptance, or closeout.
- **Required Repository Verification:** Common State Rules verification and remote-main identity immediately before and after.
- **Required Evidence:** Push result and verified remote main identity.
- **Required Outputs:** Verified main-push observation or ambiguity.
- **Quality Gates:** Common State Rules gates; validation remains separate.
- **Safe Interruption Checkpoint:** `architecture_main_push_verified`.
- **Exit Criteria:** Main state is verified; cleanup remains separately authorized.
- **Accountable-Human Transition Authority:** Separate cleanup or later authority.
- **Recovery Behavior:** Common State Rules recovery; ambiguous push is M until remotely verified.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ARCHITECTURE_INTEGRATION_CLEANUP`

- **Purpose:** Perform separately authorized temporary-resource cleanup.
- **Authoritative Inputs:** Common State Rules inputs, verified main push, inventory, and cleanup authority.
- **Entry Criteria:** Exact temporary targets and retained evidence are verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh cleanup session.
- **Authorized Actions:** Clean only named, non-authoritative temporary resources.
- **Prohibited Actions:** Delete authoritative evidence, alter main, certify, or close out.
- **Required Repository Verification:** Common State Rules verification and temporary-resource inventory.
- **Required Evidence:** Target proof, action results, and retained recovery references.
- **Required Outputs:** Cleanup observation with unresolved resources listed.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `architecture_integration_cleanup_completed`.
- **Exit Criteria:** Authorized cleanup disposition is recorded.
- **Accountable-Human Transition Authority:** Separate later authority.
- **Recovery Behavior:** Common State Rules recovery; partial cleanup is K.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_AUTHORIZATION`

- **Purpose:** Record accountable-human authority for named implementation.
- **Authoritative Inputs:** Common State Rules inputs and approved architecture.
- **Entry Criteria:** Architecture approval is exact; implementation scope is bounded.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Record only the implementation decision and limits.
- **Prohibited Actions:** Implement, commit, publish, integrate, or infer authority.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Decision identity, issuer, exact scope, limits, exclusions, and withheld authority.
- **Required Outputs:** Attributable authorization or refusal record.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_authorization_decision_recorded`.
- **Exit Criteria:** Decision is retained; no implementation begins absent exact authority.
- **Accountable-Human Transition Authority:** Separate decision to enter implementation.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION`

- **Purpose:** Implement only the exact authorized subject.
- **Authoritative Inputs:** Common State Rules inputs and exact implementation authorization.
- **Entry Criteria:** Architecture, scope, exclusions, and authority are current.
- **Recommended Capability Tier:** Tier 2; Tier 3 for consequential ambiguity.
- **Recommended Session Treatment:** Fresh implementation session.
- **Authorized Actions:** Create the bounded approved implementation artifact.
- **Prohibited Actions:** Review, approval, commit, publication, integration, or adjacent capability work.
- **Required Repository Verification:** Common State Rules verification and exact changed-path scope.
- **Required Evidence:** Common State Rules evidence, file inventory, and rationale for deviations.
- **Required Outputs:** Bounded implementation candidate.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_candidate_created`.
- **Exit Criteria:** Candidate, gates, scope, and unfinished work are recorded.
- **Accountable-Human Transition Authority:** Separate implementation-review authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_REVIEW`

- **Purpose:** Independently review an implementation candidate.
- **Authoritative Inputs:** Common State Rules inputs and candidate.
- **Entry Criteria:** Candidate is exact and independently reviewable.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Fresh independent session is mandatory.
- **Authorized Actions:** Review and report findings only.
- **Prohibited Actions:** Modify, approve, commit, or combine candidate production with review.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Independent findings and dispositions.
- **Required Outputs:** Bounded independent review result.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_review_completed`.
- **Exit Criteria:** Findings and residual uncertainty are recorded.
- **Accountable-Human Transition Authority:** Separate targeted-revision or approval authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `TARGETED_IMPLEMENTATION_REVISION`

- **Purpose:** Revise only authorized implementation findings.
- **Authoritative Inputs:** Common State Rules inputs and review findings.
- **Entry Criteria:** Finding scope and revision authority are exact.
- **Recommended Capability Tier:** Tier 2; Tier 3 for consequential ambiguity.
- **Recommended Session Treatment:** Fresh targeted-revision session; reviser MUST NOT perform renewed independent review.
- **Authorized Actions:** Make selected, bounded revisions.
- **Prohibited Actions:** Scope expansion, approval, or independent review by reviser.
- **Required Repository Verification:** Common State Rules verification and changed-path comparison.
- **Required Evidence:** Finding dispositions and exact revision scope.
- **Required Outputs:** Revised candidate.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `targeted_implementation_revision_completed`.
- **Exit Criteria:** Revision and outstanding findings are recorded.
- **Accountable-Human Transition Authority:** Separate renewed-review or approval authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_APPROVAL`

- **Purpose:** Record accountable-human implementation decision.
- **Authoritative Inputs:** Common State Rules inputs, review record, and candidate.
- **Entry Criteria:** Current review evidence and exact approval authority.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Record decision and limits only.
- **Prohibited Actions:** Commit, publication, integration, certification, or inferred later authority.
- **Required Repository Verification:** Common State Rules verification and approval-to-diff comparison.
- **Required Evidence:** Attributable decision, subject comparison, scope, limits, and authority withheld.
- **Required Outputs:** Approval, rejection, or disposition record.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_approval_decision_recorded`.
- **Exit Criteria:** Decision is retained; commit is separately authorized.
- **Accountable-Human Transition Authority:** Separate commit authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_COMMIT`

- **Purpose:** Create an approved implementation commit.
- **Authoritative Inputs:** Common State Rules inputs and approval-to-diff comparison.
- **Entry Criteria:** Exact approved subject equals candidate; commit authority is current.
- **Recommended Capability Tier:** Tier 1; escalate only for qualifying ambiguity.
- **Recommended Session Treatment:** Fresh repository-action session.
- **Authorized Actions:** Create only the named approved commit.
- **Prohibited Actions:** Publication, integration, or content outside approval.
- **Required Repository Verification:** Common State Rules verification and staged/unstaged identity.
- **Required Evidence:** Approval comparison and commit identity.
- **Required Outputs:** Bounded commit observation.
- **Quality Gates:** Common State Rules gates and required final gate.
- **Safe Interruption Checkpoint:** `implementation_committed`.
- **Exit Criteria:** Commit observation and withheld publication authority are recorded.
- **Accountable-Human Transition Authority:** Separate publication authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_PUBLICATION`

- **Purpose:** Publish the exact approved implementation commit.
- **Authoritative Inputs:** Common State Rules inputs, commit, and publication authority.
- **Entry Criteria:** Commit and intended remote ref are verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh publication session.
- **Authorized Actions:** Publish only named commit and ref.
- **Prohibited Actions:** Integrate, validate merge, push main, or cleanup.
- **Required Repository Verification:** Common State Rules verification and remote/ref comparison.
- **Required Evidence:** Full push result and verified remote identity.
- **Required Outputs:** Publication observation or discrepancy.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_feature_branch_published`.
- **Exit Criteria:** Remote state verified; publication does not authorize integration.
- **Accountable-Human Transition Authority:** Separate integration-preparation authority.
- **Recovery Behavior:** Common State Rules recovery; ambiguous network result is M pending remote check.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_INTEGRATION_PREPARATION`

- **Purpose:** Prepare authorized implementation integration resources.
- **Authoritative Inputs:** Common State Rules inputs and integration authority.
- **Entry Criteria:** Published subject and current main are verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh isolated integration session.
- **Authorized Actions:** Prepare only named integration context.
- **Prohibited Actions:** Merge, validate, push main, or cleanup.
- **Required Repository Verification:** Common State Rules verification and ancestry/main identity.
- **Required Evidence:** Preparation identities and temporary-resource inventory.
- **Required Outputs:** Prepared integration context.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_integration_resources_prepared`.
- **Exit Criteria:** Preparation and withheld merge authority are recorded.
- **Accountable-Human Transition Authority:** Separate merge-creation authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_MERGE_CREATION`

- **Purpose:** Create one authorized implementation merge.
- **Authoritative Inputs:** Common State Rules inputs and merge authority.
- **Entry Criteria:** Source, target, ancestry, and integration context verified.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Create only exact authorized merge.
- **Prohibited Actions:** Validate, push main, cleanup, or recreate merge.
- **Required Repository Verification:** Common State Rules verification and parent/merge identities.
- **Required Evidence:** Merge command, parents, result, and identity.
- **Required Outputs:** Bounded merge observation.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_merge_created`.
- **Exit Criteria:** Merge identity and withheld validation authority recorded.
- **Accountable-Human Transition Authority:** Separate validation authority.
- **Recovery Behavior:** Common State Rules recovery; existing merge awaiting gates is I.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_INTEGRATION_VALIDATION`

- **Purpose:** Validate exact implementation merge.
- **Authoritative Inputs:** Common State Rules inputs and merge identity.
- **Entry Criteria:** Exact merge and validation authority are current.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh isolated validation session.
- **Authorized Actions:** Execute and record validation only.
- **Prohibited Actions:** Recreate merge, push main, cleanup, certify, or closeout.
- **Required Repository Verification:** Common State Rules verification and merge/tree subject.
- **Required Evidence:** Complete gate commands, arguments, environment, results, statuses.
- **Required Outputs:** Validation result with failures preserved.
- **Quality Gates:** Required integration gates on exact merge.
- **Safe Interruption Checkpoint:** `implementation_integration_validation_completed`.
- **Exit Criteria:** Current validation retained; no push authority inferred.
- **Accountable-Human Transition Authority:** Separate main-push authority.
- **Recovery Behavior:** Common State Rules recovery; stale/partial validation is I.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_MAIN_PUSH`

- **Purpose:** Push one validated implementation merge to main.
- **Authoritative Inputs:** Common State Rules inputs, validation, and main-push authority.
- **Entry Criteria:** Exact merge and current remote main verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh main-push session.
- **Authorized Actions:** Push only named merge to named main ref.
- **Prohibited Actions:** Cleanup, certification, operational acceptance, or closeout.
- **Required Repository Verification:** Common State Rules verification and remote identity before/after.
- **Required Evidence:** Push result and remote-main verification.
- **Required Outputs:** Verified push observation or ambiguity.
- **Quality Gates:** Common State Rules gates; validation remains separate.
- **Safe Interruption Checkpoint:** `implementation_main_push_verified`.
- **Exit Criteria:** Main state verified; cleanup separately authorized.
- **Accountable-Human Transition Authority:** Separate cleanup or later authority.
- **Recovery Behavior:** Common State Rules recovery; ambiguous push is M pending remote verification.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `IMPLEMENTATION_INTEGRATION_CLEANUP`

- **Purpose:** Perform separately authorized temporary integration cleanup.
- **Authoritative Inputs:** Common State Rules inputs, verified main, inventory, cleanup authority.
- **Entry Criteria:** Exact non-authoritative targets and retained evidence verified.
- **Recommended Capability Tier:** Tier 1.
- **Recommended Session Treatment:** Fresh cleanup session.
- **Authorized Actions:** Clean named temporary resources only.
- **Prohibited Actions:** Delete authoritative evidence, alter main, certify, or close out.
- **Required Repository Verification:** Common State Rules verification and resource inventory.
- **Required Evidence:** Target proof, results, retained recovery references.
- **Required Outputs:** Cleanup observation and unresolved-resource list.
- **Quality Gates:** Common State Rules gates.
- **Safe Interruption Checkpoint:** `implementation_integration_cleanup_completed`.
- **Exit Criteria:** Authorized cleanup disposition recorded.
- **Accountable-Human Transition Authority:** Separate later authority.
- **Recovery Behavior:** Common State Rules recovery; partial cleanup is K.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `CERTIFICATION`

- **Purpose:** Record bounded certification evaluation and decision.
- **Authoritative Inputs:** Common State Rules inputs, integrated subject, and certification authority.
- **Entry Criteria:** Integration identity and certification criteria verified.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Fresh certification session.
- **Authorized Actions:** Evaluate and record certification decision only.
- **Prohibited Actions:** Operational acceptance, closeout, product operations, or inferred authority.
- **Required Repository Verification:** Common State Rules verification and integrated identity.
- **Required Evidence:** Certification criteria, evidence, decision identity, and exceptions.
- **Required Outputs:** Certification decision or discrepancy.
- **Quality Gates:** Required certification gates on exact subject.
- **Safe Interruption Checkpoint:** `certification_decision_recorded`.
- **Exit Criteria:** Decision retained; operational acceptance remains separate.
- **Accountable-Human Transition Authority:** Separate operational-acceptance or closeout authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `OPERATIONAL_ACCEPTANCE`

- **Purpose:** Record bounded operational-acceptance decision.
- **Authoritative Inputs:** Common State Rules inputs and applicable operational evidence.
- **Entry Criteria:** Exact operational subject and authority are established.
- **Recommended Capability Tier:** Tier 3.
- **Recommended Session Treatment:** Fresh operational-acceptance session.
- **Authorized Actions:** Evaluate and record acceptance only.
- **Prohibited Actions:** Certification substitution, closeout, product operation, or authority transfer.
- **Required Repository Verification:** Common State Rules verification as applicable.
- **Required Evidence:** Operational criteria, decision identity, scope, limits, and withheld authority.
- **Required Outputs:** Operational-acceptance decision or discrepancy.
- **Quality Gates:** Applicable gates on exact subject.
- **Safe Interruption Checkpoint:** `operational_acceptance_decision_recorded`.
- **Exit Criteria:** Decision retained; closeout remains separate.
- **Accountable-Human Transition Authority:** Separate closeout authority.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `CLOSEOUT`

- **Purpose:** Record bounded closeout decision.
- **Authoritative Inputs:** Common State Rules inputs and required predecessor evidence.
- **Entry Criteria:** Exact closeout scope and authority verified.
- **Recommended Capability Tier:** Tier 2; Tier 3 for consequential ambiguity.
- **Recommended Session Treatment:** Fresh closeout session.
- **Authorized Actions:** Reconcile and record closeout only.
- **Prohibited Actions:** Cleanup, deletion, product acceptance, or authority inference.
- **Required Repository Verification:** Common State Rules verification and retained evidence inventory.
- **Required Evidence:** Reconciliation, decision identity, residual obligations, authority withheld.
- **Required Outputs:** Closeout decision or discrepancy.
- **Quality Gates:** Required closeout gates on exact subject.
- **Safe Interruption Checkpoint:** `closeout_decision_recorded`.
- **Exit Criteria:** Decision retained; no operational authority implied.
- **Accountable-Human Transition Authority:** Separate authority for any later subject.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `INTERRUPTED_WORK_RECOVERY`

- **Purpose:** Recover an interrupted exact responsibility without blind replay.
- **Authoritative Inputs:** Common State Rules inputs, checkpoint, and observed repository state.
- **Entry Criteria:** Interruption or unreliable session state is evidenced.
- **Recommended Capability Tier:** Tier 2; Tier 3 for ambiguity or consequence.
- **Recommended Session Treatment:** Fresh recovery session.
- **Authorized Actions:** Read-only verification, preservation, classification, and authorized resumption preparation.
- **Prohibited Actions:** Blind replay, duplicate mutation, inferred transition, or cleanup.
- **Required Repository Verification:** Common State Rules verification and remote verification before retrying ambiguous mutation.
- **Required Evidence:** Checkpoint comparison, recovery class, unknowns, and valid work preserved.
- **Required Outputs:** Recovery disposition and bounded next recommendation.
- **Quality Gates:** Verify currentness of applicable prior gates.
- **Safe Interruption Checkpoint:** `interrupted_work_recovery checkpoint`.
- **Exit Criteria:** Class and safe stop or authorized resumable work recorded.
- **Accountable-Human Transition Authority:** Separate authority for any resumed responsibility.
- **Recovery Behavior:** Begin read-only and apply Section Interrupted-Work Recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `BLOCKED_DISCREPANT`

- **Purpose:** Preserve and expose a blocker, incompatibility, or contradiction.
- **Authoritative Inputs:** Common State Rules inputs and discrepancy evidence.
- **Entry Criteria:** Exact state cannot be safely proven or a blocker exists.
- **Recommended Capability Tier:** Tier 2 for bounded diagnosis; Tier 3 for contradictory governance, authority, ancestry, or high-consequence ambiguity; Tier 1 only for prescribed read-only verification.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Observe, preserve, classify, and request direction.
- **Prohibited Actions:** Mutation, normalization, authority inference, or silent repair.
- **Required Repository Verification:** Common State Rules verification and contradictory-evidence comparison.
- **Required Evidence:** Full discrepancy, failed assumptions, and authority withheld.
- **Required Outputs:** Blocked/discrepant record and safe-stop package.
- **Quality Gates:** Record applicable failed, partial, or stale gates.
- **Safe Interruption Checkpoint:** `blocked_discrepant checkpoint`.
- **Exit Criteria:** Discrepancy is retained; resolution requires separate authority.
- **Accountable-Human Transition Authority:** Attributable resolution decision for named state and subject.
- **Recovery Behavior:** Class M unless a narrower proven class applies.
- **Invalid-Transition Behavior:** Stop and retain evidence.

#### `DEFERRED`

- **Purpose:** Record an attributable bounded deferral.
- **Authoritative Inputs:** Common State Rules inputs and deferral decision.
- **Entry Criteria:** Deferral scope, reason, and authority are exact.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Preserve and record deferral only.
- **Prohibited Actions:** Treat deferral as completion, abandonment, supersession, or later authority.
- **Required Repository Verification:** Common State Rules verification.
- **Required Evidence:** Decision identity, reason, retained state, and next consideration.
- **Required Outputs:** Deferred disposition record.
- **Quality Gates:** Record current gate state without implying completion.
- **Safe Interruption Checkpoint:** `deferred checkpoint`.
- **Exit Criteria:** Deferral is attributable and recovery-ready.
- **Accountable-Human Transition Authority:** Separate authority to resume or enter another state.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `ABANDONED`

- **Purpose:** Record attributable abandonment of a subject or session.
- **Authoritative Inputs:** Common State Rules inputs and abandonment decision.
- **Entry Criteria:** Scope, retained evidence, and authority are exact.
- **Recommended Capability Tier:** Tier 2; Tier 3 for consequential ambiguity.
- **Recommended Session Treatment:** End after safe stop and checkpoint.
- **Authorized Actions:** Preserve work and record abandonment only.
- **Prohibited Actions:** Delete evidence, infer supersession, or treat as completion.
- **Required Repository Verification:** Common State Rules verification and retained-resource inventory.
- **Required Evidence:** Decision, rationale, unfinished work, effects, and authority withheld.
- **Required Outputs:** Abandonment disposition record.
- **Quality Gates:** Record applicable gate state.
- **Safe Interruption Checkpoint:** `abandonment_decision_recorded`.
- **Exit Criteria:** Work is preserved and abandonment is distinct from supersession.
- **Accountable-Human Transition Authority:** Separate authority for any successor or resumption.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

#### `SUPERSEDED`

- **Purpose:** Record attributable replacement by one exact successor subject.
- **Authoritative Inputs:** Common State Rules inputs, supersession decision, and successor identity.
- **Entry Criteria:** Predecessor, successor, rationale, and authority are exact.
- **Recommended Capability Tier:** Tier 2, escalating to Tier 3 under ES-5 when consequence or ambiguity requires it.
- **Recommended Session Treatment:** Begin fresh at an authority or independence boundary; continue only with unchanged subject, scope, authority, and reliable context.
- **Authorized Actions:** Record supersession lineage only.
- **Prohibited Actions:** Delete predecessor evidence, infer successor authority, or treat as abandonment.
- **Required Repository Verification:** Common State Rules verification and predecessor/successor identity comparison.
- **Required Evidence:** Decision identity, lineage, rationale, retained evidence, and withheld authority.
- **Required Outputs:** Supersession disposition record.
- **Quality Gates:** Record applicable gate state.
- **Safe Interruption Checkpoint:** `supersession_decision_recorded`.
- **Exit Criteria:** Supersession is attributable and predecessor evidence remains retained.
- **Accountable-Human Transition Authority:** Separate authority for successor work.
- **Recovery Behavior:** Common State Rules recovery.
- **Invalid-Transition Behavior:** Common State Rules invalid-transition behavior.

## Entry and Exit Criteria

Entry to every state MUST establish exact subject, ES-1 status, ES-6 state, authorized responsibility and issuer, repository/worktree/branch/full HEAD/baseline/relevant refs, governing architecture and decisions, inclusions/exclusions/paths/outputs, current authority limited to that state, and absence of an unsafe blocker. Exit MUST retain state outputs, gates, checkpoint, exact changed scope, residual failures and discrepancies, and a safe-stop repository state. Exit never authorizes another state.

## Authority Transitions

Transitions MUST be explicit, attributable, bounded, independently verifiable, and non-transitive. Architecture approval precedes implementation authorization; implementation review precedes implementation approval and commit; explicit approval precedes every commit; commit is separate from publication; publication is separate from integration; merge creation is separate from validation; validation is separate from main push; main push is separate from temporary-resource cleanup; certification is separate from operational acceptance; operational acceptance is separate from closeout; and abandonment is separate from supersession. Passing tests never authorizes commit, publication, integration, certification, closeout, migration, cleanup, deletion, or destructive work. Product authority and Engineering System authority MUST NOT transfer.

## Session-Orchestration Rules

Session treatment is advisory and human-controlled. A fresh session is the default for architecture preparation, implementation after approval, independent review, targeted revision, commit and publication, isolated main integration, certification or operational acceptance, closeout, and recovery where prior state is unreliable. Continuation is acceptable only when responsibility, exact authority, exact scope, repository state, and focused context remain current; no unrelated work entered; and independence is uncompromised. Checkpoint before long operations, compaction, interruption risk, authority boundary, tier change, session end, or handoff. End at a completed responsibility, material boundary, safe stop, blocker, deferral, abandonment, or contamination. Resume only from verified repository and checkpoint evidence. Abandon unreliable, mixed, stale, or incompatibly advanced session context while preserving valid work; start recovery rather than blindly restarting. A tier change and session change are independent: a new session MAY retain tier, and a focused session MAY change tier after checkpointing. No rule creates, ends, resumes, or switches a session automatically.

## Capability-Tier Relationship

ES-6 consumes, and MUST NOT redefine, ES-5 tiers: Tier 1 Procedural Execution for exact verification and prescribed repository steps; Tier 2 Engineering Implementation for bounded implementation, routine recovery, targeted revision, and ordinary closeout analysis; Tier 3 Architecture and Adjudication for architecture, high-consequence review, contradictory authority, novel design, certification, and ambiguous recovery. The least costly sufficient available tier SHOULD be recommended after correctness and consequence. A tier never changes scope, quality, evidence, or authority; accountable humans MAY override recommendations within governing rules.

## Checkpoint Standard

A checkpoint is durable human-readable evidence sufficient for a fresh session. Every checkpoint MUST identify or cite stable name; exact subject; ES-1 status; ES-6 state; repository and worktree identity; branch, full HEAD, baseline, relevant remotes, status, commit/tree/diff/observation identity as applicable; exact scope; governing architecture and authority; completed responsibility; outputs; gate commands, arguments, subjects, results, failures, and statuses; external effects; temporary resources; discrepancies and blockers; authority withheld; unfinished responsibility; recommended next responsibility without authorization implication; payload location or retained evidence reference; and decision identity for approval or disposition. A name alone never proves completion or authority.

## Interrupted-Work Recovery

Recovery MUST begin read-only, preserve valid work, avoid blind replay and duplicate content/commits/merges/pushes/cleanup, and verify remote state before retrying ambiguous mutation. It MUST distinguish network, DNS, transport, permission, sandbox, environment, dependency, capability, repository, and authority failures. Memory and conversation history are non-authoritative orientation.

Every recovery assessment MUST assign exactly one top-level recovery class from A through M; mandatory bounded substates refine that class but do not create a second top-level class; where exact classification cannot be proven, Class M takes precedence.

| Class | Condition | Required treatment |
| --- | --- | --- |
| A | No governed work began | Verify current subject, repository, authority, and entry criteria before beginning the authorized responsibility. |
| B | Branch exists but deliverable does not | Verify branch base, branch identity, exact scope, repository state, and current authority before creating the deliverable. |
| C | Partial deliverable | Preserve valid content; identify incomplete work. |
| D | Complete unreviewed deliverable | Verify scope and gates; proceed only to authorized review. |
| E | Reviewed deliverable awaiting revision | Verify findings; revise only selected authorized findings. |
| F | Approved deliverable awaiting commit | Compare approval to current diff; commit only with authority. |
| G | Committed branch awaiting publication | Verify commit and remote; publish only with authority. |
| H | Published branch awaiting integration | Verify remote commit and current main; integrate only with authority. |
| I | Merge awaiting complete current validation | Verify merge identity; complete gates without recreating merge. |
| J | Validated merge awaiting main push | Verify remote target; push only with authority. |
| K | Main push verified awaiting cleanup | Verify retained references; cleanup only with authority. |
| L | Repository advanced independently | Compare ancestry and scope; preserve work pending authorized reconciliation. |
| M | Unexpected, contradictory, ambiguous, or inexact state | Preserve all, record discrepancy, stop for direction. |

Mandatory bounded substates: staged uncommitted candidates use C, D, E, or F according to completion/review/approval evidence; a commit different from approved content is M; ambiguous push output or network failure after possible mutation is M until remote verification establishes G, J, or K; partial gates or validation stale through content, dependency, configuration, platform, or environment change are I; removed temporary worktree with branch retained, removed temporary branch with reachable merge, and partial cleanup are K; repository path or worktree mismatch is M when the expected repository, worktree, branch, subject, or path identity cannot be proven, and evidence MUST be preserved with a stop before mutation without silently redirecting work to another repository or worktree; unrelated active worktrees are L when the unrelated worktree is known, isolated, and does not conflict with the governed subject, but M when isolation, ancestry, scope, or noninterference cannot be proven, and they MUST NOT be modified, cleaned, stashed, switched, or repurposed; and unresolved authority, identity, or checkpoint contradiction, or inability to establish exact state, takes precedence as M.

## Safe-Stop Rules

A safe stop MUST cease mutation before an unapproved boundary; preserve valid work without destructive cleanup; capture repository, worktree, authority, and checkpoint evidence; identify completed, incomplete, and uncertain responsibilities; retain diagnostics; inventory temporary resources and external effects; state held and withheld authority; and assign a recovery class or explain M. A clean worktree is not required when cleaning would discard evidence or exceed authority.

## Failure and Discrepancy Handling

Dirty or unexpected state, stale refs, ancestry conflict, missing architecture/authority/checkpoint, failed/partial/stale gates, and network, DNS, transport, sandbox, permission, dependency, platform, environment, capability, repository, or authority failure MUST remain explicit. Failed gates remain failed until a permitted successful rerun on the exact subject or a permitted waiver. Capability escalation cannot cure missing authority. Contradictory evidence and invalid checkpoints require `BLOCKED_DISCREPANT` and M.

## Repository Verification

Before mutation and at material boundaries, verify repository and worktree path, branch, full HEAD, baseline, upstream and relevant remote refs, status including staged/modified/untracked scope, exact subject identity, applicable paths, expected versus actual diff, ancestry, and remote state before retrying ambiguous remote mutation. A summary MUST cite rather than replace observations.

## Evidence Requirements

Evidence MUST be attributable, exact, current for its claimed boundary, retained, and independently verifiable. It includes governing artifacts and decisions, repository identities, diffs and file inventories, review findings/dispositions, gate subjects/results, checkpoints, failures, discrepancies, and observable publication/integration results.

## Quality-Gate Model

Each responsibility MUST name applicable gates, exact subjects, freshness, and reuse conditions. Focused gates MAY precede expensive full gates; required final gates remain mandatory. Gate success never approves, authorizes, commits, publishes, merges, pushes, certifies, accepts operationally, closes out, migrates, cleans up, deletes, or performs destructive work.

## Gate-Evidence Reuse

Prior successful gate evidence MAY be reused only after an explicit retained comparison of prior and current subjects verifies every predicate: identical governed subject; identical content, commit, tree, or diff; exact command and arguments retained; complete result and exit status retained; applicable tool versions; no material dependency drift; no material configuration drift; applicable platform and environment assumptions; no relevant repository-state change; no affected file change; explicit governing permission; and no required final gate omitted. Reuse is evidence only and never authority.

## Reusable Workflow Compatibility

A separately authorized future ES-3 workflow MAY reference this standard’s entry/exit criteria, stop conditions, checkpoint names and payloads, session recommendations, ES-5 tier recommendations, repository verification, evidence expectations, gates, return packages, and recovery classes. It MUST NOT replace governing architecture, broaden scope, automate human decision or transition, infer lifecycle progress, bypass Git verification, weaken evidence/review/final gates, combine unrelated responsibilities, create automatic model switching, or treat checkpoint completion as approval.

## Context and Prompt Economics

Context economy MAY use verified Repository Knowledge, immutable identities, exact paths, governed summaries, retained failure detail, stable semantics, fresh boundary sessions, and compact checkpoint references. It MUST NOT omit current verification, weaken gates, hide uncertainty, use stale evidence, or infer authority. Efficiency measures require escaped-defect evidence, independent-review completion, final-gate completion, stale-evidence prevention, authority-preservation evidence, and exact-scope conformance; no measure may reward omitted review, stale evidence, weakened gates, mixed states, unauthorized transitions, or reduced rigor for quota or prompt length.

## Human Direction

Human Direction is ordinary selection among permitted choices, including tier or session treatment. It does not authorize a responsibility transition.

## Transition Authorization

Transition Authorization is explicit accountable-human authority to enter one named responsibility state for one exact subject. It MUST name issuer, evidence, scope, effect, limits, and authority withheld.

## Override

An Override is an accountable-human selection different from a default recommendation while remaining within governing rules. It MUST NOT expand scope or create waiver authority.

## Waiver or Exception

A Waiver or Exception is a bounded departure from a normally required rule only where a higher governing artifact permits it. It MUST name the exact rule, subject, rationale, limits, duration, risk, and retained evidence. Direction, override, and waiver MUST NOT manufacture evidence, violate constitutional invariants, broaden scope, authorize a different subject, transfer product/Engineering System authority, or infer authority from model output, checkpoint completion, test success, or mutation.

## Compact Prompt Minimums

Every compact lifecycle prompt or continuation request MUST directly provide, or exactly reference a checkpoint providing: exact subject; current ES-1 status; current ES-6 responsibility; exact authority; repository and worktree context; checkpoint identity; authorized next responsibility; and explicit exclusions or authority withheld. Prompt reduction MUST NOT remove these identifiers or weaken current-state verification.

## Invariants

Every active effort has one canonical ES-1 status and one compatible ES-6 state; every responsibility has exact subject, authority, and repository context; architecture precedes implementation; evidence/evaluation never grants authority; completion/gates never authorize another responsibility or ES-1 status; transitions are explicit and non-transitive; independent review is separate from production/revision; conversation is not authority; unknown state remains visible; recovery preserves valid work; and cleanup, destructive acts, migration, redirection, and operations remain separately bounded.

## Exclusions

This standard excludes executable workflow implementation, playbooks, templates, scripts, state machines, schemas, validators, generators, scaffolding, hooks, CI, automation, automatic session control, model routing, delegation, multi-agent behavior, product runtime changes, and unauthorized repository, certification, operational, migration, redirection, cleanup, destructive, or preservation-release action.

## Deferred Responsibilities

Reusable human-directed workflows, ES-3 workflow work, ES-4 validation, ES-7, ES-9, tooling, automation, lifecycle persistence, model routing, delegation, metrics platforms, and all product work require separate approved architecture and accountable-human authorization.

## Acceptance Criteria

Conformance requires ES-1 to remain canonical; exactly 32 atomic ES-6 states; all 16 fields per state; separate architecture approval and implementation authorization; separate implementation approval and commit; separate publication, integration, merge creation, validation, main push, cleanup, certification, operational acceptance, and closeout; independent fresh renewed review; immutable subject-specific checkpoints; A–M recovery with bounded substates and M precedence; every reuse predicate; distinct governance concepts; compact-prompt minimums; explicit verification/evidence/safe stops/failures; and no implementation beyond this documentation-only standard.

## Quality Gates

For a standard implementation, run the applicable repository quality gates against the exact candidate, preserve complete commands/results/exit statuses, inspect exact changed scope, and record any failure, partial result, stale evidence, or unavailable environment. Passing gates do not create human authority.

## Success Measures

Low-overhead evidence MAY observe shorter continuation prompts, fewer repeated reconstructions and blind restarts, fewer mixed responsibilities, reduced unnecessary Tier 3 use without capability-quality loss, successful named-checkpoint recovery, fewer repository conflicts, explicitly permitted valid gate reuse, and throughput per usage allocation. These measures are valid only alongside the safeguards in Context and Prompt Economics; no automated collection, target manipulation, or quality-evidence waiver is implied.

## Relationship to ES-3, ES-4, ES-5, and ES-9

ES-3 may later reference this standard but is not created here. ES-4 remains machine-checkable architecture validation; this standard defines no schema, validator, or executable model. ES-5 remains canonical for tier/model semantics; ES-6 consumes its advisory tiers and creates no automatic routing. ES-9 remains multi-agent readiness; this standard creates no delegation, orchestration, voting, shared state, or multi-agent capability. ES-6 does not authorize preparation, implementation, approval, or operation of any of them.

## ES-7 lifecycle-evidence discoverability

The subordinate `docs/engineering-system/standards/Lifecycle-Evidence-Retention-and-Identity-Standard.md` defines deterministic evidence records for occurrences of these responsibilities and their retention and deletion lineage. It does not modify any responsibility token, ordering, field, entry or exit criterion, transition, recovery class, or authority boundary in this standard. Evidence conformance never establishes that a responsibility occurred truthfully or authorizes entry to another state.

## Conformance Statement

An artifact conforms only when it applies this standard as documentation-only, preserves every stated separation and invariant, uses current attributable evidence, and obtains separate accountable-human authority for every responsibility and external action. Conformance neither grants nor implies any authority.
