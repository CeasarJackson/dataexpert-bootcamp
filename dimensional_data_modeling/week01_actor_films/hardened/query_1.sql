-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Hardened Query 1: Actors cumulative dimension DDL
--
-- Purpose:
--   Define the cumulative actors dimension with stronger schema constraints
--   while preserving the business behavior of the graded implementation.
--
-- Grain:
--   One row per actorid per current_year.
--
-- Hardening:
--   - Required business attributes are NOT NULL.
--   - films defaults to an empty film_struct array.
--   - Primary key protects actor/year uniqueness.
--   - Supporting index favors annual snapshot access patterns.
--
-- Preserved behavior:
--   - rating remains REAL during this phase.
--   - quality_class thresholds are unchanged.
-- =============================================================================

DROP TABLE IF EXISTS actors CASCADE;
DROP TYPE IF EXISTS film_struct CASCADE;
DROP TYPE IF EXISTS quality_class CASCADE;

CREATE TYPE film_struct AS (
    film   TEXT,
    votes  INTEGER,
    rating REAL,
    filmid TEXT
);

CREATE TYPE quality_class AS ENUM (
    'bad',
    'average',
    'good',
    'star'
);

CREATE TABLE actors (
    actor         TEXT NOT NULL,
    actorid       TEXT NOT NULL,
    films         film_struct[] NOT NULL
                      DEFAULT ARRAY[]::film_struct[],
    quality_class quality_class NOT NULL,
    is_active     BOOLEAN NOT NULL,
    current_year  INTEGER NOT NULL,

    CONSTRAINT actors_pkey
        PRIMARY KEY (actorid, current_year)
);

CREATE INDEX idx_actors_current_year_actorid
    ON actors (current_year, actorid);
