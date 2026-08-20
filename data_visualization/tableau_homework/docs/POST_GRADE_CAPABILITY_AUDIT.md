# Week 7 — Post-Grade Capability Audit

**Course:** DataExpert Boot Camp
**Assignment:** Week 7 — Data Visualization / Tableau
**Author:** Ceasar Jackson
**Graded baseline:** `week07-graded-b`
**Improvement branch:** `improve/week07-post-grade-hardening`

## Purpose

This audit determines which grader-recommended Tableau improvements are
supported by the available source data before modifying the graded workbook.

The graded baseline remains preserved at `week07-graded-b`.

## Detailed Data Sources

### Player / Match Performance

`data/prepared/tableau_player_match_performance.csv`

- Rows: 151,761
- Distinct matches: 19,050
- Distinct maps: 16
- Distinct playlists: 23
- Distinct game variants: 9
- Date range: 2015-10-27 through 2016-09-28
- Missing KDA values: 1,735

Important available measures and dimensions include:

- player gamertag
- completion date
- map ID
- playlist ID
- game variant ID
- team-game indicator
- win flag
- kills
- deaths
- assists
- headshots
- shots landed
- K/D
- KDA
- XP
- CSR information

### Player / Medal Performance

`data/prepared/tableau_player_medal_performance.csv`

- Rows: 755,229
- Distinct matches represented: 18,942
- Match-level source join coverage: 100%

Important available fields include:

- match ID
- player gamertag
- completion date
- map ID
- playlist ID
- game variant ID
- team-game indicator
- medal ID
- medal name
- medal classification
- medal difficulty
- medal description
- medal count

## Match Source Relationship

Upstream source:

`upstream/data-engineer-handbook/intermediate-bootcamp/materials/3-spark-fundamentals/data/matches.csv`

Audit results:

- Rows: 24,025
- Distinct match IDs: 24,025
- Duplicate match IDs: 0
- Player-detail match coverage: 100%
- Medal-detail match coverage: 100%

The source therefore provides a validated one-row-per-match relationship for
the match IDs represented in both detailed Tableau datasets.

## Match Duration Finding

The upstream match source contains a `match_duration` column, but:

- Missing duration rows: 24,025
- Parsed duration values: 0

Therefore match duration is structurally present but contains no usable values.

Metrics requiring actual elapsed match duration must not be created from this
source.

In particular, **Medals per 10 Minutes is not currently supportable**.

## Map Lookup

Upstream lookup:

`upstream/data-engineer-handbook/intermediate-bootcamp/materials/3-spark-fundamentals/data/maps.csv`

The lookup contains:

- `mapid`
- `name`
- `description`

Audit results for the player-detail dataset:

- Distinct detail map IDs: 16
- Map IDs with lookup rows: 16
- Missing lookup rows: 0
- Lookup-row coverage: 100%
- Source-provided human-readable names: 14
- Blank source map names: 2

Therefore Map is supported as a dashboard dimension, with an important
metadata limitation: two analytical map IDs have valid lookup rows but blank
source-provided names.

Post-grade aggregates preserve those maps and use deterministic, explicitly
non-authoritative display labels derived from the first eight characters of
the map ID:

- `Unnamed Map (cc74f4e1)`
- `Unnamed Map (ce89a40f)`

This prevents the 629 affected matches from being dropped or combined while
avoiding invention of unsupported map names.

## Playlist Metadata

The detailed datasets contain valid `playlist_id` values.

No repository playlist-name lookup was identified during the audit.

Therefore Playlist is analytically available by ID but is not currently
approved as a polished user-facing categorical filter.

UUID values should not be exposed as primary dashboard labels.

## Capability Matrix

| Capability | Verdict | Evidence / Constraint |
|---|---|---|
| K/D | Supported | `kill_death_ratio` |
| KDA | Supported | `kill_assist_death_ratio` |
| Win Rate | Supported | `did_win`, `win_flag` |
| Player filter | Supported | `player_gamertag` |
| Date/timeframe filter | Supported | `completion_date` |
| Map filter | Supported with fallback labels | 100% lookup-row coverage; 14/16 analytical maps have source-provided names; 2 retain deterministic unnamed-map labels |
| Playlist segmentation | ID only | No playlist-name lookup found |
| Game variant segmentation | ID only | No human-readable lookup verified |
| Team-game segmentation | Supported | `is_team_game` |
| Accuracy | Unsupported | Shots landed exists; attempts/fired unavailable |
| Medals per match | Derivable | Medal counts and match IDs available |
| Medals per 10 minutes | Unsupported | `match_duration` is entirely null |
| Region | Unsupported | No region field identified |
| Date range | Supported | Completion dates and KPI start/end dates |
| Prior-period deltas | Derivable | Daily performance series available |
| Distribution analysis | Supported | Detailed player/match and medal grains |
| Medal descriptions | Supported | `medal_description` |
| Map descriptions | Supported | `maps.csv` description field |

## Approved Post-Grade Scope

The following capabilities are approved for post-grade implementation:

1. Improve executive KPI hierarchy.
2. Surface the source date range.
3. Add prior-period context where calculations are valid.
4. Add a concise executive summary.
5. Add KDA as an explicitly documented analytical metric.
6. Add Map segmentation using authoritative names where available and deterministic fallback labels for blank source names.
7. Add Player filtering where appropriate.
8. Add Date/Timeframe filtering.
9. Add Team Game segmentation where analytically useful.
10. Add normalized Medals per Match measures.
11. Add medal distributions using purpose-built aggregates.
12. Improve descriptive tooltips using medal descriptions and KPI definitions.
13. Add dashboard actions where they improve exploration.
14. Improve accessibility, typography, color, and redundant encoding.
15. Add reviewer-readable PDF/screenshots to the submission package.

## Explicitly Deferred / Unsupported

The following features must not be claimed without additional source evidence:

- Accuracy
- Medals per 10 minutes
- Region
- human-readable Playlist names
- human-readable Game Variant names
- average match length

## Performance Guardrail

The detailed medal dataset contains 755,229 rows.

The post-grade workbook should not expose this grain directly merely to add
detail. Purpose-built aggregates should be generated for dashboard
visualizations wherever practical.

This reduces workbook complexity, mark counts, and rendering cost while
preserving the analytical measures required by the dashboard.

## Baseline Preservation

All post-grade work is isolated to:

`improve/week07-post-grade-hardening`

The exact graded submission remains preserved at:

`week07-graded-b`
