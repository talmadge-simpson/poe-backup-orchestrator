# POE Storage Architecture Intent — Phase 6B Closeout and Certification

**Document ID:** POE-STOR-PHASE-6B-CERT
**Status:** Proposed for architectural review
**Phase:** 6B — Preservation Baseline Acceptance
**Responsibility:** Phase-level closeout and certification
**Certified predecessor candidate:** `main` at `1fbf4355a4ad1783fda988c26122715941c50eb0`
**Predecessor quality baseline:** Ruff passing; 889 tests passing
**Implementation and certification execution authorization:** Not granted by this document

---

## 1. Purpose

This document defines the procedure for certifying and formally closing the
implemented Phase 6B preservation-baseline acceptance subsystem.

Phase 6B is functionally complete for its later-approved scope. Certification
must now establish that the implemented software governance boundary conforms
to its approved architecture, behaves correctly through one controlled
end-to-end synthetic scenario, preserves every authority boundary, and is fit
to become the certified predecessor for later architecture discovery.

This document does not certify Phase 6B, authorize execution of the controlled
procedure, create a certification record, begin Phase 6C, or introduce new
production capability.

---

## 2. Document Status and Approval Posture

This document is proposed for architectural review only.

Approval of this architecture may authorize preparation and review of the
controlled certification procedure and the draft certification record only
when paired with separate explicit execution authorization.

Certification execution, evidence capture, certification-result approval,
commit, push, merge, formal closeout, and Phase 6C initiation each remain
subject to their applicable human approval boundary.

No `PASS`, certified, closed, or Phase 6C-ready posture may be claimed from
this architecture document alone.

---

## 3. Certification Identifier and Naming Rationale

The durable certification identifier is:

```text
POE-STOR-PHASE-6B-CERT
```

Certification is a phase-level governance responsibility, not another numeric
implementation slice.

The identifiers `6B-7`, `6B-8`, and `6B-9` must not be used for this work:

- `6B-7` is already the historical Validation Finding Generation slice;
- `6B-8` is already the historical Validation Result Assembly slice; and
- `6B-9` would falsely imply a clean numeric sequence and obscure the earlier
  collision.

The parent architecture's proposed `6B-7 — Phase 6B Certification` identifier
is obsolete because implementation history assigned `6B-7` before phase
certification began. The certification responsibility remains valid and is
fulfilled by `POE-STOR-PHASE-6B-CERT` without renumbering or rewriting history.

---

## 4. Architectural Context

The implemented governance pipeline is:

```text
Discovery
→ Inventory Assembly
→ Inventory Evidence
→ Source Content Capture
→ Content Integrity Evidence
→ Baseline Candidate Formation
→ Technical Validation
→ Acceptance Evaluation
→ Human Authorization
→ Authorization Persistence
→ Independent Persisted-Authorization Verification
→ Accepted-Baseline Construction
→ Accepted-Baseline Publication
→ Accepted-Baseline Reference Publication
→ Independent Downstream Reference Verification
```

The Phase 6B boundary converts immutable Phase 6A evidence into an explicitly
authorized, immutable, independently verifiable analytical input. It grants no
migration, supersession-execution, redirection, cleanup, or destructive
authority.

Certification must evaluate the repository as implemented and merged at the
certified software baseline commit. The candidate certified software baseline
for this effort is:

```text
1fbf4355a4ad1783fda988c26122715941c50eb0
```

Architecture documents, implementation, tests, package exports, and Git
history are evidence. Later approved slice decisions govern where they
intentionally refine earlier proposals.

---

## 5. Functional-Completeness Determination

Phase 6B is functionally complete for its later-approved
preservation-baseline acceptance scope.

The repository implements:

- deterministic baseline-candidate composition;
- technical evidence loading, verification, deserialization, fact extraction,
  reconciliation, finding generation, and result assembly;
- deterministic acceptance-policy evaluation;
- explicit accountable human authorization;
- immutable canonical authorization persistence;
- independent persisted-authorization reload and verification;
- deterministic one-to-one accepted-baseline construction;
- full accepted-baseline and authoritative-reference publication;
- independent loading initiated from the reference;
- SHA-256 sidecars, restrictive permissions, locking, replay, immutable
  conflicts, lineage, retention obligations, supersession eligibility, and
  negative authority controls.

Functional completeness is not formal certification. Phase 6B remains open
until the controlled procedure, quality gates, evidence review, certification
record, explicit human approval, and final integration are complete.

---

## 6. Certification Responsibility

Certification shall prove the Phase 6B software governance boundary.

It shall determine whether the implemented contracts and services:

1. conform to approved architecture;
2. compose without bypassing predecessor evidence;
3. preserve exact identity and lineage;
4. keep analytical, evaluative, human, persistence, publication, and downstream
   authorities distinct;
