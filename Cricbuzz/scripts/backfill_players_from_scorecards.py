"""
Backfill missing player metadata from match scorecards already in the DB.
Extracts player info from batting_stats and bowling_stats and updates players table.

Usage:
  python scripts/backfill_players_from_scorecards.py                # dry-run
  python scripts/backfill_players_from_scorecards.py --apply       # apply updates
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
# Optional CLI overrides for DB credentials
parser.add_argument('--db-host', help='DB host')
parser.add_argument('--db-user', help='DB user')
parser.add_argument('--db-password', help='DB password')
parser.add_argument('--db-name', help='DB name')
parser.add_argument('--db-port', type=int, help='DB port')
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

# Find players with missing country or role
print('Finding players with missing country or role...')
cur.execute("""
    SELECT id, external_player_id, player_name, country, role 
    FROM players 
    WHERE external_player_id IS NOT NULL 
    AND (country IS NULL OR role IS NULL)
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
    has_country = p['country'] is not None
    has_role = p['role'] is not None
    
    missing = []
    if not has_country:
        missing.append('country')
    if not has_role:
        missing.append('role')
    
    print(f"Player {player_id} ({player_name}): missing {', '.join(missing)}")
    
    # Try to infer role from batting/bowling stats
    inferred_role = None
    if not has_role:
        # Check if player appears in batting and bowling stats
        cur.execute("SELECT COUNT(*) as cnt FROM batting_stats WHERE player_name = %s", (player_name,))
        bat_count = cur.fetchone()['cnt']
        cur.execute("SELECT COUNT(*) as cnt FROM bowling_stats WHERE player_name = %s", (player_name,))
        bowl_count = cur.fetchone()['cnt']
        
        if bat_count > 0 and bowl_count > 0:
            inferred_role = 'All-rounder'
        elif bat_count > 0:
            inferred_role = 'Batsman'
        elif bowl_count > 0:
            inferred_role = 'Bowler'
    
    if inferred_role:
        print(f"  inferred role={inferred_role}")
        
        if args.apply:
            cur.execute("""
                UPDATE players 
                SET role = COALESCE(%s, role)
                WHERE external_player_id = %s
            """, (inferred_role, player_id))
            conn.commit()
            updated += 1
            print('  applied')

conn.close()
print(f'\nUpdated: {updated} players')

if not args.apply:
    print('Run with --apply to update the DB')
