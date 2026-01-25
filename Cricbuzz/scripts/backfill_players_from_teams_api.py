"""
Fetch complete player data from team players API and backfill missing fields.
Usage:
  python scripts/backfill_players_from_teams_api.py --api-key <KEY>          # dry-run
  python scripts/backfill_players_from_teams_api.py --apply --api-key <KEY> # apply
"""
from typing import Dict, Any
try:
    from streamlit import secrets
    _s = secrets.get('mysql', {}) or {}
    mysql_secrets: Dict[str, Any] = dict(_s)
except Exception:
    mysql_secrets = {}

if not mysql_secrets:
    mysql_secrets = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'cricketdb',
        'port': 3306,
    }

try:
    from streamlit import secrets as st_secrets
    api_key = st_secrets.get('RAPIDAPI_KEY') or st_secrets.get('rapidapi_key')
except Exception:
    api_key = None

import sys
sys.path.insert(0, '.')

import argparse
import pymysql
import json
import time
from Cricbuzz.utils.api_client import get_api_client
from Cricbuzz.utils.mysql_sync import upsert_player

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply updates to DB')
parser.add_argument('--db-host', help='DB host')
parser.add_argument('--db-user', help='DB user')
parser.add_argument('--db-password', help='DB password')
parser.add_argument('--db-name', help='DB name')
parser.add_argument('--db-port', type=int, help='DB port')
parser.add_argument('--api-key', help='RapidAPI key')
args = parser.parse_args()

if args.db_host:
    mysql_secrets['host'] = args.db_host
if args.db_user:
    mysql_secrets['user'] = args.db_user
if args.db_password is not None:
    mysql_secrets['password'] = args.db_password
if args.db_name:
    mysql_secrets['database'] = args.db_name
if args.db_port:
    mysql_secrets['port'] = args.db_port
if args.api_key:
    api_key = args.api_key

if not api_key:
    print('ERROR: No API key provided. Set RAPIDAPI_KEY in .streamlit/secrets.toml or use --api-key')
    sys.exit(1)

print('Connecting to DB...')
conn = pymysql.connect(
    host=str(mysql_secrets.get('host', 'localhost')),
    user=str(mysql_secrets.get('user', 'root')),
    password=str(mysql_secrets.get('password', '')),
    database=str(mysql_secrets.get('database', 'cricketdb')),
    port=int(mysql_secrets.get('port') or 3306),
    charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# Get all teams
print('Fetching all teams...')
cur.execute("SELECT external_team_id FROM teams WHERE external_team_id IS NOT NULL LIMIT 100")
teams = cur.fetchall()
print(f'Found {len(teams)} teams\n')

api_client = get_api_client(api_key)
updated = 0
failed = 0
rate_limited = False

for t in teams:
    team_id = t['external_team_id']
    
    if rate_limited:
        print(f'Rate limited, stopping')
        break
    
    try:
        print(f'Fetching players for team {team_id}...')
        response = api_client.get_team_players(str(team_id))
        
        # Parse players from response
        players_list = response.get('player', []) or response.get('players', []) or response.get('playerList', []) or response.get('playersList', []) or []
        print(f'  Found {len(players_list)} players')
        
        for p in players_list:
            try:
                player_id = p.get('id') or p.get('pid') or p.get('playerId') or p.get('player_id')
                player_name = p.get('name') or p.get('playerName') or p.get('player_name')
                
                if not player_id or not player_name:
                    continue
                
                # Extract metadata
                country = p.get('country') or p.get('nationality') or p.get('countryName')
                role = p.get('role') or p.get('playingRole') or p.get('playerRole')
                dob = p.get('dateOfBirth') or p.get('dob') or p.get('birthDate')
                
                # Try meta object
                meta_obj = p.get('meta')
                try:
                    if isinstance(meta_obj, str):
                        meta_obj = json.loads(meta_obj)
                except Exception:
                    meta_obj = None
                
                if isinstance(meta_obj, dict):
                    if not country:
                        country = meta_obj.get('country') or meta_obj.get('nationality')
                    if not role:
                        role = meta_obj.get('role') or meta_obj.get('playingRole')
                    if not dob:
                        dob = meta_obj.get('dateOfBirth') or meta_obj.get('dob')
                
                if country or role or dob:
                    p_copy = dict(p)
                    p_copy['id'] = player_id
                    p_copy['country'] = country
                    p_copy['role'] = role
                    p_copy['dateOfBirth'] = dob
                    
                    if args.apply:
                        try:
                            rc = upsert_player(mysql_secrets, p_copy)
                            if rc and rc > 0:
                                updated += 1
                        except Exception as e:
                            print(f"    WARNING: upsert failed for {player_name}: {e}")
            except Exception as e:
                print(f"    ERROR processing player: {e}")
        
        # Rate limit: sleep 1 second between team requests
        time.sleep(1)
    except Exception as e:
        err_str = str(e).lower()
        if '429' in err_str or 'too many requests' in err_str:
            print(f'  Rate limited (429)')
            rate_limited = True
        else:
            print(f'  ERROR: {e}')
            failed += 1

conn.close()
print(f'\nSummary:')
print(f'  Updated: {updated} players')
print(f'  Failed: {failed} teams')

if not args.apply:
    print('\nRun with --apply to update the DB')
