##Objective: Reads raw GitHub JSON from GCS, flattens nested fields, deduplicates, and writes clean Parquet to BigQuery.##

# Import PySpark, BigQuery connector, sys

# Read execution_date from command line args

# Read raw JSON from GCS path: gs://bucket/raw/github/{execution_date}/repos.json
# Infer schema

# Flatten nested fields:
#   Extract owner.login -> owner_login
#   Extract license.name -> license_name
#   Explode topics array into separate rows

# Clean data:
#   Cast stars, forks, open_issues to integers
#   Parse created_at, updated_at to timestamps
#   Drop rows where repo id is null
#   Deduplicate on repo id

# Add metadata column: ingestion_date = execution_date

# Write to GCS processed zone as Parquet partitioned by ingestion_date

# Load Parquet to BigQuery table: github_analytics.repo_daily_stats
#   Use WRITE_APPEND mode
#   Partition BigQuery table by ingestion_date