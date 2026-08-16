"""
Apache Spark Homework Submission
Spark Fundamentals Week

Author: Ceasar Jackson
Purpose:
    Demonstrate Spark join optimization, bucketing, explicit broadcast joins,
    aggregations, sortWithinPartitions experiments, and storage comparison.

Assignment requirements implemented:
    1. Disable Spark automatic broadcast joins.
    2. Explicitly broadcast the small dimension tables: medals and maps.
    3. Bucket match_details, matches, and medals_matches_players by match_id
       into 16 buckets.
    4. Join the datasets and answer:
         - Which player averages the most kills per game?
         - Which playlist gets played the most?
         - Which map gets played the most?
         - Which map produces the most Killing Spree medals?
    5. Experiment with sortWithinPartitions() using low-cardinality columns
       and compare output sizes.

Notes:
    - Update INPUT_BASE and OUTPUT_BASE for your environment.
    - The code assumes Parquet source files. If your course environment uses
      Spark SQL managed tables, replace the read_parquet() calls with
      spark.table("<table_name>").
    - Column names follow the common DataExpert Halo dataset conventions.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import broadcast


# =============================================================================
# Configuration
# =============================================================================

INPUT_BASE = os.environ.get("SPARK_HW_INPUT_BASE", "./data")
OUTPUT_BASE = os.environ.get("SPARK_HW_OUTPUT_BASE", "./output")

NUM_BUCKETS = 16

TABLE_PATHS: Dict[str, str] = {
    "match_details": f"{INPUT_BASE}/match_details",
    "matches": f"{INPUT_BASE}/matches",
    "medals_matches_players": f"{INPUT_BASE}/medals_matches_players",
    "medals": f"{INPUT_BASE}/medals",
    "maps": f"{INPUT_BASE}/maps",
}


# =============================================================================
# Spark setup
# =============================================================================

def build_spark() -> SparkSession:
    """Create the Spark session and apply assignment-required configuration."""
    spark = (
        SparkSession.builder
        .appName("ApacheSparkHomeworkSubmission")
        .enableHiveSupport()
        .getOrCreate()
    )

    # Assignment requirement:
    # Disable Spark's automatic broadcast-join selection.
    spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")

    # Enable Adaptive Query Execution when available.
    spark.conf.set("spark.sql.adaptive.enabled", "true")

    return spark


# =============================================================================
# Input helpers
# =============================================================================

def read_parquet(spark: SparkSession, table_name: str) -> DataFrame:
    """Read a source dataset from its configured Parquet directory."""
    return spark.read.parquet(TABLE_PATHS[table_name])


def require_columns(df: DataFrame, dataframe_name: str, required: set[str]) -> None:
    """Fail early with a readable message when expected columns are absent."""
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            f"{dataframe_name} is missing required columns: {sorted(missing)}. "
            f"Available columns: {sorted(df.columns)}"
        )


# =============================================================================
# Bucketing
# =============================================================================

def create_bucketed_tables(
    match_details: DataFrame,
    matches: DataFrame,
    medals_matches_players: DataFrame,
) -> None:
    """
    Persist the three match_id-oriented datasets as 16-bucket Spark tables.

    saveAsTable() is used because Spark's bucket metadata is retained in the
    catalog and can therefore be used by Spark during bucket-aware joins.
    """
    (
        match_details.write
        .mode("overwrite")
        .bucketBy(NUM_BUCKETS, "match_id")
        .sortBy("match_id")
        .saveAsTable("hw_match_details_bucketed")
    )

    (
        matches.write
        .mode("overwrite")
        .bucketBy(NUM_BUCKETS, "match_id")
        .sortBy("match_id")
        .saveAsTable("hw_matches_bucketed")
    )

    (
        medals_matches_players.write
        .mode("overwrite")
        .bucketBy(NUM_BUCKETS, "match_id")
        .sortBy("match_id")
        .saveAsTable("hw_medals_matches_players_bucketed")
    )


# =============================================================================
# Join construction
# =============================================================================

def build_joined_dataframe(
    spark: SparkSession,
    medals: DataFrame,
    maps: DataFrame,
) -> DataFrame:
    """
    Build the assignment's optimized joined DataFrame.

    Large match-grain datasets are loaded from identically bucketed tables.
    Small lookup/dimension datasets are explicitly broadcast.
    """
    match_details = spark.table("hw_match_details_bucketed").alias("md")
    matches = spark.table("hw_matches_bucketed").alias("m")
    mmp = spark.table("hw_medals_matches_players_bucketed").alias("mmp")

    medals_dim = broadcast(medals).alias("med")
    maps_dim = broadcast(maps).alias("map")

    # Keep the base match/player grain first.
    joined = (
        match_details
        .join(matches, on="match_id", how="inner")
        .join(
            mmp,
            on=[
                match_details["match_id"] == mmp["match_id"],
                match_details["player_gamertag"] == mmp["player_gamertag"],
            ],
            how="left",
        )
        .drop(mmp["match_id"])
        .join(
            medals_dim,
            mmp["medal_id"] == medals_dim["medal_id"],
            how="left",
        )
        .join(
            maps_dim,
            matches["mapid"] == maps_dim["mapid"],
            how="left",
        )
    )

    return joined


# =============================================================================
# Required aggregations
# =============================================================================

def player_avg_kills_per_game(match_details: DataFrame) -> DataFrame:
    """
    Return players ranked by average kills per distinct game.

    Aggregating first to player/match protects the metric from accidental row
    duplication caused by later medal joins.
    """
    per_game = (
        match_details
        .groupBy("player_gamertag", "match_id")
        .agg(F.sum("player_total_kills").alias("kills_in_game"))
    )

    return (
        per_game
        .groupBy("player_gamertag")
        .agg(
            F.avg("kills_in_game").alias("avg_kills_per_game"),
            F.countDistinct("match_id").alias("games_played"),
        )
        .orderBy(F.desc("avg_kills_per_game"), F.desc("games_played"))
    )


def most_played_playlist(matches: DataFrame) -> DataFrame:
    """Rank playlists by number of distinct matches."""
    return (
        matches
        .groupBy("playlist_id")
        .agg(F.countDistinct("match_id").alias("matches_played"))
        .orderBy(F.desc("matches_played"))
    )


def most_played_map(matches: DataFrame, maps: DataFrame) -> DataFrame:
    """Rank maps by number of distinct matches using an explicit broadcast join."""
    matches_with_maps = matches.join(
        broadcast(maps),
        matches["mapid"] == maps["mapid"],
        "left",
    )

    map_name_col = "name" if "name" in maps.columns else "mapid"

    return (
        matches_with_maps
        .groupBy(maps[map_name_col].alias("map_name"))
        .agg(F.countDistinct(matches["match_id"]).alias("matches_played"))
        .orderBy(F.desc("matches_played"))
    )


def killing_spree_medals_by_map(
    matches: DataFrame,
    medals_matches_players: DataFrame,
    medals: DataFrame,
    maps: DataFrame,
) -> DataFrame:
    """Rank maps by the number of Killing Spree medals earned."""
    medal_name_col = "name" if "name" in medals.columns else "medal_name"
    map_name_col = "name" if "name" in maps.columns else "map_name"

    killing_spree = (
        medals
        .filter(F.lower(F.col(medal_name_col)) == F.lit("killing spree"))
        .select("medal_id")
    )

    result = (
        medals_matches_players.alias("mmp")
        .join(matches.alias("m"), on="match_id", how="inner")
        .join(
            broadcast(killing_spree).alias("ks"),
            F.col("mmp.medal_id") == F.col("ks.medal_id"),
            "inner",
        )
        .join(
            broadcast(maps).alias("map"),
            F.col("m.mapid") == F.col("map.mapid"),
            "left",
        )
        .groupBy(F.col(f"map.{map_name_col}").alias("map_name"))
        .agg(F.sum(F.col("mmp.count")).alias("killing_spree_medals"))
        .orderBy(F.desc("killing_spree_medals"))
    )

    return result


# =============================================================================
# sortWithinPartitions storage experiment
# =============================================================================

def directory_size_bytes(path: str) -> int:
    """Return the total local filesystem size of a directory tree."""
    root = Path(path)
    if not root.exists():
        return 0

    return sum(
        file.stat().st_size
        for file in root.rglob("*")
        if file.is_file()
    )


def run_sort_experiments(aggregated: DataFrame, output_base: str) -> DataFrame:
    """
    Write the same aggregated dataset using several intra-partition sort orders.

    Low-cardinality columns such as playlist_id and map_name often compress
    efficiently when similar values are colocated. The experiment measures the
    actual persisted size instead of assuming which ordering wins.

    Note:
        directory_size_bytes() is intended for a local filesystem. On DBFS/S3,
        use the platform filesystem API to calculate directory sizes.
    """
    experiments = {
        "unsorted": [],
        "playlist": ["playlist_id"],
        "map": ["map_name"],
        "playlist_map": ["playlist_id", "map_name"],
        "map_playlist": ["map_name", "playlist_id"],
    }

    rows = []

    for experiment_name, sort_columns in experiments.items():
        target = f"{output_base}/sort_experiments/{experiment_name}"

        candidate = aggregated
        if sort_columns:
            candidate = candidate.sortWithinPartitions(*sort_columns)

        (
            candidate.write
            .mode("overwrite")
            .parquet(target)
        )

        rows.append(
            (
                experiment_name,
                ",".join(sort_columns) if sort_columns else "<none>",
                directory_size_bytes(target),
            )
        )

    spark = aggregated.sparkSession

    return (
        spark.createDataFrame(
            rows,
            ["experiment", "sort_columns", "size_bytes"],
        )
        .withColumn(
            "size_mb",
            F.round(F.col("size_bytes") / F.lit(1024 * 1024), 3),
        )
        .orderBy("size_bytes")
    )


def build_storage_aggregate(
    matches: DataFrame,
    match_details: DataFrame,
    maps: DataFrame,
) -> DataFrame:
    """
    Build one compact aggregate containing both low-cardinality dimensions.

    This is used for the sortWithinPartitions storage experiment.
    """
    return (
        match_details.alias("md")
        .join(matches.alias("m"), on="match_id", how="inner")
        .join(
            broadcast(maps).alias("map"),
            F.col("m.mapid") == F.col("map.mapid"),
            how="left",
        )
        .groupBy(
            F.col("m.playlist_id").alias("playlist_id"),
            F.col("map.name").alias("map_name"),
        )
        .agg(
            F.countDistinct("match_id").alias("matches"),
            F.sum("player_total_kills").alias("total_kills"),
        )
    )


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    spark = build_spark()

    try:
        match_details = read_parquet(spark, "match_details")
        matches = read_parquet(spark, "matches")
        medals_matches_players = read_parquet(spark, "medals_matches_players")
        medals = read_parquet(spark, "medals")
        maps = read_parquet(spark, "maps")

        # Validate the essential join keys before expensive work begins.
        require_columns(match_details, "match_details", {"match_id"})
        require_columns(matches, "matches", {"match_id"})
        require_columns(
            medals_matches_players,
            "medals_matches_players",
            {"match_id"},
        )

        # ---------------------------------------------------------------------
        # 1. Required bucketing
        # ---------------------------------------------------------------------
        create_bucketed_tables(
            match_details,
            matches,
            medals_matches_players,
        )

        # Re-read bucketed tables so subsequent joins can use catalog metadata.
        md_bucketed = spark.table("hw_match_details_bucketed")
        matches_bucketed = spark.table("hw_matches_bucketed")
        mmp_bucketed = spark.table("hw_medals_matches_players_bucketed")

        # ---------------------------------------------------------------------
        # 2. Required optimized join
        # ---------------------------------------------------------------------
        joined = build_joined_dataframe(spark, medals, maps)

        print("\n===== JOIN PHYSICAL PLAN =====")
        joined.explain(mode="formatted")

        # ---------------------------------------------------------------------
        # 3. Required questions
        # ---------------------------------------------------------------------
        avg_kills = player_avg_kills_per_game(md_bucketed)
        playlists = most_played_playlist(matches_bucketed)
        maps_ranked = most_played_map(matches_bucketed, maps)
        spree_maps = killing_spree_medals_by_map(
            matches_bucketed,
            mmp_bucketed,
            medals,
            maps,
        )

        print("\n===== PLAYER WITH HIGHEST AVG KILLS / GAME =====")
        avg_kills.show(20, truncate=False)

        print("\n===== MOST PLAYED PLAYLIST =====")
        playlists.show(20, truncate=False)

        print("\n===== MOST PLAYED MAP =====")
        maps_ranked.show(20, truncate=False)

        print("\n===== MOST KILLING SPREE MEDALS BY MAP =====")
        spree_maps.show(20, truncate=False)

        # Persist result tables for inspection/submission evidence.
        avg_kills.write.mode("overwrite").parquet(
            f"{OUTPUT_BASE}/player_avg_kills"
        )
        playlists.write.mode("overwrite").parquet(
            f"{OUTPUT_BASE}/playlist_rankings"
        )
        maps_ranked.write.mode("overwrite").parquet(
            f"{OUTPUT_BASE}/map_rankings"
        )
        spree_maps.write.mode("overwrite").parquet(
            f"{OUTPUT_BASE}/killing_spree_by_map"
        )

        # ---------------------------------------------------------------------
        # 4. Required sortWithinPartitions experiment
        # ---------------------------------------------------------------------
        storage_aggregate = build_storage_aggregate(
            matches_bucketed,
            md_bucketed,
            maps,
        )

        size_results = run_sort_experiments(
            storage_aggregate,
            OUTPUT_BASE,
        )

        print("\n===== SORT WITHIN PARTITIONS SIZE COMPARISON =====")
        size_results.show(truncate=False)

        best = size_results.first()
        print(
            "\nSmallest output:"
            f" experiment={best['experiment']},"
            f" sort_columns={best['sort_columns']},"
            f" size_bytes={best['size_bytes']}"
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
