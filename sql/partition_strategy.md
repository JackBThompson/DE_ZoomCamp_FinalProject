# Why We Partition and Cluster

## Partitioning by ingestion_date

BigQuery charges by bytes scanned. Without partitioning, every query
scans the entire table regardless of the date range requested.

Example without partitioning:
  SELECT * FROM repo_daily_stats WHERE ingestion_date = '2025-10-01'
  → Scans 90 days of data even though you want 1 day

Example with partitioning:
  Same query → Scans only the 2025-10-01 partition
  → Up to 90x cheaper and faster

## Clustering by language and stars_count

Clustering physically co-locates rows with the same language on disk.
Dashboard queries like "show me top Python repos" skip irrelevant blocks.

Without clustering: BigQuery scans all rows then filters
With clustering: BigQuery skips non-matching blocks entirely

## Rule of thumb used in this project

- Partition on the column most commonly used in WHERE date filters
- Cluster on the columns most commonly used in GROUP BY or dashboard filters
- Never cluster on high-cardinality columns like repo name or id (too many unique values)