##Objective: Creates curated views and tables in BigQuery for downstream reporting and dashboards.##

# View: top_repos_by_language
#   SELECT language, repo name, stars, forks
#   WHERE ingestion_date = latest partition
#   ORDER BY stars DESC
#   PARTITION BY language

# View: repo_growth_over_time
#   SELECT repo id, date, stars, forks
#   Track delta between each ingestion_date
#   Calculate day-over-day star growth rate

# View: issue_response_time
#   SELECT repo id, avg time between issue opened and first comment
#   GROUP BY language, repo size bucket

# Table: repo_daily_snapshot (materialized)
#   One row per repo per day
#   Slowly changing dimension pattern — keep full history