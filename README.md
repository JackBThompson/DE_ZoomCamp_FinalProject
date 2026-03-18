# GitHub Repository Analytics Pipeline

## Problem Description

Engineering teams and open source maintainers have no easy way to track
how repository popularity, language trends, and community engagement
change over time across GitHub. This pipeline solves that by:

- Ingesting GitHub repository data daily via the REST API
- Tracking star growth, fork counts, and issue trends over time
- Making the data queryable in BigQuery and visual in Looker Studio

This project demonstrates a production-grade data engineering pipeline
handling real-world challenges: API pagination, nested JSON, schema drift,
incremental loading, and cost-efficient data warehousing.

---

## Architecture

GitHub API → Airflow (orchestration) → GCS (raw storage)
         → Spark (transformation) → BigQuery (warehouse)
         → Looker Studio (dashboard)

Kafka stream layer runs in parallel for real-time repo event ingestion.

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
| Streaming | Kafka |
| Dashboard | Looker Studio |

---

## Prerequisites

Install these before starting:
- gcloud CLI: https://cloud.google.com/sdk/docs/install
- Terraform: https://developer.hashicorp.com/terraform/install
- Docker + Docker Compose
- Python 3.10+
- A GCP account with billing enabled
- A GitHub personal access token

---

## Setup Instructions

### 1. Clone the repo
git clone https://github.com/yourusername/github-pipeline.git
cd github-pipeline

### 2. Set environment variables
cp .env.example .env
# Edit .env and fill in:
#   GITHUB_TOKEN=your_token_here
#   GCP_PROJECT_ID=your_project_id
#   GCS_BUCKET=your_bucket_name

### 3. Authenticate with GCP
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

### 4. Provision infrastructure
bash scripts/setup_gcp.sh
# This runs terraform init, plan, and apply
# Takes ~3 minutes
# Outputs: VM IP, bucket name, BigQuery dataset ID

### 5. Create BigQuery tables
bq query --use_legacy_sql=false < sql/analytics_models.sql

### 6. Start Airflow
docker compose -f docker/docker-compose.yml up -d
# Access UI at http://localhost:8080
# Username: airflow / Password: airflow

### 7. Enable the DAG
# In Airflow UI, find "github_ingestion" and toggle it ON
# It will backfill the last 90 days automatically

### 8. Start Kafka (optional, for streaming)
docker compose -f kafka/docker-compose.kafka.yml up -d
python kafka/github_stream_producer.py

---

## Local Development (no GCP required)

docker compose -f docker/docker-compose.yml up -d
# MinIO runs at localhost:9000 (replaces GCS locally)
# Airflow runs at localhost:8080
# Spark master runs at localhost:8081

---

## Dashboard

View the live Looker Studio dashboard here: [LINK]

To recreate it yourself, follow: dashboard/looker_setup.md

---

## Partitioning & Clustering Strategy

All BigQuery tables are partitioned by ingestion_date and clustered
by language/stars. See sql/partition_strategy.md for full explanation.

Short version: partitioning reduces query cost by up to 90% by only
scanning the date ranges you actually need. Clustering speeds up
dashboard filters on language without additional cost.

---

## Running Tests

pip install pytest pyspark
pytest tests/

---

## Backfilling Historical Data

python scripts/backfill.py --start_date 2025-01-01 --end_date 2025-10-01

---

## Project Structure

[paste final repo structure here]

---

## Known Limitations

- GitHub API rate limit: 5,000 requests/hour. Large backfills may hit this.
  The DAG handles this with retry logic and exponential backoff.
- Free GCP tier: e2-micro VM may be slow for large Spark jobs.
  Upgrade to e2-standard-2 for production use.