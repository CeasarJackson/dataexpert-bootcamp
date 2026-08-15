# DataExpert Boot Camp — Dimensional Data Modeling Week 1

## Assignment

Build a cumulative actor dimension and Type 2 Slowly Changing Dimension
from the `actor_films` dataset.

## Source Dataset

- Rows: 169,770
- Distinct actors: 9,447
- Distinct films: 35,894
- Year range: 1970–2021
- Source primary key: `(actorid, filmid)`

## Deliverables

- `submission/query_1.sql` — Actors table DDL
- `submission/query_2.sql` — Cumulative actors query
- `submission/query_3.sql` — Actors SCD Type 2 DDL
- `submission/query_4.sql` — Full SCD backfill
- `submission/query_5.sql` — Incremental SCD generation

## Validation Results

### Cumulative Actor Dimension

- 249,082 actor-year snapshots
- 9,447 distinct actors
- Coverage: 1970–2021
- Duplicate `(actorid, current_year)` rows: 0

### SCD Type 2

- 119,331 SCD rows
- 9,447 distinct actors
- Invalid date ranges: 0
- Overlapping SCD intervals: 0

### Incremental Equivalence

The 2021 incremental SCD result was compared with a complete 1970–2021
backfill using bidirectional `EXCEPT` queries.

Result:

- Incremental-only rows: 0
- Backfill-only rows: 0

Therefore the incremental algorithm produces the same 2021 dimensional
state as the full historical backfill.

## Environment

- PostgreSQL 14
- Docker / Docker Compose
- Official DataExpert `data-engineer-handbook` dataset and course materials
