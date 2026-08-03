# Lifecycle Evidence, Retention, and Identity Standard

**Standard identity:** `Engineering-System-Lifecycle-Evidence-Retention-and-Identity-Standard`
**Schema version:** `1.0.0`
**Lifecycle relationship:** subordinate to the Engineering Kernel and Engineering Lifecycle Standard
**Authority effect:** none

## Purpose and boundary

This standard defines immutable, deterministic evidence for one occurrence of
an Engineering Lifecycle responsibility, its retention history, and deletion
tombstones. It implements approved ES-7 architecture. It does not perform work,
decide truth or admissibility, grant authority, transition lifecycle state,
persist evidence, select storage, or authorize migration, redirection, cleanup,
deletion, certification, or product operation.

The words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative. The
companion Draft 2020-12 schema is the machine-readable structural contract.
Where semantics cannot be decided structurally, this standard remains
authoritative and accountable-human judgment remains required.

## Artifact classes

`artifact_type` MUST be exactly `LIFECYCLE_EVIDENCE_RECORD`,
`RETENTION_EVENT_RECORD`, or `DELETION_TOMBSTONE`. A lifecycle record represents
exactly one of the 32 canonical ES-6 responsibilities. Retention events and
tombstones are subordinate evidence and never create a thirty-third
responsibility. An optional package manifest has exactly `schema_version`,
`package_id`, `record_ids`, `payload_references`, `package_scope`,
`creation_mode`, and `authority_neutrality`; packaging never combines authority
or establishes lifecycle order.

All objects are closed. Required inapplicable or unavailable values use exactly
`{"status":"NOT_APPLICABLE","reason_code":"FIELD_NOT_APPLICABLE"}` or
`{"status":"UNAVAILABLE","reason_code":"EVIDENCE_UNAVAILABLE"}`. Omission,
empty values, and `null` are not substitutes.

## Canonical JSON and identity

Canonical input MUST be UTF-8 without BOM, valid Unicode already in NFC, and
contain unique object keys. Implementations MUST reject malformed Unicode,
normalization collisions, numbers, escaped solidus, non-ASCII `\\u` escapes,
noncanonical whitespace, and a trailing newline. Object keys sort by Unicode
scalar value. Serialization uses `ensure_ascii=false`, compact `,` and `:`, and
no insignificant whitespace. Timestamps are UTC RFC 3339 with exactly six
fractional digits. Decimal quantities are strings: `0` or a nonzero digit
followed by digits.

Sequence arrays preserve declared order. Set-like arrays use their declared
stable key and reject duplicates. Paths use repository-relative `/` separators,
are NFC, contain no empty, `.`, or `..` component, and sort by UTF-8 bytes.
Findings and dispositions sort by stable ID; authority tokens use the Section
13 ES-6 row order; package record IDs sort lexically; payload references sort by
SHA-256 then media type.

For a lifecycle record, omit only `evidence_record_id`, canonicalize, hash with
SHA-256, and prefix `ES-EVIDENCE-RECORD-SHA256-`. For a retention event omit only
`retention_event_id` and prefix
`ES-EVIDENCE-RETENTION-EVENT-SHA256-`. For a tombstone omit only
`deletion_tombstone_id` and prefix
`ES-EVIDENCE-DELETION-TOMBSTONE-SHA256-`. Digests are 64 lowercase hexadecimal
characters. Every other schema field is semantic unless explicitly identified
as an operational payload locator. Issued artifacts are immutable; corrections,
invalidations, and supersession create new identities with predecessor lineage.
Unsupported schema versions fail closed and MUST NOT be reinterpreted.

## Shared values

An `actor_identity` contains exactly `actor_id`, `actor_type`, `actor_role`, and
`display_name`. Actor type is `ACCOUNTABLE_HUMAN`, `HUMAN`, `AI_MODEL`, or
`SOFTWARE_SERVICE`; role is `ACCOUNTABLE_HUMAN`, `PREPARER`, `EXECUTOR`,
`REVIEWER`, `DECISION_RECORDER`, or `OBSERVER`. Only an accountable human may
use the accountable-human role.

An `authority_reference` contains exactly `authority_id`, `authority_kind`,
`issuer_actor_id`, `governed_scope`, and `source_identity`. Its kind is
`ACCOUNTABLE_HUMAN_AUTHORIZATION`, `GOVERNANCE_ARTIFACT`, `LEGAL_AUTHORITY`,
`RETENTION_ASSIGNMENT`, or `DELETION_AUTHORIZATION`. It MUST resolve to an
accountable issuer and never expands its governed scope.

