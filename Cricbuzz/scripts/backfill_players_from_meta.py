"""
Extract player metadata from the meta JSON field in the players table
and backfill missing country, role, date_of_birth fields.

Usage:
  python scripts/backfill_players_from_meta.py          # dry-run
  python scripts/backfill_players_from_meta.py --apply # apply
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

import sys
sys.path.insert(0, '.')

import argparse
import pymysql
import json

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply updates to DB')
parser.add_argument('--db-host', help='DB host')
parser.add_argument('--db-user', help='DB user')
parser.add_argument('--db-password', help='DB password')
parser.add_argument('--db-name', help='DB name')
parser.add_argument('--db-port', type=int, help='DB port')
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

# Find players with missing fields but have meta JSON
print('Finding players with missing fields...')
cur.execute("""
    SELECT id, external_player_id, player_name, meta,
           country, role, date_of_birth
    FROM players 
    WHERE external_player_id IS NOT NULL 
    AND meta IS NOT NULL
    AND (country IS NULL OR role IS NULL OR date_of_birth IS NULL)
    LIMIT 500
""")
candidates = cur.fetchall()

if not candidates:
    print('No players need backfill')
    conn.close()
    sys.exit(0)

print(f'Found {len(candidates)} players to consider\n')

updated = 0

for p in candidates:
    player_id = p['external_player_id']
    player_name = p['player_name']
    
    try:
        meta = json.loads(p['meta']) if isinstance(p['meta'], str) else p['meta']
    except Exception:
        meta = {}
    
    if not isinstance(meta, dict):
        continue
    
    missing = []
    if p['country'] is None:
        missing.append('country')
    if p['role'] is None:
        missing.append('role')
    if p['date_of_birth'] is None:
        missing.append('DOB')
    
    # Extract from meta
    country = meta.get('country') or meta.get('nationality') or meta.get('countryName')
    dob = meta.get('dateOfBirth') or meta.get('dob') or meta.get('birthDate')
    role = meta.get('role') or meta.get('playingRole')
    
    # Infer role from batting/bowling style
    if not role:
        bat_style = (meta.get('batting_style') or meta.get('battingStyle') or '').lower()
        bowl_style = (meta.get('bowling_style') or meta.get('bowlingStyle') or '').lower()
        if 'wicket' in bat_style or 'keeper' in bat_style:
            role = 'Wicket-keeper'
        elif bat_style and bowl_style:
            role = 'All-rounder'
        elif bat_style:
            role = 'Batsman'
        elif bowl_style:
            role = 'Bowler'
    
    inferred = []
    if country and p['country'] is None:
        inferred.append(f'country={country}')
    if role and p['role'] is None:
        inferred.append(f'role={role}')
    if dob and p['date_of_birth'] is None:
        inferred.append(f'DOB={dob}')
    
    if inferred:
        print(f"Player {player_id} ({player_name}): {', '.join(inferred)}")
        
        if args.apply:
            cur.execute("""
                UPDATE players 
                SET 
                    country = COALESCE(%s, country),
                    role = COALESCE(%s, role),
                    date_of_birth = COALESCE(%s, date_of_birth)
                WHERE external_player_id = %s
            """, (country, role, dob, player_id))
            conn.commit()
            updated += 1

conn.close()
print(f'\nUpdated: {updated} players')

if not args.apply:
    print('Run with --apply to update the DB')
