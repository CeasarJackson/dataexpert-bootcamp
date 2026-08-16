-- ============================================================================
-- DataExpert Boot Camp — Week 5 Apache Flink Sessionization
-- Session Metrics
-- Author: Ceasar Jackson
-- ============================================================================
--
-- Purpose:
--   Answer the two analytical questions required by the Week 5 homework:
--
--   1. What is the average number of web events per session on Tech Creator?
--   2. How do the requested hosts compare?
--
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Overall Tech Creator average
-- ---------------------------------------------------------------------------
--
-- Tech Creator is represented here by hosts ending in ".techcreator.io".

SELECT
    AVG(event_count)::NUMERIC(10, 4)
        AS avg_events_per_session_techcreator
FROM web_event_sessions
WHERE host LIKE '%.techcreator.io';


-- ---------------------------------------------------------------------------
-- 2. Requested host comparison
-- ---------------------------------------------------------------------------

SELECT
    host,
    COUNT(*) AS session_count,
    SUM(event_count) AS total_events,
    AVG(event_count)::NUMERIC(10, 4)
        AS avg_events_per_session
FROM web_event_sessions
WHERE host IN (
    'zachwilson.techcreator.io',
    'zachwilson.tech',
    'lulu.techcreator.io'
)
GROUP BY host
ORDER BY host;
