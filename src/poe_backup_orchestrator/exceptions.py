"""Common exception hierarchy for the POE Backup Orchestrator."""


class OrchestratorError(Exception):
    """Base exception for all expected orchestrator failures."""


class ConfigurationError(OrchestratorError):
    """Raised when application configuration is invalid or unavailable."""


class BootstrapError(OrchestratorError):
    """Raised when application initialization cannot be completed."""


class RepositoryValidationError(OrchestratorError):
    """Raised when repository validation cannot be executed."""


class SqliteBackupError(OrchestratorError):
    """Raised when a consistent SQLite backup cannot be completed."""


class RegistryIngestionError(OrchestratorError):
    """Raised when a Registry acquisition artifact fails ingestion validation."""


class RegistryAcceptanceError(OrchestratorError):
    """Raised when a Registry acquisition cannot be accepted."""


class RegistryAcceptanceLockError(RegistryAcceptanceError):
    """Raised when Registry acceptance cannot acquire its repository lock."""


class RegistryAcceptanceConflictError(RegistryAcceptanceError):
    """Raised when an accepted run conflicts with a validated acquisition."""


class RegistryAcceptanceInconsistentError(RegistryAcceptanceError):
    """Raised when an existing acceptance destination is incomplete or polluted."""


class OperationalReportingError(OrchestratorError):
    """Raised when an operational report cannot be durably published."""


class RuntimeStateError(OrchestratorError):
    """Base exception for durable runtime-state failures."""


class RuntimeStatePersistenceError(RuntimeStateError):
    """Raised when runtime state cannot be durably saved, loaded, or cleared."""


class RuntimeStateCorruptionError(RuntimeStateError):
    """Raised when persisted runtime-state JSON is malformed or structurally invalid."""


class RuntimeStateSchemaError(RuntimeStateError):
    """Raised when persisted runtime state uses an unsupported schema version."""
