##Objective: Creates curated views and tables in BigQuery for downstream reporting and dashboards.##

-- [SQL] Create Table: game_stats
-- Physically stores the data in BigQuery, rows written by Spark land here
-- Partitioned by GAME_DATE so queries only scan relevant days
-- Clustered by TEAM_ABBREVIATION so filtering by team hits minimal data

-- CREATE TABLE nba_analytics.game_stats
--   Partition by GAME_DATE
--   Cluster by TEAM_ABBREVIATION
--   Columns: SEASON_ID, TEAM_ID, TEAM_ABBREVIATION, TEAM_NAME,
--            GAME_ID, GAME_DATE, MATCHUP, WL, MIN, PTS,
--            FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT,
--            FTM, FTA, FT_PCT, OREB, DREB, REB,
--            AST, STL, BLK, TOV, PF, PLUS_MINUS, ingestion_date

CREATE TABLE IF NOT EXISTS nba_analytics.game_stats (
    season_id         STRING,
    team_id           INT64,
    team_abbreviation STRING,
    team_name         STRING,
    game_id           STRING,
    game_date         DATE,
    matchup           STRING,
    wl                STRING,
    min               INT64,
    pts               INT64,
    fgm               INT64,
    fga               INT64,
    fg_pct            FLOAT64,
    fg3m              INT64,
    fg3a              INT64,
    fg3_pct           FLOAT64,
    ftm               INT64,
    fta               INT64,
    ft_pct            FLOAT64,
    oreb              INT64,
    dreb              INT64,
    reb               INT64,
    ast               INT64,
    stl               INT64,
    blk               INT64,
    tov               INT64,
    pf                INT64,
    plus_minus        FLOAT64,
    ingestion_date    DATE
)
PARTITION BY game_date
CLUSTER BY team_abbreviation;

-- [SQL] Create Table: player_stats
-- Physically stores the data in BigQuery, rows written by Spark land here
-- Partitioned by GAME_DATE
-- Clustered by Player_ID for fast player-specific lookups
-- CREATE TABLE nba_analytics.player_stats
--   Partition by GAME_DATE
--   Cluster by Player_ID
--   Columns: SEASON_ID, Player_ID, Game_ID, GAME_DATE,
--            MATCHUP, WL, MIN, PTS, FGM, FGA, FG_PCT,
--            FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT,
--            OREB, DREB, REB, AST, STL, BLK, TOV,
--            PF, PLUS_MINUS, ingestion_date

CREATE TABLE IF NOT EXISTS nba_analytics.player_stats (
    season_id      STRING,
    player_id      INT64,
    game_id        STRING,
    game_date      DATE,
    matchup        STRING,
    wl             STRING,
    min            INT64,
    pts            INT64,
    fgm            INT64,
    fga            INT64,
    fg_pct         FLOAT64,
    fg3m           INT64,
    fg3a           INT64,
    fg3_pct        FLOAT64,
    ftm            INT64,
    fta            INT64,
    ft_pct         FLOAT64,
    oreb           INT64,
    dreb           INT64,
    reb            INT64,
    ast            INT64,
    stl            INT64,
    blk            INT64,
    tov            INT64,
    pf             INT64,
    plus_minus     FLOAT64,
    ingestion_date DATE
)
PARTITION BY game_date
CLUSTER BY player_id;


-- [SQL] View: top_teams_by_points
--  a saved SELECT query, no data stored, just a lens over the table — every time you query the view it runs the SELECT fresh against the underlying table
--   SELECT TEAM_ABBREVIATION, AVG(PTS) as avg_points
--   FROM game_stats
--   WHERE GAME_DATE = latest partition
--   ORDER BY avg_points DESC

CREATE OR REPLACE VIEW nba_analytics.top_teams_by_points AS
SELECT
    team_abbreviation,
    AVG(pts) AS avg_points
FROM nba_analytics.game_stats
WHERE game_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY team_abbreviation
ORDER BY avg_points DESC;



-- [SQL] View: player_performance_over_time
--  a saved SELECT query, no data stored, just a lens over the table — every time you query the view it runs the SELECT fresh against the underlying table
--   SELECT Player_ID, GAME_DATE, PTS, REB, AST, PLUS_MINUS
--   FROM player_stats
--   WHERE GAME_DATE BETWEEN start_date AND end_date
--   ORDER BY GAME_DATE

CREATE OR REPLACE VIEW nba_analytics.player_performance_over_time AS
SELECT
    player_id,
    game_date,
    pts,
    oreb + dreb AS total_reb,
    ast,
    plus_minus
FROM nba_analytics.player_stats
WHERE game_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY game_date;


-- [SQL] View: win_loss_by_team
--  a saved SELECT query, no data stored, just a lens over the table — every time you query the view it runs the SELECT fresh against the underlying table
--   SELECT TEAM_ABBREVIATION, WL, COUNT(*) as game_count
--   FROM game_stats
--   WHERE GAME_DATE >= current season start
--   GROUP BY TEAM_ABBREVIATION, WL
--   ORDER BY TEAM_ABBREVIATION

CREATE OR REPLACE VIEW nba_analytics.win_loss_by_team AS
SELECT
    team_abbreviation,
    wl,
    COUNT(*) AS game_count
FROM nba_analytics.game_stats
WHERE game_date >= '2024-10-01'
GROUP BY team_abbreviation, wl
ORDER BY team_abbreviation;


-- [SQL] Pipeline health check
--  a saved SELECT query, no data stored, just a lens over the table — every time you query the view it runs the SELECT fresh against the underlying table
--   SELECT ingestion_date, COUNT(*) as records_ingested
--   FROM game_stats
--   WHERE ingestion_date >= 7 days ago
--   GROUP BY ingestion_date
--   ORDER BY ingestion_date DESC
--   If count = 0 for today ingestion failed

CREATE OR REPLACE VIEW nba_analytics.pipeline_health_check AS
SELECT
    ingestion_date,
    COUNT(*) AS records_ingested
FROM nba_analytics.game_stats
WHERE ingestion_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY ingestion_date
ORDER BY ingestion_date DESC;