-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 4: Generate datelist_int from device_activity_datelist
-- Remediation version
--
-- Purpose:
--   Convert the 32-day device activity history into the assignment-required
--   base-2 integer representation.
--
-- Grader corrections:
--   1. Give generate_series() an explicit column alias.
--   2. Return BIGINT rather than BIT(32).
--   3. Centralize the snapshot date in a parameters CTE.
--
-- Snapshot:
--   2023-01-31
--
-- Window:
--   32 days ending on the snapshot date.
--
-- Bit position:
--   Current date      -> highest-order bit (bit 31)
--   31 days prior     -> lowest-order bit  (bit 0)
-- =============================================================================

WITH parameters AS (
    SELECT
        DATE '2023-01-31' AS snapshot_date
),

starter AS (
    SELECT
        udc.user_id,
        udc.browser_type,

        udc.device_activity_datelist
            @> ARRAY[gs.valid_date::DATE] AS is_active,

        (
            p.snapshot_date - gs.valid_date::DATE
        ) AS days_since,

        p.snapshot_date

    FROM user_devices_cumulated AS udc

    CROSS JOIN parameters AS p

    CROSS JOIN LATERAL generate_series(
        p.snapshot_date - INTERVAL '31 day',
        p.snapshot_date,
        INTERVAL '1 day'
    ) AS gs(valid_date)

    WHERE udc.date = p.snapshot_date
),

bits AS (
    SELECT
        user_id,
        browser_type,

        SUM(
            CASE
                WHEN is_active
                    THEN (
                        1::BIGINT
                        << (31 - days_since)
                    )
                ELSE 0::BIGINT
            END
        )::BIGINT AS datelist_int,

        snapshot_date

    FROM starter

    GROUP BY
        user_id,
        browser_type,
        snapshot_date
)

SELECT
    user_id,
    browser_type,
    datelist_int,
    snapshot_date AS date

FROM bits;
