-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Dimensional Data Modeling - Week 1
--
-- Query 1: Actors cumulative dimension DDL
--
-- Purpose:
--   Define the actor cumulative dimension and supporting PostgreSQL types.
--
-- Grain:
--   One row per actor per current_year.
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
    actor         TEXT,
    actorid       TEXT NOT NULL,
    films         film_struct[],
    quality_class quality_class,
    is_active     BOOLEAN,
    current_year  INTEGER NOT NULL,

    PRIMARY KEY (actorid, current_year)
);
