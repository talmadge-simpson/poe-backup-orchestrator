# POE Storage Services Platform Architecture Intent — Slice 6A-7

## Deterministic Content Integrity Evidence

### 1. Purpose

Slice 6A-7 independently verifies captured regular-file content by re-reading
source bytes in bounded chunks, recalculating SHA-256, reconciling observed size,
detecting practical indicators of concurrent source change, and persisting
deterministic integrity evidence.

### 2. Governing Principle

> Capture evidence records what was read; integrity evidence independently
> determines whether the captured claim remains verifiable.

### 3. Dependency Direction

Immutable integrity contracts reside in the model layer. Filesystem inspection,
streaming reads, hashing, and persistence reside in services. Models must not
import services. Persistence remains separate from domain modeling.

### 4. Independent Verification

The verifier consumes successful Phase 6A-6 file certifications. It does not
trust the stored digest or byte count as current source truth. Each candidate is
opened read-only, streamed in bounded chunks, and assigned a newly observed
SHA-256 and byte count.

### 5. Source-Change Detection

The verifier records `lstat` observations before and after hashing. A change in
size, nanosecond modification time, mode, device, inode, or regular-file status
is classified as source change. This is practical best-effort detection and is
not an absolute transactional filesystem guarantee.

### 6. Deterministic Outcome Precedence

Outcomes are classified in this order:

1. missing, inaccessible, or filesystem failure;
2. non-regular file;
3. source changed during verification;
4. observed size mismatch;
5. SHA-256 mismatch;
6. verified.

Each non-verified outcome carries stable machine-readable failure evidence and
human-readable detail.

### 7. Reconciliation

Every certification produces exactly one ordered integrity-evidence record.
Candidate and outcome totals must reconcile exactly. Expected and observed byte
totals are independently retained.

### 8. Persistence

Integrity evidence is serialized as canonical newline-terminated UTF-8 JSON with
stable key ordering and compact separators. Publication uses atomic replacement.
A SHA-256 sidecar independently certifies the persisted evidence artifact.

### 9. Explicit Exclusions

This slice does not implement deduplication, incremental comparison, retention,
baseline certification, authoritative preservation promotion, source mutation,
or preservation-copy creation.

### 10. Acceptance Criteria

Acceptance requires immutable contracts, independent streaming SHA-256,
captured-size verification, practical source-change detection, explicit failure
evidence, deterministic totals, atomic canonical persistence, model/service
dependency compliance, comprehensive tests, and repository-wide Ruff and pytest
success.
