-- Initialize user_devices_cumulated for 2023-01-01.

WITH deduped_devices AS (
    SELECT DISTINCT
        device_id,
        browser_type
    FROM devices
)

INSERT INTO user_devices_cumulated (
    user_id,
    browser_type,
    device_activity_datelist,
    date
)

SELECT
    e.user_id,
    d.browser_type,
    ARRAY[DATE '2023-01-01'],
    DATE '2023-01-01'

FROM events e

INNER JOIN deduped_devices d
    ON e.device_id = d.device_id

WHERE e.event_time::DATE = DATE '2023-01-01'
  AND e.user_id IS NOT NULL
  AND d.browser_type IS NOT NULL

GROUP BY
    e.user_id,
    d.browser_type;


-- Initialize hosts_cumulated for 2023-01-01.

INSERT INTO hosts_cumulated (
    host,
    host_activity_datelist,
    date
)

SELECT
    host,
    ARRAY[DATE '2023-01-01'],
    DATE '2023-01-01'

FROM events

WHERE event_time::DATE = DATE '2023-01-01'
  AND host IS NOT NULL

GROUP BY host;
