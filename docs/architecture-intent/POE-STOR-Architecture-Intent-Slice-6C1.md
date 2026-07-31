# POE Storage Architecture Intent — Slice 6C-1

## Accepted-Baseline Analytical Intake and Evidence Authentication

**Document ID:** POE-STOR-Architecture-Intent-Slice-6C1

**Status:** Approved architecture; implementation in review

**System:** POE Backup Orchestrator

**Artifact class:** Product architecture artifact

**Governed subject:** Slice 6C-1 analytical intake and evidence authentication

**Phase:** 6C — Classification and Destination Design

**Parent architecture:** `POE-STOR-Architecture-Intent-Phase-6C.md`

**Predecessor:** Certified and closed Phase 6B under `POE-STOR-PHASE-6B-CERT`

**Repository baseline inspected:** `main` at
`62ad25f973622735ce7e1c2b6962058b24c3c789`

**Certified predecessor quality gate:** Ruff passing; 889 tests passing

**Implementation authorization:** Granted by explicit human approval

---

## 1. Purpose

Slice 6C-1 accepts exactly one authoritative accepted-baseline reference artifact
contract, invokes the certified Phase 6B reference-first loader, authenticates only
profile-selected evidence belonging to accepted source roots, and constructs one
immutable deterministic in-memory `AcceptedBaselineAnalysisContext`.

The slice establishes the verified analytical intake boundary for Phase 6C. It is
verification and analytical intake only. It does not classify evidence or grant
authority belonging to any later slice.

The governing preservation rule remains:

> We do not restructure the only copy of anything.

---

## 2. Governing Architecture and Engineering Kernel

This architecture is governed by:

- `AGENTS.md`;
- `POE-STOR-MIG-001-Preservation-Baseline-Standard.md`;
- the Phase 6 and Phase 6C parent architectures;
- the certified Phase 6B implementation and certification record; and
- the Engineering System ES-0 Engineering Kernel.

ES-0 supplements this product architecture by requiring:

- explicit artifact identity, lifecycle posture, governed subject, predecessor,
  and repository identity;
- separation of evidence, evaluation, architecture approval, implementation
  authorization, review, repository authority, and certification;
- deterministic inputs, outputs, ordering, and diagnostic treatment;
- visible preservation of unknown, unsupported, incomplete, and contradictory
  evidence;
- exact product/Engineering System ownership separation; and
- exact authorized repository scope.

ES-0 does not alter the approved Phase 6C technical approach. This document remains
a product-owned architecture artifact. No Engineering System document or runtime
capability becomes a dependency of the product implementation.

Architecture preparation is evidence, not approval. Approval of this architecture
will not itself grant implementation, commit, push, merge, closeout, or
certification authority.

### Architectural Design Principles

This slice consolidates the following already-governing principles:

- Architecture governs implementation.
- Evidence precedes evaluation and authority.
- Deterministic behavior is preferred over heuristic interpretation.
- Required uncertainty and contradiction remain explicit.
- Verification fails closed rather than degrading silently.
- Semantic identity is independent of implementation presentation.
- Immutable evidence is preferred over mutable operational state.
- Provenance and lineage are never collapsed.
- Transport verification is distinct from semantic meaning.
- Implementation may optimize execution but may not reinterpret the semantic
  contract.
- Passing tests provide evidence but grant no approval or authority.
- Certification precedes claims of operational readiness.
- A result from one stage grants no authority assigned to a later stage.
- We do not restructure the only copy of anything.

---

## 3. Architectural Position

```text
AcceptedPreservationBaselineArtifact
        ↓ certified reference-first verification
AcceptedPreservationBaseline
        ↓ accepted-scope and profile selection
Authenticated accepted evidence
        ↓ schema resolution and typed deserialization
Immutable analytical fact projection
        ↓ deterministic context construction
AcceptedBaselineAnalysisContext
```

Every arrow is a governed dependency, not an authority transfer.

Authentication is not deserialization. Deserialization is not fact projection.
Fact projection is not classification. Context construction is not recommendation,
approval, persistence, publication, planning, or execution.

---

## 4. Exact Slice Responsibility

Slice 6C-1 shall:

1. accept exactly one authoritative reference artifact contract;
2. call the certified Phase 6B reference-first loader before opening evidence;
3. validate Phase 6C accepted/excluded scope invariants;
4. apply one immutable constructor-supplied analytical intake profile;
5. select required evidence only from accepted-root observations;
6. retain lineage-only observations without opening their artifacts;
7. independently authenticate selected inventory and content-integrity artifacts;
8. resolve only approved evidence schemas through an immutable registry;
9. deserialize authenticated canonical evidence into immutable structures;
10. project analysis-specific semantic facts without classification judgment;
11. validate nested scope, identity, and provenance lineage;
12. construct one immutable deterministic in-memory analytical context; and
13. return that context directly.

---

## 5. Explicit Exclusions

Slice 6C-1 must not perform or expose:

- classification or classification finding generation;
- ownership, stewardship, retention, sensitivity, lifecycle, recovery, indexing,
  information-domain, logical-collection, or destination recommendation;
- duplicate or equivalence analysis;
- canonical-copy recommendation;
- logical target design;
- physical NAS path recommendation;
- persistence or publication;
- cache or replay state;
- locking or cross-process coordination;
- human approval;
- migration-unit, dependency, wave, runbook, or plan construction;
- preservation or migration execution;
- directory, reservation-file, or share creation;
- NAS mutation;
- client or application redirection;
- cleanup authorization or execution;
- deletion, deduplication, relocation, renaming, or source mutation;
- preservation-retention release;
- supersession records or execution;
- live source-content access;
- external AI or LLM processing;
- network, cloud, database, notification, identity-provider, authentication,
  digital-signature, or other external integration; or
- Phase 6 operational-readiness claims.

---

## 6. Public Entry Contract

The public method accepts exactly one:

```python
AcceptedPreservationBaselineArtifact
```

The artifact represents the authoritative accepted-baseline reference JSON and its
SHA-256 sidecar. It is a locator and expected-value contract, not a preverified
semantic result.

No request wrapper is approved. There is no additional per-call semantic input that
would justify one.

The public method must not accept:

- `AcceptedPreservationBaselineReference`;
- `AcceptedPreservationBaseline`;
- a full-baseline path or artifact;
- caller-supplied baseline, authorization, evaluation, validation, or candidate IDs;
- caller-supplied digests, byte counts, scope, or lineage;
- separately supplied evidence paths or references;
- candidate, validation, acceptance, authorization, or persistence models;
- a per-call profile;
- a per-call adapter registry; or
- live source-content paths.

Exact input-type validation is mandatory. Duck-typed mappings, path strings, or
generic dictionaries are prohibited.

---

## 7. Certified Reference-First Loading

Slice 6C-1 shall reuse exactly:

```python
AcceptedPreservationBaselinePublisher.load_from_reference(
    reference_artifact: AcceptedPreservationBaselineArtifact,
) -> AcceptedPreservationBaseline
```

This call must complete successfully before Slice 6C-1 opens any referenced
evidence artifact.

Phase 6B continues to own:

