WITH yesterday AS (
    SELECT
        host,
        host_activity_datelist,
        date
    FROM hosts_cumulated
    WHERE date = :'previous_date'::DATE
),

today AS (
    SELECT
        host,
        event_time::DATE AS activity_date
    FROM events
    WHERE event_time::DATE = :'current_date'::DATE
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
    COALESCE(t.host, y.host),

    COALESCE(
        y.host_activity_datelist,
        ARRAY[]::DATE[]
    )
    ||
    CASE
        WHEN t.host IS NOT NULL
            THEN ARRAY[t.activity_date]
        ELSE ARRAY[]::DATE[]
    END,

    :'current_date'::DATE

FROM yesterday y

FULL OUTER JOIN today t
    ON y.host = t.host;
