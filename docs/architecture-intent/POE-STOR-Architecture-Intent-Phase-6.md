# POE Storage Services Platform Architecture Intent — Phase 6

## Storage Consolidation, NAS Centralization, and Governed Migration

### 1. Purpose

Phase 6 establishes the governed transition from a distributed, device-centered
storage environment to a NAS-centered authoritative storage platform.

The phase covers discovery, preservation, classification, migration,
reconciliation, client redirection, source cleanup, and operational
certification across the POE network.

Phase 6 architecture may be designed and implemented incrementally, but no
source data may be moved, renamed, deduplicated, redirected, reorganized, or
deleted until the preservation prerequisites defined in this architecture have
been satisfied.

### 2. Governing Principle

> We do not restructure the only copy of anything.

This principle applies to every file, directory, dataset, project, repository,
document collection, media collection, synchronized folder, and external-drive
content set within Phase 6 scope.

No transformation is authorized until an independently verifiable preservation
baseline exists.

### 3. Target Operating Model

The target operating model is:

- the NAS is the authoritative storage platform for governed POE information;
- Windows, macOS, Raspberry Pi, and future devices operate primarily as clients
  of NAS-hosted authoritative information;
- future documents, projects, source code, media, archives, and governed files
  originate on the NAS or are redirected to governed NAS locations;
- local device storage is limited to operating-system files, applications,
  caches, explicitly approved working replicas, and controlled offline copies;
- the Backup Orchestrator protects the authoritative NAS storage;
- backup, restore, retention, verification, and recovery controls are applied to
  the authoritative NAS information architecture;
- source-device copies are retained until migration reconciliation,
  representative restore testing, and Phase 6 acceptance are complete.

### 4. Scope

Phase 6 includes the following source and target domains:

- Windows desktop;
- Windows laptop;
- MacBook;
- Raspberry Pi;
- NAS;
- attached and detached external drives;
- relevant cloud-synchronized folders;
- application-managed file stores that contain user-governed information;
- source-code repositories and working directories;
- document, media, archive, export, and project collections.

Logical scope includes:

- documents;
- projects;
- source code;
- configuration;
- reports;
- media;
- images;
- archives;
- exports;
- application data suitable for file-level migration;
- synchronized cloud content;
- historical and inactive content;
- duplicate and near-duplicate candidates;
- inaccessible or excluded content requiring explicit disposition.

### 5. Out of Scope Until Explicitly Authorized

The following activities are prohibited during architecture and discovery:

- deleting source files;
- moving the only copy of any file;
- renaming source directories;
- deduplicating content;
- changing authoritative paths;
- redirecting user folders;
- repointing applications;
- replacing source repositories;
- modifying cloud synchronization roots;
- cleaning local devices;
- disposing of external drives;
- altering live NAS authoritative structures beyond approved Phase 6 staging
  and evidence locations.

### 6. Preservation-First Architecture

Before migration begins, Phase 6 must create the:

**POE Storage Consolidation Preservation Baseline**

Baseline identity format:

`POE-STOR-MIG-BASELINE-YYYYMMDD`

Required status:

`READ-ONLY / RETAIN UNTIL MIGRATION CLOSEOUT`

The preservation baseline must represent the distributed environment before
structural transformation.

It must preserve or record, where practical:

- source-device identity;
- source volume identity;
- original absolute or device-relative path;
- filename;
- directory hierarchy;
- file size;
- created, modified, and accessed timestamps;
- ownership and permissions;
- filesystem metadata;
- extended attributes;
- alternate data streams where applicable;
- symbolic-link or junction identity;
- file type;
- SHA-256;
- inventory status;
- accessibility result;
- exclusion reason;
- capture result;
- baseline evidence location.

### 7. Preservation Baseline Control Plane

The preservation baseline must include:

- source-device registry;
- source-volume registry;
- source-root declarations;
- inventory manifests;
- file counts;
- directory counts;
- byte totals;
- SHA-256 manifests;
- metadata manifests;
- exclusions;
- inaccessible-item records;
- collection errors;
- capture logs;
- baseline summary;
- baseline acceptance record;
- representative restore-test results.

The baseline must be immutable after acceptance. Corrections require a new
version or formally linked supplemental evidence; existing accepted evidence
must not be overwritten.

### 8. Source Identity Model

Every inventoried item must remain attributable to its original context.

Minimum identity hierarchy:

