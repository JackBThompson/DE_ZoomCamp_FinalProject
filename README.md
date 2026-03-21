# NBA Analytics Pipeline

## Problem Description

NBA fans, analysts, and fantasy sports players have no easy way to track
how team performance, player stats, and game trends change over time
across a full season. This pipeline solves that by:

- Ingesting NBA game and player data daily via the nba_api library
- Tracking points, rebounds, assists, shooting efficiency, and plus/minus over time
- Making the data queryable in BigQuery and visual in Looker Studio

This project demonstrates a production-grade data engineering pipeline
handling real-world challenges: incremental daily loads, nested data
structures, deduplication, and cost-efficient data warehousing.

---

## Architecture

NBA API → Airflow (orchestration) → GCS (raw storage)
       → Spark (transformation) → BigQuery (warehouse)
       → Looker Studio (dashboard)

---

## Tech Stack

| Layer | Tool |
|---|---|
| Cloud | GCP |
| IaC | Terraform |
| Orchestration | Airflow |
| Storage | GCS |
| Processing | PySpark |
| Warehouse | BigQuery |
| Dashboard | Looker Studio |

---

## Prerequisites

Install these before starting:
- gcloud CLI: https://cloud.google.com/sdk/docs/install
- Terraform: https://developer.hashicorp.com/terraform/install
- Docker + Docker Compose
- Python 3.10+
- A GCP account with billing enabled

No API key required — nba_api is a free library with no authentication needed.

---

## Setup Instructions

### 1. Clone the repo
git clone https://github.com/JackBThompson/DE_ZoomCamp_FinalProject.git
cd DE_ZoomCamp_FinalProject

### 2. Install dependencies
pip install -r requirements.txt

### 3. Set environment variables
cp .env.example .env
# Edit .env and fill in:
#   GCP_PROJECT_ID=your_project_id
#   GCS_BUCKET=your_bucket_name

### 4. Authenticate with GCP
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

### 5. Provision infrastructure
bash scripts/setup_gcp.sh
# This runs terraform init, plan, and apply
# Takes ~3 minutes
# Outputs: VM IP, bucket name, BigQuery dataset ID

### 6. Create BigQuery tables
bq query --use_legacy_sql=false < sql/analytics_models.sql

### 7. Start Airflow
docker compose -f docker/docker-compose.yml up -d
# Access UI at http://localhost:8080
# Username: airflow / Password: airflow

### 8. Enable the DAG
# In Airflow UI, find "nbaData_ingestion" and toggle it ON
# It will backfill the last 90 days automatically

---

## Local Development (no GCP required)

docker compose -f docker/docker-compose.yml up -d
# MinIO runs at localhost:9000 (replaces GCS locally)
# Airflow runs at localhost:8080
# Spark master runs at localhost:8081

---

## Verifying the Pipeline

After enabling the DAG, verify each step:

### Check GCS — raw data should appear here
gs://your_bucket/raw/nba/{date}/games.json
gs://your_bucket/raw/nba/{date}/player_stats.json

### Check BigQuery — run this to confirm data loaded
SELECT COUNT(*) FROM nba_analytics.game_stats
WHERE GAME_DATE = CURRENT_DATE()

### Check Airflow — all tasks should show green
http://localhost:8080

---

## Why We Partition and Cluster

Tables are partitioned by GAME_DATE and clustered by TEAM_ABBREVIATION because:

- Most dashboard queries filter by date range — partitioning means only
  relevant days are scanned, reducing query cost by up to 90%
- Most filters are by team — clustering means BigQuery skips
  non-matching blocks entirely without extra cost

See sql/partition_strategy.md for the full explanation with examples.

---

## Dashboard

View the live Looker Studio dashboard here: [LINK]

To recreate it yourself, follow: dashboard/looker_setup.md

### Dashboard Preview
[screenshot goes here]

Chart 1: Team points per game over the season (time series)
Chart 2: Win/Loss distribution by team (categorical)

---

## Partitioning & Clustering Strategy

All BigQuery tables are partitioned by GAME_DATE and clustered
by TEAM_ABBREVIATION. See sql/partition_strategy.md for full explanation.

Short version: partitioning reduces query cost by up to 90% by only
scanning the date ranges you actually need. Clustering speeds up
dashboard filters by team without additional cost.

---

## Running Tests

pip install pytest pyspark
pytest tests/

---

## Backfilling Historical Data

python scripts/backfill.py --start_date 2025-01-01 --end_date 2025-10-01

---

## Known Limitations

- nba_api rate limit: sleep(1) between calls prevents NBA.com from blocking requests.
  The DAG handles this automatically.
- Free GCP tier: e2-micro VM may be slow for large Spark jobs.
  Upgrade to e2-standard-2 for production use.
- nba_api is an unofficial wrapper around NBA.com endpoints.
  Data availability depends on NBA.com uptime.