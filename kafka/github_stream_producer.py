##Objective: Listens for real-time GitHub webhook events and publishes them to a Kafka topic for downstream streaming ingestion into BigQuery.##

# Import kafka-python, flask, json, os

# Initialize Kafka producer
#   bootstrap_servers from environment variable
#   value_serializer: convert dict to JSON bytes

# Define Kafka topic name: github-events

# Create Flask app to receive GitHub webhook POST requests

# Route: POST /webhook
#   Verify GitHub webhook secret from request headers
#   If signature invalid: return 401
#   Parse JSON payload from request body
#   Extract event type from X-GitHub-Event header
#   Build message dict:
#     event_type, repo name, repo id, sender, timestamp
#   Send message to Kafka topic
#   Log: event type and repo name
#   Return 200 OK

# Route: GET /health
#   Return status: ok (for Docker health checks)

# On startup:
#   Confirm Kafka connection
#   Start Flask app on port 5000