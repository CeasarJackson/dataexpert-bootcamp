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
-- Film-array policy:
--   - Exactly one film_struct is retained per filmid.
--   - Incoming-year data wins if the same filmid exists in historical state.
--   - If historical state itself contains repeated filmids, the most recently
--     appended historical occurrence wins.
--   - Final cumulative films are ordered globally by filmid.
--
-- Preserved graded behavior:
--   - Existing actors retain cumulative film history.
--   - quality_class is recalculated only for actors with films this year.
--   - Inactive actors retain their prior quality_class.
-- Quality policy:
--   - Threshold semantics intentionally preserve the graded implementation:
--       star    > 8
--       good    > 7
--       average > 6
--       bad     <= 6
--   - Existing actors with incoming films but no usable rating retain their
--     previous quality_class rather than being classified as bad.
--   - The course dataset currently contains no NULL ratings; this branch is
--     defensive hardening for future/replayed source data.
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

),

combined_actor_state AS (

    SELECT
        COALESCE(ly.actor, ty.actor) AS actor,
        COALESCE(ly.actorid, ty.actorid) AS actorid,

        ly.films AS historical_films,
        ty.films AS incoming_films,

        CASE
            -- No incoming films: preserve the previous dimensional state.
            WHEN ty.actorid IS NULL THEN
                ly.quality_class

            -- Incoming films exist but every rating is NULL. For an existing
            -- actor, absence of rating evidence must not imply poor quality.
            WHEN ty.avg_rating IS NULL
                 AND ly.quality_class IS NOT NULL THEN
                ly.quality_class

            -- Preserve the strict A-grade threshold semantics.
            WHEN ty.avg_rating > 8 THEN
                'star'::quality_class

            WHEN ty.avg_rating > 7 THEN
                'good'::quality_class

            WHEN ty.avg_rating > 6 THEN
                'average'::quality_class

            ELSE
                'bad'::quality_class
        END AS quality_class,

        ty.actorid IS NOT NULL AS is_active,

        p.current_year AS current_year

    FROM last_year AS ly

    FULL OUTER JOIN this_year AS ty
        ON ly.actorid = ty.actorid

    CROSS JOIN params AS p

),

film_candidates AS (

    SELECT
        cas.actorid,
        h.film,
        h.votes,
        h.rating,
        h.filmid,
        1 AS source_priority,
        h.position AS source_position

    FROM combined_actor_state AS cas

    CROSS JOIN LATERAL
        UNNEST(
            COALESCE(
                cas.historical_films,
                ARRAY[]::film_struct[]
            )
        )
        WITH ORDINALITY AS h(
            film,
            votes,
            rating,
            filmid,
            position
        )

    UNION ALL

    SELECT
        cas.actorid,
        i.film,
        i.votes,
        i.rating,
        i.filmid,
        2 AS source_priority,
        i.position AS source_position

    FROM combined_actor_state AS cas

    CROSS JOIN LATERAL
        UNNEST(
            COALESCE(
                cas.incoming_films,
                ARRAY[]::film_struct[]
            )
        )
        WITH ORDINALITY AS i(
            film,
            votes,
            rating,
            filmid,
            position
        )

),

deduplicated_films AS (

    SELECT DISTINCT ON (
        actorid,
        filmid
    )
        actorid,
        film,
        votes,
        rating,
        filmid

    FROM film_candidates

    ORDER BY
        actorid,
        filmid,
        source_priority DESC,
        source_position DESC

),

rebuilt_film_arrays AS (

    SELECT
        actorid,

        ARRAY_AGG(
            ROW(
                film,
                votes,
                rating,
                filmid
            )::film_struct
            ORDER BY filmid
        ) AS films

    FROM deduplicated_films

    GROUP BY actorid

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
    cas.actor,
    cas.actorid,

    COALESCE(
        rfa.films,
        ARRAY[]::film_struct[]
    ) AS films,

    cas.quality_class,
    cas.is_active,
    cas.current_year

FROM combined_actor_state AS cas

LEFT JOIN rebuilt_film_arrays AS rfa
    ON cas.actorid = rfa.actorid;

COMMIT;
