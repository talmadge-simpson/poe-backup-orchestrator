# POE Storage Services Platform Architecture Intent — Slice 6A-3

## Read-Only Filesystem Discovery Contracts and Adapter Foundation

### 1. Purpose

Slice 6A-3 establishes the first executable discovery boundary for storage
consolidation. It introduces immutable discovery contracts and a local
filesystem adapter that observes source metadata without modifying source
content.

### 2. Governing Principle

> Discovery must be evidentiary, deterministic, and non-destructive.

The discovery layer may observe names, paths, object types, metadata, and
exceptions. It may not create, alter, rename, move, copy, redirect, or delete
source content.

### 3. Contracts Introduced

This slice introduces:

- `DiscoveryPolicy`;
- `FilesystemDiscoveryRequest`;
- `DiscoveredFilesystemEntry`;
- `DiscoveryException`;
- `FilesystemDiscoveryResult`;
- `FilesystemDiscoveryAdapter`;
- `LocalFilesystemDiscoveryAdapter`.

Stable enumerations classify:

- filesystem object types;
- discovery outcomes;
- discovery exception categories.

### 4. Read-Only Adapter Behavior

The local adapter uses metadata-only filesystem operations:

- existence and directory checks;
- `os.scandir`;
- non-following stat operations;
- deterministic lexical ordering;
- relative-path normalization.

The adapter never opens file content as part of discovery and does not invoke
filesystem mutation operations.

### 5. Traversal Policy

The initial policy controls:

- inclusion of hidden entries;
- symbolic-link traversal behavior;
- maximum traversal depth.

Symbolic links are recorded as objects and are not traversed by the initial
adapter. This prevents traversal outside the declared source root and avoids
cycles.

### 6. Exception Evidence

Exceptions are retained as explicit evidence rather than silently omitted.
Stable codes cover:

- missing roots;
- roots that are not directories;
- permission denial;
- filesystem errors;
- maximum-depth boundaries;
- entries that disappear during traversal.

### 7. Determinism

Discovery entries are ordered by normalized relative path. Result contracts
reject unordered or duplicate entries.

This ensures repeatable downstream serialization, comparison, reconciliation,
and manifest construction.

### 8. Architectural Boundaries

This slice intentionally excludes:

- source-file content hashing;
- detailed inventory persistence;
- platform-specific Windows volume discovery;
- SMB or network-share authentication;
- preservation copy creation;
- migration planning;
- target-path mapping;
- storage redirection;
- source cleanup.

### 9. Acceptance Criteria

Slice 6A-3 is accepted when:

- requests require absolute source roots and UTC timestamps;
- discovery policies reject invalid depth declarations;
- missing or invalid roots produce failed evidence;
- local discovery returns normalized deterministic entries;
- hidden-entry policy is enforced;
- symbolic links are not traversed;
- maximum-depth boundaries produce explicit exceptions;
- discovery leaves fixture content and metadata unchanged;
- the complete repository quality gate passes.
