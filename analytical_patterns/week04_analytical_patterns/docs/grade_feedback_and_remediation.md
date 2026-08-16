# Week 4 — Grade Feedback and Remediation

## Student

**Name:** Ceasar Jackson
**Discord Username:** knucknuclear

## Original Grade

**B**

## Original Submission Baseline

The original graded submission is preserved by Git tag `week04-graded-a`.

The original homework files remain under:

`homework/knucknuclear/`

## Remediated Baseline

The corrected seven-output version is preserved by Git tag
`week04-remediated-a`.

## Grader Assessment

The grader identified the underlying analytical work as largely correct.

### Strengths

- Player state-change tracking correctly implemented:
  - New
  - Retired
  - Continued Playing
  - Returned from Retirement
  - Stayed Retired
- `GROUPING SETS` correctly used for:
  - player + team
  - player + season
  - team
- Distinct winning-game counting avoided fact-grain duplication.
- The 90-game rolling window correctly uses 89 preceding rows plus the current row.
- Complete 90-game windows are enforced.
- The LeBron James scoring streak uses a gaps-and-islands pattern.
- SQL is clear and well commented.

## Primary Grade Deduction

The original submission did not provide three required outputs as explicit
queries.

The original `GROUPING SETS` query produced the data required to answer them,
but the assignment required discrete answers.

The missing outputs were:

1. Query 3 — player with the most points for one team
2. Query 4 — player with the most points in one season
3. Query 5 — team with the most total wins

The grader therefore treated the original submission as providing only four
of seven explicit required outputs.

## Remediation

Three standalone SQL queries were added:

- `query_3_most_points_single_team.sql`
- `query_4_most_points_single_season.sql`
- `query_5_team_most_wins.sql`

The complete remediation package contains:

1. `query_1_player_state_change_tracking.sql`
2. `query_2_grouping_sets_game_details.sql`
3. `query_3_most_points_single_team.sql`
4. `query_4_most_points_single_season.sql`
5. `query_5_team_most_wins.sql`
6. `query_6_most_wins_90_game_stretch.sql`
7. `query_7_lebron_over_10_streak.sql`

## Query 3 Correction

The explicit answer filters the aggregate result to the `player_team`
aggregation level and orders by `total_points DESC NULLS LAST`.

## Query 4 Correction

The explicit answer filters the aggregate result to the `player_season`
aggregation level and orders by `total_points DESC NULLS LAST`.

## Query 5 Correction

The explicit answer filters the aggregate result to the `team` aggregation
level and correctly orders by `team_wins DESC NULLS LAST`.

This is important because ranking by total points would not answer the
question asking which team won the most games.

## Validation

The remediation validator checks:

- preservation of the original B-grade submission
- presence of the original required SQL
- presence of Queries 3–5
- correct Query 3 aggregation filter and ordering
- correct Query 4 aggregation filter and ordering
- correct Query 5 aggregation filter and win ordering
- correct 90-game window semantics
- correct full-window filtering
- correct LeBron streak grouping logic
- Git whitespace integrity

Validated remediation result:

`PASS=18`
`FAIL=0`

The remediation ZIP was also verified to contain exactly seven SQL query
files.

## Historical Preservation

The repository deliberately maintains two distinct states.

### Original Graded State

Git tag: `week04-graded-a`

This represents the exact submission that received the B.

### Corrected State

Git tag: `week04-remediated-a`

This represents the completed seven-output remediation.

The original graded tag was not moved or rewritten.

## Key Engineering Lesson

A technically correct shared computation does not automatically satisfy a
requirement for multiple explicit deliverables.

When requirements enumerate outputs individually, the implementation should
make each output explicit even when several answers originate from the same
intermediate dataset.

For future assignments:

1. Convert every numbered requirement into a checklist.
2. Map each requirement to an explicit output artifact.
3. Validate artifact count before submission.
4. Validate semantic correctness separately from completeness.
5. Preserve the submitted baseline before performing post-grade changes.

## Optional Optimization Opportunities

The grader identified two optional improvements that were not required for
correctness.

### Query 6

Instead of deriving team games through `game_details` and `DISTINCT`, team
game rows could be generated directly from `games`.

### Query 7

If the dataset contains DNP rows, participation could be explicitly filtered
before calculating the scoring streak after confirming the dataset's
participation semantics.

## Final Status

The original B-grade submission is preserved.

The corrected remediation:

- provides seven explicit SQL outputs
- passes 18 remediation validation checks
- has a validated seven-query package
- is merged into `main`
- is preserved under `week04-remediated-a`
