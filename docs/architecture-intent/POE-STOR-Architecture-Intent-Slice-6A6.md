# POE Storage Services Platform Architecture Intent — Slice 6A-6

## Deterministic Source Content Capture and SHA-256 Certification

### 1. Purpose

Slice 6A-6 establishes governed, read-only content capture for pending regular
file inventory records. It streams source bytes in bounded chunks, calculates
SHA-256, verifies the observed byte count against discovery evidence, records
capture timestamps, and returns immutable inventory updates.

The slice does not create preservation copies, migrate data, redirect clients,
restructure the NAS, remove source content, expose a CLI, or implement restore.

### 2. Governing Principle

> Source content certification must be deterministic, bounded in memory,
> read-only, byte-reconciled, cryptographically explicit, and represented as
> immutable evidence.

### 3. Capture Input

The service accepts one absolute source-root path, one deterministic
`InventoryAssemblyResult`, one positive chunk-size policy, and one injectable
UTC clock.

Only supported regular-file records in `PENDING` state are eligible. Directory
records and unsupported-object evidence pass through unchanged.

### 4. Deterministic Ordering

Capture follows established normalized relative-path order. Returned inventory
items, certifications, and exceptions are each ordered by normalized relative
path. The service introduces no filesystem enumeration or independent ordering.

### 5. Bounded Streaming and SHA-256

Each eligible file is opened in binary read-only mode and consumed in configured
chunks. SHA-256 is updated incrementally. Complete files are never loaded into
memory. The default chunk size is one mebibyte and must remain positive.

### 6. Byte-Count Certification

Successful certification requires a regular file, a completed stream, observed
bytes equal to discovered `size_bytes`, and a normalized SHA-256 digest. A byte
mismatch prevents digest acceptance and becomes explicit terminal evidence.

### 7. Capture Timestamps

Every successful certification records UTC start and completion timestamps. The
updated file record retains the completion timestamp as `captured_at_utc`.

### 8. Immutable Inventory Transitions

The service never mutates an assembled record. Success creates a replacement
record transitioning `PENDING -> CAPTURED` with SHA-256 and `captured_at_utc`.
Failure creates a replacement transitioning to `INACCESSIBLE` or `ERROR` while
retaining stable identity, hierarchy, metadata, path, and expected size.

### 9. Explicit Exception Evidence

Stable exception codes are `file_not_found`, `permission_denied`,
`not_regular_file`, `byte_count_mismatch`, and `filesystem_error`. Each exception
retains item identity, normalized path, and non-empty detail. An item cannot be
both certified and exceptional.

### 10. Aggregate Reconciliation

Structural and source-byte totals remain unchanged. Captured, excluded,
inaccessible, error, and pending counts are recalculated. Certification and
exception counts must reconcile aggregate totals and all items must remain
accounted for.

### 11. Source Safety

The service performs only `lstat`, regular-file validation, and binary reads. It
does not write, rename, delete, copy, migrate, redirect, or intentionally alter
source metadata, and it does not follow symbolic links as regular files.

### 12. Architectural Boundaries

This slice excludes preservation copies, destination mapping, migration,
duplicate analysis, cleanup, manifest certification, replacement of previously
published pending inventory evidence, CLI behavior, restore, and NAS
restructuring.

### 13. Acceptance Criteria

Slice 6A-6 is accepted when chunking is bounded, hashes are correct, byte counts
reconcile, timestamps are UTC, transitions are immutable, exceptions are
explicit, symbolic links are not followed, ordering is deterministic, aggregate
totals reconcile, source bytes remain unchanged, and the full quality gate
passes.

## Architectural ownership correction

Inventory assembly data contracts are owned by the model layer in
`models/storage_inventory_assembly.py`. The assembly service owns transformation
behavior only. Content-capture models and services depend on these model-layer
contracts, preventing model-to-service imports and preserving the dependency
direction `models <- services`.
