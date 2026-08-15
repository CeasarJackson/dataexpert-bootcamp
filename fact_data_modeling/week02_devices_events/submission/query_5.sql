-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 5: hosts_cumulated DDL
--
-- Grain:
--   One row per host per snapshot date.
--
-- host_activity_datelist:
--   Cumulative list of dates on which the host experienced any activity.
-- =============================================================================

DROP TABLE IF EXISTS hosts_cumulated;

CREATE TABLE hosts_cumulated (
    host                   TEXT NOT NULL,
    host_activity_datelist DATE[] NOT NULL,
    date                   DATE NOT NULL,

    PRIMARY KEY (
        host,
        date
    )
);
