# DataExpert Boot Camp — Fact Data Modeling Week 2

## Assignment

Build cumulative and reduced fact models using the DataExpert `events`,
`devices`, and `game_details` datasets.

## Source Data Findings

### Events

- Rows: 16,830
- Distinct users: 1,431
- Distinct devices: 348
- Distinct hosts: 3
- Date range: 2023-01-01 through 2023-01-31
- 2023-01-20 contains no source events

### Devices

- Rows: 7,774
- Distinct device IDs: 3,887
- Browser types in source: 199
- Device IDs are duplicated in the source
- No conflicting descriptions were found among duplicate device IDs
- Raw events/devices join rows: 33,324
- Deduplicated events/devices join rows: 16,662

The device dimension is therefore deduplicated before joining to events.

### game_details

- Original rows: 246,043
- Deduplicated rows: 245,754
- Duplicate rows removed: 289
- Deduplication grain: `(game_id, team_id, player_id)`

## Deliverables

- `submission/query_1.sql` — Deduplicate `game_details`
- `submission/query_2.sql` — `user_devices_cumulated` DDL
- `submission/query_3.sql` — Device activity cumulative query
- `submission/query_4.sql` — `datelist_int` generation
- `submission/query_5.sql` — `hosts_cumulated` DDL
- `submission/query_6.sql` — Host activity cumulative query
- `submission/query_7.sql` — `host_activity_reduced` DDL
- `submission/query_8.sql` — Day-by-day reduced fact load

## Validation Results

### User / Device Cumulative Model

- Coverage: 2023-01-01 through 2023-01-31
- Total snapshots: 25,603
- Distinct users represented: 1,427
- Browser types represented in event activity: 54
- January 20 user/browser carry-forward mismatches: 0
- January 20 host carry-forward mismatches: 0

### datelist_int

- `BIT_COUNT(datelist_int)` vs cumulative active-date cardinality mismatches: 0

### Host Reduced Fact

All three hosts contain:

- 31 hit-array positions
- 31 unique-visitor-array positions
- January 20 hits = 0
- January 20 unique visitors = 0

Monthly hit reconciliation:

- `admin.zachwilson.tech`: 1,496 source / 1,496 reduced
- `www.eczachly.com`: 2,874 source / 2,874 reduced
- `www.zachwilson.tech`: 12,460 source / 12,460 reduced

All monthly differences: 0.

The final daily hit and unique-visitor reconciliation compares all three hosts
across all 31 calendar days.

## Environment

- PostgreSQL 14
- Docker / Docker Compose
- Official DataExpert `data-engineer-handbook` course dataset
