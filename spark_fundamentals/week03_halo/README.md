# Spark Fundamentals - Week 3 Halo Homework

## Overview

This workspace contains the Week 3 Spark Fundamentals homework implementation for the Halo dataset assignment.

The solution focuses on Spark join optimization, bucketing, broadcast joins, and aggregation analysis.

## Assignment Requirements Covered

- Disable automatic broadcast joins.
- Explicitly broadcast small dimension tables.
- Bucket large fact-style tables by `match_id` using 16 buckets.
- Use `sortWithinPartitions` for partition-local sorting.
- Determine the player with the highest average kills per game.
- Determine the most played playlist.
- Determine the most played map.
- Determine which map produced the most Killing Spree medals.
- Compare output size differences across different sort strategies.

## Main Script

`spark_fundamentals/week03_halo/scripts/spark_fundamentals_homework.py`

## Validation Script

`spark_fundamentals/week03_halo/scripts/validate_spark_homework.py`

## Environment Used

- Conda environment: `dataeng`
- Python: 3.12.13
- PySpark: 4.1.1
- Delta: available
- Java: OpenJDK 21.0.12

## Validation Commands

```bash
python -m py_compile spark_fundamentals/week03_halo/scripts/*.py

python spark_fundamentals/week03_halo/scripts/validate_spark_homework.py \
  spark_fundamentals/week03_halo/scripts/spark_fundamentals_homework.py
```

## Runtime Notes

The real course parquet dataset is not committed to the repository.

Local runtime testing was completed using ignored smoke-test parquet data under `./data`.

Ignored local runtime artifacts:

- `data/`
- `output/`
- `spark-warehouse/`
- `metastore_db/`
- `derby.log`
- `spark_fundamentals/week03_halo/validation/logs/`
- `spark_fundamentals/week03_halo/validation/results/`

## Pull Request

https://github.com/CeasarJackson/dataexpert-bootcamp/pull/1
