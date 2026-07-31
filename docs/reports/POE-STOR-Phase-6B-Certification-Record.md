# POE Storage Phase 6B Certification Record

**Certification identifier:** POE-STOR-PHASE-6B-CERT

**Status:** Phase 6B certification approved

**Certification result:** PASS

**Phase 6B closeout:** APPROVED

**Phase 6C readiness:** AUTHORIZED AFTER CERTIFICATION MERGE AND origin/main SYNCHRONIZATION

## 1. Purpose and posture

This record is the proposed evidence package for certifying the Phase 6B software
governance boundary. It does not certify that a production preservation baseline
exists, that production storage is operationally ready, or that any preservation,
migration, redirection, cleanup, supersession, or destructive authority has been
granted.

Controlled Certification Attempt 1 was authorized, executed once, and ended
`FAILED / INCOMPLETE`. Controlled Certification Attempt 2 completed successfully,
its evidence was independently verified, and accountable human review approved the
Phase 6B certification result and closeout. Phase 6C has not begun and remains
conditional on certification-package integration, synchronized `origin/main`, and
a clean repository.

## 2. Certified and excluded scope

The candidate scope is the deterministic Phase 6B chain from preservation-baseline
candidate composition through technical validation, acceptance evaluation, human
authorization, immutable authorization persistence, independent persisted-evidence
verification, accepted-baseline construction and publication, authoritative
reference publication, and downstream loading initiated from that reference.

Certification excludes production data and operational readiness. It must not
classify, relocate, consolidate, deduplicate, rename, restructure, modify, clean, or
delete source content; assign NAS destinations; create or execute preservation or
migration plans; redirect clients; execute supersession; release retention
obligations; authorize cleanup; change production code or repository configuration;
or begin Phase 6C.

## 3. Git identity separation

These identities are distinct and must never be inferred from one another:

| Git identity | Commit |
| --- | --- |
| Certified software baseline commit | `1fbf4355a4ad1783fda988c26122715941c50eb0` |
| Certification preparation commit | `61ee06e3dcf73240e5b4164cceda2c98116cbffd` |
| Final certification evidence/decision commit | `PENDING` |
| Certification merge commit | `PENDING` |
| Final origin/main commit | `PENDING` |

The controlled procedure executed against the unchanged certified software
baseline. A later documentation commit does not become the tested
software baseline merely because it records evidence. Every result must remain
attributable to the exact software bytes tested.

Preparation branch: `feature/phase-6b-certification`. Candidate baseline history:

```text
1fbf435 Merge Slice 6B-6 accepted baseline publication
e05611d Implement Slice 6B-6 accepted baseline publication
8314448 Merge Slice 6B-5 authorization persistence
1dfdc2d Implement Slice 6B-5 authorization persistence
f514c38 Merge repository governance instructions
f514c38 predecessor history includes the merged Phase 6B-4 implementation
```

The exact preparation and final histories will be re-recorded during closeout.

## 4. Implementation inventory

| Responsibility | Principal models | Principal services | Principal tests |
| --- | --- | --- | --- |
| Candidate formation | `PreservationBaselineCandidate`, `PreservationEvidenceReference`, `PreservationEvidenceRequirement` | `PreservationBaselineComposer` | `test_storage_baseline_candidate_models.py`, `test_storage_baseline_composition.py` |
| Technical validation | `PreservationBaselineValidationResult`, `ValidatedEvidenceReference`, `ValidationFinding` | `FilesystemPreservationEvidenceLoader`, validation fact/reconciliation/finding services, `PreservationBaselineValidationResultAssembler` | `test_storage_baseline_validation*.py` |
| Acceptance evaluation | `AcceptancePolicy`, `PreservationBaselineAcceptanceRecommendation` | `PreservationBaselineAcceptanceEvaluator` | `test_storage_baseline_acceptance*.py` |
| Human authorization | `PreservationBaselineAuthorizationDecision`, authority, condition, scope, pilot, and identity contracts | `PreservationBaselineAuthorizationDecisionAssembler` | `test_storage_baseline_authorization*.py` |
| Authorization persistence | persistence artifact and result contracts | serializer and `PreservationBaselineAuthorizationStore` | `test_storage_baseline_authorization_persistence*.py` |
| Accepted baseline and reference | `AcceptedPreservationBaseline`, reference, artifact, publication-result, identity and mode contracts | constructor, serializer, and `AcceptedPreservationBaselinePublisher` | `test_storage_accepted_baseline*.py` |

Package exports expose the governed public models and services required by the
proposed scenario. Persisted-authorization verification remains private inside the
accepted-baseline service. The downstream full baseline is reachable only through
`AcceptedPreservationBaselinePublisher.load_from_reference` after independent
reference and full-artifact verification.

## 5. Architectural Traceability Matrix

Accountable human review considered the implemented contracts, focused tests,
889-test regression suite, Controlled Certification Attempt 2, independent
post-execution verification, and negative-authority inspection.

| Responsibility | Approved slice | Models | Services | Tests | Certification evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Candidate formation | 6B-1 | Candidate identity, scope, observations, evidence references | `PreservationBaselineComposer` | Candidate model/composition unit tests | Synthetic public-contract composition | PASS |
| Technical validation | 6B-2, historical 6B-7/6B-8 | Validation policy, validated reference, findings, result | Evidence loader, fact/reconciliation/finding services, result assembler | Validation model/service unit tests | Verified synthetic evidence and assembled result | PASS |
| Acceptance evaluation | 6B-3 | Policy, conditions, recommendation | `PreservationBaselineAcceptanceEvaluator` | Acceptance model/service unit tests | Deterministic acceptance recommendation | PASS |
| Human authorization | 6B-4 | Authority, outcome, scope, decision | Authorization decision assembler | Authorization model/service unit tests | Explicit synthetic authority decision | PASS |
| Authorization persistence | 6B-5 | Persistence artifact and result | Authorization serializer/store | Persistence unit tests | First immutable persistence and sidecar | PASS |
| Independent authorization verification | 6B-6 | Persistence result as locator | Private verifier within accepted-baseline service | Verification and malformed-evidence tests | Construction from independently reopened bytes | PASS |
| Accepted-baseline construction | 6B-6 | Accepted identity, mode, full baseline | Accepted-baseline constructor | Identity, outcome, lineage tests | Deterministic `pab-<sha256>` projection | PASS |
| Accepted-baseline publication | 6B-6 | Full artifact and publication result | Accepted-baseline publisher | Publication, replay, conflict tests | Full JSON artifact and sidecar | PASS |
| Reference publication | 6B-6 | Immutable lightweight reference | Accepted-baseline publisher | Ordering and reference tests | Reference JSON and sidecar published last | PASS |
| Downstream reference verification | 6B-6 | Reference and full baseline | `load_from_reference` | Downstream-boundary tests | Independent load initiated from reference | PASS |
| Identity and lineage | 6B-1 through 6B-6 | `pbc`, `pbv`, `pba`, `pbd`, `pab` identities | Deterministic constructors and serializers | Identity/lineage suites | All identifiers and exact nested lineage | PASS |
| Replay and conflict behavior | 6B-5, 6B-6 | Persistence/publication results | Immutable stores and publisher | Replay, sidecar, partial-state, concurrency tests | First publication, exact replay, incomplete-state failure | PASS |
| Retention obligations | 6B-4, 6B-6 | Authorization and accepted-baseline fields | Assembler and constructor | Preservation/lineage tests | Exact retained obligation | PASS |
| Supersession eligibility | 6B-4, 6B-6 | Boolean governance field | Assembler and constructor | Preservation and negative-authority tests | Preserved `true`; no supersession contract or execution | PASS |
| Negative authority boundaries | All Phase 6B slices | No execution-authority contract | No migration/cleanup/supersession service | Negative-authority tests | Input snapshots, no later authority, isolated temporary paths | PASS |

