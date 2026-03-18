##Objective: Scheduled DAG that pulls data from the GitHub API daily and lands raw JSON to GCS.##

# Import Airflow, requests, GCS hook

# Define DAG: runs daily, start_date = 90 days ago, catchup = True

# Task 1: fetch_repos
#   Build GitHub API URL with query params (language, stars, date)
#   Set Authorization header using token from Airflow connection
#   Loop through paginated responses (check Link header for next page)
#   Collect all repo objects into list
#   Return list via XCom

# Task 2: upload_to_gcs
#   Pull repo list from XCom
#   Convert to newline-delimited JSON
#   Upload to gs://bucket/raw/github/{execution_date}/repos.json
#   Log number of records written

# Task 3: trigger_spark
#   Call Spark submit via BashOperator or SparkSubmitOperator
#   Pass execution_date as argument so Spark knows which partition to process

# Set task order: fetch_repos >> upload_to_gcs >> trigger_spark