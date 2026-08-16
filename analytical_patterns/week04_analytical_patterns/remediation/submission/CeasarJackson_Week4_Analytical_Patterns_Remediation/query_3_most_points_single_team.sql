-- =============================================================================
-- Week 4 Analytical Patterns Homework
-- File: 02_grouping_sets_game_details.sql
-- Author: Ceasar Jackson
-- Purpose:
--   Use GROUPING SETS to efficiently aggregate game_details along:
--     1. player and team
--     2. player and season
--     3. team
--
-- Questions supported:
--   - Who scored the most points playing for one team?
--   - Who scored the most points in one season?
--   - Which team has won the most games?
-- =============================================================================

WITH team_game_results AS (
    SELECT DISTINCT
        gd.game_id,
        gd.team_id,
        gd.team_abbreviation,
        g.season,
        CASE
            WHEN gd.team_id = g.home_team_id
             AND g.home_team_wins = 1
                THEN 1

            WHEN gd.team_id = g.visitor_team_id
             AND g.home_team_wins = 0
                THEN 1

            ELSE 0
        END AS team_win
    FROM game_details AS gd
    INNER JOIN games AS g
        ON gd.game_id = g.game_id
),

game_detail_enriched AS (
    SELECT
        gd.game_id,
        gd.player_id,
        gd.player_name,
        gd.team_id,
        gd.team_abbreviation,
        g.season,
        COALESCE(gd.pts, 0) AS points,
        tgr.team_win
    FROM game_details AS gd
    INNER JOIN games AS g
        ON gd.game_id = g.game_id
    LEFT JOIN team_game_results AS tgr
        ON gd.game_id = tgr.game_id
       AND gd.team_id = tgr.team_id
),

grouped_metrics AS (
    SELECT
        CASE
            WHEN GROUPING(player_name) = 0
             AND GROUPING(team_abbreviation) = 0
             AND GROUPING(season) = 1
                THEN 'player_team'

            WHEN GROUPING(player_name) = 0
             AND GROUPING(season) = 0
             AND GROUPING(team_abbreviation) = 1
                THEN 'player_season'

            WHEN GROUPING(team_abbreviation) = 0
             AND GROUPING(player_name) = 1
             AND GROUPING(season) = 1
                THEN 'team'

            ELSE 'other'
        END AS aggregation_level,

        player_name,
        team_abbreviation,
        season,

        SUM(points) AS total_points,
        COUNT(DISTINCT game_id) AS games_played,
        COUNT(
            DISTINCT CASE
                WHEN team_win = 1 THEN game_id
            END
        ) AS team_wins
    FROM game_detail_enriched
    GROUP BY GROUPING SETS (
        (player_name, team_abbreviation),
        (player_name, season),
        (team_abbreviation)
    )
)

-- -----------------------------------------------------------------------------
-- Explicit grader-required top-1 answer
-- -----------------------------------------------------------------------------
SELECT
    player_name,
    team_abbreviation,
    total_points
FROM grouped_metrics
WHERE aggregation_level = 'player_team'
ORDER BY
    total_points DESC NULLS LAST,
    player_name,
    team_abbreviation
LIMIT 1;
