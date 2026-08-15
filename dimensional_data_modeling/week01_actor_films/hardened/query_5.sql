-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Query 5: Incremental actors_history_scd generation
--
-- Previous SCD snapshot:
--   2020
--
-- Incoming actor snapshot:
--   2021
--
-- Purpose:
--   Generate the 2021 SCD snapshot by combining the previous year's SCD
--   history with the incoming 2021 actors dimensional state.
--
-- Record handling:
--   Historical records -> copied unchanged.
--   Unchanged actors   -> current interval is extended through 2021.
--   Changed actors     -> old interval retained and new interval created.
--   New actors         -> new interval begins in 2021.
-- =============================================================================

WITH last_year_scd AS (

    SELECT
        actorid,
        quality_class,
        is_active,
        start_date,
        end_date

    FROM actors_history_scd

    WHERE current_year = 2020
      AND end_date = 2020

),

historical_scd AS (

    SELECT
        actorid,
        quality_class,
        is_active,
        start_date,
        end_date

    FROM actors_history_scd

    WHERE current_year = 2020
      AND end_date < 2020

),

this_year_data AS (

    SELECT
        actorid,
        quality_class,
        is_active,
        current_year

    FROM actors

    WHERE current_year = 2021

),

unchanged_records AS (

    SELECT
        ty.actorid,
        ty.quality_class,
        ty.is_active,
        ly.start_date,
        ty.current_year AS end_date

    FROM this_year_data ty

    INNER JOIN last_year_scd ly
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

    FROM this_year_data ty

    INNER JOIN last_year_scd ly
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

    FROM this_year_data ty

    LEFT JOIN last_year_scd ly
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
    actorid,
    quality_class,
    is_active,
    start_date,
    end_date,
    2021 AS current_year

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

) combined;
