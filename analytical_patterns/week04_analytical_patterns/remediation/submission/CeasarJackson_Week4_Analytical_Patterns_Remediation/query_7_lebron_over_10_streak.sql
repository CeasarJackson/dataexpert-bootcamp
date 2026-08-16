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
-- Remediation Output: Query 7
-- Longest LeBron James streak scoring more than 10 points
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Question 2:
-- How many games in a row did LeBron James score over 10 points?
-- -----------------------------------------------------------------------------

WITH lebron_games AS (
    SELECT
        gd.player_id,
        gd.player_name,
        gd.game_id,
        g.game_date_est,
        COALESCE(gd.pts, 0) AS points,
        CASE
            WHEN COALESCE(gd.pts, 0) > 10 THEN 1
            ELSE 0
        END AS scored_over_10
    FROM game_details AS gd
    INNER JOIN games AS g
        ON gd.game_id = g.game_id
    WHERE gd.player_name = 'LeBron James'
),

lebron_streak_groups AS (
    SELECT
        *,
        SUM(
            CASE
                WHEN scored_over_10 = 0 THEN 1
                ELSE 0
            END
        ) OVER (
            ORDER BY game_date_est, game_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS streak_group
    FROM lebron_games
),

lebron_positive_streaks AS (
    SELECT
        player_name,
        streak_group,
        MIN(game_date_est) AS streak_start_date,
        MAX(game_date_est) AS streak_end_date,
        COUNT(*) AS consecutive_games_over_10_points
    FROM lebron_streak_groups
    WHERE scored_over_10 = 1
    GROUP BY
        player_name,
        streak_group
)

SELECT
    player_name,
    streak_start_date,
    streak_end_date,
    consecutive_games_over_10_points
FROM lebron_positive_streaks
ORDER BY consecutive_games_over_10_points DESC
LIMIT 1;
