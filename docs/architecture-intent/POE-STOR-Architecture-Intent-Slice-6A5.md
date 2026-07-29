# POE Storage Services Platform Architecture Intent — Slice 6A-5

## Inventory Evidence Serialization and Exclusive Persistence

### 1. Purpose

Slice 6A-5 establishes the first governed on-disk evidence boundary for the
storage-consolidation inventory assembled in Slice 6A-4.

The slice serializes deterministic inventory evidence and publishes it with a
SHA-256 sidecar. It does not hash source-file content, create preservation
copies, migrate data, redirect clients, or remove source content.

### 2. Governing Principle

> Preservation evidence must be deterministic, integrity-verifiable,
> exclusively published, and resistant to contradictory overwrite.

### 3. Evidence Format

Inventory evidence uses newline-delimited JSON.

The first record is an inventory header containing:

- evidence schema version;
- discovery-request identity;
- source-root identity;
- reconciled item count;
- aggregate inventory totals;
- deterministic discovery-exception summaries.

Each remaining record represents one assembled item.

Supported file and directory records retain:

- stable item identity;
- normalized relative path;
- inventory item type;
- complete governed inventory record.

Unsupported objects retain:

- stable item identity;
- normalized relative path;
- inventory item type;
- explicit explanatory detail.

### 4. Canonical Serialization

Every NDJSON record uses:

- sorted JSON keys;
- compact separators;
- explicit enumeration values;
- ISO 8601 timestamps;
- normalized POSIX relative paths;
- UTF-8 encoding;
- one terminal newline.

Repeated serialization of the same assembly result produces identical bytes.

### 5. Integrity Evidence

The SHA-256 digest covers the exact serialized evidence bytes.

The digest sidecar uses the stable form:

`<sha256><two spaces><evidence filename>`

The publication result records:

- evidence path;
- digest-sidecar path;
- digest;
- item count;
- byte count;
- whether publication was an idempotent replay.

### 6. Exclusive Publication

Publication uses:

- a repository-local exclusive advisory lock;
- fully written temporary files;
- file synchronization before placement;
- exclusive hard-link placement that cannot overwrite an existing path;
- parent-directory synchronization;
- restrictive file mode `0640`.

The final evidence path is never exposed as a partially written file.

### 7. Idempotency and Conflict Handling

If both evidence and digest already exist and exactly match the requested
canonical publication, the operation returns idempotent success.

Publication is rejected when:

- only one member of the evidence-and-digest pair exists;
- existing evidence bytes differ;
- the digest sidecar differs;
- another publication appears during placement;
- exclusive publication ownership cannot be acquired.

Contradictory evidence is never overwritten.

### 8. Failure Containment

If digest publication fails after new evidence placement, the newly created
evidence file is removed and the parent directory is synchronized.

Temporary files are removed after success or failure.

### 9. Architectural Boundaries

This slice intentionally excludes:

- source-file content hashing;
- source-file content reads;
- capture-status transition from pending to captured;
- baseline-manifest persistence;
- preservation-copy creation;
- NAS target mapping;
- migration planning;
- client redirection;
- source cleanup;
- command-line interfaces.

### 10. Acceptance Criteria

Slice 6A-5 is accepted when:

- serialization is deterministic and newline-delimited;
- header totals reconcile the assembly result;
- items retain deterministic relative-path order;
- supported and unsupported evidence remain explicit;
- SHA-256 covers exact serialized bytes;
- publication requires an absolute evidence path;
- evidence and sidecar are synchronized and restrictively permissioned;
- identical replay is idempotent;
- contradictory or incomplete existing evidence is rejected;
- temporary files are removed;
- source fixture content and metadata remain unchanged;
- the complete repository quality gate passes.
