# Engineering System Architecture Intent — Slice ES-7

## Lifecycle Evidence Retention and Identity

**Document ID:** `Engineering-System-Architecture-Intent-Slice-ES-7`
**Status:** Revised architecture candidate; prepared for fresh independent review
**System:** POE Engineering System
**Slice:** ES-7 — Lifecycle Evidence Retention and Identity
**Predecessor:** ES-6 — Engineering Lifecycle Standard
**Governing lifecycle:** ES-1 lifecycle state `ARCHITECTURE_IN_REVIEW`
**Current responsibility:** ES-6 `ARCHITECTURE_REVISION`
**Implementation authorization:** `WITHHELD`
**Repository authority:** Revision of this one architecture candidate only
**Later authority:** Review, approval, implementation, commit, publication,
integration, closeout, certification, and operational authority remain withheld
**Predecessor candidate SHA-256:**
`03092d4d4aadf10a779a5158ee8f987c09765262bad9eb997d27d4417e642c18`
**Revision cause:** `ES7-AR-024`; the complete legal-hold release successor
semantics are identity-bearing specification content and therefore change the
candidate identity

---

## 1. Purpose and Independently Useful Outcome

ES-7 defines the prospective normative architecture for identity-bound,
retained evidence of Engineering System lifecycle responsibilities. A conforming
record shall allow a later responsibility to verify:

- which ES-6 responsibility completed or stopped;
- the exact governed subject and governing authority;
- the repository, worktree, and artifact identity evaluated;
- the commands, bounded results, findings, decision, and residual uncertainty;
- the attributable preparer, reviewer, accountable human, or other declared role;
- the reviewer's explicit independence declaration and relevant disclosures;
- the authority granted by an attributable decision;
- the authority expressly withheld; and
- the exact predecessor evidence and next responsibility requiring separate
  authorization.

This outcome is independently useful because lifecycle completion can be audited
without depending on mutable conversation context, a filename, or an unsupported
summary. Evidence remains evidence: record completeness, a stable digest, a
passing command, or retained approval evidence shall never manufacture truth,
approval, repository authority, certification, or operational authority.

## 2. Governance, Precedence, and Relationship to ES-6

This architecture is governed, in descending precedence, by `AGENTS.md`, the
Engineering Kernel, the Engineering Lifecycle Standard, the Slice Specification
Standard, the Repository Knowledge Foundation, the Model Routing Standard where
applicable, approved Engineering System architecture, the Phase 6C-3 evidence-gap
assessment, and current repository evidence and conventions. Contradictions
remain visible and require accountable-human disposition.

ES-7 is subordinate to and complementary with ES-6. It defines the evidence
identity, admissibility, binding, retention, reconstruction, correction, and
package semantics that ES-6 requires but intentionally leaves unimplemented.
ES-7 shall not:

- change the meaning, ordering, entry criteria, exit criteria, or authority
  boundary of any ES-6 responsibility;
- make responsibility completion automatically advance ES-1 lifecycle state;
- convert evidence capture into a lifecycle transition, approval, or repository
  act;
- weaken fresh independent review or accountable-human decision requirements; or
- make ES-6 depend on executable tooling.

A later minimum implementation should include a narrowly bounded reference from
ES-6 to the subordinate evidence standard so users can find its contract. That
reference is necessary for discoverability and unambiguous normative precedence,
but it shall not alter ES-6 responsibility semantics. No ES-6 amendment is
authorized during this architecture-revision responsibility.

## 3. Architectural Scope and Non-Responsibilities

ES-7 governs:

- lifecycle evidence-record and evidence-package classes;
- the minimum evidence-record contract and admissibility rules;
- deterministic evidence-record identity and canonical serialization;
- exact governed-artifact binding across repository states;
- attributable actor roles and reviewer-independence declarations;
- contemporaneous and reconstructed evidence states;
- retention, immutability, correction, and supersession;
- negative-authority semantics;
- predecessor verification and ES-6 lifecycle integration;
- repository-authority boundaries for evidence production;
- prospective adoption and historical compatibility; and
- the smallest later normative implementation and validation boundary.

ES-7 does not implement or authorize tooling, generators, validators, templates,
schemas, persistence adapters, storage products, signing, CI enforcement,
automatic capture, model routing, session control, product behavior, migration,
redirection, cleanup, or destructive operations. It does not retain or require
secrets, credentials, hidden reasoning, or unrestricted transcripts.

## 4. Evidence Artifact Classes and Package Structure

The architecture requires three independently identified artifact classes and
an optional evidence package:

1. An **evidence record** represents exactly one ES-6 responsibility occurrence
   for one exact governed subject. It has its own deterministic identity,
   admissibility state, artifact binding, authority effect, and predecessor link.
2. An **evidence package** is a bounded manifest that may retain one or more
   evidence records and referenced payloads. It has a distinct package identity.
   Packaging shall not merge records, transfer authority between them, or make
   package order lifecycle order.
3. A **retention event record** is subordinate ES-7 evidence about exactly one
   issued lifecycle evidence record and its exact retained payload or package.
   It is not a new ES-6 responsibility and grants no authority.
4. A **deletion tombstone** is subordinate ES-7 evidence of an authorized,
   in-progress, completed, failed, or legally blocked deletion affecting an
   issued record's payload. It neither replaces the lifecycle record nor creates
   deletion authority.

One record per responsibility is mandatory. A responsibility repeated after a
finding, interruption, changed subject, or renewed authorization produces a new
record. Multiple records may share one package only when their identities and
boundaries remain independently recoverable. A package manifest shall declare
exactly these semantic fields: `schema_version`, `package_id`, `record_ids`,
`payload_references`, `package_scope`, `creation_mode`, and
`authority_neutrality`. This is the authoritative package-manifest field
contract. `record_ids` and `payload_references` use the ordering and exact
identity rules in Section 6.2; no package field grants or transfers authority.

The normative record classes are:

| Evidence class | ES-6 responsibility represented |
| --- | --- |
| Observation and assessment | `DISCOVERY_CURRENT_STATE_ASSESSMENT`, `INTERRUPTED_WORK_RECOVERY`, `BLOCKED_DISCREPANT`, `DEFERRED`, `ABANDONED`, or `SUPERSEDED` |
| Architecture preparation | `ARCHITECTURE_PREPARATION` |
| Architecture review | `ARCHITECTURE_REVIEW` |
| Architecture revision | `ARCHITECTURE_REVISION` |
| Architecture approval | `ARCHITECTURE_APPROVAL` |
| Implementation authorization | `IMPLEMENTATION_AUTHORIZATION` |
| Implementation | `IMPLEMENTATION` or `TARGETED_IMPLEMENTATION_REVISION` |
| Implementation review | `IMPLEMENTATION_REVIEW` |
| Implementation approval | `IMPLEMENTATION_APPROVAL` |
| Commit authority and result | `ARCHITECTURE_COMMIT` or `IMPLEMENTATION_COMMIT` |
| Publication authority and result | `ARCHITECTURE_PUBLICATION` or `IMPLEMENTATION_PUBLICATION` |
| Integration authority and result | Architecture or implementation integration preparation, merge creation, validation, main push, or cleanup, each as a separate record |
| Closeout | `CLOSEOUT` |
| Certification | `CERTIFICATION` |
| Operational acceptance | `OPERATIONAL_ACCEPTANCE` |

Every record shall carry an explicit closed `artifact_type` discriminator:
`LIFECYCLE_EVIDENCE_RECORD`, `RETENTION_EVENT_RECORD`, or
`DELETION_TOMBSTONE`. Packages remain manifests rather than a fourth record
branch. Subordinate artifacts never represent a thirty-third ES-6 responsibility.

## 5. Minimum Evidence-Record Contract

### 5.1 Field-status vocabulary

- `REQUIRED`: present with a valid, non-ambiguous value.
- `CONDITIONALLY_REQUIRED`: present when its declared condition applies; absence
  shall include a machine-readable non-applicability reason.
- `OPTIONAL`: may be absent without changing admissibility or identity unless
  Section 6 makes it semantic when supplied.
- `PROHIBITED`: shall not appear in a conforming record or payload.
- `DEFERRED`: outside the minimum normative implementation and not required for
  admissibility.

`UNAVAILABLE` is an explicit value, not omission. It is permitted only for fields
whose rules allow it, must include a reason code, and never means `NONE`,
`NOT_APPLICABLE`, independent, verified, or approved.

### 5.2 Candidate-field disposition

| Field | Status | Contract |
| --- | --- | --- |
| `artifact_type` | `REQUIRED` | Exactly `LIFECYCLE_EVIDENCE_RECORD` for this branch; the other Section 4 tokens select their separately defined contracts. |
| `schema_version` | `REQUIRED` | Exact supported evidence-record schema version. |
| `evidence_record_id` | `REQUIRED` | Deterministic identity computed under Section 6. |
| `lifecycle_responsibility` | `REQUIRED` | Exactly one canonical ES-6 responsibility token. |
| `lifecycle_status` | `REQUIRED` | Exact observed ES-1 lifecycle state; compatibility with the ES-6 responsibility is validated without inferring a transition. |
| `governed_subject` | `REQUIRED` | Stable subject identifier, title, class, scope, and applicable slice identity. |
| `repository_identity` | `REQUIRED` | Stable repository identifier plus repository-relative root identity; no unnecessary absolute path. |
| `branch_or_ref_context` | `CONDITIONALLY_REQUIRED` | Required when Git state or a repository transition is claimed; mutable refs include observation time and resolved commit. |
| `baseline_commit` | `CONDITIONALLY_REQUIRED` | Required for repository/worktree claims; full immutable commit. |
| `worktree_classification` | `CONDITIONALLY_REQUIRED` | Required for any uncommitted, staged, mixed, or dirty subject. |
| `artifact_path` | `CONDITIONALLY_REQUIRED` | Repository-relative path for repository artifacts; ordered list for multi-file subjects. |
| `artifact_sha256` | `CONDITIONALLY_REQUIRED` | Required for uncommitted files and external byte payloads; permitted as additional committed-content evidence. |
| `git_blob_id` | `CONDITIONALLY_REQUIRED` | Required for each committed or staged file binding; absent with reason for non-Git external evidence. |
| `accountable_human_authorization` | `REQUIRED` | Exact attributable authorization or explicit statement that none applied to an observation-only record. |
| `authorization_issuer` | `REQUIRED` | Stable accountable-human identity or `UNAVAILABLE` with the record non-admissible for an authority gate. |
| `actor_identity` | `REQUIRED` | Preparer, executor, reviewer, decision recorder, or observer identity and role. |
| `model_family_version` | `CONDITIONALLY_REQUIRED` | Required when an AI model materially prepared, reviewed, or executed and the value is available; otherwise `UNAVAILABLE` with reason. |
| `session_identity` | `CONDITIONALLY_REQUIRED` | Required when available and relevant to provenance or independence; `UNAVAILABLE` is permitted and shall limit claims. |
| `independence_declaration` | `CONDITIONALLY_REQUIRED` | Required for every responsibility requiring independent review; includes disclosures and basis. |
| `review_or_execution_scope` | `REQUIRED` | Exact inclusions, exclusions, and subject boundary. |
| `commands_and_arguments` | `CONDITIONALLY_REQUIRED` | Required when commands were executed or claimed; exact ordered argv or a bounded safe representation. |
| `command_completion_exit_status` | `CONDITIONALLY_REQUIRED` | Required per command; distinguish completed, interrupted, timed out, not run, and unknown. |
| `bounded_results` | `CONDITIONALLY_REQUIRED` | Required for claimed command or inspection outcomes; inline summary or content-addressed payload reference. |
| `findings` | `REQUIRED` | Ordered findings or an explicit empty collection; no silent omission. |
| `dispositions` | `CONDITIONALLY_REQUIRED` | Required when findings are dispositioned; attributable and linked to finding identities. |
| `residual_risks` | `REQUIRED` | Ordered risks or explicit empty collection. |
| `uncertainty` | `REQUIRED` | Ordered uncertainties or explicit empty collection; unknown remains explicit. |
| `decision` | `REQUIRED` | Bounded result for the responsibility, including incomplete, blocked, rejected, or no-decision. |
| `authority_granted` | `REQUIRED` | Duplicate-free, canonically ordered list of zero or more exact ES-6 responsibility tokens from Section 13.2; empty by default. Evidence cannot populate it absent attributable authority evidence. |
| `authority_withheld` | `REQUIRED` | Duplicate-free, canonically ordered list of exact ES-6 responsibility tokens from Section 13.2, including all adjacent and later authority not granted. |
| `decision_effect` | `REQUIRED` | Exact non-transitive effect on the governed subject. |
| `next_responsibility_requiring_authorization` | `REQUIRED` | One named next responsibility or explicit `NONE`; recommendation is non-authorizing. |
| `non_authorizing_evidence_statement` | `REQUIRED` | Exact constant string `EVIDENCE_IDENTITY_AND_RETENTION_DO_NOT_GRANT_AUTHORITY_V1`, canonically declaring that identity and retention do not create authority. |
| `start_timestamp` | `CONDITIONALLY_REQUIRED` | Required for contemporaneous execution when reliably captured; otherwise explicit unavailable state. |
| `completion_timestamp` | `REQUIRED` | Time the record was completed, not an inferred event time; reconstruction uses reconstruction time. |
| `resulting_artifact_identity` | `CONDITIONALLY_REQUIRED` | Required when the responsibility creates or changes a governed candidate or repository object. |
| `predecessor_evidence_id` | `CONDITIONALLY_REQUIRED` | Required when ES-6 entry depends on a prior responsibility; may be a non-admissible reference during prospective bootstrap. |
| `correction_or_supersession_reference` | `CONDITIONALLY_REQUIRED` | Required for corrections, replacements, or explicit supersession. |
| `payload_location` | `OPTIONAL` | Repository-relative or durable external locator with digest; mutable locator alone is insufficient. |
| `retention_class` | `REQUIRED` | Issuance-time proposed or initially assigned Section 11 class; assignment authority evidence available at issuance is distinct from a producer proposal. Later state exists only in retention events. |
| `retention_assignment_state` | `REQUIRED` | Issuance-time state only: `PROPOSED` or `ASSIGNED_PENDING_RETENTION`. Post-issuance confirmation, unavailability, expiry, and deletion shall not mutate this field. |
| `retention_assignment_authority` | `CONDITIONALLY_REQUIRED` | Required when accountable assignment exists at issuance; otherwise explicit non-applicability. Later assignment is a `RETENTION_ASSIGNED` event. |
| `retention_confirmation` | `PROHIBITED` | Post-issuance confirmation is represented only by a `RETENTION_CONFIRMED` event. |
| `evidence_origin_state` | `REQUIRED` | Exactly one Section 10 state. |
| `artifact_binding` | `REQUIRED` | Exactly one Section 8 mode and its complete deterministic binding contract. |
| credentials, secrets, hidden reasoning, unrestricted transcripts | `PROHIBITED` | Never retained as evidence payload. |
| cryptographic signature, federated identity proof, storage-adapter metadata | `DEFERRED` | Requires separate architecture; shall not be required for minimum admissibility. |

The minimum normative standard may add fields only when needed to make these
semantics unambiguous. It shall not weaken a status or turn an operational field
into semantic identity without architecture review.

### 5.3 Shared closed value-object contracts

The following contracts are authoritative wherever the named value occurs in a
lifecycle record, package manifest, retention event, deletion tombstone, or
their active detail objects. Each concrete object contains exactly the members
listed, every listed member is required, no member is optional, and additional
properties are prohibited. A field whose applicability rule requires
`NOT_APPLICABLE` or permits `UNAVAILABLE` uses only the exact two-member Section
6.2 status object, never a partial concrete object. The required `limitations`
wrapper is the sole exception: its internal status is represented by the exact
three-member contract below so that the field always has one object shape. All
strings satisfy the Section 6.2 Unicode and canonicalization rules.

| Value | Exact concrete members and constraints | Ordering and identity |
| --- | --- | --- |
| `actor_identity` | `actor_id`: non-empty stable identifier; `actor_type`: one of `ACCOUNTABLE_HUMAN`, `HUMAN`, `AI_MODEL`, or `SOFTWARE_SERVICE`; `actor_role`: one of `ACCOUNTABLE_HUMAN`, `PREPARER`, `EXECUTOR`, `REVIEWER`, `DECISION_RECORDER`, or `OBSERVER`; `display_name`: non-empty attributable name. `actor_type=ACCOUNTABLE_HUMAN` requires `actor_role=ACCOUNTABLE_HUMAN`; no other actor type may use that role. AI or service actors never become accountable authority. | Object keys canonicalize under Section 6.2. The complete object participates wherever `actor_identity` is semantic; no display or role field is excluded. |
| `authority_reference` | `authority_id`: non-empty stable identifier; `authority_kind`: one of `ACCOUNTABLE_HUMAN_AUTHORIZATION`, `GOVERNANCE_ARTIFACT`, `LEGAL_AUTHORITY`, `RETENTION_ASSIGNMENT`, or `DELETION_AUTHORIZATION`; `issuer_actor_id`: exact `actor_id` of the accountable issuer; `governed_scope`: non-empty bounded scope string; `source_identity`: non-empty immutable record, artifact, or decision identity. The issuer must resolve to an `actor_identity` whose type and role are both `ACCOUNTABLE_HUMAN`; a reference never expands its bounded scope. | Object keys canonicalize under Section 6.2. Every member participates in the containing identity. |
| `assignment_authority` | `authority_reference`: one concrete authority-reference object above with `authority_kind=RETENTION_ASSIGNMENT` or `ACCOUNTABLE_HUMAN_AUTHORIZATION`; `assigned_by_actor_id`: exact accountable issuer `actor_id`. The two actor identifiers must match. | Object keys canonicalize under Section 6.2. Both members participate in retention-event identity. |
| `content_identity` | `sha256`: exactly 64 lowercase hexadecimal characters; `media_type`: non-empty lowercase type/subtype token; `byte_length`: canonical non-negative decimal string. It identifies exact retained bytes and supplies no locator or authority. | Object keys canonicalize under Section 6.2. All members participate in identity. |
| `package_identity` | `package_id`: exact `ES-EVIDENCE-PACKAGE-SHA256-<64-lowercase-hex-digest>` identifier. It identifies the Section 4 manifest and supplies no membership, locator, or authority beyond that identified manifest. | The sole member participates in identity. |
| ordinary `location_identity` | `location_scheme`: one of `REPOSITORY_RELATIVE`, `CONTENT_ADDRESSED`, or `EXTERNAL_IMMUTABLE`; `location_value`: non-empty canonical locator valid for that scheme. It shall not contain credentials. This ordinary shape is used in every location-bearing event except `RETENTION_RELOCATED`, whose exact two-location wrapper remains defined in Section 11.1.1 and whose nested values each use this ordinary shape. | Object keys canonicalize under Section 6.2. Both members participate in the event identity. |
| `location_type` | A string token, exactly one of `REPOSITORY_PATH`, `CONTENT_ADDRESS`, or `EXTERNAL_IMMUTABLE_OBJECT`. It must correspond respectively to `REPOSITORY_RELATIVE`, `CONTENT_ADDRESSED`, or `EXTERNAL_IMMUTABLE`. | Scalar; participates in the containing identity. |
| `limitations` | `status`: one of `NONE`, `PRESENT`, `UNAVAILABLE`, or `NOT_APPLICABLE`; `entries`: an array of strings; `reason_code`: one of `NONE`, `BOUNDED_LIMITATIONS_RECORDED`, `LIMITATIONS_UNAVAILABLE`, or `FIELD_NOT_APPLICABLE`. `NONE` requires empty `entries` and `reason_code=NONE`; `PRESENT` requires a non-empty array and `BOUNDED_LIMITATIONS_RECORDED`; `UNAVAILABLE` requires an empty array and `LIMITATIONS_UNAVAILABLE`; `NOT_APPLICABLE` requires an empty array and `FIELD_NOT_APPLICABLE`. Entries are non-empty bounded statements and may not encode structural state, authority, or transitions. | Entries sort by exact string in Unicode scalar order and duplicates are prohibited. The complete object participates wherever `limitations` is semantic. |

