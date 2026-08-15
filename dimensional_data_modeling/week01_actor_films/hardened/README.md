# Week 1 Hardened SQL

## Purpose

This directory contains post-grade, production-oriented variants of the
DataExpert Week 1 dimensional data modeling assignment.

The original submission earned a final grade of **A** and remains unchanged
under:

    ../submission/

The exact graded Git baseline is:

- Tag: `week01-graded-a`
- Commit: `4e1f775`

The hardened variants begin as byte-for-byte copies of the graded SQL and are
modified only on the dedicated branch:

    improve/week01-post-grade-hardening

## Engineering Goals

Post-grade improvements may include:

- reusable year parameterization
- explicit idempotent rerun behavior
- stronger constraints and defaults
- deterministic film-array construction
- documented film deduplication behavior
- explicit null-rating policy
- stronger SCD boundary handling
- supporting indexes
- additional reconciliation and regression validation

## Preservation Rule

Files under `../submission/` must not be modified as part of post-grade
hardening.

All behavioral changes belong in this directory and must be validated against
the known-good graded results before being committed.

## Phase 1 — Parameterization and Transactional Idempotency

Validated on PostgreSQL 14 using the official DataExpert Week 1 dataset.

### Cumulative Actors

`query_2.sql` now accepts:

- `previous_year`
- `current_year`

The target `current_year` snapshot is transactionally replaced before
regeneration.

Validation for 2020 -> 2021:

- rows regenerated: 9,447
- differences versus graded result: 0
- second-run differences: 0

### Incremental SCD

`query_5.sql` now accepts:

- `previous_year`
- `current_year`

The target SCD snapshot is transactionally replaced before regeneration.

Validation for 2020 -> 2021:

- rows generated: 119,331
- differences versus full 2021 backfill: 0
- second run deleted: 119,331
- second run inserted: 119,331

### Rerun Policy

The hardened implementation uses transactional replace semantics:

1. `BEGIN`
2. delete only the target snapshot
3. regenerate the target snapshot
4. `COMMIT`

If generation fails, PostgreSQL rolls back the transaction, preventing a
partially deleted or partially rebuilt snapshot.

The graded submission under `../submission/` remains unchanged.

