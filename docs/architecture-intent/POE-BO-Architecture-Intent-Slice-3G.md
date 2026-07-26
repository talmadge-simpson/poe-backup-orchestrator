# POE Backup Orchestrator Architecture Intent — Slice 3G

## 1. Slice Identity

- **Slice:** 3G
- **Title:** CLI Integration and Executable Composition
- **Status:** Implementation Candidate
- **Branch:** `feature/cli-integration`
- **Depends on:** Slices 3A–3F

## 2. Purpose

Slice 3G converts the orchestration and reporting capabilities delivered in
Slices 3A–3F into a production-oriented command-line execution path.

The CLI remains a presentation and argument-parsing layer. Runtime dependency
composition, orchestration, report generation, report publication, and process
exit-code selection belong to an application service.

## 3. Command Contract

The new command is:

```text
poe-backup-orchestrator run \
  --source PATH \
  [--asset-id ASSET_ID] \
  [--destination-root PATH]
```

Defaults:

- `asset-id`: `poeregistry`
- `destination-root`:
  `<repository_root>/Registry/POERegistry`

The command uses the configured staging and reporting roots.

## 4. Composition Boundary

The execution path is:

```text
CLI
  -> bootstrap
  -> RegistryBackupRunService
     -> repository readiness guard
     -> RegistryBackupOrchestrator
        -> Registry acquisition
        -> acquisition validation
        -> repository acceptance
     -> operational report projection
     -> atomic report publication
  -> operator summary
  -> process exit code
```

The CLI must not reproduce orchestration logic.

## 5. Integration Compatibility Requirement

The existing generic SQLite backup service emits a generic SQLite manifest.
The Registry ingestion service requires the governed Registry acquisition
manifest contract.

Slice 3G therefore introduces a Registry-specific acquisition wrapper. It:

1. delegates transactionally consistent SQLite backup creation to the existing
   SQLite backup service;
2. replaces the generic manifest with the Registry acquisition contract;
3. preserves manifest-last publication;
4. returns the existing `SqliteBackupResult` model so orchestration contracts
   remain unchanged.

This is an integration normalization, not a replacement of the generic SQLite
backup service.

## 6. Repository Readiness

A repository validation result that is not valid must stop execution before
Registry acquisition begins. The runtime composition layer converts an invalid
result into `RepositoryValidationError`, allowing existing failure mapping to
produce exit code `20`.

## 7. Runtime Identity and Time

Production runtime implementations must provide:

- timezone-aware UTC timestamps;
- filesystem-safe, collision-resistant job identifiers.

Job IDs use:

```text
YYYYMMDDTHHMMSSffffffZ-<12 hex characters>
```

## 8. Reporting and Exit Codes

Every completed orchestration result, including governed operational failures,
must be projected and published as JSON and text reports.

Exit-code policy:

- successful execution: `0`
- governed orchestration failure: the mapped failure exit code
- configuration/bootstrap error: `1` under the legacy CLI boundary
- report publication failure: `60`
- unexpected programmer defect: propagate unchanged during service execution

A report publication failure is written to stderr because the report itself
could not be durably published.

## 9. Operator Output

The `run` command prints the human-readable operational summary followed by:

- JSON report path
- text summary path

The CLI returns the run-service exit code without reclassifying it.

## 10. Deliverables

- `services/registry_acquisition.py`
- `services/run_service.py`
- updated `services/adapters.py`
- updated `services/__init__.py`
- updated `exceptions.py`
- updated `cli.py`
- `tests/unit/test_registry_acquisition_service.py`
- `tests/unit/test_run_service.py`
- expanded `tests/unit/test_cli.py`

## 11. Verification

Verification must include:

- Registry-specific manifest compatibility;
- invalid repository readiness stopping acquisition;
- successful orchestration and report publication;
- governed failure report publication and mapped exit code;
- reporting publication failure mapped to exit code `60`;
- CLI argument forwarding;
- CLI operator output;
- all preexisting tests;
- Ruff formatting and linting.

## 12. Acceptance Criteria

Slice 3G is complete when:

1. `poe-backup-orchestrator run` is available.
2. Runtime composition is outside `cli.py`.
3. Registry acquisition manifests pass the existing ingestion contract.
4. Invalid repository readiness prevents acquisition.
5. Success and governed failure reports are published.
6. Exit codes are deterministic.
7. Ruff passes.
8. The full pytest suite passes.
