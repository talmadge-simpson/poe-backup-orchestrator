"""Tests for production runtime-state service composition."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from poe_backup_orchestrator.services import build_runtime_recovery_inspector
from poe_backup_orchestrator.services.runtime_recovery import (
    RuntimeRecoveryInspector,
    SystemHostIdentity,
    SystemProcessLiveness,
)
from poe_backup_orchestrator.services.runtime_state_store import RuntimeStateStore


@dataclass(frozen=True)
class FixedClock:
    value: datetime = datetime(2026, 7, 27, 17, 0, tzinfo=UTC)

    def now_utc(self) -> datetime:
        return self.value


def test_builder_composes_runtime_recovery_inspector(tmp_path: Path) -> None:
    """Confirm the runtime inspector factory owns its production graph."""

    clock = FixedClock()
    inspector = build_runtime_recovery_inspector(
        state_root=tmp_path / "state",
        clock=clock,
    )

    assert isinstance(inspector, RuntimeRecoveryInspector)
    assert isinstance(inspector.store, RuntimeStateStore)
    assert inspector.store.state_root == tmp_path / "state"
    assert isinstance(inspector.host_identity, SystemHostIdentity)
    assert isinstance(inspector.process_liveness, SystemProcessLiveness)
    assert inspector.clock is clock


def test_builder_is_exported_from_services_package() -> None:
    """Confirm callers can depend on the public composition boundary."""

    from poe_backup_orchestrator import services

    assert services.build_runtime_recovery_inspector is build_runtime_recovery_inspector