A `content_identity` contains exactly lowercase `sha256`, lowercase
`media_type`, and decimal-string `byte_length`. A `location_identity` contains
exactly `location_scheme` and `location_value`; scheme is
`REPOSITORY_RELATIVE`, `CONTENT_ADDRESSED`, or `EXTERNAL_IMMUTABLE` and MUST
agree with location type `REPOSITORY_PATH`, `CONTENT_ADDRESS`, or
`EXTERNAL_IMMUTABLE_OBJECT` respectively. Credentials are prohibited.

`limitations` contains exactly `status`, `entries`, and `reason_code`. `NONE`
requires an empty list and `NONE`; `PRESENT` requires nonempty unique sorted
entries and `BOUNDED_LIMITATIONS_RECORDED`; `UNAVAILABLE` requires an empty list
and `LIMITATIONS_UNAVAILABLE`; `NOT_APPLICABLE` requires an empty list and
`FIELD_NOT_APPLICABLE`.

## Lifecycle evidence record

The schema requires every Section 5 ES-7 field and closes the object.
`schema_version` is `1.0.0`. `lifecycle_responsibility` is exactly one canonical
ES-6 token. `evidence_origin_state` is `CONTEMPORANEOUS`,
`RECONSTRUCTED_VERIFIED`, `RECONSTRUCTED_PARTIAL`, or `UNVERIFIED_REFERENCE`.
Reconstruction uses its actual completion time, identifies gaps, never
backdates, and cannot masquerade as current independent or authority evidence.

Artifact binding MUST select exactly one explicit mode: committed, uncommitted,
staged, untracked, mixed manifest, published, or external. It binds the full
baseline, exact path/scope, bytes or immutable Git objects, modes, and
worktree/index classification applicable to that mode. Ambiguity, conflict,
missing bytes, path collision, unproved filters, or contradictory classifications
make the record non-admissible. A staged deletion preserves the baseline object
and mode, requires stage-zero and result values to be `NOT_APPLICABLE`, and is
exactly `STAGED`/`ABSENT`/`false` or
`STAGED_AND_UNSTAGED`/`RECREATED`/`true` with concrete recreated identity.

`authority_granted` and `authority_withheld` are duplicate-free arrays using
only the 32 ES-6 tokens in their canonical lifecycle order. Granted authority
defaults empty and only attributable human evidence may populate it. The exact
required `non_authorizing_evidence_statement` is
`EVIDENCE_IDENTITY_AND_RETENTION_DO_NOT_GRANT_AUTHORITY_V1`.

## Retention

Retention classes are `TRANSIENT_CHECKPOINT`, `SLICE_LIFECYCLE`,
`REPOSITORY_LIFETIME`, and `GOVERNANCE_PERMANENT`. Issuance assignment state is
`PROPOSED` or `ASSIGNED_PENDING_RETENTION`. Issuance, assignment, confirmation,
retrievability, relocation, failure, restoration, expiry, legal hold, deletion
authorization, and deletion completion remain separate. Expiry never authorizes
deletion and legal hold blocks deletion completion.

A retention event declares transition kind `OPERATIONAL`, `CORRECTION`, or
`INVALIDATION`. Only `OPERATIONAL` has an ordinary event kind:
`RETENTION_ASSIGNED`, `RETENTION_CONFIRMED`, `RETRIEVABILITY_CONFIRMED`,
`RETENTION_RELOCATED`, `RETENTION_UNAVAILABLE`, `RETENTION_RESTORED`,
`RETENTION_EXPIRED`, `DELETION_AUTHORIZED`, `DELETION_COMPLETED`,
`LEGAL_HOLD_APPLIED`, or `LEGAL_HOLD_RELEASED`. Its reason code MUST be the exact
event-kind mapping in the schema. `DELETION_COMPLETED` alone requires a concrete
`deletion_tombstone_id`; all others require explicit non-applicability.

Corrections and invalidations require an immediate predecessor, have no ordinary
event kind, preserve operational state, and cannot relocate, alter hold,
retrievability, expiry, assignment, or deletion. Corrected semantic fields and
corrected evidence use the closed schema vocabularies and deterministic order.
Invalidation identifies invalidated claims and never supplies replacement state.
The event chain MUST be single, acyclic, and predicate-valid. Missing, forked,
cyclic, stale, or contradictory lineage fails closed.

Legal-hold application has precedence. Confirmation and retrievability
confirmation may preserve an active hold. Every hold-preserving event may be
followed by `LEGAL_HOLD_RELEASED` only with attributable release authority and
unchanged predicates. Release grants no deletion authority. No operational
event follows completed deletion.