Attempt 2 produced objective evidence for every matrix responsibility, and human
certification review approved every required row as PASS.

## 6. Existing unit and component evidence

The certified software baseline candidate was merged with Ruff formatting and static
analysis passing and 889 tests passing. That regression total is an input to
certification, not sufficient certification evidence by itself. Preparation-time
quality-gate results are recorded in Section 11 after execution; controlled
certification evidence remains pending.

## 7. Proposed controlled procedure

The Attempt 2 harness created a secure temporary execution root outside the
repository and used public package contracts to:

1. create canonical synthetic evidence and a governed SHA-256 sidecar;
2. compose one candidate and authenticate its evidence;
3. assemble technical validation with no findings and evaluate acceptance;
4. assemble explicit synthetic authorization with scope, retention, and
   supersession-eligibility evidence;
5. persist authorization evidence immutably;
6. construct and publish the accepted baseline by independently reopening the
   persistence result's artifact;
7. publish its reference, then load the full baseline only from that reference;
8. prove first publication and sequential verified replay without rewrite;
9. verify artifact digests, exact sidecar syntax, byte counts, and `0640` modes;
10. prove an incomplete publication fails closed and remains unchanged;
11. prove rejected authorization creates no publication destination;
12. prove synthetic inputs remain byte-identical and no later authority occurs.

Attempt 2 execution command, interpreter identities, exact temporary root, results,
and cleanup confirmation are recorded below. The complete executed source is
preserved verbatim with its exact byte count and digest in Appendix B.

## 8. Controlled Certification Attempt 1 — FAILED / INCOMPLETE

Attempt 1 is permanently classified `FAILED / INCOMPLETE`. It cannot support
certification and must never be rewritten or retroactively relabeled as PASS.
Its approved harness was frozen for that attempt: no agent or human may
regenerate, edit, reformat, refactor, optimize, replace, or otherwise rewrite
its historical definition or evidence.

Any byte change invalidates the approval and requires a new byte count, SHA-256,
complete-source review, and explicit human execution approval.

### 8.1 Frozen candidate execution definition

| Field | Preparation value | Executed value |
| --- | --- | --- |
| Complete source | Preserved in Appendix A | Executed source preserved; byte count and digest reproduced |
| Approved harness path | `/tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py` | Same invocation path; canonical path matched |
| Approved harness byte count | 14140 bytes | 14140 bytes |
| Approved harness SHA-256 | `cacf44eca9428a8ab12002dd62608b26e87c7ccb6a1ea24de53b1ad924923108` | Same digest |
| Approved interpreter | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python`; preparation version 3.13.5 | Invocation path same; canonical target `/usr/bin/python3.13`; Python 3.13.5 |
| Approved execution command | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python /tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py` | Same command executed once |
| Resolved execution root | Not created | `/tmp/poe-phase-6b-certification-q_34t7c3` |
| Executable harness removed | Not applicable; execution not authorized | CONFIRMED after evidence capture |

### 8.2 Mandatory external pre-execution gate

Immediately before any harness instruction is imported or executed, an external
workflow must calculate and compare the following values. Digest and byte-count
verification must occur outside the harness before its process starts. The
approved harness must not receive self-verification code because that would
change its reviewed bytes.

| Chain-of-custody field | Approved value | Observed pre-execution value | Match |
| --- | --- | --- | --- |
| Harness byte count | 14140 | 14140 | YES |
| Harness SHA-256 | `cacf44eca9428a8ab12002dd62608b26e87c7ccb6a1ea24de53b1ad924923108` | `cacf44eca9428a8ab12002dd62608b26e87c7ccb6a1ea24de53b1ad924923108` | YES |
| Harness path | `/tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py` | `/tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py` | YES |
| Interpreter | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python` | `/usr/bin/python3.13`; Python 3.13.5 | NO — canonical path differs |
| Execution command | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python /tmp/poe-phase-6b-certification-preparation.5AGJgZ/phase_6b_certification_harness.py` | Same exact command | YES |

**Pre-execution chain-of-custody result:** FAIL

The harness process was started despite the canonical-interpreter mismatch. This
contravened the governed stop condition and invalidates the run as certification
evidence. The discrepancy and execution are retained here rather than silently
reclassified as a match.

The result may become `PASS` only if every comparison matches. A byte-count or
digest mismatch must stop the workflow before import or execution. A path,
interpreter, or command mismatch likewise prohibits execution until reviewed
and explicitly approved.

A summary or digest alone is insufficient. The final record must contain the exact
executed source in a delimited appendix, state its resolved path and execution
command, and confirm that re-encoding the preserved source reproduces both the
executed byte count and SHA-256. Secrets, credentials, tokens, production paths, and
environment-sensitive data are prohibited from both harness and record.

## 9. Controlled-run evidence placeholders

Attempt 1 remains failed and incomplete. Attempt 2 execution-derived fields are
populated below. Human architectural-conformance review, formal certification,
closeout, certification-package Git identities, and Phase 6C readiness remain
`PENDING` or `NOT AUTHORIZED` as applicable.

No production identifiers, paths, evidence, credentials, or source content may be
introduced when these fields are completed.

### 9.1 Controlled Certification Attempt 1 execution evidence

The exact approved command was executed once. The process exited with status 1
before emitting its governed evidence document. It reached candidate composition,
technical validation, acceptance evaluation, authorization persistence,
accepted-baseline publication, sequential replay, downstream reference loading,
and the incomplete-publication conflict exercise.

The failure was:

```text
AssertionError: incomplete state changed
```

The assertion occurred at harness line 258. The incomplete-publication conflict
correctly failed closed for semantic artifacts, but the repository locking utility
created the expected zero-byte
`.locks/accepted-preservation-baseline-publication.lock` file. The harness snapshot
treated that lock file as an impermissible state change. The approved frozen harness
must not be modified or rerun under the prior approval.

