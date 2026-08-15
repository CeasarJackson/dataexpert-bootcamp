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

## Phase 3 — Deterministic and Replay-Safe Film Arrays

The cumulative actor-generation logic was hardened to rebuild each actor's
film array rather than blindly concatenating historical and incoming arrays.

### Film Identity Policy

`filmid` is treated as the logical film identity within an actor's cumulative
history.

The hardened behavior is:

1. retain at most one `film_struct` per `(actorid, filmid)`
2. prefer incoming-year data over historical state on a collision
3. if historical state contains repeated `filmid` values, retain the most
   recently appended historical occurrence
4. rebuild the final cumulative array ordered globally by `filmid`

### Dataset Observation

The production course dataset contains no natural collision between a film
already present in the 2020 cumulative actor state and a 2021 `actor_films`
record for the same actor and `filmid`.

Validation result:

- natural 2020-history / 2021-source collisions: 0

Therefore collision behavior was validated with controlled regression tests.

### Historical Replay Test

A duplicate historical film was deliberately appended to a 2020 actor array
using the same `filmid` but altered attributes.

After regenerating the 2021 snapshot:

- resulting occurrences of that `filmid`: 1
- retained representation: the most recently appended historical occurrence

The original 2020 and 2021 actor snapshots were restored after the test.

### Incoming-Wins Test

A synthetic deterministic test supplied both historical and incoming
representations for the same `(actorid, filmid)`.

Result:

- incoming representation selected: true

This validates the explicit source-priority rule without weakening or
modifying source-table constraints.

### Global Validation

After restoration and regeneration:

- duplicate `(actorid, current_year, filmid)` occurrences: 0
- global film-array ordering violations: 0
- actor-year snapshot count remains unchanged
- distinct actor count remains unchanged
- graded submission remains untouched

## Phase 4 — Explicit Null-Rating Policy

The cumulative actor-generation logic now defines explicit behavior for
incoming actor-year groups whose film ratings provide no usable quality signal.

### Dataset Profile

The current course dataset contains:

- 169,770 `actor_films` rows
- 0 rows with `rating IS NULL`
- 105,026 actor-year groups
- 0 actor-year groups with all ratings NULL
- 0 actor-year groups with a NULL `AVG(rating)`

Therefore this change is defensive hardening rather than a correction to
existing source data.

### Quality-Class Policy

The graded threshold semantics are intentionally preserved:

- `avg_rating > 8` -> `star`
- `avg_rating > 7` -> `good`
- `avg_rating > 6` -> `average`
- `avg_rating <= 6` -> `bad`

Boundary profiling confirmed that changing these operators to inclusive
thresholds would materially alter results:

- exactly 8.0: 376 actor-year groups
- exactly 7.0: 1,975 actor-year groups
- exactly 6.0: 2,951 actor-year groups

For an existing actor with incoming films but no usable rating evidence, the
hardened implementation retains the previous `quality_class` rather than
implicitly classifying the actor as `bad`.

### Regression Validation

The hardened 2021 snapshot was regenerated after implementing the policy.

Bidirectional `EXCEPT` comparison against the pre-change Phase 4 baseline:

- hardened-only rows: 0
- baseline-only rows: 0

The real dataset therefore remains behaviorally identical.

### Synthetic Policy Validation

Synthetic test results:

- `8.1` -> `star`
- `8.0` -> `good`
- `7.0` -> `average`
- `6.0` -> `bad`
- existing actor with NULL average rating -> previous `quality_class`

This confirms both the defensive NULL-rating behavior and preservation of the
strict A-grade threshold rules.
