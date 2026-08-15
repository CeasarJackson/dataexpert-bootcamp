# DataExpert Week 1 — Post-Grade Improvement Plan

## Baseline

The graded Week 1 submission earned a final grade of **A**.

Git baseline:

- Tag: `week01-graded-a`
- Commit: `4e1f775`

The purpose of this branch is not to correct a failed submission. It is to
preserve the graded implementation while exploring production-oriented
hardening and engineering improvements.

## Grader-Recommended Improvements

### 1. Schema constraints

Consider strengthening business-rule enforcement:

- `actors.actor` -> `NOT NULL`
- `actors.quality_class` -> `NOT NULL`
- `actors.is_active` -> `NOT NULL`
- `actors.films` -> `NOT NULL DEFAULT ARRAY[]::film_struct[]`

### 2. Rating precision

Evaluate replacing `REAL` with:

- `DOUBLE PRECISION`
- `NUMERIC(3,1)`

Document implications for `AVG(rating)` and quality thresholds.

### 3. Parameterization

Replace hard-coded processing years with reusable runtime parameters for:

- cumulative actor generation
- incremental SCD generation

### 4. Idempotency

Define an explicit rerun policy.

Candidate strategies:

- fail on duplicate snapshot
- delete or truncate the target snapshot before rerun
- `ON CONFLICT DO UPDATE`
- `ON CONFLICT DO NOTHING`

The preferred policy should be documented and tested.

### 5. Film-array consistency

Evaluate:

- deterministic ordering by `filmid`
- deduplication by `filmid`
- behavior when a source film is replayed or duplicated

### 6. SCD robustness

Consider:

- explicit first-row streak initialization
- interval-overlap validation
- handling missing annual snapshots
- handling reappearing actors

### 7. Null-rating policy

PostgreSQL `AVG()` ignores null ratings.

If all incoming ratings are null, define whether the desired behavior is:

- retain the previous `quality_class`
- classify as `bad`
- classify as unknown or reject the row

### 8. Indexing

Evaluate indexes such as:

    CREATE INDEX ON actor_films (year, actorid);
    CREATE INDEX ON actors (actorid, current_year);
    CREATE INDEX ON actors_history_scd (actorid, current_year);
    CREATE INDEX ON actors_history_scd (actorid, start_date, end_date);

Measure whether each index improves actual workload patterns.

## Engineering Approach

Changes should be introduced incrementally:

1. Preserve the graded baseline.
2. Add one improvement category at a time.
3. Inspect the Git diff.
4. Rerun SQL validation.
5. Compare row counts and SCD equivalence.
6. Commit only after validation passes.

## Validation Expectations

Post-grade changes must preserve the known-good Week 1 outcomes unless a
documented business-rule change intentionally alters them.

Baseline validation results include:

- cumulative actor coverage from 1970 through 2021
- 9,447 distinct actors
- 249,082 actor-year snapshots
- zero duplicate `(actorid, current_year)` rows
- 119,331 SCD rows for the 2021 backfill snapshot
- zero invalid SCD date ranges
- zero overlapping SCD intervals
- zero differences between the 2021 incremental SCD result and full backfill

## Repository Layout

The graded submission must remain unchanged under:

    dimensional_data_modeling/week01_actor_films/submission/

Production-oriented variants should be developed separately under:

    dimensional_data_modeling/week01_actor_films/hardened/

Development and validation helpers may remain under:

    dimensional_data_modeling/week01_actor_films/sql/
    dimensional_data_modeling/week01_actor_films/validation/

## Non-Goals

This branch will not:

- alter the historical `week01-graded-a` tag
- overwrite the original graded submission files
- change business rules without documenting the rationale
- claim production readiness without validation
- merge hardened behavior into the graded baseline