1. baseline ID;
2. source device ID;
3. source volume ID;
4. source root ID;
5. original relative path;
6. item identity and SHA-256.

The target NAS path must never replace or obscure original-source identity in
the migration evidence.

### 9. Information Classification

Before final target placement, content must be classified according to:

- information domain;
- business or personal purpose;
- authoritative status;
- lifecycle state;
- sensitivity;
- retention requirement;
- recovery priority;
- indexing eligibility;
- external-AI eligibility;
- active, reference, archive, quarantine, or disposition state;
- project or system affiliation;
- ownership;
- duplicate relationship.

Classification may be automated or assisted, but authoritative classification
decisions must remain reviewable and evidenced.

### 10. NAS Target Architecture

The NAS target architecture must separate:

- authoritative active information;
- project workspaces;
- source-code repositories;
- media;
- reference information;
- archives;
- incoming and migration staging;
- quarantine;
- exports;
- application data;
- restore-test locations;
- platform reports and logs;
- preservation baselines.

Target paths must be governed by stable naming, ownership, permissions,
retention, backup policy, and recovery priority.

No target directory becomes authoritative merely because data was copied into
it. Authority is established only after reconciliation and cutover acceptance.

### 11. Controlled Migration Model

Migration must operate as a controlled copy-and-verify process.

For each migration unit:

1. identify the accepted preservation-baseline source;
2. identify the approved NAS target;
3. copy without modifying the accepted source;
4. preserve metadata where practical;
5. create a target inventory;
6. calculate target SHA-256 values;
7. reconcile source and target file counts;
8. reconcile source and target byte totals;
9. reconcile source and target hashes;
10. record exceptions;
11. resolve or formally accept exceptions;
12. perform representative restore testing;
13. approve the migration unit;
14. authorize client redirection separately.

Migration tools must not default to destructive synchronization.

### 12. Duplicate Handling

Duplicate discovery is permitted before cleanup. Duplicate deletion is not.

Duplicate candidates must be classified as:

- exact duplicate;
- probable duplicate;
- version relationship;
- derivative;
- format conversion;
- independent authoritative copy;
- unresolved.

Exact hash equality alone does not authorize deletion. Retention, provenance,
path meaning, project context, and authoritative status must be considered.

Disposition requires a governed decision record.

### 13. Client Redirection and Cutover

Client redirection occurs only after the relevant migration unit has passed
reconciliation.

Cutover controls must address:

- Windows known-folder redirection or approved equivalent;
- laptop offline behavior;
- macOS folder and application behavior;
- Raspberry Pi service paths;
- source-code workspace behavior;
- application-specific storage paths;
- cloud synchronization interaction;
- NAS availability and reconnect behavior;
- permissions;
- credentials;
- network performance;
- rollback to the prior client path.

A client cutover must be reversible until accepted.

### 14. Backup Orchestrator Integration

The Backup Orchestrator must protect authoritative NAS content according to
governed policy.

Before local cleanup is authorized:

- NAS authoritative locations must be registered;
- applicable backup policies must be assigned;
- at least one governed backup must complete;
- integrity verification must pass;
- representative restore testing must pass;
- recovery evidence must be retained;
- the preservation baseline must remain available independently of the new NAS
  authoritative copy.

### 15. Source Cleanup

Source cleanup is a Phase 6E activity and requires explicit authorization.

Cleanup eligibility requires:

- accepted preservation baseline;
- completed migration;
- source-to-target reconciliation;
- resolved or accepted exceptions;
- authoritative NAS cutover;
- successful NAS backup;
- representative restore test;
- client validation;
- rollback window completion;
- cleanup approval record.

Cleanup must be staged and evidenced. Immediate irreversible deletion is
prohibited.

### 16. Phase Acceptance

Phase 6 is accepted only when:

- all in-scope sources are inventoried or explicitly excluded;
- the preservation baseline is complete and accepted;
- NAS target architecture is approved;
- migration units are reconciled;
- authoritative paths are established;
- clients are redirected and validated;
- Backup Orchestrator protection is operational;
- representative restore tests pass;
- source cleanup is approved and evidenced;
- final distributed-to-NAS reconciliation passes;
- operational documentation is complete;
- Phase 6 certification result is `PASS`.

### 17. Architectural Decision

Phase 6 is authorized to proceed through discovery, architecture, inventory
design, and preservation-baseline implementation.

No migration or cleanup is authorized by this architecture document alone.
Those activities require the acceptance gates defined for the applicable Phase
6 increment.
