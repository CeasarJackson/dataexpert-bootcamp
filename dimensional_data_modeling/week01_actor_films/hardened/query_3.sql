-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Query 3: Actors History SCD Type 2 DDL
--
-- Purpose:
--   Track changes to an actor's quality_class and is_active dimensions
--   without overwriting historical states.
--
-- Grain:
--   One row per actor per continuous dimensional state within an SCD snapshot.
--
-- Temporal fields:
--   start_date   - first year the state became valid
--   end_date     - last year the state remained valid
--   current_year - point-in-time SCD snapshot year
-- =============================================================================

DROP TABLE IF EXISTS actors_history_scd CASCADE;
DROP TYPE IF EXISTS actor_scd_type CASCADE;

CREATE TYPE actor_scd_type AS (
    quality_class quality_class,
    is_active     BOOLEAN,
    start_date    INTEGER,
    end_date      INTEGER
);

CREATE TABLE actors_history_scd (
    actorid       TEXT NOT NULL,
    quality_class quality_class NOT NULL,
    is_active     BOOLEAN NOT NULL,
    start_date    INTEGER NOT NULL,
    end_date      INTEGER NOT NULL,
    current_year  INTEGER NOT NULL,

    PRIMARY KEY (
        actorid,
        start_date,
        current_year
    ),

    CHECK (end_date >= start_date)
);
