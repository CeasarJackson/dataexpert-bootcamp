-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 8: Day-by-day incremental load of host_activity_reduced
--
-- Example incoming day:
--   2023-01-31
--
-- Grain:
--   One row per host per calendar month.
--
-- Processing model:
--   Run once per calendar day in chronological order.
--
-- Array semantics:
--   Position N represents day N of the month.
--
-- Behavior:
--   - Active hosts append today's hit/visitor metrics.
--   - Existing inactive hosts append zeroes.
--   - New hosts appearing after day 1 receive leading zeroes so their arrays
--     remain aligned to calendar-day positions.
--   - A completely inactive calendar date still appends zeroes to known hosts.
-- =============================================================================

WITH parameters AS (
    SELECT
        DATE '2023-01-31' AS current_date,
        DATE_TRUNC(
            'month',
            DATE '2023-01-31'
        )::DATE AS month_start
),

today AS (
    SELECT
        p.month_start AS month,
        e.host,
        COUNT(1)::BIGINT AS hit_count,
        COUNT(DISTINCT e.user_id)::BIGINT AS unique_visitor_count

    FROM events AS e

    CROSS JOIN parameters AS p

    WHERE e.event_time::DATE = p.current_date
      AND e.host IS NOT NULL

    GROUP BY
        p.month_start,
        e.host
),

existing_hosts AS (
    SELECT
        har.month,
        har.host,
        har.hit_array,
        har.unique_visitors

    FROM host_activity_reduced AS har

    CROSS JOIN parameters AS p

    WHERE har.month = p.month_start
),

combined AS (
    SELECT
        COALESCE(eh.month, t.month, p.month_start) AS month,
        COALESCE(eh.host, t.host) AS host,

        CASE
            WHEN eh.host IS NOT NULL THEN
                eh.hit_array
                || ARRAY[COALESCE(t.hit_count, 0::BIGINT)]

            ELSE
                ARRAY_FILL(
                    0::BIGINT,
                    ARRAY[
                        GREATEST(
                            p.current_date - p.month_start,
                            0
                        )
                    ]
                )
                || ARRAY[COALESCE(t.hit_count, 0::BIGINT)]
        END AS hit_array,

        CASE
            WHEN eh.host IS NOT NULL THEN
                eh.unique_visitors
                || ARRAY[
                    COALESCE(
                        t.unique_visitor_count,
                        0::BIGINT
                    )
                ]

            ELSE
                ARRAY_FILL(
                    0::BIGINT,
                    ARRAY[
                        GREATEST(
                            p.current_date - p.month_start,
                            0
                        )
                    ]
                )
                || ARRAY[
                    COALESCE(
                        t.unique_visitor_count,
                        0::BIGINT
                    )
                ]
        END AS unique_visitors

    FROM existing_hosts AS eh

    FULL OUTER JOIN today AS t
        ON eh.month = t.month
       AND eh.host = t.host

    CROSS JOIN parameters AS p
)

INSERT INTO host_activity_reduced (
    month,
    host,
    hit_array,
    unique_visitors
)

SELECT
    month,
    host,
    hit_array,
    unique_visitors

FROM combined

WHERE host IS NOT NULL

ON CONFLICT (month, host)
DO UPDATE SET
    hit_array = EXCLUDED.hit_array,
    unique_visitors = EXCLUDED.unique_visitors;