## Deletion tombstones

`deletion_state` is `DELETION_AUTHORIZED`, `DELETION_IN_PROGRESS`,
`DELETION_COMPLETED`, `DELETION_FAILED`, or
`DELETION_BLOCKED_BY_LEGAL_HOLD`. Transition kind is `INITIAL`,
`STATE_PROGRESSION`, `CORRECTION`, or `INVALIDATION`. Initial has no predecessor;
progression requires one predecessor and changes state along the permitted
graph; correction and invalidation require one predecessor and preserve state.

Completed deletion alone has a completion timestamp, method, and evidence; it
requires no active hold and retrievability `DELETED`. Authorized deletion claims
no execution. In-progress and failed states preserve partial or unknown
retrievability. A held deletion cannot claim completion. `deletion_state` is
never a corrected field; supporting evidence for an unchanged state may be
corrected through `corrected_evidence.supported_claim=DELETION_STATE`. Only
`STATE_PROGRESSION` changes the state value. Tombstones retain non-sensitive
identity and lineage, never deleted payload bytes, and remain
`GOVERNANCE_PERMANENT` unless stricter law applies.

## Attribution, authority, and admissibility

Independent review records require reviewer identity, role, preparation/revision
disclosures, shared-context exposure, conflicts, evidence examined, rationale,
and conclusion `INDEPENDENT`, `NOT_INDEPENDENT`, or `INDETERMINATE`. A new model,
session, or process does not establish independence. Unavailable identity or an
indeterminate conclusion is inadmissible for a gate requiring independence.

Review is not approval; approval is not implementation authorization;
implementation approval is not commit; commit is not publication; publication
is not integration; integration is not closeout; closeout is not certification;
and certification is not operational authority. Evidence of an action may prove
state but not retrospective authorization. Truth, attribution, independence,
admissibility, approval, authorization, retention sufficiency, legal posture,
and every destructive decision remain accountable-human judgments.

## Privacy, validation, and conformance

Credentials, secrets, cookies, keys, hidden reasoning, unrestricted transcripts,
unnecessary absolute paths, broad environment dumps, and unrelated sensitive
content are prohibited. Payload references bind exact digest, media type, byte
length, source, transformation, and limitations without copying excessive data.

Conformance requires schema closure, canonical identity fixtures, positive and
negative branch fixtures, exact vocabularies, deterministic ordering, immutable
lineage, fail-closed unknowns, authority separation, legal-hold precedence, and
the static consistency checks maintained with the schema. Structural validity
does not establish evidentiary truth or authorize any lifecycle transition.

Validation order is deterministic and fail-closed: decode exact UTF-8 with
duplicate-key detection; validate canonical input bytes; validate the supported
Draft 2020-12 schema branch; recompute the artifact identity; validate stable-ID
uniqueness and canonical collection order; resolve shared actor, authority,
package, location, and content correspondences; traverse predecessor lineage;
apply correction or invalidation overlays; derive operational state; verify
tombstone and completion linkage; then evaluate gate-specific admissibility.
Failure or unavailability at any earlier step stops later evaluation and yields
non-admissibility or `BLOCKED_DISCREPANT`; it never selects a permissive branch.

The schema enforces closed artifact and transition branches, discriminators,
field presence, concrete versus status-object applicability, value-object
shapes, vocabularies, identifier forms, binding-mode cross-products,
event-kind field cross-products, typed correction values, correction versus
invalidation exclusivity, tombstone completion fields, and permitted tombstone
state-progression pairs. Static tests enforce invariants that JSON Schema cannot
establish from one instance: canonical array order by architecture-specific
keys, stable-ID uniqueness beyond whole-item equality, recomputed semantic and
manifest identities, shared actor/authority/location agreement, predecessor
existence, single-chain continuity, forks, cycles, stale correction targets,
overlay application, operational successor predicates, legal-hold state,
unchanged retained binding and retention class, tombstone predecessor-state
agreement, and deletion-authorization/completion correspondence. These tests do
not weaken or replace accountable-human evidentiary judgment.

The repository dependency policy currently provides no general-purpose JSON
Schema Draft 2020-12 validator. The authorized static tests therefore separate
JSON parsing, schema-structure inspection, contract-specific structural checks,
cross-record semantic validation, raw canonical-byte validation, and identity
recomputation. Those checks are not represented as Draft 2020-12 meta-schema
validation or as a general-purpose JSON Schema interpreter. Meta-schema
validation remains an explicit environment/tooling limitation until a validator
is separately authorized within repository dependency policy.
