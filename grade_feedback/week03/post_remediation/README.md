# Week 3 — Spark Fundamentals Post-Remediation Status

## Student

**Name:** Ceasar Jackson  
**Discord Username:** knucknuclear

## Original Grade

**80% / B**

## Remediation Status

Technical remediation is complete.

The original grader identified two material gaps:

1. insufficient evidence that all three large bucketed datasets participated in
   bucket-aligned joins
2. insufficient physical `partitionBy` / `repartition` experimentation

Both have now been corrected and runtime-validated.

## Runtime Evidence

The final Spark physical plan confirms:

- three `Bucketed: true` scans
- `SelectedBucketsCount: 16 out of 16` for all three large inputs
- two large-table `SortMergeJoin` operations on `match_id`
- explicit `BroadcastExchange` / `BroadcastHashJoin` operations for small
  dimensions
- no hash-partition shuffle exchange between the bucket-aligned large joins

The final storage experiment performs:

- a controlled non-partitioned baseline
- `partitionBy("playlist_id")`
- `partitionBy("map_name")`
- `partitionBy("playlist_id", "map_name")`
- explicit `repartition`
- `sortWithinPartitions`

Physical partition directories were produced during execution.

## Validation

Final Week 3 remediation validator:

**23 PASS / 0 FAIL**

The hardened implementation also:

- compiles successfully
- executes successfully under PySpark 4.1.1
- passes the original Week 3 static validator
- preserves the original graded ZIP unchanged

## Historical Preservation

The original submission baseline is:

`week03-graded-a`

Original submitted ZIP SHA-256:

`719984774276fc2da7291a4841ea6009608bf685414eddda79de1c0d3b124c79`

## Grade Status

The recorded course grade remains **80% / B** until the instructor or
platform explicitly publishes an updated score.

Technical remediation status:

**Complete**