The run did not reach the rejected-authorization scenario, final evidence JSON
write, or cleanup. Controlled certification result: `FAILED / INCOMPLETE`.

After independent evidence capture and appendix-digest reproduction, the exact
synthetic execution root
`/tmp/poe-phase-6b-certification-q_34t7c3` and exact harness preparation root
`/tmp/poe-phase-6b-certification-preparation.5AGJgZ` were removed under the
authorized cleanup boundary. Both paths were confirmed absent. No repository or
production path was included in cleanup.

Observed synthetic identities before failure:

- baseline: `synthetic-baseline-001`;
- candidate: `pbc-50276a2727307a8bf77ab65a5055fc27cacfb29aac0c4d316c1a6f01a6e0ca1a`;
- validation: `pbv-7a72cd58805727cb6c6d13c1480a387fbb17e2fd8cdfa63ef88b354098bd55f2`;
- evaluation: `pba-033a442e14730b48e83597137d223ee1e78cceab9249dc68e1f175391484838d`;
- authorization: `pbd-1b84ac27a58cde5df35b87ac364e6a0d0abcef8903beb8c514211e4afdcd124d`;
- accepted baseline:
  `pab-ee621373f448c475f04ad6697c5b449a097118d50f3c566e19927102ce02abc8`.

Observed governed artifact evidence before failure:

| Artifact | Bytes | SHA-256 | Mode |
| --- | ---: | --- | --- |
| Synthetic input | 154 | `b8e6a125623da03301c00ee4c98df4f329510c1f6ded6170d4dd84d815e69ab0` | `0600` |
| Authorization | 3753 | `07d45e95944de779da3090033a691c1c58d0332601bc6f64d0e1cd6c52a77c14` | `0640` |
| Accepted baseline | 5332 | `fb1cf35c3e906ac730b08c3ad9674602d974d12c9cf66b020d8a2b6aef4ea808` | `0640` |
| Accepted-baseline reference | 767 | `05e556b7632a71e3e4d42f0302b6c30f2b430406b6f1a6d144b7da6dd0078646` | `0640` |

Each governed artifact had a canonical two-space SHA-256 sidecar with one final
newline and mode `0640`. The controlled run remains invalid because the external
chain-of-custody gate did not pass and the harness did not complete.

### 9.2 Controlled Certification Attempt 2 — PREPARATION / NOT EXECUTED

Attempt 2 execution is not authorized. The following new, byte-distinct proposed
harness was generated outside the repository for review and has not been imported
or executed.

| Proposed Attempt 2 field | Value | Execution observation |
| --- | --- | --- |
| Complete source | Appendix B | Exact executed source preserved |
| Preparation path | `/tmp/poe-phase-6b-certification-attempt2-preparation.TwyA6i/phase_6b_certification_attempt2_harness.py` | Exact path matched |
| Line count | 373 | 373 |
| Byte count | 15446 | 15446 — match |
| SHA-256 | `ca28135f2a06c2b107ad00e4ccce73402fafb30d36e8ca41b08aed9fd1f4bad1` | Same digest — match |
| Interpreter invocation path | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python` | Same invocation path — match |
| Canonical interpreter executable | `/usr/bin/python3.13` | `/usr/bin/python3.13` — match |
| Python version | `3.13.5` | `3.13.5` — match |
| Exact proposed command | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python /tmp/poe-phase-6b-certification-attempt2-preparation.TwyA6i/phase_6b_certification_attempt2_harness.py` | Same exact command executed once |
| Pre-execution chain-of-custody result | Required | PASS |

The source was frozen after complete-source review and explicit human approval.
It was executed exactly once without modification or regeneration.

The only intended behavioral difference from Attempt 1 is the governed
incomplete-state correction. Attempt 2 excludes `.locks`, lock files, and hidden
active-attempt temporary infrastructure from the semantic snapshot; separately
compares the pre-existing incomplete artifact bytes; and explicitly proves that
the missing accepted-baseline sidecar, reference, and reference sidecar remain
absent. It still requires the governed immutable conflict and permits only expected
destination-lock infrastructure.

Expected output remains one synthetic evidence JSON document containing Phase 6B
identities, artifact filenames, byte counts, SHA-256 values, sidecar syntax,
permissions, first-publication and replay results, downstream-reference loading,
corrected incomplete-state failure, rejected-decision non-publication, unchanged
inputs, retained obligations, supersession eligibility, and negative-authority
results.

#### Attempt 2 execution evidence

- external chain-of-custody result: `PASS`;
- UTC start timestamp: `2026-07-31T19:15:17,427376115+00:00`;
- UTC completion timestamp: `2026-07-31T19:15:24,960280429+00:00`;
- process exit code: `0`;
- stderr: empty;
- platform: `Linux 6.18.34+rpt-rpi-v8 aarch64`;
- temporary filesystem: `tmpfs`, block size `4096`;
- synthetic execution root:
  `/tmp/poe-phase-6b-certification-ji2dedxp`;
- evidence-document byte count: `3074`;
- evidence-document SHA-256:
  `f7306a35e252438d07060e7241bb37d90e8b7caa0b6a0172a39e4324d50e2b07`.

Execution stdout was the following governed evidence object:

```json
{
  "schema_version": "phase-6b-certification-evidence-1.0",
  "software_baseline": "1fbf4355a4ad1783fda988c26122715941c50eb0",
  "execution_root": "/tmp/poe-phase-6b-certification-ji2dedxp",
  "identifiers": {
    "baseline_id": "synthetic-baseline-001",
    "candidate_id": "pbc-50276a2727307a8bf77ab65a5055fc27cacfb29aac0c4d316c1a6f01a6e0ca1a",
    "validation_id": "pbv-7a72cd58805727cb6c6d13c1480a387fbb17e2fd8cdfa63ef88b354098bd55f2",
    "evaluation_id": "pba-033a442e14730b48e83597137d223ee1e78cceab9249dc68e1f175391484838d",
    "authorization_id": "pbd-1b84ac27a58cde5df35b87ac364e6a0d0abcef8903beb8c514211e4afdcd124d",
    "accepted_baseline_id": "pab-ee621373f448c475f04ad6697c5b449a097118d50f3c566e19927102ce02abc8"
  },
  "results": {
    "authorization_first_persistence": true,
    "accepted_baseline_first_publication": true,
    "accepted_baseline_exact_replay": true,
    "downstream_reference_verification": true,
    "incomplete_publication_failed_closed": true,
    "rejected_authorization_no_publication": true,
    "synthetic_inputs_unchanged": true,
    "supersession_eligible_preserved_without_execution": true,
    "later_authority_exercised": false,
    "destructive_operation_exercised": false
  }
}
```

Independent verification reproduced every governed artifact digest and canonical
two-space sidecar, verified `0640` artifact and sidecar permissions, and confirmed
the reference independently loads the full accepted baseline through the public
reference boundary. The loaded baseline preserved the authorization, validation,
candidate, and baseline lineage; accepted source root; retention obligation; and
`supersession_eligible=true`.

