"""
Backfill player metadata (country, role, date_of_birth) using the player profile API.

Fetches /stats/v1/player/{player_id} for each player in the DB to get:
- country
- date_of_birth
- role

Usage:
  python scripts/backfill_players_from_profile_api.py --api-key YOUR_KEY          # dry-run
  python scripts/backfill_players_from_profile_api.py --api-key YOUR_KEY --apply # apply

Author: Auto-generated backfill script
"""

import sys
sys.path.insert(0, '.')

import argparse
import pymysql
import time
from typing import Dict, Any

# Import API client
from Cricbuzz.utils.api_client import get_api_client, extract_player_metadata
from Cricbuzz.utils.mysql_sync import upsert_player

# Parse arguments
parser = argparse.ArgumentParser(description='Backfill player metadata from API')
parser.add_argument('--api-key', required=True, help='RapidAPI key')
parser.add_argument('--apply', action='store_true', help='Apply updates (default: dry-run)')
parser.add_argument('--db-host', default='localhost', help='DB host')
parser.add_argument('--db-user', default='root', help='DB user')
parser.add_argument('--db-password', default='', help='DB password')
parser.add_argument('--db-name', default='cricketdb', help='DB name')
parser.add_argument('--db-port', type=int, default=3306, help='DB port')
parser.add_argument('--limit', type=int, default=100, help='Max players to process')
parser.add_argument('--sleep', type=float, default=0.5, help='Sleep between API calls (seconds)')

args = parser.parse_args()

# Initialize API client
print('Initializing API client...')
api_client = get_api_client(args.api_key)

# Connect to DB
print(f'Connecting to DB {args.db_host}:{args.db_port}...')
try:
    conn = pymysql.connect(
        host=args.db_host,
        user=args.db_user,
        password=args.db_password,
        database=args.db_name,
        port=args.db_port,
        charset='utf8mb4'
    )
    cur = conn.cursor(pymysql.cursors.DictCursor)
except Exception as e:
    print(f'ERROR: Failed to connect to DB: {e}')
    sys.exit(1)

# Fetch players with NULL metadata
print('Finding players with missing metadata...')
try:
    cur.execute("""
        SELECT id, external_player_id, player_name, country, role, date_of_birth
        FROM players 
        WHERE external_player_id IS NOT NULL 
        AND (country IS NULL OR role IS NULL OR date_of_birth IS NULL)
        LIMIT %s
    """, (args.limit,))
    candidates = cur.fetchall()
except Exception as e:
    print(f'ERROR: Failed to query players: {e}')
    conn.close()
    sys.exit(1)

if not candidates:
    print('No players found with missing metadata')
    conn.close()
    sys.exit(0)

print(f'Found {len(candidates)} players with missing metadata\n')

updated = 0
failed = 0
rate_limited = False

for idx, p in enumerate(candidates, 1):
    player_id = p['external_player_id']
    player_name = p['player_name']
    
    print(f'[{idx}/{len(candidates)}] {player_name} (ID {player_id})...', end=' ')
    
    try:
        # Fetch player profile from API
        profile = api_client.get_player_profile(str(player_id))
        
        if not profile:
            print('ERROR: No profile data')
            failed += 1
            continue
        
        # Check for rate limiting
        if 'status' in profile and profile['status'] == 429:
            print('RATE LIMITED (429)')
            rate_limited = True
            break
        
        # Extract metadata
        player_data = extract_player_metadata(profile)
        
        # Log what we found
        found = []
        if player_data.get('country') and p['country'] is None:
            found.append(f"country={player_data['country']}")
        if player_data.get('role') and p['role'] is None:
            found.append(f"role={player_data['role']}")
        if player_data.get('date_of_birth') and p['date_of_birth'] is None:
            found.append(f"DOB={player_data['date_of_birth']}")
        
        if found:
            print(', '.join(found))
            
            if args.apply:
                # Upsert player with new metadata
                try:
                    mysql_secrets = {
                        'host': args.db_host,
                        'user': args.db_user,
                        'password': args.db_password,
                        'database': args.db_name,
                        'port': args.db_port
                    }
                    rc = upsert_player(mysql_secrets, player_data)
                    if rc and rc > 0:
                        updated += 1
                except Exception as ue:
                    print(f'  [upsert error: {ue}]')
                    failed += 1
        else:
            print('no new data')
        
        # Rate limiting: sleep between requests
        time.sleep(args.sleep)
        
    except Exception as e:
        print(f'ERROR: {e}')
        failed += 1

conn.close()

print(f'\n=== SUMMARY ===')
print(f'Processed: {len(candidates)}')
print(f'Updated: {updated}')
print(f'Failed: {failed}')
if rate_limited:
    print('Status: RATE LIMITED - Try again later or increase --sleep')

if not args.apply:
    print('\nRun with --apply to update the DB')
