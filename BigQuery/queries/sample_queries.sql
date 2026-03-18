##Objective: Provides ready-to-run example queries that demonstrate the value of the dataset and verify the pipeline is working correctly.##

# Query 1: Top 10 most starred repos today
#   Filter to today's partition only
#   Sort by star count descending
#   Return top 10 results

# Query 2: Fastest growing repos this week
#   Look at the last 7 days of star growth data
#   Sum the daily star delta per repo
#   Return the top 10 biggest gainers

# Query 3: Language breakdown
#   Filter to today's partition
#   Count how many repos exist per language
#   Calculate average stars per language
#   Sort by most popular language first

# Query 4: Repos that crossed 1000 stars this month
#   Filter to current month only
#   Only include repos with at least 1000 stars
#   Sort by earliest date first to see who crossed the threshold first

# Query 5: Pipeline health check
#   Count how many records were ingested each day for the last 7 days
#   Sort most recent day first
#   If today shows zero records the ingestion DAG failed