Independent extraction of Appendix B reproduced exactly 15,446 bytes and SHA-256
`ca28135f2a06c2b107ad00e4ccce73402fafb30d36e8ca41b08aed9fd1f4bad1`
before cleanup of the temporary executable source.

The incomplete publication retained its 5,332-byte pre-existing semantic artifact
with SHA-256
`beff296abcbc5c066b5f03d431facc505ad94bc5c1b2ddce74f9558514277343`.
Its baseline sidecar, reference, and reference sidecar remained absent. The only
additional entry was governed `.locks` infrastructure. The rejected authorization
persisted as `pbd-16d83460faebaf24a6d4ef82428f3f98c5714398bddac299580eaeda46455e92`,
while the rejected publication directory remained absent.

Attempt 2 supplies complete controlled-procedure evidence for human review. It does
not itself establish certification PASS, Phase 6B closeout, or Phase 6C readiness.

After evidence capture and Appendix B reproduction, bounded cleanup removed only
`/tmp/poe-phase-6b-certification-ji2dedxp` and
`/tmp/poe-phase-6b-certification-attempt2-preparation.TwyA6i`. Both exact paths
were confirmed absent, and no other Phase 6B certification temporary directory
remained under `/tmp`.

The proposed harness imports only the public models and services listed in
Appendix B: candidate, evidence-reference, validation, acceptance, authorization,
authorization-persistence, accepted-baseline publication, and downstream-reference
loading contracts. Persisted-authorization verification remains an internal service
concern reached through the public publisher.

Expected temporary layout is one securely generated
`/tmp/poe-phase-6b-certification-*` execution root containing `accepted-input`,
`authorization`, `publication`, `incomplete-publication`, `rejected-input`,
`rejected-authorization`, and the final synthetic evidence JSON. A rejected
publication directory must remain absent.

Static inspection found no network, subprocess, shell, privilege, Git, production,
NAS, credential, secret, repository-write, migration, redirection, cleanup-authority,
supersession-execution, or destructive-service surface. The harness contains no
cleanup operation. After evidence capture, separately governed cleanup may remove
only its exact resolved synthetic execution root and the exact Attempt 2 preparation
root.

## 10. Filesystem, cryptographic, and negative-authority evidence

The controlled run must record all created synthetic files beneath one resolved
temporary root, verify lowercase SHA-256 and canonical two-space sidecars with one
final newline, record byte counts and restrictive modes, and establish that replay
does not rewrite the four publication files. It must retain contradictory incomplete
state unchanged after the governed failure.

Negative-authority evidence must show that input snapshots are unchanged; rejected
authorization publishes nothing; the public downstream path starts at the reference;
and no migration, classification, NAS mapping, redirection, cleanup, deletion,
supersession execution, external integration, or production path exists in the
harness or resulting state.

## 11. Quality-gate evidence

Final certification-review quality gates:

| Gate | Result |
| --- | --- |
| `ruff format --check .` | PASS — 236 files already formatted |
| `ruff check .` | PASS |
| `pytest -q` | PASS — 889 tests |
| `git diff --check` | PASS |
| Untracked-document whitespace audit | PASS after preparation correction |

Before a certification package commit, the workflow must also run
`git diff --cached --check`. Gate success does not itself authorize commit or
integration.

## 12. Known discrepancies and approved deferrals

- Historical Slice 6B-7 means Validation Finding Generation and Slice 6B-8 means
  Validation Result Assembly. The parent architecture's proposed use of 6B-7 for
  certification is obsolete; `POE-STOR-PHASE-6B-CERT` resolves the collision without
  renumbering or rewriting merged history.
- Later approved slices refined stale parent naming and status metadata. Historical
  documents remain unchanged; this record becomes authoritative only after approval
  and integration.
- Supersession execution is intentionally deferred. Certification must demonstrate
  only that `supersession_eligible` is preserved and grants no execution authority.
- Phase 6C classification and all target architecture, duplicate disposition,
  migration planning, execution, redirection, cleanup, and operational certification
  remain deferred.
- No permanent historical-certification integration test or executable harness is
  authorized.

## 13. Residual-risk framework

Human certification review accepts these residual risks within the certified scope:

- certification used synthetic rather than production evidence;
- filesystem observations apply to the recorded Linux/tmpfs environment and are
  not a power-loss or storage-controller guarantee;
- SHA-256 establishes byte integrity but not authenticated human identity;
- representative restore testing remains required for a future real accepted
  preservation baseline;
- supersession records and execution remain deferred;
- classification, destination design, migration, redirection, cleanup, and final
  Phase 6 operational certification remain deferred;
- historical naming, numbering, and status discrepancies remain documented rather
  than rewritten; and
- Phase 6A has no dedicated phase closeout record.

These accepted residual risks do not invalidate the certified Phase 6B software
governance boundary and must not be converted into production-readiness claims.

## 14. Formal result and human approval

**Formal certification result:** PASS

**Formal Phase 6B closeout decision:** APPROVED

**Phase 6C readiness statement:** AUTHORIZED AFTER CERTIFICATION MERGE AND
`origin/main` SYNCHRONIZATION

### 14.1 Accountable human certification decision

- certification identifier: `POE-STOR-PHASE-6B-CERT`;
- decision: `PASS`;
- Phase 6B closeout: `APPROVED`;
- decision basis: successful Controlled Certification Attempt 2, independent
  evidence verification, passing regression and quality gates, complete
  traceability, and verified negative-authority boundaries;
- decision authority: accountable repository owner / human certifier;
- decision date: `2026-07-31`;
- effect: Phase 6B is approved for formal closeout and certification-package
  integration; and
- limitation: this decision certifies the Phase 6B software governance boundary,
  not a real production preservation baseline, representative restore readiness,
  migration readiness, cleanup authority, or full Phase 6 operational readiness.

This decision makes no digital-signature, authentication, identity-provider, or
non-repudiation claim.

### 14.2 Formal closeout effect

Human approval establishes the Phase 6B certification result as PASS and Phase 6B
functional work as complete for the certified scope. Supersession execution remains
an approved deferral rather than an implicit capability.

The decision grants no authority for migration, NAS consolidation, redirection,
cleanup, deletion, source restructuring, production-baseline acceptance, or any
other destructive or later-phase operation. It authorizes preparation for committing
and publishing the completed certification package only after separate explicit
commit approval, and integration only after separate explicit merge approval.

Phase 6C architecture discovery may begin only after the certification package is
merged into `main`, `origin/main` is synchronized, and the repository is clean.
Phase 6C has not begun.

Required human approvals:

| Approval | Status |
| --- | --- |
| Certification architecture | APPROVED |
| Exact proposed harness and execution | Attempt 1 failed; Attempt 2 approved and executed once |
| Controlled evidence and completed record | APPROVED |
| Commit and feature-branch publication | PENDING |
| Integration into main | PENDING |
| Phase 6B certification and closeout | APPROVED |
| Phase 6C architecture discovery | AUTHORIZED only after approved package merge, synchronized `origin/main`, and clean repository |

