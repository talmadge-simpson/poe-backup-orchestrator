# POE Backup Orchestrator Architecture Intent — Slice 5E-5

## Restore Operational Certification Harness

### 1. Purpose

Establish a repeatable, governed, non-production operational certification
environment for the POE Registry restore pipeline.

The certification harness proves that a selected governed recovery point can be
validated, restored, promoted, verified, rolled back, and evidenced without
targeting or modifying the live authoritative Registry.

### 2. Architectural Motivation

A backup capability is not operationally complete until recovery can be
demonstrated through a repeatable and auditable process. Restore certification
must therefore validate more than file extraction. It must prove:

- repository readiness;
- recovery-point eligibility and selection;
- explicit application-validation policy;
- controlled restoration into an isolated authoritative target;
- preservation of the pre-restore state;
- verification of the promoted state;
- publication of immutable execution evidence;
- cryptographic verification of the evidence package.

The certification harness converts restore behavior into an operationally
testable contract.

### 3. Certification Isolation Boundary

The harness must never target the live authoritative Registry.

All certification activity is confined to:

`/srv/poe-backup/Restore-Tests/Operational-Certification/<run-id>/`

Each certification run receives dedicated locations for:

- authoritative target;
- staging;
- rollback;
- locking;
- execution records;
- validation-policy evidence;
- generated reports.

The run identifier establishes an immutable evidence boundary for the complete
certification attempt.

### 4. Governed Certification Workflow

The certification harness must execute the following sequence:

1. Validate the managed backup repository.
2. Discover and select two distinct governed recovery points.
3. Use the older recovery point to seed an isolated authoritative target.
4. Verify the seeded target with SQLite integrity checking and SHA-256 hashing.
5. Generate and retain an explicit Registry application-validation policy.
6. Execute the newer recovery point through the certified `restore execute`
   command.
7. Capture the pre-restore authoritative target as a rollback artifact.
8. Promote the selected restore artifact into the isolated authoritative target.
9. Verify SQLite integrity after promotion.
10. Prove that the promoted target is byte-identical to the selected recovery
    artifact.
11. Prove that the rollback artifact is byte-identical to the pre-restore
    authoritative target.
12. Publish the restore execution record.
13. Publish the execution-record `.json.sha256` sidecar.
14. Verify that the sidecar matches the published execution record.
15. Emit a timestamped operational-certification report containing the result,
    evidence locations, and relevant hashes.

A failure at any mandatory gate must fail the certification run.

## Slice 5E-5A — Registry Application Validation Policy Refinement

### 5. Validation-Policy Contract

Operational certification established that the Registry application validator
supports policy-driven empty-table exceptions through
`tables_allowed_empty`, but the TOML loader and certification-policy generator
did not initially expose that model capability.

The restore validation-policy TOML contract therefore includes:

- `[policy]`
  - `id`
  - `version`
  - `tables_allowed_empty`
- `[required_columns]`
  - one governed column list for every required Registry table.

The loader must:

- reject a missing or malformed `[policy]` table;
- reject a missing or empty `[required_columns]` table;
- reject `tables_allowed_empty` when it is not a TOML array;
- default `tables_allowed_empty` to an empty collection when omitted;
- preserve the declared table names as the application-validation policy.

### 6. Allowed-Empty-Table Handling

Empty-table handling is explicit and governed.

The validator must continue to require:

- all required tables;
- all required columns;
- non-empty content for tables not explicitly exempted.

Only tables declared in `tables_allowed_empty` may pass application validation
with zero rows.

The operational-certification policy currently recognizes the following tables
as legitimately empty in the certified Registry recovery point:

- `asset_backup_requirements`
- `asset_operational_status`
- `backup_status`
- `disposition_records`
- `indexing_status`
- `projects`
- `relationships`
- `supersessions`

This declaration does not weaken structural validation. It records the accepted
operational state of tables whose absence of rows is legitimate at the time of
certification.

Reference, structural, and other required operational tables remain subject to
non-empty validation unless explicitly governed otherwise.

### 7. Governed Restore Execution

Certification must invoke the supported restore execution interface rather than
bypassing the application through direct filesystem replacement.

The governed execution must retain the established controls for:

- restore-plan identity;
- recovery-point eligibility;
- target-path authority;
- exclusive execution ownership;
- staging isolation;
- validation before promotion;
- rollback capture;
- durable execution-state recording;
- deterministic failure handling.

