-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Hardened Query 2: Parameterized cumulative actors generation
--
-- Purpose:
--   Generate one cumulative actor snapshot from the immediately preceding
--   annual snapshot.
--
-- Runtime parameters:
--   previous_year - existing cumulative snapshot year
--   current_year  - incoming actor_films source year / target snapshot year
--
-- Example:
--   psql \
--     -v previous_year=2020 \
--     -v current_year=2021 \
--     -f query_2.sql
--
-- Grain:
--   One row per actorid per current_year.
--
-- Rerun policy:
--   The target current_year snapshot is replaced transactionally. If generation
--   fails, PostgreSQL rolls back both the DELETE and INSERT.
--
-- Preserved graded behavior:
--   - Existing actors retain cumulative film history.
--   - Incoming films are appended to existing film arrays.
--   - quality_class is recalculated only for actors with films this year.
--   - Inactive actors retain their prior quality_class.
-- =============================================================================

BEGIN;

DELETE FROM actors
WHERE current_year = :'current_year'::INTEGER;

WITH params AS (

    SELECT
        :'previous_year'::INTEGER AS previous_year,
        :'current_year'::INTEGER AS current_year

),

last_year AS (

    SELECT
        a.actor,
        a.actorid,
        a.films,
        a.quality_class,
        a.is_active,
        a.current_year

    FROM actors AS a

    CROSS JOIN params AS p

    WHERE a.current_year = p.previous_year

),

this_year AS (

    SELECT
        af.actor,
        af.actorid,

        ARRAY_AGG(
            ROW(
                af.film,
                af.votes,
                af.rating,
                af.filmid
            )::film_struct
            ORDER BY af.filmid
        ) AS films,

        AVG(af.rating) AS avg_rating,

        af.year

    FROM actor_films AS af

    CROSS JOIN params AS p

    WHERE af.year = p.current_year

    GROUP BY
        af.actor,
        af.actorid,
        af.year

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

    p.current_year AS current_year

FROM last_year AS ly

FULL OUTER JOIN this_year AS ty
    ON ly.actorid = ty.actorid

CROSS JOIN params AS p;

COMMIT;
