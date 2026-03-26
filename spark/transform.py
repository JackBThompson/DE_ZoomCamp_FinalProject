##Objective: Reads raw NBA JSON from GCS, cleans and transforms game and player stats, and writes to BigQuery.##
## Python holds it all together - PySpark handles reading/writing, and Spark SQL handles the transformation logic  ##

# Import PySpark, BigQuery connector, sys
import pyspark
from pyspark.sql import SparkSession
from pyspark.sql import types
from pyspark.sql.functions import col, to_date, lit
from datetime import datetime
import os
import sys

# [PYTHON] Read execution_date from command line args
#   Airflow passes execution_date when it calls spark-submit

execution_date = sys.argv[1]

bucket = os.environ.get('GCS_BUCKET')
project = os.environ.get('GCP_PROJECT_ID')
dataset = os.environ.get('BIGQUERY_DATASET')


# [PYTHON] Create Spark session with BigQuery and GCS connectors
spark = SparkSession.builder \
    .appName('nba_transform') \
    .config('spark.jars', '/home/jackthompson/spark-bigquery-latest_2.12.jar') \
    .config('spark.hadoop.fs.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem') \
    .config('spark.hadoop.fs.AbstractFileSystem.gs.impl', 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS') \
    .config('spark.hadoop.google.cloud.auth.service.account.enable', 'true') \
    .config('spark.hadoop.google.cloud.auth.service.account.json.keyfile', '/home/jackthompson/DE_ZoomCamp_FinalProject/gcp-key.json') \
    .getOrCreate()

spark.conf.set('temporaryGcsBucket', bucket)

# [PYSPARK] Read raw games JSON from GCS path: gs://bucket/raw/nba/{execution_date}/games.json
# [PYSPARK] Read raw player stats JSON from GCS path: gs://bucket/raw/nba/{execution_date}/player_stats.json

df_games = spark.read.json(f'gs://{bucket}/raw/nba/{execution_date}/games.json')
df_stats = spark.read.json(f'gs://{bucket}/raw/nba/{execution_date}/player_stats.json')

# [PYSPARK] Clean games data:
#   Cast GAME_DATE string to date type
#   Cast PTS, REB, AST, STL, BLK, TOV to integers
#   Cast FG_PCT, FG3_PCT, FT_PCT, PLUS_MINUS to floats
#   Drop rows where GAME_ID is null
#   Deduplicate on GAME_ID and TEAM_ID

df_games = df_games \
    .withColumn('GAME_DATE', to_date(col('GAME_DATE'), 'yyyy-MM-dd')) \
    .withColumn('PTS', col('PTS').cast(types.IntegerType())) \
    .withColumn('REB', col('REB').cast(types.IntegerType())) \
    .withColumn('AST', col('AST').cast(types.IntegerType())) \
    .withColumn('STL', col('STL').cast(types.IntegerType())) \
    .withColumn('BLK', col('BLK').cast(types.IntegerType())) \
    .withColumn('TOV', col('TOV').cast(types.IntegerType())) \
    .withColumn('TEAM_ID', col('TEAM_ID').cast(types.IntegerType())) \
    .withColumn('FG_PCT', col('FG_PCT').cast(types.FloatType())) \
    .withColumn('FG3_PCT', col('FG3_PCT').cast(types.FloatType())) \
    .withColumn('FT_PCT', col('FT_PCT').cast(types.FloatType())) \
    .withColumn('PLUS_MINUS', col('PLUS_MINUS').cast(types.FloatType())) \
    .filter(col('GAME_ID').isNotNull()) \
    .dropDuplicates(['GAME_ID', 'TEAM_ID'])

df_games = df_games.toDF(*[c.lower() for c in df_games.columns])

# [PYSPARK] Clean player stats data:
#   Cast GAME_DATE string to date type
#   Cast PTS, REB, AST, STL, BLK, TOV, MIN to integers
#   Cast FG_PCT, FG3_PCT, FT_PCT, PLUS_MINUS to floats
#   Drop rows where Player_ID is null
#   Deduplicate on Player_ID and Game_ID

df_stats = df_stats \
    .withColumn('GAME_DATE', to_date(col('GAME_DATE'), 'yyyy-MM-dd')) \
    .withColumn('PTS', col('PTS').cast(types.IntegerType())) \
    .withColumn('REB', col('REB').cast(types.IntegerType())) \
    .withColumn('AST', col('AST').cast(types.IntegerType())) \
    .withColumn('STL', col('STL').cast(types.IntegerType())) \
    .withColumn('BLK', col('BLK').cast(types.IntegerType())) \
    .withColumn('TOV', col('TOV').cast(types.IntegerType())) \
    .withColumn('MIN', col('MIN').cast(types.IntegerType())) \
    .withColumn('FG_PCT', col('FG_PCT').cast(types.FloatType())) \
    .withColumn('FG3_PCT', col('FG3_PCT').cast(types.FloatType())) \
    .withColumn('FT_PCT', col('FT_PCT').cast(types.FloatType())) \
    .withColumn('PLUS_MINUS', col('PLUS_MINUS').cast(types.FloatType())) \
    .filter(col('Player_ID').isNotNull()) \
    .dropDuplicates(['Player_ID', 'Game_ID'])

df_stats = df_stats.toDF(*[c.lower() for c in df_stats.columns])

# [PYTHON] Add metadata column: ingestion_date = execution_date to both DataFrames

df_games = df_games.withColumn('ingestion_date', lit(execution_date))
df_stats = df_stats.withColumn('ingestion_date', lit(execution_date))

# [PYSPARK] Write games to GCS processed zone as Parquet partitioned by GAME_DATE
# [PYSPARK] Write player stats to GCS processed zone as Parquet partitioned by GAME_DATE

df_games.write.partitionBy('GAME_DATE') \
    .mode('append') \
    .parquet(f'gs://{bucket}/processed/nba/{execution_date}/games/')

df_stats.write.partitionBy('GAME_DATE') \
    .mode('append') \
    .parquet(f'gs://{bucket}/processed/nba/{execution_date}/player_stats/')

# [SPARK SQL] Load games Parquet to BigQuery table: nba_analytics.game_stats
#   Use WRITE_APPEND mode
#   Partition BigQuery table by GAME_DATE
#   Cluster by TEAM_ABBREVIATION


df_games.write.format('bigquery') \
    .option('table', f'{project}.{dataset}.game_stats') \
    .option('partitionField', 'GAME_DATE') \
    .option('clusteredFields', 'TEAM_ABBREVIATION') \
    .mode('append') \
    .save()


# [SPARK SQL] Load player stats Parquet to BigQuery table: nba_analytics.player_stats
#   Use WRITE_APPEND mode
#   Partition BigQuery table by GAME_DATE
#   Cluster by Player_ID

df_stats.write.format('bigquery') \
    .option('table', f'{project}.{dataset}.player_stats') \
    .option('partitionField', 'GAME_DATE') \
    .option('clusteredFields', 'Player_ID') \
    .mode('append') \
    .save()

spark.stop()