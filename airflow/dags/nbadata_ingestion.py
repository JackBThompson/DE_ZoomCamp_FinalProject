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

dag = DAG(
    dag_id='nba_ingestion',
    schedule_interval='@daily',
    start_date=datetime.now() - timedelta(days=90),
    catchup=True
)

def fetch_games(**context):
    execution_date = context['ds']
    games = LeagueGameFinder(
        date_from_nullable=execution_date,
        date_to_nullable=execution_date,
        timeout=60
    )
    sleep(1)
    df = games.get_data_frames()[0]
    records = df.to_dict(orient='records')
    context['ti'].xcom_push(key='games', value=records)

def fetch_player_stats(**context):
    current_season = '2024-25'
    active_players = players.get_active_players()[:10]
    all_stats = []
    for player in active_players:
        player_id = player['id']
        player_log = PlayerGameLog(
            player_id=player_id,
            season=current_season,
            timeout=60
        )
        sleep(1)
        df = player_log.get_data_frames()[0]
        df = df.fillna(0)
        records = df.to_dict(orient='records')
        all_stats.extend(records)
    context['ti'].xcom_push(key='player_stats', value=all_stats)

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

fetch_games_task >> fetch_player_stats_task >> upload_to_gcs_task >> trigger_spark