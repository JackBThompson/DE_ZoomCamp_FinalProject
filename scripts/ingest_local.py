##Objective: Standalone script to pull NBA data locally and upload to GCS, bypassing NBA.com cloud IP ban.##

import json
import os
import pandas as pd
from nba_api.stats.endpoints import LeagueGameFinder, PlayerGameLog
from nba_api.stats.static import players
from google.cloud import storage
from datetime import date
from time import sleep

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp-key.json'

BUCKET = 'nba-pipeline-jaitfrey-03-26'
execution_date = str(date.today())

def upload_to_gcs(bucket_name, destination, data):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination)
    blob.upload_from_string(data, content_type='application/json')
    print(f'Uploaded to gs://{bucket_name}/{destination}')

# Fetch games
print('Fetching games...')
games = LeagueGameFinder(
    date_from_nullable=execution_date,
    date_to_nullable=execution_date,
    timeout=60
)
sleep(1)
df_games = games.get_data_frames()[0]
games_json = '\n'.join([json.dumps(r) for r in df_games.to_dict(orient='records')])
upload_to_gcs(BUCKET, f'raw/nba/{execution_date}/games.json', games_json)
print(f'Games uploaded: {len(df_games)} records')

# Fetch player stats — limited to 10 players for speed
print('Fetching player stats...')
active_players = players.get_active_players()[:10]
all_stats = []

for player in active_players:
    player_log = PlayerGameLog(
        player_id=player['id'],
        season='2024-25',
        timeout=60
    )
    sleep(1)
    df = player_log.get_data_frames()[0]
    df = df.fillna(0)
    df['player_name'] = player['full_name']  # ← add this line
    df = df[df['GAME_DATE'] == pd.Timestamp(execution_date).strftime('%b %d, %Y').replace(' 0', ' ')]
    all_stats.extend(df.to_dict(orient='records'))
    print(f"Fetched {player['full_name']}: {len(df)} records")

stats_json = '\n'.join([json.dumps(r) for r in all_stats])
upload_to_gcs(BUCKET, f'raw/nba/{execution_date}/player_stats.json', stats_json)
print(f'Player stats uploaded: {len(all_stats)} records')