No signature, authentication, or identity-provider claim is made by this table.

## Appendix A — Controlled Certification Attempt 1 exact executed source

The following is the complete exact source executed during the failed controlled
attempt. Before execution it contained 14,140 bytes and had SHA-256
`cacf44eca9428a8ab12002dd62608b26e87c7ccb6a1ea24de53b1ad924923108`.
Independent extraction of this fenced source reproduced exactly 14,140 bytes and
the same SHA-256 before temporary-file cleanup.

```python
"""Proposed controlled Phase 6B certification harness; synthetic data only."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models import (
    STORAGE_INVENTORY_SCHEMA_VERSION,
    AcceptanceConditionDisposition,
    AcceptanceMode,
    AcceptancePolicy,
    AuthorizationAuthority,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    EvidenceValidationStatus,
    PreservationBaselineIdentity,
    PreservationEvidenceReference,
    PreservationEvidenceRequirement,
    PreservationEvidenceType,
    PreservationEvidenceValidationPolicy,
    ValidatedEvidenceReference,
)
from poe_backup_orchestrator.services import (
    AcceptedPreservationBaselineConflictError,
    AcceptedPreservationBaselineConstructionError,
    AcceptedPreservationBaselinePublisher,
    EvidenceLoadStatus,
    FilesystemPreservationEvidenceLoader,
    PreservationBaselineAcceptanceEvaluator,
    PreservationBaselineAuthorizationDecisionAssembler,
    PreservationBaselineAuthorizationStore,
    PreservationBaselineComposer,
    PreservationBaselineValidationResultAssembler,
)

SOFTWARE_BASELINE = "1fbf4355a4ad1783fda988c26122715941c50eb0"
FIXED_TIME = datetime(2026, 7, 31, 12, 0, tzinfo=UTC)
SOURCE_ROOT_ID = "synthetic-source-root-001"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_restrictive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def verify_sidecar(evidence_path: Path, sidecar_path: Path) -> dict[str, object]:
    content = evidence_path.read_bytes()
    digest = sha256_bytes(content)
    expected = f"{digest}  {evidence_path.name}\n".encode("ascii")
    require(sidecar_path.read_bytes() == expected, f"invalid sidecar: {sidecar_path}")
    return {
        "filename": evidence_path.name,
        "sidecar_filename": sidecar_path.name,
        "byte_count": len(content),
        "sha256": digest,
        "sidecar_syntax": expected.decode("ascii"),
        "mode": oct(stat.S_IMODE(evidence_path.stat().st_mode)),
        "sidecar_mode": oct(stat.S_IMODE(sidecar_path.stat().st_mode)),
    }


def snapshot(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): sha256_bytes(path.read_bytes())
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def build_authorization(*, root: Path, rejected: bool = False):
    input_directory = root / ("rejected-input" if rejected else "accepted-input")
    evidence_path = input_directory / "synthetic-inventory-evidence.json"
    evidence_content = (
        b'{"baseline_id":"synthetic-baseline-001",'
        b'"schema_name":"synthetic_inventory_evidence",'
        b'"schema_version":"1.0","source_root_id":"synthetic-source-root-001"}\n'
    )
    digest = sha256_bytes(evidence_content)
    write_restrictive(evidence_path, evidence_content)
    sidecar_path = evidence_path.with_name(f"{evidence_path.name}.sha256")
    write_restrictive(sidecar_path, f"{digest}  {evidence_path.name}\n".encode("ascii"))

    reference = PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        source_root_id=SOURCE_ROOT_ID,
        schema_version="1.0",
        evidence_path=evidence_path,
        digest_path=sidecar_path,
        sha256=digest,
        byte_count=len(evidence_content),
    )
    baseline_identity = PreservationBaselineIdentity(
        schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
        baseline_id="synthetic-baseline-001",
        created_at_utc=FIXED_TIME,
        status="preservation-candidate",
        retained_until="superseded-by-explicit-governed-decision",
    )
    candidate = PreservationBaselineComposer(clock=lambda: FIXED_TIME).compose(
        baseline_identity=baseline_identity,
        source_root_ids=(SOURCE_ROOT_ID,),
        requirements=(
            PreservationEvidenceRequirement(
                source_root_id=SOURCE_ROOT_ID,
                evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            ),
        ),
        evidence_references=(reference,),
    )
    loaded = FilesystemPreservationEvidenceLoader().load(reference)
    require(loaded.status is EvidenceLoadStatus.VERIFIED, "synthetic evidence not verified")
    validated_reference = ValidatedEvidenceReference(
        evidence_reference=reference,
        status=EvidenceValidationStatus.VERIFIED,
        calculated_sha256=loaded.calculated_sha256,
        calculated_byte_count=loaded.calculated_byte_count,
        sidecar_sha256=loaded.sidecar_sha256,
        resolved_schema_name="synthetic_inventory_evidence",
        resolved_schema_version="1.0",
    )
    validation = PreservationBaselineValidationResultAssembler().assemble(
        candidate=candidate,
        validation_policy=PreservationEvidenceValidationPolicy(
            profile_id="phase-6b-certification-synthetic-v1",
            supported_schema_versions=(),
        ),
        validated_evidence=(validated_reference,),
        findings=(),
        validated_at_utc=FIXED_TIME,
    )
    recommendation = PreservationBaselineAcceptanceEvaluator().evaluate(
        validation_result=validation,
        policy=AcceptancePolicy(
            policy_id="phase-6b-certification-acceptance",
            policy_version="1.0",
            mode=AcceptanceMode.STRICT,
            rules=(),
            unmapped_finding_disposition=AcceptanceConditionDisposition.BLOCKING,
        ),
    )
    outcome = (
        AuthorizationDecisionOutcome.REJECT if rejected else AuthorizationDecisionOutcome.AUTHORIZE
    )
    scope = AuthorizationScope(
        accepted_source_root_ids=() if rejected else (SOURCE_ROOT_ID,),
        excluded_source_root_ids=(SOURCE_ROOT_ID,) if rejected else (),
        scope_limitations=("synthetic-certification-only",),
    )
    decision = PreservationBaselineAuthorizationDecisionAssembler().assemble(
        recommendation=recommendation,
        outcome=outcome,
        authority=AuthorizationAuthority(
            authority_id="synthetic-certification-reviewer",
            display_name="Synthetic Certification Reviewer",
            authority_role="certification-fixture-authority",
            authority_basis="controlled synthetic certification scenario",
            organization="POE synthetic certification",
        ),
        decided_at_utc=FIXED_TIME,
        condition_decisions=(),
        scope=scope,
        pilot=None,
        retention_obligations=("retain synthetic evidence through certification review",),
        supersession_eligible=True,
        rationale=(
            "Synthetic rejection proves the no-publication boundary."
            if rejected
            else "Synthetic authorization permits only baseline publication certification."
        ),
    )
    return decision, candidate, validation, recommendation, input_directory


def main() -> None:
    execution_root = Path(tempfile.mkdtemp(prefix="poe-phase-6b-certification-")).resolve()
    require(execution_root.parent == Path(tempfile.gettempdir()).resolve(), "unsafe root parent")
    require(execution_root.name.startswith("poe-phase-6b-certification-"), "unsafe root name")

    decision, candidate, validation, recommendation, inputs = build_authorization(
        root=execution_root
    )
    before_inputs = snapshot(inputs)
    authorization_result = PreservationBaselineAuthorizationStore().persist(
        decision=decision,
        destination_directory=execution_root / "authorization",
    )
    publisher = AcceptedPreservationBaselinePublisher()
    first = publisher.publish(
        persistence_result=authorization_result,
        destination_directory=execution_root / "publication",
    )
    publication_snapshot = snapshot(execution_root / "publication")
    replay = publisher.publish(
        persistence_result=authorization_result,
        destination_directory=execution_root / "publication",
    )
    require(not first.idempotent_replay, "first publication incorrectly marked replay")
    require(replay.idempotent_replay, "sequential publication was not verified replay")
    require(
        snapshot(execution_root / "publication") == publication_snapshot,
        "replay rewrote publication state",
    )
    loaded_baseline = publisher.load_from_reference(first.reference_artifact)
    require(
        loaded_baseline.identity.accepted_baseline_id == first.accepted_baseline_id,
        "reference load identity mismatch",
    )
    require(loaded_baseline.authorization_decision == decision, "authorization changed")
    require(loaded_baseline.accepted_source_root_ids == (SOURCE_ROOT_ID,), "scope changed")
    require(loaded_baseline.excluded_source_root_ids == (), "excluded scope changed")
    require(
        loaded_baseline.retention_obligations == decision.retention_obligations,
        "retention obligations changed",
    )
    require(loaded_baseline.supersession_eligible is True, "supersession eligibility lost")
    require(
        tuple(item.source_root_id for item in loaded_baseline.accepted_evidence_graph)
        == (SOURCE_ROOT_ID,),
        "accepted evidence graph scope mismatch",
    )

    incomplete_directory = execution_root / "incomplete-publication"
    incomplete_directory.mkdir(mode=0o700)
    (incomplete_directory / ".locks").mkdir(mode=0o700)
    incomplete_baseline = incomplete_directory / first.accepted_baseline_artifact.evidence_path.name
    shutil.copyfile(first.accepted_baseline_artifact.evidence_path, incomplete_baseline)
    os.chmod(incomplete_baseline, 0o600)
    incomplete_before = snapshot(incomplete_directory)
    incomplete_failed_closed = False
    try:
        publisher.publish(
            persistence_result=authorization_result,
            destination_directory=incomplete_directory,
        )
    except AcceptedPreservationBaselineConflictError:
        incomplete_failed_closed = True
    require(incomplete_failed_closed, "incomplete publication did not fail closed")
    require(snapshot(incomplete_directory) == incomplete_before, "incomplete state changed")

    rejected, _, _, _, rejected_inputs = build_authorization(root=execution_root, rejected=True)
    rejected_before = snapshot(rejected_inputs)
    rejected_result = PreservationBaselineAuthorizationStore().persist(
        decision=rejected,
        destination_directory=execution_root / "rejected-authorization",
    )
    rejected_destination = execution_root / "rejected-publication"
    rejection_failed_closed = False
    try:
        publisher.publish(
            persistence_result=rejected_result,
            destination_directory=rejected_destination,
        )
    except AcceptedPreservationBaselineConstructionError:
        rejection_failed_closed = True
    require(rejection_failed_closed, "rejected authorization did not fail closed")
    require(not rejected_destination.exists(), "rejected authorization created publication state")
    require(snapshot(inputs) == before_inputs, "accepted synthetic inputs changed")
    require(snapshot(rejected_inputs) == rejected_before, "rejected synthetic inputs changed")

    artifacts = {
        "authorization": verify_sidecar(
            authorization_result.artifact.evidence_path,
            authorization_result.artifact.sha256_path,
        ),
        "accepted_baseline": verify_sidecar(
            first.accepted_baseline_artifact.evidence_path,
            first.accepted_baseline_artifact.sha256_path,
        ),
        "accepted_baseline_reference": verify_sidecar(
            first.reference_artifact.evidence_path,
            first.reference_artifact.sha256_path,
        ),
    }
    require(
        all(
            item["mode"] == "0o640" and item["sidecar_mode"] == "0o640"
            for item in artifacts.values()
        ),
        "governed artifact permissions not restrictive",
    )
    evidence = {
        "schema_version": "phase-6b-certification-evidence-1.0",
        "software_baseline": SOFTWARE_BASELINE,
        "execution_root": str(execution_root),
        "identifiers": {
            "baseline_id": candidate.identity.baseline_id,
            "candidate_id": candidate.identity.candidate_id,
            "validation_id": validation.identity.validation_id,
            "evaluation_id": recommendation.identity.evaluation_id,
            "authorization_id": decision.identity.authorization_id,
            "accepted_baseline_id": first.accepted_baseline_id,
        },
        "artifacts": artifacts,
        "results": {
            "authorization_first_persistence": not authorization_result.idempotent_replay,
            "accepted_baseline_first_publication": not first.idempotent_replay,
            "accepted_baseline_exact_replay": replay.idempotent_replay,
            "downstream_reference_verification": True,
            "incomplete_publication_failed_closed": incomplete_failed_closed,
            "rejected_authorization_no_publication": rejection_failed_closed,
            "synthetic_inputs_unchanged": True,
            "supersession_eligible_preserved_without_execution": True,
            "later_authority_exercised": False,
            "destructive_operation_exercised": False,
        },
        "cleanup": {
            "authorized_exact_root_only": str(execution_root),
            "performed_by_harness": False,
        },
    }
    evidence_path = execution_root / "phase-6b-certification-evidence.json"
    write_restrictive(
        evidence_path,
        (json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode(),
    )
    print(json.dumps(evidence, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
```

