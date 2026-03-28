##Objective: Scheduled DAG that pulls NBA game data daily and lands raw JSON to GCS.##

import pandas as pd
import json
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from nba_api.stats.endpoints import LeagueGameFinder, PlayerGameLog
from nba_api.stats.static import players
from datetime import datetime, timedelta
from time import sleep
 
dag = DAG(
    dag_id='nba_ingestion',
    schedule_interval='@daily',
    start_date=datetime.now() - timedelta(days=90),
    catchup=False
)
 
def fetch_games(**context):
    execution_date = context['ds']
    bucket = os.environ.get('GCS_BUCKET')
 
    games = LeagueGameFinder(
        date_from_nullable=execution_date,
        date_to_nullable=execution_date,
        timeout=60
    )
 
    sleep(1)
    df = games.get_data_frames()[0]
    records = df.to_dict(orient='records')
    games_json = '\n'.join([json.dumps(r) for r in records])
 
    hook = GCSHook()
    hook.upload(
        bucket_name=bucket,
        object_name=f'raw/nba/{execution_date}/games.json',
        data=games_json,
        mime_type='application/json'
    )
 
def fetch_player_stats(**context):
    execution_date = context['ds']
    bucket = os.environ.get('GCS_BUCKET')
 
    current_season = '2024-25'
    active_players = players.get_active_players()[:10]
 
    all_stats = []
 
    for player in active_players:
        player_id = player['id']
        player_name = player['full_name']
 
        player_log = PlayerGameLog(
            player_id=player_id,
            season=current_season,
            timeout=60
        )
 
        sleep(1)
 
        df = player_log.get_data_frames()[0]
        df = df.fillna(0)
        df['player_name'] = player_name
        df = df[df['GAME_DATE'] == pd.Timestamp(execution_date).strftime('%b %d, %Y').replace(' 0', ' ')]
        records = df.to_dict(orient='records')
        all_stats.extend(records)
        print(f"Fetched {player_name}: {len(records)} records")
 
    # Outside the loop — upload after all players are fetched
    stats_json = '\n'.join([json.dumps(r) for r in all_stats])
 
    hook = GCSHook()
    hook.upload(
        bucket_name=bucket,
        object_name=f'raw/nba/{execution_date}/player_stats.json',
        data=stats_json,
        mime_type='application/json'
    )
 
trigger_spark = BashOperator(
    task_id='trigger_spark',
    bash_command='spark-submit /home/jackthompson/DE_ZoomCamp_FinalProject/spark/transform.py {{ ds }}',
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
 
[fetch_games_task, fetch_player_stats_task] >> trigger_spark