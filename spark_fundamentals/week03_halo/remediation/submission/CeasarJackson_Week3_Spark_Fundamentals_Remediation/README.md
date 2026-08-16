# DataExpert Week 3 — Spark Fundamentals Final Remediation

## Student

**Name:** Ceasar Jackson  
**Discord Username:** knucknuclear

## Purpose

This package contains the final remediation for the Week 3 Spark Fundamentals
assignment.

The original graded submission is preserved separately under:

`week03-graded-a`

The original submitted ZIP has not been modified.

## Remediated Requirements

### Bucket-aware joins

The three large datasets are persisted as 16-bucket Spark catalog tables using
`match_id` as the bucket key:

- `match_details`
- `matches`
- `medals_matches_players`

The hardened join strategy aligns the large-table joins on `match_id`.

Runtime physical-plan evidence confirms:

- all three scans report `Bucketed: true`
- all three scans report `SelectedBucketsCount: 16 out of 16`
- the large-table joins execute as `SortMergeJoin`
- there is no hash-partition shuffle exchange between those bucketed joins
- explicit broadcast exchanges are used for the small lookup dimensions

See:

`evidence/joined_physical_plan_formatted.txt`

### Physical partition experiments

The final implementation performs four controlled output-layout experiments:

1. coalesced non-partitioned baseline
2. partition by `playlist_id`
3. partition by `map_name`
4. partition by `playlist_id, map_name`

The partitioned variants also use `repartition()` and
`sortWithinPartitions()`.

Runtime output confirmed actual physical partition directories.

Measured smoke-test sizes:

| Experiment | Bytes |
|---|---:|
| baseline_coalesced | 1503 |
| partition_playlist_sorted_playlist_map | 2189 |
| partition_map_sorted_map_playlist | 2220 |
| partition_playlist_map_sorted_playlist_map | 2342 |

See:

- `evidence/partition_sort_size_results.csv`
- `evidence/partition_sort_size_results.json`

## Other Assignment Requirements

The implementation also covers:

- disabling automatic broadcast joins
- explicit broadcasting of small dimensions
- player average kills per game
- most-played playlist
- most-played map
- Killing Spree medal totals by map

## Validation

Validated using:

- Python 3.12.13
- PySpark 4.1.1
- Conda environment `dataeng`

Final remediation validator result:

`23 PASS / 0 FAIL`

The hardened implementation also passes the original Week 3 static assignment
validator.

## Historical Preservation

Original graded ZIP SHA-256:

`719984774276fc2da7291a4841ea6009608bf685414eddda79de1c0d3b124c79`