5. create independently verifiable immutable evidence;
6. behave deterministically under first publication and exact replay;
7. fail closed under incomplete or contradictory publication state;
8. preserve rejection as evidence without publishing an accepted baseline;
9. preserve retention and supersession-eligibility evidence without granting
   later authority; and
10. remain free of source mutation and destructive capability.

Certification shall not assert that a real production preservation baseline
exists, has passed representative restore testing, is operationally ready, or
satisfies later migration-closeout requirements.

---

## 7. Included Scope

Certification includes:

- repository, architecture, implementation, test, export, and Git-history
  inspection;
- objective-to-implementation and objective-to-test traceability;
- the full repository quality gate;
- one controlled end-to-end synthetic public-contract scenario;
- isolated filesystem artifact creation and verification;
- authorization persistence and independent verification;
- accepted-baseline construction and publication;
- authoritative reference publication and downstream loading;
- first-publication and sequential exact-replay evidence;
- SHA-256 and sidecar verification;
- restrictive-permission evidence;
- controlled incomplete-state failure evidence;
- controlled rejection-without-publication evidence;
- negative-authority inspection;
- approved-deferral and residual-risk review;
- preparation of the final certification record; and
- a formal human closeout decision after all evidence exists.

---

## 8. Explicit Exclusions

Certification excludes:

- production or authoritative source data;
- live preservation evidence;
- production NAS paths;
- content classification;
- sensitivity or governance classification;
- retention-policy assignment for target placement;
- target storage design or NAS destination mapping;
- duplicate analysis or disposition;
- migration-unit or wave planning;
- preservation or migration execution;
- NAS consolidation;
- supersession records, comparison, or execution;
- client redirection;
- cleanup authorization or execution;
- retention release;
- deletion, deduplication, renaming, restructuring, relocation, replacement, or
  modification of source content;
- CLI, bootstrap, configuration, authentication, digital signatures,
  notifications, identity-provider, or external-integration work;
- permanent production, model, service, export, test, or harness additions;
- Phase 6 operational readiness claims; and
- Phase 6C architecture or implementation.

No excluded capability may enter certification because it would make evidence
collection more convenient.

---

## 9. Approved Deferrals

The following are explicit, nonblocking deferrals:

- supersession-scope comparison;
- supersession authorization, records, and execution;
- production-baseline capture and acceptance;
- representative restore testing for a real accepted baseline;
- classification and destination design;
- duplicate analysis and migration planning;
- migration, redirection, cleanup, and final Phase 6 certification;
- cryptographic signatures and authenticated authority identity; and
- recurring or deployed operational certification automation.

Certification must prove that `supersession_eligible` is preserved through
authorization, accepted-baseline construction, serialization, publication,
reference verification, and downstream loading. It must also prove that no
supersession record or execution authority exists.

Deferral of supersession execution is an approved later architectural
refinement and is not a Phase 6B certification blocker.

---

## 10. Certification Inputs

Required inputs are:

- `AGENTS.md`;
- the preservation-baseline governance standard;
- the Phase 6 roadmap and parent architecture;
- the Phase 6B parent architecture;
- all Phase 6A and Phase 6B slice documents;
- current Phase 6B models, services, tests, and package exports;
- Phase 4 and Phase 5 certification and closeout precedents;
- relevant Phase 6B Git history;
- the exact certified software baseline commit and its synchronized
  `origin/main` state;
- the full test suite, currently 889 tests at the predecessor baseline;
- a separately reviewed temporary certification harness; and
- synthetic evidence created solely for the controlled procedure.

The current 889-test suite is a required certification input. Passing it is not
by itself sufficient certification evidence.

### 10.1 Git identity separation

Certification evidence must distinguish four Git identities:

1. **Certified software baseline commit** — the unchanged Phase 6B functional
   implementation whose exact software bytes are exercised by the controlled
   certification procedure. The candidate for this effort is
   `1fbf4355a4ad1783fda988c26122715941c50eb0`.
2. **Certification package commit** — the later commit containing the approved
   certification architecture and completed certification record.
3. **Certification merge commit** — the merge commit integrating the approved
   certification package into `main`.
4. **Final `origin/main` commit** — the synchronized remote-main state after
   certification-package integration and completion of the authorized
   integration workflow.

The controlled certification procedure executes against the certified
software baseline commit. Certification documentation may be prepared in a
separate worktree state, but it must import and exercise software bytes
attributable to that exact baseline rather than uncommitted or later-modified
production code.

The certification package commit does not become the software implementation
baseline merely because it records the evidence. Documentation commits, merge
commits, and synchronized remote state must never be substituted for the exact
functional bytes that were tested.

