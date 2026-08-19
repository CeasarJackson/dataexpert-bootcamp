#!/usr/bin/env python3
"""
===============================================================================
Week 7 Post-Grade Aggregate Builder
===============================================================================

Author:
    Ceasar Jackson

Project:
    DataExpert Boot Camp — Week 7 Data Visualization / Tableau

Purpose:
    Build deterministic, purpose-specific aggregate datasets for the Week 7
    post-grade Tableau hardening work.

    The script intentionally writes to a separate post_grade directory so the
    exact graded prepared datasets remain unchanged.

Inputs:
    data/prepared/tableau_player_match_performance.csv
    data/prepared/tableau_player_medal_performance.csv
    upstream/.../3-spark-fundamentals/data/maps.csv

Outputs:
    data/prepared/post_grade/map_performance.csv
    data/prepared/post_grade/medal_per_match.csv
    data/prepared/post_grade/medal_distribution.csv

Important semantic rule:
    Match-normalized medal metrics use the complete match population from
    tableau_player_match_performance.csv.

    They MUST NOT use only matches represented in the medal-detail dataset,
    because matches with zero medal rows would otherwise disappear from the
    denominator.

Usage:
    python3 data_visualization/tableau_homework/scripts/build_post_grade_aggregates.py

Validation:
    python3 -m py_compile \
      data_visualization/tableau_homework/scripts/build_post_grade_aggregates.py
===============================================================================
"""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

WEEK7_ROOT = REPO_ROOT / "data_visualization/tableau_homework"

PLAYER_FILE = (
    WEEK7_ROOT
    / "data/prepared/tableau_player_match_performance.csv"
)

MEDAL_FILE = (
    WEEK7_ROOT
    / "data/prepared/tableau_player_medal_performance.csv"
)

MAP_FILE = (
    REPO_ROOT
    / "upstream/data-engineer-handbook/intermediate-bootcamp"
    / "materials/3-spark-fundamentals/data/maps.csv"
)

OUTPUT_DIR = WEEK7_ROOT / "data/prepared/post_grade"


def fail(message: str) -> None:
    """Terminate execution with a clear validation failure."""

    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_file(path: Path) -> None:
    """Require an input file to exist and be non-empty."""

    if not path.is_file():
        fail(f"required input does not exist: {path}")

    if path.stat().st_size == 0:
        fail(f"required input is empty: {path}")


def map_display_name(map_id: str, source_name: str) -> str:
    """
    Return a deterministic human-readable display label for a map.

    Source-provided names are preserved exactly after surrounding whitespace
    is removed. If the authoritative lookup contains a blank name, retain the
    map in the analytical population and use a traceable fallback label based
    on the first eight characters of its map ID.

    The fallback does not claim to be an authoritative map name.
    """

    name = source_name.strip()

    if name:
        return name

    return f"Unnamed Map ({map_id[:8]})"


def load_map_names() -> dict[str, str]:
    """Return map ID -> human-readable map name."""

    result: dict[str, str] = {}

    with MAP_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        reader = csv.DictReader(handle)

        required = {"mapid", "name"}

        if not required.issubset(reader.fieldnames or []):
            fail(
                "maps.csv missing required columns: "
                + ", ".join(sorted(required))
            )

        for row in reader:
            map_id = row["mapid"].strip()
            name = row["name"].strip()

            if map_id:
                result[map_id] = name

    return result


