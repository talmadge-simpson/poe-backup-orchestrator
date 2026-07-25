"""Common exception hierarchy for the POE Backup Orchestrator."""


class OrchestratorError(Exception):
    """Base exception for all expected orchestrator failures."""


class ConfigurationError(OrchestratorError):
    """Raised when application configuration is invalid or unavailable."""


class BootstrapError(OrchestratorError):
    """Raised when application initialization cannot be completed."""