The final certification record must provide separate, clearly labeled fields
for all four applicable commit hashes. A hash not yet available while the
record remains in review must be marked `PENDING` rather than guessed or
conflated with another identity. Integration review must capture the package,
merge, and final remote identities as they become available under the
authorized workflow.

Certification evidence, artifact digests, harness results, quality-gate
outputs, and traceability conclusions must remain attributable to the exact
certified software baseline bytes. Any production-code change after the
controlled run invalidates that attribution and requires a new controlled run
against a newly approved software baseline.

---

## 11. Certified Implementation Inventory

The certification record must inventory the implemented responsibilities and
their authoritative modules.

At minimum, it shall identify:

- candidate models and composition service;
- evidence loader, deserializer, adapters, fact extraction, reconciliation,
  finding generation, and validation-result assembly;
- acceptance recommendation models and evaluator;
- human-authorization models and assembler;
- authorization-persistence artifact/result models, serializer, and store;
- accepted-baseline identity, baseline, reference, artifact, and publication
  result models;
- accepted-baseline constructor, serializer, publisher, private authorization
  verification, and downstream reference loader;
- package exports; and
- focused tests for every stage and authority boundary.

Inventory establishes what is certified. It must not infer capabilities from
documents when no implementation or evidence exists.

---

## 12. Certification Evidence Classes

Certification evidence shall remain separated into four classes.

### 12.1 Unit and component evidence

Existing focused and regression tests prove individual model invariants,
service behavior, failure handling, durability calls, replay, conflicts,
lineage, and negative boundaries.

### 12.2 Controlled certification-procedure evidence

The temporary harness proves one composed public-contract chain on a real but
isolated temporary filesystem using synthetic evidence only.

### 12.3 Architectural conformance evidence

The traceability matrix, dependency inspection, export inspection, worktree
scope, Git history, discrepancy register, deferral register, and negative
authority review establish conformance to the approved scope.

### 12.4 Human certification approval

An accountable human reviews the prior three evidence classes and explicitly
approves or rejects the formal certification result and Phase 6B closeout.

No evidence class substitutes for another. Automated success cannot create the
human certification decision.

---

## 13. Controlled Certification Procedure

The controlled procedure shall:

1. verify the certified software baseline commit, branch, `origin/main`, and
   clean worktree state, and record it separately from certification-package
   identities;
2. record Python, platform, and filesystem context;
3. present the complete exact temporary harness source and exact bytes for human
   review before execution;
4. create one isolated temporary root using the operating system's secure
   temporary-directory mechanism;
5. generate synthetic Phase 6A evidence and SHA-256 sidecars beneath that root;
6. exercise the public Phase 6B chain defined in Section 16;
7. capture identities, filenames, byte counts, digests, sidecars, permissions,
   replay state, and downstream verification results;
8. create controlled incomplete publication state beneath a separate synthetic
   directory and prove fail-closed behavior;
9. create a controlled rejected authorization and prove publication absence;
10. prove the synthetic source inputs remain byte-for-byte unchanged;
11. prove no later-authority artifact or action occurred;
12. calculate and record the exact harness SHA-256 and byte count, preserve the
    exact executed source in the certification record, and then remove the
    temporary executable harness and synthetic temporary root after evidence
    capture;
13. verify the final committed-worktree scope contains no harness or synthetic
    artifacts;
14. run the full quality gates; and
15. prepare the certification record in review posture.

The procedure must stop on any unexpected, unverifiable, ambiguous, or
contradictory state. It must not repair evidence to obtain a passing result.

---

## 14. Temporary Harness Governance

The harness shall be generated and executed outside the repository in a secure
temporary directory created with `mktemp -d` or an equivalent operating-system
facility.

This location is selected because it:

- keeps the repository worktree and index free of temporary certification code;
- avoids relying on an ignored repository path whose contents could be
  overlooked during review;
- makes final removal and scope verification unambiguous; and
- prevents accidental commitment as permanent test infrastructure.

Before execution, the exact harness content, resolved temporary location, input
paths, output paths, imported public contracts, and prohibited-operation audit
must be presented for human review.

### 14.1 Approved Harness Freeze

Once the exact harness source, byte count, SHA-256, path, interpreter, and
execution command receive explicit human approval, that reviewed harness is
frozen and immutable for the governed certification run.

After approval, no agent or human may regenerate, edit, reformat, optimize,
refactor, replace, rename, move, rewrite, touch, or otherwise mutate the harness.
Imports, comments, whitespace, line endings, and file bytes must remain exact.
Different source must not be copied over the approved path, and a semantically
equivalent but byte-different harness must not be executed under the prior
approval.

Any byte change invalidates the prior approval. The changed harness requires a
new byte count, a new SHA-256, a new complete-source review, and new explicit
human execution approval before any instruction from it may execute.

The Attempt 1 frozen execution definition was:

- path:
  `/tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py`;