- reference artifact and sidecar path validation;
- `lstat()`-based regular-file and symbolic-link checks;
- exact reference byte-count and SHA-256 verification;
- exact lowercase two-space reference sidecar and final newline;
- strict reference decoding and rejection of unknown, missing, duplicate, or
  incorrectly typed fields;
- canonical reference-byte verification;
- deterministic full-baseline filename and path derivation;
- full-baseline artifact and sidecar verification;
- canonical accepted-baseline decoding;
- accepted-baseline/reference identity, mode, and scope agreement; and
- complete accepted-baseline model validation.

Slice 6C-1 must not duplicate, weaken, reinterpret, repair, or normalize those
behaviors. It must not reserialize or rehash the accepted baseline merely to repeat
certified verification.

After the certified load, Slice 6C-1 may check only its analytical boundary:

- accepted and excluded source-root sets are disjoint;
- every selected observation belongs to an accepted root;
- no excluded-root observation enters selected evidence;
- every accepted root satisfies the approved profile;
- reference root, evidence type, and schema agree with the observation and profile;
- inventory and content-integrity facts agree with accepted lineage; and
- no nested fact leaks excluded scope.

An `AcceptedPreservationBaselineError` from the certified loader must become
`AcceptedBaselineReferenceVerificationError` with its causal chain preserved:

```python
raise AcceptedBaselineReferenceVerificationError(message) from exc
```

No evidence path may be opened after reference-first loading fails.

---

## 8. Analytical Intake Profile

Slice 6C-1 introduces a public immutable semantic profile rather than runtime
configuration.

Approved profile contracts are:

- `STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION`;
- `AcceptedBaselineAnalysisProfileIdentity`;
- `AcceptedBaselineAnalysisEvidenceRequirement`;
- `AcceptedBaselineAnalysisEvidenceRule`;
- `AcceptedBaselineAnalysisProfile`; and
- `stable_accepted_baseline_analysis_profile_id`.

The profile identity format is:

```text
pbaip-<64 lowercase hexadecimal characters>
```

The profile defines:

- profile schema version;
- profile version;
- canonically ordered evidence rules;
- required or lineage-only disposition;
- evidence type;
- supported schema name and version;
- fact-projection semantic identity;
- adapter-registry semantic identity;
- missing-evidence behavior;
- unsupported-evidence behavior;
- inventory and content-integrity per-artifact byte ceilings;
- inventory and content-integrity per-root item ceilings;
- aggregate context byte and projected-item ceilings;
- inventory NDJSON per-record byte ceiling;
- the explicit initial fixed-schema JSON-depth policy; and
- deterministic ordering requirements.

The profile is frozen, slotted, hashable, and part of context semantics. It grants
no classification, recommendation, approval, or later authority.

Profile construction must reject:

- empty rules;
- duplicate evidence types;
- duplicate schema registrations;
- contradictory dispositions;
- unsupported requirement values;
- missing, zero, negative, or otherwise invalid limits;
- noncanonical rule order;
- empty profile version;
- empty adapter-registry identity; and
- empty fact-projection identity.

One repository-default profile shall eventually be constructed in code. No file,
environment variable, CLI option, or external configuration is introduced.

---

## 9. Initial Evidence Dispositions

Required for every accepted source root:

- `PreservationEvidenceType.INVENTORY_EVIDENCE`;
- `PreservationEvidenceType.CONTENT_INTEGRITY_EVIDENCE`.

Lineage-only initially:

- `BASELINE_MANIFEST`;
- `DISCOVERY_RESULT`;
- `CONTENT_CAPTURE_RESULT`;
- `EXCEPTION_EVIDENCE`;
- `RECONCILIATION_EVIDENCE`.

There is no optional analytical evidence type in the initial profile.

Lineage-only observations remain explicit and auditable but their artifacts are not
opened. `CONTENT_CAPTURE_RESULT` is metadata and grants no authority to open captured
source content or paths carried by that metadata.

---

## 10. Resource-Limit Evidence and Decision

### 10.1 Repository observations

Repository inspection establishes:

- inventory evidence is canonical UTF-8 NDJSON with one header and one fully
  materialized JSON record per inventory item;
- content-integrity evidence is one canonical UTF-8 JSON document containing a
  fully materialized evidence array;
- both serializers materialize their complete output bytes before persistence;
- the current validation loader streams in one-mebibyte chunks for hashing but
  accumulates all chunks and joins them into one bytes object;
- JSON/JSONL deserialization and immutable freezing materialize full Python object
  graphs;
- current focused tests use only a handful of records and sub-kibibyte synthetic
  evidence;
- the repository contains no representative environment inventory artifacts,
  content-integrity artifacts, production-scale item counts, or recorded size
  distributions;
- repository documentation identifies Raspberry Pi as a supported platform but
  records no applicable RAM size, available-memory budget, concurrent service
  budget, or measured Python peak-resident-set behavior for this workload; and
- no current schema establishes a maximum JSON depth or maximum record length.

Authentication can hash and count bytes with bounded read buffers, but the current
deserialization and projection model still requires complete evidence and projected
facts in memory. A streaming hash limit alone is therefore insufficient to prove
safe execution.

### 10.2 Approved characterization identity

The accountable human approved one controlled synthetic characterization performed
against the following exact subject:

| Attribute | Recorded value |
|---|---|
| Repository commit | `62ad25f973622735ce7e1c2b6962058b24c3c789` |
| Host | Raspberry Pi 4 Model B Rev 1.4 |
| Machine architecture | `aarch64` |
| Kernel | `6.18.34+rpt-rpi-v8` |
| Python invocation | `/home/talmadge/poe-backup-orchestrator/.venv/bin/python` |
| Canonical interpreter | `/usr/bin/python3.13` |
| Python version | `3.13.5` |
| Physical RAM | 8,198,590,464 bytes |
| Swap | 2,147,479,552 bytes, zram-backed |
| Harness byte count | 24,233 bytes |
| Harness SHA-256 | `d03a247025568a658cda07aad7e99c424b62d4b061602eec46ede79ddbdf66a2` |
| Report SHA-256 | `f38bbfb2f248765e2ac07561182fc0f126aca3ac370a3c9e2e02bbe2db2d72cb` |
| Executions | Exactly one |
| Completed scales | 100, 1,000, 5,000, 10,000, 25,000, and 50,000 items per evidence artifact |
| Result | Every scale succeeded; process exit code 0 |

The measured envelopes were:

| Items per artifact | Inventory bytes | Integrity bytes | Aggregate bytes | Absolute peak RSS | Incremental peak RSS |
|---:|---:|---:|---:|---:|---:|
| 25,000 | 20,253,856 | 20,084,566 | 40,338,422 | 721,530,880 | 545,570,816 |
| 50,000 | 40,511,407 | 40,189,593 | 80,701,000 | 1,416,085,504 | 1,106,079,744 |

At the 50,000-item scale, final available memory was approximately 3.30 GiB, the
largest canonical inventory NDJSON record was 1,647 bytes including its final
newline, and the fixed content-integrity JSON schema had measured depth 4.

The temporary harness, report, and synthetic artifacts were removed after evidence
capture. The procedure read or modified no production evidence, live source content,
or repository content.

### 10.3 Initial Accepted-Baseline Analysis Resource Profile v1.0

The stable semantic resource-profile version is:

