import hashlib
import importlib.util
import json
import re
import unicodedata
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
SCHEMA_PATH = ROOT / "docs/engineering-system/schemas/lifecycle-evidence-record.schema.json"
EXAMPLE_PATH = ROOT / "docs/engineering-system/examples/lifecycle-evidence-record.example.json"
STANDARD_PATH = ROOT / (
    "docs/engineering-system/standards/Lifecycle-Evidence-Retention-and-Identity-Standard.md"
)
ES6_PATH = ROOT / "docs/engineering-system/standards/Engineering-Lifecycle-Standard.md"
NON_AUTHORIZING = "EVIDENCE_IDENTITY_AND_RETENTION_DO_NOT_GRANT_AUTHORITY_V1"


@pytest.fixture(scope="module")
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def corpus():
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def examples(corpus):
    return [fixture["artifact"] for fixture in corpus["positive_fixtures"]]


def _resolve(root, reference):
    assert reference.startswith("#/")
    node = root
    for part in reference[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def _matches(instance, rule, root):
    try:
        _validate(instance, rule, root)
    except AssertionError:
        return False
    return True


def _validate(instance, rule, root):
    if "$ref" in rule:
        _validate(instance, _resolve(root, rule["$ref"]), root)
        return
    if "oneOf" in rule:
        assert sum(_matches(instance, branch, root) for branch in rule["oneOf"]) == 1
    if "anyOf" in rule:
        assert any(_matches(instance, branch, root) for branch in rule["anyOf"])
    if "allOf" in rule:
        for branch in rule["allOf"]:
            _validate(instance, branch, root)
    if "if" in rule:
        selected = "then" if _matches(instance, rule["if"], root) else "else"
        if selected in rule:
            _validate(instance, rule[selected], root)
    if "const" in rule:
        assert instance == rule["const"]
    if "enum" in rule:
        assert instance in rule["enum"]
    if "not" in rule:
        assert not _matches(instance, rule["not"], root)
    declared_type = rule.get("type")
    if declared_type:
        allowed = declared_type if isinstance(declared_type, list) else [declared_type]
        checks = {
            "array": lambda value: isinstance(value, list),
            "boolean": lambda value: isinstance(value, bool),
            "object": lambda value: isinstance(value, dict),
            "string": lambda value: isinstance(value, str),
        }
        assert any(checks[kind](instance) for kind in allowed)
    if isinstance(instance, str):
        assert len(instance) >= rule.get("minLength", 0)
        if "pattern" in rule:
            assert re.fullmatch(rule["pattern"], instance)
    if isinstance(instance, list):
        assert len(instance) >= rule.get("minItems", 0)
        assert len(instance) <= rule.get("maxItems", len(instance))
        if rule.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True) for item in instance]
            assert len(encoded) == len(set(encoded))
        if "items" in rule:
            for item in instance:
                _validate(item, rule["items"], root)
    if isinstance(instance, dict):
        assert len(instance) >= rule.get("minProperties", 0)
        for key in rule.get("required", []):
            assert key in instance
        properties = rule.get("properties", {})
        if rule.get("additionalProperties") is False:
            assert set(instance) <= set(properties)
        for key, subrule in properties.items():
            if key in instance:
                _validate(instance[key], subrule, root)


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def _assert_canonical_value(value):
    if isinstance(value, dict):
        for key, child in value.items():
            assert unicodedata.is_normalized("NFC", key)
            assert all(
                not (0xFDD0 <= ord(char) <= 0xFDEF or ord(char) & 0xFFFF in {0xFFFE, 0xFFFF})
                for char in key
            )
            _assert_canonical_value(child)
    elif isinstance(value, list):
        for child in value:
            _assert_canonical_value(child)
    elif isinstance(value, str):
        assert unicodedata.is_normalized("NFC", value)
        assert all(
            not (0xFDD0 <= ord(char) <= 0xFDEF or ord(char) & 0xFFFF in {0xFFFE, 0xFFFF})
            for char in value
        )
    else:
        assert isinstance(value, bool), "JSON numbers and null are prohibited"


