# POE Backup Orchestrator Architecture Intent — Slice 5E-4

## Minimal Restore Execution CLI

Expose a same-process `restore execute` workflow that validates the repository, discovers and evaluates one recovery point, builds an in-memory plan, requires `--confirm-execution`, loads an explicit validation-policy TOML, executes the certified restore pipeline, publishes immutable evidence, and prints completion details. This slice does not persist plans or introduce an approval state machine.