- byte count: `14140`;
- SHA-256:
  `cacf44eca9428a8ab12002dd62608b26e87c7ccb6a1ea24de53b1ad924923108`;
- interpreter:
  `/home/talmadge/poe-backup-orchestrator/.venv/bin/python`; and
- execution command:
  `/home/talmadge/poe-backup-orchestrator/.venv/bin/python /tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py`.

Attempt 1 was executed and failed. Its definition and evidence remain historical
and must not be reused or retroactively validated. Every later attempt requires
its own byte count, SHA-256, path, interpreter identities, command,
complete-source review, and explicit execution approval.

### 14.2 Pre-execution Chain-of-custody Gate

Immediately before the first harness instruction is imported or executed, an
external pre-execution gate must independently calculate and record the actual
harness byte count, actual harness SHA-256, resolved harness path, actual
interpreter invocation path, canonical interpreter executable, Python version,
and exact command about to execute.

The external gate must compare those observations with the approved frozen
definition for that attempt. Execution must stop before importing or running the
harness if the observed byte count or SHA-256 differs from the separately
approved values. Harness-path, interpreter-identity, Python-version, or command
mismatches also fail the governed chain of custody and prohibit execution until
explicitly reviewed and approved.

Interpreter identity has three distinct governed attributes:

1. the approved interpreter invocation path, which is the exact path written in
   the approved execution command;
2. the approved canonical interpreter executable, which is the expected result
   of resolving that invocation path through symlinks; and
3. the approved Python version returned by the invocation path.

The gate compares invocation path to invocation path and canonical executable
to canonical executable. Neither value may be silently substituted for the
other. Resolution of an approved virtual-environment invocation path to its
separately approved canonical executable is not a mismatch. The exact command
must nevertheless use the approved invocation path.

For a proposed Attempt 2, these interpreter attributes are:

- invocation path:
  `/home/talmadge/poe-backup-orchestrator/.venv/bin/python`;
- canonical executable: `/usr/bin/python3.13`; and
- Python version: `3.13.5`.

Attempt 1 failed chain-of-custody because the architecture had not separately
approved the canonical executable before execution. This clarification governs
only a future, separately reviewed and approved attempt. It does not
retroactively validate Attempt 1.

The certification evidence must record fields equivalent to:

- Approved harness byte count;
- Observed harness byte count;
- Byte-count match;
- Approved harness SHA-256;
- Observed harness SHA-256;
- Digest match;
- Approved harness path;
- Resolved harness path;
- Path match;
- Approved interpreter invocation path;
- Observed interpreter invocation path;
- Invocation-path match;
- Approved canonical interpreter executable;
- Observed canonical interpreter executable;
- Canonical-executable match;
- Approved Python version;
- Observed Python version;
- Python-version match;
- Approved execution command;
- Observed execution command;
- Command match; and
- Pre-execution chain-of-custody result.

The result may be `PASS` only when every governed comparison matches. Digest
and byte-count verification must occur outside the harness before its process
starts. No self-verification code may be added to the approved harness because
doing so would change the reviewed bytes and invalidate approval.

The harness must:

- import installed repository public contracts from the certified worktree;
- contain no shell execution, network access, privilege escalation, source-tree
  writes, repository-history operations, deletion beyond its exact temporary
  root, or destructive API;
- use explicit absolute paths beneath its temporary root;
- use synthetic identities and content;
- create no persistent configuration or integration state;
- be inspectable as plain source before execution; and
- be removed after evidence capture.

Removal must target the exact resolved temporary root only. The final record
must state whether removal succeeded.

The final certification record must preserve the complete exact harness source
that was executed, preferably in a clearly delimited appendix or governed
source-code section. A summary or digest alone is insufficient for independent
auditability.

The record must also preserve:

- the SHA-256 digest of the exact executed harness bytes;
- the harness byte count;
- the resolved temporary harness path;
- the exact execution command;
- the exact Python interpreter path and Python version used;
- confirmation that the source embedded in the record reproduces the recorded
  harness byte count and SHA-256 when encoded as the governed executed bytes;
  and
- confirmation that the temporary executable harness file was removed after
  evidence capture.

The preserved Markdown source is governance evidence. It does not become a
permanent executable test, production file, importable module, certification
utility, or supported repository interface. The executable harness remains
outside the repository throughout execution and must not enter the final
committed worktree.

The harness must contain no secrets, credentials, tokens, production paths,
live identifiers, or environment-specific sensitive data. Such content is
prohibited from the executable harness and therefore must not appear in the
certification record. Synthetic paths and identities must be used wherever the
source itself records a value.

---

## 15. Synthetic Evidence Requirements

All scenario inputs must be synthetic and clearly labeled as certification
fixtures.

Synthetic evidence shall include enough governed content to exercise:

- one preservation baseline identity;
- one or more synthetic source-root identities;
- persisted inventory evidence and sidecar;
- persisted content-integrity evidence and sidecar where required by the
  selected validation profile;
- candidate evidence requirements and references;
- validated evidence facts and lineage;
- one acceptance recommendation;
- one explicit synthetic human authorization;
- one rejected authorization in the negative scenario; and
- isolated authorization and accepted-baseline publication directories.

Synthetic authority fields must state that they are certification-test
identities and make no authentication or real-world approval claim.

No path may resolve to production data, the repository source tree, a live NAS
location, or an authoritative evidence store.

---

## 16. End-to-End Public-Contract Scenario

The controlled scenario must use public contracts from candidate formation
through downstream accepted-baseline loading.

It shall prove, in order:

1. candidate composition from synthetic persisted-evidence references;
2. candidate identity and evidence-requirement coverage;
3. technical evidence loading, digest and sidecar verification;
4. governed deserialization, fact extraction, reconciliation, finding
   generation, and validation-result assembly as applicable;
5. deterministic acceptance evaluation;
6. explicit synthetic human authorization;
7. exact authorization persistence;
8. independent persisted-authorization reload and verification by the
   accepted-baseline constructor;
9. deterministic `pab-<sha256>` accepted-baseline construction;
10. full accepted-baseline artifact and sidecar publication;
11. authoritative reference artifact and sidecar publication last;
12. independent downstream loading beginning from the reference artifact;
13. complete baseline, candidate, validation, evaluation, authorization,
    persistence, accepted-baseline, and reference lineage;
14. exact preservation of scope, conditions, retention obligations, and
    `supersession_eligible`;
15. first-publication result;
16. sequential exact replay without rewrite;
17. independent SHA-256 sidecar verification;
18. restrictive permissions;
19. incomplete-state failure;
20. rejected authorization producing no publication; and
21. no source mutation or later authority.

The harness must not bypass the authoritative reference by supplying a full
accepted-baseline path or object directly to downstream loading.

---

## 17. Filesystem Evidence

The controlled run shall record:

- temporary filesystem root and filesystem type where determinable;
- authorization and accepted-baseline destination paths relative to that root;
- every final artifact and sidecar filename;
- regular-file and no-link observations;
- file byte counts;
- file permission modes;
- first-publication existence set;
- replay byte and modification-time observations;
- incomplete-state filenames and failure classification;
- rejection destination absence; and
- successful removal of only the synthetic temporary state.

Expected final artifact and sidecar modes are restrictive `0640`. Directory and
lock-directory observations shall be recorded without claiming guarantees the
host filesystem cannot prove.

The run proves successful filesystem behavior on the recorded isolated
environment. It is not a power-loss, storage-controller, or hardware-durability
certification.

---

## 18. Cryptographic Evidence

For authorization, full accepted-baseline, and reference artifacts, the run
shall record:

- artifact filename;
- exact byte count;
- calculated lowercase SHA-256;
- sidecar filename;
- sidecar content or verified canonical syntax;
- sidecar-to-artifact filename agreement;
- sidecar-to-calculated-digest agreement; and
- model/reference-to-calculated-digest agreement where applicable.

The required sidecar syntax is:

```text
<64-lowercase-hex-sha256>  <exact-filename>\n
```

SHA-256 evidence proves byte integrity. It does not prove authenticated human
identity, signer identity, or non-repudiation.

---

## 19. Replay Evidence

After first publication, the controlled procedure shall invoke the same public
publisher sequentially with the same verified authorization input.

Replay evidence must prove:

- the destination lock was successfully acquired;
- all four publication files were independently and completely verified;
- `idempotent_replay` is true only for the second result;
- artifact and sidecar bytes remain unchanged;
- modification times remain unchanged where the filesystem supports reliable
  observation; and
- no replacement, repair, merge, versioning, or silent deletion occurred.

Concurrent lock behavior is already covered by component tests and need not be
introduced into the controlled certification scenario.

---

## 20. Incomplete-State Evidence

In a separate synthetic publication directory, the harness shall create one
deliberately incomplete accepted-baseline publication set using synthetic bytes
only.

The public publisher must:

- acquire the destination lock;
- classify the state as an immutable incomplete-publication conflict;
- publish no missing file;
- leave the deliberately pre-existing synthetic file unchanged;
- perform no repair or cleanup of pre-existing state; and
- preserve the causal and classification evidence required by the approved
  contract.

The incomplete-state comparison must distinguish:

- pre-existing semantic publication state;
- governed lock infrastructure;
- temporary files owned by the active attempt; and
- final immutable publication artifacts and sidecars.

