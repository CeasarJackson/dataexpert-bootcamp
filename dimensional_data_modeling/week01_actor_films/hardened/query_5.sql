-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Hardened Query 5: Parameterized incremental actors_history_scd generation
--
-- Purpose:
--   Generate the current Type 2 SCD snapshot from:
--
--     1. the previous SCD snapshot
--     2. the incoming actors cumulative snapshot
--
-- Runtime parameters:
--   previous_year - previous SCD snapshot year
--   current_year  - incoming actors snapshot / target SCD snapshot year
--
-- Example:
--   psql \
--     -v previous_year=2020 \
--     -v current_year=2021 \
--     -f query_5.sql
--
-- Record handling:
--   Historical records -> copied unchanged.
--   Unchanged actors   -> open interval extended through current_year.
--   Changed actors     -> previous interval closed and new interval created.
--   New actors         -> new interval begins in current_year.
--
-- Incremental-year contract:
--   current_year must equal previous_year + 1. Non-adjacent processing windows
--   fail before the target snapshot is modified.
--
-- Rerun policy:
--   The target current_year SCD snapshot is replaced transactionally. A failure
--   rolls back both the DELETE and INSERT.
-- =============================================================================

\if :{?previous_year}
\else
    \echo 'ERROR: required psql variable previous_year was not provided'
    \quit 3
\endif

\if :{?current_year}
\else
    \echo 'ERROR: required psql variable current_year was not provided'
    \quit 3
\endif

-- ---------------------------------------------------------------------------
-- Incremental-year contract validation
-- ---------------------------------------------------------------------------
--
-- This algorithm models exactly one annual transition. Evaluate the contract
-- before BEGIN so an invalid processing window cannot modify target state.
SELECT
    (
        :'current_year'::INTEGER
        =
        :'previous_year'::INTEGER + 1
    ) AS incremental_year_contract_ok
\gset

\if :incremental_year_contract_ok
\else
    \echo 'ERROR: current_year must equal previous_year + 1'

    -- Deliberately raise a SQL error so ON_ERROR_STOP=1 causes psql to
    -- terminate with a nonzero exit status. PostgreSQL 14 psql does not
    -- support supplying an exit code argument to \quit.
    SELECT 1 / 0 AS invalid_incremental_year_window;
\endif

BEGIN;

DELETE FROM actors_history_scd
WHERE current_year = :'current_year'::INTEGER;

WITH params AS (

    SELECT
        :'previous_year'::INTEGER AS previous_year,
        :'current_year'::INTEGER AS current_year

),

last_year_scd AS (

    SELECT
        scd.actorid,
        scd.quality_class,
        scd.is_active,
        scd.start_date,
        scd.end_date

    FROM actors_history_scd AS scd

    CROSS JOIN params AS p

    WHERE scd.current_year = p.previous_year
      AND scd.end_date = p.previous_year

),

historical_scd AS (

    SELECT
        scd.actorid,
        scd.quality_class,
        scd.is_active,
        scd.start_date,
        scd.end_date

    FROM actors_history_scd AS scd

    CROSS JOIN params AS p

    WHERE scd.current_year = p.previous_year
      AND scd.end_date < p.previous_year

),

this_year_data AS (

    SELECT
        a.actorid,
        a.quality_class,
        a.is_active,
        a.current_year

    FROM actors AS a

    CROSS JOIN params AS p

    WHERE a.current_year = p.current_year

),

unchanged_records AS (

    SELECT
        ty.actorid,
        ty.quality_class,
        ty.is_active,
        ly.start_date,
        ty.current_year AS end_date

    FROM this_year_data AS ty

    INNER JOIN last_year_scd AS ly
        ON ty.actorid = ly.actorid

    WHERE ty.quality_class = ly.quality_class
      AND ty.is_active = ly.is_active

),

changed_records AS (

    SELECT
        ty.actorid,

        UNNEST(
            ARRAY[
                ROW(
                    ly.quality_class,
                    ly.is_active,
                    ly.start_date,
                    ly.end_date
                )::actor_scd_type,

                ROW(
                    ty.quality_class,
                    ty.is_active,
                    ty.current_year,
                    ty.current_year
                )::actor_scd_type
            ]
        ) AS records

    FROM this_year_data AS ty

    INNER JOIN last_year_scd AS ly
        ON ty.actorid = ly.actorid

    WHERE ty.quality_class IS DISTINCT FROM ly.quality_class
       OR ty.is_active IS DISTINCT FROM ly.is_active

),

unnested_changed_records AS (

    SELECT
        actorid,
        (records::actor_scd_type).quality_class AS quality_class,
        (records::actor_scd_type).is_active AS is_active,
        (records::actor_scd_type).start_date AS start_date,
        (records::actor_scd_type).end_date AS end_date

    FROM changed_records

),

new_records AS (

    SELECT
        ty.actorid,
        ty.quality_class,
        ty.is_active,
        ty.current_year AS start_date,
        ty.current_year AS end_date

    FROM this_year_data AS ty

    LEFT JOIN last_year_scd AS ly
        ON ty.actorid = ly.actorid

    WHERE ly.actorid IS NULL

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
    combined.actorid,
    combined.quality_class,
    combined.is_active,
    combined.start_date,
    combined.end_date,
    p.current_year AS current_year

FROM (

    SELECT *
    FROM historical_scd

    UNION ALL

    SELECT *
    FROM unchanged_records

    UNION ALL

    SELECT *
    FROM unnested_changed_records

    UNION ALL

    SELECT *
    FROM new_records

) AS combined

CROSS JOIN params AS p;

COMMIT;