`retention_assignment_authority`, `correction_authority_reference`,
`invalidation_authority_reference`, `deletion_authority_reference`, and
`legal_authority_reference` use the same `authority_reference` concrete object;
their surrounding applicability and permitted `authority_kind` narrow it. No
implementation may introduce an alternative object shape, omit a declared
member, treat a scalar identifier as one of these objects, or infer a member
from conversation, free-form limitations, or another field.

## 6. Deterministic Evidence-Record Identity

### 6.1 Namespace and format

The record identifier shall be:

```text
ES-EVIDENCE-RECORD-SHA256-<64-lowercase-hex-digest>
```

The digest is SHA-256 over the UTF-8 bytes of the canonical semantic payload.
The stable algorithm identifier is `sha256`. An evidence-record ID identifies
only those serialized semantics. It does not assert that the content is true,
admissible, approved, independent, or authoritative.

### 6.2 Canonical JSON profile

Canonical bytes use the repository convention of sorted object keys,
`ensure_ascii=false`, compact separators, UTF-8, and SHA-256, with the following
complete restrictions. RFC 8259 supplies JSON syntax only; this profile is the
normative canonicalization contract where it is stricter.

1. Input is UTF-8 without BOM. A decoder shall reject malformed UTF-8, isolated
   surrogates, noncharacters, and Unicode scalar values `U+0000` through
   `U+001F` in source form; required JSON escapes for control characters are
   permitted. Every member name and string value shall already be Unicode NFC.
   Normalization is validation, not silent repair.
2. Object member names are unique and serialized in ascending Unicode scalar
   value order after NFC validation. Duplicate names, including names that
   collide after NFC normalization, fail closed.
3. Arrays whose contract declares sequence meaningful preserve input order.
   Set-like arrays are sorted by the exact stable key declared for that field;
   ties are rejected rather than resolved by input order. The standard and
   schema shall classify every array as ordered or set-like. Execution commands
   and command results preserve execution order. Package record IDs sort by
   evidence-record ID. Artifact paths, inclusions, exclusions, expected scope,
   and manifest entries sort by Section 8 path order. Findings, dispositions,
   risks, and uncertainties require stable IDs and sort by those IDs. Authority
   tokens and disclosure tokens sort by exact token. Payload references sort by
   SHA-256, then media type. No other array is admissible until the schema gives
   it one of these rules and a unique stable key.
4. Serialization contains no insignificant whitespace and no trailing newline:
   comma is `,`, colon is `:`, and no space surrounds either.
5. Strings use double quotes. Quotation mark, reverse solidus, and control
   characters use the shortest lowercase JSON escape: `\"`, `\\`, `\b`,
   `\t`, `\n`, `\f`, `\r`, or lowercase `\u00xx` when no short escape exists.
   Solidus `/` is never escaped. Non-ASCII scalar values are emitted directly
   as UTF-8, never as `\u` escape sequences.
6. JSON numbers are prohibited everywhere. Counts, lengths, and versions are
   canonical decimal strings: `0` or a nonzero digit followed by digits, with no
   sign, leading zero, fraction, exponent, or surrounding whitespace. Booleans
   are the JSON literals `true` and `false`.
7. Timestamps use RFC 3339 UTC only, exactly `YYYY-MM-DDTHH:MM:SS.ffffffZ`, with
   six decimal fractional-second digits. Offset forms, leap seconds, reduced
   precision, and `-00:00` are prohibited. Timestamps are observations and never
   identity substitutes.
8. `null` is permitted only for fields whose schema explicitly assigns a
   semantic unknown value; it is never equivalent to omission. Optional absence
   is omission. Required empty collections are `[]` or `{}`. `NOT_APPLICABLE`
   is `{"status":"NOT_APPLICABLE","reason_code":"<closed-token>"}` and
   `UNAVAILABLE` is the same shape with status `UNAVAILABLE`; neither is null,
   empty, or omitted.
9. Digests and Git object IDs use lowercase hexadecimal at their declared full
   length. Enum tokens preserve declared uppercase spelling. Paths preserve
   case and follow Section 8 normalization.
10. The top-level `schema_version` is semantic and serialized like every other
    member. For evidence-record version `1`, its exact value is the string
    `1.0.0`. Package manifests have their own schema version and canonical
    payload. The top-level `evidence_record_id` member alone is omitted before
    serialization and digest computation; no placeholder is inserted.

The serializer shall produce the same bytes on every supported platform and
implementation. A reader shall parse with duplicate-key detection, validate all
profile restrictions and schema semantics, recompute canonical bytes, and reject
any supplied representation that differs byte-for-byte. It shall not normalize,
coerce, trim, reorder, repair, or choose a platform-native line ending.

Package identity is
`ES-EVIDENCE-PACKAGE-SHA256-<64-lowercase-hex-digest>`. Its digest is SHA-256 of
the Section 6 canonical package manifest after omitting only the top-level
`package_id`. Package record membership is sorted as above, and payload
references bind digest, media type, byte length, and semantic limitations.
Package identity changes when membership or semantic payload references change;
it never changes any member record identity or authority.

Retention-event and deletion-tombstone identities use this same canonical JSON
profile. For a retention event, omit only top-level `retention_event_id` and use
`ES-EVIDENCE-RETENTION-EVENT-SHA256-<64-lowercase-hex>`. For a deletion
tombstone, omit only top-level `deletion_tombstone_id` and use
`ES-EVIDENCE-DELETION-TOMBSTONE-SHA256-<64-lowercase-hex>`. All other fields,
including `retention_event_transition_kind`, every active branch-detail member,
explicit inactive-branch non-applicability, schema version, lineage, authority
references, timestamps, event locations, deletion state, deletion-tombstone
linkage, and limitations, are semantic. Every identity-bearing retention-event
array follows its exact Section 11.1 ordering rule; duplicates fail closed and
member insertion order carries no meaning.

### 6.3 Schema evolution and identity

The normative schema uses semantic version strings. A version change is required
for any structural, vocabulary, canonicalization, admissibility, artifact-binding,
retention, or field-meaning change. A patch version may only clarify annotations
without changing accepted instances or canonical bytes; a minor version may add
optional, backward-compatible structure; a major version is required for any
incompatible change. Every version remains a semantic identity input.

Readers may accept explicitly supported older versions by validating each under
its original schema and canonicalization profile. They shall never reinterpret
an older record under a newer profile. Future or otherwise unsupported versions
fail closed as non-admissible. Any semantic field change, including a version
change that changes accepted semantics, creates a new evidence identity and must
use correction or supersession lineage.

### 6.4 Semantic and excluded fields

All Section 5 fields other than `evidence_record_id`, `payload_location`, and
implementation storage metadata are semantic when present. Payload content
digests and media types are semantic; their mutable locators are operational.
Excluded operational fields include filesystem absolute location, database row
ID, upload retry count, cache state, transport headers, log offset, storage
adapter, and presentation formatting. Exclusion from identity does not permit an
excluded field to contradict the semantic payload.

The governed-artifact identity is an input to evidence identity, not the same
identity. Two responsibilities about the same artifact require distinct evidence
records. Two byte-identical artifacts in different governed contexts may have the
same content digest but different governed-artifact and evidence identities.

### 6.5 Corrections and supersession

An issued record is immutable. A correction creates a new record with a new
identity, `correction_or_supersession_reference` pointing to the prior record,
and a disposition describing the corrected field and reason. Supersession also
creates a new record and preserves both identities. Neither operation rewrites,
deletes, or causes the prior record to inherit the successor's authority.

### 6.6 Identity-churn conformance examples

Broad semantic identity is intentional. The future non-normative example and
static fixtures shall demonstrate that changes to governed subject, ES-6
responsibility, scope, authority evidence, actor/reviewer identity, independence
declaration, findings, decision, risks, uncertainty, timestamps, evidence origin,
retention assignment, predecessor, payload digest/media type, or artifact binding
must change evidence identity. Artifact byte, object, mode, path, baseline,
classification, rename, deletion, symlink, or submodule changes therefore change
artifact identity and evidence identity.

Reordering object members before canonicalization, changing presentation
whitespace, moving a record between packages, or changing an operational field
excluded by Section 6.4 must not change evidence identity. Payload location may
change without changing evidence identity only when the payload digest, media
type, semantic access limitations, and retention semantics do not change; the
location observation is separately identified. A factual correction, semantic
retention change, or changed decision requires a new correction/superseding
record and predecessor lineage. Identity churn is the expected consequence of
immutable, semantically complete evidence and is mitigated by deterministic
correction and supersession, never mutable records.

## 7. Evidence Admissibility

Admissibility is a bounded evaluation for one named lifecycle gate, not truth or
authority. A record is admissible only when:

- its schema is supported and canonical identity recomputes exactly;
- required fields and applicable conditional fields are present;
- reviewer identity and independence are sufficient under Section 9, and its
  evidence-origin state is sufficient for that gate under Section 10;
- actor, authority, subject, scope, and artifact bindings are exact;
- predecessor identity and continuity checks pass when required;
- the claimed command results are complete enough for the claimed conclusion;
- contradictions, unavailable values, findings, risks, and uncertainty are not
  silently omitted;
- reviewer-independence requirements are explicitly met where applicable;
- prohibited content is absent; and
- its immutable issuance-time retention statement and the exact ordered
  retention-event chain satisfy Section 11 for the named gate; any required
  payload remains retrievable and no completed tombstone removed it;
- every retention event has exactly one valid
  `retention_event_transition_kind` branch, explicit inactive-branch
  non-applicability, exact predecessor applicability, closed branch details,
  deterministic identity and collection ordering, and a uniquely derivable
  operational lineage; correction and invalidation do not independently become
  current operational state or supply operational authority;
- every deletion state, tombstone transition kind, transition-details branch,
  and predecessor-applicability rule validates, and any
  `DELETION_COMPLETED` event has an exact, non-circular link to one completed
  tombstone governed by an earlier deletion-authorization event in the same
  chain; and
- no intervening change invalidates the governed subject or predecessor.

Failure of any predicate makes the record non-admissible for that gate and
requires a stop or bounded discrepancy record. It shall not cause silent repair,
fallback to conversation history, or inference of the missing fact. A record may
remain useful historical evidence while non-admissible for a current gate.

## 8. Exact Governed-Artifact Binding

Every record shall declare exactly one binding mode. All commit, tree, and object
IDs are full IDs for the repository object format. All byte lengths are canonical
decimal strings. Unless a mode explicitly binds an index object, working-tree
identities bind bytes read directly from the filesystem before Git clean or
smudge filters and before line-ending conversion. Text and binary content are
treated identically.

### 8.1 Path and filesystem rules

Repository paths are UTF-8, NFC, case-preserving, slash-separated Git path names
relative to the repository root. They shall contain no leading slash, empty
component, `.` or `..` component, reverse solidus, NUL, or platform-dependent
normalization. Ordering compares unsigned UTF-8 bytes. Duplicate paths and paths
that collide under the host filesystem's case or Unicode behavior are
non-admissible; exact case-sensitive binding must be provable even on a
case-insensitive host.

A regular-file identity includes mode `100644` or `100755`. A symbolic link uses
mode `120000`; its content is the link-target byte sequence stored by Git or read
from the link itself, never the dereferenced target. A submodule uses mode
`160000` and binds the exact gitlink commit ID; its nested content is excluded
unless a separately declared manifest entry binds it. Mode-only and executable
changes are semantic. If filters, attributes, platform conversion, filesystem
behavior, or missing content prevents exact identity, the binding is
non-admissible and fails closed.

### 8.2 Single-artifact modes

- **Committed single file:** full commit ID; the commit's root tree ID;
  repository-relative path; object type; blob ID; file mode; and optional
  cross-system SHA-256 of the exact blob bytes. The path must resolve uniquely in
  that tree and must not be a submodule unless represented as the submodule mode.
- **Committed tree:** full commit ID; exact repository root or subtree path and
  tree ID; and explicit inclusion and exclusion path rules. Inclusion begins at
  the named tree and recursively includes every entry unless excluded by an
  exact repository-relative path prefix listed in canonical path order. Globs,
  ignore files, environment rules, and implicit exclusions are prohibited.
  Symlinks bind link blobs; submodules bind gitlink commit IDs and are not
  traversed. Missing roots, path overlap between inclusion and exclusion, or an
  object-type mismatch fail closed.
- **Uncommitted tracked file:** full baseline commit; path; baseline blob or
  explicit baseline absence; `STAGED_ONLY`, `UNSTAGED_ONLY`, or
  `STAGED_AND_UNSTAGED`; exact selected candidate bytes and their byte length,
  SHA-256, computed Git blob ID, and file mode. The binding also includes the
  baseline-to-candidate pair: baseline blob/mode and resulting blob/mode, which
  is the deterministic before/after identity. For `STAGED_AND_UNSTAGED`, index
  and worktree identities are both recorded and the record declares which is the
  governed candidate; a vague diff identity is prohibited.
- **Untracked candidate:** full baseline commit; exact path; `UNTRACKED` state;
  exact expected complete worktree scope; byte length; SHA-256; computed Git blob
  ID; and mode. The path must be absent from the baseline and index. A symlink is
  read as link content. An untracked directory requires the multi-file manifest.
- **Staged content:** full baseline commit plus one deterministic stage-zero
  manifest. Each path records baseline object/mode, stage-zero blob or gitlink
  ID, byte length when bytes exist, file mode, and whether worktree content
  diverges from stage zero. The aggregate stage-zero manifest digest is the index
  identity; an implementation need not create an index tree. A missing stage-zero
  entry is expected only for a valid `DELETED` entry whose path existed in the
  baseline or prior index state. It is invalid for every non-deletion state. Any
  conflict stage, intent-to-add without exact candidate bytes, or multiple
  admissible interpretations fails closed.

For staged deletion, the entry contract is exactly:

```text
path; state=DELETED; baseline_object_id; baseline_mode;
stage_zero_object_id=NOT_APPLICABLE; stage_zero_mode=NOT_APPLICABLE;
resulting_bytes=NOT_APPLICABLE; resulting_sha256=NOT_APPLICABLE;
byte_length=NOT_APPLICABLE; classification; worktree_state;
worktree_divergence; worktree_identity
```

No stage-zero entry may exist for that path. Absence is the expected deletion
result, not an error. `baseline_object_id` and `baseline_mode`, including mode
`100755`, preserve the deleted object's exact identity. The classification
cross-product is exact:

| Observable staged-deletion state | `state` | `classification` | `worktree_state` | `worktree_divergence` | `worktree_identity` |
| --- | --- | --- | --- | --- | --- |
| No recreated worktree content | `DELETED` | `STAGED` | `ABSENT` | `false` | All four subfields `NOT_APPLICABLE` |
| Path recreated in the worktree | `DELETED` | `STAGED_AND_UNSTAGED` | `RECREATED` | `true` | Concrete and exact |

`classification=STAGED_AND_UNSTAGED` is prohibited when
`worktree_state=ABSENT`. `classification=STAGED` is prohibited when recreated
worktree content exists. `worktree_state=RECREATED` requires a concrete
`worktree_identity` containing exactly `worktree_sha256`,
`worktree_git_object_id`, `worktree_byte_length`, and `worktree_mode`.
`worktree_sha256` is the exact byte identity; `worktree_git_object_id` is the
computed Git blob or gitlink identity where applicable, otherwise explicit
`NOT_APPLICABLE`; byte length is canonical decimal; and mode follows Section
8.1. `worktree_state=ABSENT` requires all four fields to be explicit
`NOT_APPLICABLE`. This is the authoritative `worktree_identity` subfield
contract. Equivalent observable states shall not receive different
classifications. A staged deletion and unstaged recreation never collapses into
one state. These rules apply identically to staged-only manifests and staged
entries within mixed multi-file manifests.

### 8.3 Canonical multi-file candidate manifest

A mixed candidate uses one manifest with `schema_version`, full
`baseline_commit`, exact inclusions, exact exclusions, and an `entries` array.
Every affected path appears exactly once, in ascending Section 8.1 path order,
and contains:

```text
path; state; baseline_object_id; baseline_mode; stage_zero_object_id;
stage_zero_mode; resulting_bytes; resulting_sha256;
resulting_git_object_id; byte_length; resulting_mode; classification;
rename_from; rename_to; deletion; worktree_state; worktree_divergence;
worktree_identity; symlink_target_sha256; submodule_commit_id
```

`state` is one of `ADDED`, `MODIFIED`, `DELETED`, `RENAMED_OLD`, or
`RENAMED_NEW`; `classification` is one of `STAGED`, `UNSTAGED`, `UNTRACKED`, or
`STAGED_AND_UNSTAGED`. Inapplicable values use explicit `NOT_APPLICABLE`, not
omission. A deletion records the baseline object and mode, `deletion=true`, and
no resulting bytes. For a staged deletion, the entry shall use the exact Section
8.2 deletion values: `state=DELETED`, concrete `baseline_object_id` and
`baseline_mode`, `stage_zero_object_id=NOT_APPLICABLE`,
`stage_zero_mode=NOT_APPLICABLE`, `resulting_bytes=NOT_APPLICABLE`,
`resulting_sha256=NOT_APPLICABLE`, `resulting_git_object_id=NOT_APPLICABLE`,
`byte_length=NOT_APPLICABLE`, `resulting_mode=NOT_APPLICABLE`, and
`classification=STAGED` when `worktree_state=ABSENT`, or
`classification=STAGED_AND_UNSTAGED` when `worktree_state=RECREATED`.
`RECREATED` requires `worktree_divergence=true` and a concrete, exact
`worktree_identity` using the exact Section 8.2 subfield contract. `ABSENT`
requires `worktree_divergence=false` and each of those four subfields to be
explicit `NOT_APPLICABLE`. The opposite pairings are prohibited. Thus the
mixed manifest represents every staged-deletion semantic without treating
expected stage-zero absence as missing evidence. For entries to which index or
worktree state does not apply, the corresponding fields are explicit
`NOT_APPLICABLE`. A rename is two entries: `RENAMED_OLD` names the new path in
`rename_to`, and `RENAMED_NEW` names the old path in `rename_from`; both bind
their applicable baseline and result identities. Similarity inference is never
identity evidence. Symlinks and submodules follow Section 8.1.

