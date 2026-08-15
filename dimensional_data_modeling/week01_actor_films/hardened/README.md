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
