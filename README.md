# NBA Analytics Pipeline

## Problem Description

NBA fans, analysts, and fantasy sports players have no easy way to track how team performance, player stats, and game trends evolve across a full season. This pipeline solves that by ingesting NBA game and player data daily, transforming it with PySpark, and surfacing it in a Looker Studio dashboard.

The project covers the full data engineering stack: incremental daily loads, raw JSON landing in GCS, batch transformation with Spark, partitioned and clustered tables in BigQuery, and a live dashboard built on top of SQL views.

---

## Architecture

```
NBA API
  → Airflow DAG (orchestration)
  → GCS (raw JSON storage)
  → PySpark (transformation)
  → BigQuery (warehouse + SQL views)
  → Looker Studio (dashboard)
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Cloud | GCP |
| IaC | Terraform |
| Orchestration | Airflow (Docker) |
| Storage | Google Cloud Storage |
| Processing | PySpark |
| Warehouse | BigQuery |
| Dashboard | Looker Studio |

---

## Prerequisites

- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- Docker + Docker Compose
- Python 3.10+
- GCP account with billing enabled

No NBA API key required — `nba_api` is a free library with no authentication.

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/JackBThompson/DE_ZoomCamp_FinalProject.git
cd DE_ZoomCamp_FinalProject
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
cp .env.example .env
# Open .env and fill in your GCP values:
# GCS_BUCKET, GCP_PROJECT_ID, BIGQUERY_DATASET
```

### 4. Authenticate with GCP
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 5. Provision infrastructure (Terraform)
```bash
bash scripts/setup_gcp.sh
```

### 6. Create BigQuery tables
```bash
bq query --use_legacy_sql=false < sql/analytics_models.sql
```

### 7. Ingest raw data locally
> **Important:** NBA.com actively blocks requests from GCP, AWS, and all major cloud providers. Ingestion must be run from your local machine.

```bash
python scripts/ingest_local.py
```
This fetches game and player data from the NBA API and uploads raw JSON directly to GCS.

### 8. Start Airflow on the VM
```bash
gcloud compute ssh airflow-vm --zone=us-east4-a
cd ~/DE_ZoomCamp_FinalProject
docker-compose -f docker/docker-compose.yml up -d
```
Airflow UI is available at `http://localhost:8080` after startup.

### 9. Run the Spark transformation
```bash
spark-submit \
  --packages com.google.cloud.spark:spark-bigquery-with-dependencies_2.12:0.36.1 \
  --jars /home/jackthompson/gcs-connector-hadoop3-latest.jar \
  --conf spark.hadoop.fs.gs.impl=com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem \
  --conf spark.hadoop.fs.AbstractFileSystem.gs.impl=com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS \
  --conf spark.hadoop.google.cloud.auth.service.account.enable=true \
  --conf spark.hadoop.google.cloud.auth.service.account.json.keyfile=/home/jackthompson/DE_ZoomCamp_FinalProject/gcp-key.json \
  spark/transform.py 2026-03-24
```

### 10. Verify data landed in BigQuery
```sql
SELECT COUNT(*) FROM `nba_analytics.game_stats`;
SELECT COUNT(*) FROM `nba_analytics.player_stats`;
```

---

## Local Development (no GCP required)

```bash
docker compose -f docker/docker-compose.yml up -d
```

| Service | URL |
|---|---|
| Airflow | http://localhost:8080 |
| Spark master | http://localhost:8081 |
| MinIO (GCS replacement) | http://localhost:9000 |

---

## Why Tables Are Partitioned and Clustered

Both `game_stats` and `player_stats` are partitioned by `game_date` and clustered by `team_abbreviation` / `player_id`.

- **Partitioning** — dashboard queries always filter by date range. Partitioning means BigQuery only scans the relevant days rather than the entire table, reducing query cost by up to 90%.
- **Clustering** — most filters are team or player specific. Clustering lets BigQuery skip non-matching blocks entirely at no extra cost.

See `sql/partition_strategy.md` for the full explanation with query examples.

---

## Dashboard

View the live Looker Studio dashboard: [LINK]

Built on two tiles:
- **Win/Loss by Team** — categorical bar chart showing wins and losses per team across the 2024-25 season
- **Player Performance Over Time** — time series showing points, rebounds, assists, and plus/minus per game

To recreate the dashboard, follow `dashboard/looker_setup.md`.

---

## Backfilling Historical Data

```bash
python scripts/backfill.py --start_date 2025-01-01 --end_date 2025-10-01
```

---

## Running Tests

```bash
pip install pytest pyspark
pytest tests/
```

---

## Known Limitations

- **NBA.com blocks cloud IPs** — ingestion must run locally via `scripts/ingest_local.py`. This is a documented limitation of `nba_api` affecting GCP, AWS, and Azure since 2020.
- **Player stats limited to 10 players** — the `[:10]` slice in `ingest_local.py` is intentional for demo purposes. Remove it to fetch all active players, but expect ~8 hours of runtime.
- **Rate limiting** — `sleep(1)` between API calls is required to avoid NBA.com rate limits.
- **Free tier VM** — the e2-micro instance may be slow for large Spark jobs. Upgrade to e2-standard-2 for production use.
- **Unofficial API** — `nba_api` wraps undocumented NBA.com endpoints. Data availability depends on NBA.com uptime.


1. Top Scorers by Avg Pointstop_scorersCategorical bar chartPlayer Performance Over Timeplayer_performance_over_timeTemporal line chart