The deliberately pre-existing semantic artifact must remain byte-for-byte
unchanged. No missing accepted-baseline artifact, accepted-baseline sidecar,
reference artifact, or reference sidecar may be published. No pre-existing
semantic artifact may be repaired, replaced, removed, or normalized, and the
governed conflict must be raised.

Creation or reuse of the destination-scoped lock file is expected lock
infrastructure, not semantic evidence mutation. Lock files and `.locks`
directory entries must therefore be excluded from the semantic-state snapshot
comparison. Active-attempt temporary infrastructure that is not a final
semantic artifact must also be classified separately and handled according to
the certified cleanup contract. These distinctions do not weaken fail-closed
publication behavior or permit semantic-state mutation.

The harness may remove this synthetic directory only after recording the
failure evidence.

---

## 21. Rejection Evidence

The controlled procedure shall create one valid synthetic
`PreservationBaselineAuthorizationDecision` with outcome `REJECT`, persist it,
and invoke the accepted-baseline publication entry point.

The evidence must prove:

- the rejection decision persists as immutable authorization evidence;
- accepted-baseline construction fails with the governed rejection
  classification;
- no accepted-baseline destination or publication file is created;
- no reference is published; and
- rejection does not become an accepted-baseline lifecycle state.

---

## 22. Downstream Reference-Verification Evidence

Downstream verification must begin from the published reference artifact
contract and sidecar.

The controlled procedure shall prove:

- the reference pair is independently read and verified;
- its canonical bytes, byte count, filename, and SHA-256 agree;
- it resolves only the governed sibling full-artifact filename;
- the full baseline pair is independently verified;
- reference and full-baseline identities, mode, scope, digests, and lineage
  agree;
- the typed `AcceptedPreservationBaseline` is returned only after successful
  verification; and
- no candidate, validation result, authorization decision, persistence result,
  caller-supplied full path, or unverified full-baseline object substitutes for
  the authoritative reference boundary.

---

## 23. Negative-Authority Evidence

Certification must record both static inspection and controlled-run evidence
showing the absence of:

- source-content writes or authoritative-data access;
- validation or acceptance-policy reinterpretation during persistence or
  publication;
- implicit human authorization;
- scope expansion or contraction;
- authorization-evidence repair or normalization;
- acceptance inferred from persistence success;
- supersession records or execution;
- classification, destination design, or duplicate disposition;
- migration planning or execution;
- NAS consolidation;
- client redirection;
- cleanup authorization or execution;
- deletion, deduplication, restructuring, renaming, or source mutation;
- retention release;
- CLI, configuration, authentication, signature, notification, identity
  provider, or external integration; and
- Phase 6C work.

The harness itself must be audited for these prohibited capabilities before it
is authorized to run.

---

## 24. Architectural Traceability Matrix Requirements

The certification record must include an Architectural Traceability Matrix
with these columns:

| Responsibility | Approved slice | Models | Services | Tests | Certification evidence | Status |
|---|---|---|---|---|---|---|

The matrix must cover at least:

- candidate formation;
- technical validation;
- acceptance evaluation;
- human authorization;
- authorization persistence;
- independent authorization verification;
- accepted-baseline construction;
- accepted-baseline publication;
- reference publication;
- downstream reference verification;
- identity and complete lineage;
- replay and conflict behavior;
- retention obligations;
- supersession eligibility; and
- negative authority boundaries.

Each row must cite exact implemented contracts, services, focused tests, and
controlled-procedure observations. A row may be `PASS` only when all cited
evidence exists and agrees. Documentation alone cannot make a row pass.

The matrix must identify technical validation as implemented across the 6B-2
architecture and the historical 6B-7 and 6B-8 implementation documents rather
than concealing the numbering history.

---

## 25. Quality Gates

The full repository gate is mandatory:

