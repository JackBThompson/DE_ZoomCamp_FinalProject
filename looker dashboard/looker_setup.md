# Looker Studio Dashboard

## Live Dashboard Link
https://lookerstudio.google.com/u/0/reporting/26200b1d-e0c6-4919-9eee-d55676aa994b/page/YsZtF
https://lookerstudio.google.com/u/0/reporting/787022c9-e531-44ce-9291-e9183fe5bf2e/page/dRZtF

Looker Studio Dashboard Setup
Connect to BigQuery

Go to lookerstudio.google.com → Create → Report
Add data → BigQuery → NBApipeline → nba_analytics


## Tile 1 — Top Scorers by Average Points (Bar Chart)

Add data source: top_scorers
Insert → Vertical bar chart
Dimension: player_name
Metric: avg_pts (aggregation: Average)
Sort: avg_pts descending
Add title: "Top Scorers by Average Points — 2024-25 Season"


## Tile 2 — Player Performance Over Time (Time Series)

Add data source: player_performance_over_time
Insert → Time series chart
Dimension - X axis: game_date (granularity: Year Month)
Breakdown dimension: player_name
Metric - Y axis: pts (aggregation: Average)
Add filter: game_date Between 2024-10-01 and 2025-04-13
Add title: "Player Performance by Points — 2024-25 Season"