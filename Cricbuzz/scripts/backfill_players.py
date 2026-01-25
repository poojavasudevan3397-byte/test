"""
Backfill missing player metadata (DOB, country, role) from Cricbuzz API.
Fetches player profiles for players with missing fields and updates the DB.

Usage:
  python scripts/backfill_players.py --api-key <KEY>              # dry-run, shows candidates
  python scripts/backfill_players.py --apply --api-key <KEY>     # apply updates
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
from Cricbuzz.utils.api_client import get_api_client

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply updates to DB')
# Optional CLI overrides for DB credentials
parser.add_argument('--db-host', help='DB host')
parser.add_argument('--db-user', help='DB user')
parser.add_argument('--db-password', help='DB password')
parser.add_argument('--db-name', help='DB name')
parser.add_argument('--db-port', type=int, help='DB port')
# Optional API key override
parser.add_argument('--api-key', help='RapidAPI key')
args = parser.parse_args()

# Apply CLI overrides
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

# Find players with missing DOB, country, or role
print('Finding players with missing DOB, country, or role...')
cur.execute("""
    SELECT id, external_player_id, player_name, country, role, date_of_birth 
    FROM players 
    WHERE external_player_id IS NOT NULL 
    AND (date_of_birth IS NULL OR country IS NULL OR role IS NULL)
    LIMIT 500
""")
candidates = cur.fetchall()

if not candidates:
    print('No players need backfill')
    conn.close()
    sys.exit(0)

print(f'Found {len(candidates)} players to consider\n')

api_client = get_api_client(api_key)
updated = 0
skipped = 0
failed = 0

for p in candidates:
    player_id = p['external_player_id']
    player_name = p['player_name']
    has_dob = p['date_of_birth'] is not None
    has_country = p['country'] is not None
    has_role = p['role'] is not None
    
    missing = []
    if not has_dob:
        missing.append('DOB')
    if not has_country:
        missing.append('country')
    if not has_role:
        missing.append('role')
    
    print(f"Player {player_id} ({player_name}): missing {', '.join(missing)}")
    
    try:
        profile = api_client.get_player_profile(str(player_id))
        
        # Extract metadata
        dob = profile.get('dateOfBirth') or profile.get('dob') or profile.get('birthDate')
        country = profile.get('country') or profile.get('nationality') or profile.get('countryName')
        role = profile.get('role') or profile.get('playingRole') or profile.get('playerRole')
        
        # Try meta object for DOB/country/role
        meta_obj = profile.get('meta')
        try:
            if isinstance(meta_obj, str):
                meta_obj = json.loads(meta_obj)
        except Exception:
            meta_obj = None
        
        if isinstance(meta_obj, dict):
            if not dob:
                dob = meta_obj.get('dateOfBirth')
            if not country:
                country = meta_obj.get('country') or meta_obj.get('nationality')
            if not role:
                bat_style = meta_obj.get('batting_style') or meta_obj.get('battingStyle') or ''
                bowl_style = meta_obj.get('bowling_style') or meta_obj.get('bowlingStyle') or ''
                if 'wicket' in str(bat_style).lower() or 'keeper' in str(bat_style).lower():
                    role = 'Wicket-keeper'
                elif bat_style and bowl_style:
                    role = 'All-rounder'
                elif bat_style:
                    role = 'Batsman'
                elif bowl_style:
                    role = 'Bowler'
        
        if dob or country or role:
            print(f"  inferred: DOB={dob}, country={country}, role={role}")
            
            if args.apply:
                cur.execute("""
                    UPDATE players 
                    SET 
                        date_of_birth = COALESCE(%s, date_of_birth),
                        country = COALESCE(%s, country),
                        role = COALESCE(%s, role)
                    WHERE external_player_id = %s
                """, (dob, country, role, player_id))
                conn.commit()
                updated += 1
                print('  applied')
        else:
            print('  no data found in API')
            skipped += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        failed += 1

conn.close()
print(f'\nSummary:')
print(f'  Updated: {updated}')
print(f'  Skipped: {skipped}')
print(f'  Failed: {failed}')

if not args.apply:
    print('\nRun with --apply to update the DB')
