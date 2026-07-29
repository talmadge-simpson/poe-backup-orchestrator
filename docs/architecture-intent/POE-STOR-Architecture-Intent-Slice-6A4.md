# POE Storage Services Platform Architecture Intent — Slice 6A-4

## Discovery-to-Inventory Transformation and Deterministic Assembly

### 1. Purpose

Slice 6A-4 establishes the deterministic transformation boundary between
read-only filesystem discovery evidence and the governed storage inventory
contracts introduced in Slice 6A-1.

The slice assembles inventory evidence in memory. It does not persist an
inventory, hash file content, create a preservation copy, migrate data,
redirect clients, or remove source content.

### 2. Governing Principle

> Discovery observations become inventory evidence only through an explicit,
> deterministic, and reconciled transformation.

### 3. Assembly Context

Every assembled item inherits a governed identity context containing:

- preservation baseline identity;
- capture-session identity;
- source-device identity;
- source-volume identity;
- source-root identity.

The relative path and item type complete the item identity.

### 4. Stable Item Identifiers

Each assembled item receives a deterministic identifier calculated from:

- baseline ID;
- capture-session ID;
- source-device ID;
- source-volume ID;
- source-root ID;
- normalized relative path;
- inventory item type.

The canonical identity components are SHA-256 hashed. Repeating the same
assembly with the same governed identity produces the same item identifier.

### 5. Inventory Mapping

Regular files become pending `FileInventoryRecord` instances containing:

- source identity;
- relative path;
- observed size;
- observed modification time;
- observed permissions;
- no SHA-256 until a later content-capture slice.

Directories become pending `DirectoryInventoryRecord` instances containing:

- source identity;
- relative path;
- metadata;
- direct file and directory counts;
- descendant file and directory counts;
- descendant byte totals.

### 6. Unsupported Object Evidence

The current inventory schema has dedicated records for files and directories.
Symbolic links and other filesystem objects remain represented as explicit
unsupported-item evidence rather than being discarded or misclassified.

They retain:

- deterministic item ID;
- relative path;
- inventory item type;
- explanatory detail.

### 7. Exception Reconciliation

Discovery exceptions are grouped deterministically by stable exception code.
Each summary contains:

- category;
- count;
- up to five normalized example paths;
- sorted distinct detail evidence.

Discovery exceptions remain separate from item capture status because they can
describe traversal boundaries rather than individual inventoried objects.

### 8. Aggregate Reconciliation

`InventoryTotals` reconciles:

- directory count;
- file count;
- symbolic-link count;
- other-object count;
- total file bytes;
- pending item count.

Every newly assembled item is pending because source content hashing and
preservation capture have not occurred.

The assembly rejects any mismatch between discovered entry count and assembled
inventory totals.

### 9. Determinism

The assembly enforces:

- normalized relative paths;
- deterministic path order;
- unique relative paths;
- unique stable item identifiers;
- stable exception-category ordering;
- stable example-path ordering;
- stable exception-detail ordering.

### 10. Architectural Boundaries

This slice intentionally excludes:

- source-content hashing;
- source-content reads;
- inventory serialization;
- inventory persistence;
- baseline manifest persistence;
- preservation copy creation;
- NAS target mapping;
- migration planning;
- client redirection;
- source cleanup.

### 11. Acceptance Criteria

Slice 6A-4 is accepted when:

- failed discoveries cannot be assembled;
- source-root identity must match the assembly context;
- file and directory observations map to governed inventory records;
- source hierarchy identity is propagated without loss;
- item identifiers are stable and deterministic;
- directory counts and descendant bytes reconcile;
- unsupported objects remain explicit evidence;
- discovery exceptions are summarized deterministically;
- inventory totals reconcile all discovered objects;
- fixture content and metadata remain unchanged;
- the complete repository quality gate passes.
