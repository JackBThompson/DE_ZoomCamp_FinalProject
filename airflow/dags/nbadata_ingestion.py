##Objective: Scheduled DAG that pulls NBA game data daily and lands raw JSON to GCS.##

import pandas as pd
import json
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from nba_api.stats.endpoints import LeagueGameFinder, PlayerGameLog
from nba_api.stats.static import players
from datetime import datetime, timedelta
from time import sleep

# Define DAG: runs daily, start_date = 90 days ago, catchup = True
dag = DAG(
    dag_id='nba_ingestion',
    schedule_interval='@daily',
    start_date=datetime.now() - timedelta(days=90),
    catchup=True
)

# Sanity Check
# 1. from nba_api.stats.endpoints import leaguegamefinder
# 2. games = leaguegamefinder.LeagueGameFinder()
# 3. print(games.get_data_frames()[0].head())
# 4. print(games.get_data_frames()[0].columns.tolist())


# Task 1: fetch_games
#   Call LeagueGameFinder with date_from and date_to = execution_date
#   Extract DataFrame from response using get_data_frames()[0]
#   Add sleep(1) to avoid rate limiting NBA.com
#   Convert DataFrame to list of dicts
#   Return list via XCom

def fetch_games(**context):
    execution_date = context['ds']

    games = LeagueGameFinder(
        date_from_nullable=execution_date,
        date_to_nullable=execution_date
    )

    sleep(1)

    df = games.get_data_frames()[0]
    records = df.to_dict(orient='records')
    context['ti'].xcom_push(key='games', value=records)


# Task 2: fetch_player_stats
#   Loop through active player IDs
#   Call PlayerGameLog for each player with season = current season
#   Add sleep(1) between each call to avoid rate limiting
#   Collect all player stat rows into list
#   Return list via XCom

def fetch_player_stats(**context):
    current_season = '2024-25'

    active_players = players.get_active_players()

    all_stats = []

    for player in active_players:
        player_id = player['id']

        player_log = PlayerGameLog(
            player_id=player_id,
            season=current_season
        )

        sleep(1)

        df = player_log.get_data_frames()[0]
        df = df.fillna(0)
        records = df.to_dict(orient='records')
        all_stats.extend(records)

    context['ti'].xcom_push(key='player_stats', value=all_stats)


# Task 3: upload_to_gcs
#   Pull games list and player stats list from XCom
#   Convert each to newline-delimited JSON
#   Upload games to gs://bucket/raw/nba/{execution_date}/games.json
#   Upload player stats to gs://bucket/raw/nba/{execution_date}/player_stats.json
#   Log number of records written for each

def upload_to_gcs(**context):
    execution_date = context['ds']

    games = context['ti'].xcom_pull(key='games', task_ids='fetch_games')
    player_stats = context['ti'].xcom_pull(key='player_stats', task_ids='fetch_player_stats')

    games_json = '\n'.join([json.dumps(record) for record in games])
    stats_json = '\n'.join([json.dumps(record) for record in player_stats])

    hook = GCSHook()

    hook.upload(
        bucket_name='nba-pipeline-jaitfrey-03-26',
        object_name=f'raw/nba/{execution_date}/games.json',
        data=games_json,
        mime_type='application/json'
    )

    hook.upload(
        bucket_name='nba-pipeline-jaitfrey-03-26',
        object_name=f'raw/nba/{execution_date}/player_stats.json',
        data=stats_json,
        mime_type='application/json'
    )

    print(f'Uploaded {len(games)} game records')
    print(f'Uploaded {len(player_stats)} player stat records')


# Task 4: trigger_spark
#   Call Spark submit via BashOperator
#   Pass execution_date as argument so Spark knows which partition to process

trigger_spark = BashOperator(
    task_id='trigger_spark',
    bash_command='spark-submit /home/codespace/DE_ZoomCamp_FinalProject/spark/transform.py {{ ds }}',
    dag=dag
)

fetch_games_task = PythonOperator(
    task_id='fetch_games',
    python_callable=fetch_games,
    dag=dag
)

fetch_player_stats_task = PythonOperator(
    task_id='fetch_player_stats',
    python_callable=fetch_player_stats,
    dag=dag
)

upload_to_gcs_task = PythonOperator(
    task_id='upload_to_gcs',
    python_callable=upload_to_gcs,
    dag=dag
)

# Task order
fetch_games_task >> fetch_player_stats_task >> upload_to_gcs_task >> trigger_spark