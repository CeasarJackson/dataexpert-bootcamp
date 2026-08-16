-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 3: Cumulative device_activity_datelist generation
--
-- Example processing window:
--   Previous snapshot: 2023-01-30
--   Incoming day:      2023-01-31
--
-- Important source-data behavior:
--   devices contains duplicate physical rows for each device_id. The
--   deduped_devices CTE prevents those duplicate records from doubling event
--   counts during the events/devices join.
--
-- Behavior:
--   - Existing user/browser combinations retain their activity history.
--   - Active combinations append the incoming date once.
--   - New combinations begin with the incoming date.
--   - Inactive combinations are carried forward unchanged.
-- =============================================================================

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

    WHERE date = DATE '2023-01-30'
),

today AS (
    SELECT
        e.user_id,
        d.browser_type,
        e.event_time::DATE AS activity_date

    FROM events AS e

    INNER JOIN deduped_devices AS d
        ON e.device_id = d.device_id

    WHERE e.event_time::DATE = DATE '2023-01-31'
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
    COALESCE(t.user_id, y.user_id) AS user_id,

    COALESCE(t.browser_type, y.browser_type) AS browser_type,

    COALESCE(
        y.device_activity_datelist,
        ARRAY[]::DATE[]
    )
    ||
    CASE
        WHEN t.user_id IS NOT NULL
            THEN ARRAY[t.activity_date]
        ELSE ARRAY[]::DATE[]
    END AS device_activity_datelist,

    DATE '2023-01-31' AS date

FROM yesterday AS y

FULL OUTER JOIN today AS t
    ON y.user_id = t.user_id
   AND y.browser_type = t.browser_type

ON CONFLICT (user_id, browser_type, date)
DO UPDATE SET
    device_activity_datelist = EXCLUDED.device_activity_datelist;