The manifest is serialized under Section 6 after removing only its own
`candidate_manifest_id`, then identified as
`ES-CANDIDATE-MANIFEST-SHA256-<64-lowercase-hex>`. The manifest includes every
path in the exact candidate and no unrelated path; exclusions are exact path
prefixes and are themselves semantic. Duplicate paths, missing bytes for any
non-deleted regular file or symlink, unmatched rename pairs, implicit ignore
rules, unknown states, or inability to compute any required identity fail closed.

### 8.4 Published and external modes

- **Published artifact:** the applicable local immutable file, tree, candidate,
  or commit identity; remote repository identity; full resolved remote commit or
  object identity; mutable ref name; ref observation timestamp; and observation
  method. The immutable resolved object is semantic. A later ref movement does
  not rewrite the observation. Publication proves remote availability only;
  integration requires separate ancestry and target-ref evidence.
- **External evidence:** stable issuer/source identity; governed subject; media
  type; byte length; SHA-256 of captured bytes; capture method and temporal
  boundary; immutable or content-addressed locator; access and retrievability
  limitations; and any transformation from source to captured bytes. A mutable
  locator alone, inaccessible bytes, unknown transformation, or unverifiable
  issuer makes the binding non-admissible for gates requiring the payload.

For uncommitted content, immutable digests bind the exact candidate but do not
make it committed. For committed content, commit, tree, blob/gitlink, path, and
mode identities are complementary and none substitutes for another.

## 9. Actor Identity, Reviewer Attribution, and Independence

Records shall distinguish these roles:

- **accountable human** — the person who may issue bounded approval or authority;
- **preparer or executor** — the attributable actor that produced the candidate
  or performed the responsibility;
- **reviewer** — the attributable actor that evaluated the exact candidate;
- **model identity** — family and version where available for AI-assisted work;
  never an accountable authority; and
- **session identity** — an available provenance locator, not proof of identity,
  independence, correctness, or authority.

An independence declaration is required for architecture review, implementation
review, renewed review after revision, certification review where independence is
required, and any governing artifact that requires it. It shall state the
reviewer's role, whether the reviewer prepared or revised the governed subject,
prior responsibilities performed, shared-session or shared-context exposure,
conflicts of interest, evidence examined, and an explicit conclusion of
`INDEPENDENT`, `NOT_INDEPENDENT`, or `INDETERMINATE` with rationale.

A new process, agent, model, session name, or conversation shall not by itself
establish independence. The lifecycle record must support the declaration, and
the accountable human retains judgment over sufficiency. If identity is
unavailable, the field states `UNAVAILABLE` with reason. An unavailable reviewer
identity or indeterminate independence makes the record inadmissible for a gate
that requires attributable independent review.

## 10. Contemporaneous and Reconstructed Evidence

Every record shall have exactly one evidence-origin state:

- `CONTEMPORANEOUS`: recorded during the responsibility from direct observations
  with reliable timestamps and exact subject identity;
- `RECONSTRUCTED_VERIFIED`: created later from immutable, independently
  verifiable sources sufficient to prove each bounded claim;
- `RECONSTRUCTED_PARTIAL`: created later with material gaps, unavailable fields,
  or incomplete proof; or
- `UNVERIFIED_REFERENCE`: a locator or assertion not verified against the
  required source and identity boundary.

Reconstructed records use their actual reconstruction completion timestamp and
may separately cite evidenced historical event times. They shall never backdate,
invent commands, infer exit statuses, manufacture session identities, or present
reconstructed narrative as original evidence. Mutable transcripts and session
summaries without independently verifiable subject and actor binding cannot
become identity-bound review records merely by being hashed.

`CONTEMPORANEOUS` evidence is required for a current independent review,
authorization decision, repository mutation, certification, or operational gate
unless the governing standard expressly permits `RECONSTRUCTED_VERIFIED` and an
accountable human accepts its exact limitations. `RECONSTRUCTED_PARTIAL` and
`UNVERIFIED_REFERENCE` may support historical understanding and discrepancy
assessment but are insufficient for current lifecycle entry or authority gates.

## 11. Retention, Immutability, and Historical Preservation

Record construction, issuance, identity, retention assignment, successful
retention, retrievability, relocation, admissibility, retention expiry, deletion
authorization, and deletion completion are separate states. Issuance fixes the
lifecycle record forever. It contains only the proposed or initially assigned
retention class and authority evidence then available. It shall not mutate when
retention is later assigned, confirmed, relocated, unavailable, restored,
expired, authorized for deletion, or deleted.

The producer may propose a class but shall not authorize its own assignment.
Accountable assignment cites applicable governance. Until the lifecycle record
and its event chain prove the assignment and any class-required durable
retention, the record is non-admissible for a gate requiring retained evidence.
A truthful immutable record may therefore exist and remain non-admissible.

The closed minimum vocabulary is:

| Retention class | Purpose and minimum boundary | Eligible evidence and assignment | Admissibility and expiry |
| --- | --- | --- | --- |
| `TRANSIENT_CHECKPOINT` | Safe recovery for the current responsibility through its completion, abandonment, supersession, or transfer to a stronger class. | Session-local partial evidence and recoverable checkpoints; accountable human assigns, while the producer may only propose. | Durable retention is required only when a dependent recovery gate cites it. Expiry does not authorize deletion; unresolved work or a legal hold prevents ordinary expiry. |
| `SLICE_LIFECYCLE` | Preserve evidence through slice integration and attributable closeout, plus resolution of all cited findings, discrepancies, corrections, and supersessions. | Preparation, review, revision, authorization, implementation, validation, repository-transition, and closeout records for one slice; accountable-human assignment required. | A valid `RETENTION_CONFIRMED` event is required before the record satisfies a later slice gate. At boundary expiry a `RETENTION_EXPIRED` event records expiry pending separate disposition. |
| `REPOSITORY_LIFETIME` | Preserve evidence for at least the period in which the repository and its governed history are maintained. | Integrated architecture, implementation, repository-state, certification, lineage, and evidence required to interpret enduring repository state; accountable-human assignment required. | Durable immutable or content-addressed retention and retrievability are required for admissibility. Repository archival or replacement does not itself authorize deletion. |
| `GOVERNANCE_PERMANENT` | Preserve constitutional, approval, certification, exception, legal-hold, deletion-tombstone, and authority-lineage evidence without an ordinary expiry boundary. | Evidence whose removal would break governance or authority interpretation; assignment requires accountable-human governance authority. | Durable retention and retrievability are required. Reclassification, payload removal, or deletion requires separate applicable governance and legal authority. |

### 11.1 Retention event record

A retention event binds exactly one issued lifecycle record through
`evidence_record_id` and binds the exact retained payload through
`content_identity` or package through `package_identity`; at least one is
required and an inapplicable one is explicit. Its closed event-kind vocabulary is:

```text
RETENTION_ASSIGNED RETENTION_CONFIRMED RETRIEVABILITY_CONFIRMED
RETENTION_RELOCATED RETENTION_UNAVAILABLE RETENTION_RESTORED
RETENTION_EXPIRED DELETION_AUTHORIZED DELETION_COMPLETED
LEGAL_HOLD_APPLIED LEGAL_HOLD_RELEASED
```

Every event requires `artifact_type=RETENTION_EVENT_RECORD`,
`retention_event_schema_version`, `retention_event_id`,
`retention_event_transition_kind`, `event_kind`, `evidence_record_id`,
`prior_retention_event_id`, `retention_class`, `assignment_authority`,
`content_identity`, `package_identity`, `location_identity`, `location_type`,
`retrievability_state`, `event_timestamp`, `actor_identity`,
`authority_reference`, `reason_code`, `deletion_tombstone_id`, `limitations`,
`correction_details`, `invalidation_details`, and
`non_authorizing_evidence_statement`. This is the authoritative retention-event
field contract; each field is declared exactly once and no other retention-event
semantic field is implied. Inapplicable fields use the Section 5.1 explicit
`NOT_APPLICABLE` status object; omission is prohibited.

`retention_event_transition_kind` is the single required semantic discriminator
for every retention event and participates in canonical retention-event identity.
Its closed vocabulary is `OPERATIONAL`, `CORRECTION`, and `INVALIDATION`.
Exactly one mutually exclusive schema branch is selected solely by this field.
The branch shall never be inferred from `reason_code`, `limitations`, timestamps,
package membership, or any other field. No branch creates lifecycle, repository,
retention-operation, deletion, or other authority.

For `retention_event_transition_kind=OPERATIONAL`, `event_kind` is exactly one
ordinary token from the closed vocabulary above, while `correction_details` and
`invalidation_details` are each explicit `NOT_APPLICABLE`. The event-kind-specific
operational fields and state transition shall validate, and the predecessor is
`NOT_APPLICABLE` only for the first event and otherwise identifies exactly one
immediately preceding event in the same chain. An operational event asserts no
correction or invalidation and may not silently correct or invalidate its
predecessor.

For the `OPERATIONAL` branch, `reason_code` is required and has this exact
event-kind mapping: `RETENTION_ASSIGNED=ASSIGNMENT_AUTHORIZED`,
`RETENTION_CONFIRMED=RETENTION_VERIFIED`,
`RETRIEVABILITY_CONFIRMED=RETRIEVABILITY_VERIFIED`,
`RETENTION_RELOCATED=LOCATION_CHANGED`,
`RETENTION_UNAVAILABLE=RETENTION_FAILURE_OBSERVED`,
`RETENTION_RESTORED=RETENTION_RESTORATION_VERIFIED`,
`RETENTION_EXPIRED=RETENTION_POLICY_EXPIRED`,
`DELETION_AUTHORIZED=DELETION_SEPARATELY_AUTHORIZED`,
`DELETION_COMPLETED=DELETION_COMPLETION_VERIFIED`,
`LEGAL_HOLD_APPLIED=LEGAL_HOLD_AUTHORIZED`, and
`LEGAL_HOLD_RELEASED=LEGAL_HOLD_RELEASE_AUTHORIZED`. This closed mapping supplies
event context but does not select the branch. `CORRECTION` and `INVALIDATION`
require `reason_code=NOT_APPLICABLE`; their respective closed detail-object reason
codes carry the branch-specific normative reason.

For `retention_event_transition_kind=CORRECTION`, `event_kind` is explicit
`NOT_APPLICABLE`, `prior_retention_event_id` identifies exactly one concrete
immediate predecessor, `correction_details` is the required closed object below,
and `invalidation_details` is explicit `NOT_APPLICABLE`. A correction performs no
operational retention-state transition. It preserves the predecessor's derived
operational state and ordinary event-kind semantics, preserves immutable prior
history, and receives a new deterministic retention-event identity. It shall not
implicitly relocate content, change retrievability, assignment, expiration,
legal-hold or deletion state, or perform any other ordinary retention action.

`correction_details` contains exactly `corrected_fields`, `corrected_evidence`,
`correction_reason_code`, and `correction_authority_reference`.
`correction_authority_reference` is concrete and attributable.
`correction_reason_code` has the closed vocabulary `FACTUAL_ERROR`,
`IDENTITY_ERROR`, `ATTRIBUTION_ERROR`, `EVIDENCE_REPLACEMENT`, and
`SCHEMA_INTERPRETATION_ERROR`.

`corrected_fields` is a canonically ordered array of closed objects. Each object
contains exactly `field_name`, `prior_value_identity`, `corrected_value`, and
`correction_value_schema`. `field_name` selects the closed eligible vocabulary
below. `prior_value_identity` is the lowercase SHA-256 identity, under Section
6.2, of the exact predecessor value including a `NOT_APPLICABLE` or `UNAVAILABLE`
status object when present. `corrected_value` is the exact typed replacement,
must differ semantically from that predecessor value, participates in the
correction-event identity, cannot be inferred from top-level metadata, and cannot
perform an operational transition. `correction_value_schema` is the exact closed
field-specific token below; it is not free-form and selects a JSON Schema branch
that validates `corrected_value` without inference.

| `field_name` | `correction_value_schema` and exact value type | Concrete/status forms | Evidence-only correction | Operational-state effect and eligibility |
| --- | --- | --- | --- | --- |
| `event_timestamp` | `RETENTION_EVENT_TIMESTAMP_V1`; canonical UTC RFC 3339 string | Concrete only | Yes, as `EVENT_ATTRIBUTION` | Historical observation only; eligible |
| `actor_identity` | `RETENTION_EVENT_ACTOR_IDENTITY_V1`; Section 5.3 closed actor object | Concrete only | Yes, as `EVENT_ATTRIBUTION` | Attribution only; eligible |
| `authority_reference` | `RETENTION_EVENT_AUTHORITY_REFERENCE_V1`; Section 5.3 closed attributable authority-reference object | Concrete or `NOT_APPLICABLE` exactly as the predecessor event-kind row permits | Yes, as `EVENT_AUTHORITY` | Historical authority representation only; eligible only when it does not create, remove, or broaden operational authority |
| `reason_code` | `RETENTION_EVENT_REASON_CODE_V1`; exact closed token required by the predecessor event kind | Concrete ordinary-event token or `NOT_APPLICABLE` for a non-operational predecessor | Yes, as `EVENT_ATTRIBUTION` | Descriptive classification only; eligible only when the replacement remains the required token for that predecessor kind |
| `limitations` | `RETENTION_EVENT_LIMITATIONS_V1`; Section 5.3 closed limitations object | Exact closed object | Yes, as `EVENT_ATTRIBUTION` | Non-structural limitation only; eligible |
| `non_authorizing_evidence_statement` | `RETENTION_EVENT_NON_AUTHORIZING_STATEMENT_V1`; exact required constant string | Concrete constant only | Yes, as `EVENT_ATTRIBUTION` | No state effect; eligible only if it remains the required constant |

This table is the complete `field_name` and `correction_value_schema`
vocabulary. Schema versions, record identity, branch discriminator, ordinary
`event_kind`, predecessor lineage, evidence-record binding, retained-content and
package binding, and correction/invalidation details are ineligible. The
operational fields `retention_class`, `assignment_authority`, `content_identity`,
`package_identity`, `location_identity`, `location_type`, `retrievability_state`,
and `deletion_tombstone_id` are prohibited from semantic-value correction because
a changed value could alter assignment, retained content, package, location,
retrievability, expiry, legal hold, deletion, or current operational state. Their
unchanged support may be corrected only through `corrected_evidence`. A real
change to any such claim requires a separate `OPERATIONAL` event; invalid prior
semantics require `INVALIDATION` and an independently attributable replacement.

`corrected_evidence` is a duplicate-free array of closed objects containing
exactly `supported_claim`, `evidence_kind`,
`predecessor_evidence_identity`, and `corrected_evidence_identity`.
`supported_claim` has the closed vocabulary `RETENTION_CLASS`,
`ASSIGNMENT_AUTHORITY`, `LOCATION_IDENTITY`, `RETRIEVABILITY_STATE`,
`EVENT_ATTRIBUTION`, `EVENT_AUTHORITY`, `DELETION_COMPLETION`, and
`LEGAL_HOLD_STATUS`. `evidence_kind` has the closed vocabulary
`AUTHORITY_REFERENCE`, `ACTOR_IDENTITY`, `LOCATION_EVIDENCE`,
`RETRIEVABILITY_EVIDENCE`, `DELETION_TOMBSTONE`, and
`LEGAL_HOLD_EVIDENCE`. Entries sort by `supported_claim`, then `evidence_kind`,
then predecessor evidence identity, then corrected evidence identity, all by
Unicode scalar value order. Duplicate tuples of those four semantic keys are
invalid. Every member participates in canonical retention-event identity; no
free-form member carries normative meaning. Evidence-only correction may leave
the underlying semantic value unchanged. At least one of `corrected_fields` or
`corrected_evidence` is non-empty.

Corrected-field entries sort by `field_name`, then `prior_value_identity`, then
the Section 6.2 canonical SHA-256 identity of `corrected_value`, all in Unicode
scalar value order. A `field_name` may occur at most once in one correction;
there is no multi-valued exception. Duplicate, ambiguous, or competing entries
are invalid. Top-level retention-event fields describe the correction event
itself. Corrected predecessor values exist only in
`correction_details.corrected_fields`; top-level `event_timestamp`,
`actor_identity`, `authority_reference`, `reason_code`, `location_identity`,
`retrievability_state`, `deletion_tombstone_id`, or other metadata shall never be
reused implicitly as corrected values. A token may occur in both locations only
with these explicit, non-conflicting meanings. Branch-level `NOT_APPLICABLE`
requirements govern the correction event's operational fields, not a typed
`corrected_value` nested inside the correction details.

Correction application is deterministic: resolve the exact immediate
predecessor; for every entry recompute and compare `prior_value_identity`;
validate `corrected_value` against the branch selected by
`correction_value_schema`; reject a prohibited operational-state-bearing change;
apply eligible values only as an overlay on that predecessor's historical
representation; then apply `corrected_evidence` without changing semantic
values. Original bytes and identities remain unchanged. Operational state is
derived only from the unique valid operational lineage plus permitted overlays.
A mismatch, ambiguity, stale target, duplicate field, conflicting correction,
fork, or cycle fails closed as `BLOCKED_DISCREPANT`. A correction remains
non-operational and never independently becomes current operational state.

For `retention_event_transition_kind=INVALIDATION`, `event_kind` and
`correction_details` are explicit `NOT_APPLICABLE`,
`prior_retention_event_id` identifies exactly one concrete immediate predecessor,
and `invalidation_details` is required. The invalidation performs no operational
state transition, preserves immutable history, creates no silent replacement,
and receives a new deterministic identity. `invalidation_details` is a closed
object containing exactly `invalidated_fields`, `invalidation_reason_code`,
`invalidation_authority_reference`, and
`attributable_replacement_event_id`.

`invalidated_fields` is a non-empty, duplicate-free array ordered by exact field
token in Unicode scalar value order. Its closed vocabulary is the
`corrected_fields` vocabulary plus `event_kind`, `evidence_record_id`,
`content_identity`, and `package_identity`. It excludes exactly
`retention_event_schema_version`, `retention_event_id`,
`retention_event_transition_kind`, `prior_retention_event_id`,
`correction_details`, and `invalidation_details` because those are immutable
schema, identity, discriminator, lineage, or branch-detail structure rather than
the predecessor claims being invalidated. `invalidation_reason_code` has the
closed vocabulary
`CLAIM_UNSUPPORTED`, `CLAIM_CONTRADICTED`, `AUTHORITY_INVALID`,
`WRONG_EVIDENCE_RECORD`, and `WRONG_RETAINED_CONTENT`.
`invalidation_authority_reference` is concrete and attributable.
`attributable_replacement_event_id` is concrete only when that independently
identified replacement already exists and is independently attributable;
otherwise it is explicit `NOT_APPLICABLE`. The invalidation does not adopt the
replacement's semantics or operational state, and invalidation alone cannot
select a current retention branch.