Successful command completion alone is insufficient. The post-promotion,
rollback, and evidence-verification gates must also pass.

### 8. Rollback Capture

Before promotion, the existing isolated authoritative target must be copied into
the run-specific rollback hierarchy.

The rollback artifact must:

- preserve the complete pre-restore target;
- pass SQLite integrity verification;
- produce a SHA-256 hash;
- match the pre-restore target hash exactly;
- remain available after successful promotion for certification evidence and
  representative rollback testing.

Rollback capture is mandatory even though the certification target is isolated.

### 9. Promotion Verification

After governed promotion, the harness must verify:

- SQLite integrity reports `ok`;
- the promoted target exists at the declared authoritative target path;
- the promoted target SHA-256 equals the selected restore artifact SHA-256.

This proves that the certified restore did not merely complete procedurally; it
produced the exact selected recovery state.

### 10. Execution-Record Publication

The restore execution record is governed evidence of the restore attempt.

Publication must:

- serialize deterministic JSON;
- use a plan-derived execution-record identity;
- write the record durably;
- publish atomically;
- detect conflicting prior publication;
- support idempotent republication of identical evidence;
- apply restrictive file permissions;
- return the record path, SHA-256, and byte count.

### 11. SHA-256 Sidecar Publication

For every published execution record:

`restore-execution-<plan-id>.json`

the publisher must also create:

`restore-execution-<plan-id>.json.sha256`

The sidecar must:

- contain the execution-record SHA-256 and filename in `sha256sum`-compatible
  form;
- be written to a temporary file;
- be flushed and synchronized;
- be atomically renamed into place;
- synchronize the containing directory before publication returns;
- remain singular during idempotent republication;
- verify successfully against the corresponding JSON execution record.

The sidecar makes the published execution evidence independently
tamper-evident.

## Slice 5E-5B — Operational Acceptance Criteria

### 12. Mandatory Acceptance Gates

Phase 5 restore operational certification is accepted only when all of the
following gates pass:

- managed repository validation passes;
- two distinct governed recovery points are available;
- the isolated authoritative target is seeded successfully;
- pre-restore SQLite integrity passes;
- the explicit validation policy is generated and retained;
- the restore plan is accepted by governed restore execution;
- staging and locking controls operate within the certification boundary;
- rollback capture completes before promotion;
- governed restore execution completes;
- post-promotion SQLite integrity passes;
- the promoted target matches the selected recovery artifact;
- the rollback artifact matches the pre-restore target;
- the execution record is published;
- the `.json.sha256` sidecar is published;
- the sidecar verifies the execution record;
- a timestamped certification report is published;
- the final certification result is `PASS`;
- the full repository quality gate passes.

### 13. Generated Evidence

Each successful certification run must retain, at minimum:

- timestamped operational-certification report;
- certification run identifier;
- selected restore recovery-point identity;
- seed recovery-point identity;
- isolated authoritative target;
- generated validation-policy TOML;
- staging and rollback locations;
- pre-restore target hash;
- selected recovery-artifact hash;
- promoted target hash;
- rollback-artifact hash;
- restore execution-record JSON;
- execution-record SHA-256;
- execution-record `.json.sha256` sidecar;
- sidecar-verification result;
- final certification result.

### 14. Architectural Constraints

The certification design is subject to the following constraints:

- The live authoritative Registry is outside the certification target boundary.
- Empty-table exceptions must be explicit; implicit exceptions are prohibited.
- The only-copy state of a target may never be overwritten without rollback
  capture.
- Promotion success must be verified by content identity, not command status
  alone.
- Execution evidence must be durably and atomically published.
- Certification evidence must remain attributable to one run identifier.
- A partial or failed run must never be represented as certified.

### 15. Future Extension Points

The certification architecture may later be extended to support:

- additional application-specific validation-policy types;
- multiple authoritative dataset classes;
- representative automated rollback execution;
- scheduled restore-certification cadence;
- certification-result registration in the POE Registry;
- remote or secondary-repository recovery validation;
- recovery-time and recovery-point objective measurement;
- Storage Services Platform-wide disaster-recovery certification.

### 16. Slice Acceptance

Slice 5E-5 is accepted when:

- the certification harness passes end to end;
- validation-policy empty-table behavior is explicit and tested;
- governed restore promotion and rollback evidence are verified;
- execution-record JSON and `.json.sha256` evidence are published and verified;
- the architecture intent, contract tests, certification report, and repository
  quality gates are complete.
