##Objective: Stores configurable values like project ID, region, and bucket name so nothing is hardcoded.##

# Define variable: gcp_project_id
# Define variable: gcp_region (default: us-central1)
# Define variable: bucket_name
# Define variable: bigquery_dataset
# Define variable: vm_machine_type (default: e2-micro)

# GCP project ID
variable "project_id" {
  description = "Your GCP project ID"
  type        = string
  default     = "nbapipeline-490916"
}

# GCP region — all resources in the same region to avoid egress costs
variable "region" {
  description = "GCP region for all resources"
  type        = string
  default     = "us-east4"
}

# Path to your service account key file
variable "credentials_file" {
  description = "Path to GCP service account key JSON file"
  type        = string
  default     = "../gcp-key.json"
}

# GCS bucket name
variable "bucket_name" {
  description = "Name of the GCS bucket for raw and processed data"
  type        = string
  default     = "nba-pipeline-jaitfrey-03-26"
}

# BigQuery dataset name
variable "bigquery_dataset" {
  description = "BigQuery dataset name for NBA analytics tables"
  type        = string
  default     = "nba_analytics"
}