# Week 4 — Analytical Patterns

## Student

**Name:** Ceasar Jackson
**Discord Username:** knucknuclear

## Purpose

This directory contains post-submission learning, validation, documentation,
and portfolio hardening for DataExpert Boot Camp Week 4 Analytical Patterns.

The original graded submission is preserved under `homework/knucknuclear/`.
The protected Git baseline is `week04-graded-a`.

## Topics

Week 4 focuses on three analytical SQL patterns:

1. Player state-change tracking
2. `GROUPING SETS`
3. Window functions and streak analysis

## Graded Submission

The graded source contains:

- `01_player_state_change_tracking.sql`
- `02_grouping_sets_game_details.sql`
- `03_window_functions_game_details.sql`
- `README.md`

The homework upload artifact is:

- `CeasarJackson_Week4_Analytical_Patterns.zip`

A canonical copy of the validated ZIP is retained under the post-grade
`submission/` directory.

## Post-Grade Workspace

- `docs/` — explanatory and portfolio documentation
- `notes/` — learning and interview notes
- `reference/` — reference material
- `scripts/` — deterministic build and validation utilities
- `sql/` — reference copies for post-grade experimentation
- `submission/` — canonical validated ZIP artifact
- `validation/logs/` — validation logs
- `validation/results/` — reproducible validation results

## State Change Tracking

Required states:

- New
- Retired
- Continued Playing
- Returned from Retirement
- Stayed Retired

Important concepts include season-over-season comparison, prior-state
detection, historical existence checks, complete entity/time grids, and
temporal classification.

## GROUPING SETS

Required aggregation grains:

- player + team
- player + season
- team

Important concepts include `GROUPING SETS`, `GROUPING()`, aggregation grain,
distinct game counting, and avoiding duplicated fact counts.

## Window Functions

Required analyses:

- maximum wins by a team across a complete 90-game stretch
- longest LeBron James streak scoring more than 10 points per game

Important concepts include `ROWS BETWEEN`, `ROW_NUMBER()`, rolling
aggregates, gaps-and-islands, and cumulative streak identifiers.

## Baseline Preservation

Post-grade work must never alter the original Week 4 submission.

Validate preservation with:

    git diff --quiet week04-graded-a -- homework/knucknuclear \
      && echo "PASS: graded Week 4 submission unchanged" \
      || echo "FAIL: graded Week 4 submission changed"

## Validation

Run the complete Week 4 validation suite with:

    ./analytical_patterns/week04_analytical_patterns/scripts/validate_week04.sh

The validation suite checks:

- baseline tag availability
- required graded files
- graded-submission preservation
- reference SQL availability
- ZIP existence and integrity
- SHA-256 equality between working and canonical ZIPs
- Git whitespace integrity

## Submission ZIP

Validate the upload archive with:

    unzip -t CeasarJackson_Week4_Analytical_Patterns.zip

The repository-wide `.gitignore` intentionally excludes generated Week ZIPs.
The canonical Week 4 ZIP under `submission/` is explicitly force-tracked.
