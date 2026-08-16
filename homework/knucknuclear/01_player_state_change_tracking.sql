-- =============================================================================
-- Week 4 Analytical Patterns Homework
-- File: 01_player_state_change_tracking.sql
-- Author: Ceasar Jackson
-- Purpose:
--   Track player state changes across seasons using the players, players_scd,
--   and player_seasons tables from Week 1.
--
-- States:
--   New
--   Retired
--   Continued Playing
--   Returned from Retirement
--   Stayed Retired
-- =============================================================================

WITH season_bounds AS (
    SELECT
        MIN(current_season) AS min_season,
        MAX(current_season) AS max_season
    FROM player_seasons
),

seasons AS (
    SELECT generate_series(min_season, max_season) AS current_season
    FROM season_bounds
),

all_players AS (
    SELECT DISTINCT
        player_name
    FROM players

    UNION

    SELECT DISTINCT
        player_name
    FROM players_scd

    UNION

    SELECT DISTINCT
        player_name
    FROM player_seasons
),

player_season_grid AS (
    SELECT
        p.player_name,
        s.current_season
    FROM all_players AS p
    CROSS JOIN seasons AS s
),

player_activity AS (
    SELECT DISTINCT
        player_name,
        current_season
    FROM player_seasons
),

player_activity_flags AS (
    SELECT
        grid.player_name,
        grid.current_season,
        CASE
            WHEN curr.player_name IS NOT NULL THEN 1
            ELSE 0
        END AS is_active_current_season,
        CASE
            WHEN prev.player_name IS NOT NULL THEN 1
            ELSE 0
        END AS was_active_previous_season,
        CASE
            WHEN prior.player_name IS NOT NULL THEN 1
            ELSE 0
        END AS had_any_prior_season
    FROM player_season_grid AS grid
    LEFT JOIN player_activity AS curr
        ON grid.player_name = curr.player_name
       AND grid.current_season = curr.current_season
    LEFT JOIN player_activity AS prev
        ON grid.player_name = prev.player_name
       AND grid.current_season - 1 = prev.current_season
    LEFT JOIN player_activity AS prior
        ON grid.player_name = prior.player_name
       AND prior.current_season < grid.current_season
),

player_state_changes AS (
    SELECT
        player_name,
        current_season,
        CASE
            WHEN is_active_current_season = 1
             AND was_active_previous_season = 0
             AND had_any_prior_season = 0
                THEN 'New'

            WHEN is_active_current_season = 1
             AND was_active_previous_season = 1
                THEN 'Continued Playing'

            WHEN is_active_current_season = 0
             AND was_active_previous_season = 1
                THEN 'Retired'

            WHEN is_active_current_season = 1
             AND was_active_previous_season = 0
             AND had_any_prior_season = 1
                THEN 'Returned from Retirement'

            WHEN is_active_current_season = 0
             AND was_active_previous_season = 0
             AND had_any_prior_season = 1
                THEN 'Stayed Retired'

            ELSE 'Not Yet in League'
        END AS player_state
    FROM player_activity_flags
)

SELECT
    player_name,
    current_season,
    player_state
FROM player_state_changes
WHERE player_state <> 'Not Yet in League'
ORDER BY
    player_name,
    current_season;