The three branches are unequivocally exclusive. A record shall not simultaneously
assert an ordinary retention action and correction or invalidation, and no active
branch object may appear in an inactive branch. `reason_code` remains an
event-context token within the selected branch and is never the primary branch
discriminator. Free-form `limitations` may explain bounded consequences but
shall not encode or substitute for the branch, object shape, vocabulary, state
transition, or lineage contract. Any real relocation, assignment, expiration,
legal-hold, retrievability, restoration, or deletion change after a correction or
invalidation requires a separately identified `OPERATIONAL` event.

#### 11.1.1 Derived operational state and applicability

The normative operational state is one closed composite object containing
exactly these dimensions:

| Dimension | Closed vocabulary; initial value |
| --- | --- |
| `retention_assignment_state` | `UNASSIGNED`, `ASSIGNED`; initially `UNASSIGNED` |
| `retention_confirmation_state` | `UNCONFIRMED`, `CONFIRMED`; initially `UNCONFIRMED` |
| `retrievability_state` | `UNKNOWN`, `RETRIEVABLE`, `UNAVAILABLE`; initially `UNKNOWN` |
| `location_state` | `NO_LOCATION`, `LOCATED`; initially `NO_LOCATION` |
| `legal_hold_state` | `NO_HOLD`, `ACTIVE_HOLD`; initially `NO_HOLD` |
| `deletion_state` | `NOT_AUTHORIZED`, `AUTHORIZED`, `COMPLETED`; initially `NOT_AUTHORIZED` |
| `retention_expiry_state` | `ACTIVE`, `EXPIRED`; initially `ACTIVE` |

Only the event effects below may change a dimension; every unlisted dimension is
preserved and is prohibited from changing. `RETENTION_ASSIGNED` is the only
valid first event, uses `prior_retention_event_id=NOT_APPLICABLE`, and derives
the first state from the initial tuple. Every other ordinary event requires one
concrete immediate predecessor. Correction and invalidation cannot be first.

In the matrix, `C` means a concrete value is required and `N/A` means the exact
Section 5.1 `NOT_APPLICABLE` object is required; there is no optional field.
`binding` means the already-established concrete `content_identity` or
`package_identity` is repeated unchanged, with the other binding field `N/A`.
`class=current` means the current concrete class is repeated unchanged;
`class=one` means exactly one Section 11 class. `location_identity=C` means a
concrete location object. For relocation only, that object is a closed object
containing exactly `prior_location_identity` and `resulting_location_identity`,
both concrete and unequal; `location_type` is the concrete resulting type.
`auth` abbreviates `assignment_authority/authority_reference`; `id` abbreviates
`content_identity/package_identity`; `loc` abbreviates
`location_identity/location_type`; and `tomb` abbreviates
`deletion_tombstone_id`. Every row also requires concrete `event_timestamp` and
`actor_identity`, and requires `correction_details` and `invalidation_details`
to be `N/A`.

| Event kind; reason | May be first; required predecessor-state predicates | Resulting effect | class; auth; id; loc; retrievability; tomb | Legal-hold, deletion, expiry constraints |
| --- | --- | --- | --- | --- |
| `RETENTION_ASSIGNED`; `ASSIGNMENT_AUTHORIZED` | Yes only; initial tuple | assignment=`ASSIGNED` | class=one; C/C; binding; N/A/N/A; `UNKNOWN`; N/A | hold=`NO_HOLD`, deletion=`NOT_AUTHORIZED`, expiry=`ACTIVE` |
| `RETENTION_CONFIRMED`; `RETENTION_VERIFIED` | No; assigned, unconfirmed, active, not completed | confirmation=`CONFIRMED`, location=`LOCATED`, retrievability=`UNKNOWN` | current; N/A/N/A; binding; C/C; `UNKNOWN`; N/A | preserves hold/deletion/expiry |
| `RETRIEVABILITY_CONFIRMED`; `RETRIEVABILITY_VERIFIED` | No; confirmed, located, active, not completed | retrievability=`RETRIEVABLE` | current; N/A/N/A; binding; C/C; `RETRIEVABLE`; N/A | preserves hold/deletion/expiry |
| `RETENTION_RELOCATED`; `LOCATION_CHANGED` | No; confirmed, located, active, retrievability not `UNAVAILABLE`, deletion not authorized/completed | location remains `LOCATED`, retrievability=`UNKNOWN` | current; N/A/N/A; binding; C relocation object/C; `UNKNOWN`; N/A | permitted during hold; prohibited after expiry or deletion authorization |
| `RETENTION_UNAVAILABLE`; `RETENTION_FAILURE_OBSERVED` | No; confirmed, located, active, not completed, currently not unavailable | retrievability=`UNAVAILABLE` | current; N/A/N/A; binding; C/C; `UNAVAILABLE`; N/A | blocks gate admissibility and deletion completion; preserves hold/deletion authority |
| `RETENTION_RESTORED`; `RETENTION_RESTORATION_VERIFIED` | No; confirmed, located, active, currently unavailable, not completed | retrievability=`RETRIEVABLE` | current; N/A/N/A; binding; C/C; `RETRIEVABLE`; N/A | preserves hold/deletion/expiry |
| `RETENTION_EXPIRED`; `RETENTION_POLICY_EXPIRED` | No; assigned, active, not completed | expiry=`EXPIRED` | current; N/A/C; binding; N/A/N/A; current value; N/A | does not change hold or deletion and grants no deletion authority; content may remain retrievable |
| `DELETION_AUTHORIZED`; `DELETION_SEPARATELY_AUTHORIZED` | No; expired, deletion not authorized/completed | deletion=`AUTHORIZED` | current; N/A/C; binding; N/A/N/A; current value; N/A | active hold may coexist with authorization but blocks completion |
| `DELETION_COMPLETED`; `DELETION_COMPLETION_VERIFIED` | No; deletion authorized, no active hold, retrievability not unavailable, exact completed tombstone | deletion=`COMPLETED`, retrievability=`UNAVAILABLE`, location=`NO_LOCATION` | current; N/A/N/A; binding; N/A/N/A; `UNAVAILABLE`; C | impossible during active hold; completion is irreversible |
| `LEGAL_HOLD_APPLIED`; `LEGAL_HOLD_AUTHORIZED` | No; no active hold, deletion not completed | hold=`ACTIVE_HOLD` | current; N/A/C; binding; N/A/N/A; current value; N/A | may follow expiry or authorization; blocks deletion completion |
| `LEGAL_HOLD_RELEASED`; `LEGAL_HOLD_RELEASE_AUTHORIZED` | No; active hold, deletion not completed | hold=`NO_HOLD` | current; N/A/C; binding; N/A/N/A; current value; N/A | release grants no deletion authority |

`assignment_authority` is concrete only for `RETENTION_ASSIGNED` and `N/A` in
every other row. `authority_reference` is concrete only in rows showing `C` and
`N/A` otherwise. The current content/package binding is concrete exactly as
defined by `binding` in every row; changing it is invalid. Location fields are
concrete exactly in the five rows showing `C` and `N/A` in every other row.
`deletion_tombstone_id` is concrete only for `DELETION_COMPLETED`. These rules,
the reason mapping, and the class rules are exhaustive; “where relevant” and “as
applicable” have no normative meaning.

The complete successor graph is:

```text
RETENTION_ASSIGNED -> RETENTION_CONFIRMED | LEGAL_HOLD_APPLIED
RETENTION_CONFIRMED -> RETRIEVABILITY_CONFIRMED | RETENTION_RELOCATED |
  RETENTION_UNAVAILABLE | RETENTION_EXPIRED | LEGAL_HOLD_APPLIED |
  LEGAL_HOLD_RELEASED
RETRIEVABILITY_CONFIRMED -> RETENTION_RELOCATED | RETENTION_UNAVAILABLE |
  RETENTION_EXPIRED | LEGAL_HOLD_APPLIED | LEGAL_HOLD_RELEASED
RETENTION_RELOCATED -> RETRIEVABILITY_CONFIRMED | RETENTION_UNAVAILABLE |
  RETENTION_EXPIRED | LEGAL_HOLD_APPLIED | LEGAL_HOLD_RELEASED
RETENTION_UNAVAILABLE -> RETENTION_RESTORED | RETENTION_EXPIRED |
  LEGAL_HOLD_APPLIED | LEGAL_HOLD_RELEASED
RETENTION_RESTORED -> RETENTION_RELOCATED | RETENTION_UNAVAILABLE |
  RETENTION_EXPIRED | LEGAL_HOLD_APPLIED | LEGAL_HOLD_RELEASED
RETENTION_EXPIRED -> DELETION_AUTHORIZED | LEGAL_HOLD_APPLIED |
  LEGAL_HOLD_RELEASED
DELETION_AUTHORIZED -> DELETION_COMPLETED | LEGAL_HOLD_APPLIED |
  LEGAL_HOLD_RELEASED
LEGAL_HOLD_APPLIED -> LEGAL_HOLD_RELEASED | RETENTION_CONFIRMED |
  RETRIEVABILITY_CONFIRMED | RETENTION_RELOCATED | RETENTION_UNAVAILABLE |
  RETENTION_RESTORED | RETENTION_EXPIRED | DELETION_AUTHORIZED
LEGAL_HOLD_RELEASED -> RETENTION_CONFIRMED | RETRIEVABILITY_CONFIRMED |
  RETENTION_RELOCATED | RETENTION_UNAVAILABLE | RETENTION_RESTORED |
  RETENTION_EXPIRED | DELETION_AUTHORIZED | DELETION_COMPLETED |
  LEGAL_HOLD_APPLIED
DELETION_COMPLETED -> no operational successor
```

An edge is permitted only when its matrix predicates also hold; all other edges
are prohibited. No ordinary event is idempotent: repeated confirmation,
retrievability confirmation, hold application, hold release, assignment, expiry,
authorization, or completion is prohibited rather than producing a redundant
identity. Duplicate successors or competing operational successors form a fork
and enter `BLOCKED_DISCREPANT`.

Confirmation and retrievability confirmation are evidentiary observations, not
retention release, deletion, or cleanup actions. Subject to their matrix
predicates, each may occur while `legal_hold_state=ACTIVE_HOLD` and after a
`LEGAL_HOLD_RELEASED` event. The event preserves the current hold state. Thus
confirmation is permitted during and after hold, and retrievability confirmation
is permitted during and after hold; neither applies or releases a hold, grants
deletion authority, permits deletion completion, or introduces another state.
Every event that can preserve `ACTIVE_HOLD` has `LEGAL_HOLD_RELEASED` as a
successor, subject to the release row's predicates. Conversely, every ordinary
event whose matrix predicates can hold immediately after `LEGAL_HOLD_APPLIED`
is present as its successor. The graph therefore neither strands a legal hold
after a hold-preserving event nor prohibits a matrix-permitted sequence.

State derivation starts with the initial tuple, traverses the unique acyclic
lineage, applies valid representational overlays, and applies each operational
row's exact effects. Invalidated operational claims are omitted only when a
unique independently attributable replacement lineage remains; otherwise state
is `BLOCKED_DISCREPANT`. A contradiction, prohibited edge, unmet predicate,
wrong concrete/`N/A` field, class or binding change, active-hold completion,
relocation after deletion authorization, restoration after completion, fork,
cycle, or unknown token is `BLOCKED_DISCREPANT`. Expiry never grants deletion
authority. Deletion authorization never implies completion. Evidence may remain
retrievable after expiry. No restoration or relocation is possible after
deletion completion.

Assignment authority and authority reference are required for assignment,
legal-hold, and deletion-authority operational events. Exact location is required
for confirmation, retrievability, relocation, unavailability, and restoration
operational events. `deletion_tombstone_id` is concrete and required only for an
`OPERATIONAL` event with `event_kind=DELETION_COMPLETED`, where it shall identify
the corresponding completed tombstone whose `evidence_record_id`, governing
`retention_event_id`, payload identity, authority, completion evidence, and
deletion state validate against the event and chain. The tombstone's governing
event must be an earlier `DELETION_AUTHORIZED` event in this same exact chain;
it shall not identify the `DELETION_COMPLETED` event, which would create a
canonical-identity cycle. Every other operational event kind, and every
non-operational branch, requires `deletion_tombstone_id=NOT_APPLICABLE`; a
concrete tombstone reference is prohibited. Missing, non-completed, mismatched,
cyclic, or otherwise unverifiable completion linkage is non-admissible. The
field is semantic and participates in retention-event canonical identity.

The first event is `OPERATIONAL` and uses an explicit `NOT_APPLICABLE`
predecessor. Every later event names exactly one concrete immediate predecessor.
Events are ordered only by predecessor traversal from the lifecycle record and
then verified against `event_timestamp`; timestamps do not repair lineage. An
operational successor after a correction or invalidation names that
non-operational event as predecessor but derives its predecessor state from the
unique valid operational ancestor after applying the intervening structural
correction or invalidation overlay. Correction changes only the named historical
representation; it does not independently become current operational state.
Invalidation removes the predecessor claim from state derivation but does not
select a replacement or current branch. A concrete attributable replacement is
evaluated only as its own event.

Missing predecessors, cycles, duplicate successors, forks, inconsistent
content/package identities, correction of an already invalidated event, or a
correction whose target is not applicable fail closed. Invalidation of a prior
correction is permitted only as an immediate successor and cancels only that
correction's representational effect; it does not revive an invalid operational
claim or change state. A correction or invalidation reached on a stale or forked
branch has no selected effect. Forked or contradictory successor chains remain
`BLOCKED_DISCREPANT`; no timestamp, replacement reference, package order, or
free-form explanation selects among them. The current retention class and latest
valid operational state derive only when one acyclic operational lineage remains
after all valid overlays are applied. Gate evaluation jointly considers the
lifecycle record, that lineage, current class, latest retrievability, active legal
holds, deletion state, and any tombstone. Missing, contradictory, stale, or
unverifiable events fail closed.

Content identity, package identity, retention class, event kind, transition kind,
authority, branch details, and event lineage are semantic. A location identity is
semantic to the event that observed or changed it. Relocation creates an
`OPERATIONAL` `RETENTION_RELOCATED` event with a new identity and leaves the
lifecycle record unchanged. Operational retrieval endpoints may change without
rewriting either issued artifact, but the changed location cannot satisfy a gate
until a new valid operational event records it. Mutable location alone never
establishes retention or retrievability.

An issued retention event is immutable and shall not be deleted. Correction and
invalidation always create new events under the exact structural branches above,
preserve every prior identity, and never cause authority inheritance.

Authoritative retention may be repository-based or external. Repository
retention is not universally mandatory because it would create unauthorized
repository mutations. A retained record satisfies its retention claim only when
stored immutably or by content address, retrievable for its class, and its bytes
recompute to the declared identity.

External retained evidence may be referenced when the record includes a stable
source/issuer, content digest, media type, immutable or content-addressed locator,
access boundary, retention expectation, and limitations. A mutable conversation
URL, ephemeral command buffer, or session handle alone is not authoritative
retention.

When repository retention is separately authorized, packages should reside under
one dedicated Engineering System evidence namespace, partitioned by stable slice
identity and package ID. Names shall be deterministic, avoid timestamps as
identity, and keep large or sensitive payloads external. One manifest should
reference bounded payloads instead of copying unrestricted logs. Draft,
superseded, reconstructed, failed, and contradictory evidence remains preserved
according to its class and shall not be silently rewritten or removed.

### 11.2 Privacy and legally required deletion tombstone

Deletion requires separate accountable-human authority and applicable legal
authority for exact targets. Retention expiry never implies it. An active legal
hold blocks deletion completion. Every tombstone has exactly one required
`deletion_state` discriminator. Its closed vocabulary is
`DELETION_AUTHORIZED`, `DELETION_IN_PROGRESS`, `DELETION_COMPLETED`,
`DELETION_FAILED`, and `DELETION_BLOCKED_BY_LEGAL_HOLD`; authorization alone
never implies completion.

Every `DELETION_TOMBSTONE` requires `artifact_type=DELETION_TOMBSTONE`,
`tombstone_schema_version`, `deletion_tombstone_id`, `deletion_state`,
`tombstone_transition_kind`, `tombstone_transition_details`,
`evidence_record_id`, `retention_event_id`, `governed_subject`,
`deleted_payload_identity`, `deleted_payload_media_type`,
`deletion_reason_category`, `deletion_authority_reference`,
`legal_authority_reference`, `legal_hold_status`,
`deletion_requested_timestamp`, `deletion_completed_timestamp`,
`deletion_actor_identity`, `deletion_method_class`, `completion_evidence`,
`remaining_retained_metadata`, `retrievability_state`, `admissibility_effect`,
`limitations`, `predecessor_tombstone_id`, and
`non_authorizing_evidence_statement`. This is the authoritative tombstone field
contract; no other tombstone semantic field is implied. All fields are required,
with explicit status objects where conditionally inapplicable.
`legal_authority_reference` is concrete for legally compelled deletion and
otherwise `NOT_APPLICABLE`. `deletion_completed_timestamp`,
`deletion_method_class`, and `completion_evidence` are concrete only for
`deletion_state=DELETION_COMPLETED`; every other state requires them to be
`NOT_APPLICABLE` and prohibits a completion claim. A completed state additionally
requires `legal_hold_status` to show no active hold and
`retrievability_state=DELETED`. `DELETION_BLOCKED_BY_LEGAL_HOLD` requires a
concrete active-hold observation and shall not claim completed deletion.
`DELETION_FAILED` and `DELETION_IN_PROGRESS` require retrievability and
limitations to preserve any partial or unknown outcome; neither may use
`DELETED` without completed, independently verifiable evidence.
`DELETION_AUTHORIZED` records authority only and prohibits any execution or
completion implication.

`deletion_state`, `tombstone_transition_kind`, and
`tombstone_transition_details` participate in canonical tombstone identity.
`tombstone_transition_kind` is the single required semantic discriminator for
tombstone creation, state progression, correction, and invalidation. Its closed
vocabulary and exact semantics are:

- `INITIAL` requires `predecessor_tombstone_id=NOT_APPLICABLE`, establishes the
  first tombstone state, and requires
  `tombstone_transition_details=NOT_APPLICABLE`;
- `STATE_PROGRESSION` requires exactly one concrete immediate predecessor,
  follows the permitted successor graph below, prohibits preserving the same
  `deletion_state`, and requires transition details containing the exact
  predecessor and successor deletion states;
- `CORRECTION` requires exactly one concrete immediate predecessor, preserves
  the predecessor `deletion_state` and therefore permits a same-state successor,
  may correct a semantic claim or its supporting evidence without declaring the
  `deletion_state` value corrected, does not imply state progression, and
  requires the closed correction structure defined below; and
