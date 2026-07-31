"""Construction and immutable publication of accepted preservation baselines."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
import types
from dataclasses import dataclass, field, fields, is_dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final, Union, get_args, get_origin, get_type_hints

from poe_backup_orchestrator.models.storage_accepted_baseline import (
    STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION,
    AcceptedPreservationBaseline,
    AcceptedPreservationBaselineArtifact,
    AcceptedPreservationBaselineIdentity,
    AcceptedPreservationBaselineMode,
    AcceptedPreservationBaselinePublicationResult,
    AcceptedPreservationBaselineReference,
    stable_accepted_preservation_baseline_id,
)
from poe_backup_orchestrator.models.storage_baseline_authorization import (
    AuthorizationDecisionOutcome,
    PreservationBaselineAuthorizationDecision,
)
from poe_backup_orchestrator.models.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationArtifact,
    PreservationBaselineAuthorizationPersistenceResult,
)
from poe_backup_orchestrator.services.storage_baseline_authorization_persistence import (
    PreservationBaselineAuthorizationSerializer,
)
from poe_backup_orchestrator.utilities.locking import (
    LockContentionError,
    LockingError,
    exclusive_file_lock,
)

ACCEPTED_BASELINE_PUBLICATION_LOCK_FILENAME: Final[str] = (
    "accepted-preservation-baseline-publication.lock"
)
_FULL_PREFIX: Final[str] = "accepted-preservation-baseline-"
_REFERENCE_PREFIX: Final[str] = "accepted-preservation-baseline-reference-"


class AcceptedPreservationBaselineError(RuntimeError):
    """Base failure for accepted-baseline verification and publication."""


class PersistedAuthorizationVerificationError(AcceptedPreservationBaselineError):
    """Persisted authorization evidence could not be verified exactly."""


class AcceptedPreservationBaselineConstructionError(AcceptedPreservationBaselineError):
    """Verified authorization cannot produce an accepted baseline."""


class AcceptedPreservationBaselinePublicationError(AcceptedPreservationBaselineError):
    """Accepted-baseline evidence could not be durably published."""


class AcceptedPreservationBaselineConflictError(AcceptedPreservationBaselinePublicationError):
    """Immutable accepted-baseline publication state is contradictory."""


class AcceptedPreservationBaselineLockError(AcceptedPreservationBaselinePublicationError):
    """Exclusive accepted-baseline publication ownership is unavailable."""


@dataclass(frozen=True, slots=True)
class _VerifiedAuthorization:
    decision: PreservationBaselineAuthorizationDecision
    artifact: PreservationBaselineAuthorizationArtifact
    content: bytes


@dataclass(slots=True)
class AcceptedPreservationBaselineConstructor:
    """Verify one persisted authorization and project exactly one baseline."""

    authorization_serializer: PreservationBaselineAuthorizationSerializer = (
        PreservationBaselineAuthorizationSerializer()
    )

    def construct(
        self,
        persistence_result: PreservationBaselineAuthorizationPersistenceResult,
    ) -> AcceptedPreservationBaseline:
        if not isinstance(persistence_result, PreservationBaselineAuthorizationPersistenceResult):
            raise PersistedAuthorizationVerificationError(
                "persistence_result must be PreservationBaselineAuthorizationPersistenceResult"
            )
        verified = self._verify_authorization(persistence_result)
        decision = verified.decision
        mode = _mode_for_outcome(decision.outcome)
        identity = decision.identity
        accepted_baseline_id = stable_accepted_preservation_baseline_id(
            authorization_id=identity.authorization_id,
            evaluation_id=identity.evaluation_id,
            validation_id=identity.validation_id,
            candidate_id=identity.candidate_id,
            baseline_id=identity.baseline_id,
            mode=mode,
            accepted_source_root_ids=decision.scope.accepted_source_root_ids,
            excluded_source_root_ids=decision.scope.excluded_source_root_ids,
            scope_limitations=decision.scope.scope_limitations,
            condition_decisions=decision.condition_decisions,
            pilot=decision.pilot,
            retention_obligations=decision.retention_obligations,
            supersession_eligible=decision.supersession_eligible,
        )
        accepted_roots = set(decision.scope.accepted_source_root_ids)
        graph = tuple(
            observation
            for observation in decision.recommendation.validation_result.candidate.observations
            if observation.source_root_id in accepted_roots
        )
        try:
            return AcceptedPreservationBaseline(
                identity=AcceptedPreservationBaselineIdentity(
                    schema_version=STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION,
                    accepted_baseline_id=accepted_baseline_id,
                    authorization_id=identity.authorization_id,
                    evaluation_id=identity.evaluation_id,
                    validation_id=identity.validation_id,
                    candidate_id=identity.candidate_id,
                    baseline_id=identity.baseline_id,
                ),
                authorization_decision=decision,
                authorization_artifact_sha256=verified.artifact.sha256,
                authorization_artifact_byte_count=verified.artifact.byte_count,
                mode=mode,
                accepted_source_root_ids=decision.scope.accepted_source_root_ids,
                excluded_source_root_ids=decision.scope.excluded_source_root_ids,
                scope_limitations=decision.scope.scope_limitations,
                accepted_evidence_graph=graph,
                condition_decisions=decision.condition_decisions,
                pilot=decision.pilot,
                retention_obligations=decision.retention_obligations,
                supersession_eligible=decision.supersession_eligible,
            )
        except ValueError as exc:
            raise AcceptedPreservationBaselineConstructionError(
                f"accepted-baseline construction failed: {exc}"
            ) from exc

    def _verify_authorization(
        self,
        result: PreservationBaselineAuthorizationPersistenceResult,
    ) -> _VerifiedAuthorization:
        artifact = result.artifact
        expected_name = f"preservation-baseline-authorization-{result.authorization_id}.json"
        if artifact.evidence_path.name != expected_name:
            raise PersistedAuthorizationVerificationError(
                "authorization artifact filename does not match authorization_id"
            )
        _require_regular_pair(
            artifact.evidence_path,
            artifact.sha256_path,
            PersistedAuthorizationVerificationError,
            "authorization",
        )
        try:
            content = artifact.evidence_path.read_bytes()
            sidecar = artifact.sha256_path.read_bytes()
        except OSError as exc:
            raise PersistedAuthorizationVerificationError(
                f"unable to read persisted authorization evidence: {exc}"
            ) from exc
        digest = hashlib.sha256(content).hexdigest()
        expected_sidecar = f"{digest}  {expected_name}\n".encode("ascii")
        if len(content) != artifact.byte_count:
            raise PersistedAuthorizationVerificationError(
                "authorization artifact byte count does not match persistence result"
            )
        if digest != artifact.sha256:
            raise PersistedAuthorizationVerificationError(
                "authorization artifact digest does not match persistence result"
            )
        if sidecar != expected_sidecar:
            raise PersistedAuthorizationVerificationError(
                "authorization SHA-256 sidecar is malformed or contradictory"
            )
        try:
            decision = _decode_exact(content, PreservationBaselineAuthorizationDecision)
            canonical = self.authorization_serializer.serialize(decision)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise PersistedAuthorizationVerificationError(
                f"authorization artifact cannot be reconstructed exactly: {exc}"
            ) from exc
        except Exception as exc:
            if isinstance(exc, AcceptedPreservationBaselineError):
                raise
            raise PersistedAuthorizationVerificationError(
                f"authorization artifact verification failed: {exc}"
            ) from exc
        if canonical != content:
            raise PersistedAuthorizationVerificationError(
                "authorization artifact bytes are not canonical"
            )
        if decision.identity.authorization_id != result.authorization_id:
            raise PersistedAuthorizationVerificationError(
                "authorization identity does not match persistence result"
            )
        if decision.identity.baseline_id != result.baseline_id:
            raise PersistedAuthorizationVerificationError(
                "authorization baseline identity does not match persistence result"
            )
        return _VerifiedAuthorization(decision=decision, artifact=artifact, content=content)


class AcceptedPreservationBaselineSerializer:
    """Canonical serializer for full accepted baselines and references."""

    def serialize(
        self,
        value: AcceptedPreservationBaseline | AcceptedPreservationBaselineReference,
    ) -> bytes:
        if not isinstance(
            value, (AcceptedPreservationBaseline, AcceptedPreservationBaselineReference)
        ):
            raise AcceptedPreservationBaselinePublicationError(
                "value must be an accepted baseline or accepted-baseline reference"
            )
        try:
            payload = _json_value(value)
            text = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        except AcceptedPreservationBaselineError:
            raise
        except (TypeError, ValueError) as exc:
            raise AcceptedPreservationBaselinePublicationError(
                f"accepted-baseline serialization failed: {exc}"
            ) from exc
        return f"{text}\n".encode()


@dataclass(slots=True)
class AcceptedPreservationBaselinePublisher:
    """Publish the full baseline pair followed by its authoritative reference pair."""

    constructor: AcceptedPreservationBaselineConstructor = field(
        default_factory=AcceptedPreservationBaselineConstructor
    )
    serializer: AcceptedPreservationBaselineSerializer = field(
        default_factory=AcceptedPreservationBaselineSerializer
    )

    def publish(
        self,
        *,
        persistence_result: PreservationBaselineAuthorizationPersistenceResult,
        destination_directory: Path,
    ) -> AcceptedPreservationBaselinePublicationResult:
        baseline = self.constructor.construct(persistence_result)
        destination = Path(destination_directory)
        if not destination.is_absolute():
            raise AcceptedPreservationBaselinePublicationError(
                "destination_directory must be absolute"
            )
        baseline_content = self.serializer.serialize(baseline)
        baseline_digest = hashlib.sha256(baseline_content).hexdigest()
        accepted_id = baseline.identity.accepted_baseline_id
        baseline_filename = f"{_FULL_PREFIX}{accepted_id}.json"
        baseline_path = destination / baseline_filename
        baseline_sidecar_path = destination / f"{baseline_filename}.sha256"
        reference = AcceptedPreservationBaselineReference(
            schema_version=STORAGE_ACCEPTED_BASELINE_SCHEMA_VERSION,
            accepted_baseline_id=accepted_id,
            baseline_id=baseline.identity.baseline_id,
            authorization_id=baseline.identity.authorization_id,
            mode=baseline.mode,
            accepted_source_root_ids=baseline.accepted_source_root_ids,
            excluded_source_root_ids=baseline.excluded_source_root_ids,
            accepted_baseline_filename=baseline_filename,
            accepted_baseline_sha256_filename=f"{baseline_filename}.sha256",
            accepted_baseline_sha256=baseline_digest,
            accepted_baseline_byte_count=len(baseline_content),
        )
        reference_content = self.serializer.serialize(reference)
        reference_digest = hashlib.sha256(reference_content).hexdigest()
        reference_filename = f"{_REFERENCE_PREFIX}{accepted_id}.json"
        reference_path = destination / reference_filename
        reference_sidecar_path = destination / f"{reference_filename}.sha256"
        contents = (
            baseline_content,
            f"{baseline_digest}  {baseline_filename}\n".encode("ascii"),
            reference_content,
            f"{reference_digest}  {reference_filename}\n".encode("ascii"),
        )
        paths = (
            baseline_path,
            baseline_sidecar_path,
            reference_path,
            reference_sidecar_path,
        )
        if any(path.parent != destination for path in paths):
            raise AcceptedPreservationBaselinePublicationError(
                "accepted-baseline identity produced an unsafe publication path"
            )
        lock_path = destination / ".locks" / ACCEPTED_BASELINE_PUBLICATION_LOCK_FILENAME
        try:
            destination.mkdir(parents=True, exist_ok=True, mode=0o770)
            if not destination.is_dir():
                raise AcceptedPreservationBaselinePublicationError(
                    "destination_directory must identify a directory"
                )
            lock_path.parent.mkdir(parents=True, exist_ok=True, mode=0o770)
        except AcceptedPreservationBaselineError:
            raise
        except OSError as exc:
            raise AcceptedPreservationBaselinePublicationError(
                f"unable to prepare accepted-baseline destination {destination}: {exc}"
            ) from exc
        try:
            with exclusive_file_lock(lock_path):
                replay = self._publish_under_lock(
                    paths=paths,
                    contents=contents,
                    accepted_baseline_id=accepted_id,
                )
        except LockContentionError as exc:
            raise AcceptedPreservationBaselineLockError(
                f"accepted-baseline publication is already active: {destination}"
            ) from exc
        except LockingError as exc:
            raise AcceptedPreservationBaselineLockError(
                f"accepted-baseline publication lock failed for {destination}: {exc}"
            ) from exc
        return _publication_result(
            baseline=baseline,
            paths=paths,
            digests=(baseline_digest, reference_digest),
            byte_counts=(len(baseline_content), len(reference_content)),
            replay=replay,
        )

    def load_from_reference(
        self,
        reference_artifact: AcceptedPreservationBaselineArtifact,
    ) -> AcceptedPreservationBaseline:
        """Independently verify the reference boundary and its full baseline."""

        if not isinstance(reference_artifact, AcceptedPreservationBaselineArtifact):
            raise AcceptedPreservationBaselinePublicationError(
                "reference_artifact must be AcceptedPreservationBaselineArtifact"
            )
        reference_content = _verify_artifact_contract(reference_artifact, "reference")
        try:
            reference = _decode_exact(reference_content, AcceptedPreservationBaselineReference)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AcceptedPreservationBaselinePublicationError(
                f"accepted-baseline reference is invalid: {exc}"
            ) from exc
        if self.serializer.serialize(reference) != reference_content:
            raise AcceptedPreservationBaselinePublicationError(
                "accepted-baseline reference is not canonical"
            )
        parent = reference_artifact.evidence_path.parent
        baseline_artifact = AcceptedPreservationBaselineArtifact(
            evidence_path=parent / reference.accepted_baseline_filename,
            sha256_path=parent / reference.accepted_baseline_sha256_filename,
            sha256=reference.accepted_baseline_sha256,
            byte_count=reference.accepted_baseline_byte_count,
        )
        baseline_content = _verify_artifact_contract(baseline_artifact, "accepted baseline")
        try:
            baseline = _decode_exact(baseline_content, AcceptedPreservationBaseline)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise AcceptedPreservationBaselinePublicationError(
                f"accepted-baseline artifact is invalid: {exc}"
            ) from exc
        if self.serializer.serialize(baseline) != baseline_content:
            raise AcceptedPreservationBaselinePublicationError(
                "accepted-baseline artifact is not canonical"
            )
        if (
            baseline.identity.accepted_baseline_id != reference.accepted_baseline_id
            or baseline.identity.baseline_id != reference.baseline_id
            or baseline.identity.authorization_id != reference.authorization_id
            or baseline.mode is not reference.mode
            or baseline.accepted_source_root_ids != reference.accepted_source_root_ids
            or baseline.excluded_source_root_ids != reference.excluded_source_root_ids
        ):
            raise AcceptedPreservationBaselineConflictError(
                "accepted-baseline reference metadata conflicts with full artifact"
            )
        return baseline

    def _publish_under_lock(
        self,
        *,
        paths: tuple[Path, Path, Path, Path],
        contents: tuple[bytes, bytes, bytes, bytes],
        accepted_baseline_id: str,
    ) -> bool:
        existence = tuple(os.path.lexists(path) for path in paths)
        if any(existence):
            if not all(existence):
                raise _conflict(
                    accepted_baseline_id,
                    "incomplete_publication_set",
                    next(path for path, exists in zip(paths, existence, strict=True) if exists),
                )
            _require_exact_publication(paths, contents, accepted_baseline_id)
            return True

        created = [False, False, False, False]
        try:
            for index, (path, content) in enumerate(zip(paths, contents, strict=True)):
                _persist_exclusively(path, content)
                created[index] = True
                _fsync_directory(path.parent)
        except FileExistsError as exc:
            if all(os.path.lexists(path) for path in paths):
                try:
                    _require_exact_publication(paths, contents, accepted_baseline_id)
                except AcceptedPreservationBaselineError:
                    pass
                else:
                    return True
            cleanup_error = _cleanup_created(paths, created)
            if cleanup_error is not None:
                raise AcceptedPreservationBaselinePublicationError(
                    "accepted-baseline race cleanup failed"
                ) from cleanup_error
            raise _conflict(
                accepted_baseline_id,
                "concurrent_publication_race",
                Path(exc.filename) if exc.filename else paths[0],
            ) from exc
        except OSError as exc:
            cleanup_error = _cleanup_created(paths, created)
            if cleanup_error is not None:
                raise AcceptedPreservationBaselinePublicationError(
                    "accepted-baseline publication failed and cleanup also failed"
                ) from cleanup_error
            raise AcceptedPreservationBaselinePublicationError(
                f"unable to publish accepted-baseline evidence: {exc}"
            ) from exc
        return False


def _mode_for_outcome(outcome: AuthorizationDecisionOutcome) -> AcceptedPreservationBaselineMode:
    mapping = {
        AuthorizationDecisionOutcome.AUTHORIZE: AcceptedPreservationBaselineMode.STRICT,
        AuthorizationDecisionOutcome.AUTHORIZE_WITH_EXCEPTIONS: (
            AcceptedPreservationBaselineMode.APPROVED_EXCEPTIONS
        ),
        AuthorizationDecisionOutcome.AUTHORIZE_PARTIAL_SCOPE: (
            AcceptedPreservationBaselineMode.PARTIAL_SOURCE
        ),
        AuthorizationDecisionOutcome.AUTHORIZE_PILOT: AcceptedPreservationBaselineMode.PILOT,
    }
    try:
        return mapping[outcome]
    except KeyError as exc:
        raise AcceptedPreservationBaselineConstructionError(
            "rejected authorization cannot produce an accepted baseline"
        ) from exc


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() != UTC.utcoffset(value):
            raise AcceptedPreservationBaselinePublicationError(
                "accepted-baseline content contains a non-UTC datetime"
            )
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise AcceptedPreservationBaselinePublicationError(
        f"accepted-baseline content contains unsupported value {type(value).__name__}"
    )


def _decode_exact(content: bytes, expected_type: type[Any]) -> Any:
    text = content.decode("utf-8")

    def object_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON field: {key}")
            result[key] = value
        return result

    payload = json.loads(text, object_pairs_hook=object_hook)
    return _typed_value(payload, expected_type, "$", get_type_hints)


def _typed_value(
    value: Any,
    expected: Any,
    path: str,
    hints_loader: Any,
) -> Any:
    origin = get_origin(expected)
    args = get_args(expected)
    if origin in (Union, types.UnionType):
        if value is None and type(None) in args:
            return None
        candidates = tuple(item for item in args if item is not type(None))
        errors: list[Exception] = []
        for candidate in candidates:
            try:
                return _typed_value(value, candidate, path, hints_loader)
            except (TypeError, ValueError) as exc:
                errors.append(exc)
        raise TypeError(f"{path} does not match its governed union type") from errors[-1]
    if origin is tuple:
        if not isinstance(value, list):
            raise TypeError(f"{path} must be an array")
        item_type = args[0]
        return tuple(
            _typed_value(item, item_type, f"{path}[{index}]", hints_loader)
            for index, item in enumerate(value)
        )
    if is_dataclass(expected):
        if not isinstance(value, dict):
            raise TypeError(f"{path} must be an object")
        hints = hints_loader(expected)
        expected_fields = {field.name for field in fields(expected)}
        actual_fields = set(value)
        missing = expected_fields - actual_fields
        unknown = actual_fields - expected_fields
        if missing:
            raise ValueError(f"{path} missing fields: {sorted(missing)}")
        if unknown:
            raise ValueError(f"{path} contains unknown fields: {sorted(unknown)}")
        kwargs = {
            field.name: _typed_value(
                value[field.name], hints[field.name], f"{path}.{field.name}", hints_loader
            )
            for field in fields(expected)
        }
        return expected(**kwargs)
    if isinstance(expected, type) and issubclass(expected, Enum):
        if not isinstance(value, str):
            raise TypeError(f"{path} must be a string enum value")
        return expected(value)
    if expected is datetime:
        if not isinstance(value, str):
            raise TypeError(f"{path} must be a UTC timestamp string")
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
            raise ValueError(f"{path} must be UTC")
        return parsed.astimezone(UTC)
    if expected is Path:
        if not isinstance(value, str):
            raise TypeError(f"{path} must be a path string")
        return Path(value)
    if expected is bool:
        if type(value) is not bool:
            raise TypeError(f"{path} must be bool")
        return value
    if expected is int:
        if type(value) is not int:
            raise TypeError(f"{path} must be int")
        return value
    if expected is str:
        if not isinstance(value, str):
            raise TypeError(f"{path} must be string")
        return value
    raise TypeError(f"{path} has unsupported governed type {expected!r}")


def _require_regular_pair(
    artifact_path: Path,
    sidecar_path: Path,
    error_type: type[AcceptedPreservationBaselineError],
    label: str,
) -> None:
    for target in (artifact_path, sidecar_path):
        try:
            mode = target.lstat().st_mode
        except OSError as exc:
            raise error_type(f"{label} evidence target is missing or unreadable: {target}") from exc
        if not stat.S_ISREG(mode):
            raise error_type(f"{label} evidence target is not a regular file: {target}")


def _verify_artifact_contract(
    artifact: AcceptedPreservationBaselineArtifact,
    label: str,
) -> bytes:
    _require_regular_pair(
        artifact.evidence_path,
        artifact.sha256_path,
        AcceptedPreservationBaselinePublicationError,
        label,
    )
    try:
        content = artifact.evidence_path.read_bytes()
        sidecar = artifact.sha256_path.read_bytes()
    except OSError as exc:
        raise AcceptedPreservationBaselinePublicationError(
            f"unable to read {label} evidence: {exc}"
        ) from exc
    digest = hashlib.sha256(content).hexdigest()
    expected_sidecar = f"{digest}  {artifact.evidence_path.name}\n".encode("ascii")
    if len(content) != artifact.byte_count or digest != artifact.sha256:
        raise AcceptedPreservationBaselineConflictError(
            f"{label} artifact metadata conflicts with stored bytes"
        )
    if sidecar != expected_sidecar:
        raise AcceptedPreservationBaselineConflictError(
            f"{label} sidecar is malformed or contradictory"
        )
    return content


def _require_exact_publication(
    paths: tuple[Path, Path, Path, Path],
    contents: tuple[bytes, bytes, bytes, bytes],
    accepted_baseline_id: str,
) -> None:
    for path, proposed in zip(paths, contents, strict=True):
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            raise AcceptedPreservationBaselinePublicationError(
                f"unable to inspect existing publication target {path}: {exc}"
            ) from exc
        if not stat.S_ISREG(mode):
            raise _conflict(accepted_baseline_id, "non_regular_publication_target", path)
        try:
            existing = path.read_bytes()
        except OSError as exc:
            raise AcceptedPreservationBaselinePublicationError(
                f"unable to read existing publication target {path}: {exc}"
            ) from exc
        if existing != proposed:
            raise _conflict(accepted_baseline_id, "publication_content_conflict", path)


def _publication_result(
    *,
    baseline: AcceptedPreservationBaseline,
    paths: tuple[Path, Path, Path, Path],
    digests: tuple[str, str],
    byte_counts: tuple[int, int],
    replay: bool,
) -> AcceptedPreservationBaselinePublicationResult:
    return AcceptedPreservationBaselinePublicationResult(
        accepted_baseline_id=baseline.identity.accepted_baseline_id,
        baseline_id=baseline.identity.baseline_id,
        authorization_id=baseline.identity.authorization_id,
        accepted_baseline_artifact=AcceptedPreservationBaselineArtifact(
            evidence_path=paths[0],
            sha256_path=paths[1],
            sha256=digests[0],
            byte_count=byte_counts[0],
        ),
        reference_artifact=AcceptedPreservationBaselineArtifact(
            evidence_path=paths[2],
            sha256_path=paths[3],
            sha256=digests[1],
            byte_count=byte_counts[1],
        ),
        idempotent_replay=replay,
    )


def _conflict(
    accepted_baseline_id: str,
    classification: str,
    target: Path,
) -> AcceptedPreservationBaselineConflictError:
    return AcceptedPreservationBaselineConflictError(
        f"accepted_baseline_id={accepted_baseline_id}; "
        f"classification={classification}; target={target}"
    )


def _persist_exclusively(destination: Path, content: bytes) -> None:
    descriptor = -1
    temporary_path: Path | None = None
    try:
        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        temporary_path = Path(raw_path)
        os.fchmod(descriptor, 0o640)
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary_path, destination)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _cleanup_created(paths: tuple[Path, Path, Path, Path], created: list[bool]) -> OSError | None:
    try:
        for path, was_created in reversed(tuple(zip(paths, created, strict=True))):
            if was_created:
                path.unlink(missing_ok=True)
        if any(created):
            _fsync_directory(paths[0].parent)
    except OSError as exc:
        return exc
    return None


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
