# POE-STOR-MIG-001 — Preservation Baseline Standard

## 1. Standard

Every POE storage-consolidation effort must establish an immutable,
independently verifiable preservation baseline before source restructuring.

The standard applies whenever content may be:

- moved;
- renamed;
- reorganized;
- deduplicated;
- redirected;
- migrated;
- archived;
- deleted;
- replaced as authoritative.

## 2. Baseline Identity

Baseline name:

**POE Storage Consolidation Preservation Baseline**

Baseline ID format:

`POE-STOR-MIG-BASELINE-YYYYMMDD`

Baseline status:

`READ-ONLY / RETAIN UNTIL MIGRATION CLOSEOUT`

A baseline may include multiple capture sessions, but each capture session must
remain traceable to the baseline ID and source identity.

## 3. Mandatory Controls

A preservation baseline must:

- preserve original source-device identity;
- preserve original path identity;
- preserve timestamps and metadata where practical;
- inventory files and directories;
- calculate file counts and byte totals;
- calculate SHA-256 hashes;
- record exclusions;
- record inaccessible items;
- record collection errors;
- protect evidence from modification;
- support representative restore testing;
- remain retained until migration closeout;
- be reconciled against the final NAS authoritative structure.

## 4. Source Registration

Each source device must receive a stable source-device ID.

Each source volume must record:

- source-device ID;
- hostname or device name;
- operating system;
- volume label;
- volume identifier or UUID where available;
- filesystem;
- mount point or drive letter;
- capacity;
- capture timestamp;
- connectivity method;
- encryption state where known;
- accessibility result.

Each inventoried source root must receive a source-root ID.

## 5. Inventory Record

Each file inventory record should include:

- baseline ID;
- capture-session ID;
- source-device ID;
- source-volume ID;
- source-root ID;
- original relative path;
- item type;
- filename;
- extension;
- size in bytes;
- created timestamp;
- modified timestamp;
- accessed timestamp where reliable;
- owner;
- permissions or mode;
- SHA-256;
- metadata-capture status;
- content-capture status;
- exclusion or error code;
- evidence reference.

Directory records should include equivalent path and metadata context plus child
file, child directory, and byte totals where practical.

## 6. Evidence Package

The baseline evidence package must include:

- baseline manifest;
- device manifest;
- volume manifest;
- source-root manifest;
- file inventory;
- directory inventory;
- SHA-256 manifest;
- count and byte summaries;
- exclusion register;
- inaccessible-item register;
- collection-error register;
- capture logs;
- tool versions;
- configuration used;
- baseline acceptance record;
- restore-test evidence.

Evidence formats should be open, machine-readable, and human-reviewable.

Preferred formats include:

- JSON;
- JSON Lines;
- CSV;
- TOML;
- Markdown;
- plain-text SHA-256 manifests.

## 7. Immutability

After acceptance:

- baseline evidence must be read-only;
- evidence must not be edited in place;
- recalculation must produce supplemental evidence;
- corrections must be versioned;
- prior accepted versions must remain retained;
- baseline hashes must be retained independently;
- access should be limited to authorized platform administration.

## 8. Exclusions

Exclusions must never be silent.

Every exclusion must record:

- source identity;
- path or scope;
- exclusion reason;
- authorizing rule or decision;
- estimated impact where known;
- whether the item remains recoverable elsewhere;
- review status.

Examples may include:

- operating-system caches;
- recreatable application caches;
- transient package caches;
- explicitly excluded virtual-memory files;
- inaccessible encrypted content;
- unsupported filesystem objects.

## 9. Inaccessible Items

Inaccessible items must remain visible in baseline reporting.

The record must include:

- source identity;
- original path;
- observed item type;
- failure timestamp;
- error result;
- attempted collection method;
- retry result;
- escalation or disposition decision.

An inaccessible item is not considered preserved.

## 10. Verification

Baseline verification must include:

- manifest readability;
- SHA-256-manifest validation;
- file-count reconciliation;
- byte-total reconciliation;
- evidence completeness;
- source-identity completeness;
- exclusion and error review;
- representative file retrieval;
- representative restore testing.

## 11. Acceptance Gate

The preservation baseline is accepted only when:

- all declared source roots have a terminal capture status;
- inventories and summaries are generated;
- SHA-256 evidence is complete for captured regular files;
- exclusions are explicit;
- inaccessible items are explicit;
- errors are resolved or formally accepted;
- evidence integrity verification passes;
- representative restore testing passes;
- baseline status is changed to
  `READ-ONLY / RETAIN UNTIL MIGRATION CLOSEOUT`.

## 12. Retention and Release

The baseline must remain retained until all of the following are complete:

- NAS migration reconciliation;
- authoritative cutover;
- Backup Orchestrator protection;
- representative NAS restore testing;
- source cleanup acceptance;
- final Phase 6 certification.

Baseline release or archival requires an explicit migration-closeout decision.