- `INVALIDATION` requires exactly one concrete immediate predecessor, preserves
  the predecessor `deletion_state` in the invalidation tombstone, preserves
  immutable history, declares through the closed invalidation structure why the
  predecessor claim is invalid, and does not itself manufacture or select a
  replacement state.

The `tombstone_transition_details` schema has one branch selected solely by
`tombstone_transition_kind`. For `STATE_PROGRESSION` it contains exactly
`predecessor_deletion_state` and `successor_deletion_state`, each from the
unchanged five-state `deletion_state` vocabulary. For `CORRECTION` it contains
exactly `corrected_fields`, `corrected_evidence`, and `correction_reason_code`.
`corrected_fields` identifies tombstone semantic fields whose values are
corrected while `deletion_state` remains unchanged. It is a duplicate-free,
canonically ordered array whose closed vocabulary is exactly
`tombstone_schema_version`, `evidence_record_id`, `retention_event_id`,
`governed_subject`, `deleted_payload_identity`, `deleted_payload_media_type`,
`deletion_reason_category`, `deletion_authority_reference`,
`legal_authority_reference`, `legal_hold_status`,
`deletion_requested_timestamp`, `deletion_completed_timestamp`,
`deletion_actor_identity`, `deletion_method_class`, `completion_evidence`,
`remaining_retained_metadata`, `retrievability_state`, `admissibility_effect`,
`limitations`, and `non_authorizing_evidence_statement`. It excludes the
immutable identity, transition, lineage, and state-discriminator fields
`deletion_tombstone_id`, `tombstone_transition_kind`,
`tombstone_transition_details`, `predecessor_tombstone_id`, and
`deletion_state`. For a semantic-value correction, `corrected_fields` is
non-empty and the successor contains a changed corrected value for every named
field. A field whose semantic value is unchanged shall not appear in
`corrected_fields`; supporting-evidence-only correction is represented solely
through `corrected_evidence`.

`corrected_evidence` identifies supporting evidence that is replaced,
supplemented, or reattributed while its underlying semantic value, including an
unchanged deletion state, remains unchanged. It is a duplicate-free,
canonically ordered array of closed objects containing exactly `evidence_kind`
(`AUTHORITY_REFERENCE`, `LEGAL_AUTHORITY_REFERENCE`,
`LEGAL_HOLD_OBSERVATION`, `PAYLOAD_IDENTITY`, `ACTOR_IDENTITY`,
`COMPLETION_EVIDENCE`, or `RETRIEVABILITY_EVIDENCE`),
`predecessor_evidence_identity`, `corrected_evidence_identity`, and
`supported_claim`. `supported_claim` has the closed vocabulary
`DELETION_AUTHORITY`, `LEGAL_AUTHORITY`, `LEGAL_HOLD_STATUS`,
`DELETED_PAYLOAD_IDENTITY`, `DELETION_ACTOR_IDENTITY`,
`DELETION_COMPLETION`, `RETRIEVABILITY_STATE`, and `DELETION_STATE`.
`supported_claim=DELETION_STATE` corrects only evidence supporting the unchanged
state; it never declares the `deletion_state` value corrected or authorizes a
state transition. At least one of `corrected_fields` or `corrected_evidence` is
non-empty, permitting either a semantic-value correction, an evidence-only
correction, or both without conflating their meanings.

`corrected_fields` sorts by exact field token; `corrected_evidence` sorts by
`supported_claim`, then `evidence_kind`, then predecessor evidence identity,
then corrected evidence identity, all by Unicode scalar value order; duplicate
tuples of those four semantic keys are invalid. Both collections and every
member of each corrected-evidence object participate in canonical tombstone
identity.
`correction_reason_code` is one of `FACTUAL_ERROR`, `IDENTITY_ERROR`,
`ATTRIBUTION_ERROR`, or `EVIDENCE_REPLACEMENT`. For `INVALIDATION`, transition
details contain exactly `invalidated_fields`, `invalidation_reason_code`,
`invalidation_authority_reference`, and `attributable_successor_tombstone_id`.
`invalidated_fields` is a non-empty, duplicate-free array using the
`corrected_fields` closed vocabulary plus `deletion_state`, ordered by exact
field token; it excludes `deletion_tombstone_id`, `tombstone_transition_kind`,
`tombstone_transition_details`, and `predecessor_tombstone_id`.
`invalidation_reason_code` is one of
`CLAIM_UNSUPPORTED`, `CLAIM_CONTRADICTED`, `AUTHORITY_INVALID`, or
`WRONG_GOVERNED_SUBJECT`; the authority reference is concrete; and the successor
is concrete only when a separately attributable replacement record already
exists, otherwise explicit `NOT_APPLICABLE`. The invalidation tombstone never
adopts that replacement's state. Free-form `limitations` may explain impact but
shall not carry or substitute for these structural semantics.

`deletion_state` determines the schema branch, conditional fields,
admissibility effect, and gate behavior. An `INITIAL` tombstone with a
predecessor is invalid. Every non-`INITIAL` tombstone requires a concrete
predecessor identifying the immediately prior
tombstone for the same lifecycle record, governing retention event, governed
subject, and deleted payload; it changes `deletion_state` only to a state
consistent with the observed authority, legal hold, execution, and completion
evidence. The only permitted successor-state transitions are:

```text
DELETION_AUTHORIZED -> DELETION_IN_PROGRESS | DELETION_COMPLETED |
                       DELETION_FAILED | DELETION_BLOCKED_BY_LEGAL_HOLD
DELETION_IN_PROGRESS -> DELETION_COMPLETED | DELETION_FAILED |
                        DELETION_BLOCKED_BY_LEGAL_HOLD
DELETION_FAILED -> DELETION_IN_PROGRESS | DELETION_BLOCKED_BY_LEGAL_HOLD
DELETION_BLOCKED_BY_LEGAL_HOLD -> DELETION_IN_PROGRESS | DELETION_FAILED
DELETION_COMPLETED -> no successor state
```

Direct authorization-to-completion is valid only for an atomically observed
authorized deletion with complete evidence; it never permits inference across a
missing state. Resuming a failed or legally blocked deletion requires current
authority and, for a blocked state, evidence that the hold no longer blocks the
attempt. A same-state successor is valid only for `CORRECTION` or
`INVALIDATION`. `STATE_PROGRESSION` is the only transition kind that may change
`deletion_state`, and it is invalid with an unchanged state. Correcting evidence
supporting an unchanged state is not progression. A correction or invalidation
with a changed state is invalid, and no tombstone may combine correction and
progression. Determining that a predecessor's state value itself was erroneous
requires an attributable `INVALIDATION` naming `deletion_state` and a separate,
attributable replacement or successor record conforming to the applicable state
and transition rules; invalidation shall not silently manufacture the
replacement state. Missing lineage, forks, cycles,
invalid predecessor applicability, an unsupported transition, or contradictory
state-dependent or transition-kind-dependent fields fail closed.
Jurisdictional policy, deletion technology selection, cryptographic erasure,
and legal duration are deferred; the schema shall prohibit undeclared fields.

The tombstone binds the lifecycle record, governing retention event, exact
payload identity, authority, legal-hold observation, and resulting admissibility.
A completed tombstone must cite independently verifiable completion evidence and
shall never contain the sensitive payload or imply it remains retrievable. Its
`retention_event_id` identifies the earlier governing `DELETION_AUTHORIZED`
event. A later `DELETION_COMPLETED` event identifies this completed tombstone
through `deletion_tombstone_id`; both independently recomputed identities and
all shared semantics must agree without circular identity input. Issued
tombstones are immutable. Corrections, invalidations, and state progression
create a new tombstone with predecessor lineage and preserve every prior
identity.

The applicable existing ES-6 action boundary is the exact authorized cleanup or
closeout responsibility when its governing scope includes deletion. A blocked,
failed, partial, contradictory, or legally held attempt is recorded through
`BLOCKED_DISCREPANT` as applicable. No tombstone or event creates that authority,
and no new ES-6 responsibility is introduced.

A gate requiring deleted bytes is non-admissible. A gate requiring only surviving
metadata may remain admissible when the lifecycle record, retention chain,
tombstone, and exact gate requirements all validate. Failed or partial deletion
remains explicit and does not claim non-retrievability. Deletion may constrain
future verification without making truthful prior observations false. Any
unresolved conflict among hold, authority, event, tombstone, completion evidence,
or observed retrievability enters `BLOCKED_DISCREPANT`. Tombstones are
`GOVERNANCE_PERMANENT` unless stricter applicable law governs them.

## 12. Negative-Authority Semantics

Every record shall contain or deterministically derive all of:

```text
authority_granted
authority_withheld
decision_effect
next_responsibility_requiring_authorization
non_authorizing_evidence_statement
```

The default for `authority_granted` is the empty set. Only exact attributable
human authority evidence may populate it. Any authority not explicitly granted
for the exact subject, scope, issuer, effect, and temporal boundary is withheld.
Both authority fields use only the exact 32 canonical ES-6 responsibility tokens
enumerated in Section 13.2, contain no duplicates, and are ordered by their
Section 13.2 row order. No free-form or additional authority token is permitted.
The exact required value of `non_authorizing_evidence_statement` in every
lifecycle record, retention event, and deletion tombstone is
`EVIDENCE_IDENTITY_AND_RETENTION_DO_NOT_GRANT_AUTHORITY_V1`.
The canonical non-authorizing statement shall preserve these distinctions:

- review is not approval;
- approval is not implementation authorization;
- implementation approval is not commit authority;
- commit is not publication;
- publication is not integration;
- integration is not closeout;
- closeout is not certification; and
- certification is not operational authority unless separately and explicitly
  granted.

Evidence of an action that occurred may prove an observable repository state; it
does not retrospectively prove that the action was authorized. A record shall
preserve that discrepancy.

## 13. Lifecycle Integration and Responsibility Evidence

### 13.1 Integration rule

Evidence recording occurs within each ES-6 responsibility as part of its required
exit evidence or safe-stop checkpoint. ES-7 creates no separate evidence-capture
responsibility because that would add a thirty-third ES-6 responsibility, create
circular entry dependencies, and separate evidence from the observation boundary
it records. Serialization or later retention may be performed only as an
authorized action inside the current responsibility or as a separately authorized
repository act; it never becomes an implicit lifecycle transition.

At entry to every responsibility, the actor shall verify the predecessor record
ID where a predecessor is required, recompute its identity, verify its
admissibility for the intended entry gate, compare governed-artifact identity to
the current exact subject, detect intervening changes, confirm authority and
decision continuity, and check required independence. At exit, one independently
identified record shall state completion, safe stop, or discrepancy. Failure of
any required check stops mutation, preserves current evidence, and enters the
applicable ES-6 recovery or `BLOCKED_DISCREPANT` posture under separate authority.

### 13.2 Per-responsibility evidence contract

The table supplements, and does not replace, each ES-6 state profile. “Common”
means exact subject, ES-1/ES-6 states, repository/worktree identity, authorization,
scope, governing inputs, predecessor, commands/results, discrepancies, decision,
and authority withheld.

| ES-6 responsibility | Entry evidence and verification | Exit evidence | Required stop conditions |
| --- | --- | --- | --- |
| `DISCOVERY_CURRENT_STATE_ASSESSMENT` | Current repository observations and bounded observation authority | Sources, observations, discrepancies, uncertainty, bounded assessment | Identity ambiguity, requested mutation, or inference beyond evidence |
| `ARCHITECTURE_PREPARATION` | Common; exact architecture-preparation authorization and allowed path scope | Exact candidate binding, rationale, gates, unresolved questions, implementation withheld | Baseline/scope drift, missing architecture authority, or attempted review/approval |
| `ARCHITECTURE_REVIEW` | Exact candidate equals preparation exit; attributable independent reviewer | Findings, severities, scopes, candidate digest, uncertainty, no approval | Candidate drift, failed independence, missing evidence, or requested modification |
| `ARCHITECTURE_REVISION` | Exact review findings and bounded revision authority | New candidate identity, finding dispositions, unresolved findings | Scope expansion, stale findings, or reviser acting as renewed reviewer |
| `ARCHITECTURE_APPROVAL` | Current independent review bound to exact candidate and exact decision authority | Attributable approve/reject/disposition decision and limits | Candidate drift, inadequate review, or attempt to infer implementation |
| `ARCHITECTURE_COMMIT` | Approval subject equals exact staged/unstaged candidate; commit authority | Resulting commit/tree/blob identities and remaining authority | Diff mismatch, unexpected paths, stale approval, or absent commit authority |
| `ARCHITECTURE_PUBLICATION` | Exact approved commit, remote/ref baseline, publication authority | Push result and independently observed remote identity | Remote drift, ambiguous result pending verification, or integration request |
| `ARCHITECTURE_INTEGRATION_PREPARATION` | Published identity, current main, ancestry, bounded integration-preparation authority | Isolated context and temporary-resource identities; merge withheld | Main/source drift, overlap, or attempted merge |
| `ARCHITECTURE_MERGE_CREATION` | Exact prepared source/target and merge-creation authority | Merge commit, parents, tree, command/result; validation withheld | Existing/changed merge, conflict outside scope, or absent merge authority |
| `ARCHITECTURE_INTEGRATION_VALIDATION` | Exact merge identity and validation authority | Commands, complete results/statuses, environment limits; push withheld | Merge drift, incomplete/failed required gate, or push request |
| `ARCHITECTURE_MAIN_PUSH` | Validated merge unchanged, remote baseline, exact main-push authority | Push result and before/after local and remote identities | Remote drift, lease mismatch, ambiguous result until checked, or cleanup request |
| `ARCHITECTURE_INTEGRATION_CLEANUP` | Verified main push, exact target inventory, cleanup authority | Target-specific actions/results and retained recovery evidence | Unverified integration, broad target, authoritative evidence risk, or missing cleanup authority |
| `IMPLEMENTATION_AUTHORIZATION` | Approved exact architecture, decision scope, accountable issuer | Explicit grant/denial, exclusions, and later authority withheld | Architecture mismatch, missing approval, or attempted implementation |
| `IMPLEMENTATION` | Exact architecture and implementation authorization; current repository scope | Candidate manifest/digests, changes, tests, deviations, uncertainty | Scope/architecture drift, missing authority, or attempted self-review |
| `IMPLEMENTATION_REVIEW` | Exact implementation candidate and independent reviewer | Findings/dispositions, exact candidate identity, residual uncertainty | Candidate drift, failed independence, modification, or attempted approval |
| `TARGETED_IMPLEMENTATION_REVISION` | Current findings and exact revision authority | Revised manifest/digest and finding-by-finding disposition | Scope expansion, stale finding, or reviser acting as reviewer |
| `IMPLEMENTATION_APPROVAL` | Current independent review bound to exact candidate and decision authority | Attributable decision, subject comparison, limits, commit withheld | Candidate drift, unresolved required review, or inferred commit authority |
| `IMPLEMENTATION_COMMIT` | Approved candidate equals exact index/worktree; commit authority | Commit/tree/blob identities and remaining authority | Any diff mismatch, unexpected path, or absent commit authority |
| `IMPLEMENTATION_PUBLICATION` | Exact commit, remote/ref baseline, publication authority | Push result and verified remote identity | Remote drift, ambiguous result pending verification, or integration request |
| `IMPLEMENTATION_INTEGRATION_PREPARATION` | Published identity, current main, ancestry, integration-preparation authority | Isolated context and temporary inventory; merge withheld | Main/source drift, overlap, or attempted merge |
| `IMPLEMENTATION_MERGE_CREATION` | Exact prepared source/target and merge authority | Merge commit, parents, tree, command/result; validation withheld | Existing/changed merge, conflict outside scope, or absent authority |
| `IMPLEMENTATION_INTEGRATION_VALIDATION` | Exact merge identity and validation authority | Complete gates/results and environment limitations; push withheld | Merge drift, incomplete/failed required gate, or push request |
| `IMPLEMENTATION_MAIN_PUSH` | Validated merge unchanged, remote baseline, main-push authority | Push and independently verified remote-main identity | Remote drift, lease mismatch, ambiguity until checked, or cleanup request |
| `IMPLEMENTATION_INTEGRATION_CLEANUP` | Verified main push, target inventory, cleanup authority | Target actions/results and retained recovery references | Unverified integration, broad target, evidence risk, or missing authority |
| `CERTIFICATION` | Exact integrated subject, complete admissible evidence set, certification authority, required independence | Attributable certification/non-certification decision, limits, operational authority withheld | Identity/lineage gap, stale gate, unresolved blocker, or inferred operations |
| `OPERATIONAL_ACCEPTANCE` | Exact certified or otherwise eligible subject and separate operational-acceptance authority | Bounded acceptance/rejection and explicit operational limits | Product/engineering authority confusion, stale subject, or unauthorized operation |
| `CLOSEOUT` | Exact integrated/certified state, unresolved inventory, closeout authority | Closed/not-closed decision, retained evidence index, residual risks | Missing evidence, unresolved required work, or inferred cleanup/certification |
| `INTERRUPTED_WORK_RECOVERY` | Last exact checkpoint, repository reinspection, recovery authority, class A–M | Reconciled completed/incomplete work and safe next posture | Contradictory/stale identity, unsafe mutation, or authority no longer current |
| `BLOCKED_DISCREPANT` | Contradictory, missing, unsafe, or invalid-transition evidence | Preserved discrepancy, affected claims, needed human disposition | Any mutation or silent selection among contradictions |
| `DEFERRED` | Current exact subject and attributable deferral decision | Reason, retained state, residual work, next consideration | Treating deferral as completion or successor authority |
| `ABANDONED` | Exact subject, retained resources, attributable abandonment decision | Rationale, unfinished work, effects, evidence inventory | Deletion, inferred supersession, or completion claim |
| `SUPERSEDED` | Exact predecessor/successor identities and supersession authority | Immutable lineage, rationale, retained predecessor, successor authority withheld | Missing successor identity, deletion, or inferred successor authorization |

Intervening change is any change to the semantic evidence payload, governed
artifact binding, baseline, applicable governing artifacts, authority, review
findings, required tool/configuration assumptions, or relevant repository state.
When detected, prior evidence may remain historical but shall not satisfy the
current entry gate without an explicit rule permitting reuse and a retained exact
comparison.

## 14. Repository Authority and Practical Evidence Production

Evidence production is logically required by ES-6 but repository mutation is
separately governed. The architecture therefore separates:

1. **in-memory or session-local capture**, permitted only within the current
   responsibility and not durable repository evidence;
2. **external immutable retention**, permitted only when the current
   authorization includes that external effect and location;
3. **repository file creation or modification**, requiring explicit path-scoped
   repository-write authority;
4. **staging**, requiring separate staging authority where governance demands;
5. **commit**, requiring exact commit authority;
6. **publication**, requiring exact push/ref authority; and
7. **integration**, requiring its own preparation, merge, validation, push, and
   cleanup authorities under ES-6.

