# POE Storage Services Platform Phase 6 Roadmap

## 1. Phase Objective

Centralize governed information on the NAS while preserving the complete
pre-migration distributed environment and maintaining a recoverable path
throughout the transformation.

## 2. Governing Rule

> We do not restructure the only copy of anything.

## 3. Phase 6A — Discovery, Inventory, and Preservation Baseline

### Objectives

- register all in-scope source devices, volumes, and source roots;
- identify cloud-synchronized and application-managed storage;
- define exclusions explicitly;
- build inventory and hashing tools;
- capture the distributed environment;
- create and accept the immutable preservation baseline;
- perform representative baseline restore tests.

### Deliverables

- source-device catalog;
- source-volume catalog;
- source-root catalog;
- inventory schema;
- metadata-capture specification;
- SHA-256 manifest specification;
- exclusion register;
- inaccessible-item register;
- preservation-baseline implementation;
- baseline acceptance report.

### Exit Gate

No Phase 6B target-placement decision may rely on undocumented sources.

No Phase 6C migration may begin until the preservation baseline is accepted.

## 4. Phase 6B — Information Classification and Target Architecture

### Objectives

- classify discovered information;
- distinguish authoritative, replica, archive, transient, and disposition
  candidates;
- define NAS information domains;
- establish naming and path standards;
- establish permissions and ownership;
- map backup, retention, recovery, and indexing policies;
- create source-to-target mapping.

### Deliverables

- information-classification model;
- NAS logical architecture;
- NAS physical path model;
- naming standard;
- permissions model;
- source-to-target mapping register;
- duplicate-candidate register;
- migration-wave plan;
- approved target architecture.

### Exit Gate

Every migration unit must have an approved target, ownership, authority,
retention, backup policy, and reconciliation method.

## 5. Phase 6C — Controlled Migration and Reconciliation

### Objectives

- execute non-destructive migration waves;
- preserve metadata where practical;
- calculate target hashes;
- reconcile source and target;
- record and resolve exceptions;
- validate representative files and applications;
- certify each migration unit.

### Deliverables

- migration runbooks;
- migration manifests;
- target inventories;
- reconciliation reports;
- exception records;
- migration-unit acceptance records;
- representative restore-test evidence.

### Exit Gate

No client path may be redirected until the applicable migration unit is
reconciled and accepted.

## 6. Phase 6D — Client Redirection and NAS Authoritative Cutover

### Objectives

- redirect future file creation to governed NAS paths;
- configure client mounts and reconnect behavior;
- update application storage paths;
- validate Windows, macOS, and Raspberry Pi workflows;
- control offline-copy behavior;
- establish authoritative NAS status;
- validate rollback to prior client paths.

### Deliverables

- desktop cutover plan;
- laptop cutover plan;
- MacBook cutover plan;
- Raspberry Pi cutover plan;
- application-redirection register;
- client validation evidence;
- cutover acceptance report;
- rollback procedures.

### Exit Gate

NAS authoritative cutover requires operational access, correct permissions,
successful workflow testing, Backup Orchestrator protection, and an accepted
rollback path.

## 7. Phase 6E — Source Cleanup, Acceptance, and Operational Certification

### Objectives

- identify source-cleanup candidates;
- obtain explicit cleanup authorization;
- stage cleanup;
- verify NAS authoritative copies and backups;
- execute approved local cleanup;
- reconcile the final environment;
- certify the Storage Services Platform operating model.

### Deliverables

- cleanup-eligibility register;
- disposition decisions;
- cleanup runbooks;
- cleanup evidence;
- final source-to-NAS reconciliation;
- operational procedures;
- Phase 6 certification report;
- updated disaster-recovery documentation.

### Exit Gate

Phase 6 closes only when the final certification result is `PASS`.

## 8. Implementation Sequence

The recommended execution sequence is:

1. freeze migration and cleanup activity;
2. approve Phase 6 architecture;
3. implement source registration and inventory schemas;
4. inventory one low-risk pilot source;
5. validate inventory and hashing controls;
6. create a pilot preservation baseline;
7. restore representative pilot items;
8. expand baseline capture to all in-scope sources;
9. accept the complete preservation baseline;
10. approve NAS target architecture;
11. migrate controlled pilot units;
12. reconcile and certify pilot units;
13. execute remaining migration waves;
14. redirect clients in controlled order;
15. establish NAS authority;
16. verify Backup Orchestrator protection;
17. authorize staged source cleanup;
18. perform final reconciliation and certification.

## 9. Initial Source Workstreams

Initial discovery workstreams:

- Windows desktop storage;
- Windows laptop storage;
- MacBook storage;
- Raspberry Pi storage;
- current NAS content;
- external-drive content;
- cloud-synchronized folders;
- source-code repositories;
- OneNote exports or locally synchronized artifacts where applicable;
- application-specific user data.

## 10. Phase 6 Initial Backlog

The initial implementation backlog is:

- define source-device and source-volume identifiers;
- define inventory record schema;
- define baseline directory structure;
- define baseline manifest format;
- define exclusion taxonomy;
- define inaccessible-item taxonomy;
- select metadata-preserving copy methods per operating system;
- select SHA-256 collection methods;
- define safe network collection method;
- define read-only baseline controls;
- define representative restore-test protocol;
- define baseline acceptance report;
- select the Phase 6A pilot source.

## 11. Recommended Pilot

The recommended pilot should be:

- small enough to inspect manually;
- non-authoritative or independently recoverable;
- representative of real directory structure;
- inclusive of multiple file types;
- free from active application locks where practical;
- suitable for verifying path, metadata, count, byte, and hash reconciliation.

The pilot must not be used as justification to bypass the full preservation
baseline for other sources.

## 12. Program-Level Dependencies

Phase 6 depends on:

- operational NAS availability;
- Phase 5 governed restore capability;
- sufficient backup-repository capacity;
- source-device network access;
- permissions and credential availability;
- stable source identity;
- approved retention and classification decisions.

## 13. Completion Definition

Phase 6 is complete when:

- the distributed pre-migration environment remains recoverable;
- governed information is authoritative on the NAS;
- client devices operate against the NAS target model;
- the Backup Orchestrator protects authoritative storage;
- source cleanup is reconciled and evidenced;
- operational certification passes.
