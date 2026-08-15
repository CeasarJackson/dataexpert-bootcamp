-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 6: Incremental host_activity_datelist generation
--
-- Example processing window:
--   Previous snapshot: 2023-01-30
--   Incoming day:      2023-01-31
--
-- Behavior:
--   - Existing hosts retain their historical activity dates.
--   - Active hosts append the incoming date.
--   - New hosts begin with the incoming date.
--   - Previously known hosts with no activity are carried forward unchanged.
-- =============================================================================

WITH yesterday AS (
    SELECT
        host,
        host_activity_datelist,
        date

    FROM hosts_cumulated

    WHERE date = DATE '2023-01-30'
),

today AS (
    SELECT
        host,
        event_time::DATE AS activity_date

    FROM events

    WHERE event_time::DATE = DATE '2023-01-31'
      AND host IS NOT NULL

    GROUP BY
        host,
        event_time::DATE
)

INSERT INTO hosts_cumulated (
    host,
    host_activity_datelist,
    date
)

SELECT
    COALESCE(t.host, y.host) AS host,

    COALESCE(
        y.host_activity_datelist,
        ARRAY[]::DATE[]
    )
    ||
    CASE
        WHEN t.host IS NOT NULL
            THEN ARRAY[t.activity_date]
        ELSE ARRAY[]::DATE[]
    END AS host_activity_datelist,

    DATE '2023-01-31' AS date

FROM yesterday AS y

FULL OUTER JOIN today AS t
    ON y.host = t.host;
