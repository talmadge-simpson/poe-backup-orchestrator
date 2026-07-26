# POE Backup Orchestrator
## Architecture Intent — Slice 3F: Operational Reporting

**Status:** Approved for implementation
**Phase:** 3 — End-to-End Orchestration Pipeline
**Slice:** 3F — Operational Reporting

## 1. Purpose

Introduce deterministic operational reporting for completed Registry backup executions.

Slice 3F will transform `RegistryBackupExecutionResult` into durable, structured, operator-consumable evidence without changing orchestration decisions, service behavior, or CLI policy.

## 2. Problem Being Solved

The orchestrator now returns a complete typed result for both successful and expected failed executions. That result is currently available only in memory.

Without operational reporting:

- execution evidence is not durably recorded
- operators cannot inspect a completed run after process exit
- failure categories, retryability, and exit codes are not persisted
- accepted artifact details are not available through a stable report contract
- CLI integration would need to duplicate presentation logic
- automated monitoring and future retention processing lack a canonical report artifact

Slice 3F establishes the authoritative reporting boundary.

## 3. Scope

This slice will:

- merge Slice 3E into `main`
- create a dedicated Slice 3F feature branch
- inspect current configuration, result models, evidence models, paths, and serialization conventions
- define a stable operational report schema
- serialize successful and failed execution results
- write reports atomically
- produce a human-readable summary derived from the same report model
- preserve UTC timestamps and stable enum values
- preserve failure category, failed state, error type, message, retryability, and exit code
- preserve available completed-stage result data
- avoid fabricating unavailable component data
- return a typed report-generation result or reference suitable for later orchestration integration
- add hermetic unit tests
- keep reporting independent of CLI formatting and exit handling

## 4. Out of Scope

This slice will not:

- add or modify CLI commands
- execute the production Registry backup workflow
- add alerts, email, or messaging
- implement report retention
- compress or archive reports
- add dashboard rendering
- add filesystem integration tests against the production repository
- alter failure-mapping policy
- alter service contracts
- implement report-stage failure mapping unless an existing report exception contract already supports it
- add distributed locking

## 5. Architectural Intent

Operational reporting is a presentation and persistence concern downstream of orchestration.

The reporting layer must consume a completed `RegistryBackupExecutionResult` and must not:

- rerun any service
- reinterpret success or failure
- change execution state
- classify exceptions
- derive new orchestration policy
- inspect mutable production state to fill gaps
- parse human-readable messages to recover structured fields

One canonical structured report model must drive all serialized forms.

## 6. Report Contract

The report must contain, at minimum:

- schema name
- schema version
- job ID
- outcome
- started timestamp
- completed timestamp
- duration in milliseconds
- final state
- failure object or `null`
- warnings
- evidence references
- repository stage result or `null`
- acquisition stage result or `null`
- validation stage result or `null`
- acceptance stage result or `null`
- report generation timestamp
- application version when available from an existing authoritative source

The failure object must contain:

- category
- failed state
- error type
- message
- retryable
- exit code

## 7. Serialization Rules

The structured report should use JSON unless inspection identifies an already approved project standard.

Serialization must be:

- UTF-8
- deterministic
- stable in field naming
- based on enum values rather than Python representations
- explicit about absent values using JSON `null`
- compatible with immutable dataclasses
- free of unserializable runtime objects
- independent of object memory addresses
- safe for paths and timestamps
- terminated with a newline when written as a text artifact

UTC timestamps must be serialized in ISO 8601 form with an explicit UTC designator or offset.

## 8. File Naming and Placement

The report filename must be deterministic and safe.

Preferred pattern, subject to inspection:

```text
registry-backup-<job-id>.json
registry-backup-<job-id>.txt
```

Reports must be written beneath the configured Backup Orchestrator report root.

The reporting service must reject or normalize unsafe job identifiers according to existing `JobId` invariants rather than constructing arbitrary paths from untrusted strings.

## 9. Atomic Persistence

Report publication must be atomic.

The implementation should:

1. create the destination directory if the existing project contract permits it
2. serialize content fully
3. write to a temporary file in the destination filesystem
4. flush and synchronize when consistent with existing utilities
5. stage both report artifacts before publishing either final destination
6. publish the human-readable summary before the JSON artifact
7. treat the JSON artifact as the authoritative publication-complete marker
8. restore any prior report pair if replacement publication fails
9. remove temporary and backup files after success or handled failure
10. never leave a newly published partial report pair

The exact implementation should reuse existing filesystem utilities when available.

## 10. Human-Readable Summary

A concise text summary should be produced from the same canonical report data.

It should include:

- job identity
- outcome
- timing
- completed stages
- failure details when present
- accepted artifact destination when available
- evidence locations when available
- warnings

The summary must not become an independent source of truth.

## 11. Data Reduction and Safety

The report must not dump arbitrary object internals.

Stage results must be serialized through explicit adapters or known dataclass fields.

The implementation must avoid persisting:

- Python repr output
- callable objects
- service instances
- secrets
- environment variables
- unrelated configuration
- stack traces for expected operational failures
- transient lock objects
- file descriptors

Unknown stage result types should fail visibly during development rather than being silently converted to misleading strings.

## 12. Compatibility Requirements

The implementation must remain compatible with:

- Slice 3A execution models
- Slice 3B state machine
- Slice 3C normalized service contracts
- Slice 3D orchestrator
- Slice 3E failure mapping
- future CLI integration
- future filesystem integration tests
- future report retention and archival

No existing public model or service API may be removed.

## 13. Verification Strategy

Unit tests must verify:

- successful execution report serialization
- failed execution report serialization
- stable schema metadata
- enum values serialize correctly
- timestamps serialize correctly
- failure details are complete
- completed prior-stage results are preserved
- absent stage results serialize as `null`
- warnings and evidence serialize deterministically
- human-readable summary matches the canonical report model
- destination filenames are deterministic
- atomic publication does not expose partial final files
- write failures do not produce a false successful report result
- unsupported values fail visibly
- no production repository paths are used
- all existing tests remain green

## 14. Proposed File Structure

```text
src/poe_backup_orchestrator/
    models/
        operational_report.py
    services/
        operational_reporting.py

tests/unit/
    test_operational_reporting.py
```

The exact structure may change after inspection, but the separation between report data, serialization, persistence, orchestration, and CLI concerns must remain explicit.

## 15. Required Invariants

- orchestration result remains the authoritative source
- reporting does not alter execution outcome
- one canonical report model drives all output
- JSON output is deterministic
- missing data remains explicitly absent
- expected failure details are preserved exactly
- final report publication is atomic
- no partial final report is exposed
- report paths remain beneath the configured root
- tests remain hermetic
- Ruff and the complete test suite remain clean

## 16. Acceptance Criteria

Slice 3F is complete when:

1. Slice 3E is merged into `main`.
2. Existing reporting-related contracts and utilities have been inspected.
3. A canonical operational report model is implemented.
4. Successful and failed execution results serialize deterministically.
5. Failure details are preserved completely.
6. Available stage results are represented without fabricated data.
7. JSON report persistence is atomic.
8. A human-readable summary is generated from the same canonical model.
9. Reporting tests are hermetic and comprehensive.
10. Existing orchestration behavior remains unchanged.
11. Ruff formatting and static analysis pass.
12. All tests pass.
13. The feature branch is committed and pushed.
14. The working tree is clean.
