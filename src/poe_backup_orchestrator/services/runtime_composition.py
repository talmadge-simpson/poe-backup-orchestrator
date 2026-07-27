"""Production composition helpers for runtime-state services."""

from __future__ import annotations

from pathlib import Path

from poe_backup_orchestrator.models import Clock
from poe_backup_orchestrator.services.run_service import SystemUtcClock
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspector,
    SystemHostIdentity,
    SystemProcessLiveness,
)
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore


def build_runtime_recovery_inspector(
    *,
    state_root: Path,
    clock: Clock | None = None,
) -> RuntimeRecoveryInspector:
    """Build the production dependency graph for runtime-state inspection."""

    return RuntimeRecoveryInspector(
        store=RuntimeStateStore(state_root),
        host_identity=SystemHostIdentity(),
        process_liveness=SystemProcessLiveness(),
        clock=clock or SystemUtcClock(),
    )