```text
poe.storage.baseline-analysis.resource-profile/1.0
```

The architecture governs which resource controls must exist, which fields are
semantic, their deterministic enforcement order, fail-closed behavior, identity
participation, change control, and the measurement, review, and human approval needed
for future profiles. The resource profile supplies the numerical values for one
approved deployment and implementation envelope.

The initial immutable profile limits are:

| Profile field | Approved value | Scope |
|---|---:|---|
| Maximum inventory-evidence bytes | 40,000,000 bytes | Per artifact |
| Maximum content-integrity-evidence bytes | 40,000,000 bytes | Per artifact |
| Maximum inventory items | 25,000 | Per accepted root |
| Maximum content-integrity observations | 25,000 | Per accepted root |
| Maximum aggregate evidence bytes | 80,000,000 bytes | Per analytical context |
| Maximum aggregate projected items | 50,000 | Per analytical context |
| Maximum canonical inventory NDJSON record | 1,647 bytes, including exactly one final newline | Per record |
| Configurable JSON nesting-depth limit | None | Initial fixed, strictly typed schemas |

These values are not timeless universal architectural maxima. They are the approved
initial deployment and implementation envelope. The complete resource-profile
version and every value are immutable semantic fields of the approved
`AcceptedBaselineAnalysisProfile` contract and participate in `pbaip` identity. A
change to any value or enforcement semantic creates a different profile identity;
decreasing a limit changes identity just as increasing one does. Increasing a limit
also requires new characterization evidence, architecture review, and explicit human
approval.

Implementations must not substitute local values through configuration, environment
variables, CLI parameters, undocumented constants, a separate profile loader, or a
database record. An accepted baseline may be processed only under an explicitly
identified approved profile. A context created under one profile must never be
represented as though it were created under another profile.

A violation fails closed with
`AcceptedBaselineEvidenceAuthenticationError`; no partial context is returned and no
value is silently truncated, skipped, sampled, or downgraded. No new public module,
configuration surface, or runtime profile-loading mechanism is introduced.

The 1,647-byte record limit is the maximum exact canonical inventory record exercised
by the approved characterization. It is a deliberately strict first-envelope limit
with no inferred, unmeasured headroom. The count includes the final newline and is
checked before UTF-8 or JSON decoding. Legitimate future evidence above the limit
fails closed. A larger value requires targeted record-length characterization and
approved architecture refinement.

The fixed content-integrity schema measured JSON depth 4. Artifact bytes and item
counts are bounded before parsing, and strict typed deserialization rejects
incompatible structures. No separately configurable depth ceiling is introduced for
the initial fixed schemas. Extensible or caller-defined schemas require a new
architecture decision before use.

### 10.4 Deterministic enforcement order

The service enforces budgets in this exact order:

1. validate the declared reference byte count against the evidence-type artifact
   ceiling before opening the artifact;
2. validate that accepting the declared artifact cannot exceed the aggregate context
   byte budget;
3. authenticate through bounded streaming reads;
4. stop before retaining bytes beyond the applicable artifact or aggregate ceiling;
5. for inventory NDJSON, enforce the per-record byte ceiling before UTF-8 and JSON
   decoding of that record;
6. count typed inventory items and content-integrity observations during
   deserialization or projection;
7. fail before adding an item that exceeds its per-root or aggregate count limit; and
8. return a context only after every required artifact and aggregate budget check
   succeeds.

No stage may silently omit a record or return partial semantic state.

### 10.5 Measurement rationale and limitations

The approved ceilings remain within the successfully measured envelope while using
the 25,000-item result as the conservative per-root item boundary. The independent
artifact and aggregate byte ceilings remain below the successfully exercised
50,000-item sizes and 80,701,000-byte aggregate. The approved aggregate item limit is
half the 100,000 combined records exercised at the largest scale.

The characterization used deterministic synthetic evidence rather than production
evidence. Its immediate repeated context-like aggregate reused immutable tuples and
did not represent a second complete filesystem reload and deserialization. Python
allocator retention accumulated across sequential scales, and future evidence-size
distributions may differ. The approved ceilings therefore intentionally fail closed
outside the measured envelope; a larger envelope requires new characterization
evidence. These limitations do not block initial implementation under the approved
conservative limits.

---

## 11. Evidence Selection

The verified accepted baseline contains:

```python
accepted_evidence_graph: tuple[EvidenceRequirementObservation, ...]
```

Candidate observation statuses are exactly:

- `PRESENT`;
- `ABSENT`;
- `NOT_APPLICABLE`.

Authentication failures and unsupported schemas are not candidate statuses and
must not be injected into the candidate model.

Selection requires:

- accepted and excluded root sets are disjoint;
- selected evidence belongs only to accepted roots;
- no selected evidence belongs to an excluded root;
- exactly one observation exists for every required
  `(source_root_id, evidence_type)` key;
- every required observation is `PRESENT`;
- every selected `PRESENT` observation has exactly one matching reference;
- observation and reference source root, evidence type, and schema agree;
- duplicate keys fail;
- selected observations use canonical order
  `(source_root_id, evidence_type.value)`;
- lineage-only observations remain explicit but unopened; and
- no observation is silently dropped.

A missing required observation or required `ABSENT` or `NOT_APPLICABLE` observation
fails construction. Unknown evidence enum values must fail during certified strict
accepted-baseline decoding or explicit profile evaluation.

---

## 12. Strict Complete-Context Rule

A valid `AcceptedBaselineAnalysisContext` exists only when every required evidence
artifact for every accepted root is:

- present;
- independently authenticated;
- schema-supported;
- canonically deserialized;
- successfully projected;
- within approved resource limits;
- scope-consistent; and
- lineage-consistent.

No valid partial context is permitted when required evidence is missing, failed,
unsupported, malformed, over limit, or contradictory. No permissive intake mode or
silent fallback exists.

Lineage-only `ABSENT` and `NOT_APPLICABLE` observations remain explicit without
invalidating an otherwise complete context.

A failed construction returns no context. A failure must never be converted into
absence, lineage-only status, or fabricated facts.

---

## 13. Private Evidence Authenticator

`FilesystemPreservationEvidenceLoader` must not be reused unchanged because it:

- uses `stat()`-style behavior that follows symbolic links;
- accepts broadly permissive sidecar forms;
- strips sidecar whitespace rather than enforcing exact producer syntax and final
  newline; and
- accumulates complete evidence without profile-governed limits.

A narrow private authenticator shall reside only in:

```text
src/poe_backup_orchestrator/services/storage_baseline_analysis.py
```

It consumes only selected `PreservationEvidenceReference` objects originating from
the verified accepted baseline. It must:

1. require absolute evidence and sidecar paths;
2. use `lstat()` to reject symbolic links and non-regular files;
3. use `O_NOFOLLOW` where supported;
4. compare pathname and opened-descriptor device/inode identity;
5. perform descriptor-level `fstat()` verification;
6. stream evidence in bounded chunks for hashing and counting;
7. enforce the approved profile byte limit before and during reading;
8. verify exact expected byte count and lowercase SHA-256;
9. authenticate the sidecar independently through the same path controls;
10. verify the exact producer-specific sidecar bytes;
11. compare before/after descriptor size and stable metadata where practical;
12. detect replacement or mutation during authentication where practical;
13. provide immutable authenticated bytes and operational metadata to typed
    deserialization; and
