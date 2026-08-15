-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Query 2: Cumulative actors table generation
--
-- Example processing window:
--   Previous cumulative snapshot: 2020
--   Incoming source year:         2021
--
-- To process another year, update the previous/current year predicates.
--
-- Purpose:
--   Generate one actor snapshot year by combining:
--
--     1. the previous cumulative actor snapshot
--     2. films released during the incoming year
--
-- Notes:
--   - Existing actors retain their historical film arrays.
--   - New films are appended to the cumulative array.
--   - quality_class is recalculated only when an actor releases films.
--   - Inactive actors retain their most recent quality_class.
-- =============================================================================

WITH last_year AS (

    SELECT
        actor,
        actorid,
        films,
        quality_class,
        is_active,
        current_year

    FROM actors

    WHERE current_year = 2020

),

this_year AS (

    SELECT
        actor,
        actorid,

        ARRAY_AGG(
            ROW(
                film,
                votes,
                rating,
                filmid
            )::film_struct
            ORDER BY filmid
        ) AS films,

        AVG(rating) AS avg_rating,

        year

    FROM actor_films

    WHERE year = 2021

    GROUP BY
        actor,
        actorid,
        year

)

INSERT INTO actors (
    actor,
    actorid,
    films,
    quality_class,
    is_active,
    current_year
)

SELECT
    COALESCE(ly.actor, ty.actor) AS actor,

    COALESCE(ly.actorid, ty.actorid) AS actorid,

    COALESCE(
        ly.films,
        ARRAY[]::film_struct[]
    )
    ||
    COALESCE(
        ty.films,
        ARRAY[]::film_struct[]
    ) AS films,

    CASE
        WHEN ty.actorid IS NOT NULL THEN
            CASE
                WHEN ty.avg_rating > 8 THEN 'star'
                WHEN ty.avg_rating > 7 THEN 'good'
                WHEN ty.avg_rating > 6 THEN 'average'
                ELSE 'bad'
            END::quality_class

        ELSE ly.quality_class
    END AS quality_class,

    ty.actorid IS NOT NULL AS is_active,

    2021 AS current_year

FROM last_year ly

FULL OUTER JOIN this_year ty
    ON ly.actorid = ty.actorid;
