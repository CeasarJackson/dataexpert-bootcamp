-- =============================================================================
-- Initialize actors cumulative dimension for first available year: 1970
-- =============================================================================

INSERT INTO actors (
    actor,
    actorid,
    films,
    quality_class,
    is_active,
    current_year
)
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

    CASE
        WHEN AVG(rating) > 8 THEN 'star'
        WHEN AVG(rating) > 7 THEN 'good'
        WHEN AVG(rating) > 6 THEN 'average'
        ELSE 'bad'
    END::quality_class AS quality_class,

    TRUE AS is_active,

    1970 AS current_year

FROM actor_films
WHERE year = 1970

GROUP BY
    actor,
    actorid;