14. mutate, repair, normalize, replace, or rewrite nothing.

The authenticator is private. This slice does not introduce a reusable generic
authentication framework.

---

## 14. Producer-Specific Sidecars

The slice preserves existing certified producer formats without retroactive rewrite.

Inventory evidence requires exact ASCII bytes:

```text
<64 lowercase hexadecimal characters><two spaces><exact evidence filename>\n
```

Content-integrity evidence requires exact ASCII bytes:

```text
<64 lowercase hexadecimal characters>\n
```

Uppercase hexadecimal, missing newline, extra newline, extra line, leading or
trailing whitespace, incorrect separator, incorrect filename where applicable,
incorrect digest, or non-ASCII content fails authentication.

The inventory sidecar path must be the inventory evidence filename with `.sha256`
appended, as required by its certified publication contract. Content-integrity
evidence must use the exact digest path already carried by its accepted reference;
the current certified producer uses `content-integrity-evidence.sha256` rather than
appending `.sha256` to the JSON filename.

No common sidecar format is imposed retroactively.

---

## 15. Hard-Link Policy

Evidence must not fail solely because `st_nlink` is greater than one. A hard-linked
regular file may be legitimate immutable evidence.

Controls remain:

- `lstat()` regular-file verification;
- symbolic-link rejection;
- `O_NOFOLLOW` where supported;
- descriptor-level `fstat()`;
- pathname/descriptor device-and-inode agreement;
- exact byte count and SHA-256;
- canonical-format verification; and
- before/after descriptor stability checks where practical.

Link count is recorded as operational verification metadata and excluded from
semantic identity. A link count greater than one may become a failure only under a
separately documented threat model and explicitly approved policy.

The slice must not interpret a hard link as a duplicate, alternate version,
nonauthoritative copy, or disposition candidate.

---

## 16. Authentication, Deserialization, Projection, and Context

The boundaries are:

```text
artifact authentication
≠ schema resolution
≠ typed deserialization
≠ analytical fact projection
≠ context construction
≠ classification
≠ recommendation
≠ approval
```

Slice 6C-1 may reuse certified behavior from:

- `InventoryEvidenceAdapter`;
- `ContentIntegrityEvidenceAdapter`;
- `ValidationAdapterRegistry`; and
- schema probing and recursively immutable JSON-freezing conventions.

Validation facts are service-layer technical-validation contracts. They must not be
exported as the public Phase 6C analytical model.

Analysis-specific projection produces `AcceptedBaselineAnalysisEvidence`, retaining:

- original accepted observation;
- requirement disposition;
- authentication status;
- resolved schema name and version;
- evidence semantic identity;
- fact-projection identity;
- recursively immutable semantic facts;
- exact source-root and item provenance; and
- operational verification metadata.

The context must not retain raw mutable JSON, open streams, file handles, adapter
objects, registry instances, service instances, or mutable buffers.

Validation results and findings remain predecessor lineage. Slice 6C-1 must not
reevaluate them or promote them into classification facts.

Adapters and projectors must not normalize or rewrite source IDs, source-root IDs,
relative paths, hashes, capture identities, item identities, outcomes, provenance,
or unsupported semantic values. Structural canonicalization into deterministic
immutable tuples is permitted.

---

## 17. Semantic Behavior Identities

The profile records:

- `adapter_registry_id`; and
- `fact_projection_id`.

These identify semantic behavior, not implementation presentation. Neither identity
may derive from class names alone, Python module paths, source paths, object IDs,
memory addresses, registration order, `repr()`, or instance identity.

### Canonical Semantic Manifest Serialization

The following language-neutral byte-level algorithm is normative for every
architecture-defined semantic-manifest identity in this slice:

1. The semantic payload is the JSON object defined by the architecture.
2. JSON object keys are ordered lexically by Unicode code point.
3. Array order is preserved exactly as defined by the normative architecture
   payload.
4. Strings are encoded as UTF-8.
5. Non-ASCII characters are emitted directly rather than ASCII-escaped.
6. Serialization uses a comma between array elements and object members, a colon
   between each object key and value, and no additional whitespace.
7. JSON booleans, nulls, strings, and integers use their canonical JSON
   representations.
8. Floating-point values are prohibited unless a future architecture defines an
   exact canonical representation.
9. No byte-order mark is present.
10. No leading or trailing whitespace is present.
11. No final newline is present.
12. SHA-256 is calculated over the exact serialized bytes.
13. The identity is recorded as 64 lowercase hexadecimal characters.
14. Implementations must independently reproduce the architecture-recorded digest
    before using the manifest.
15. A digest mismatch is an architectural-conformance failure and fails closed.

Normative language-neutral expression:

```text
canonical_bytes =
    UTF8(
        JSON(
            semantic_payload,
            object_keys=lexical_unicode_order,
            arrays=architecture_defined_order,
            separators=(",", ":"),
            ensure_ascii=false,
            trailing_newline=false
        )
    )

semantic_behavior_id =
    lowercase_hex(SHA256(canonical_bytes))
```

A language runtime's serializer, including Python `json.dumps`, is only a conforming
implementation when it reproduces these exact bytes; no language API is the
normative contract. The architecture-recorded identities remain:

```text
adapter_registry_id: f8d9caf9c32ff3da38b901efb001faf4f31cd131a567f2e2acfc0abaf06825d2
fact_projection_id: 00c4f0f475908c11ebc8f42aec8d4b4dd9b39f5fdfa3dbcd56fdde4feebfdaec
```

### 17.1 Adapter-registry manifest

The initial adapter-registry manifest schema is
`poe.storage.baseline-analysis.adapter-registry/1.0`. The following JSON is the
complete normative manifest. Its object keys are serialized lexically; its
`registrations` are ordered by `(evidence_type, schema_name, schema_version)`:

```json
{
  "manifest_schema_version": "poe.storage.baseline-analysis.adapter-registry/1.0",
  "registrations": [
    {
      "canonical_bytes_required": true,
      "evidence_type": "content_integrity_evidence",
      "parse_contract_id": "poe.storage.content-integrity-evidence.typed-parse/1.0",
      "schema_name": "poe.storage.content-integrity-evidence",
      "schema_version": "1.0",
      "sidecar_rule_id": "poe.storage.content-integrity-evidence.sidecar/lowercase-digest-final-newline/1.0",
      "strict_schema_resolution": true
    },
    {
      "canonical_bytes_required": true,
      "evidence_type": "inventory_evidence",
      "parse_contract_id": "poe.storage.inventory-evidence.typed-parse/1.0",
      "schema_name": "poe.storage.inventory-evidence",
      "schema_version": "1.0",
      "sidecar_rule_id": "poe.storage.inventory-evidence.sidecar/lowercase-digest-two-spaces-exact-filename-final-newline/1.0",
      "strict_schema_resolution": true
    }
  ]
}
```

Lowercase SHA-256 over the compact canonical UTF-8 serialization of that exact
payload produces:

```text
adapter_registry_id: f8d9caf9c32ff3da38b901efb001faf4f31cd131a567f2e2acfc0abaf06825d2
```

### 17.2 Fact-projection manifest