```bash
source .venv/bin/activate
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Before commit, also require:

```bash
git diff --cached --check
```

The certification record shall capture the executed results and final test
total. It must not copy the predecessor total if the repository state has
changed.

Quality-gate success is necessary but does not substitute for the controlled
procedure, architectural conformance review, or human certification approval.

---

## 26. Certification Record Structure

The final permanent record is:

```text
docs/reports/POE-STOR-Phase-6B-Certification-Record.md
```

It must include:

1. purpose;
2. document status and approval posture;
3. certified and excluded scope;
4. separately labeled certified software baseline, certification package,
   certification merge, and final `origin/main` commit identities, plus branch
   and relevant Git history;
5. Python, platform, and filesystem context;
6. implementation inventory;
7. Architectural Traceability Matrix;
8. unit and component evidence;
9. full quality-gate evidence and test total;
10. controlled certification-procedure evidence, including the exact execution
    command, interpreter, Python version, and resolved harness path;
11. synthetic identifiers and lineage;
12. filesystem and cryptographic evidence;
13. first-publication and replay evidence;
14. incomplete-state and rejection evidence;
15. downstream reference-verification evidence;
16. negative-authority evidence;
17. historical discrepancies;
18. approved deferrals;
19. residual risks;
20. formal certification result;
21. formal Phase 6B closeout decision;
22. Phase 6C readiness statement;
23. complete exact executed harness source in a delimited governed appendix,
    its byte count and SHA-256, reproduction verification, and removal
    confirmation;
24. explicit human approval record; and
25. final repository status.

The record must begin in a review posture. Before successful execution and
explicit human approval it must state, equivalently:

```text
Status: Certification evidence in review
Certification result: NOT YET DETERMINED
Phase 6B closeout: NOT AUTHORIZED
```

It must not claim `PASS`, certification, closeout, or Phase 6C readiness until
all required evidence has passed and explicit human certification approval has
been granted.

---

## 27. Formal Closeout Criteria

Phase 6B may be formally certified and closed only when:

1. every required traceability row is complete and passing;
2. all public contracts import and compose correctly;
3. the controlled synthetic scenario completes successfully;
4. authorization and publication artifacts independently verify;
5. downstream loading begins from the reference;
6. identity, lineage, scope, conditions, retention, and eligibility remain
   exact;
7. first publication and sequential exact replay pass;
8. incomplete publication fails closed without mutation;
9. rejected authorization produces no accepted-baseline publication;
10. only synthetic isolated state was created or removed;
11. no later authority or destructive operation occurred;
12. the temporary harness and synthetic state are removed;
13. the final permanent worktree contains only approved certification
    documents;
14. the full repository quality gate passes;
15. all discrepancies, deferrals, and residual risks are recorded;
16. the certification record identifies the certified software baseline
    separately from every applicable certification-package, merge, and final
    remote identity;
17. the complete exact harness source in the record reproduces the recorded
    harness byte count and SHA-256 and the temporary executable file is removed;
    and
18. an accountable human explicitly approves the certification result and
    closeout.

Any failed or unverifiable criterion keeps Phase 6B open.

---

## 28. Residual Risks

The certification record must evaluate at least:

- unit-heavy evidence before the controlled end-to-end run;
- filesystem observations being environment-specific rather than a hardware
  power-loss guarantee;
- SHA-256 integrity not providing authenticated signer identity;
- absence of deployed recurring certification automation;
- supersession contracts and execution remaining deferred;
- stale historical status metadata;
- roadmap and parent-architecture naming conflicts;
- Phase 6A lacking a dedicated closeout record;
- representative restore testing remaining required for a real operational
  preservation baseline; and
- downstream Phase 6C having no authority until separately architected.

Residual risks may be accepted only when they do not contradict the certified
scope and are explicitly approved by the human certifier.

---

## 29. Historical Discrepancy Handling

Earlier architecture documents must remain historically unchanged.

The certification record becomes the authoritative current Phase 6B status
record and shall explain, without rewriting history:

- stale proposed or implementation-review statuses;
- obsolete predecessor commits and test totals;
- the roadmap's older Phase 6B and Phase 6C names;
- the parent 6B-5 responsibility later split across 6B-5 and 6B-6;
- the parent `6B-7` certification identifier collision;
- validation implementation under historical 6B-7 and 6B-8 documents;
- later exclusive-placement refinement of atomic-replacement wording;
- later non-blocking lock-contention refinement of compatible-retry wording;
- preservation of supersession eligibility with execution deferred; and
- the absence of a prior Phase 6B certification or closeout record.

Later approved slice architecture may refine an earlier proposal. The record
must cite that refinement rather than silently treating the earlier statement
as implemented.

---

## 30. Numbering-Collision Resolution

The durable resolution is:

```text
6B-7 — Validation Finding Generation                 HISTORICAL / PRESERVED
6B-8 — Validation Result Assembly                    HISTORICAL / PRESERVED
POE-STOR-PHASE-6B-CERT — Phase 6B Certification     CURRENT PHASE-LEVEL ID
```

No alias, renumbering, document rename, amended historical commit, or new
numeric certification slice is permitted.

Future references to Phase 6B certification must use
`POE-STOR-PHASE-6B-CERT` or the full phase-level title.

---

## 31. Relationship to Phase 6C

Phase 6C architecture discovery may begin only after:

1. the controlled certification procedure and quality gates pass;
2. the final certification record is complete;
3. explicit human approval grants `PASS` and Phase 6B closeout;
4. the certification package is committed and merged into `main`;
5. `main` and `origin/main` are synchronized; and
6. the repository is clean.

The later parent architecture identifies the next functional boundary as:

```text
Phase 6C — Classification and Destination Design
```

That phase must begin from an independently verified
`AcceptedPreservationBaselineReference`. It may receive analytical
classification and design authority only. Migration, supersession execution,
redirection, cleanup, and destructive authority remain withheld.

This certification effort must not create Phase 6C documents, contracts,
services, tests, configuration, or decisions.

---

## 32. Exact Architecture-Only Worktree Scope

Preparation and review of this architecture is limited to:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Phase-6B-Certification.md
```

