# Week 2 — Grade Feedback and Remediation

## Student

**Name:** Ceasar Jackson
**Discord Username:** knucknuclear

## Original Grade

**B**

## Original Baseline

The original graded submission is preserved by Git tag:

`week02-graded-a`

The original eight submitted SQL files remain unchanged under:

`fact_data_modeling/week02_devices_events/submission/`

## Confirmed Functional Issue

The grader identified a functional issue in Query 4.

The original implementation:

- used `generate_series(...) AS valid_date`, which aliases the relation but
  does not explicitly name the generated column
- returned `BIT(32)` even though the assignment requested a base-2 integer
  representation

The remediation corrects both issues.

### Query 4 Corrections

The remediated Query 4 now:

- uses `AS gs(valid_date)` to explicitly name the generated date column
- uses `gs.valid_date` consistently
- returns a `BIGINT`
- uses a BIGINT bit-shift expression
- centralizes the snapshot date in a parameters CTE

## Source Table Naming Review

The grader suggested that the assignment might expect table names such as
`nba_game_details` and `web_events`.

Repository evidence shows that the actual DataExpert Boot Camp Week 2
materials use:

- `game_details`
- `events`
- `devices`

Evidence includes:

- `intermediate-bootcamp/materials/2-fact-data-modeling/tables/game_details.sql`
- `intermediate-bootcamp/materials/2-fact-data-modeling/tables/events.sql`
- `intermediate-bootcamp/materials/2-fact-data-modeling/tables/devices.sql`
- the Week 2 homework instructions explicitly reference `devices`, `events`,
  and `game_details`

Therefore, the remediation intentionally retains the original source-table
names rather than renaming them to unsupported alternatives.

## Remaining Grader Suggestions

The following are robustness or production-hardening opportunities rather
than confirmed assignment failures:

- deterministic tie-breaking in Query 1
- idempotent rerun handling with `ON CONFLICT`
- parameterized snapshot dates
- clearer `snapshot_date` naming
- additional constraints where useful

These may be included as post-grade hardening without modifying the original
graded submission.

## Remediation Status

- original B-grade submission preserved
- Query 4 generate_series alias corrected
- Query 4 integer representation corrected to BIGINT
- bootcamp source-table naming verified against upstream materials
