# POE Storage Services Platform Architecture Intent — Slice 6A-2

## Inventory Capture Session and Preservation Baseline Manifest

### 1. Purpose

Slice 6A-2 establishes the execution-level and publication-level contracts
surrounding the source identity and inventory records introduced by Slice
6A-1.

This slice defines how an inventory capture is scoped, summarized, reconciled,
and represented as deterministic preservation evidence.

### 2. Governing Principle

> A preservation baseline is not merely a collection of files. It is a
> certified statement of scope, provenance, completeness, exceptions, and
> integrity.

### 3. Contracts Introduced

Slice 6A-2 introduces:

- `CaptureScope`;
- `InventoryTotals`;
- `CaptureExceptionSummary`;
- `CaptureSession`;
- `PreservationBaselineManifest`.

Stable enumerations define:

- capture-session lifecycle state;
- baseline-manifest publication state.

### 4. Capture Session Semantics

A capture session declares:

- the baseline it contributes to;
- the source devices, volumes, and roots in scope;
- include and exclude patterns;
- execution timestamps;
- aggregate inventory totals;
- exception summaries;
- terminal failure evidence when applicable.

Status-specific validation prevents contradictory records. For example:

- planned sessions cannot contain execution timestamps;
- running sessions require a start timestamp;
- terminal sessions require a completion timestamp;
- completed sessions cannot contain exceptions or pending items;
- failed sessions require failure detail.

### 5. Inventory Reconciliation

`InventoryTotals` reconciles object-type totals against capture-status totals.

This guarantees that every inventoried object is accounted for as captured,
excluded, inaccessible, failed, or pending.

### 6. Manifest Composition

A preservation baseline manifest contains:

- baseline identity;
- source-device declarations;
- source-volume declarations;
- source-root declarations;
- capture-session evidence;
- the absolute path to detailed inventory evidence;
- deterministic canonical JSON;
- SHA-256 integrity evidence for certified manifests.

The manifest validates all device-volume-root relationships and all capture
scope references.

### 7. Canonical Serialization and Integrity

Canonical JSON uses:

- stable field names;
- sorted JSON keys;
- compact separators;
- explicit enumeration values;
- ISO 8601 timestamps;
- string paths;
- exclusion of the digest field from digest calculation.

A certified manifest must contain the exact SHA-256 digest calculated from its
canonical content.

### 8. Architectural Boundaries

This slice intentionally excludes:

- filesystem traversal;
- operating-system discovery adapters;
- hashing of source files;
- detailed inventory serialization;
- manifest persistence;
- command-line interfaces;
- preservation-copy creation;
- NAS target mapping;
- migration and cleanup behavior.

### 9. Acceptance Criteria

Slice 6A-2 is accepted when:

- capture scopes reject missing or duplicate source identities;
- aggregate totals reconcile item and status counts;
- capture lifecycle rules reject contradictory states;
- source hierarchy references are validated;
- canonical JSON is deterministic;
- certified manifests require a matching SHA-256 digest;
- unit tests cover valid construction and invalid-state rejection;
- the complete repository quality gate passes.
