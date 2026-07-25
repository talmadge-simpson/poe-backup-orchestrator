"""Repository validation models for the POE Backup Orchestrator."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RepositoryValidationResult:
    """Structured result returned by repository validation."""

    command: tuple[str, ...]
    return_code: int
    mounted: bool
    healthy: bool
    operational: bool
    standard_output: str
    standard_error: str

    @property
    def is_valid(self) -> bool:
        """Return whether the repository satisfies all required conditions."""
        return self.return_code == 0 and self.mounted and self.healthy and self.operational
