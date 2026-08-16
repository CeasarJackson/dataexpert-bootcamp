-- =============================================================================
-- Week 4 Analytical Patterns Homework
-- File: 03_window_functions_game_details.sql
-- Author: Ceasar Jackson
-- Purpose:
--   Use window functions on game_details and games to answer:
--     1. What is the most games a team has won in a 90-game stretch?
--     2. How many games in a row did LeBron James score over 10 points?
-- =============================================================================

-- =============================================================================
-- Remediation Output: Query 6
-- Most games a team has won in a complete 90-game stretch
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Question 1:
-- What is the most games a team has won in a 90-game stretch?
-- -----------------------------------------------------------------------------

WITH team_games AS (
    SELECT DISTINCT
        gd.team_id,
        gd.team_abbreviation,
        gd.game_id,
        g.game_date_est,
        CASE
            WHEN gd.team_id = g.home_team_id
             AND g.home_team_wins = 1
                THEN 1

            WHEN gd.team_id = g.visitor_team_id
             AND g.home_team_wins = 0
                THEN 1

            ELSE 0
        END AS is_win
    FROM game_details AS gd
    INNER JOIN games AS g
        ON gd.game_id = g.game_id
),

team_rolling_90_games AS (
    SELECT
        team_id,
        team_abbreviation,
        game_id,
        game_date_est,
        is_win,
        ROW_NUMBER() OVER (
            PARTITION BY team_id
            ORDER BY game_date_est, game_id
        ) AS team_game_number,
        SUM(is_win) OVER (
            PARTITION BY team_id
            ORDER BY game_date_est, game_id
            ROWS BETWEEN 89 PRECEDING AND CURRENT ROW
        ) AS wins_in_90_game_stretch
    FROM team_games
)

SELECT
    team_id,
    team_abbreviation,
    game_id AS ending_game_id,
    game_date_est AS ending_game_date,
    wins_in_90_game_stretch
FROM team_rolling_90_games
WHERE team_game_number >= 90
ORDER BY wins_in_90_game_stretch DESC
LIMIT 1;
