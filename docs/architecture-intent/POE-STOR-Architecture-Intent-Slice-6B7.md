# POE Storage Architecture Intent — Slice 6B-7

## Deterministic Validation Finding Generation

**Document ID:** POE-STOR-Architecture-Intent-Slice-6B7  
**Status:** Implementation checkpoint  
**Phase:** 6B — Preservation Baseline Acceptance  
**Slice:** 6B-7 — Validation Finding Generation  
**Certified predecessor:** `1833047`

## Purpose

This slice converts immutable preservation-evidence reconciliation observations
into immutable `ValidationFinding` objects.

The service is analytical only. It does not decide whether a finding blocks
acceptance, whether an exception is overridable, whether a baseline should be
accepted, or whether migration or cleanup may proceed.

## Inputs

The generator consumes one `PreservationEvidenceReconciliation` and the exact
absolute paths of the inventory and content-integrity evidence artifacts. It
does not reload, rewrite, repair, infer, or persist evidence.

## Certified Finding Rules

- Source-root disagreement becomes `SOURCE_ROOT_IDENTITY_MISMATCH` with
  `CRITICAL` severity.
- Reconciliation interpretation failure becomes `CONTRADICTORY_EVIDENCE` with
  `CRITICAL` severity.
- Inventory declared-count disagreement becomes
  `INVENTORY_RECONCILIATION_MISMATCH` with `ERROR` severity.
- Duplicate relative paths become `DUPLICATE_EVIDENCE` with `ERROR` severity.
- Inventory-only records become
  `CONTENT_INTEGRITY_RECONCILIATION_MISMATCH` with `ERROR` severity.
- Integrity-only records become `INVENTORY_RECONCILIATION_MISMATCH` with
  `ERROR` severity.
- Conflicting non-null item identifiers become `CONTRADICTORY_EVIDENCE` with
  `ERROR` severity.

Successful reconciliation creates no routine `VERIFIED` findings.

## Determinism and Authority Boundary

Finding drafts use the approved canonical sort key. Contiguous sequences are
assigned only after sorting, beginning with one.

This slice contains no acceptance recommendation, blocking classification,
exception approval, human authorization, persistence, migration authority,
client redirection, cleanup authority, or destructive behavior.
