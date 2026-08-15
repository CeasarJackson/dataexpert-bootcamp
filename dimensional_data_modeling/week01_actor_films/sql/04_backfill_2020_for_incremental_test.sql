WITH streak_started AS (

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

    WHERE current_year <= 2020

),

streak_identified AS (

    SELECT
        actorid,
        current_year,
        quality_class,
        is_active,

        SUM(
            CASE WHEN did_change THEN 1 ELSE 0 END
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
    actorid,
    quality_class,
    is_active,
    start_date,
    end_date,
    2020
FROM aggregated;
