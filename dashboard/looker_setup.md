# Looker Studio Dashboard

## Live Dashboard Link
[paste public Looker Studio URL here]

## Dashboard Overview
This dashboard tracks GitHub repository trends over time using data
ingested daily from the GitHub REST API and stored in BigQuery.

## Charts

Chart 1: Top Repositories by Stars
  What it shows: highest starred repos across all languages
  How to use: filter by language dropdown to narrow results

Chart 2: Language Distribution
  What it shows: breakdown of repos by programming language
  How to use: compare which languages dominate the dataset

Chart 3: Daily Star Growth
  What it shows: day-over-day change in stars per repo
  How to use: identify trending repos before they go viral

Chart 4: Total Repos Tracked (scorecard)
  What it shows: running count of unique repos in the dataset

## Filters Available
  Date range: filters all charts by ingestion_date partition
  Language: filters all charts by programming language

## Screenshot
See screenshots/dashboard_preview.png