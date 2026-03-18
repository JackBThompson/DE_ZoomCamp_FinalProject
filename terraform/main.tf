##Objective: Defines all GCP resources — GCS buckets, BigQuery datasets, GCE VM, and service accounts.##

# Create GCS bucket with two folders: raw/ and processed/
# Create BigQuery dataset called "github_analytics"
# Create GCE e2-micro VM to host Airflow
# Create service account with roles: BigQuery Admin, Storage Admin
# Output service account key to local file for use in other services