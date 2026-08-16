# Week 2 — Fact Data Modeling Grade Remediation

## Student

**Name:** Ceasar Jackson
**Discord Username:** knucknuclear

## Original Grade

**B**

## Purpose

This package contains the corrected Week 2 Fact Data Modeling submission.

The original graded submission is preserved unchanged at Git tag:

`week02-graded-a`

## Contents

1. `query_1.sql` — deduplicate `game_details`
2. `query_2.sql` — `user_devices_cumulated` DDL
3. `query_3.sql` — incremental user/device activity population
4. `query_4.sql` — 32-day device activity base-2 integer representation
5. `query_5.sql` — `hosts_cumulated` DDL
6. `query_6.sql` — incremental host activity population
7. `query_7.sql` — `host_activity_reduced` DDL
8. `query_8.sql` — incremental host monthly array metrics

## Primary Remediation

Query 4 was corrected to:

- explicitly alias the `generate_series()` output column
- return the required integer representation as `BIGINT`
- use BIGINT bit shifting
- centralize the snapshot date in a parameters CTE

## Source Table Naming Verification

The grader raised a possible naming mismatch involving `nba_game_details`
and `web_events`.

The upstream DataExpert Week 2 materials were inspected directly and confirm
that the assignment uses:

- `game_details`
- `events`
- `devices`

Therefore those source-table names are intentionally retained.

## Validation

The Week 2 remediation validator currently passes:

- 13 checks
- 0 failures

Run:

    ./fact_data_modeling/week02_devices_events/remediation/scripts/validate_week02_remediation.sh
