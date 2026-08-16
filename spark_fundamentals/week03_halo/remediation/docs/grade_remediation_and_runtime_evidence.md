# Week 3 Spark Fundamentals — Grade Remediation and Runtime Evidence

## Student

**Name:** Ceasar Jackson  
**Discord Username:** knucknuclear

## Original Grade

**B / 80%**

## Historical Baseline

The original graded Week 3 submission is preserved under:

`week03-graded-a`

The original submitted ZIP remains byte-for-byte unchanged.

Original ZIP SHA-256:

`719984774276fc2da7291a4841ea6009608bf685414eddda79de1c0d3b124c79`

## Primary Grader Findings

The original submission was strong in:

- automatic broadcast disablement
- explicit broadcast joins
- 16-bucket Hive table creation
- analytical aggregations
- use of `sortWithinPartitions`
- code organization and documentation

The two material remediation requirements were:

1. prove that all three large bucketed tables participate in bucket-aligned
   joins on `match_id`
2. perform genuine physical partitioning experiments using
   `repartition` / `partitionBy` plus `sortWithinPartitions`

## Requirement 3 — Bucket-Aware Join Remediation

The hardened implementation joins:

- `hw_match_details_bucketed`
- `hw_matches_bucketed`
- `hw_medals_matches_players_bucketed`

on the shared bucket key:

`match_id`

Player-level matching for `medals_matches_players` is applied after the
bucket-key join so the bucket-aligned join opportunity is preserved.

### Runtime Physical-Plan Evidence

The persisted formatted Spark physical plan confirms:

- `hw_match_details_bucketed`
  - `Bucketed: true`
  - `SelectedBucketsCount: 16 out of 16`
- `hw_matches_bucketed`
  - `Bucketed: true`
  - `SelectedBucketsCount: 16 out of 16`
- `hw_medals_matches_players_bucketed`
  - `Bucketed: true`
  - `SelectedBucketsCount: 16 out of 16`

The two large-data joins appear as `SortMergeJoin` operations on `match_id`.

There are no shuffle `Exchange` operators between those three bucketed
scans and their large-table joins.

The only exchanges in the captured plan are intentional
`BroadcastExchange` operations for the small `medals` and `maps`
dimensions.

This provides runtime evidence that Spark recognizes and uses the compatible
bucket metadata.

Evidence:

`evidence/joined_physical_plan_formatted.txt`

## Requirement 5 — Physical Partitioning Experiments

The hardened implementation performs four controlled storage experiments:

1. non-partitioned coalesced baseline
2. partition by `playlist_id`, sorted within partitions by
   `playlist_id, map_name`
3. partition by `map_name`, sorted within partitions by
   `map_name, playlist_id`
4. partition by `playlist_id, map_name`, sorted within partitions by
   `playlist_id, map_name`

Runtime filesystem inspection confirmed actual physical partition
directories including:

- `playlist_id=playlist1`
- `playlist_id=playlist2`
- `map_name=Blood Gulch`
- `map_name=Lockout`
- combined `playlist_id=.../map_name=...` directories

### Runtime Size Measurements

| Experiment | Size Bytes |
|---|---:|
| baseline_coalesced | 1503 |
| partition_playlist_sorted_playlist_map | 2189 |
| partition_map_sorted_map_playlist | 2220 |
| partition_playlist_map_sorted_playlist_map | 2342 |

The smoke-test dataset is intentionally small, so the coalesced baseline is
the smallest output. The assignment requirement is to implement and compare
multiple genuine physical partitioning strategies; it does not require a
partitioned variant to be smallest for every dataset.

Evidence:

- `evidence/partition_sort_size_results.csv`
- `evidence/partition_sort_size_results.json`

## Broadcast Evidence

The runtime physical plan also confirms explicit broadcast behavior for the
small dimensions through:

- `BroadcastExchange`
- `BroadcastHashJoin`

for `medals` and `maps`.

Automatic broadcast remains disabled through:

`spark.sql.autoBroadcastJoinThreshold = -1`

## Analytical Results from Runtime Test

The remediation runtime completed successfully and produced all required
analytical outputs:

- highest average kills per game
- most-played playlist
- most-played map
- map with most Killing Spree medals

The smoke-test results included:

- highest average kills: `PlayerA` — `15.0`
- most-played playlist: `playlist1` — `2` matches
- most-played map: `Blood Gulch` — `2` matches
- most Killing Spree medals: `Blood Gulch` — `4`

## Environment

Validated with:

- Python 3.12.13
- PySpark 4.1.1
- Conda environment: `dataeng`

## Validation Status

The hardened script:

- compiles successfully
- imports and executes successfully with PySpark 4.1.1
- passes the original Week 3 static assignment validator
- preserves the original graded ZIP
- generates persisted physical-plan evidence
- generates genuine partitioned-table experiments
- produces runtime measurement evidence

## Remediation Status

The substantive Week 3 grader deductions have now been remediated.

The original graded submission remains immutable while the corrected
implementation and evidence are maintained separately.
