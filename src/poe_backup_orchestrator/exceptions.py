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
