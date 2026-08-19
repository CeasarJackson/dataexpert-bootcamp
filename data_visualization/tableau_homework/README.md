# DataExpert Boot Camp — Data Visualization / Tableau Homework

## Author

Ceasar Jackson

## Overview

This workspace contains the DataExpert Boot Camp data-visualization homework
implemented with Tableau.

The assignment requires two Tableau Public dashboards with different
analytical purposes:

1. An executive dashboard for concise performance and engagement monitoring.
2. An exploratory dashboard with interactive filters for deeper player and
   medal analysis.

The dashboard design is grounded in the validated Halo multiplayer datasets
prepared in this workspace.

## Assignment Deliverables

The planned Tableau deliverables are:

- **Halo Multiplayer Performance: Executive Overview**
- **Halo Player & Medal Explorer**

The detailed worksheet, filter, dashboard-action, layout, and formatting
specification is maintained in:

`docs/TABLEAU_DASHBOARD_BLUEPRINT.md`

## Source Data

Validated source row counts:

| Source | Rows |
| --- | ---: |
| Match details | 151,761 |
| Matches | 24,025 |
| Medal definitions | 183 |
| Player-medal facts | 755,229 |

Validated cardinalities include:

- 19,050 matches with player-detail data
- 69,420 unique players
- 25 maps
- 27 playlists
- 12 game variants
- 8 teams
- 130 distinct medal names in the prepared analytical data

The validated source date range is:

`2015-10-27` through `2016-09-28`

## Analytical Grain

The validated analytical grains are:

### Player Match

`match_id + player_gamertag`

### Player Medal

`match_id + player_gamertag + medal_id`

Validation found no duplicate rows at either expected grain.

## Prepared Tableau Data

### Compact Executive / Git-Eligible Data

These datasets are retained as compact repository artifacts:

- `data/prepared/executive_kpis.csv`
- `data/prepared/executive_daily_performance.csv`
- `data/prepared/executive_player_performance.csv`
- `data/prepared/exploratory_medal_summary.csv`

### Large Local Analytical Data

The following prepared datasets remain available locally for Tableau analysis
but are intentionally excluded from ordinary Git history:

- `data/prepared/tableau_player_match_performance.csv`
- `data/prepared/tableau_player_medal_performance.csv`
- `data/prepared/exploratory_daily_player_medals.csv`

They remain part of the analytical workflow even though Git does not track
their generated CSV contents.

Checksum evidence for prepared datasets is retained under
`validation/results/`.

## Executive Dashboard

### Halo Multiplayer Performance: Executive Overview

Audience:

Executives and decision-makers who need a concise view of player activity,
performance, and engagement.

### Validated KPI Values

| KPI | Value |
| --- | ---: |
| Matches with Player Data | 19,050 |
| Unique Players | 69,420 |
| Total Kills | 1,350,442 |
| Overall K/D | 0.9869 |
| Player Appearance Win Rate | 47.97% |
| Medals Awarded | 1,560,446 |

`Player Appearance Win Rate` is the percentage of player-match appearances
marked as a win. It is not the percentage of distinct matches won.

### Executive Worksheets

The executive dashboard specification contains:

1. **Matches Over Time**
   - source: `executive_daily_performance.csv`
   - line chart of daily match volume

2. **Combat Performance Trend**
   - source: `executive_daily_performance.csv`
   - line chart of daily kill/death ratio
   - reference line at `1.0`

3. **Top Established Players**
   - source: `executive_player_performance.csv`
   - filter: `established_player_flag = 1`
   - top 15 by kills
   - supporting tooltip values include matches played, K/D, and win rate

4. **Top Medal Distribution**
   - source: `exploratory_medal_summary.csv`
   - top 10 or 15 medals by medal count

### Executive Dashboard Layout

Recommended fixed size:

`1400 x 900`

Recommended structure:

- header/title
- six KPI cards
- matches-over-time view
- combat-performance trend
- top established players
- top medal distribution
- dataset scope/date-range footer

## Exploratory Dashboard

### Halo Player & Medal Explorer

Audience:

Analysts and users who want to investigate medal behavior by player, date,
difficulty, classification, and team-game status.

Primary local analytical source:

`data/prepared/exploratory_daily_player_medals.csv`

### Exploratory Filters

Expose:

- completion date
- player gamertag
- medal name
- medal classification
- medal difficulty
- team-game status

Filters should apply to all relevant exploratory worksheets.

### Exploratory Worksheets

The exploratory dashboard specification contains:

1. **Medal Volume Over Time**
2. **Medal Ranking**
3. **Medal Classification Mix**
4. **Medal Difficulty Mix**
5. **Player Medal Leaderboard**
6. **Player / Medal Detail**

Selections of medals, classifications, difficulties, and players should filter
related exploratory views.

### Exploratory Dashboard Layout

Recommended fixed size:

`1400 x 900`

Recommended structure:

- header
- filter strip
- medal trend
- medal ranking
- classification and difficulty views
- player leaderboard
- detail area

## Formatting Standards

### Counts

Use thousands separators.

Examples:

- `1,350,442`
- `69,420`

### Ratios

Display K/D ratios to approximately two decimal places.

Example:

`0.99`

### Rates

Display win rates as percentages.

Example:

`47.97%`

### Dates

Display readable calendar dates.

### Titles

Use human-readable business labels rather than raw CSV field names.

## Data Quality Validation

Validation confirmed:

- no duplicate `match_id` values in the match dimension
- no duplicate player-match rows
- no duplicate player-medal rows
- no duplicate medal IDs in the medal dimension
- all match-detail match IDs resolve to the match source
- all player-medal match IDs resolve to the match source
- all player-medal medal IDs resolve to the medal dimension

Medal metadata coverage:

- 181 of 183 medals have names
- 181 of 183 medals have classifications
- 181 of 183 medals have difficulty metadata

## Validation Evidence

Validation artifacts are maintained in:

`validation/results/`

Important files include:

- `source_profile.csv`
- `source_profile.txt`
- `tableau_dataset_summary.json`
- `tableau_dataset_summary.txt`
- `tableau_dashboard_dataset_summary.json`
- `tableau_prepared_sha256.txt`
- `tableau_dashboard_sha256.txt`

The checksum files provide provenance for both compact repository datasets
and large locally retained analytical datasets.

## Git / Data Footprint Policy

The Tableau workspace intentionally separates:

- compact documentation and dashboard-support datasets suitable for Git
- large generated analytical datasets retained locally for Tableau work

The workspace `.gitignore` excludes:

- the large prepared analytical CSV files
- Tableau transient artifacts
- Python cache files
- local validation logs

This avoids unnecessarily large repository history while preserving local
analytical reproducibility.

## Repository Structure

```text
tableau_homework/
├── .gitignore
├── README.md
├── data/
│   ├── prepared/
│   └── source/
├── docs/
│   └── TABLEAU_DASHBOARD_BLUEPRINT.md
├── scripts/
├── sql/
├── submission/
├── tableau/
└── validation/
    ├── logs/
    └── results/
```

## Current Status

Completed:

- source profiling
- grain validation
- join-coverage validation
- prepared analytical datasets
- compact executive datasets
- checksum evidence
- dashboard blueprint
- Git/data-footprint policy
- repository documentation

Remaining:

- build Tableau worksheets
- assemble executive dashboard
- assemble exploratory dashboard
- configure filters and dashboard actions
- perform visual QA
- publish/package final Tableau deliverables
- create final submission artifacts

## Security

No secrets, credentials, or environment configuration files are required for
the prepared Tableau datasets in this workspace.

## Author

Ceasar Jackson