An evidence record may be assembled as a bounded return package without writing
it to the repository. The accountable human can then separately authorize its
retention location and repository transitions. Evidence that records an
authorization must cite the pre-existing attributable authorization; writing the
record does not create that authorization. This is the practical bootstrap path
and prevents evidence requirements from silently authorizing file creation.

## 15. Prospective Bootstrap and Phase 6C-3 Recovery

ES-7 adopts prospectively. Its own architecture preparation, review, and approval
do not require completed ES-7 implementation. Until the minimum mechanism is
implemented, ES-6's existing required evidence, exact repository observations,
and attributable human direction remain the governing bootstrap evidence. Any
later ES-7 record describing this bootstrap shall be honestly labeled
`RECONSTRUCTED_VERIFIED`, `RECONSTRUCTED_PARTIAL`, or `UNVERIFIED_REFERENCE`; it
shall not be presented as contemporaneous.

The prospective Phase 6C-3 recovery sequence is:

1. approve the exact ES-7 architecture after fresh independent review;
2. separately authorize and implement the minimum ES-7 evidence mechanism;
3. under separate review authority, conduct a fresh independent Tier 3 review
   against the exact byte-unchanged Phase 6C-3 candidate;
4. retain prospective, identity-bound review evidence;
5. under separate approval authority, rerun Phase 6C-3 architecture approval
   against that exact candidate and review record; and
6. proceed to Phase 6C-3 implementation only under separate explicit authority.

Current evidence identifies an evidence-retention gap, not a semantic defect in
the Phase 6C-3 candidate. Phase 6C-3 requires no semantic revision based on the
current evidence. Its present bytes shall remain unchanged throughout this ES-7
architecture-revision responsibility. That statement is assessment evidence,
not Phase 6C-3 approval or implementation authorization.

## 16. Historical Compatibility

Prospective adoption is the default. Completed historical slices shall not be
retroactively invalidated solely because they predate ES-7. Historical evidence
may be:

- indexed with citations to its original source and limitations;
- referenced without conversion;
- reconstructed with an explicit Section 10 origin state and current
  reconstruction timestamp; or
- left as legacy evidence when reconstruction would add no reliable value.

Session outputs, chat summaries, old logs, document status text, and Git history
retain their original evidentiary value and limitations. They shall not be
silently normalized into contemporaneous records, used to invent accountable
decisions, or treated as identity-bound independent reviews without adequate
proof. Repository Knowledge may index adopted records only under separately
authorized work and remains a derived view rather than the authoritative record.

## 17. Exact Future Implementation Boundary

### 17.1 Minimum normative implementation

The exact proposed minimum implementation is this six-file scope:

```text
ADD    docs/engineering-system/standards/Lifecycle-Evidence-Retention-and-Identity-Standard.md
ADD    docs/engineering-system/schemas/lifecycle-evidence-record.schema.json
ADD    docs/engineering-system/examples/lifecycle-evidence-record.example.json
MODIFY docs/engineering-system/standards/Engineering-Lifecycle-Standard.md
ADD    tests/unit/test_engineering_lifecycle_evidence_schema.py
MODIFY docs/engineering-system/knowledge/Repository-Knowledge-Index.md
```

This scope is sufficient and no seventh artifact is required. The Markdown
standard is the authoritative normative prose contract. The schema uses JSON
Schema Draft 2020-12 and is the normative machine-readable structural contract
for all three record classes through explicit `artifact_type` discriminators and
closed, separately defined branches in this one authorized schema file. It
governs fields, required presence, shapes, enumerations, formats, conditional
structure, and prohibited additional properties. It does not imply that truth,
independence, authority, retention sufficiency, legal posture, or semantic
admissibility is fully machine-decidable. The example is schema-valid and
non-normative; it contains bounded examples, or content-addressed bounded
references, for lifecycle records, retention events, and deletion tombstones
without duplicating or redefining normative prose. The retention-event schema
uses exact `retention_event_transition_kind` discriminators and mutually
exclusive, closed `OPERATIONAL`, `CORRECTION`, and `INVALIDATION` branches;
inactive detail fields require explicit `NOT_APPLICABLE`, and every branch object
prohibits additional properties. Its retention-event set includes a valid
operational event, semantic-field correction, evidence-only correction,
invalidation, separate operational successor after correction, and separate
replacement after invalidation. Its deletion set includes all
five `deletion_state` values, one valid immutable successor chain, one same-state
semantic-field correction, one same-state evidence correction with
`supported_claim=DELETION_STATE`, one attributable invalidation of an erroneous
state claim that does not silently supply a replacement state, and one valid
state change represented only by `STATE_PROGRESSION`; each correction preserves
state. It also includes a `DELETION_COMPLETED` event linked through
`deletion_tombstone_id` to its completed tombstone, an event requiring explicit
non-applicability for that field, and a mixed manifest containing an exact
staged deletion with both absent and recreated-worktree cases. Content-addressed
references may keep this bounded, but each required relationship remains
schema-valid and independently resolvable.

The ES-6 modification is limited to a discoverability and conformance reference
to the new subordinate standard. It shall not change any responsibility token,
meaning, ordering, field, transition, or authority boundary. Repository Knowledge
modification is limited to derivative index entries identifying approved
artifacts and lineage; it creates no authority and does not replace source
evidence. Tests are static contract validation only. These are proposed later
changes, not authorized files in this revision.

### 17.2 Deferred tooling and automation

Generators, interactive capture, Git hooks, CI enforcement, persistence adapters,
external storage integrations, query/reporting services, automated admissibility
judgment, signatures, federation, and cross-repository aggregation require later
architecture and explicit authority. No minimum normative implementation choice
shall predetermine those technologies.

## 18. Testing and Validation Strategy

Later implementation shall provide machine-checkable evidence that:

- supported schema versions are explicit and unsupported versions fail closed;
- canonical serialization and SHA-256 identity are stable across repeated runs;
- object-member and unordered-collection ordering is deterministic;
- duplicate keys, non-NFC strings, invalid Unicode, escaped solidus, non-ASCII
  escapes, numbers, wrong timestamp precision, BOMs, whitespace, and trailing
  newlines fail the canonical profile;
- every required and applicable conditional field is enforced;
- every shared Section 5.3 value object enforces its exact required members,
  closed vocabularies, cross-member constraints, ordering, identity
  participation, and prohibition of additional properties;
- optional omission, explicit empty collections, `NOT_APPLICABLE`, and
  `UNAVAILABLE` remain distinct;
- exact artifact SHA-256, Git blob, tree, commit, baseline, and worktree-class
  bindings obey their applicable modes;
- multi-file manifests are complete, deterministically ordered, and scope-bound;
- every committed, staged, unstaged, untracked, mixed, published, and external
  binding mode covers its required identity, path, mode, filter, symlink,
  submodule, rename, deletion, conflict, divergence, and fail-closed cases;
- the Draft 2020-12 schema is meta-schema valid, the non-normative example is
  schema-valid, enums and required fields align with the prose contract, and
  documentation/schema consistency checks cover every mechanically comparable
  vocabulary;
- canonical identity fixtures include positive cross-platform bytes and negative
  variants, and reproduce their declared SHA-256 values;
- all four retention classes, assignment states, durable-retention predicates,
  unavailable-location behavior, and non-admissible pre-retention records are
  represented without selecting storage or duration;
- every retention-event transition kind selects exactly one mutually exclusive
  schema branch; ordinary event kinds are confined to `OPERATIONAL`; correction
  and invalidation use their exact closed objects and are non-operational;
  inactive branches are explicit `NOT_APPLICABLE`; all branch members and
  collections participate in deterministic identity with exact ordering and
  duplicate rejection; and fixtures cover valid operational, semantic-field
  correction, evidence-only correction, invalidation, separate operational
  successor after correction, and separate replacement after invalidation;
- retention-event negative fixtures reject correction or invalidation with an
  operational event kind, missing predecessor, correction and invalidation both
  active, inactive branch content, duplicate corrected or invalidated fields,
  a correction that changes operational state, an invalidation that selects
  replacement state, forks, cycles, stale branches, and ambiguous current-state
  derivation; identity fixtures prove ordering and sensitivity for the
  discriminator and every branch detail;
- every operational retention-event kind enforces required conditional fields,
  exact predecessor linkage, relocation, retrievability, legal hold, and
  fail-closed cases; `DELETION_COMPLETED` alone requires a concrete
  `deletion_tombstone_id`, every other kind requires explicit non-applicability,
  and the governing-event/tombstone/completion-event linkage is exact and
  non-circular;
- schema branches and positive/negative fixtures encode every Section 11.1.1
  applicability row, predecessor predicate, permitted successor, prohibited
  transition, concrete-versus-`NOT_APPLICABLE` requirement, reason mapping,
  repeated-event rule, state effect, legal-hold/deletion restriction, and
  correction/invalidation overlay interaction;
- examples cover assignment -> confirmation -> retrievability, relocation,
  unavailable -> restored, hold application and release, expiry without deletion
  authority, authorized then completed deletion with an exact tombstone, active-
  hold blocking, invalid first event, invalid transition, invalid applicability,
  an operational successor after correction, and a replacement operational event
  after invalidation;
- positive and negative examples cover confirmation and retrievability
  confirmation both during an active legal hold and after legal-hold release,
  with matrix predicates preserved and no hold, deletion, or expiry side effect;
- positive and negative examples cover legal-hold release after every
  hold-preserving event kind, plus relocation and deletion authorization
  immediately after hold application when their unchanged matrix predicates
  hold; omitted, predicate-invalid, and post-completion release edges fail closed;
- corrected-value fixtures validate every closed `field_name`/
  `correction_value_schema` pair, predecessor-value binding, changed-value
  requirement, canonical corrected-value identity and ordering, duplicate-field
  rejection, top-level metadata separation, evidence-only correction, and
  rejection of every hidden operational-state change;
- lifecycle records remain byte-identical across post-issuance retention events,
  while each semantic event change produces a new event identity;
- correction and supersession create new identities and retain predecessor links;
- one record cannot represent multiple lifecycle responsibilities;
- `authority_granted` defaults empty and withheld authority remains explicit;
- no lifecycle transition or authority can be inferred from decision, status,
  completion, digest validity, or gate success;
- reconstructed evidence is labeled, cannot be backdated, and cannot masquerade
  as contemporaneous evidence;
- reviewer identity, role, independence conclusion, basis, and disclosures are
  structurally present when required;
- secrets, credentials, hidden reasoning, unrestricted transcripts, unnecessary
  absolute paths, and excessive environment content are rejected;
- package membership never changes record identity or transfers authority;
- exact predecessor linkage and decision continuity are validated;
- intervening artifact, governance, authority, configuration, or repository
  changes invalidate reuse where applicable; and
- payload digests, locations, and package scope cannot silently diverge;
- prohibited-content field names and structurally identifiable payload classes
  are rejected, while semantic secret detection remains accountable review;
- all five `deletion_state` values and all four `tombstone_transition_kind`
  discriminator values enforce their conditional fields, canonical identity
  effects, correction-versus-progression rules, exact predecessor applicability,
  closed corrected-field, evidence-kind, and `supported_claim` vocabularies, and
  admissibility consequences; authorization never implies completion; legal hold
  blocks completion; completed tombstones require completion evidence; failed or
  partial deletion remains explicit; tombstones preserve non-sensitive lineage
  and contain no deleted payload;
- tombstone fixtures include a valid same-state semantic-field correction, a
  valid same-state evidence correction supporting `DELETION_STATE`, rejection
  of `deletion_state` in `corrected_fields`, rejection of a changed state under
  `CORRECTION`, rejection of correction and progression combined in one
  tombstone, a valid state change under `STATE_PROGRESSION`, and invalidation of
  an erroneous state claim without silent replacement; ordering fixtures reject
  duplicate semantic keys and prove canonical ordering and identity sensitivity
  for `corrected_fields` and `corrected_evidence`;
- staged deletion requires expected stage-zero absence, preserved baseline
  object and executable mode, explicit non-applicable results, and the exact
  `STAGED`/`ABSENT`/`false` versus
  `STAGED_AND_UNSTAGED`/`RECREATED`/`true` cross-product in staged-only and mixed
  manifests; recreated content requires exact byte, Git-object where applicable,
  byte-length, and mode identity, while absence requires explicit
  non-applicability; the schema rejects opposite pairings, omissions, and
  equivalent observable states with different classifications; and
- identity-churn fixtures cover every Section 6.6 must-change, must-not-change,
  operational-location, correction, and artifact-change category.

Accountable-human judgment remains required to determine architecture quality,
evidence truthfulness, actor attribution sufficiency, reviewer independence,
finding significance, risk acceptance, admissibility for a consequential gate,
approval, authorization, exception, repository transition, certification,
operational acceptance, retention duration, and destructive or cleanup action.
Static conformance shall not decide those matters.

Architecture-revision quality gates are:

```bash
ruff format --check .
ruff check .
pytest -q
git diff --check
```

Gate success is validation evidence only.

## 19. Security and Privacy

Evidence shall apply data minimization. It may retain stable actor roles,
available model/session provenance, exact commands and arguments after secret
screening, bounded results, findings, decisions, artifact identities, and the
environment facts necessary to interpret a gate. It shall not retain:

- passwords, tokens, keys, cookies, credentials, or authentication material;
- hidden chain of thought, private reasoning, or requests for such content;
- unrestricted transcripts or complete terminal history;
- sensitive source content not needed for the governed decision;
- absolute user or host paths when repository-relative identity suffices;
- broad environment dumps, unrelated process state, or unnecessary personal
  data; or
- mutable external content without digest and provenance limitations.

Command evidence shall preserve semantic argv while permitting deterministic
redaction of secret values. Redaction shall be explicit and must not conceal a
parameter material to reproducibility; if safe reproducibility is impossible,
the limitation and uncertainty are recorded. Content digests may themselves be
sensitive correlation identifiers and require access controls proportionate to
the source.

Privacy minimization does not authorize silent redaction after issuance. If
applicable law requires payload deletion, Section 11.2 governs the separate
authority, immutable tombstone, loss of retrievability, and gate-specific
non-admissibility. A legal hold or preservation obligation blocks ordinary
expiry and cleanup. The minimum implementation records this posture but does not
choose jurisdictional policy, storage controls, or deletion technology.

## 20. Risks, Unresolved Questions, and Deferrals

| Risk or question | Architectural treatment or unresolved decision |
| --- | --- |
| Evidence fabrication | Digests prove stable content, not truth; require attribution, source binding, admissibility evaluation, and accountable judgment. Signing is deferred. |
| Overcollection and privacy | Minimum fields, bounded payloads, explicit prohibition of secrets/reasoning/transcripts, and external references for large evidence. |
| Excess lifecycle overhead | One compact record per responsibility occurrence, optional packages, references rather than duplication, and no universal repository-write requirement preserve the reviewed granularity boundary. |
| Repository pollution | The exact six-file minimum scope is fixed in Section 17; evidence storage remains separately authorized and external content-addressed retention remains permitted. |
| Unavailable model/session identity | Explicit `UNAVAILABLE`; never infer. Review must decide when that limitation blocks a gate. |
| Mutable external transcripts | Non-authoritative unless bounded, digested, and immutably retained; transcript content alone does not prove identity. |
| Ambiguous reviewer independence | Explicit declaration, disclosures, and accountable-human sufficiency judgment; session novelty alone is insufficient. |
| Evidence becoming authority | Deny-by-default fields, canonical non-authorizing statement, and non-transitive decision effects. |
| Circular evidence requirements | Prospective bootstrap and in-responsibility capture; ES-7 does not require its implementation for its own architecture approval. |
| Long-term archival | Immutable lifecycle records plus closed retention events govern assignment, confirmation, relocation, unavailability, restoration, retrievability, holds, expiry, and deletion; duration, media refresh, and archival technology remain policy decisions. |
| Cross-repository use | Stable repository and external-source identity is required; federated namespace, trust, and transport are deferred. |
| Correction and deletion tension | Sections 11.1–11.2 require immutable corrective event/tombstone lineage, separate human/legal authority, legal-hold precedence, and fail-closed payload-dependent gates; cryptographic erasure and jurisdictional policy remain deferred. |
| Retention-event correction or invalidation creates an operational transition | The required `retention_event_transition_kind` discriminator, mutually exclusive closed branches, ordinary-kind prohibition, state-preserving overlay semantics, and separate-`OPERATIONAL` requirement prevent correction or invalidation from silently changing state or authority. |
| Retention-event forks, stale correction branches, or silent replacements | Exact predecessor linkage preserves forks as `BLOCKED_DISCREPANT`; correction/invalidation overlays do not become operational state; invalidation does not select a replacement; and no branch or mutable endpoint satisfies a gate until one valid operational lineage is uniquely established. |
| Correction names a field but not its replacement value | Closed typed corrected-value entries bind predecessor value identity, replacement value, and field-specific schema; operational-state-bearing values are excluded and support-only changes remain in `corrected_evidence`. |
| Operational events permit discretionary applicability or state inference | The seven-dimension state, exhaustive eleven-row matrix, sole-first-event rule, complete successor graph, and closed fail-closed rule remove event, field, hold, expiry, deletion, location, and retrievability discretion. |
| Referenced operational values require implementation-defined structure | Section 5.3 closes actor, authority, assignment, content, package, ordinary-location, location-type, and limitations representations, including required members, vocabularies, ordering, identity, and additional-property rejection. |
| Legal-hold confirmation semantics diverge between matrix and graph | Confirmation and retrievability confirmation are explicitly permitted during a hold and after release when their unchanged matrix predicates hold; both preserve hold state and grant no later authority. |
| Legal-hold release becomes unreachable after a hold-preserving event | Every event kind that can preserve `ACTIVE_HOLD` has a predicate-guarded `LEGAL_HOLD_RELEASED` successor, and every event permitted immediately after hold application appears in the graph; all non-matrix and post-completion edges remain prohibited. |
| Deletion-state, transition-kind, or completion-link inconsistency | Required closed `deletion_state` and `tombstone_transition_kind` discriminators, transition-specific structural details, exact predecessor applicability, state-dependent schema branches, and a one-way non-circular `DELETION_COMPLETED` event reference to the completed tombstone fail closed on missing or contradictory state, transition, correction, invalidation, or linkage. |
| Correction vocabulary conflates evidence correction with state change | Closed and disjoint `corrected_fields`, `corrected_evidence`, and `supported_claim` contracts exclude `deletion_state` from corrected semantic values, allow evidence support for an unchanged state to be corrected, preserve deterministic identity, and reserve state-value change to `STATE_PROGRESSION`. |
| Deletion verification loss | Completed tombstones preserve non-sensitive identity and completion evidence; byte-dependent future gates fail while truthful bounded prior observations remain historical. |
| Signing and federation | Deferred pending threat model, key governance, revocation, trust roots, and cross-repository architecture. |
| Automated capture and validation | Deferred; automation must never collect secrets, decide authority, or silently transition lifecycle state. |
| Canonical JSON divergence | Section 6 fixes exact bytes and rejects normalization; cross-language fixtures and negative cases are required because host encoders may differ. |
| Artifact-binding complexity | Section 8 defines exact modes and fail-closed cases; filters, conflicts, path collisions, or unavailable bytes may make a record non-admissible rather than permit approximation. |
| Retention authority | Construction, issuance, assignment, successful retention, admissibility, expiry, and deletion are separate; unavailable retention stops dependent gates. |
| Identity churn | Semantically complete immutable records intentionally change identity when meaning changes; Section 6.6 requires deterministic correction and supersession examples rather than mutation. |