The initial projection manifest schema is
`poe.storage.baseline-analysis.fact-projection/1.0`. The following JSON is the
complete normative manifest. Field paths name the entire approved semantic
projection; an implementation may not add, omit, rename, or reinterpret a projected
field without changing this manifest and identity.

```json
{
  "duplicate_key_rules": [
    "duplicate canonical object key fails",
    "duplicate integrity item_id fails",
    "duplicate integrity relative_path fails",
    "duplicate inventory item_id fails",
    "duplicate inventory relative_path fails"
  ],
  "evidence_projections": [
    {
      "evidence_type": "content_integrity_evidence",
      "field_paths": [
        "evidence[].detail",
        "evidence[].expected_sha256",
        "evidence[].expected_size_bytes",
        "evidence[].failure_code",
        "evidence[].item_id",
        "evidence[].observed_sha256",
        "evidence[].observed_size_bytes",
        "evidence[].outcome",
        "evidence[].relative_path",
        "evidence[].schema_version",
        "evidence[].source_observation_after.device_id",
        "evidence[].source_observation_after.inode",
        "evidence[].source_observation_after.mode",
        "evidence[].source_observation_after.modified_at_ns",
        "evidence[].source_observation_after.size_bytes",
        "evidence[].source_observation_before.device_id",
        "evidence[].source_observation_before.inode",
        "evidence[].source_observation_before.mode",
        "evidence[].source_observation_before.modified_at_ns",
        "evidence[].source_observation_before.size_bytes",
        "evidence[].verification_completed_at_utc",
        "evidence[].verification_started_at_utc",
        "schema_version",
        "source_root_id",
        "totals.candidate_file_count",
        "totals.digest_mismatch_count",
        "totals.filesystem_error_count",
        "totals.inaccessible_count",
        "totals.missing_count",
        "totals.not_regular_file_count",
        "totals.size_mismatch_count",
        "totals.source_changed_count",
        "totals.total_expected_bytes",
        "totals.total_observed_bytes",
        "totals.verified_count",
        "verification_completed_at_utc",
        "verification_started_at_utc"
      ],
      "schema_name": "poe.storage.content-integrity-evidence",
      "schema_version": "1.0"
    },
    {
      "evidence_type": "inventory_evidence",
      "field_paths": [
        "header.discovery_request_id",
        "header.exception_summaries[].category",
        "header.exception_summaries[].count",
        "header.exception_summaries[].detail",
        "header.exception_summaries[].example_paths[]",
        "header.item_count",
        "header.record_kind",
        "header.schema_version",
        "header.source_root_id",
        "header.totals.captured_count",
        "header.totals.directory_count",
        "header.totals.error_count",
        "header.totals.excluded_count",
        "header.totals.file_count",
        "header.totals.inaccessible_count",
        "header.totals.junction_count",
        "header.totals.other_item_count",
        "header.totals.pending_count",
        "header.totals.symbolic_link_count",
        "header.totals.total_file_bytes",
        "records[].detail",
        "records[].item_id",
        "records[].item_type",
        "records[].record.capture_status",
        "records[].record.captured_at_utc",
        "records[].record.descendant_directory_count",
        "records[].record.descendant_file_count",
        "records[].record.descendant_size_bytes",
        "records[].record.direct_directory_count",
        "records[].record.direct_file_count",
        "records[].record.error_detail",
        "records[].record.exclusion_reason",
        "records[].record.identity.baseline_id",
        "records[].record.identity.capture_session_id",
        "records[].record.identity.item_type",
        "records[].record.identity.relative_path",
        "records[].record.identity.source_device_id",
        "records[].record.identity.source_root_id",
        "records[].record.identity.source_volume_id",
        "records[].record.metadata.accessed_at_utc",
        "records[].record.metadata.created_at_utc",
        "records[].record.metadata.modified_at_utc",
        "records[].record.metadata.owner",
        "records[].record.metadata.permissions",
        "records[].record.sha256",
        "records[].record.size_bytes",
        "records[].record_kind",
        "records[].relative_path",
        "records[].support_status"
      ],
      "schema_name": "poe.storage.inventory-evidence",
      "schema_version": "1.0"
    }
  ],
  "immutable_representation_rules": {
    "arrays": "tuples preserving approved semantic order",
    "json_objects": "tuples of key-value pairs ordered by lexical key",
    "null": "None",
    "scalars": "exact JSON string, integer, boolean, or null value"
  },
  "lineage_validation_rules": [
    "authenticated evidence source_root_id equals its accepted observation and reference source_root_id",
    "content-integrity document source_root_id equals its authenticated evidence source_root_id",
    "content-integrity item_id and relative_path reconcile uniquely to inventory item_id and relative_path",
    "every supported inventory record identity.source_root_id equals the inventory header source_root_id",
    "inventory envelope item_id, item_type, and relative_path equal their nested record identity values",
    "inventory header source_root_id equals its authenticated evidence source_root_id",
    "selected evidence belongs to accepted roots and never to excluded roots"
  ],
  "manifest_schema_version": "poe.storage.baseline-analysis.fact-projection/1.0",
  "operationally_excluded_fields": [
    "artifact_descriptor_device_id",
    "artifact_descriptor_inode",
    "artifact_link_count",
    "artifact_path",
    "artifact_transport_sha256",
    "artifact_verified_byte_count",
    "authentication_host",
    "authentication_timestamp",
    "sidecar_descriptor_device_id",
    "sidecar_descriptor_inode",
    "sidecar_link_count",
    "sidecar_path",
    "sidecar_transport_sha256",
    "temporary_path"
  ],
  "ordering_rules": {
    "content_integrity_evidence": "(source_root_id, relative_path, item_id)",
    "inventory_evidence": "(source_root_id, relative_path, item_id)",
    "object_keys": "lexical Unicode code-point order",
    "projected_evidence": "(source_root_id, evidence_type, schema_name, schema_version)"
  },
  "path_representation": "exact canonical POSIX relative-path string; no normalization",
  "timestamp_representation": "exact producer-canonical ISO 8601 UTC string with explicit offset; no timezone conversion"
}
```

Lowercase SHA-256 over the compact canonical UTF-8 serialization of that exact
payload produces:

```text
fact_projection_id: 00c4f0f475908c11ebc8f42aec8d4b4dd9b39f5fdfa3dbcd56fdde4feebfdaec
```

Each behavior identity is lowercase SHA-256 over compact canonical UTF-8 JSON. A
nonsemantic refactor that preserves these manifests does not change identity. A
semantic behavior change must change its manifest and identity, which changes the
profile and context identities.

These normative payloads, version strings, and recorded digests fix the initial
behavior identities. They are architecture-defined and must not be derived
opportunistically from implementation code.

---

## 18. Public Model Surface

The minimal approved public model surface is:

- `STORAGE_BASELINE_ANALYSIS_SCHEMA_VERSION`;
- `STORAGE_BASELINE_ANALYSIS_PROFILE_SCHEMA_VERSION`;
- `AcceptedBaselineAnalysisProfileIdentity`;
- `AcceptedBaselineAnalysisEvidenceRequirement`;
- `AcceptedBaselineAnalysisEvidenceRule`;
- `AcceptedBaselineAnalysisProfile`;
- `AcceptedBaselineAnalysisEvidenceStatus`;
- `AcceptedBaselineAnalysisContextIdentity`;
- `AcceptedBaselineAnalysisEvidence`;
- `AcceptedBaselineAnalysisContext`;
- `stable_accepted_baseline_analysis_profile_id`; and
- `stable_accepted_baseline_analysis_context_id`.

