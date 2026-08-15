-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Hardened Query 3: Actors History SCD Type 2 DDL
--
-- Purpose:
--   Track changes to quality_class and is_active while preserving historical
--   states and strengthening schema-level validation and access paths.
--
-- Grain:
--   One row per actor per continuous state within an SCD snapshot.
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

    CONSTRAINT actors_history_scd_pkey
        PRIMARY KEY (
            actorid,
            start_date,
            current_year
        ),

    CONSTRAINT actors_history_scd_valid_date_range
        CHECK (end_date >= start_date)
);

CREATE INDEX idx_actors_history_scd_actor_snapshot
    ON actors_history_scd (
        actorid,
        current_year
    );

CREATE INDEX idx_actors_history_scd_actor_interval
    ON actors_history_scd (
        actorid,
        start_date,
        end_date
    );