## Appendix B — Controlled Certification Attempt 2 exact executed source

This is the complete exact Attempt 2 source executed once after approval. It
contains 15,446 bytes and has SHA-256
`ca28135f2a06c2b107ad00e4ccce73402fafb30d36e8ca41b08aed9fd1f4bad1`.
Independent extraction from this appendix reproduces the same byte count and
digest. This is governance evidence, not permanent executable infrastructure.

```python
"""Proposed controlled Phase 6B certification harness; synthetic data only."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.models import (
    STORAGE_INVENTORY_SCHEMA_VERSION,
    AcceptanceConditionDisposition,
    AcceptanceMode,
    AcceptancePolicy,
    AuthorizationAuthority,
    AuthorizationDecisionOutcome,
    AuthorizationScope,
    EvidenceValidationStatus,
    PreservationBaselineIdentity,
    PreservationEvidenceReference,
    PreservationEvidenceRequirement,
    PreservationEvidenceType,
    PreservationEvidenceValidationPolicy,
    ValidatedEvidenceReference,
)
from poe_backup_orchestrator.services import (
    AcceptedPreservationBaselineConflictError,
    AcceptedPreservationBaselineConstructionError,
    AcceptedPreservationBaselinePublisher,
    EvidenceLoadStatus,
    FilesystemPreservationEvidenceLoader,
    PreservationBaselineAcceptanceEvaluator,
    PreservationBaselineAuthorizationDecisionAssembler,
    PreservationBaselineAuthorizationStore,
    PreservationBaselineComposer,
    PreservationBaselineValidationResultAssembler,
)

SOFTWARE_BASELINE = "1fbf4355a4ad1783fda988c26122715941c50eb0"
FIXED_TIME = datetime(2026, 7, 31, 12, 0, tzinfo=UTC)
SOURCE_ROOT_ID = "synthetic-source-root-001"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def write_restrictive(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def verify_sidecar(evidence_path: Path, sidecar_path: Path) -> dict[str, object]:
    content = evidence_path.read_bytes()
    digest = sha256_bytes(content)
    expected = f"{digest}  {evidence_path.name}\n".encode("ascii")
    require(sidecar_path.read_bytes() == expected, f"invalid sidecar: {sidecar_path}")
    return {
        "filename": evidence_path.name,
        "sidecar_filename": sidecar_path.name,
        "byte_count": len(content),
        "sha256": digest,
        "sidecar_syntax": expected.decode("ascii"),
        "mode": oct(stat.S_IMODE(evidence_path.stat().st_mode)),
        "sidecar_mode": oct(stat.S_IMODE(sidecar_path.stat().st_mode)),
    }


def snapshot(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): sha256_bytes(path.read_bytes())
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def semantic_snapshot(directory: Path) -> dict[str, str]:
    """Snapshot semantic files while excluding locks and active temporary infrastructure."""

    return {
        str(path.relative_to(directory)): sha256_bytes(path.read_bytes())
        for path in sorted(directory.rglob("*"))
        if path.is_file()
        and ".locks" not in path.relative_to(directory).parts
        and not path.name.startswith(".")
    }


def build_authorization(*, root: Path, rejected: bool = False):
    input_directory = root / ("rejected-input" if rejected else "accepted-input")
    evidence_path = input_directory / "synthetic-inventory-evidence.json"
    evidence_content = (
        b'{"baseline_id":"synthetic-baseline-001",'
        b'"schema_name":"synthetic_inventory_evidence",'
        b'"schema_version":"1.0","source_root_id":"synthetic-source-root-001"}\n'
    )
    digest = sha256_bytes(evidence_content)
    write_restrictive(evidence_path, evidence_content)
    sidecar_path = evidence_path.with_name(f"{evidence_path.name}.sha256")
    write_restrictive(sidecar_path, f"{digest}  {evidence_path.name}\n".encode("ascii"))

    reference = PreservationEvidenceReference(
        evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
        source_root_id=SOURCE_ROOT_ID,
        schema_version="1.0",
        evidence_path=evidence_path,
        digest_path=sidecar_path,
        sha256=digest,
        byte_count=len(evidence_content),
    )
    baseline_identity = PreservationBaselineIdentity(
        schema_version=STORAGE_INVENTORY_SCHEMA_VERSION,
        baseline_id="synthetic-baseline-001",
        created_at_utc=FIXED_TIME,
        status="preservation-candidate",
        retained_until="superseded-by-explicit-governed-decision",
    )
    candidate = PreservationBaselineComposer(clock=lambda: FIXED_TIME).compose(
        baseline_identity=baseline_identity,
        source_root_ids=(SOURCE_ROOT_ID,),
        requirements=(
            PreservationEvidenceRequirement(
                source_root_id=SOURCE_ROOT_ID,
                evidence_type=PreservationEvidenceType.INVENTORY_EVIDENCE,
            ),
        ),
        evidence_references=(reference,),
    )
    loaded = FilesystemPreservationEvidenceLoader().load(reference)
    require(loaded.status is EvidenceLoadStatus.VERIFIED, "synthetic evidence not verified")
    validated_reference = ValidatedEvidenceReference(
        evidence_reference=reference,
        status=EvidenceValidationStatus.VERIFIED,
        calculated_sha256=loaded.calculated_sha256,
        calculated_byte_count=loaded.calculated_byte_count,
        sidecar_sha256=loaded.sidecar_sha256,
        resolved_schema_name="synthetic_inventory_evidence",
        resolved_schema_version="1.0",
    )
    validation = PreservationBaselineValidationResultAssembler().assemble(
        candidate=candidate,
        validation_policy=PreservationEvidenceValidationPolicy(
            profile_id="phase-6b-certification-synthetic-v1",
            supported_schema_versions=(),
        ),
        validated_evidence=(validated_reference,),
        findings=(),
        validated_at_utc=FIXED_TIME,
    )
    recommendation = PreservationBaselineAcceptanceEvaluator().evaluate(
        validation_result=validation,
        policy=AcceptancePolicy(
            policy_id="phase-6b-certification-acceptance",
            policy_version="1.0",
            mode=AcceptanceMode.STRICT,
            rules=(),
            unmapped_finding_disposition=AcceptanceConditionDisposition.BLOCKING,
        ),
    )
    outcome = (
        AuthorizationDecisionOutcome.REJECT if rejected else AuthorizationDecisionOutcome.AUTHORIZE
    )
    scope = AuthorizationScope(
        accepted_source_root_ids=() if rejected else (SOURCE_ROOT_ID,),
        excluded_source_root_ids=(SOURCE_ROOT_ID,) if rejected else (),
        scope_limitations=("synthetic-certification-only",),
    )
    decision = PreservationBaselineAuthorizationDecisionAssembler().assemble(
        recommendation=recommendation,
        outcome=outcome,
        authority=AuthorizationAuthority(
            authority_id="synthetic-certification-reviewer",
            display_name="Synthetic Certification Reviewer",
            authority_role="certification-fixture-authority",
            authority_basis="controlled synthetic certification scenario",
            organization="POE synthetic certification",
        ),
        decided_at_utc=FIXED_TIME,
        condition_decisions=(),
        scope=scope,
        pilot=None,
        retention_obligations=("retain synthetic evidence through certification review",),
        supersession_eligible=True,
        rationale=(
            "Synthetic rejection proves the no-publication boundary."
            if rejected
            else "Synthetic authorization permits only baseline publication certification."
        ),
    )
    return decision, candidate, validation, recommendation, input_directory


def main() -> None:
    execution_root = Path(tempfile.mkdtemp(prefix="poe-phase-6b-certification-")).resolve()
    require(execution_root.parent == Path(tempfile.gettempdir()).resolve(), "unsafe root parent")
    require(execution_root.name.startswith("poe-phase-6b-certification-"), "unsafe root name")

    decision, candidate, validation, recommendation, inputs = build_authorization(
        root=execution_root
    )
    before_inputs = snapshot(inputs)
    authorization_result = PreservationBaselineAuthorizationStore().persist(
        decision=decision,
        destination_directory=execution_root / "authorization",
    )
    publisher = AcceptedPreservationBaselinePublisher()
    first = publisher.publish(
        persistence_result=authorization_result,
        destination_directory=execution_root / "publication",
    )
    publication_snapshot = snapshot(execution_root / "publication")
    replay = publisher.publish(
        persistence_result=authorization_result,
        destination_directory=execution_root / "publication",
    )
    require(not first.idempotent_replay, "first publication incorrectly marked replay")
    require(replay.idempotent_replay, "sequential publication was not verified replay")
    require(
        snapshot(execution_root / "publication") == publication_snapshot,
        "replay rewrote publication state",
    )
    loaded_baseline = publisher.load_from_reference(first.reference_artifact)
    require(
        loaded_baseline.identity.accepted_baseline_id == first.accepted_baseline_id,
        "reference load identity mismatch",
    )
    require(loaded_baseline.authorization_decision == decision, "authorization changed")
    require(loaded_baseline.accepted_source_root_ids == (SOURCE_ROOT_ID,), "scope changed")
    require(loaded_baseline.excluded_source_root_ids == (), "excluded scope changed")
    require(
        loaded_baseline.retention_obligations == decision.retention_obligations,
        "retention obligations changed",
    )
    require(loaded_baseline.supersession_eligible is True, "supersession eligibility lost")
    require(
        tuple(item.source_root_id for item in loaded_baseline.accepted_evidence_graph)
        == (SOURCE_ROOT_ID,),
        "accepted evidence graph scope mismatch",
    )

    incomplete_directory = execution_root / "incomplete-publication"
    incomplete_directory.mkdir(mode=0o700)
    (incomplete_directory / ".locks").mkdir(mode=0o700)
    incomplete_baseline = incomplete_directory / first.accepted_baseline_artifact.evidence_path.name
    shutil.copyfile(first.accepted_baseline_artifact.evidence_path, incomplete_baseline)
    os.chmod(incomplete_baseline, 0o600)
    incomplete_missing_paths = (
        incomplete_baseline.with_name(f"{incomplete_baseline.name}.sha256"),
        incomplete_directory / first.reference_artifact.evidence_path.name,
        incomplete_directory / first.reference_artifact.sha256_path.name,
    )
    require(
        all(not path.exists() for path in incomplete_missing_paths),
        "incomplete fixture unexpectedly contains a missing final artifact",
    )
    incomplete_baseline_before = incomplete_baseline.read_bytes()
    incomplete_semantic_before = semantic_snapshot(incomplete_directory)
    incomplete_failed_closed = False
    try:
        publisher.publish(
            persistence_result=authorization_result,
            destination_directory=incomplete_directory,
        )
    except AcceptedPreservationBaselineConflictError:
        incomplete_failed_closed = True
    require(incomplete_failed_closed, "incomplete publication did not fail closed")
    require(
        incomplete_baseline.read_bytes() == incomplete_baseline_before,
        "pre-existing incomplete semantic artifact changed",
    )
    require(
        semantic_snapshot(incomplete_directory) == incomplete_semantic_before,
        "incomplete semantic publication state changed",
    )
    require(
        all(not path.exists() for path in incomplete_missing_paths),
        "publisher created a missing final semantic artifact",
    )

    rejected, _, _, _, rejected_inputs = build_authorization(root=execution_root, rejected=True)
    rejected_before = snapshot(rejected_inputs)
    rejected_result = PreservationBaselineAuthorizationStore().persist(
        decision=rejected,
        destination_directory=execution_root / "rejected-authorization",
    )
    rejected_destination = execution_root / "rejected-publication"
    rejection_failed_closed = False
    try:
        publisher.publish(
            persistence_result=rejected_result,
            destination_directory=rejected_destination,
        )
    except AcceptedPreservationBaselineConstructionError:
        rejection_failed_closed = True
    require(rejection_failed_closed, "rejected authorization did not fail closed")
    require(not rejected_destination.exists(), "rejected authorization created publication state")
    require(snapshot(inputs) == before_inputs, "accepted synthetic inputs changed")
    require(snapshot(rejected_inputs) == rejected_before, "rejected synthetic inputs changed")

    artifacts = {
        "authorization": verify_sidecar(
            authorization_result.artifact.evidence_path,
            authorization_result.artifact.sha256_path,
        ),
        "accepted_baseline": verify_sidecar(
            first.accepted_baseline_artifact.evidence_path,
            first.accepted_baseline_artifact.sha256_path,
        ),
        "accepted_baseline_reference": verify_sidecar(
            first.reference_artifact.evidence_path,
            first.reference_artifact.sha256_path,
        ),
    }
    require(
        all(
            item["mode"] == "0o640" and item["sidecar_mode"] == "0o640"
            for item in artifacts.values()
        ),
        "governed artifact permissions not restrictive",
    )
    evidence = {
        "schema_version": "phase-6b-certification-evidence-1.0",
        "software_baseline": SOFTWARE_BASELINE,
        "execution_root": str(execution_root),
        "identifiers": {
            "baseline_id": candidate.identity.baseline_id,
            "candidate_id": candidate.identity.candidate_id,
            "validation_id": validation.identity.validation_id,
            "evaluation_id": recommendation.identity.evaluation_id,
            "authorization_id": decision.identity.authorization_id,
            "accepted_baseline_id": first.accepted_baseline_id,
        },
        "artifacts": artifacts,
        "results": {
            "authorization_first_persistence": not authorization_result.idempotent_replay,
            "accepted_baseline_first_publication": not first.idempotent_replay,
            "accepted_baseline_exact_replay": replay.idempotent_replay,
            "downstream_reference_verification": True,
            "incomplete_publication_failed_closed": incomplete_failed_closed,
            "rejected_authorization_no_publication": rejection_failed_closed,
            "synthetic_inputs_unchanged": True,
            "supersession_eligible_preserved_without_execution": True,
            "later_authority_exercised": False,
            "destructive_operation_exercised": False,
        },
        "cleanup": {
            "authorized_exact_root_only": str(execution_root),
            "performed_by_harness": False,
        },
    }
    evidence_path = execution_root / "phase-6b-certification-evidence.json"
    write_restrictive(
        evidence_path,
        (json.dumps(evidence, sort_keys=True, separators=(",", ":")) + "\n").encode(),
    )
    print(json.dumps(evidence, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
```