No certification record or harness is authorized in this architecture-only
change.

---

## 33. Exact Later Certification Worktree Scope

After separate architecture, execution, and implementation authorization, the
only permanent certification files may be:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Phase-6B-Certification.md
docs/reports/POE-STOR-Phase-6B-Certification-Record.md
```

The temporary harness and all synthetic evidence must remain outside the
repository and must be removed after evidence capture.

No permanent production code, model, service, export, CLI, configuration,
test, fixture, harness, generated evidence, or integration file is authorized.

If certification exposes a product defect, correction requires a separate
architecture review and approved worktree scope. The certification effort must
not silently repair implementation.

---

## 34. Recommended Execution Sequence

After explicit authorization:

1. verify the certified predecessor state and clean worktree;
2. create the authorized certification feature branch while preserving this
   document;
3. prepare the draft certification record in review posture;
4. generate the temporary harness outside the repository;
5. present the complete harness, resolved paths, and safety audit for explicit
   human execution approval;
6. record environment and repository context;
7. record the reviewed harness source, exact bytes, byte count, SHA-256,
   resolved path, execution command, interpreter, and Python version;
8. run the external pre-execution chain-of-custody gate and stop before import
   or execution unless every approved and observed harness value matches;
9. execute the controlled synthetic scenario against the certified software
   baseline;
10. capture objective filesystem, cryptographic, replay, failure, rejection,
   lineage, and negative-authority evidence;
11. preserve the complete exact executed harness source in the record and prove
    that it reproduces the recorded byte count and SHA-256;
12. remove the temporary executable harness and synthetic state and record the
    result;
13. verify the permanent worktree contains only the two approved documents;
14. run the full quality gates and staged whitespace gate when applicable;
15. complete the traceability matrix, discrepancy register, deferral register,
    risk assessment, and evidence sections;
16. present the complete certification package in review posture with separate
    Git identity fields and `PENDING` where an integration identity does not yet
    exist;
17. obtain explicit human certification and closeout approval;
18. update the record to `PASS` or another approved final result only as
    authorized;
19. commit, push, and merge only under separate explicit approvals, recording
    package, merge, and final `origin/main` identities as they become available;
    and
20. verify synchronized `main`, clean repository state, and retained evidence
    before any Phase 6C discovery begins.

---

## 35. Acceptance Criteria

This architecture is ready for approval when it:

- uses the approved phase-level identifier and resolves the numbering collision;
- preserves all historical documents unchanged;
- distinguishes software certification from production-baseline acceptance;
- limits permanent artifacts to the architecture and final record;
- defines an inspectable external temporary harness with explicit removal;
- requires complete exact harness source, byte count, SHA-256, execution
  command, interpreter, version, path, digest reproduction, and removal evidence;
- prohibits production data and destructive authority;
- defines the complete public-contract scenario;
- requires objective filesystem, cryptographic, replay, incomplete-state,
  rejection, reference, lineage, and negative evidence;
- defines the Architectural Traceability Matrix;
- separates evidence classes and human approval;
- requires all quality gates;
- preserves supersession eligibility while deferring execution;
- defines review-first certification-record posture;
- separates the certified software baseline from certification package, merge,
  and final remote commit identities;
- withholds Phase 6C until approved closeout is merged; and
- grants no execution or implementation authority by itself.

The later certification package is acceptable only when every criterion in
Section 27 is satisfied and explicitly approved.

---

## 36. Human Approval Boundaries

Explicit human approval is required for:

1. this certification architecture;
2. creation of the certification branch and draft record;
3. the exact temporary harness before execution;
4. the resolved temporary paths and synthetic input scope;
5. execution of the controlled procedure;
6. any response to a failed or contradictory result;
7. the completed evidence and traceability matrix;
8. the formal certification result;
9. Phase 6B closeout;
10. commit and feature-branch publication;
11. merge and `origin/main` publication; and
12. authorization to begin Phase 6C architecture discovery.

Passing tests, successful procedure execution, or clean Git state cannot
substitute for these approval boundaries.

---

## 37. Architectural Decision

Phase 6B certification is a distinct phase-level governance transition under
`POE-STOR-PHASE-6B-CERT`.

Its governing rule is:

> Certify the implemented software boundary with synthetic, isolated,
> independently verifiable evidence. Preserve history. Grant no operational or
> later-phase authority until an accountable human explicitly approves and
> closes Phase 6B.

This document authorizes no certification execution, certification result,
closeout, repository-history change, or Phase 6C work.