Evidence requirements are:

- `REQUIRED`;
- `LINEAGE_ONLY`.

Evidence statuses in a valid context are:

- `AUTHENTICATED`;
- `LINEAGE_ONLY`.

No status may imply that failed required evidence can coexist with a valid context.

Models must be frozen, slotted, immutable, service-independent, and canonically
ordered where order is nonsemantic. Models must contain no live resources, mutable
registries, adapters, service objects, classification fields, destination fields,
approval fields, or later authority.

The slice does not add a public intake-result wrapper, raw-byte model, verified-
baseline wrapper, generic authenticator, generic registry framework, separate fact
subclasses, or lineage wrapper.

---

## 19. Public Service and Method

The public service is:

```python
AcceptedBaselineAnalysisIntakeService
```

Recommended constructor dependencies are:

- `AcceptedPreservationBaselinePublisher`;
- `AcceptedBaselineAnalysisProfile`; and
- `ValidationAdapterRegistry`.

The primary method is exactly:

```python
def build_context(
    self,
    reference_artifact: AcceptedPreservationBaselineArtifact,
) -> AcceptedBaselineAnalysisContext: ...
```

The method has exactly one public argument. Profile and registry are constructor
dependencies, not per-call inputs. Composition may inject certified concrete
dependencies for testing, but callers cannot bypass the public input boundary.

Defaults must use `dataclasses.field(default_factory=...)` or module-level immutable
constants where appropriate. Function calls must not appear directly as default
argument values.

No clock, cache, lock, persistence store, publisher for analytical output, or replay
result is required.

Every invocation freshly verifies the reference, full accepted baseline, and selected
evidence. Repeated successful invocations return equal contexts.

---

## 20. Public Output

The service returns:

```python
AcceptedBaselineAnalysisContext
```

directly.

No `AcceptedBaselineAnalysisIntakeResult` is introduced because there is no
persistence result, replay flag, publication path, execution timestamp, lock result,
or cache result.

Operational evidence-verification metadata may be nested in analytical evidence
records while remaining excluded from semantic identity where it is not semantic.

---

## 21. Profile Identity

`pbaip` identity is SHA-256 over compact canonical UTF-8 JSON with lexical object
keys and canonical rule ordering.

The semantic payload includes:

- profile schema version;
- profile version;
- ordered evidence rules;
- requirement dispositions;
- evidence types;
- schema names and versions;
- missing and unsupported behavior;
- adapter-registry semantic ID;
- fact-projection semantic ID;
- all approved byte, record, item, aggregate, and structural limits; and
- deterministic ordering rules.

Presentation metadata, class names, module paths, runtime objects, and registration
order are excluded.

---

## 22. Context Identity

The context identity format is:

```text
pbac-<64 lowercase hexadecimal characters>
```

It is SHA-256 over compact canonical UTF-8 JSON with sorted object keys and
deterministic tuple ordering.

The exact semantic payload includes:

- analysis-context schema version;
- accepted-baseline ID;
- analysis-profile ID;
- profile version;
- adapter-registry semantic ID;
- fact-projection semantic ID;
- ordered authenticated evidence records containing:
  - source-root ID;
  - evidence type;
  - original observation status;
  - resolved schema name and version;
  - evidence semantic ID;
  - complete canonical semantic facts;
- ordered lineage-only observations containing:
  - source-root ID;
  - evidence type;
  - observation status;
  - approved explanatory detail where semantic.

The context ID changes when any accepted-baseline identity, semantic profile rule,
behavior ID, schema, selected evidence semantics, projected fact, source root, or
semantic state changes. It must not be derived only from accepted-baseline ID.

---

## 23. Semantic Evidence Identity and Transport Metadata

Each authenticated evidence record has an evidence semantic identity calculated from:

- evidence semantic schema version;
- evidence type;
- resolved schema name and version;
- source-root ID;
- complete canonical projected semantic facts; and
- fact-projection identity.

Record but exclude as independent direct components of semantic identities:

- artifact path;
- sidecar path;
- transport SHA-256;
- sidecar SHA-256;
- byte count;
- load or analysis timestamp;
- host;
- temporary path;
- object or memory identity;
- link count;
- lock state; and
- persistence location.

Authenticated content still affects identity through the evidence semantic ID and
complete facts.

Noncanonical evidence bytes fail. Two accepted canonical artifacts with identical
semantic content under the same accepted-baseline and profile semantics produce the
same context identity. Changed canonical semantic content changes evidence and context
identities. Changed transport metadata alone does not change semantic identity, but
mismatched bytes, counts, digests, or sidecars fail before context construction.

---

## 24. Cardinality and Repeated Construction

The invariant is:

> For one `accepted_baseline_id` and one exact `analysis_profile_id`, there exists
> exactly one valid `analysis_context_id` and one valid
> `AcceptedBaselineAnalysisContext`.

Different separately approved profiles may produce different contexts for the same
accepted baseline. The profile identity incorporates semantic adapter-registry and
fact-projection identities.

Repeated construction:

- performs fresh filesystem verification;
- is deterministic recomputation;
- returns equal objects; and
- is not persistence replay.

No `idempotent_replay`, cache, persistence, lock, cross-process coordination, or
concurrency policy is introduced. Filesystem and registry enumeration order must not
affect results.

---

## 25. Complete Lineage

The context directly retains:

- input `AcceptedPreservationBaselineArtifact`;
- verified `AcceptedPreservationBaseline`;
- `AcceptedBaselineAnalysisProfile`; and
- ordered authenticated and lineage-only evidence records.

Those contracts retain lineage to:

- accepted-baseline ID;
- accepted-baseline artifact identity available through the governed reference;
- authorization artifact digest and byte count;
- authorization ID;
- evaluation ID;
- validation ID;
- candidate ID;
- original baseline ID;
- accepted and excluded roots;
- authorization conditions;
- pilot scope and limitations;
- retention obligations;
- supersession eligibility;
- accepted evidence observations;
- validation findings as predecessor lineage;
- evidence type and schema;
- source-root ID;
- inventory identity;
- capture session;
- source device;
- source volume;
- relative path;
- item identity; and
- content-integrity outcome and totals.

Every projected fact must be attributable to exactly one authenticated evidence
record. Every authenticated evidence record must correspond to exactly one `PRESENT`
accepted observation.

Duplicated lineage is permitted only for local validation, and duplicated values must
agree exactly. Contradictory lineage fails construction. Excluded observations remain
visible through predecessor lineage but never enter the authenticated analytical
evidence tuple. No provenance may be collapsed.

---

## 26. Deterministic Ordering

Canonical order is:

- accepted and excluded roots: `source_root_id`;
- evidence records: `(source_root_id, evidence_type.value)`;
- profile rules: `(evidence_type.value, schema_name, schema_version)`;
- inventory facts: `(source_root_id, relative_path, item_id)`;
- integrity facts: `(source_root_id, relative_path, item_id)`;
- lineage references:
  `(source_root_id, evidence_type.value, schema_name, schema_version)`;