def load_player_population():
    """
    Load the authoritative player/match population.

    Returns structures used as denominators for normalized metrics.
    """

    player_match_keys: set[tuple[str, str]] = set()
    all_matches: set[str] = set()

    map_matches: dict[str, set[str]] = defaultdict(set)
    map_player_matches: dict[str, set[tuple[str, str]]] = defaultdict(set)
    map_players: dict[str, set[str]] = defaultdict(set)

    match_map: dict[str, str] = {}

    with PLAYER_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        reader = csv.DictReader(handle)

        required = {
            "match_id",
            "player_gamertag",
            "map_id",
        }

        if not required.issubset(reader.fieldnames or []):
            fail(
                "player dataset missing required columns: "
                + ", ".join(sorted(required))
            )

        row_count = 0

        for row in reader:
            row_count += 1

            match_id = row["match_id"].strip()
            player = row["player_gamertag"].strip()
            map_id = row["map_id"].strip()

            if not match_id or not player or not map_id:
                fail(
                    f"blank grain key encountered in player row {row_count}"
                )

            key = (match_id, player)

            if key in player_match_keys:
                fail(
                    "duplicate player/match grain encountered: "
                    f"{match_id} / {player}"
                )

            player_match_keys.add(key)
            all_matches.add(match_id)

            map_matches[map_id].add(match_id)
            map_player_matches[map_id].add(key)
            map_players[map_id].add(player)

            previous_map = match_map.setdefault(match_id, map_id)

            if previous_map != map_id:
                fail(
                    f"match {match_id} resolves to multiple maps"
                )

    return {
        "player_match_keys": player_match_keys,
        "all_matches": all_matches,
        "map_matches": map_matches,
        "map_player_matches": map_player_matches,
        "map_players": map_players,
        "match_map": match_map,
    }