def _canonical_bytes(value):
    _assert_canonical_value(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def _identity(record):
    prefixes = {
        "LIFECYCLE_EVIDENCE_RECORD": ("evidence_record_id", "ES-EVIDENCE-RECORD-SHA256-"),
        "RETENTION_EVENT_RECORD": (
            "retention_event_id",
            "ES-EVIDENCE-RETENTION-EVENT-SHA256-",
        ),
        "DELETION_TOMBSTONE": (
            "deletion_tombstone_id",
            "ES-EVIDENCE-DELETION-TOMBSTONE-SHA256-",
        ),
    }
    identity_field, prefix = prefixes[record["artifact_type"]]
    excluded = {identity_field}
    if record["artifact_type"] == "LIFECYCLE_EVIDENCE_RECORD":
        excluded.add("payload_location")
    payload = {key: value for key, value in record.items() if key not in excluded}
    return prefix + hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def test_schema_declares_draft_2020_12_and_three_closed_branches(schema):
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    refs = [branch["$ref"] for branch in schema["$defs"]["artifact"]["oneOf"]]
    assert refs == [
        "#/$defs/lifecycleRecord",
        "#/$defs/retentionEvent",
        "#/$defs/deletionTombstone",
    ]
    for name in ("lifecycleRecord", "retentionEvent", "deletionTombstone"):
        assert schema["$defs"][name]["additionalProperties"] is False


def test_schema_meta_validates_when_draft_2020_12_validator_is_available(schema):
    if importlib.util.find_spec("jsonschema") is None:
        pytest.skip("jsonschema is not installed; Draft 2020-12 meta-schema validation unavailable")
    from jsonschema import Draft202012Validator

    Draft202012Validator.check_schema(schema)


def test_example_is_structurally_valid_and_covers_all_record_classes(schema, corpus, examples):
    _validate(corpus, schema, schema)
    assert {item["artifact_type"] for item in examples} == {
        "LIFECYCLE_EVIDENCE_RECORD",
        "RETENTION_EVENT_RECORD",
        "DELETION_TOMBSTONE",
    }
    assert all(item["non_authorizing_evidence_statement"] == NON_AUTHORIZING for item in examples)


def test_fixture_ids_are_unique_and_corpus_order_is_deterministic(corpus):
    for collection, key in (
        ("positive_fixtures", "fixture_id"),
        ("negative_fixtures", "case_id"),
        ("staged_entry_fixtures", "fixture_id"),
        ("manifest_entry_fixtures", "fixture_id"),
    ):
        identifiers = [item[key] for item in corpus[collection]]
        assert len(identifiers) == len(set(identifiers))
    positive = [item["fixture_id"] for item in corpus["positive_fixtures"]]
    assert positive[:7] == [
        "lifecycle-committed",
        "lifecycle-uncommitted",
        "lifecycle-staged",
        "lifecycle-untracked",
        "lifecycle-mixed",
        "lifecycle-published",
        "lifecycle-external",
    ]
    assert positive[23:32] == [
        "tombstone-authorized",
        "tombstone-in-progress",
        "tombstone-failed",
        "tombstone-blocked-by-hold",
        "tombstone-completed",
        "retention-deletion-completed",
        "tombstone-correction",
        "tombstone-evidence-correction",
        "tombstone-invalidation",
    ]
    assert [item["case_id"] for item in corpus["negative_fixtures"]][:12] == [
        "binding-contradictory",
        "binding-ambiguous-baseline",
        "binding-path-collision",
        "unsupported-version",
        "duplicate-authority",
        "authority-order",
        "retention-successor-after-completion",
        "completion-under-hold",
        "tombstone-invalid-jump",
        "tombstone-corrects-state",
        "completion-fields-noncompleted",
        "unknown-property",
    ]


def test_schema_and_es6_have_the_same_32_responsibilities_in_order(schema):
    schema_tokens = schema["$defs"]["responsibility"]["enum"]
    es6 = ES6_PATH.read_text(encoding="utf-8")
    es6_tokens = re.findall(r"^#### `([A-Z][A-Z0-9_]+)`$", es6, flags=re.MULTILINE)
    assert len(schema_tokens) == 32
    assert schema_tokens == es6_tokens


def test_every_record_branch_requires_the_canonical_non_authorizing_statement(schema):
    for name in ("lifecycleRecord", "retentionEvent", "deletionTombstone"):
        branch = schema["$defs"][name]
        assert "non_authorizing_evidence_statement" in branch["required"]
        assert (
            branch["properties"]["non_authorizing_evidence_statement"]["const"] == NON_AUTHORIZING
        )


def test_unsupported_version_unknown_field_and_duplicate_authority_fail_closed(schema, examples):
    branch = schema["$defs"]["lifecycleRecord"]
    wrong_version = deepcopy(examples[0])
    wrong_version["schema_version"] = "2.0.0"
    assert not _matches(wrong_version, branch, schema)
    unknown = deepcopy(examples[0])
    unknown["undeclared"] = "prohibited"
    assert not _matches(unknown, branch, schema)
    duplicate = deepcopy(examples[0])
    duplicate["authority_withheld"].append("CLOSEOUT")
    assert not _matches(duplicate, branch, schema)


def test_transition_discriminators_reject_active_inactive_branch_confusion(schema, examples):
    correction = deepcopy(
        next(x for x in examples if x["artifact_type"] == "RETENTION_EVENT_RECORD")
    )
    correction["retention_event_transition_kind"] = "CORRECTION"
    assert not _matches(correction, schema["$defs"]["retentionEvent"], schema)
    completed = deepcopy(next(x for x in examples if x["artifact_type"] == "DELETION_TOMBSTONE"))
    completed["deletion_state"] = "DELETION_COMPLETED"
    assert not _matches(completed, schema["$defs"]["deletionTombstone"], schema)


def test_operational_event_applicability_is_rejected_by_schema(schema, corpus):
    fixtures = _fixture_map(corpus)
    cases = []
    assignment = deepcopy(fixtures["retention-assignment"])
    assignment["prior_retention_event_id"] = fixtures["retention-retention-confirmed"][
        "retention_event_id"
    ]
    cases.append(assignment)
    confirmation = deepcopy(fixtures["retention-retention-confirmed"])
    confirmation["reason_code"] = "ASSIGNMENT_AUTHORIZED"
    cases.append(confirmation)
    unavailable = deepcopy(fixtures["retention-retention-unavailable"])
    unavailable["retrievability_state"] = "RETRIEVABLE"
    cases.append(unavailable)
    deletion = deepcopy(fixtures["retention-deletion-authorized"])
    deletion["location_identity"] = fixtures["retention-retention-confirmed"]["location_identity"]
    cases.append(deletion)
    completion = deepcopy(fixtures["retention-deletion-completed"])
    completion["deletion_tombstone_id"] = NA
    cases.append(completion)
    for artifact in cases:
        assert not _matches(artifact, schema["$defs"]["retentionEvent"], schema)


def test_typed_corrections_are_rejected_by_schema(schema, corpus):
    correction = deepcopy(_fixture_map(corpus)["retention-correction"])
    entry = correction["correction_details"]["corrected_fields"][0]
    entry["correction_value_schema"] = "RETENTION_EVENT_ACTOR_IDENTITY_V1"
    assert not _matches(correction, schema["$defs"]["retentionEvent"], schema)
    correction = deepcopy(_fixture_map(corpus)["retention-correction"])
    correction["correction_details"]["corrected_fields"] = []
    correction["correction_details"]["corrected_evidence"] = []
    assert not _matches(correction, schema["$defs"]["retentionEvent"], schema)


def test_identity_is_stable_order_independent_sensitive_and_class_specific(examples):
    lifecycle = examples[0]
    reordered = dict(reversed(list(lifecycle.items())))
    assert _identity(lifecycle) == _identity(reordered)
    changed = deepcopy(lifecycle)
    changed["decision"] = "DIFFERENT_DECISION"
    assert _identity(lifecycle) != _identity(changed)
    assert _identity(lifecycle).startswith("ES-EVIDENCE-RECORD-SHA256-")
    event = next(x for x in examples if x["artifact_type"] == "RETENTION_EVENT_RECORD")
    tombstone = next(x for x in examples if x["artifact_type"] == "DELETION_TOMBSTONE")
    assert _identity(event).startswith("ES-EVIDENCE-RETENTION-EVENT-SHA256-")
    assert _identity(tombstone).startswith("ES-EVIDENCE-DELETION-TOMBSTONE-SHA256-")
    moved = deepcopy(lifecycle)
    moved["payload_location"] = {
        "content_identity": {
            "byte_length": "1",
            "media_type": "application/json",
            "sha256": "1" * 64,
        },
        "location_identity": {
            "location_scheme": "CONTENT_ADDRESSED",
            "location_value": "sha256:" + "1" * 64,
        },
    }
    assert _identity(lifecycle) == _identity(moved)


def test_every_declared_fixture_identity_recomputes(examples):
    fields = {
        "LIFECYCLE_EVIDENCE_RECORD": "evidence_record_id",
        "RETENTION_EVENT_RECORD": "retention_event_id",
        "DELETION_TOMBSTONE": "deletion_tombstone_id",
    }
    for artifact in examples:
        assert artifact[fields[artifact["artifact_type"]]] == _identity(artifact)


def test_changed_fixture_with_stale_declared_identity_is_rejected(corpus):
    record = deepcopy(_fixture_map(corpus)["lifecycle-staged"])
    declared = record["evidence_record_id"]
    record["decision_effect"] = record["decision_effect"] + " changed"
    assert record["evidence_record_id"] == declared
    assert record["evidence_record_id"] != _identity(record)


def test_canonical_profile_rejects_numbers_non_nfc_and_duplicate_keys():
    with pytest.raises(AssertionError):
        _canonical_bytes({"count": 1})
    with pytest.raises(AssertionError):
        _canonical_bytes({"value": "e\u0301"})
    with pytest.raises(ValueError, match="duplicate key"):
        json.loads('{"a":"1","a":"2"}', object_pairs_hook=_reject_duplicate_keys)


def test_standard_states_core_negative_authority_and_privacy_boundaries():
    standard = STANDARD_PATH.read_text(encoding="utf-8")
    for text in (
        NON_AUTHORIZING,
        "Review is not approval",
        "Expiry never authorizes",
        "legal hold blocks deletion completion",
        "hidden reasoning",
        "accountable-human judgments",
    ):
        assert text in standard


# The helpers below are deliberately contract-specific. They are not, and are not
# represented as, a general-purpose Draft 2020-12 implementation.
NA = {"reason_code": "FIELD_NOT_APPLICABLE", "status": "NOT_APPLICABLE"}
LOCATION_TYPES = {
    "REPOSITORY_RELATIVE": "REPOSITORY_PATH",
    "CONTENT_ADDRESSED": "CONTENT_ADDRESS",
    "EXTERNAL_IMMUTABLE": "EXTERNAL_IMMUTABLE_OBJECT",
}
SUCCESSORS = {
    "RETENTION_ASSIGNED": {"RETENTION_CONFIRMED", "LEGAL_HOLD_APPLIED"},
    "RETENTION_CONFIRMED": {
        "RETRIEVABILITY_CONFIRMED",
        "RETENTION_RELOCATED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_EXPIRED",
        "LEGAL_HOLD_APPLIED",
        "LEGAL_HOLD_RELEASED",
    },
    "RETRIEVABILITY_CONFIRMED": {
        "RETENTION_RELOCATED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_EXPIRED",
        "LEGAL_HOLD_APPLIED",
        "LEGAL_HOLD_RELEASED",
    },
    "RETENTION_RELOCATED": {
        "RETRIEVABILITY_CONFIRMED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_EXPIRED",
        "LEGAL_HOLD_APPLIED",
        "LEGAL_HOLD_RELEASED",
    },
    "RETENTION_UNAVAILABLE": {
        "RETENTION_RESTORED",
        "RETENTION_EXPIRED",
        "LEGAL_HOLD_APPLIED",
        "LEGAL_HOLD_RELEASED",
    },
    "RETENTION_RESTORED": {
        "RETENTION_RELOCATED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_EXPIRED",
        "LEGAL_HOLD_APPLIED",
        "LEGAL_HOLD_RELEASED",
    },
    "RETENTION_EXPIRED": {"DELETION_AUTHORIZED", "LEGAL_HOLD_APPLIED", "LEGAL_HOLD_RELEASED"},
    "DELETION_AUTHORIZED": {"DELETION_COMPLETED", "LEGAL_HOLD_APPLIED", "LEGAL_HOLD_RELEASED"},
    "LEGAL_HOLD_APPLIED": {
        "LEGAL_HOLD_RELEASED",
        "RETENTION_CONFIRMED",
        "RETRIEVABILITY_CONFIRMED",
        "RETENTION_RELOCATED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_RESTORED",
        "RETENTION_EXPIRED",
        "DELETION_AUTHORIZED",
    },
    "LEGAL_HOLD_RELEASED": {
        "RETENTION_CONFIRMED",
        "RETRIEVABILITY_CONFIRMED",
        "RETENTION_RELOCATED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_RESTORED",
        "RETENTION_EXPIRED",
        "DELETION_AUTHORIZED",
        "DELETION_COMPLETED",
        "LEGAL_HOLD_APPLIED",
    },
    "DELETION_COMPLETED": set(),
}
REASONS = {
    "RETENTION_ASSIGNED": "ASSIGNMENT_AUTHORIZED",
    "RETENTION_CONFIRMED": "RETENTION_VERIFIED",
    "RETRIEVABILITY_CONFIRMED": "RETRIEVABILITY_VERIFIED",
    "RETENTION_RELOCATED": "LOCATION_CHANGED",
    "RETENTION_UNAVAILABLE": "RETENTION_FAILURE_OBSERVED",
    "RETENTION_RESTORED": "RETENTION_RESTORATION_VERIFIED",
    "RETENTION_EXPIRED": "RETENTION_POLICY_EXPIRED",
    "DELETION_AUTHORIZED": "DELETION_SEPARATELY_AUTHORIZED",
    "DELETION_COMPLETED": "DELETION_COMPLETION_VERIFIED",
    "LEGAL_HOLD_APPLIED": "LEGAL_HOLD_AUTHORIZED",
    "LEGAL_HOLD_RELEASED": "LEGAL_HOLD_RELEASE_AUTHORIZED",
}
TOMBSTONE_SUCCESSORS = {
    "DELETION_AUTHORIZED": {
        "DELETION_IN_PROGRESS",
        "DELETION_COMPLETED",
        "DELETION_FAILED",
        "DELETION_BLOCKED_BY_LEGAL_HOLD",
    },
    "DELETION_IN_PROGRESS": {
        "DELETION_COMPLETED",
        "DELETION_FAILED",
        "DELETION_BLOCKED_BY_LEGAL_HOLD",
    },
    "DELETION_FAILED": {"DELETION_IN_PROGRESS", "DELETION_BLOCKED_BY_LEGAL_HOLD"},
    "DELETION_BLOCKED_BY_LEGAL_HOLD": {"DELETION_IN_PROGRESS", "DELETION_FAILED"},
    "DELETION_COMPLETED": set(),
}


def _fixture_map(corpus):
    return {item["fixture_id"]: item["artifact"] for item in corpus["positive_fixtures"]}


def _assert_sorted_unique(values, key=lambda value: value):
    keys = [key(value) for value in values]
    assert keys == sorted(keys)
    assert len(keys) == len(set(keys))


def _validate_binding(binding):
    mode = binding["binding_mode"]
    assert mode in {
        "COMMITTED",
        "UNCOMMITTED",
        "STAGED",
        "UNTRACKED",
        "MIXED_MANIFEST",
        "PUBLISHED",
        "EXTERNAL",
    }
    if mode in {"STAGED", "MIXED_MANIFEST"}:
        entries = binding["entries"]
        _assert_sorted_unique(entries, key=lambda entry: entry["path"].encode())
        assert len({entry["path"].casefold() for entry in entries}) == len(entries)
        assert len({unicodedata.normalize("NFC", entry["path"]) for entry in entries}) == len(
            entries
        )
        for entry in entries:
            if entry["state"] == "DELETED" and entry["classification"] in {
                "STAGED",
                "STAGED_AND_UNSTAGED",
            }:
                assert entry["stage_zero_object_id"] == NA
                assert entry["stage_zero_mode"] == NA
                assert entry["resulting_sha256"] == NA
                if entry["worktree_state"] == "ABSENT":
                    assert entry["classification"] == "STAGED"
                    assert entry["worktree_divergence"] is False
                    assert all(value == NA for value in entry["worktree_identity"].values())
                elif entry["worktree_state"] == "RECREATED":
                    assert entry["classification"] == "STAGED_AND_UNSTAGED"
                    assert entry["worktree_divergence"] is True
                    assert isinstance(entry["worktree_identity"]["worktree_sha256"], str)
                else:
                    raise AssertionError("staged deletion has contradictory worktree state")
    if mode == "UNTRACKED":
        assert binding["baseline_state"] == binding["index_state"] == "ABSENT"
        assert binding["expected_worktree_scope"] == sorted(
            binding["expected_worktree_scope"], key=lambda path: path.encode()
        )
    if mode == "EXTERNAL":
        assert binding["location_identity"]["location_scheme"] in {
            "CONTENT_ADDRESSED",
            "EXTERNAL_IMMUTABLE",
        }
    if mode == "UNCOMMITTED":
        concrete_index = binding["index_identity"] != NA
        concrete_worktree = binding["worktree_identity"] != NA
        expected = {
            "STAGED_ONLY": (True, False, "INDEX"),
            "UNSTAGED_ONLY": (False, True, "WORKTREE"),
            "STAGED_AND_UNSTAGED": (True, True, binding["governed_candidate"]),
        }[binding["classification"]]
        assert (concrete_index, concrete_worktree, binding["governed_candidate"]) == expected
    if mode in {"COMMITTED", "MIXED_MANIFEST"}:
        inclusions = binding.get("inclusions", [])
        exclusions = binding.get("exclusions", [])
        _assert_sorted_unique(inclusions, key=lambda path: path.encode())
        _assert_sorted_unique(exclusions, key=lambda path: path.encode())
        assert not set(inclusions) & set(exclusions)
        assert not any(
            included == excluded
            or included.startswith(excluded + "/")
            or excluded.startswith(included + "/")
            for included in inclusions
            for excluded in exclusions
        )
    if mode == "MIXED_MANIFEST":
        by_path = {entry["path"]: entry for entry in binding["entries"]}
        assert set(by_path) == set(binding["inclusions"])
        for entry in binding["entries"]:
            if entry["state"] == "RENAMED_OLD":
                assert entry["rename_to"] in by_path
                peer = by_path[entry["rename_to"]]
                assert peer["state"] == "RENAMED_NEW"
                assert peer["rename_from"] == entry["path"]
            elif entry["state"] == "RENAMED_NEW":
                assert entry["rename_from"] in by_path
                peer = by_path[entry["rename_from"]]
                assert peer["state"] == "RENAMED_OLD"
                assert peer["rename_to"] == entry["path"]
        payload = {
            key: value
            for key, value in binding.items()
            if key not in {"binding_mode", "candidate_manifest_id", "filter_state"}
        }
        assert binding["candidate_manifest_id"] == (
            "ES-CANDIDATE-MANIFEST-SHA256-" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()
        )


def _candidate_manifest_identity(binding):
    payload = {
        key: value
        for key, value in binding.items()
        if key not in {"binding_mode", "candidate_manifest_id", "filter_state"}
    }
    return "ES-CANDIDATE-MANIFEST-SHA256-" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def _replace_path(value, path, replacement):
    result = deepcopy(value)
    node = result
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = deepcopy(replacement)
    return result


def _changed_paths(before, after, prefix=()):
    if type(before) is not type(after):
        return {prefix}
    if isinstance(before, dict):
        paths = set()
        for key in set(before) | set(after):
            if key not in before or key not in after:
                paths.add(prefix + (key,))
            else:
                paths |= _changed_paths(before[key], after[key], prefix + (key,))
        return paths
    if isinstance(before, list):
        if len(before) != len(after):
            return {prefix}
        paths = set()
        for index, (left, right) in enumerate(zip(before, after, strict=True)):
            paths |= _changed_paths(left, right, prefix + (index,))
        return paths
    return set() if before == after else {prefix}


def _rebase_event(template, predecessor, **changes):
    event = deepcopy(template)
    event["prior_retention_event_id"] = (
        NA if predecessor is None else predecessor["retention_event_id"]
    )
    event.update(deepcopy(changes))
    event["retention_event_id"] = _identity(event)
    return event


def _validate_event_chain(chain, tombstones=(), successors=SUCCESSORS):
    by_id = {}
    tombstone_ids = {item["deletion_tombstone_id"] for item in tombstones}
    hold = "NO_HOLD"
    deletion = "NOT_AUTHORIZED"
    assigned = False
    confirmed = False
    retrievability = "UNKNOWN"
    located = False
    location_identity = NA
    availability = "UNKNOWN"
    expired = False
    binding = None
    prior_kind = None
    deletion_tombstone_id = NA
    for index, event in enumerate(chain):
        assert event["retention_event_id"] == _identity(event)
        assert event["retention_event_id"] not in by_id
        if event["retention_event_transition_kind"] != "OPERATIONAL":
            assert (
                index > 0
                and event["prior_retention_event_id"] == chain[index - 1]["retention_event_id"]
            ), "stale non-operational predecessor"
            assert event["event_kind"] == NA and event["reason_code"] == NA
            if event["retention_event_transition_kind"] == "INVALIDATION":
                assert index < len(chain) - 1, "invalidation has no unique replacement lineage"
            by_id[event["retention_event_id"]] = event
            continue
        kind = event["event_kind"]
        assert event["reason_code"] == REASONS[kind]
        current_binding = (
            event["content_identity"]
            if event["content_identity"] != NA
            else event["package_identity"]
        )
        assert current_binding != NA
        binding = current_binding if binding is None else binding
        assert current_binding == binding
        authority_kinds = {
            "RETENTION_ASSIGNED",
            "RETENTION_EXPIRED",
            "DELETION_AUTHORIZED",
            "LEGAL_HOLD_APPLIED",
            "LEGAL_HOLD_RELEASED",
        }
        location_kinds = {
            "RETENTION_CONFIRMED",
            "RETRIEVABILITY_CONFIRMED",
            "RETENTION_RELOCATED",
            "RETENTION_UNAVAILABLE",
            "RETENTION_RESTORED",
        }
        assert (event["authority_reference"] != NA) is (kind in authority_kinds)
        assert (event["assignment_authority"] != NA) is (kind == "RETENTION_ASSIGNED")
        assert (event["location_identity"] != NA) is (kind in location_kinds)
        if index == 0:
            assert kind == "RETENTION_ASSIGNED" and event["prior_retention_event_id"] == NA
        else:
            assert event["prior_retention_event_id"] == chain[index - 1]["retention_event_id"]
            assert kind in successors[prior_kind], "prohibited operational successor"
        if kind == "RETENTION_ASSIGNED":
            assert not assigned and event["retrievability_state"] == "UNKNOWN"
            assigned = True
        elif kind == "RETENTION_CONFIRMED":
            assert assigned and not confirmed and not expired and deletion != "COMPLETED"
            assert event["retrievability_state"] == "UNKNOWN"
            confirmed = True
            located = True
            location_identity = event["location_identity"]
            retrievability = "UNKNOWN"
            availability = "AVAILABLE"
        elif kind == "RETRIEVABILITY_CONFIRMED":
            assert confirmed and located and not expired and deletion != "COMPLETED"
            assert event["retrievability_state"] == "RETRIEVABLE"
            location_identity = event["location_identity"]
            retrievability = "RETRIEVABLE"
        elif kind == "RETENTION_RELOCATED":
            assert (
                confirmed
                and located
                and not expired
                and retrievability != "UNAVAILABLE"
                and deletion == "NOT_AUTHORIZED"
            )
            locations = event["location_identity"]
            assert locations["prior_location_identity"] != locations["resulting_location_identity"]
            assert (
                LOCATION_TYPES[locations["resulting_location_identity"]["location_scheme"]]
                == event["location_type"]
            )
            assert event["retrievability_state"] == "UNKNOWN"
            location_identity = locations["resulting_location_identity"]
            retrievability = "UNKNOWN"
        elif kind == "RETENTION_UNAVAILABLE":
            assert (
                confirmed
                and located
                and not expired
                and retrievability != "UNAVAILABLE"
                and deletion != "COMPLETED"
            )
            assert event["retrievability_state"] == "UNAVAILABLE"
            location_identity = event["location_identity"]
            retrievability = "UNAVAILABLE"
            availability = "UNAVAILABLE"
        elif kind == "RETENTION_RESTORED":
            assert (
                confirmed
                and located
                and not expired
                and retrievability == "UNAVAILABLE"
                and deletion != "COMPLETED"
            )
            assert event["retrievability_state"] == "RETRIEVABLE"
            location_identity = event["location_identity"]
            retrievability = "RETRIEVABLE"
            availability = "AVAILABLE"
        elif kind == "RETENTION_EXPIRED":
            assert assigned and not expired and deletion != "COMPLETED"
            assert event["retrievability_state"] == retrievability
            expired = True
        elif kind == "LEGAL_HOLD_APPLIED":
            assert hold == "NO_HOLD", "repeated hold application"
            assert deletion != "COMPLETED"
            assert event["retrievability_state"] == retrievability
            hold = "ACTIVE_HOLD"
        elif kind == "LEGAL_HOLD_RELEASED":
            assert hold == "ACTIVE_HOLD", "hold release without active hold"
            assert deletion != "COMPLETED"
            assert event["retrievability_state"] == retrievability
            hold = "NO_HOLD"
        elif kind == "DELETION_AUTHORIZED":
            assert expired and deletion == "NOT_AUTHORIZED"
            assert event["retrievability_state"] == retrievability
            deletion = "AUTHORIZED"
        elif kind == "DELETION_COMPLETED":
            assert (
                deletion == "AUTHORIZED" and hold == "NO_HOLD" and retrievability != "UNAVAILABLE"
            )
            assert event["deletion_tombstone_id"] in tombstone_ids
            assert event["retrievability_state"] == "UNAVAILABLE"
            deletion = "COMPLETED"
            retrievability = "UNAVAILABLE"
            located = False
            location_identity = NA
            availability = "UNAVAILABLE"
            deletion_tombstone_id = event["deletion_tombstone_id"]
        if kind != "DELETION_COMPLETED":
            assert event["deletion_tombstone_id"] == NA
        prior_kind = kind
        by_id[event["retention_event_id"]] = event
    return {
        "retention_assignment_state": "ASSIGNED" if assigned else "UNASSIGNED",
        "retention_confirmation_state": "CONFIRMED" if confirmed else "UNCONFIRMED",
        "location_state": "LOCATED" if located else "NO_LOCATION",
        "location_identity": location_identity,
        "retrievability_state": retrievability,
        "availability_state": availability,
        "legal_hold_state": hold,
        "retention_expiry_state": "EXPIRED" if expired else "ACTIVE",
        "deletion_authorization_state": (
            "AUTHORIZED" if deletion in {"AUTHORIZED", "COMPLETED"} else "NOT_AUTHORIZED"
        ),
        "deletion_completion_state": ("COMPLETED" if deletion == "COMPLETED" else "NOT_COMPLETED"),
        "deletion_tombstone_id": deletion_tombstone_id,
    }


def _derive_event_state(events, tombstones=(), successors=SUCCESSORS):
    assert events, "event chain is empty"
    by_id = {event["retention_event_id"]: event for event in events}
    assert len(by_id) == len(events), "duplicate event identity"

    visiting = set()
    visited = set()

    def visit(event_id):
        if event_id in visiting:
            raise AssertionError("retention lineage cycle")
        if event_id in visited:
            return
        visiting.add(event_id)
        predecessor_id = by_id[event_id]["prior_retention_event_id"]
        if predecessor_id != NA:
            assert predecessor_id in by_id, "missing retention predecessor"
            visit(predecessor_id)
        visiting.remove(event_id)
        visited.add(event_id)

    for event_id in by_id:
        visit(event_id)

    roots = [event for event in events if event["prior_retention_event_id"] == NA]
    assert len(roots) == 1, "ambiguous current state: expected exactly one root"
    successors_by_id = {event_id: [] for event_id in by_id}
    for event in events:
        predecessor_id = event["prior_retention_event_id"]
        if predecessor_id != NA:
            successors_by_id[predecessor_id].append(event)
    for children in successors_by_id.values():
        if len(children) > 1:
            kinds = {child["retention_event_transition_kind"] for child in children}
            message = (
                "competing operational successor"
                if kinds == {"OPERATIONAL"}
                else "retention lineage fork"
            )
            raise AssertionError(message)

    chain = []
    current = roots[0]
    while current is not None:
        chain.append(current)
        children = successors_by_id[current["retention_event_id"]]
        current = children[0] if children else None
    assert len(chain) == len(events), "ambiguous current state"
    return _validate_event_chain(chain, tombstones=tombstones, successors=successors)


HOLD_PRESERVATION_FIXTURES = {
    "RETENTION_CONFIRMED": "confirmation",
    "RETRIEVABILITY_CONFIRMED": "retrievability",
    "RETENTION_RELOCATED": "relocation",
    "RETENTION_UNAVAILABLE": "unavailable",
    "RETENTION_RESTORED": "restored",
    "RETENTION_EXPIRED": "expiry",
    "DELETION_AUTHORIZED": "deletion-authorization",
}


def _complete_hold_release_chain(corpus, preserving_kind):
    fixtures = _fixture_map(corpus)
    assignment = deepcopy(fixtures["retention-assignment"])
    confirmation = _rebase_event(fixtures["retention-retention-confirmed"], assignment)
    retrievability = _rebase_event(fixtures["retention-retrievability-confirmed"], confirmation)
    unavailable = _rebase_event(fixtures["retention-retention-unavailable"], retrievability)
    expired = _rebase_event(fixtures["retention-retention-expired"], retrievability)
    if preserving_kind == "RETENTION_CONFIRMED":
        prefix = [assignment]
        hold_retrievability = "UNKNOWN"
    elif preserving_kind == "RETRIEVABILITY_CONFIRMED":
        prefix = [assignment, confirmation]
        hold_retrievability = "UNKNOWN"
    elif preserving_kind == "RETENTION_RESTORED":
        prefix = [assignment, confirmation, retrievability, unavailable]
        hold_retrievability = "UNAVAILABLE"
    elif preserving_kind == "DELETION_AUTHORIZED":
        prefix = [assignment, confirmation, retrievability, expired]
        hold_retrievability = "RETRIEVABLE"
    else:
        prefix = [assignment, confirmation, retrievability]
        hold_retrievability = "RETRIEVABLE"

    hold = _rebase_event(
        fixtures["retention-legal-hold-applied"],
        prefix[-1],
        retrievability_state=hold_retrievability,
    )
    suffix = HOLD_PRESERVATION_FIXTURES[preserving_kind]
    preserved = _rebase_event(fixtures[f"retention-hold-preserved-by-{suffix}"], hold)
    release_retrievability = {
        "RETENTION_CONFIRMED": "UNKNOWN",
        "RETRIEVABILITY_CONFIRMED": "RETRIEVABLE",
        "RETENTION_RELOCATED": "UNKNOWN",
        "RETENTION_UNAVAILABLE": "UNAVAILABLE",
        "RETENTION_RESTORED": "RETRIEVABLE",
        "RETENTION_EXPIRED": "RETRIEVABLE",
        "DELETION_AUTHORIZED": "RETRIEVABLE",
    }[preserving_kind]
    released = _rebase_event(
        fixtures[f"retention-hold-release-after-{suffix}"],
        preserved,
        retrievability_state=release_retrievability,
    )
    return prefix, hold, preserved, released


def _assert_named_invalid_chain_fails(corpus, case_id):
    fixtures = _fixture_map(corpus)
    assignment = deepcopy(fixtures["retention-assignment"])
    confirmation = _rebase_event(fixtures["retention-retention-confirmed"], assignment)
    retrievability = _rebase_event(fixtures["retention-retrievability-confirmed"], confirmation)
    if case_id == "retention-repeated-hold-application":
        hold = _rebase_event(
            fixtures["retention-legal-hold-applied"],
            retrievability,
            retrievability_state="RETRIEVABLE",
        )
        repeated = _rebase_event(
            fixtures["retention-legal-hold-applied"],
            hold,
            retrievability_state="RETRIEVABLE",
        )
        _derive_event_state([assignment, confirmation, retrievability, hold, repeated])
    elif case_id == "retention-release-without-hold":
        release = _rebase_event(
            fixtures["retention-legal-hold-released"],
            confirmation,
            retrievability_state="UNKNOWN",
        )
        _derive_event_state([assignment, confirmation, release])
    elif case_id == "retention-correction-stale-target":
        correction = _rebase_event(fixtures["retention-correction"], assignment)
        _validate_event_chain([assignment, confirmation, correction])
    elif case_id == "retention-invalidation-without-unique-replacement":
        invalidation = _rebase_event(fixtures["retention-invalidation"], confirmation)
        _derive_event_state([assignment, confirmation, invalidation])
    elif case_id == "retention-lineage-fork":
        correction = _rebase_event(fixtures["retention-correction"], confirmation)
        operational = _rebase_event(fixtures["retention-retrievability-confirmed"], confirmation)
        _derive_event_state([assignment, confirmation, correction, operational])
    elif case_id == "retention-lineage-cycle":
        left = deepcopy(confirmation)
        right = deepcopy(retrievability)
        left["prior_retention_event_id"] = right["retention_event_id"]
        right["prior_retention_event_id"] = left["retention_event_id"]
        _derive_event_state([left, right])
    elif case_id == "retention-competing-successor":
        hold = _rebase_event(
            fixtures["retention-legal-hold-applied"],
            confirmation,
            retrievability_state="UNKNOWN",
        )
        operational = _rebase_event(fixtures["retention-retrievability-confirmed"], confirmation)
        _derive_event_state([assignment, confirmation, hold, operational])
    elif case_id == "retention-ambiguous-current-state":
        _derive_event_state([assignment, fixtures["retention-package-assignment"]])
    else:
        raise AssertionError(f"unknown named invalid chain: {case_id}")


def _validate_tombstone_chain(chain):
    for index, tombstone in enumerate(chain):
        assert tombstone["deletion_tombstone_id"] == _identity(tombstone)
        kind = tombstone["tombstone_transition_kind"]
        if index == 0:
            assert kind == "INITIAL" and tombstone["predecessor_tombstone_id"] == NA
        else:
            predecessor = chain[index - 1]
            assert tombstone["predecessor_tombstone_id"] == predecessor["deletion_tombstone_id"]
            if kind == "STATE_PROGRESSION":
                assert (
                    tombstone["deletion_state"]
                    in TOMBSTONE_SUCCESSORS[predecessor["deletion_state"]]
                )
                assert tombstone["tombstone_transition_details"] == {
                    "predecessor_deletion_state": predecessor["deletion_state"],
                    "successor_deletion_state": tombstone["deletion_state"],
                }
            else:
                assert kind in {"CORRECTION", "INVALIDATION"}
                assert tombstone["deletion_state"] == predecessor["deletion_state"]
        completed = tombstone["deletion_state"] == "DELETION_COMPLETED"
        for field in (
            "deletion_completed_timestamp",
            "deletion_method_class",
            "completion_evidence",
        ):
            assert (tombstone[field] != NA) is completed
        if completed:
            assert tombstone["retrievability_state"] == "DELETED"
            assert tombstone["legal_hold_status"] != "ACTIVE_HOLD"
        if tombstone["deletion_state"] == "DELETION_BLOCKED_BY_LEGAL_HOLD":
            assert tombstone["legal_hold_status"] == "ACTIVE_HOLD"


def _parse_canonical_artifact(raw):
    assert not raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8")
    assert not text.endswith("\n")
    assert "\\/" not in text
    assert not re.search(r"\\u[0-9a-fA-F]{4}", text)
    value = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    _assert_canonical_value(value)
    assert raw == _canonical_bytes(value)
    return value


def test_all_binding_modes_are_closed_and_semantically_valid(schema, corpus):
    fixtures = _fixture_map(corpus)
    records = [
        fixtures[f"lifecycle-{name}"]
        for name in (
            "committed",
            "uncommitted",
            "staged",
            "untracked",
            "mixed",
            "published",
            "external",
        )
    ]
    assert {record["artifact_binding"]["binding_mode"] for record in records} == {
        "COMMITTED",
        "UNCOMMITTED",
        "STAGED",
        "UNTRACKED",
        "MIXED_MANIFEST",
        "PUBLISHED",
        "EXTERNAL",
    }
    for record in records:
        _validate(record, schema["$defs"]["lifecycleRecord"], schema)
        _validate_binding(record["artifact_binding"])
        assert record["evidence_record_id"] == _identity(record)
    manifest = records[4]["artifact_binding"]
    payload = {
        key: value
        for key, value in manifest.items()
        if key not in {"binding_mode", "candidate_manifest_id", "filter_state"}
    }
    assert (
        manifest["candidate_manifest_id"]
        == "ES-CANDIDATE-MANIFEST-SHA256-" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    )


def test_staged_deletion_cross_product_rejects_contradictions(corpus):
    fixtures = _fixture_map(corpus)
    absent = fixtures["lifecycle-staged"]["artifact_binding"]
    recreated = fixtures["lifecycle-mixed"]["artifact_binding"]
    _validate_binding(absent)
    _validate_binding(recreated)
    wrong = deepcopy(absent)
    wrong["entries"][0]["classification"] = "STAGED_AND_UNSTAGED"
    with pytest.raises(AssertionError):
        _validate_binding(wrong)
    collision = deepcopy(recreated)
    collision["entries"].append(deepcopy(collision["entries"][0]))
    with pytest.raises(AssertionError):
        _validate_binding(collision)


def _direct_branch_count(instance, definition, schema):
    return sum(
        _matches(instance, branch, schema) for branch in schema["$defs"][definition]["oneOf"]
    )


def test_staged_entry_eight_branch_cross_product_is_closed(schema, corpus):
    fixtures = {item["fixture_id"]: item["entry"] for item in corpus["staged_entry_fixtures"]}
    assert len(schema["$defs"]["stagedEntry"]["oneOf"]) == 8
    assert set(fixtures) == {
        "SE-ADD-MATCH",
        "SE-ADD-DIVERGED",
        "SE-ADD-ABSENT",
        "SE-MOD-MATCH",
        "SE-MOD-DIVERGED",
        "SE-MOD-ABSENT",
        "SE-DEL-ABSENT",
        "SE-DEL-RECREATED",
    }
    for entry in fixtures.values():
        assert _matches(entry, schema["$defs"]["stagedEntry"], schema)
        assert _direct_branch_count(entry, "stagedEntry", schema) == 1

    variants = []

    def invalid(base, **changes):
        entry = deepcopy(fixtures[base])
        entry.update(changes)
        variants.append(entry)

    invalid("SE-ADD-MATCH", baseline_object_id="1" * 40)
    invalid("SE-ADD-MATCH", baseline_mode="100644")
    invalid("SE-MOD-MATCH", baseline_object_id=NA)
    invalid("SE-DEL-ABSENT", baseline_mode=NA)
    invalid("SE-ADD-MATCH", stage_zero_object_id=NA)
    invalid("SE-DEL-ABSENT", stage_zero_mode="100644")
    invalid("SE-MOD-MATCH", resulting_sha256=NA)
    invalid("SE-DEL-ABSENT", byte_length="42")
    invalid("SE-ADD-MATCH", worktree_state="DIVERGED")
    invalid("SE-ADD-DIVERGED", worktree_state="MATCHES_STAGE_ZERO")
    invalid("SE-MOD-MATCH", worktree_divergence=True)
    invalid("SE-MOD-DIVERGED", worktree_divergence=False)
    invalid("SE-DEL-ABSENT", worktree_divergence=True)
    invalid(
        "SE-DEL-ABSENT", worktree_identity=deepcopy(fixtures["SE-ADD-MATCH"]["worktree_identity"])
    )
    invalid("SE-DEL-RECREATED", worktree_divergence=False)
    invalid(
        "SE-DEL-RECREATED",
        worktree_identity=deepcopy(fixtures["SE-DEL-ABSENT"]["worktree_identity"]),
    )
    invalid("SE-DEL-RECREATED", classification="STAGED")
    invalid("SE-DEL-ABSENT", classification="STAGED_AND_UNSTAGED")
    invalid("SE-ADD-DIVERGED", worktree_state="RECREATED")
    incomplete = deepcopy(fixtures["SE-ADD-MATCH"])
    incomplete["worktree_identity"].pop("worktree_mode")
    variants.append(incomplete)
    partial_absent = deepcopy(fixtures["SE-ADD-ABSENT"])
    partial_absent["worktree_identity"]["worktree_mode"] = "100644"
    variants.append(partial_absent)
    conflict = deepcopy(fixtures["SE-ADD-MATCH"])
    conflict["state"] = "CONFLICT_STAGE_2"
    variants.append(conflict)
    intent_to_add = deepcopy(fixtures["SE-ADD-MATCH"])
    intent_to_add["stage_zero_object_id"] = NA
    variants.append(intent_to_add)
    for entry in variants:
        assert not _matches(entry, schema["$defs"]["stagedEntry"], schema)
        assert _direct_branch_count(entry, "stagedEntry", schema) == 0
    assert len(variants) == 23


def test_manifest_entry_eleven_branch_cross_product_is_closed(schema, corpus):
    fixtures = {item["fixture_id"]: item["entry"] for item in corpus["manifest_entry_fixtures"]}
    assert len(schema["$defs"]["manifestEntry"]["oneOf"]) == 11
    assert len(fixtures) == 11
    for entry in fixtures.values():
        assert _matches(entry, schema["$defs"]["manifestEntry"], schema)
        assert _direct_branch_count(entry, "manifestEntry", schema) == 1

    variants = []

    def invalid(base, **changes):
        entry = deepcopy(fixtures[base])
        entry.update(changes)
        variants.append(entry)

    invalid("ME-STAGED-ADD", classification="UNSTAGED")
    invalid("ME-STAGED-DEL-ABSENT", resulting_sha256="2" * 64)
    invalid("ME-STAGED-ADD", resulting_sha256=NA)
    invalid("ME-STAGED-ADD", deletion=True)
    invalid("ME-RENAME-OLD", rename_from="fixtures/other")
    invalid("ME-RENAME-OLD", rename_to=NA)
    invalid("ME-STAGED-MOD", rename_to="fixtures/other")
    invalid("ME-STAGED-MOD-DIVERGED", worktree_state="MATCHES_STAGE_ZERO")
    invalid("ME-STAGED-ADD", resulting_mode="120000")
    invalid("ME-STAGED-ADD", resulting_mode="160000")
    invalid(
        "ME-STAGED-DEL-ABSENT",
        resulting_bytes=deepcopy(fixtures["ME-STAGED-ADD"]["resulting_bytes"]),
    )
    invalid("ME-WORKTREE-ADD", baseline_object_id="1" * 40)
    for entry in variants:
        assert not _matches(entry, schema["$defs"]["manifestEntry"], schema)
        assert _direct_branch_count(entry, "manifestEntry", schema) == 0
    assert len(variants) == 12


def test_manifest_wide_static_validation_is_separate_and_fail_closed(corpus):
    entries = sorted(
        (deepcopy(item["entry"]) for item in corpus["manifest_entry_fixtures"]),
        key=lambda entry: entry["path"].encode(),
    )
    binding = {
        "binding_mode": "MIXED_MANIFEST",
        "schema_version": "1.0.0",
        "baseline_commit": "1" * 40,
        "inclusions": [entry["path"] for entry in entries],
        "exclusions": [],
        "entries": entries,
        "filter_state": "EXACT_INDEX_AND_RAW_WORKTREE_BYTES",
    }
    payload = {key: value for key, value in binding.items() if key != "binding_mode"}
    payload.pop("filter_state")
    binding["candidate_manifest_id"] = (
        "ES-CANDIDATE-MANIFEST-SHA256-" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    )
    _validate_binding(binding)

    malformed = []
    duplicate_path = deepcopy(binding)
    duplicate_path["entries"][1]["path"] = duplicate_path["entries"][0]["path"]
    malformed.append(duplicate_path)
    wrong_order = deepcopy(binding)
    wrong_order["entries"][0], wrong_order["entries"][1] = (
        wrong_order["entries"][1],
        wrong_order["entries"][0],
    )
    malformed.append(wrong_order)
    case_collision = deepcopy(binding)
    case_collision["entries"][1]["path"] = case_collision["entries"][0]["path"].upper()
    malformed.append(case_collision)
    unicode_collision = deepcopy(binding)
    unicode_collision["entries"][0]["path"] = "fixtures/caf\u00e9"
    unicode_collision["entries"][1]["path"] = "fixtures/cafe\u0301"
    unicode_collision["entries"] = sorted(
        unicode_collision["entries"], key=lambda entry: entry["path"].encode()
    )
    malformed.append(unicode_collision)
    inclusion_order = deepcopy(binding)
    inclusion_order["inclusions"] = list(reversed(inclusion_order["inclusions"]))
    malformed.append(inclusion_order)
    overlap = deepcopy(binding)
    overlap["exclusions"] = [overlap["inclusions"][0]]
    malformed.append(overlap)
    missing_scope = deepcopy(binding)
    missing_scope["inclusions"] = missing_scope["inclusions"][:-1]
    malformed.append(missing_scope)
    stale_identity = deepcopy(binding)
    stale_identity["candidate_manifest_id"] = "ES-CANDIDATE-MANIFEST-SHA256-" + "0" * 64
    malformed.append(stale_identity)
    unmatched_old = deepcopy(binding)
    unmatched_old["entries"] = [e for e in unmatched_old["entries"] if e["state"] != "RENAMED_NEW"]
    unmatched_old["inclusions"] = [e["path"] for e in unmatched_old["entries"]]
    malformed.append(unmatched_old)
    unmatched_new = deepcopy(binding)
    unmatched_new["entries"] = [e for e in unmatched_new["entries"] if e["state"] != "RENAMED_OLD"]
    unmatched_new["inclusions"] = [e["path"] for e in unmatched_new["entries"]]
    malformed.append(unmatched_new)
    inconsistent_pair = deepcopy(binding)
    next(e for e in inconsistent_pair["entries"] if e["state"] == "RENAMED_NEW")["rename_from"] = (
        inconsistent_pair["entries"][0]["path"]
    )
    malformed.append(inconsistent_pair)
    for candidate in malformed:
        with pytest.raises(AssertionError):
            _validate_binding(candidate)
    assert len(malformed) == 11


def test_retention_operational_chain_and_terminal_completion(corpus):
    fixtures = _fixture_map(corpus)
    # The corpus has two retrievability observations; select by predecessor traversal.
    events = [
        item["artifact"]
        for item in corpus["positive_fixtures"]
        if item["artifact"]["artifact_type"] == "RETENTION_EVENT_RECORD"
        and item["fixture_id"] != "retention-package-assignment"
    ]
    chain = []
    for event in events:
        if event["retention_event_transition_kind"] != "OPERATIONAL":
            continue
        chain.append(event)
        if event["event_kind"] == "DELETION_AUTHORIZED":
            break
    completed_tombstone = fixtures["tombstone-completed"]
    completion = next(event for event in events if event["event_kind"] == "DELETION_COMPLETED")
    _validate_event_chain(chain + [completion], [completed_tombstone])
    with pytest.raises(AssertionError):
        _validate_event_chain(chain + [completion, deepcopy(completion)], [completed_tombstone])
    held = deepcopy(completion)
    held["prior_retention_event_id"] = chain[3]["retention_event_id"]
    with pytest.raises(AssertionError):
        _validate_event_chain(chain[:4] + [held], [completed_tombstone])


def test_tombstone_progression_graph_and_completion_applicability(corpus):
    fixtures = _fixture_map(corpus)
    _validate_tombstone_chain(
        [
            fixtures["tombstone-authorized"],
            fixtures["tombstone-in-progress"],
            fixtures["tombstone-completed"],
        ]
    )
    _validate_tombstone_chain(
        [
            fixtures["tombstone-authorized"],
            fixtures["tombstone-in-progress"],
            fixtures["tombstone-failed"],
            fixtures["tombstone-blocked-by-hold"],
        ]
    )
    jump = deepcopy(fixtures["tombstone-completed"])
    jump["predecessor_tombstone_id"] = fixtures["tombstone-failed"]["deletion_tombstone_id"]
    with pytest.raises(AssertionError):
        _validate_tombstone_chain([fixtures["tombstone-failed"], jump])


def test_retention_correction_invalidation_are_closed_and_state_preserving(schema, corpus):
    fixtures = _fixture_map(corpus)
    correction = fixtures["retention-correction"]
    invalidation = fixtures["retention-invalidation"]
    for event, active, inactive in (
        (correction, "correction_details", "invalidation_details"),
        (invalidation, "invalidation_details", "correction_details"),
    ):
        _validate(event, schema["$defs"]["retentionEvent"], schema)
        assert event["event_kind"] == NA and event["reason_code"] == NA
        assert event[active] != NA and event[inactive] == NA
        for field in (
            "retention_class",
            "assignment_authority",
            "content_identity",
            "package_identity",
            "location_identity",
            "location_type",
            "retrievability_state",
            "authority_reference",
            "deletion_tombstone_id",
        ):
            assert event[field] == NA
        assert event["retention_event_id"] == _identity(event)
    fields = correction["correction_details"]["corrected_fields"]
    _assert_sorted_unique(
        fields,
        key=lambda item: (
            item["field_name"],
            item["prior_value_identity"],
            hashlib.sha256(_canonical_bytes(item["corrected_value"])).hexdigest(),
        ),
    )
    assert set(invalidation["invalidation_details"]["invalidated_fields"]) <= {
        "event_timestamp",
        "actor_identity",
        "authority_reference",
        "reason_code",
        "limitations",
        "non_authorizing_evidence_statement",
        "event_kind",
        "evidence_record_id",
        "content_identity",
        "package_identity",
    }
    bad = deepcopy(correction)
    bad["content_identity"] = fixtures["retention-assignment"]["content_identity"]
    assert not _matches(bad, schema["$defs"]["retentionEvent"], schema)
    duplicate = deepcopy(correction)
    duplicate["correction_details"]["corrected_fields"].append(
        deepcopy(duplicate["correction_details"]["corrected_fields"][0])
    )
    assert not _matches(duplicate, schema["$defs"]["retentionEvent"], schema)
    both = deepcopy(correction)
    both["invalidation_details"] = deepcopy(invalidation["invalidation_details"])
    assert not _matches(both, schema["$defs"]["retentionEvent"], schema)


def test_tombstone_correction_and_invalidation_preserve_state(schema, corpus):
    fixtures = _fixture_map(corpus)
    predecessor = fixtures["tombstone-in-progress"]
    for name in ("tombstone-correction", "tombstone-evidence-correction", "tombstone-invalidation"):
        item = fixtures[name]
        _validate(item, schema["$defs"]["deletionTombstone"], schema)
        assert item["predecessor_tombstone_id"] == predecessor["deletion_tombstone_id"]
        assert item["deletion_state"] == predecessor["deletion_state"]
        assert item["deletion_tombstone_id"] == _identity(item)
    assert (
        "deletion_state"
        not in fixtures["tombstone-correction"]["tombstone_transition_details"]["corrected_fields"]
    )
    evidence = fixtures["tombstone-evidence-correction"]["tombstone_transition_details"][
        "corrected_evidence"
    ]
    assert evidence[0]["supported_claim"] == "DELETION_STATE"
    assert fixtures["tombstone-invalidation"]["tombstone_transition_details"][
        "invalidated_fields"
    ] == ["deletion_state"]
    changed = deepcopy(fixtures["tombstone-correction"])
    changed["deletion_state"] = "DELETION_FAILED"
    with pytest.raises(AssertionError):
        _validate_tombstone_chain([predecessor, changed])


def test_raw_canonical_bytes_accept_exact_and_reject_noncanonical(examples):
    artifact = examples[0]
    raw = _canonical_bytes(artifact)
    assert _parse_canonical_artifact(raw) == artifact
    variants = [raw + b"\n", b" " + raw, raw.replace(b'":', b'": ', 1), b"\xef\xbb\xbf" + raw]
    for variant in variants:
        with pytest.raises((AssertionError, UnicodeError, ValueError)):
            _parse_canonical_artifact(variant)
    with pytest.raises(ValueError):
        _parse_canonical_artifact(b'{"a":"1","a":"2"}')
    with pytest.raises(AssertionError):
        _parse_canonical_artifact('{"value":"e\u0301"}'.encode())
    with pytest.raises(AssertionError):
        _parse_canonical_artifact(b'{"number":1}')
    with pytest.raises(AssertionError):
        _parse_canonical_artifact(b'{"value":null}')
    with pytest.raises(AssertionError):
        _parse_canonical_artifact(b'{"value":"a\\/b"}')
    with pytest.raises(AssertionError):
        _parse_canonical_artifact(b'{"value":"\\u00e9"}')
    with pytest.raises(UnicodeDecodeError):
        _parse_canonical_artifact(b'{"value":"\xff"}')
    with pytest.raises(AssertionError):
        _parse_canonical_artifact('{"value":"\ufdd0"}'.encode())


def test_authority_order_shared_contracts_and_location_agreement(schema, corpus):
    responsibilities = schema["$defs"]["responsibility"]["enum"]
    for artifact in _fixture_map(corpus).values():
        if artifact["artifact_type"] == "LIFECYCLE_EVIDENCE_RECORD":
            indexes = [responsibilities.index(token) for token in artifact["authority_withheld"]]
            assert indexes == sorted(indexes) and len(indexes) == len(set(indexes))
    event = _fixture_map(corpus)["retention-retention-confirmed"]
    assert LOCATION_TYPES[event["location_identity"]["location_scheme"]] == event["location_type"]
    bad = deepcopy(event)
    bad["location_type"] = "REPOSITORY_PATH"
    assert LOCATION_TYPES[bad["location_identity"]["location_scheme"]] != bad["location_type"]
    for event in (
        artifact
        for artifact in _fixture_map(corpus).values()
        if artifact["artifact_type"] == "RETENTION_EVENT_RECORD"
    ):
        actor = event["actor_identity"]
        if actor["actor_role"] == "ACCOUNTABLE_HUMAN":
            assert actor["actor_type"] == "ACCOUNTABLE_HUMAN"
        for field in ("authority_reference", "assignment_authority"):
            reference = event[field]
            if reference == NA:
                continue
            reference = reference.get("authority_reference", reference)
            assert reference["issuer_actor_id"] == actor["actor_id"]
        assignment = event["assignment_authority"]
        if assignment != NA:
            assert (
                assignment["assigned_by_actor_id"]
                == assignment["authority_reference"]["issuer_actor_id"]
            )
    package_event = _fixture_map(corpus)["retention-package-assignment"]
    assert package_event["content_identity"] == NA
    assert re.fullmatch(
        r"ES-EVIDENCE-PACKAGE-SHA256-[0-9a-f]{64}",
        package_event["package_identity"]["package_id"],
    )


def test_fixture_corpus_names_required_positive_and_negative_cases(corpus):
    positive = {item["fixture_id"] for item in corpus["positive_fixtures"]}
    negative = {item["case_id"] for item in corpus["negative_fixtures"]}
    assert {
        "lifecycle-committed",
        "lifecycle-uncommitted",
        "lifecycle-staged",
        "lifecycle-untracked",
        "lifecycle-mixed",
        "lifecycle-published",
        "lifecycle-external",
        "retention-legal-hold-applied",
        "retention-legal-hold-released",
        "retention-deletion-authorized",
        "retention-deletion-completed",
        "tombstone-authorized",
        "tombstone-in-progress",
        "tombstone-failed",
        "tombstone-blocked-by-hold",
        "tombstone-completed",
        "retention-correction",
        "retention-invalidation",
        "retention-operational-successor-after-correction",
        "retention-replacement-after-invalidation",
        "tombstone-correction",
        "tombstone-evidence-correction",
        "tombstone-invalidation",
    } <= positive
    assert {
        "binding-contradictory",
        "binding-ambiguous-baseline",
        "binding-path-collision",
        "unsupported-version",
        "duplicate-authority",
        "authority-order",
        "retention-successor-after-completion",
        "completion-under-hold",
        "tombstone-invalid-jump",
        "tombstone-corrects-state",
        "completion-fields-noncompleted",
        "unknown-property",
    } <= negative


def test_every_declarative_negative_fixture_is_rejected(schema, corpus):
    fixtures = _fixture_map(corpus)
    rejected = set()
    for case in corpus["negative_fixtures"]:
        case_id = case["case_id"]
        base = deepcopy(fixtures[case["base_fixture_id"]])
        if case_id == "binding-contradictory":
            base["artifact_binding"]["classification"] = "UNTRACKED"
            assert not _matches(base, schema["$defs"]["lifecycleRecord"], schema)
        elif case_id == "binding-ambiguous-baseline":
            base["artifact_binding"]["baseline_commit"] = NA
            assert not _matches(base, schema["$defs"]["lifecycleRecord"], schema)
        elif case_id == "binding-path-collision":
            base["artifact_binding"]["entries"].append(
                deepcopy(base["artifact_binding"]["entries"][0])
            )
            with pytest.raises(AssertionError):
                _validate_binding(base["artifact_binding"])
        elif case_id == "unsupported-version":
            base["schema_version"] = "2.0.0"
            assert not _matches(base, schema["$defs"]["lifecycleRecord"], schema)
        elif case_id == "duplicate-authority":
            base["authority_withheld"].append(base["authority_withheld"][-1])
            assert not _matches(base, schema["$defs"]["lifecycleRecord"], schema)
        elif case_id == "authority-order":
            responsibilities = schema["$defs"]["responsibility"]["enum"]
            indexes = [
                responsibilities.index(token) for token in reversed(base["authority_withheld"])
            ]
            assert indexes != sorted(indexes)
        elif case_id == "retention-successor-after-completion":
            assert not SUCCESSORS["DELETION_COMPLETED"]
        elif case_id == "completion-under-hold":
            completion = deepcopy(fixtures["retention-deletion-completed"])
            completion["prior_retention_event_id"] = fixtures["retention-legal-hold-applied"][
                "retention_event_id"
            ]
            with pytest.raises(AssertionError):
                _validate_event_chain(
                    [fixtures["retention-assignment"], completion],
                    [fixtures["tombstone-completed"]],
                )
        elif case_id == "tombstone-invalid-jump":
            assert "DELETION_COMPLETED" not in TOMBSTONE_SUCCESSORS["DELETION_FAILED"]
        elif case_id == "tombstone-corrects-state":
            assert "deletion_state" not in schema["$defs"]["tombstoneCorrectableField"]["enum"]
        elif case_id == "completion-fields-noncompleted":
            base["deletion_completed_timestamp"] = "2026-08-03T14:00:00.000000Z"
            assert not _matches(base, schema["$defs"]["deletionTombstone"], schema)
        elif case_id == "unknown-property":
            base["undeclared"] = "x"
            assert not _matches(base, schema["$defs"]["lifecycleRecord"], schema)
        elif case_id in CORRECTION_NEGATIVE_CASE_IDS:
            with pytest.raises(AssertionError, match=case["expected_error"]):
                _assert_declared_correction_negative(case, fixtures, schema)
        elif "chain_case" in case["mutation"]:
            assert case["expected_error"] == "BLOCKED_DISCREPANT"
            with pytest.raises(AssertionError):
                _assert_named_invalid_chain_fails(corpus, case_id)
        elif "semantic_case" in case["mutation"]:
            assert case["expected_error"] == "BLOCKED_DISCREPANT"
            assert case["mutation"]["semantic_case"] == case_id
        else:
            raise AssertionError(f"unhandled negative fixture: {case_id}")
        rejected.add(case_id)
    assert rejected == {case["case_id"] for case in corpus["negative_fixtures"]}


def test_successor_graph_is_closed_and_completed_deletion_is_terminal():
    expected_kinds = set(REASONS)
    assert set(SUCCESSORS) == expected_kinds
    assert SUCCESSORS["DELETION_COMPLETED"] == set()
    for predecessor, allowed in SUCCESSORS.items():
        assert allowed <= expected_kinds
        assert predecessor not in allowed
    assert "DELETION_COMPLETED" not in SUCCESSORS["LEGAL_HOLD_APPLIED"]
    for preserving in {
        "RETENTION_CONFIRMED",
        "RETRIEVABILITY_CONFIRMED",
        "RETENTION_RELOCATED",
        "RETENTION_UNAVAILABLE",
        "RETENTION_RESTORED",
        "RETENTION_EXPIRED",
        "DELETION_AUTHORIZED",
    }:
        assert "LEGAL_HOLD_RELEASED" in SUCCESSORS[preserving]


def test_stable_id_arrays_limitations_and_privacy_fail_closed(schema, corpus):
    fixtures = _fixture_map(corpus)
    record = deepcopy(fixtures["lifecycle-committed"])
    record["findings"] = [
        {"item_id": "finding-2", "statement": "two"},
        {"item_id": "finding-1", "statement": "one"},
    ]
    with pytest.raises(AssertionError):
        _assert_sorted_unique(record["findings"], key=lambda item: item["item_id"])
    assert fixtures["retention-assignment"]["limitations"] == {
        "entries": [],
        "reason_code": "NONE",
        "status": "NONE",
    }
    record["secret"] = "prohibited"
    assert not _matches(record, schema["$defs"]["lifecycleRecord"], schema)
    standard = STANDARD_PATH.read_text(encoding="utf-8").lower()
    for prohibited in ("credentials", "secrets", "hidden reasoning", "unrestricted transcripts"):
        assert prohibited in standard


SEMANTIC_CORRECTIONS = {
    "event_timestamp": "RETENTION_EVENT_TIMESTAMP_V1",
    "actor_identity": "RETENTION_EVENT_ACTOR_IDENTITY_V1",
    "authority_reference": "RETENTION_EVENT_AUTHORITY_REFERENCE_V1",
    "reason_code": "RETENTION_EVENT_REASON_CODE_V1",
    "limitations": "RETENTION_EVENT_LIMITATIONS_V1",
}
EVIDENCE_CORRECTIONS = {
    "retention-evidence-correction-retention-class": ("RETENTION_CLASS", "AUTHORITY_REFERENCE"),
    "retention-evidence-correction-assignment-authority": (
        "ASSIGNMENT_AUTHORITY",
        "AUTHORITY_REFERENCE",
    ),
    "retention-evidence-correction-location": ("LOCATION_IDENTITY", "LOCATION_EVIDENCE"),
    "retention-evidence-correction-retrievability": (
        "RETRIEVABILITY_STATE",
        "RETRIEVABILITY_EVIDENCE",
    ),
    "retention-evidence-correction-attribution": ("EVENT_ATTRIBUTION", "ACTOR_IDENTITY"),
    "retention-evidence-correction-authority": ("EVENT_AUTHORITY", "AUTHORITY_REFERENCE"),
    "retention-evidence-correction-deletion": ("DELETION_COMPLETION", "DELETION_TOMBSTONE"),
    "retention-evidence-correction-hold": ("LEGAL_HOLD_STATUS", "LEGAL_HOLD_EVIDENCE"),
}
CORRECTION_NEGATIVE_FIELDS = (
    "event-timestamp",
    "actor-identity",
    "authority-reference",
    "reason-code",
    "limitations",
)
CORRECTION_NEGATIVE_CASE_IDS = {
    f"retention-correction-{field}-{failure}"
    for field in CORRECTION_NEGATIVE_FIELDS
    for failure in ("wrong-schema", "wrong-type", "stale-prior-value", "unchanged")
} | {
    "retention-correction-fields-misordered",
    "retention-correction-field-duplicate",
    "retention-correction-non-authorizing-statement-changed",
}


def _value_identity(value):
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _apply_declared_artifact_mutation(artifact, mutation):
    parts = mutation["path"].split(".")
    assert parts[0] == "artifact"
    path = tuple(int(part) if part.isdigit() else part for part in parts[1:])
    if path[-1] == "reverse":
        collection_path = path[:-1]
        node = artifact
        for part in collection_path:
            node = node[part]
        return _replace_path(artifact, collection_path, list(reversed(node)))
    if path[-1] == "+":
        collection_path = path[:-1]
        node = artifact
        for part in collection_path:
            node = node[part]
        return _replace_path(artifact, collection_path, node + [mutation["value"]])
    return _replace_path(artifact, path, mutation["value"])


def _assert_declared_correction_negative(case, fixtures, schema):
    event = _apply_declared_artifact_mutation(fixtures[case["base_fixture_id"]], case["mutation"])
    expected_error = case["expected_error"]
    fields = event["correction_details"]["corrected_fields"]
    if expected_error in {
        "WRONG_CORRECTION_VALUE_SCHEMA",
        "CORRECTED_VALUE_WRONG_TYPE",
        "NON_AUTHORIZING_STATEMENT_CHANGED",
    }:
        assert all(_matches(item, schema["$defs"]["correctedField"], schema) for item in fields), (
            expected_error
        )
    elif expected_error == "STALE_PRIOR_VALUE_IDENTITY":
        _validate(event, schema["$defs"]["retentionEvent"], schema)
        predecessor = fixtures["retention-deletion-authorized"]
        assert all(
            item["prior_value_identity"] == _value_identity(predecessor[item["field_name"]])
            for item in fields
        ), expected_error
    elif expected_error == "UNCHANGED_CORRECTED_VALUE":
        _validate(event, schema["$defs"]["retentionEvent"], schema)
        predecessor = fixtures["retention-deletion-authorized"]
        assert all(item["corrected_value"] != predecessor[item["field_name"]] for item in fields), (
            expected_error
        )
    elif expected_error == "CORRECTED_FIELDS_MISORDERED":
        keys = [
            (
                item["field_name"],
                item["prior_value_identity"],
                _value_identity(item["corrected_value"]),
            )
            for item in fields
        ]
        assert keys == sorted(keys), expected_error
    elif expected_error == "CORRECTED_FIELD_DUPLICATE":
        keys = [
            (
                item["field_name"],
                item["prior_value_identity"],
                _value_identity(item["corrected_value"]),
            )
            for item in fields
        ]
        assert len(keys) == len(set(keys)), expected_error
    else:
        raise AssertionError(f"unhandled correction negative: {case['case_id']}")


@pytest.mark.parametrize("case_id", sorted(CORRECTION_NEGATIVE_CASE_IDS))
def test_individually_named_correction_negative_fixtures_fail_for_intended_reason(
    corpus, schema, case_id
):
    fixtures = _fixture_map(corpus)
    cases = {item["case_id"]: item for item in corpus["negative_fixtures"]}
    assert CORRECTION_NEGATIVE_CASE_IDS <= cases.keys()
    case = cases[case_id]
    assert case["base_fixture_id"] in fixtures
    assert set(case["mutation"]) == {"path", "value"}
    with pytest.raises(AssertionError, match=case["expected_error"]):
        _assert_declared_correction_negative(case, fixtures, schema)


def _assert_correction_against_predecessor(event, predecessor, schema):
    _validate(event, schema["$defs"]["retentionEvent"], schema)
    assert event["prior_retention_event_id"] == predecessor["retention_event_id"]
    assert event["retention_event_id"] == _identity(event)
    assert predecessor["retention_event_id"] == _identity(predecessor)
    for item in event["correction_details"]["corrected_fields"]:
        field = item["field_name"]
        assert item["correction_value_schema"] == SEMANTIC_CORRECTIONS[field]
        assert item["prior_value_identity"] == _value_identity(predecessor[field])
        assert item["corrected_value"] != predecessor[field]
    _assert_sorted_unique(
        event["correction_details"]["corrected_fields"],
        key=lambda item: (
            item["field_name"],
            item["prior_value_identity"],
            _value_identity(item["corrected_value"]),
        ),
    )
    _assert_sorted_unique(
        event["correction_details"]["corrected_evidence"],
        key=lambda item: (
            item["supported_claim"],
            item["evidence_kind"],
            item["predecessor_evidence_identity"],
            item["corrected_evidence_identity"],
        ),
    )


@pytest.mark.parametrize("field,schema_name", SEMANTIC_CORRECTIONS.items())
def test_semantic_correction_fixtures_are_bound_typed_and_identity_changing(
    corpus, schema, field, schema_name
):
    fixtures = _fixture_map(corpus)
    predecessor = fixtures["retention-deletion-authorized"]
    event = fixtures[f"retention-correction-{field.replace('_', '-')}"]
    _assert_correction_against_predecessor(event, predecessor, schema)
    item = event["correction_details"]["corrected_fields"][0]
    assert item["field_name"] == field and item["correction_value_schema"] == schema_name
    assert event["retention_event_id"] != predecessor["retention_event_id"]
    for mutation in (
        lambda x: x.update(
            correction_value_schema=(
                "RETENTION_EVENT_ACTOR_IDENTITY_V1"
                if schema_name == "RETENTION_EVENT_TIMESTAMP_V1"
                else "RETENTION_EVENT_TIMESTAMP_V1"
            )
        ),
        lambda x: x.update(corrected_value=[]),
        lambda x: x.update(prior_value_identity="0" * 64),
        lambda x: x.update(corrected_value=deepcopy(predecessor[field])),
    ):
        bad = deepcopy(item)
        mutation(bad)
        schema_valid = _matches(bad, schema["$defs"]["correctedField"], schema)
        semantically_valid = (
            schema_valid
            and bad["prior_value_identity"] == _value_identity(predecessor[field])
            and bad["corrected_value"] != predecessor[field]
        )
        assert not semantically_valid


def test_correction_order_duplicates_constant_and_prohibited_fields_fail_closed(corpus, schema):
    fixtures = _fixture_map(corpus)
    event = fixtures["retention-correction-fields-and-evidence"]
    _assert_correction_against_predecessor(event, fixtures["retention-deletion-authorized"], schema)
    fields = event["correction_details"]["corrected_fields"]
    for malformed in (list(reversed(fields)), fields + [deepcopy(fields[0])]):
        with pytest.raises(AssertionError):
            _assert_sorted_unique(
                malformed,
                key=lambda item: (
                    item["field_name"],
                    item["prior_value_identity"],
                    _value_identity(item["corrected_value"]),
                ),
            )
    constant = deepcopy(fields[0])
    constant.update(
        field_name="non_authorizing_evidence_statement",
        correction_value_schema="RETENTION_EVENT_NON_AUTHORIZING_STATEMENT_V1",
        corrected_value="AUTHORITY_GRANTED",
    )
    assert not _matches(constant, schema["$defs"]["correctedField"], schema)
    prohibited = {
        "retention_class",
        "assignment_authority",
        "content_identity",
        "package_identity",
        "location_identity",
        "location_type",
        "retrievability_state",
        "deletion_tombstone_id",
        "schema_version",
        "record_identity",
        "transition_discriminator",
        "event_kind",
        "predecessor_lineage",
        "binding_structure",
        "operational_state",
    }
    allowed = set(schema["$defs"]["correctedField"]["properties"]["field_name"]["enum"])
    assert prohibited.isdisjoint(allowed)


@pytest.mark.parametrize("fixture_id,pair", EVIDENCE_CORRECTIONS.items())
def test_evidence_only_corrections_preserve_semantics_and_overlay_deterministically(
    corpus, schema, fixture_id, pair
):
    fixtures = _fixture_map(corpus)
    event = fixtures[fixture_id]
    predecessor = fixtures["retention-deletion-authorized"]
    _assert_correction_against_predecessor(event, predecessor, schema)
    assert event["correction_details"]["corrected_fields"] == []
    overlay = event["correction_details"]["corrected_evidence"][0]
    assert (overlay["supported_claim"], overlay["evidence_kind"]) == pair
    assert overlay["predecessor_evidence_identity"] != overlay["corrected_evidence_identity"]
    assert event["retention_event_id"] != predecessor["retention_event_id"]


def test_evidence_correction_unknown_malformed_equal_duplicate_and_order_fail_closed(
    corpus, schema
):
    event = deepcopy(_fixture_map(corpus)["retention-correction-fields-and-evidence"])
    item = event["correction_details"]["corrected_evidence"][0]
    for key, value in (
        ("supported_claim", "UNKNOWN_CLAIM"),
        ("evidence_kind", "UNKNOWN_KIND"),
        ("predecessor_evidence_identity", "bad"),
        ("corrected_evidence_identity", "bad"),
    ):
        bad = deepcopy(item)
        bad[key] = value
        assert not _matches(bad, schema["$defs"]["correctedEvidence"], schema)
    equal = deepcopy(item)
    equal["corrected_evidence_identity"] = equal["predecessor_evidence_identity"]
    assert _matches(equal, schema["$defs"]["correctedEvidence"], schema)
    assert equal["corrected_evidence_identity"] == equal["predecessor_evidence_identity"]
    with pytest.raises(AssertionError):
        assert equal["corrected_evidence_identity"] != equal["predecessor_evidence_identity"]
    for malformed in ([item, deepcopy(item)], [deepcopy(item), item]):
        with pytest.raises(AssertionError):
            _assert_sorted_unique(
                malformed,
                key=lambda x: (
                    x["supported_claim"],
                    x["evidence_kind"],
                    x["predecessor_evidence_identity"],
                    x["corrected_evidence_identity"],
                ),
            )


@pytest.mark.parametrize("preserving_kind", HOLD_PRESERVATION_FIXTURES)
def test_complete_hold_preservation_and_release_chains(corpus, preserving_kind):
    prefix, hold, preserved, released = _complete_hold_release_chain(corpus, preserving_kind)
    state_before_hold = _derive_event_state(prefix)
    state_after_hold = _derive_event_state(prefix + [hold])
    state_after_preservation = _derive_event_state(prefix + [hold, preserved])
    state_after_release = _derive_event_state(prefix + [hold, preserved, released])

    assert state_before_hold["legal_hold_state"] == "NO_HOLD"
    assert state_after_hold["legal_hold_state"] == "ACTIVE_HOLD"
    assert state_after_preservation["legal_hold_state"] == "ACTIVE_HOLD"
    assert state_after_release["legal_hold_state"] == "NO_HOLD"
    for predecessor, successor in zip(
        prefix + [hold, preserved], prefix[1:] + [hold, preserved, released], strict=True
    ):
        assert successor["prior_retention_event_id"] == predecessor["retention_event_id"]
    preservation_dimensions = {
        key: value for key, value in state_after_preservation.items() if key != "legal_hold_state"
    }
    release_dimensions = {
        key: value for key, value in state_after_release.items() if key != "legal_hold_state"
    }
    assert preservation_dimensions == release_dimensions
    assert {
        "retention_confirmation_state",
        "location_state",
        "location_identity",
        "retrievability_state",
        "availability_state",
        "retention_expiry_state",
        "deletion_authorization_state",
        "deletion_completion_state",
        "deletion_tombstone_id",
    } <= preservation_dimensions.keys()


def test_repeated_hold_application_fails_closed(corpus):
    with pytest.raises(AssertionError, match="prohibited operational successor"):
        _assert_named_invalid_chain_fails(corpus, "retention-repeated-hold-application")


def test_hold_release_without_active_hold_fails_closed(corpus):
    with pytest.raises(AssertionError, match="hold release without active hold"):
        _assert_named_invalid_chain_fails(corpus, "retention-release-without-hold")


def test_stale_correction_target_fails_closed(corpus):
    with pytest.raises(AssertionError, match="stale non-operational predecessor"):
        _assert_named_invalid_chain_fails(corpus, "retention-correction-stale-target")


def test_invalidation_without_unique_replacement_fails_closed(corpus):
    with pytest.raises(AssertionError, match="no unique replacement"):
        _assert_named_invalid_chain_fails(
            corpus, "retention-invalidation-without-unique-replacement"
        )


def test_retention_lineage_fork_fails_closed(corpus):
    with pytest.raises(AssertionError, match="retention lineage fork"):
        _assert_named_invalid_chain_fails(corpus, "retention-lineage-fork")


def test_retention_lineage_cycle_fails_closed(corpus):
    with pytest.raises(AssertionError, match="retention lineage cycle"):
        _assert_named_invalid_chain_fails(corpus, "retention-lineage-cycle")


def test_competing_successor_fails_closed(corpus):
    with pytest.raises(AssertionError, match="competing operational successor"):
        _assert_named_invalid_chain_fails(corpus, "retention-competing-successor")


def test_ambiguous_current_state_fails_closed(corpus):
    with pytest.raises(AssertionError, match="ambiguous current state"):
        _assert_named_invalid_chain_fails(corpus, "retention-ambiguous-current-state")


@pytest.mark.parametrize("preserving_kind", HOLD_PRESERVATION_FIXTURES)
def test_omitted_release_edges_execute_and_fail_closed(corpus, preserving_kind):
    prefix, hold, preserved, released = _complete_hold_release_chain(corpus, preserving_kind)
    graph = deepcopy(SUCCESSORS)
    graph[preserving_kind].remove("LEGAL_HOLD_RELEASED")
    with pytest.raises(AssertionError, match="prohibited operational successor"):
        _derive_event_state(prefix + [hold, preserved, released], successors=graph)


@pytest.mark.parametrize("kind", sorted(REASONS))
def test_every_operational_successor_after_completion_executes_and_fails_closed(corpus, kind):
    fixtures = _fixture_map(corpus)
    completed_chain = [
        fixtures[name]
        for name in (
            "retention-assignment",
            "retention-retention-confirmed",
            "retention-retrievability-confirmed-under-hold",
            "retention-legal-hold-applied",
            "retention-retention-unavailable",
            "retention-retention-restored",
            "retention-legal-hold-released",
            "retention-retention-relocated",
            "retention-retrievability-confirmed",
            "retention-retention-expired",
            "retention-deletion-authorized",
            "retention-deletion-completed",
        )
    ]
    template = next(
        item["artifact"]
        for item in corpus["positive_fixtures"]
        if item["artifact"].get("event_kind") == kind
    )
    attempted = _rebase_event(template, completed_chain[-1])
    with pytest.raises(AssertionError, match="prohibited operational successor"):
        _derive_event_state(completed_chain + [attempted], [fixtures["tombstone-completed"]])


LIFECYCLE_IDENTITY_CATEGORIES = {
    "governed subject": "governed_subject",
    "ES-6 responsibility": "lifecycle_responsibility",
    "scope": "review_or_execution_scope",
    "authority evidence": "accountable_human_authorization",
    "actor identity": "actor_identity",
    "reviewer identity": "authorization_issuer",
    "independence declaration": "independence_declaration",
    "findings": "findings",
    "decision/status": "decision",
    "risks": "residual_risks",
    "uncertainty": "uncertainty",
    "timestamp": "completion_timestamp",
    "evidence origin": "evidence_origin_state",
    "retention assignment": "retention_assignment_authority",
    "predecessor lineage": "predecessor_evidence_id",
    "payload digest": "artifact_sha256",
    "payload media type": "resulting_artifact_identity",
    "artifact binding": "artifact_binding",
}


@pytest.mark.parametrize("category,field", LIFECYCLE_IDENTITY_CATEGORIES.items())
def test_lifecycle_semantic_category_churn_rejects_stale_identity(corpus, category, field):
    record = deepcopy(_fixture_map(corpus)["lifecycle-committed"])
    stale = record["evidence_record_id"]
    value = record[field]
    if isinstance(value, str):
        record[field] = value + "-changed"
    elif isinstance(value, list):
        record[field] = value + [{"item_id": "zz-change", "statement": "identity change"}]
    else:
        record[field] = {**value, "identity_test_extension": "changed"}
    assert stale != _identity(record)
    assert record["evidence_record_id"] == stale


def test_identity_must_not_change_categories(corpus):
    record = deepcopy(_fixture_map(corpus)["lifecycle-committed"])
    expected = _identity(record)
    assert _identity(dict(reversed(list(record.items())))) == expected
    relocated = deepcopy(record)
    relocated["payload_location"] = "elsewhere/record.json"
    assert _identity(relocated) == expected
    assert _canonical_bytes({"b": "2", "a": "1"}) == _canonical_bytes({"a": "1", "b": "2"})


ARTIFACT_BINDING_CHURN_CATEGORIES = (
    "artifact bytes",
    "Git object",
    "mode",
    "path",
    "baseline",
    "classification",
    "rename",
    "deletion",
    "symlink",
    "submodule",
)


def _manifest_binding_from_fixture_entries(corpus, replacements=None):
    replacements = replacements or {}
    entries_by_id = {
        item["fixture_id"]: deepcopy(item["entry"]) for item in corpus["manifest_entry_fixtures"]
    }
    entries_by_id.update(deepcopy(replacements))
    entries = sorted(entries_by_id.values(), key=lambda entry: entry["path"].encode())
    binding = {
        "binding_mode": "MIXED_MANIFEST",
        "schema_version": "1.0.0",
        "baseline_commit": "1" * 40,
        "inclusions": [entry["path"] for entry in entries],
        "exclusions": [],
        "entries": entries,
        "filter_state": "EXACT_INDEX_AND_RAW_WORKTREE_BYTES",
    }
    binding["candidate_manifest_id"] = _candidate_manifest_identity(binding)
    return binding


def _artifact_binding_churn_case(corpus, category):
    entries = {
        item["fixture_id"]: deepcopy(item["entry"]) for item in corpus["manifest_entry_fixtures"]
    }
    replacements = {}
    if category == "symlink":
        symlink = entries["ME-STAGED-ADD"]
        symlink["resulting_mode"] = "120000"
        symlink["symlink_target_sha256"] = "3" * 64
        replacements["ME-STAGED-ADD"] = symlink
    elif category == "submodule":
        submodule = entries["ME-STAGED-ADD"]
        submodule.update(
            resulting_bytes=NA,
            resulting_sha256=NA,
            byte_length=NA,
            resulting_mode="160000",
            symlink_target_sha256=NA,
            submodule_commit_id="3" * 40,
        )
        replacements["ME-STAGED-ADD"] = submodule
    binding = _manifest_binding_from_fixture_entries(corpus, replacements)
    entry_indexes = {entry["path"]: index for index, entry in enumerate(binding["entries"])}
    targets = {
        "artifact bytes": (
            ("entries", entry_indexes["fixtures/ME-STAGED-ADD"], "resulting_bytes", "sha256"),
            "3" * 64,
        ),
        "Git object": (
            ("entries", entry_indexes["fixtures/ME-STAGED-ADD"], "resulting_git_object_id"),
            "2" * 40,
        ),
        "mode": (
            ("entries", entry_indexes["fixtures/ME-STAGED-ADD"], "resulting_mode"),
            "100755",
        ),
        "path": (
            ("entries", entry_indexes["fixtures/ME-WORKTREE-ADD"], "path"),
            "fixtures/ME-WORKTREE-ADD-changed",
        ),
        "baseline": (("baseline_commit",), "2" * 40),
        "classification": (
            ("entries", entry_indexes["fixtures/ME-STAGED-ADD"], "classification"),
            "UNTRACKED",
        ),
        "rename": (
            ("entries", entry_indexes["fixtures/ME-RENAME-OLD"], "rename_to"),
            "fixtures/ME-RENAME-NEW-changed",
        ),
        "deletion": (
            ("entries", entry_indexes["fixtures/ME-STAGED-DEL-ABSENT"], "deletion"),
            False,
        ),
        "symlink": (
            ("entries", entry_indexes["fixtures/ME-STAGED-ADD"], "symlink_target_sha256"),
            "4" * 64,
        ),
        "submodule": (
            ("entries", entry_indexes["fixtures/ME-STAGED-ADD"], "submodule_commit_id"),
            "4" * 40,
        ),
    }
    path, replacement = targets[category]
    return binding, path, replacement


@pytest.mark.parametrize("category", ARTIFACT_BINDING_CHURN_CATEGORIES)
def test_artifact_binding_identity_churn_matrix(corpus, schema, category):
    binding, path, replacement = _artifact_binding_churn_case(corpus, category)
    _validate_binding(binding)
    for entry in binding["entries"]:
        _validate(entry, schema["$defs"]["manifestEntry"], schema)
    stale_identity = binding["candidate_manifest_id"]
    changed = _replace_path(binding, path, replacement)
    assert _changed_paths(binding, changed) == {path}
    assert _candidate_manifest_identity(changed) != stale_identity
    assert changed["candidate_manifest_id"] == stale_identity
    with pytest.raises(AssertionError, match="stale candidate manifest identity"):
        assert changed["candidate_manifest_id"] == _candidate_manifest_identity(changed), (
            "stale candidate manifest identity"
        )


RETENTION_EVENT_CHURN_CASES = (
    "corrected field name",
    "correction value schema",
    "prior value identity",
    "corrected value",
    "supported claim",
    "evidence kind",
    "predecessor evidence identity",
    "corrected evidence identity",
    "invalidated fields",
    "invalidation reason",
    "invalidation authority identity",
    "attributable replacement identity",
    "predecessor lineage",
    "evidence record identity",
    "location identity",
    "location type",
    "retrievability field",
    "limitations status",
    "transition discriminator",
    "event kind",
)


def _retention_event_churn_case(corpus, case_name):
    fixtures = _fixture_map(corpus)
    correction = fixtures["retention-correction-event-timestamp"]
    evidence = fixtures["retention-evidence-correction-retention-class"]
    invalidation = fixtures["retention-invalidation"]
    relocation = fixtures["retention-retention-relocated"]
    cases = {
        "corrected field name": (
            correction,
            ("correction_details", "corrected_fields", 0, "field_name"),
            "actor_identity",
            False,
        ),
        "correction value schema": (
            correction,
            ("correction_details", "corrected_fields", 0, "correction_value_schema"),
            "RETENTION_EVENT_ACTOR_IDENTITY_V1",
            False,
        ),
        "prior value identity": (
            correction,
            ("correction_details", "corrected_fields", 0, "prior_value_identity"),
            "0" * 64,
            True,
        ),
        "corrected value": (
            correction,
            ("correction_details", "corrected_fields", 0, "corrected_value"),
            "2026-08-03T13:22:00.000000Z",
            True,
        ),
        "supported claim": (
            evidence,
            ("correction_details", "corrected_evidence", 0, "supported_claim"),
            "EVENT_ATTRIBUTION",
            True,
        ),
        "evidence kind": (
            evidence,
            ("correction_details", "corrected_evidence", 0, "evidence_kind"),
            "ACTOR_IDENTITY",
            True,
        ),
        "predecessor evidence identity": (
            evidence,
            (
                "correction_details",
                "corrected_evidence",
                0,
                "predecessor_evidence_identity",
            ),
            "6" * 64,
            True,
        ),
        "corrected evidence identity": (
            evidence,
            ("correction_details", "corrected_evidence", 0, "corrected_evidence_identity"),
            "7" * 64,
            True,
        ),
        "invalidated fields": (
            invalidation,
            ("invalidation_details", "invalidated_fields"),
            ["event_timestamp", "reason_code"],
            True,
        ),
        "invalidation reason": (
            invalidation,
            ("invalidation_details", "invalidation_reason_code"),
            "CLAIM_CONTRADICTED",
            True,
        ),
        "invalidation authority identity": (
            invalidation,
            ("invalidation_details", "invalidation_authority_reference", "source_identity"),
            "retention-decision-2",
            True,
        ),
        "attributable replacement identity": (
            invalidation,
            ("invalidation_details", "attributable_replacement_event_id"),
            fixtures["retention-replacement-after-invalidation"]["retention_event_id"],
            True,
        ),
        "predecessor lineage": (
            correction,
            ("prior_retention_event_id",),
            "ES-EVIDENCE-RETENTION-EVENT-SHA256-" + "0" * 64,
            True,
        ),
        "evidence record identity": (
            relocation,
            ("evidence_record_id",),
            "ES-EVIDENCE-RECORD-SHA256-" + "0" * 64,
            True,
        ),
        "location identity": (
            relocation,
            ("location_identity", "resulting_location_identity", "location_value"),
            "immutable:relocated-object",
            True,
        ),
        "location type": (
            relocation,
            ("location_type",),
            "EXTERNAL_IMMUTABLE_OBJECT",
            True,
        ),
        "retrievability field": (
            fixtures["retention-retention-confirmed"],
            ("retrievability_state",),
            "RETRIEVABLE",
            False,
        ),
        "limitations status": (
            relocation,
            ("limitations", "status"),
            "UNAVAILABLE",
            False,
        ),
        "transition discriminator": (
            relocation,
            ("retention_event_transition_kind",),
            "CORRECTION",
            False,
        ),
        "event kind": (
            relocation,
            ("event_kind",),
            "RETENTION_CONFIRMED",
            False,
        ),
    }
    return cases[case_name]


@pytest.mark.parametrize("case_name", RETENTION_EVENT_CHURN_CASES)
def test_retention_event_identity_churn_matrix(corpus, schema, case_name):
    artifact, path, replacement, remains_schema_valid = _retention_event_churn_case(
        corpus, case_name
    )
    _validate(artifact, schema["$defs"]["retentionEvent"], schema)
    assert artifact["retention_event_id"] == _identity(artifact)
    changed = _replace_path(artifact, path, replacement)
    assert _changed_paths(artifact, changed) == {path}
    assert _identity(changed) != artifact["retention_event_id"]
    with pytest.raises(AssertionError, match="stale retention-event identity"):
        assert changed["retention_event_id"] == _identity(changed), "stale retention-event identity"
    assert _matches(changed, schema["$defs"]["retentionEvent"], schema) is (remains_schema_valid)
    if case_name == "location type":
        resulting = changed["location_identity"]["resulting_location_identity"]
        assert LOCATION_TYPES[resulting["location_scheme"]] != changed["location_type"]


TOMBSTONE_CHURN_CASES = (
    "artifact discriminator",
    "deletion-state discriminator",
    "tombstone transition kind",
    "predecessor tombstone ID",
    "authorization identity",
    "completion linkage",
    "corrected fields",
    "corrected evidence",
    "invalidation details",
    "admissibility effect",
    "retrievability status",
    "legal-hold status",
    "raw canonical semantic bytes",
)


def _tombstone_churn_case(corpus, case_name):
    fixtures = _fixture_map(corpus)
    completed = fixtures["tombstone-completed"]
    correction = fixtures["tombstone-correction"]
    evidence = fixtures["tombstone-evidence-correction"]
    invalidation = fixtures["tombstone-invalidation"]
    cases = {
        "artifact discriminator": (completed, ("artifact_type",), "UNKNOWN_ARTIFACT", False),
        "deletion-state discriminator": (
            completed,
            ("deletion_state",),
            "DELETION_AUTHORIZED",
            False,
        ),
        "tombstone transition kind": (
            completed,
            ("tombstone_transition_kind",),
            "CORRECTION",
            False,
        ),
        "predecessor tombstone ID": (
            completed,
            ("predecessor_tombstone_id",),
            "ES-EVIDENCE-DELETION-TOMBSTONE-SHA256-" + "0" * 64,
            True,
        ),
        "authorization identity": (
            completed,
            ("deletion_authority_reference", "source_identity"),
            "deletion-decision-2",
            True,
        ),
        "completion linkage": (
            completed,
            ("retention_event_id",),
            "ES-EVIDENCE-RETENTION-EVENT-SHA256-" + "0" * 64,
            True,
        ),
        "corrected fields": (
            correction,
            ("tombstone_transition_details", "corrected_fields", 0),
            "deletion_reason_category",
            True,
        ),
        "corrected evidence": (
            evidence,
            (
                "tombstone_transition_details",
                "corrected_evidence",
                0,
                "corrected_evidence_identity",
            ),
            "5" * 64,
            True,
        ),
        "invalidation details": (
            invalidation,
            ("tombstone_transition_details", "invalidation_reason_code"),
            "CLAIM_CONTRADICTED",
            True,
        ),
        "admissibility effect": (
            completed,
            ("admissibility_effect",),
            "Deleted payload is unavailable to byte-dependent gates",
            True,
        ),
        "retrievability status": (
            completed,
            ("retrievability_state",),
            "PARTIALLY_RETRIEVABLE",
            False,
        ),
        "legal-hold status": (
            completed,
            ("legal_hold_status",),
            "ACTIVE_HOLD",
            False,
        ),
        "raw canonical semantic bytes": (
            completed,
            ("remaining_retained_metadata",),
            ["content identity", "authority lineage", "completion digest"],
            True,
        ),
    }
    return cases[case_name]


@pytest.mark.parametrize("case_name", TOMBSTONE_CHURN_CASES)
def test_deletion_tombstone_identity_churn_matrix(corpus, schema, case_name):
    artifact, path, replacement, remains_schema_valid = _tombstone_churn_case(corpus, case_name)
    _validate(artifact, schema["$defs"]["deletionTombstone"], schema)
    assert artifact["deletion_tombstone_id"] == _identity(artifact)
    changed = _replace_path(artifact, path, replacement)
    assert _changed_paths(artifact, changed) == {path}
    original_semantics = {
        key: value for key, value in artifact.items() if key != "deletion_tombstone_id"
    }
    changed_semantics = {
        key: value for key, value in changed.items() if key != "deletion_tombstone_id"
    }
    assert (
        hashlib.sha256(_canonical_bytes(original_semantics)).digest()
        != hashlib.sha256(_canonical_bytes(changed_semantics)).digest()
    )
    if case_name != "artifact discriminator":
        assert _identity(changed) != artifact["deletion_tombstone_id"]
        with pytest.raises(AssertionError, match="stale tombstone identity"):
            assert changed["deletion_tombstone_id"] == _identity(changed), (
                "stale tombstone identity"
            )
    assert _matches(changed, schema["$defs"]["deletionTombstone"], schema) is (remains_schema_valid)


PACKAGE_MANIFEST_FIELDS = {
    "schema_version",
    "package_id",
    "record_ids",
    "payload_references",
    "package_scope",
    "creation_mode",
    "authority_neutrality",
}


def _package_manifest_identity(package):
    semantics = {key: value for key, value in package.items() if key != "package_id"}
    return "ES-EVIDENCE-PACKAGE-SHA256-" + hashlib.sha256(_canonical_bytes(semantics)).hexdigest()


def _closed_package_manifest(record_ids):
    package = {
        "schema_version": "1.0.0",
        "package_id": "",
        "record_ids": sorted(record_ids),
        "payload_references": [],
        "package_scope": "ES-7 lifecycle evidence conformance fixture",
        "creation_mode": "BOUNDED_STATIC_FIXTURE",
        "authority_neutrality": NON_AUTHORIZING,
    }
    package["package_id"] = _package_manifest_identity(package)
    return package


def _validate_package_manifest(package):
    assert set(package) == PACKAGE_MANIFEST_FIELDS
    assert package["schema_version"] == "1.0.0"
    _assert_sorted_unique(package["record_ids"])
    assert all(
        re.fullmatch(r"ES-EVIDENCE-RECORD-SHA256-[0-9a-f]{64}", record_id)
        for record_id in package["record_ids"]
    )
    _assert_sorted_unique(
        package["payload_references"],
        key=lambda item: (item["sha256"], item["media_type"]),
    )
    assert package["authority_neutrality"] == NON_AUTHORIZING
    assert package["package_id"] == _package_manifest_identity(package), "stale package identity"


def test_package_membership_identity_contract(corpus):
    fixtures = _fixture_map(corpus)
    members = [fixtures["lifecycle-committed"], fixtures["lifecycle-external"]]
    member_identities = [member["evidence_record_id"] for member in members]
    package = _closed_package_manifest(member_identities)
    _validate_package_manifest(package)
    package_event = fixtures["retention-package-assignment"]
    assert package_event["package_identity"]["package_id"] == package["package_id"]

    added = _closed_package_manifest(
        member_identities + [fixtures["lifecycle-uncommitted"]["evidence_record_id"]]
    )
    removed = _closed_package_manifest(member_identities[:-1])
    reordered = _closed_package_manifest(list(reversed(member_identities)))
    assert added["package_id"] != package["package_id"]
    assert removed["package_id"] != package["package_id"]
    assert reordered["package_id"] == package["package_id"]
    assert [member["evidence_record_id"] for member in members] == member_identities
    assert all(
        _identity(member) == member_id
        for member, member_id in zip(members, member_identities, strict=True)
    )

    stale = deepcopy(package)
    stale["record_ids"].append(fixtures["lifecycle-uncommitted"]["evidence_record_id"])
    stale["record_ids"].sort()
    with pytest.raises(AssertionError, match="stale package identity"):
        _validate_package_manifest(stale)
    duplicate = deepcopy(package)
    duplicate["record_ids"].append(duplicate["record_ids"][0])
    duplicate["record_ids"].sort()
    with pytest.raises(AssertionError):
        _validate_package_manifest(duplicate)


def test_retention_tombstone_package_and_manifest_identity_boundaries(corpus):
    fixtures = _fixture_map(corpus)
    for fixture_id in (
        "retention-correction-fields-and-evidence",
        "retention-invalidation",
        "tombstone-correction",
        "tombstone-evidence-correction",
        "tombstone-invalidation",
    ):
        artifact = fixtures[fixture_id]
        changed = deepcopy(artifact)
        changed[
            "event_timestamp"
            if artifact["artifact_type"] == "RETENTION_EVENT_RECORD"
            else "admissibility_effect"
        ] += " changed"
        assert _identity(changed) != _identity(artifact)
    manifest = deepcopy(fixtures["lifecycle-mixed"]["artifact_binding"])
    stale = manifest["candidate_manifest_id"]
    manifest["entries"][0]["path"] += "-changed"
    payload = {
        k: v
        for k, v in manifest.items()
        if k not in {"binding_mode", "candidate_manifest_id", "filter_state"}
    }
    recomputed = (
        "ES-CANDIDATE-MANIFEST-SHA256-" + hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    )
    assert stale != recomputed
