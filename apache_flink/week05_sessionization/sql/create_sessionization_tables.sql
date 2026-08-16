-- ============================================================================
-- DataExpert Boot Camp — Week 5 Apache Flink Sessionization
-- PostgreSQL Physical Sink Tables
-- Author: Ceasar Jackson
-- ============================================================================
--
-- Purpose:
--   Create the physical PostgreSQL tables required by the PyFlink JDBC sinks.
--
-- Important:
--   Flink CREATE TABLE statements register connector tables only. They do not
--   create these physical PostgreSQL tables.
--
-- ============================================================================

CREATE TABLE IF NOT EXISTS web_event_sessions (
    ip TEXT NOT NULL,
    host TEXT NOT NULL,
    session_start TIMESTAMP(3) NOT NULL,
    session_end TIMESTAMP(3) NOT NULL,
    event_count BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS web_event_session_host_summary (
    host TEXT PRIMARY KEY,
    session_count BIGINT NOT NULL,
    total_events BIGINT NOT NULL,
    avg_events_per_session DOUBLE PRECISION NOT NULL
);
