# POE Storage Services Platform Architecture Intent — Slice 6A-1

## Source Identity and Inventory Schema

### 1. Purpose

Slice 6A-1 establishes immutable domain contracts for source identity and
preservation inventory records.

This slice does not inspect filesystems, collect inventories, copy content,
write preservation evidence, migrate data, redirect clients, or delete source
content.

### 2. Governing Principle

> We do not restructure the only copy of anything.

The source-identity model exists to preserve original context before any
storage transformation is considered.

### 3. Domain Hierarchy

The governed hierarchy is:

1. preservation baseline;
2. source device;
3. source volume;
4. source root;
5. inventory item identity;
6. file or directory inventory record.

Every inventory item remains attributable to its original device, volume,
source root, and relative path.

### 4. Contracts Introduced

Slice 6A-1 introduces:

- `SourceDevice`;
- `SourceVolume`;
- `SourceRoot`;
- `InventoryItemIdentity`;
- `InventoryMetadata`;
- `FileInventoryRecord`;
- `DirectoryInventoryRecord`;
- `PreservationBaselineIdentity`.

Stable enumerations define:

- source-device type;
- source accessibility;
- inventory item type;
- capture status.

### 5. Validation Rules

The models enforce:

- immutable values;
- UTC-aware timestamps;
- non-empty identifiers;
- whitespace-free identifiers;
- relative rather than absolute item paths;
- non-negative sizes and counts;
- lowercase normalized SHA-256;
- SHA-256 evidence for captured files;
- explicit reasons for excluded items;
- explicit error details for inaccessible or failed items;
- valid directory count relationships;
- supported schema version.

### 6. Architectural Boundaries

This slice intentionally excludes:

- operating-system discovery adapters;
- filesystem traversal;
- hashing services;
- metadata extraction;
- inventory serialization;
- baseline persistence;
- CLI commands;
- NAS target mapping;
- migration logic;
- cleanup logic.

Those capabilities must build on the accepted Slice 6A-1 contracts.

### 7. Acceptance Criteria

Slice 6A-1 is accepted when:

- all domain contracts are immutable;
- invalid state is rejected during construction;
- source relationships remain explicit;
- inventory records preserve original relative paths;
- captured files require valid SHA-256 evidence;
- excluded and inaccessible records require explicit evidence;
- unit tests cover successful construction and invalid-state rejection;
- the complete repository quality gate passes.
