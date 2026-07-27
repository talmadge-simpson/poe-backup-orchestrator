# POE Backup Orchestrator Architecture Intent — Slice 4A

## Production Runtime Foundation

### Objective

Establish an explicit, deterministic runtime boundary between development,
test, and production execution without introducing packaging, systemd,
timer, log-rotation, or deployment automation concerns.

### Decisions

1. Runtime selection is explicit and strongly typed.
2. Configuration remains authoritative for the configured environment.
3. A requested environment must match the configuration.
4. Production configuration resolves beneath `/etc/poe/backup-orchestrator`.
5. Production state and log roots use the discovered `/var/lib` and `/var/log`
   hierarchies.
6. Production identity is `poe-backup:poe-backup`.
7. Production bootstrap validates identity, paths, access, and create/write/remove
   capability before exposing application context.
8. Capability probes are ephemeral and removed.
9. Development and test configuration paths remain supported.
10. Packaging, systemd, timers, logrotate, and deployment remain deferred.

### Acceptance Criteria

- Runtime environments are strongly typed.
- Production paths and identity are centralized.
- Unsupported environments fail deterministically.
- Environment mismatches fail bootstrap.
- Validation returns structured evidence.
- Existing behavior and automated tests remain intact.
- Ruff, pytest, and Git whitespace validation pass.