def load_medals():
    """Aggregate medal facts without inventing zero-medal rows."""

    total_medals = 0
    medal_matches: set[str] = set()

    map_medals: Counter[str] = Counter()
    medal_totals: Counter[tuple[str, str]] = Counter()
    medal_names: dict[str, str] = {}

    with MEDAL_FILE.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        reader = csv.DictReader(handle)

        required = {
            "match_id",
            "map_id",
            "medal_id",
            "medal_name",
            "medal_count",
        }

        if not required.issubset(reader.fieldnames or []):
            fail(
                "medal dataset missing required columns: "
                + ", ".join(sorted(required))
            )

        for row_number, row in enumerate(reader, start=1):
            match_id = row["match_id"].strip()
            map_id = row["map_id"].strip()
            medal_id = row["medal_id"].strip()
            medal_name = row["medal_name"].strip()

            try:
                count = int(row["medal_count"] or 0)
            except ValueError:
                fail(
                    f"invalid medal_count at medal row {row_number}: "
                    f"{row['medal_count']!r}"
                )

            if count < 0:
                fail(
                    f"negative medal_count at medal row {row_number}"
                )

            total_medals += count
            medal_matches.add(match_id)
            map_medals[map_id] += count
            medal_totals[(medal_id, medal_name)] += count

            if medal_id:
                previous_name = medal_names.setdefault(
                    medal_id,
                    medal_name,
                )

                if previous_name != medal_name:
                    fail(
                        f"medal ID {medal_id} has multiple names"
                    )

    return {
        "total_medals": total_medals,
        "medal_matches": medal_matches,
        "map_medals": map_medals,
        "medal_totals": medal_totals,
    }


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, object]],
) -> None:
    """Write a deterministic UTF-8 CSV."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(rows)


def build_map_performance(
    population,
    medals,
    map_names: dict[str, str],
) -> list[dict[str, object]]:
    """Build one row per map."""

    rows: list[dict[str, object]] = []

    map_matches = population["map_matches"]
    map_player_matches = population["map_player_matches"]
    map_players = population["map_players"]
    map_medals = medals["map_medals"]

    missing_lookup_ids = set(map_matches) - set(map_names)

    if missing_lookup_ids:
        fail(
            "map lookup rows missing for: "
            + ", ".join(sorted(missing_lookup_ids))
        )

    display_names = {
        map_id: map_display_name(map_id, map_names[map_id])
        for map_id in map_matches
    }

    for map_id in sorted(
        map_matches,
        key=lambda value: (
            display_names[value].casefold(),
            value,
        ),
    ):
        match_count = len(map_matches[map_id])
        player_match_count = len(map_player_matches[map_id])
        distinct_players = len(map_players[map_id])
        medal_count = map_medals[map_id]

        rows.append(
            {
                "map_id": map_id,
                "map_name": display_names[map_id],
                "match_count": match_count,
                "player_match_count": player_match_count,
                "distinct_players": distinct_players,
                "medal_count": medal_count,
                "medals_per_match": (
                    f"{medal_count / match_count:.6f}"
                    if match_count
                    else "0.000000"
                ),
                "medals_per_player_match": (
                    f"{medal_count / player_match_count:.6f}"
                    if player_match_count
                    else "0.000000"
                ),
            }
        )

    return rows


def build_medal_per_match(
    population,
    medals,
) -> list[dict[str, object]]:
    """Build the authoritative overall match-normalized medal KPI."""

    match_count = len(population["all_matches"])
    player_match_count = len(population["player_match_keys"])
    medal_count = medals["total_medals"]
    medal_match_count = len(medals["medal_matches"])

    return [
        {
            "match_count": match_count,
            "player_match_count": player_match_count,
            "matches_with_medal_rows": medal_match_count,
            "matches_without_medal_rows": (
                match_count - medal_match_count
            ),
            "medal_count": medal_count,
            "medals_per_match": (
                f"{medal_count / match_count:.6f}"
            ),
            "medals_per_player_match": (
                f"{medal_count / player_match_count:.6f}"
            ),
        }
    ]


def build_medal_distribution(
    medals,
) -> list[dict[str, object]]:
    """Build one row per medal type, ranked by total count."""

    totals = medals["medal_totals"]
    grand_total = medals["total_medals"]

    ranked = sorted(
        totals.items(),
        key=lambda item: (
            -item[1],
            item[0][1].casefold(),
            item[0][0],
        ),
    )

    rows: list[dict[str, object]] = []

    for rank, ((medal_id, medal_name), count) in enumerate(
        ranked,
        start=1,
    ):
        rows.append(
            {
                "medal_rank": rank,
                "medal_id": medal_id,
                "medal_name": medal_name,
                "medal_count": count,
                "share_of_medals": (
                    f"{count / grand_total:.8f}"
                    if grand_total
                    else "0.00000000"
                ),
            }
        )

    return rows


def main() -> int:
    """Build and validate all approved post-grade aggregate datasets."""

    print("=" * 78)
    print(" WEEK 7 — BUILD POST-GRADE AGGREGATES")
    print("=" * 78)

    for path in (PLAYER_FILE, MEDAL_FILE, MAP_FILE):
        require_file(path)
        print(f"PASS: input exists: {path.relative_to(REPO_ROOT)}")

    print()
    print("Loading authoritative map lookup...")
    map_names = load_map_names()

    print("Loading player/match population...")
    population = load_player_population()

    print("Loading medal facts...")
    medals = load_medals()

    match_count = len(population["all_matches"])
    medal_match_count = len(medals["medal_matches"])

    if medal_match_count > match_count:
        fail("medal match population exceeds player match population")

    print()
    print(f"Player/match rows:       {len(population['player_match_keys']):,}")
    print(f"Distinct matches:        {match_count:,}")
    print(f"Matches with medals:     {medal_match_count:,}")
    print(
        "Matches without medals:  "
        f"{match_count - medal_match_count:,}"
    )
    print(f"Total medals:            {medals['total_medals']:,}")

    map_rows = build_map_performance(
        population,
        medals,
        map_names,
    )

    medal_per_match_rows = build_medal_per_match(
        population,
        medals,
    )

    medal_distribution_rows = build_medal_distribution(
        medals,
    )

    print()
    print("Writing deterministic post-grade outputs...")

    write_csv(
        OUTPUT_DIR / "map_performance.csv",
        [
            "map_id",
            "map_name",
            "match_count",
            "player_match_count",
            "distinct_players",
            "medal_count",
            "medals_per_match",
            "medals_per_player_match",
        ],
        map_rows,
    )

    write_csv(
        OUTPUT_DIR / "medal_per_match.csv",
        [
            "match_count",
            "player_match_count",
            "matches_with_medal_rows",
            "matches_without_medal_rows",
            "medal_count",
            "medals_per_match",
            "medals_per_player_match",
        ],
        medal_per_match_rows,
    )

    write_csv(
        OUTPUT_DIR / "medal_distribution.csv",
        [
            "medal_rank",
            "medal_id",
            "medal_name",
            "medal_count",
            "share_of_medals",
        ],
        medal_distribution_rows,
    )

    print()
    print("Generated:")

    for path in sorted(OUTPUT_DIR.glob("*.csv")):
        print(
            f"  {path.relative_to(REPO_ROOT)} "
            f"({path.stat().st_size:,} bytes)"
        )

    print()
    print("PASS: post-grade aggregate build complete")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