No unresolved question authorizes broader implementation. Architecture review
shall determine whether any question is blocking or requires targeted revision.

## 21. Assumptions, Dependencies, and Invariants

ES-7 assumes the Engineering Kernel, ES-1, ES-2, ES-5, and ES-6 remain governing;
Git supplies commit, tree, and blob identity where repository content is
involved; SHA-256 remains approved for stable evidence identity; accountable
human decisions can be retained independently; and external immutable retention
can be referenced without selecting a storage product. Failed assumptions remain
explicit.

Architectural invariants are:

1. one evidence record represents one ES-6 responsibility occurrence;
2. evidence identity, artifact identity, repository identity, actor identity,
   decision identity, and authority identity remain distinct;
3. evidence and evaluation never grant authority;
4. absent or unavailable evidence is not silently inferred;
5. lifecycle records, retention events, tombstones, and packages are immutable after issuance;
6. correction and supersession preserve prior identity and lineage;
7. uncommitted candidates are bound by exact bytes and worktree class;
8. independent review requires explicit attributable evidence beyond a session
   name;
9. reconstruction is visible and never backdated;
10. responsibility completion does not authorize the next responsibility;
11. retention and every repository transition have separate authority;
12. historical evidence is preserved without retrospective invalidation;
13. canonical bytes are platform-independent and unsupported versions fail
    closed without reinterpretation;
14. every artifact-binding mode is exact or non-admissible; approximate identity
    is prohibited;
15. valid retention assignment and required durable retention derive from the
    exact event chain and precede admissibility for dependent gates;
16. retention expiry does not grant deletion; legal hold blocks completion; and
    lawful deletion never rewrites an issued record or event;
17. every deletion tombstone declares exactly one closed `deletion_state` and
    exactly one closed `tombstone_transition_kind`; correction, invalidation,
    and progression are structurally distinct; `CORRECTION` and `INVALIDATION`
    preserve the predecessor state, only `STATE_PROGRESSION` may change it, and
    deletion completion is admissible only through exact non-circular
    event-to-tombstone linkage;
18. every retention event declares exactly one closed
    `retention_event_transition_kind`; its operational, correction, and
    invalidation branches are mutually exclusive, identity-bearing, and closed;
    correction and invalidation preserve operational state and immutable lineage,
    do not create authority or replacement state, and any operational change is a
    separate `OPERATIONAL` event;
19. retention-event current state derives only from one valid acyclic operational
    lineage after deterministic correction/invalidation overlays; missing,
    forked, cyclic, stale, or contradictory lineage fails closed as
    `BLOCKED_DISCREPANT`;
20. staged-only and mixed manifests preserve the same exact staged-deletion
    classification/worktree-state/divergence cross-product;
21. secrets, hidden reasoning, and unrestricted transcripts are prohibited;
22. ES-7 remains model-neutral and product-runtime independent;
23. every corrected semantic value is explicit, typed, predecessor-bound,
    identity-bearing, and incapable of performing an operational transition; and
24. every operational event validates one exhaustive applicability row and one
    permitted successor edge, with all resulting dimensions uniquely derivable;
25. every shared operational value object has one closed structural definition,
    and confirmation or retrievability confirmation may occur during or after a
    legal hold only under the same matrix predicates and without changing hold;
    and
26. every matrix-permitted legal-hold release remains reachable after each
    hold-preserving event, while every prohibited or predicate-invalid release
    edge remains prohibited.

## 22. Repository Scope and Quality Boundary

The exact authorized architecture-revision change is:

```text
ADD docs/architecture-intent/Engineering-System-Architecture-Intent-Slice-ES-7.md
```

The following protected architecture candidate shall remain byte-for-byte
unchanged:

```text
docs/architecture-intent/POE-STOR-Architecture-Intent-Slice-6C3.md
```

No other repository file may change. In particular, this responsibility does not
authorize modification of ES-6, creation of the subordinate standard, schema,
template, tests, validator, tooling, Repository Knowledge, branches, index,
commits, remotes, or Phase 6C-3.

## 23. Acceptance Criteria

ES-7 is ready for independent architecture review only when:

1. its normative outcome makes every responsibility occurrence independently
   auditable without making evidence authoritative;
2. lifecycle records, retention events, deletion tombstones, and packages are
   defined while responsibility identities remain separate;
3. every candidate field has an explicit semantic status and unavailable-value
   treatment;
4. deterministic identity, the complete canonical JSON profile, schema evolution,
   ordering, optional fields, corrections, and operational-field exclusions are
   uniquely implementable;
5. every required repository/artifact state has exact binding semantics,
   canonical manifest identity, and fail-closed behavior;
6. actor attribution, model/session availability, reviewer role, independence,
   and conflicts are explicit;
7. contemporaneous and reconstructed states cannot be confused;
8. all four retention classes and the closed retention-event chain define
   assignment, confirmation, relocation, unavailability, restoration,
   retrievability, hold, expiry, correction, and deletion boundaries without
   selecting storage or legal duration;
9. every retention event uses the single required
   `retention_event_transition_kind` discriminator; the `OPERATIONAL`,
   `CORRECTION`, and `INVALIDATION` branches are closed and mutually exclusive;
   correction and invalidation have exact immutable lineage, deterministic
   identity and ordering, non-operational state-preserving semantics, and
   fail-closed current-state derivation; reason codes and free-form limitations
   never select or define a branch;
10. authority defaults denied and all required negative-authority distinctions are
   preserved;
11. all 32 ES-6 responsibilities have entry, exit, verification, continuity, and
    stop semantics;
12. evidence capture creates no circular or thirty-third responsibility;
13. repository creation, modification, staging, commit, publication, and
    integration remain separately authorized;
14. Phase 6C-3 has a prospective recovery path with no current semantic revision;
15. historical slices remain valid and reconstruction remains honest;
16. the exact six-file minimum normative implementation, Draft 2020-12 schema,
   authoritative prose, non-normative example, discoverability-only ES-6 change,
   derivative index change, and static tests are separated from deferred
   automation;
17. machine-checkable requirements and accountable-human judgments are distinct;
18. security and privacy prohibit excessive capture and define every tombstone
   field, deletion state, transition kind, structural correction and invalidation,
   immutable lineage, completion evidence, gate-specific consequences, and
   legal-hold precedence; `deletion_state` is excluded from `corrected_fields`,
   evidence supporting an unchanged state is correctable through closed
   `corrected_evidence.supported_claim`, and state-value change remains exclusive
   to `STATE_PROGRESSION`;
19. identity-churn examples distinguish semantic, operational, correction,
   location, and artifact-identity changes;
20. all internal references resolve to the intended sections;
21. risks and unresolved questions remain explicit;
22. the exact one-file scope and protected-candidate identity are preserved;
23. staged deletion preserves baseline identity and mode, treats stage-zero
   absence as expected only for deletion, and enforces the exact
   classification/worktree-state/divergence and recreated-content identity
   cross-product;
24. the single schema and example paths support all three artifact classes and
    the exact six-file future scope remains sufficient;
25. the Normative Contract Consistency Audit confirms that every referenced
    semantic field, discriminator, relationship, conditional rule, identity
    input or exclusion, and implementation requirement is declared and
    structurally representable without contradiction or orphaned fields;
26. all applicable quality gates pass against the exact candidate;
27. corrected semantic values use the exact four-member typed entry, bind the
    predecessor value, participate in canonical identity, remain separate from
    event metadata and evidence-only corrections, and cannot hide an operational
    transition; and
28. the closed composite state, exhaustive applicability matrix, sole-first-
    event rule, successor graph, exact effects, and fail-closed derivation make
    every operational event and current state uniquely executable;
29. actor, authority, assignment, content, package, ordinary-location,
    location-type, and limitations contracts are completely machine-
    representable with no additional properties or implementation invention; and
30. the matrix, successor graph, examples, tests, risks, and invariants all
    permit confirmation and retrievability confirmation during an active legal
    hold and after release, subject to unchanged predicates and without a new
    operational state; and
31. the successor graph contains every matrix-required release edge after a
    hold-preserving event and every matrix-permitted immediate successor of
    hold application, without admitting a prohibited edge or changing an event,
    state, predicate, or authority boundary.

Acceptance-criteria satisfaction does not approve the architecture or authorize
implementation.

## 24. Architecture-Revision Finding Disposition

| Finding | Disposition | Resolution location |
| --- | --- | --- |
| `ES7-AR-001` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 5.2, 6.2–6.6, 7, 18, 20, 21, and 23 define exact canonical bytes, schema evolution, identity effects, tests, risks, and invariants. |
| `ES7-AR-002` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 5.2, 7, 8.1–8.4, 18, 20, 21, and 23 define every binding mode, manifest, path/filter/filesystem semantics, and failure behavior. |
| `ES7-AR-003` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 5.2, 7, 11–11.1, 13, 18, 20, 21, and 23 define the closed retention vocabulary and separate assignment, retention, retrievability, admissibility, expiry, and deletion authority. |
| `ES7-AR-004` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 17–18 and 22–23 fix the exact six-file proposed boundary, Draft 2020-12 roles, static tests, current one-file scope, and withheld implementation. |
| `ES7-AR-005` — MINOR | Corrected. | Section 7 now cites reviewer identity and independence in Section 9 and evidence-origin sufficiency in Section 10; all section references were inspected after renumbering. |
| `ES7-AR-006` — MINOR | Resolved in revised candidate; fresh review required. | Sections 6.5, 7, 11.1, 18–21, and 23 define separate legal authority, immutable tombstones, payload-dependent non-admissibility, legal holds, tests, and risks. |
| `ES7-AR-007` — OBSERVATION | Considered without weakening semantic identity. | Sections 6.6, 18, and 20 define required conformance examples and treat churn through correction and supersession rather than mutation. |
| `ES7-AR-008` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 4–7, 11–11.1, 13, and 17–23 define immutable issuance-time retention, independently identified event kinds and fields, exact chain evaluation, relocation, correction, schema branches, tests, invariants, and gate consequences. |
| `ES7-AR-009` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 8.2–8.3, 18, and 23 define expected stage-zero absence only for valid deletion, baseline object/mode preservation, explicit non-applicable results, recreation divergence, and staged-only/mixed-manifest tests. |
| `ES7-AR-010` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 4, 6–7, 11.2, 13, and 17–23 define the complete tombstone contract, five states, identity, immutable lineage, ES-6 action boundary, legal hold, completion evidence, admissibility, schema/example support, tests, risks, and invariants. |
| `ES7-AR-011` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 6–7, 11.2, 18, 20–21, and 23 add exactly one required `deletion_state` discriminator, its closed vocabulary, identity participation, conditional schema branches, immutable correction rules, closed successor graph, admissibility effects, and tests. |
| `ES7-AR-012` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 6–7, 11.1–11.2, 18, 20–21, and 23 add the required semantic `deletion_tombstone_id` retention-event field, require it only for `DELETION_COMPLETED`, prohibit concrete use elsewhere, and define exact one-way non-circular validation, identity, schema, example, admissibility, and test behavior. |
| `ES7-AR-013` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 8.2–8.3, 18, 21, and 23 make the mixed-manifest entry contract a structural superset of every staged-deletion semantic and align stage-zero absence, non-applicable results, worktree state, divergence, and recreated identity without contradiction. |
| `ES7-AR-014` — MAJOR | Corrected in revised candidate; fresh review required. | Header, Sections 24–24.1, and Section 25 correct the canonical ES-1 state to `ARCHITECTURE_IN_REVIEW`, retain predecessor identity and finding attribution, and preserve `ARCHITECTURE_REVISION` with implementation withheld. |
| `ES7-AR-015` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 6–7, 11.1–11.2, 17–18, and 20–24 add exactly one tombstone transition discriminator, closed transition details, exact predecessor and same-state rules, canonical identity participation, schema/example/test requirements, admissibility, risks, invariants, and acceptance criteria. |
| `ES7-AR-016` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 8.2–8.3, 17–18, and 20–24 define and enforce one deterministic staged-deletion cross-product for absent and recreated worktree content in staged-only and mixed manifests. |
| `ES7-AR-017` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 11.2, 17–18, 20–21, and 23–24.1 exclude state and immutable transition fields from `corrected_fields`, distinguish evidence-only correction through closed `supported_claim`, reserve state change to `STATE_PROGRESSION`, and align identity, invalidation, examples, tests, risks, invariants, acceptance, and audits. |
| `ES7-AR-018` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 6–7, 11.1, 17–18, 20–21, and 23–24.1 add the single required `retention_event_transition_kind` discriminator, mutually exclusive closed operational/correction/invalidation branches, deterministic lineage and current-state derivation, identity, schema/example/test requirements, admissibility, risks, invariants, acceptance, and audits. |
| `ES7-AR-019` — BLOCKING | Resolved in revised candidate; fresh review required. | Sections 6–7, 11.1, 17–18, 20–21, and 23–24.1 replace field-name-only correction with exact typed identity-bearing corrected-value entries and a deterministic overlay algorithm. |
| `ES7-AR-020` — MAJOR | Resolved in revised candidate; fresh review required. | Sections 7, 11.1.1, 17–18, 20–21, and 23–24.1 define the closed composite state, exhaustive applicability matrix, first-event rule, successor graph, exact effects, and fail-closed derivation. |
| `ES7-AR-021` — BLOCKING | Resolved in revised candidate; fresh review required. | Sections 5.3, 6, 11.1, 17–18, 20–21, and 23–24.1 close `actor_identity`, `authority_reference`, and `limitations`, including exact members, applicability, vocabularies, constraints, ordering, identity, and additional-property prohibition. |
| `ES7-AR-022` — BLOCKING | Resolved in revised candidate; fresh review required. | Sections 11.1.1, 17–18, 20–21, and 23–24.1 consistently permit confirmation and retrievability confirmation during an active legal hold and after release under unchanged predicates. |
| `ES7-AR-023` — BLOCKING | Resolved in revised candidate; fresh review required. | Sections 5.3, 6, 11.1, 17–18, 20–21, and 23–24.1 completely define content, package, assignment-authority, authority-reference, actor, ordinary-location, and location-type representations. |
| `ES7-AR-024` — BLOCKING | Resolved in revised candidate; fresh review required. | Sections 11.1.1, 18, 20–21, and 23–24.1 make every matrix-required legal-hold release reachable and align all successor edges with the existing operational predicates. |

#### `ES7-AR-014` disposition record

- **Disposition:** `CORRECTED`; every authoritative current-state declaration is
  `ARCHITECTURE_IN_REVIEW`. The predecessor candidate SHA-256 is retained in the
  header, and the candidate identity changes because lifecycle state is semantic
  specification content.
- **Revised sections:** Header, this disposition, the consistency audit, and
  Section 25.
- **Preserved constraints:** The artifact remains an unapproved architecture
  draft/candidate; `ARCHITECTURE_APPROVED` is not claimed; ES-6 responsibility
  remains `ARCHITECTURE_REVISION`; implementation remains `WITHHELD`.
- **Audit verification:** Lifecycle declarations are compatible with the ES-6
  responsibility and no declaration implies a lifecycle transition or approval.
- **Remaining questions:** None for the lifecycle correction; approval quality
  and candidate sufficiency remain questions for independent review.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind the new
  candidate identity.

#### `ES7-AR-015` disposition record

- **Disposition:** `RESOLVED`; `tombstone_transition_kind` is the one required
  semantic transition discriminator with the closed vocabulary `INITIAL`,
  `STATE_PROGRESSION`, `CORRECTION`, and `INVALIDATION`.
- **Revised sections:** Sections 6–7, 11.1–11.2, 17–18, 20–21, 23, and 24.
- **Preserved constraints:** The established five-state `deletion_state`
  vocabulary, immutable tombstones, exact lineage, deny-by-default authority,
  legal-hold precedence, non-circular completion linkage, and six-file future
  implementation boundary remain unchanged.
- **Audit verification:** Transition kind, predecessor applicability, successor
  graph, same-state rules, correction/invalidation structure, identity inputs,
  schema branches, examples, tests, admissibility, invariants, acceptance
  criteria, and risks now agree without free-form inference.
- **Remaining questions:** Jurisdictional policy and deletion technology remain
  deferred; they do not weaken the structural contract.
- **Fresh-review requirement:** Fresh independent Tier 3 review must determine
  whether the closed structures and vocabularies are architecturally sufficient.

#### `ES7-AR-016` disposition record

- **Disposition:** `RESOLVED`; one observable staged-deletion state now maps to
  exactly one classification/worktree-state/divergence combination.
- **Revised sections:** Sections 8.2–8.3, 17–18, 20–21, 23, and 24.
- **Preserved constraints:** Baseline object and mode, expected stage-zero
  absence, explicit non-applicability, exact candidate identity, staged-only and
  mixed-manifest equivalence, and the six-file boundary remain unchanged.
- **Audit verification:** Absent worktree content maps only to
  `STAGED`/`ABSENT`/`false`; recreated content maps only to
  `STAGED_AND_UNSTAGED`/`RECREATED`/`true` with exact worktree identity. Opposite
  pairings and observationally equivalent alternative classifications are
  prohibited across prose, schema, examples, tests, admissibility, identity, and
  acceptance criteria.
- **Remaining questions:** None for classification determinism; platform-specific
  inability to bind exact bytes, object identity where applicable, length, or
  mode remains a fail-closed admissibility condition.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete revised candidate.

#### `ES7-AR-017` disposition record

- **Disposition:** `RESOLVED`; `CORRECTION` preserves the predecessor
  `deletion_state`, and the closed `corrected_fields` vocabulary excludes
  `deletion_state` and all immutable tombstone identity, transition, and lineage
  fields. Evidence supporting an unchanged state is corrected only through
  `corrected_evidence` with `supported_claim=DELETION_STATE`.
- **Revised sections:** Sections 11.2, 17–18, 20–21, 23, 24, and 24.1.
- **Semantic choice adopted:** Semantic-value corrections and supporting-evidence
  corrections are distinct closed structures. `STATE_PROGRESSION` is the only
  transition kind that may change state. An erroneous prior state claim requires
  attributable invalidation plus a separate conforming replacement or successor
  record; invalidation does not silently supply it.
