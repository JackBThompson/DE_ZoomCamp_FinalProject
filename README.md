# NBA Analytics Pipeline

## Problem Description

NBA fans, analysts, and fantasy sports players have no easy way to track how player performance and game trends evolve across a full season. This pipeline solves that by ingesting NBA game and player data, transforming it with PySpark, and surfacing it in a Looker Studio dashboard.

The project covers the full data engineering stack: raw JSON landing in GCS, batch transformation with Spark, partitioned and clustered tables in BigQuery, and a live dashboard built on top of SQL views.

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
python3 scripts/ingest_local.py
```
This fetches full 2024-25 season game and player data for 10 NBA stars and uploads raw JSON directly to GCS.

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
  spark/transform.py 2025-04-13
```

### 10. Verify data landed in BigQuery
```sql
SELECT COUNT(*) FROM `nba_analytics.game_stats`;
SELECT COUNT(*) FROM `nba_analytics.player_stats`;
```

---

## Why Tables Are Partitioned and Clustered

Both `game_stats` and `player_stats` are partitioned by `game_date` and clustered by `team_abbreviation` / `player_id`.

- **Partitioning** — dashboard queries always filter by date range. Partitioning means BigQuery only scans the relevant days rather than the entire table, reducing query cost by up to 90%.
- **Clustering** — most filters are team or player specific. Clustering lets BigQuery skip non-matching blocks entirely at no extra cost.

---

## Dashboard

View the live Looker Studio dashboard:
https://lookerstudio.google.com/u/0/reporting/787022c9-e531-44ce-9291-e9183fe5bf2e/page/dRZtF

Built on two tiles:
- **Top Scorers by Average Points** — categorical bar chart ranking 10 NBA stars by avg points per game across the 2024-25 season
- **Player Performance Over Time** — time series showing average points per player per month across the 2024-25 season

To recreate the dashboard, follow `dashboard/looker_setup.md`.

---

## Running Tests

```bash
pip install pytest pyspark
pytest tests/
```

---

## Known Limitations

- **NBA.com blocks cloud IPs** — ingestion must run locally via `scripts/ingest_local.py`. This is a documented limitation of `nba_api` affecting GCP, AWS, and Azure since 2020.
- **Rate limiting** — `sleep(1)` between API calls is required to avoid NBA.com rate limits.
- **Unofficial API** — `nba_api` wraps undocumented NBA.com endpoints. Data availability depends on NBA.com uptime.
