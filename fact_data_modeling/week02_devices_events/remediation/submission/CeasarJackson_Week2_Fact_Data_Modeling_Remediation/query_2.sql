-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 2: user_devices_cumulated DDL
--
-- Design:
--   PostgreSQL does not have a native MAP<STRING, ARRAY[DATE]> type.
--   The assignment permits browser_type as a separate column.
--
-- Grain:
--   One row per user_id + browser_type + snapshot date.
--
-- device_activity_datelist:
--   Cumulative list of dates on which the user generated activity from the
--   associated browser type.
-- =============================================================================

DROP TABLE IF EXISTS user_devices_cumulated;

CREATE TABLE user_devices_cumulated (
    user_id                  NUMERIC NOT NULL,
    browser_type             TEXT NOT NULL,
    device_activity_datelist DATE[] NOT NULL,
    date                     DATE NOT NULL,

    PRIMARY KEY (
        user_id,
        browser_type,
        date
    )
);
