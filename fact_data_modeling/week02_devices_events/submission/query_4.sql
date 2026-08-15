-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 4: Generate datelist_int from device_activity_datelist
--
-- Snapshot:
--   2023-01-31
--
-- Window:
--   32 days ending on the snapshot date.
--
-- Bit position:
--   Current date      -> highest-order bit
--   31 days prior     -> lowest-order bit
-- =============================================================================

WITH starter AS (
    SELECT
        udc.user_id,
        udc.browser_type,

        udc.device_activity_datelist
            @> ARRAY[valid_date::DATE] AS is_active,

        (
            udc.date - valid_date::DATE
        ) AS days_since,

        udc.date

    FROM user_devices_cumulated AS udc

    CROSS JOIN generate_series(
        DATE '2023-01-31' - INTERVAL '31 day',
        DATE '2023-01-31',
        INTERVAL '1 day'
    ) AS valid_date

    WHERE udc.date = DATE '2023-01-31'
),

bits AS (
    SELECT
        user_id,
        browser_type,

        SUM(
            CASE
                WHEN is_active
                    THEN POWER(
                        2::NUMERIC,
                        31 - days_since
                    )
                ELSE 0
            END
        )::BIGINT::BIT(32) AS datelist_int,

        date

    FROM starter

    GROUP BY
        user_id,
        browser_type,
        date
)

SELECT
    user_id,
    browser_type,
    datelist_int,
    date

FROM bits;
