WITH deduped_devices AS (
    SELECT DISTINCT
        device_id,
        browser_type
    FROM devices
),

yesterday AS (
    SELECT
        user_id,
        browser_type,
        device_activity_datelist,
        date
    FROM user_devices_cumulated
    WHERE date = :'previous_date'::DATE
),

today AS (
    SELECT
        e.user_id,
        d.browser_type,
        e.event_time::DATE AS activity_date

    FROM events e

    INNER JOIN deduped_devices d
        ON e.device_id = d.device_id

    WHERE e.event_time::DATE = :'current_date'::DATE
      AND e.user_id IS NOT NULL
      AND d.browser_type IS NOT NULL

    GROUP BY
        e.user_id,
        d.browser_type,
        e.event_time::DATE
)

INSERT INTO user_devices_cumulated (
    user_id,
    browser_type,
    device_activity_datelist,
    date
)

SELECT
    COALESCE(t.user_id, y.user_id),
    COALESCE(t.browser_type, y.browser_type),

    COALESCE(
        y.device_activity_datelist,
        ARRAY[]::DATE[]
    )
    ||
    CASE
        WHEN t.user_id IS NOT NULL
            THEN ARRAY[t.activity_date]
        ELSE ARRAY[]::DATE[]
    END,

    :'current_date'::DATE

FROM yesterday y

FULL OUTER JOIN today t
    ON y.user_id = t.user_id
   AND y.browser_type = t.browser_type;
