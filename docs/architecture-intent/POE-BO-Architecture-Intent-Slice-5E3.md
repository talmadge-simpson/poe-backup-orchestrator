# POE Backup Orchestrator Architecture Intent — Slice 5E-3

## Durable Restore Execution Record Publication

### Purpose

Slice 5E-3 makes the successful restore execution record introduced by Slice
5E-2 durable. The slice projects the immutable in-memory
`RestoreExecutionRecord` into deterministic JSON and publishes one governed
evidence artifact for each completed restore execution.

### Scope

This slice introduces:

- deterministic JSON projection of the complete restore execution record;
- UTC timestamp and filesystem path normalization;
- a dedicated restore execution record publisher;
- atomic, durable, no-overwrite publication;
- SHA-256 publication evidence;
- idempotent handling of an already-published identical record;
- conflict rejection when an existing record path contains different content;
- cleanup of temporary publication artifacts after success or failure.

The publisher receives the final execution-record directory explicitly. The
expected production location is:

```text
<reports_root>/Backup-Orchestrator/Restore/Executions/
```

Production configuration may already define `reports_root` at the
`Backup-Orchestrator` level. Path composition therefore remains the
responsibility of the caller until CLI composition is introduced in Slice
5E-4.

### Persistence Contract

Each completed execution is published as:

```text
restore-execution-<plan_id>.json
```

The document:

- uses UTF-8 encoding;
- ends with one newline;
- is formatted with two-space indentation;
- sorts mapping keys deterministically;
- renders UTC datetimes with a `Z` suffix;
- renders `Path` values as strings;
- renders enum members by their values;
- preserves tuples and lists as JSON arrays;
- preserves nested dataclass field names.

Publication is staged in the destination directory, flushed with `fsync`, and
atomically linked into its final no-overwrite name. The destination directory
is then flushed. A pre-existing identical document is treated as an idempotent
success. A pre-existing different document is a publication conflict.

### Security and Integrity

- destination directories are created with mode `0770`;
- temporary files are created with mode `0600`;
- the final JSON artifact retains mode `0600`;
- publication evidence contains the SHA-256 digest and byte count;
- unsafe plan identifiers that could escape the target directory are rejected.

### Explicitly Deferred

This slice does not introduce:

- restore CLI commands;
- execution-history listing or search;
- retention or pruning;
- compression;
- digital signatures;
- failed or partial execution records;
- restart and recovery behavior;
- execution-record indexing;
- orchestration wiring that changes the Slice 5E-2 return contract.

### Acceptance Criteria

1. A completed execution record serializes deterministically.
2. Nested dataclasses, enums, paths, tuples, and UTC datetimes are JSON-safe.
3. Publication creates the expected execution-record path.
4. Published bytes are fully flushed before final visibility.
5. Publication never overwrites a different existing record.
6. Republishing identical bytes is idempotent.
7. Temporary files are removed after success or failure.
8. Publication evidence reports path, SHA-256 digest, and byte count.
9. The existing test suite remains green.
