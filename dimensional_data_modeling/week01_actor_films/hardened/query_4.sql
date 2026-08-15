-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Hardened Query 4: actors_history_scd full backfill
--
-- Purpose:
--   Rebuild the complete Type 2 SCD snapshot from cumulative annual actor
--   snapshots.
--
-- Grain:
--   One row per actorid per continuous dimensional state within the latest
--   available SCD snapshot.
--
-- Streak-boundary policy:
--   A new SCD interval starts when:
--
--     1. the row is the actor's first observed snapshot
--     2. quality_class changes
--     3. is_active changes
--     4. the annual snapshot sequence contains a gap
--
-- Missing-year policy:
--   Missing source years must never be represented as though a dimensional
--   state were known to be continuously valid across that period. A year gap
--   therefore starts a new SCD streak even when dimensional attributes match.
--
-- Rerun policy:
--   The latest SCD snapshot is replaced transactionally.
-- =============================================================================

BEGIN;

-- Delete the existing target snapshot as a separate statement.
--
-- This deliberately occurs before the INSERT statement rather than inside a
-- data-modifying CTE. PostgreSQL statements within the transaction execute in
-- sequence, so the rebuilt snapshot can be inserted without conflicting with
-- rows from the previous target snapshot.
DELETE FROM actors_history_scd
WHERE current_year = (
    SELECT MAX(current_year)
    FROM actors
);

WITH latest_year AS (

    SELECT
        MAX(current_year) AS current_year
    FROM actors

),

ordered_actor_state AS (

    SELECT
        actorid,
        current_year,
        quality_class,
        is_active,

        ROW_NUMBER() OVER (
            PARTITION BY actorid
            ORDER BY current_year
        ) AS actor_row_number,

        LAG(current_year) OVER (
            PARTITION BY actorid
            ORDER BY current_year
        ) AS previous_year,

        LAG(quality_class) OVER (
            PARTITION BY actorid
            ORDER BY current_year
        ) AS previous_quality_class,

        LAG(is_active) OVER (
            PARTITION BY actorid
            ORDER BY current_year
        ) AS previous_is_active

    FROM actors

),

streak_started AS (

    SELECT
        actorid,
        current_year,
        quality_class,
        is_active,

        (
            actor_row_number = 1

            OR previous_year IS NULL

            OR current_year <> previous_year + 1

            OR quality_class
               IS DISTINCT FROM previous_quality_class

            OR is_active
               IS DISTINCT FROM previous_is_active
        ) AS did_change

    FROM ordered_actor_state

),

streak_identified AS (

    SELECT
        actorid,
        current_year,
        quality_class,
        is_active,

        SUM(
            CASE
                WHEN did_change THEN 1
                ELSE 0
            END
        ) OVER (
            PARTITION BY actorid
            ORDER BY current_year
            ROWS BETWEEN UNBOUNDED PRECEDING
                 AND CURRENT ROW
        ) AS streak_identifier

    FROM streak_started

),

aggregated AS (

    SELECT
        actorid,
        quality_class,
        is_active,
        streak_identifier,
        MIN(current_year) AS start_date,
        MAX(current_year) AS end_date

    FROM streak_identified

    GROUP BY
        actorid,
        quality_class,
        is_active,
        streak_identifier

),

target_snapshot AS (

    SELECT
        ly.current_year
    FROM latest_year AS ly
    WHERE ly.current_year IS NOT NULL

)

INSERT INTO actors_history_scd (
    actorid,
    quality_class,
    is_active,
    start_date,
    end_date,
    current_year
)

SELECT
    a.actorid,
    a.quality_class,
    a.is_active,
    a.start_date,
    a.end_date,
    ts.current_year

FROM aggregated AS a

CROSS JOIN target_snapshot AS ts;

COMMIT;
