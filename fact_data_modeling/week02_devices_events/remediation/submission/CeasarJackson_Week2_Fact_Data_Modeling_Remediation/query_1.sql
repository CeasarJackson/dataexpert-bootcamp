-- =============================================================================
-- DataExpert Intermediate Data Engineering Boot Camp
-- Fact Data Modeling - Week 2
--
-- Query 1: Deduplicate game_details
--
-- Purpose:
--   Remove duplicate player/game/team records from game_details.
--
-- Grain:
--   One row per (game_id, team_id, player_id).
--
-- Validation against the supplied dataset:
--   Original rows:      246,043
--   Deduplicated rows:  245,754
--   Duplicates removed:     289
-- =============================================================================

WITH deduplicated AS (
    SELECT
        gd.*,

        ROW_NUMBER() OVER (
            PARTITION BY
                game_id,
                team_id,
                player_id
            ORDER BY
                game_id,
                team_id,
                player_id
        ) AS row_num

    FROM game_details AS gd
)

SELECT
    game_id,
    team_id,
    team_abbreviation,
    team_city,
    player_id,
    player_name,
    nickname,
    start_position,
    comment,
    min,
    fgm,
    fga,
    fg_pct,
    fg3m,
    fg3a,
    fg3_pct,
    ftm,
    fta,
    ft_pct,
    oreb,
    dreb,
    reb,
    ast,
    stl,
    blk,
    "TO",
    pf,
    pts,
    plus_minus

FROM deduplicated

WHERE row_num = 1;
