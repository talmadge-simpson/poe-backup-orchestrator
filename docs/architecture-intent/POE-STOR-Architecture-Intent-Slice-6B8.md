# POE Storage Architecture Intent — Slice 6B-8

## Validation Result Assembly

**Status:** Implementation slice  
**Predecessor:** Slice 6B-7 Validation Finding Generation  
**Implementation authorization:** Limited to this slice

## Purpose

Slice 6B-8 assembles the already-derived technical validation inputs into one
immutable `PreservationBaselineValidationResult`.

The slice does not load evidence, deserialize evidence, extract facts,
reconcile records, generate findings, persist evidence, evaluate acceptance
policy, or record human authority.

## Responsibility

`PreservationBaselineValidationResultAssembler` accepts:

- one immutable `PreservationBaselineCandidate`;
- one explicit `PreservationEvidenceValidationPolicy`;
- immutable validated evidence references;
- immutable ordered validation findings; and
- an explicit UTC validation timestamp.

It produces exactly one immutable validation result.

## Determinism

The assembler:

1. canonicalizes validated evidence by source-root identity, evidence type, and
   evidence path;
2. rejects duplicate validated references;
3. requires contiguous finding sequences beginning with one;
4. derives the stable validation identifier from the candidate identifier,
   policy profile, canonical validated evidence, and ordered findings; and
5. excludes the validation timestamp from the stable identifier.

Repeated assembly from semantically identical inputs produces the same
validation identifier.

## Existing Model Authority

The existing model layer remains authoritative for:

- candidate and baseline lineage;
- exact coverage of all present candidate evidence references;
- immutable result construction;
- validation schema version;
- stable identifier validation; and
- canonical finding invariants.

The assembler does not duplicate or weaken those model invariants.

## Failure Boundary

`PreservationBaselineValidationError` is raised when a deterministic result
cannot safely be assembled, including:

- invalid input types;
- mutable collection inputs;
- duplicate validated references;
- noncontiguous finding sequences; or
- rejection by the authoritative result model.

Evidence defects remain findings produced by earlier analytical stages. They
are not converted into service exceptions by this slice.

## Authority Boundary

This slice contains no:

- acceptance recommendation;
- acceptance mode;
- blocking classification;
- overridability decision;
- exception approval;
- human authorization;
- persistence;
- migration authority;
- client redirection;
- source cleanup authority; or
- destructive behavior.

A technically complete validation result does not imply acceptance.