- **Preserved constraints:** ES7-AR-014 and ES7-AR-016 remain resolved; the five
  deletion states, four transition kinds, immutable lineage, deterministic
  staged-deletion classification, evidence/authority separation, deny-by-default
  authority, all 32 ES-6 mappings, exact six-file future boundary, Phase 6C-3
  byte identity, and security/privacy restrictions are unchanged.
- **Audit verification:** The focused correction-contract audit confirms the
  closed vocabularies, same-state rules, structural evidence correction,
  identity participation, deterministic ordering, duplicate rejection,
  invalidation boundary, and exclusive progression rule. The document-wide
  audit confirms no contradiction or orphaned field was introduced.
- **Remaining questions:** None for ES7-AR-017. Previously deferred jurisdiction,
  deletion-technology, cryptographic-erasure, storage, and accountable-evidence
  sufficiency questions remain unchanged and non-authorizing.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind the new
  candidate identity and independently verify ES7-AR-017, both consistency
  audits, the complete architecture, the six-file future boundary, and Phase
  6C-3 byte preservation.

#### `ES7-AR-018` disposition record

- **Disposition:** `RESOLVED`; every retention event now has exactly one required
  `retention_event_transition_kind` selected from `OPERATIONAL`, `CORRECTION`, or
  `INVALIDATION`, with a mutually exclusive closed structural branch.
- **Revised sections:** Header, Sections 6–7, 11.1, 17–18, 20–21, 23, 24, 24.1,
  and 25.
- **Semantic structure adopted:** Ordinary event kinds occur only in
  `OPERATIONAL`. `CORRECTION` uses the exact closed `correction_details` object;
  `INVALIDATION` uses the exact closed `invalidation_details` object. Inactive
  branches are explicit `NOT_APPLICABLE`; all branch semantics and collections
  participate in deterministic identity; correction and invalidation are
  immutable non-operational overlays and never independently become current
  operational state or select a replacement.
- **Preserved architecture:** ES7-AR-014 through ES7-AR-017 remain resolved;
  deletion-tombstone progression, correction, invalidation, and staged-deletion
  classification remain deterministic; lifecycle records, retention events, and
  tombstones remain immutable; exact artifact binding, evidence/authority
  separation, deny-by-default authority, all 32 ES-6 mappings, the exact six-file
  future implementation boundary, Phase 6C-3 byte identity, and security/privacy
  restrictions are unchanged.
- **Focused audit result:** `PASS`; one explicit discriminator selects each
  branch, `reason_code` is not that discriminator, ordinary event kinds are
  operational-only, both non-operational objects are closed and exact, inactive
  branches are explicit, all fields and closed vocabularies are declared once,
  all identity-bearing collections have deterministic ordering and duplicate
  rejection, no free-form text carries structural meaning, correction cannot
  change operational state, invalidation cannot create a replacement, and later
  operational change requires a separate event with fail-closed lineage.
- **Complete consistency-audit result:** `PASS`; the complete candidate has no
  undeclared reference, orphaned field, duplicate semantic declaration,
  contradictory branch, identity ambiguity, unsupported schema/example/test
  requirement, new ES-6 responsibility, or implementation-boundary expansion.
- **Remaining questions:** None for ES7-AR-018. Previously deferred jurisdiction,
  deletion-technology, cryptographic-erasure, storage, and accountable-evidence
  sufficiency questions remain unchanged and non-authorizing.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind the new
  candidate identity and independently verify ES7-AR-018, both audits, the
  complete architecture, the exact six-file future boundary, all 32 mappings,
  and Phase 6C-3 byte preservation.

#### `ES7-AR-019` disposition record

- **Disposition:** `RESOLVED`; `corrected_fields` now carries exact typed
  predecessor-bound replacement values rather than field-name tokens.
- **Revised sections:** Header, Sections 11.1, 18, 24, 24.1, and 25, with
  narrowly necessary consistency updates to identity, admissibility, risks,
  invariants, and acceptance criteria.
- **Semantic structure adopted:** Each closed entry has exactly `field_name`,
  `prior_value_identity`, `corrected_value`, and `correction_value_schema`;
  canonical ordering, duplicate rejection, metadata separation, and the
  correction-overlay algorithm are normative.
- **Preserved architecture:** `corrected_evidence` remains the distinct support-
  only mechanism; correction remains immutable and non-operational; operational-
  state-bearing changes require separate operational events. ES7-AR-014 through
  ES7-AR-018, tombstone semantics, staged-deletion classification, all 32 ES-6
  mappings, the six-file boundary, Phase 6C-3 bytes, and security/privacy remain
  unchanged.
- **Focused audit result:** `PASS`; every eligible semantic field has a typed
  carrier and predecessor identity, all members participate in canonical
  identity, metadata is separate, evidence-only correction is distinct, and
  hidden operational transitions, duplicates, ambiguity, forks, and cycles fail
  closed. No implementation decision remains.
- **Complete consistency-audit impact:** `PASS`; the new members are declared,
  identity-bearing, schema-addressable, testable, and not orphaned.
- **Remaining questions:** None for ES7-AR-019; previously deferred policy and
  technology questions remain non-authorizing.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete new candidate identity.

#### `ES7-AR-020` disposition record

- **Disposition:** `RESOLVED`; all eleven ordinary event kinds now have one
  exhaustive applicability row and one closed operational-state interpretation.
- **Revised sections:** Header, Sections 11.1.1, 18, 24, 24.1, and 25, with
  narrowly necessary consistency updates to identity, admissibility, risks,
  invariants, and acceptance criteria.
- **Semantic structure adopted:** One seven-dimension closed composite state,
  `RETENTION_ASSIGNED` as the sole first event, a complete successor graph,
  exact concrete/`NOT_APPLICABLE` requirements, exact per-event effects, and
  deterministic fail-closed current-state derivation.
- **Preserved architecture:** The three mutually exclusive transition branches,
  immutable events, non-operational overlays, exact tombstone linkage, legal-hold
  precedence, expiration without deletion authority, all prior resolved
  findings, all 32 mappings, the six-file boundary, Phase 6C-3 bytes, and
  security/privacy remain unchanged.
- **Focused audit result:** `PASS`; every event, state dimension, first-event
  rule, successor, field applicability, reason, interaction, repetition rule,
  and resulting effect is closed and uniquely executable; invalid combinations
  enter `BLOCKED_DISCREPANT`. No “as applicable” ambiguity remains.
- **Complete consistency-audit impact:** `PASS`; prose, future schema, examples,
  tests, identity, lineage, and admissibility requirements support the same
  operational contract without a new artifact or responsibility.
- **Remaining questions:** None for ES7-AR-020; storage, jurisdiction, deletion
  technology, and accountable evidence sufficiency remain deferred.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete new candidate identity.

#### `ES7-AR-021` disposition record

- **Disposition:** `RESOLVED`; `actor_identity`, `authority_reference`, and
  `limitations` now have one authoritative closed structural contract.
- **Structural result:** Exact required members, closed vocabularies,
  cross-member constraints, deterministic ordering, identity participation,
  status handling, and additional-property prohibition are explicit.
- **Preserved architecture:** Existing attribution, accountable-human authority,
  non-authorizing evidence, bounded limitations, immutability, all 32 ES-6
  mappings, and the six-file boundary remain unchanged.
- **Focused audit result:** `PASS`; the three objects are machine-representable,
  declared once, referenced consistently, and require no implementation choice.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete new candidate identity.

#### `ES7-AR-022` disposition record

- **Disposition:** `RESOLVED`; confirmation and retrievability confirmation are
  permitted both during an active legal hold and after its release whenever the
  existing applicability predicates hold.
- **Consistency result:** The applicability matrix remains unchanged; the
  successor graph now contains the matching edges, and prose, examples, tests,
  risks, invariants, and acceptance criteria state the same model.
- **Preserved architecture:** Both events preserve legal-hold state and grant no
  deletion, cleanup, release, or other later authority. No operational state or
  event kind was added.
- **Focused audit result:** `PASS`; all four required hold/confirmation cases
  have one deterministic answer and invalid predicate combinations fail closed.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete new candidate identity.

#### `ES7-AR-023` disposition record

- **Disposition:** `RESOLVED`; content identity, package identity, assignment
  authority, authority reference, actor identity, ordinary location identity,
  and location type are completely machine-representable.
- **Structural result:** Every object has exact required members, closed values
  where applicable, value and correspondence constraints, deterministic
  ordering, identity participation, and prohibited additional properties.
- **Preserved architecture:** Exact bytes, package-manifest identity,
  accountable assignment, attributable authority, immutable/content-addressed
  location, model neutrality, and deny-by-default authority are unchanged.
- **Focused audit result:** `PASS`; every reference resolves to one structural
  definition and no implementation-defined object shape remains.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete new candidate identity.

#### `ES7-AR-024` disposition record

- **Disposition:** `RESOLVED`; the successor graph now contains
  `LEGAL_HOLD_RELEASED` after every event kind that can preserve
  `legal_hold_state=ACTIVE_HOLD` under the existing applicability matrix.
- **Consequential consistency result:** `LEGAL_HOLD_APPLIED` also contains the
  previously omitted `RETENTION_RELOCATED` and `DELETION_AUTHORIZED` successors
  required by the unchanged matrix predicates. No operational state, event kind,
  predicate, effect, or authority boundary changed.
- **Preserved architecture:** Legal-hold precedence, irreversible completed
  deletion, expiration without deletion authority, immutable event lineage,
  deterministic identity, all 32 ES-6 mappings, the six-file boundary, Phase
  6C-3 bytes, prospective adoption, and security/privacy boundaries are
  unchanged.
- **Focused legal-hold transition audit:** `PASS`; every permitted operational
  sequence remains reachable, every legal nonterminal hold state has a
  deterministic release path where the matrix permits release, all required
  release edges exist, all predicate-invalid and post-completion edges remain
  prohibited, and no contradictory transition rule remains.
- **Complete consistency-audit result:** `PASS`; the matrix, graph, operational
  semantics, invariants, examples, tests, risks, acceptance criteria, and this
  disposition use one transition model without implementation discretion or
  scope expansion.
- **Fresh-review requirement:** Fresh independent Tier 3 review must bind and
  assess the complete revised candidate identity and independently verify
  ES7-AR-024 and both consistency audits.

### 24.1 Normative Contract Consistency Audit

The focused identity-contract audit for ES7-AR-021 and ES7-AR-023 completed with
result `PASS`. Actor, authority, assignment, content, package, ordinary-location,
location-type, and limitations values each have one authoritative definition;
all members, applicability forms, vocabularies, constraints, ordering rules,
identity effects, and additional-property prohibitions are explicit. Every use
resolves to that definition and no implementation must invent object structure.

The focused legal-hold transition audit for ES7-AR-022 completed with result
`PASS`. Confirmation and retrievability confirmation may each occur during an
active legal hold and after legal-hold release when the existing matrix
predicates hold. Each preserves legal-hold state. The applicability matrix,
successor graph, examples, tests, risks, invariants, and acceptance criteria use
that one model, introduce no state, and grant no later authority.

The focused legal-hold transition audit for ES7-AR-024 completed with result
`PASS`. For every reachable composite state with `ACTIVE_HOLD` and deletion not
completed, the predecessor event kind has a `LEGAL_HOLD_RELEASED` edge whenever
the unchanged release predicates hold. `LEGAL_HOLD_APPLIED` exposes every
immediately matrix-permitted successor, including relocation and deletion
authorization. All matrix-prohibited, predicate-invalid, repeated, and
post-completion edges remain prohibited. No legal operational sequence is
stranded and no new state, event kind, predicate, effect, recovery rule, or
authority was introduced.

The focused operational-object audit completed with result `PASS`. All named
operational objects and scalars are closed, schema-addressable, identity-bearing
as declared, deterministically ordered where collection order applies, and
reject additional properties, unknown tokens, incomplete objects, and invalid
cross-member combinations.

The focused corrected-value representation audit for ES7-AR-019 completed with
result `PASS`. Every corrected semantic field has an exact typed value carrier
and predecessor-value identity; corrected values and their closed schema tokens
participate in canonical identity; correction-event metadata is structurally
separate; operational-state-bearing semantic changes are prohibited; evidence-
only correction remains distinct; ordering and duplication rules are exact; and
the overlay algorithm is uniquely executable and fail-closed.

The focused operational transition audit for ES7-AR-020 completed with result
`PASS`. Every ordinary event kind has one complete row; all seven state
dimensions have closed vocabularies and initial values; first-event eligibility,
the successor graph, exact resulting effects, concrete/`NOT_APPLICABLE` fields,
reason tokens, repetition rules, and hold/expiry/deletion/location/retrievability
interactions are closed; current-state derivation is unique; and every invalid
combination fails closed.

The focused retention-event contract audit completed for ES7-AR-018 with result
`PASS`. It confirmed that `retention_event_transition_kind` is the single
required branch discriminator and `reason_code` is not; ordinary event kinds are
confined to `OPERATIONAL`; `CORRECTION` and `INVALIDATION` are non-operational;
all three branches and both detail objects are mutually exclusive, closed, and
exact; inactive branches are explicit `NOT_APPLICABLE`; all fields and
vocabularies are declared exactly once; all identity-bearing collections have
exact ordering and duplicate-key rejection; no correction or invalidation
semantics rely on free-form text; correction cannot silently change current
retention state; invalidation cannot silently create or select a replacement;
actual operational change requires a separate event; and event-chain derivation
remains deterministic and fail-closed for missing, cyclic, forked, stale,
invalidated, or contradictory lineage.

The mandatory document-wide audit completed after the final targeted
disposition with result `PASS`. It confirmed that:

- every authoritative lifecycle declaration uses `ARCHITECTURE_IN_REVIEW`, which
  is compatible with active ES-6 responsibility `ARCHITECTURE_REVISION`, and
  implementation authorization remains `WITHHELD`;
- each semantic field used by a lifecycle record, package manifest, retention
  event, deletion tombstone, and candidate-manifest entry is declared in that
  artifact's one authoritative contract;
- all shared identity, authority, location, and limitations values resolve to
  the single closed Section 5.3 contract, with no orphaned or competing shape;
- `artifact_type`, `lifecycle_status`, `retention_event_transition_kind`,
  `event_kind`, `deletion_state`, `tombstone_transition_kind`, candidate entry
  `state`, and `classification` provide every required discriminator;
- predecessor, correction, supersession, retention-event, deletion-tombstone,
  governed-artifact, payload, package, rename, and worktree references all have
  corresponding structural fields;
- explicit status objects and state- or event-kind-specific schema branches can
  represent every conditional rule without omission standing for
  non-applicability;
- every correction, invalidation, and progression mechanism is structurally
  represented, including the mutually exclusive retention-event correction and
  invalidation details and tombstone transition details;
- every required relationship, including deletion authorization, tombstone
  correction, invalidation, progression, deletion completion, and staged
  deletion, is machine-
  representable without a canonical-identity cycle;
- normative cross-references resolve to the intended contracts and no prose
  depends on undeclared semantic data;
- every canonical identity input is declared, while `payload_location` and the
  operational storage fields excluded by Section 6.4 remain explicitly excluded;
- every retention-event and tombstone correction/invalidation collection and
  member participates in identity, is deterministically ordered, rejects
  duplicate semantic keys, and excludes only explicitly declared immutable,
  binding, discriminator, lineage, or state fields;
- the one-schema, one-example, and static-test implementation requirements can
  represent and check all three record branches and the manifest semantics;
- all 32 canonical ES-6 responsibility tokens remain represented by the
  per-responsibility evidence contract, with no thirty-third responsibility;
- no contract field is orphaned, no duplicate authoritative field definition
  remains, and the staged-only and mixed-manifest deletion definitions enforce
  the same exact observable-state cross-product;
- the exact six-file future implementation boundary remains sufficient and no
  architecture scope expansion is required; and
- legal-hold confirmation behavior is identical across the applicability
  matrix, successor graph, examples, tests, risks, invariants, and acceptance
  criteria, with no new event kind or state; and
- every release transition required by the operational applicability matrix is
  present in the successor graph, every legal nonterminal hold state has the
  required deterministic successor path, every prohibited edge remains
  prohibited, and no contradictory transition rule remains.

No unresolved normative contract inconsistency remains in this candidate. The
focused corrected-value representation audit, focused operational transition
audit, and complete document-wide audit all pass. The audit additionally
confirmed that every cross-artifact reference has a field, every conditional
rule is machine-representable, every semantic and identity field is declared,
all identity-bearing collections are ordered, no prose requires undeclared data,
no contract field is orphaned, all internal references resolve, all 32 canonical
ES-6 tokens remain represented without a thirty-third, and the exact six-file
future implementation boundary remains sufficient.
This is architecture-revision evidence, not independent review, architecture
approval, or implementation authorization.

The targeted dispositions preserve one lifecycle record per ES-6 responsibility,
deny-by-default authority, immutable lineage, legal-hold precedence, retention
expiry without deletion authority, and the exact six-file future implementation
boundary. No subordinate artifact is an ES-6 responsibility. Remaining policy
questions are jurisdictional duration, deletion technology, cryptographic
erasure, storage implementation, and the accountable sufficiency of evidence;
all remain deferred and non-authorizing. Fresh independent Tier 3 review of the
complete candidate is required.

No disposition is architecture approval. The reviser has not conducted renewed
independent review. The revised candidate is prepared for a fresh independent
Tier 3 `ARCHITECTURE_REVIEW` against its new exact identity.

The `architecture_revision checkpoint` consists of the baseline commit, old and
new candidate SHA-256 identities, protected Phase 6C-3 SHA-256, exact one-file
revision scope, finding dispositions, gate commands and results, unresolved
questions, and all authority withheld. It is completed by the bounded revision
report; it does not approve this document or authorize review, implementation,
retention, or any repository transition.

## 25. Lifecycle Posture and Architectural Decision

**Document status:** Revised architecture candidate; prepared for fresh independent review
**ES-1 lifecycle state:** `ARCHITECTURE_IN_REVIEW`
**ES-6 responsibility state:** `ARCHITECTURE_REVISION`
**Implementation authorization:** `WITHHELD`

ES-7 proposes a prospective, documentation-first evidence architecture built on
one immutable, deterministic record per ES-6 responsibility occurrence and
optional packages of independently identified records. It binds exact governed
artifacts, preserves reconstruction and correction lineage, requires explicit
reviewer-independence evidence, and makes every authority effect deny-by-default
and non-transitive.

This targeted `ARCHITECTURE_REVISION` is complete for the revised candidate. The
document remains an architecture draft and is not approved. The next recommended
responsibility is a fresh independent Tier 3
`ARCHITECTURE_REVIEW` of this exact candidate. That recommendation does not grant
review authority, approve the candidate, advance ES-1, or authorize any later
work. The accountable human must next explicitly authorize `ARCHITECTURE_REVIEW`
for the exact ES-7 candidate identity, name the review scope and independence
requirement, and continue to withhold modification, approval, implementation,
and repository-transition authority unless separately granted.