- explicit states:
  `(source_root_id, evidence_type.value, status.value, detail)`;
- object keys: lexical order.

Implementation must not depend on filesystem traversal order, external dictionary
insertion order, registry registration order, `repr()`, hash iteration order, or
memory identity.

Duplicate semantic sort keys are contradictions and fail construction.

---

## 27. Failure Taxonomy

The narrow public hierarchy is:

```text
AcceptedBaselineAnalysisIntakeError
├── AcceptedBaselineReferenceVerificationError
├── AcceptedBaselineEvidenceAuthenticationError
└── AcceptedBaselineAnalysisContextError
```

Use:

- `AcceptedBaselineReferenceVerificationError` for certified Phase 6B loading
  failures;
- `AcceptedBaselineEvidenceAuthenticationError` for selection, path, artifact,
  sidecar, size, digest, resource-limit, schema, adapter, projection, scope, and
  lineage failures; and
- `AcceptedBaselineAnalysisContextError` for semantic identity or final context
  assembly failures.

Profile model construction raises `ValueError` at the model boundary. Service
construction may wrap invalid injected profiles only where necessary to preserve the
public service boundary.

All translated failures preserve their causal exceptions with `raise ... from exc`.
The service fails fast in deterministic evidence order. Error messages must not expose
evidence payload contents. Paths may appear only when necessary to identify the
governed artifact. Finer diagnostic categories may remain private and stable.

---

## 28. Security and Path Controls

Slice 6C-1 requires:

- exact public input type;
- absolute governed artifact paths;
- evidence paths originating only in accepted lineage;
- no path inference or caller substitution;
- `lstat()` symbolic-link and non-regular-file rejection;
- `O_NOFOLLOW` where supported;
- descriptor-level `fstat()`;
- pathname/descriptor device-and-inode agreement;
- bounded streaming authentication;
- approved per-artifact, per-root, and aggregate resource limits;
- exact byte-count and SHA-256 verification;
- exact producer-specific sidecar verification;
- strict UTF-8 and JSON/JSONL structure;
- canonical evidence bytes;
- deterministic failure order;
- permission failures that fail closed; and
- no network, subprocess, database, cloud, external API, or AI dependency.

No repository or NAS containment assumption is imposed beyond the exact accepted
evidence paths. Valid accepted evidence may reside outside the repository.

The service must never open inventory relative paths, source-root paths, mount points,
captured-content paths, device paths, or any live path carried inside semantic facts.

---

## 29. Negative Authority Invariants

Tests, imports, exports, signatures, and filesystem spies must prove that Slice 6C-1
cannot:

- classify content or generate classification findings;
- recommend ownership, retention, sensitivity, lifecycle, logical collections,
  destination domains, or NAS paths;
- inspect live source content;
- analyze duplicates or designate canonical copies;
- build migration units, waves, or plans;
- execute preservation or migration;
- create directories, reservation files, or shares;
- write to NAS or authoritative source storage;
- redirect clients;
- persist or publish the context;
- request or record human approval;
- authorize migration or cleanup;
- delete, relocate, rename, deduplicate, restructure, or mutate source content;
- release preservation retention;
- execute supersession; or
- call external AI or integrations.

No public model may contain classification, destination, approval, migration,
cleanup, destructive-authority, or operational-readiness fields. The public service
exposes analytical intake construction only.

---

## 30. Model Tests

Required model tests cover:

- frozen/slotted immutability;
- absence of model-to-service imports;
- exact context and profile schema versions;
- empty and malformed values;
- exact lowercase `pbaip` and `pbac` formats;
- stable profile, evidence, and context identities;
- identity sensitivity to semantic profile, schema, facts, roots, states, behavior
  IDs, limits, and accepted-baseline ID;
- exclusion of operational metadata;
- behavior-ID stability under unchanged canonical manifests;
- canonical ordering;
- duplicate rules, evidence records, and facts;
- contradictory requirements;
- exact baseline/profile/context cardinality;
- valid evidence status invariants;
- accepted-only analytical evidence;
- complete lineage agreement;
- invalid nested types; and
- absence of mutable registries, adapters, handles, streams, raw mutable payloads,
  and later authority.

---

## 31. Service Success Tests

Required service success tests cover:

- exact `AcceptedPreservationBaselineArtifact` input;
- certified `load_from_reference` called before any evidence open;
- no caller semantic substitutions;
- required evidence selection for every accepted root;
- producer-specific artifact and sidecar authentication;
- schema resolution and canonical deserialization;
- analysis-specific semantic projection;
- accepted-root filtering;
- complete context construction;
- deterministic equality across repeated calls;
- fresh verification on every invocation;
- registry-order independence;
- input and filesystem nonmutation;
- no live source-path access;
- valid hard-linked regular evidence not rejected solely for link count;
- complete accepted/excluded lineage; and
- exact preservation of conditions, pilot limits, retention obligations, and
  supersession eligibility.

---

## 32. Boundary and Failure Tests

Required tests cover:

- wrong public input type;
- representative translated Phase 6B loader failures with preserved causes;
- no evidence open after Phase 6B failure;
- accepted/excluded overlap and excluded-root leakage;
- missing required observation;
- required `ABSENT` or `NOT_APPLICABLE`;
- duplicate observation;
- missing or unreadable evidence and sidecar;
- symbolic link, directory, FIFO, and other non-regular target;
- pathname/descriptor mismatch and replacement-race detection;
- exact hard-link policy;
- malformed producer-specific sidecars;
- uppercase digest, wrong filename where applicable, wrong separator, extra line,
  missing newline, and non-ASCII sidecar;
- byte-count and SHA-256 mismatch;
- malformed UTF-8, JSON, or JSONL;
- noncanonical evidence;
- unsupported evidence type or schema;
- payload/reference schema disagreement;
- source-root, baseline, capture-session, item, or relative-path contradiction;
- ambiguous adapter registration;
- adapter parse and fact-projection failures;
- duplicate semantic fact identity;
- every approved byte, item, aggregate, record, and structural limit; and
- no partial context returned after failure.

---

## 33. Negative Authority Tests

Use spies, export inspection, import inspection, and immutable input snapshots to
prove:

- only accepted evidence paths are opened;
- no live source path is opened;
- no filesystem write method is called;
- no directory, reservation, or share is created;
- no persistence, publication, lock, cache, migration, NAS, cleanup, supersession,
  AI, network, CLI, database, configuration, or external-integration dependency
  exists;
- public models contain no later-stage fields; and
- the public service exposes analytical intake only.

---

## 34. Reliance on Certified Phase 6B Tests

Slice 6C-1 must not duplicate the exhaustive certified Phase 6B test matrices for:

- every accepted-reference sidecar mutation;
- strict accepted-reference decoding;
- full-baseline canonical decoding;
- reference/full-artifact identity and metadata conflict;
- accepted-baseline publication order;
- publication replay, lock contention, cleanup, and four-file partial states;
- authorization persistence verification; or
- accepted-baseline construction and outcome mapping.

Slice 6C-1 must include representative boundary tests proving that it invokes the
certified loader first, translates failures, preserves causes, and opens no evidence
after failure.

