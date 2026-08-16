"""
Spark Homework Validation Utility

Purpose:
    Validate that the Spark homework source file contains the key assignment
    constructs before submission.

Usage:
    python validate_spark_homework.py spark_fundamentals_homework.py
"""

from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_PATTERNS = {
    "automatic broadcast disabled":
        'spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")',
    "explicit broadcast":
        "broadcast(",
    "16 buckets":
        ".bucketBy(NUM_BUCKETS, \"match_id\")",
    "sortWithinPartitions":
        ".sortWithinPartitions(",
    "player average kills":
        "avg_kills_per_game",
    "playlist aggregation":
        "most_played_playlist",
    "map aggregation":
        "most_played_map",
    "Killing Spree aggregation":
        "killing_spree_medals_by_map",
}


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: python validate_spark_homework.py "
            "spark_fundamentals_homework.py"
        )
        return 2

    source_path = Path(sys.argv[1])

    if not source_path.is_file():
        print(f"FAIL: file not found: {source_path}")
        return 2

    text = source_path.read_text(encoding="utf-8")
    failures = []

    for label, pattern in REQUIRED_PATTERNS.items():
        if pattern in text:
            print(f"PASS: {label}")
        else:
            print(f"FAIL: {label}")
            failures.append(label)

    if failures:
        print(f"\nValidation failed: {len(failures)} requirement(s) missing.")
        return 1

    print("\nPASS: all static homework checks succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
