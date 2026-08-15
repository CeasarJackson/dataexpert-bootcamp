-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Query 4: actors_history_scd full backfill
--
-- Purpose:
--   Populate the complete Type 2 SCD history in a single query.
--
-- Algorithm:
--   1. Compare each actor-year state with the preceding year using LAG().
--   2. Flag changes to quality_class or is_active.
--   3. Cumulatively sum change flags to identify state streaks.
--   4. Collapse each streak into start_date/end_date boundaries.
--   5. Store the result as the latest available SCD snapshot.
-- =============================================================================

WITH latest_year AS (

    SELECT MAX(current_year) AS current_year
    FROM actors

),

streak_started AS (

    SELECT
        actorid,
        current_year,
        quality_class,
        is_active,

        (
            LAG(quality_class) OVER (
                PARTITION BY actorid
                ORDER BY current_year
            ) IS DISTINCT FROM quality_class

            OR

            LAG(is_active) OVER (
                PARTITION BY actorid
                ORDER BY current_year
            ) IS DISTINCT FROM is_active
        ) AS did_change

    FROM actors

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
    aggregated.actorid,
    aggregated.quality_class,
    aggregated.is_active,
    aggregated.start_date,
    aggregated.end_date,
    latest_year.current_year

FROM aggregated

CROSS JOIN latest_year;
