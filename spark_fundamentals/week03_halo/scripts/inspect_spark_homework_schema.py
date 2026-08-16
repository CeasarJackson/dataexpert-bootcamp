"""
Schema Inspection Utility
Apache Spark Homework - Spark Fundamentals Week

Run this before the homework job if your source column names differ from the
expected DataExpert Halo dataset schema.

Example:
    spark-submit inspect_spark_homework_schema.py
"""

import os

from pyspark.sql import SparkSession


INPUT_BASE = os.environ.get("SPARK_HW_INPUT_BASE", "./data")

TABLES = [
    "match_details",
    "matches",
    "medals_matches_players",
    "medals",
    "maps",
]


def main() -> None:
    spark = (
        SparkSession.builder
        .appName("InspectSparkHomeworkSchema")
        .getOrCreate()
    )

    try:
        for table_name in TABLES:
            path = f"{INPUT_BASE}/{table_name}"
            print("\n" + "=" * 80)
            print(f"TABLE: {table_name}")
            print(f"PATH : {path}")
            print("=" * 80)

            df = spark.read.parquet(path)
            df.printSchema()
            df.show(5, truncate=False)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