Evidence-artifact tests are not redundant because Slice 6C-1 adds a stricter,
producer-specific authentication boundary.

---

## 35. Exact Later Implementation Scope

The proposed implementation scope is exactly:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C1.md
src/poe_backup_orchestrator/models/storage_baseline_analysis.py
src/poe_backup_orchestrator/models/__init__.py
src/poe_backup_orchestrator/services/storage_baseline_analysis.py
src/poe_backup_orchestrator/services/__init__.py
tests/unit/test_storage_baseline_analysis_models.py
tests/unit/test_storage_baseline_analysis.py
```

No change is presumed necessary to accepted-baseline implementation, validation
implementation, persistence modules, shared utilities, CLI, bootstrap,
configuration, databases, NAS adapters, external integrations, or existing tests.

Any necessary expansion must stop implementation and return for architecture review.

---

## 36. Recommended Implementation Sequence

After resource-limit evidence, architecture refinement, architecture approval, and
explicit implementation authorization:

1. define immutable profile, rule, evidence, identity, and context models;
2. define approved semantic adapter and projection manifests and stable IDs;
3. implement stable profile, evidence, and context identity functions;
4. implement the private bounded descriptor-based authenticator;
5. compose the certified reference-first publisher;
6. reuse approved typed schema adapters after authentication;
7. implement analysis-specific semantic projection;
8. enforce resource, scope, lineage, ordering, and completeness invariants;
9. assemble and return the context;
10. add model tests;
11. add service, boundary, failure, and negative-authority tests;
12. add only approved exports;
13. run focused tests and the full quality gate;
14. verify exact worktree scope, dependency direction, and exclusions; and
15. obtain explicit human implementation approval before repository transitions.

---

## 37. Quality Gates

The full gate is:

```bash
source .venv/bin/activate
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Before commit, also run:

```bash
git diff --cached --check
```

Passing gates produces validation evidence. It does not grant architecture approval,
implementation approval, commit, push, merge, closeout, or certification authority.

---

## 38. Slice Acceptance Criteria

Slice 6C-1 implementation may be accepted only when evidence proves:

1. exactly one authoritative reference-artifact input is accepted;
2. certified reference-first loading cannot be bypassed;
3. evidence opens only after successful accepted-baseline verification;
4. only accepted referenced evidence is opened;
5. live source content is never opened;
6. inventory and content-integrity evidence are required and authenticated for every
   accepted root;
7. exact producer-specific sidecars are verified;
8. all retained observation states are explicit;
9. complete predecessor and item provenance is preserved;
10. `pbaip` identity covers all semantic profile behavior and resource limits;
11. `pbac` identity covers the complete semantic context;
12. behavior IDs are independent of class names and object identity;
13. repeated construction freshly verifies and returns equal objects;
14. transport metadata does not independently perturb semantic identity;
15. missing, over-limit, unsupported, malformed, and contradictory required evidence
    fails closed;
16. no partial required-evidence context is returned;
17. valid hard-linked regular evidence is not rejected solely for link count;
18. no classification or destination semantics exist;
19. no persistence, publication, cache, lock, or replay contract exists;
20. no later authority or unapproved integration exists;
21. all focused tests and full quality gates pass; and
22. only the approved seven files change.

Meeting these criteria does not approve the implementation or authorize a repository
transition.

---

## 39. Certification Implications

Future `POE-STOR-PHASE-6C-CERT` evidence must prove for Slice 6C-1:

- exact reference-artifact entry;
- certified reference-first loading;
- independently authenticated accepted evidence;
- accepted-root filtering;
- deterministic profile, behavior, evidence, and context identities;
- exact producer-specific sidecars;
- enforced resource limits;
- explicit lineage-only states;
- complete provenance;
- fresh deterministic repeated construction;
- no source mutation or live-content access;
- no classification or destination recommendation;
- no persistence; and
- no later authority.

This architecture does not define or authorize a certification procedure.

---

## 40. Known Discrepancies

The following remain visible without rewriting prior documents:

1. The Phase 6C parent metadata says `Proposed for architectural review`, while
   commits `d6558231bfac1e016b01e694a7201a28ef6b74f1` and
   `a4bb624f5862bea2988271d966f9fe30b3b99b4b` plus human approval establish its
   approval and integration.
2. The older roadmap assigns classification to Phase 6B and migration to Phase 6C;
   later approved and certified architecture establishes the current Phase 6C/6D/6E
   boundaries.
3. Conceptual accepted-reference wording maps to the certified public input
   `AcceptedPreservationBaselineArtifact`.
4. The older evidence loader does not satisfy the stricter Phase 6C authentication
   boundary.
5. Inventory and content-integrity producers use different certified sidecar formats.
6. Validation facts are technical service contracts, not public Phase 6C analytical
   models.
7. Accepted-baseline loading returns the full model rather than a public verified-
   load wrapper; Slice 6C-1 must not change that certified API for convenience.
8. Candidate observations cannot encode `FAILED` or `UNSUPPORTED`; those are
   authentication outcomes.
9. Phase 6A lacks a dedicated closeout record.
10. Repository tests and documentation previously lacked representative
    evidence-size and target Raspberry Pi memory measurements. The approved
    synthetic characterization recorded in Section 10 resolves the initial
    numerical intake envelope without rewriting that earlier repository state.

---

## 41. Approved Worktree Scopes

Preparation and review of this architecture was limited exactly to:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C1.md
```

The separately approved implementation scope is limited exactly to the seven files
listed in Section 37. No other product model, service, export, test, utility, CLI,
configuration, evidence execution, or later artifact is authorized.

---

## 42. Approval and Blocker Posture

**Document status:** Approved architecture; implementation in review

**Implementation authorization:** Granted by explicit human approval

Final human architecture approval and separate implementation authorization were
granted for the exact seven-file scope. Implementation is now in review and has not
been committed, published, merged, closed, or certified.

The resource-limit blocker is resolved for the initial implementation envelope by
the approved controlled synthetic characterization and Section 10 limits. The
behavior-manifest blocker is resolved by the exact normative manifests and calculated
identities in Section 17. The canonicalization contract is explicitly
language-neutral and normative, and the initial resource profile is explicitly
distinct from enduring architectural resource governance. No known architectural
blocker remains for the approved implementation review.

The architecture is approved and its implementation remains subject to human review.
No commit, push, merge, other repository transition, certification, or later product
authority has been granted.

---

## 43. Architectural Decision

Slice 6C-1 is the deterministic in-memory verification and analytical-intake boundary
between certified accepted-baseline publication and later Phase 6C classification.

It accepts exactly one `AcceptedPreservationBaselineArtifact`, reuses the certified
reference-first loader, opens only profile-required accepted evidence, authenticates
that evidence under producer-specific and descriptor-level controls, projects
immutable semantic facts, and constructs exactly one complete
`AcceptedBaselineAnalysisContext` for one accepted-baseline/profile pair.

It grants no classification, recommendation, approval, persistence, publication,
planning, migration, destination, cleanup, supersession, destructive, integration,
or operational-readiness authority.

This approved architecture governs only Slice 6C-1. Its previously identified
resource-limit and semantic-behavior-manifest blockers are resolved for the initial
envelope. The authorized implementation remains in review and grants no repository
transition or later product authority.
