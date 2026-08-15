-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 7: host_activity_reduced DDL
--
-- Grain:
--   One row per host per calendar month.
--
-- Array semantics:
--   hit_array[N]
--       = number of events for the host on day N of the month
--
--   unique_visitors[N]
--       = COUNT(DISTINCT user_id) for the host on day N of the month
--
-- Missing activity days are represented with zero values.
-- =============================================================================

DROP TABLE IF EXISTS host_activity_reduced;

CREATE TABLE host_activity_reduced (
    month           DATE NOT NULL,
    host            TEXT NOT NULL,
    hit_array       BIGINT[] NOT NULL,
    unique_visitors BIGINT[] NOT NULL,

    PRIMARY KEY (
        month,
        host
    )
);
