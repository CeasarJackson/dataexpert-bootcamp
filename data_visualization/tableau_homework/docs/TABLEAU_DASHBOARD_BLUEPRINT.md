# DataExpert Data Visualization Homework
## Tableau Dashboard Blueprint

**Author:** Ceasar Jackson

## Assignment Deliverables

Create and publish two Tableau Public dashboards:

1. Executive dashboard
2. Exploratory dashboard with filters

The two dashboards must answer different analytical needs.

---

# Dashboard 1 — Halo Multiplayer Performance: Executive Overview

## Audience

Executives and decision-makers who need a concise view of player activity,
performance, and engagement.

## Primary KPI Cards

| KPI | Value | Tableau Source |
|---|---:|---|
| Matches with Player Data | 19,050 | `executive_kpis.csv` |
| Unique Players | 69,420 | `executive_kpis.csv` |
| Total Kills | 1,350,442 | `executive_kpis.csv` |
| Overall K/D | 0.9869 | `executive_kpis.csv` |
| Player Win Rate | 47.97% | `executive_kpis.csv` |
| Medals Awarded | 1,560,446 | `executive_kpis.csv` |

### Important Metric Definition

`Player Win Rate` is the percentage of player-match appearances marked as a
win. It is not the percentage of matches won.

## Executive Sheets

### EXEC 01 — Matches Over Time

Source: `executive_daily_performance.csv`

- Columns: `completion_date`
- Rows: `matches`
- Mark: Line
- Purpose: show activity trend over the available period.

### EXEC 02 — Combat Performance Trend

Source: `executive_daily_performance.csv`

- Columns: `completion_date`
- Rows: `kill_death_ratio`
- Mark: Line
- Reference line: 1.0
- Purpose: distinguish periods where aggregate kills exceeded deaths.

### EXEC 03 — Top Established Players

Source: `executive_player_performance.csv`

Filter:

`established_player_flag = 1`

Recommended ranking:

- Top 15 by `kills`
- Show `matches_played`, `kill_death_ratio`, and `win_rate` in tooltip.

Use horizontal bars.

### EXEC 04 — Top Medal Distribution

Source: `exploratory_medal_summary.csv`

- Dimension: `medal_name`
- Measure: `medal_count`
- Top 10 or Top 15
- Sort descending

## Executive Dashboard Layout

Recommended fixed desktop size:

`1400 x 900`

Structure:

- Header/title
- Six KPI cards
- Matches-over-time chart
- Combat-performance trend
- Top established players
- Top medal distribution
- Footer with dataset scope/date range

## Executive Design Principles

- Minimal filters.
- No dense detail table.
- Immediate KPI readability.
- Consistent number formatting.
- Tooltips provide context without clutter.
- Avoid misleading axis truncation where comparison depends on magnitude.

---

# Dashboard 2 — Halo Player & Medal Explorer

## Audience

Analysts and users who want to investigate medal behavior by player, date,
difficulty, classification, and team-game status.

## Primary Source

`exploratory_daily_player_medals.csv`

## Exploratory Filters

Expose these filters:

- `completion_date`
- `player_gamertag`
- `medal_name`
- `medal_classification`
- `medal_difficulty`
- `is_team_game`

All filters should apply to all relevant exploratory worksheets.

## Exploratory Sheets

### EXP 01 — Medal Volume Over Time

- Columns: `completion_date`
- Rows: `SUM(medal_count)`
- Mark: Line

### EXP 02 — Medal Ranking

- Rows: `medal_name`
- Columns: `SUM(medal_count)`
- Mark: Horizontal bar
- Sort descending

### EXP 03 — Medal Classification Mix

- Dimension: `medal_classification`
- Measure: `SUM(medal_count)`
- Mark: Bar

### EXP 04 — Medal Difficulty Mix

- Dimension: `medal_difficulty`
- Measure: `SUM(medal_count)`
- Mark: Bar

### EXP 05 — Player Medal Leaderboard

- Rows: `player_gamertag`
- Columns: `SUM(medal_count)`
- Top 20 under current filters

### EXP 06 — Player / Medal Detail

Recommended columns:

- player
- medal
- classification
- difficulty
- medal count

Use only as a supporting detail view.

## Dashboard Actions

Configure interactive filtering so that selecting:

- a medal,
- a classification,
- a difficulty,
- or a player

filters the other exploratory views.

## Exploratory Dashboard Layout

Recommended fixed desktop size:

`1400 x 900`

Structure:

- Header
- Filter strip
- Medal trend
- Medal ranking
- Classification and difficulty views
- Player leaderboard
- Detail area

---

# Formatting Standards

## Dates

Display as readable calendar dates.

## Counts

Use thousands separators.

Examples:

- `1,350,442`
- `69,420`

## Ratios

K/D:

`0.99`

## Rates

Player Win Rate:

`47.97%`

## Titles

Use human-readable labels instead of CSV column names.

Example:

`player_gamertag` -> `Player`

---

# Data Sources

## Executive

- `executive_kpis.csv`
- `executive_daily_performance.csv`
- `executive_player_performance.csv`
- `exploratory_medal_summary.csv`

## Exploratory

- `exploratory_daily_player_medals.csv`

---

# Publishing Names

Recommended Tableau Public workbook/dashboard names:

## Executive

`Halo Multiplayer Performance - Executive Overview`

## Exploratory

`Halo Player and Medal Explorer`

---

# Submission

The final grader-facing ZIP should contain a recognized text document with
the two Tableau Public URLs.

Recommended file:

`tableau_public_links.txt`

Required contents:

Executive Dashboard:
https://public.tableau.com/views/...

Exploratory Dashboard:
https://public.tableau.com/views/...

Do not submit placeholder URLs.

---

# Validation Requirements

Before submission verify:

- Both dashboards are publicly accessible without authentication.
- Executive and exploratory dashboards are visibly different.
- Exploratory dashboard contains functioning filters.
- Tableau Public URLs use the `/views/` path.
- KPI values reconcile with preparation outputs.
- Dashboard titles are professional and descriptive.
- No local filesystem paths or private information are visible.
