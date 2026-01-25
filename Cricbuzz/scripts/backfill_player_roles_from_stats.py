"""
Infer and populate player roles from existing batting/bowling stats.

For any player in the players table who appears in batting_stats or bowling_stats,
infer their role based on:
- Only batting: "Batsman"
- Only bowling: "Bowler"  
- Both batting and bowling: "All-rounder"
- Batting with bowling style indicating keeper: "Wicket-keeper"

Usage:
  python scripts/backfill_player_roles_from_stats.py --db-host localhost --db-user root --db-password Vasu@76652 --db-name cricketdb
  python scripts/backfill_player_roles_from_stats.py --db-host localhost --db-user root --db-password Vasu@76652 --db-name cricketdb --apply
"""

import sys
sys.path.insert(0, '.')

import argparse
import pymysql
from typing import Set, Dict, Any

parser = argparse.ArgumentParser(description='Infer player roles from batting/bowling stats')
parser.add_argument('--db-host', default='localhost', help='DB host')
parser.add_argument('--db-user', default='root', help='DB user')
parser.add_argument('--db-password', default='', help='DB password')
parser.add_argument('--db-name', default='cricketdb', help='DB name')
parser.add_argument('--db-port', type=int, default=3306, help='DB port')
parser.add_argument('--apply', action='store_true', help='Apply updates (default: dry-run)')

args = parser.parse_args()

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

print('Finding players with NULL role...')

# Get players with NULL role
cur.execute("""
    SELECT DISTINCT p.id, p.external_player_id, p.player_name
    FROM players p
    WHERE p.role IS NULL
    AND p.external_player_id IS NOT NULL
    ORDER BY p.player_name
""")
candidates = cur.fetchall()

if not candidates:
    print('No players with NULL role found')
    conn.close()
    sys.exit(0)

print(f'Found {len(candidates)} players with NULL role\n')

# For each candidate, check if they appear in batting/bowling stats
updated = 0

for p in candidates:
    player_id = p['external_player_id']
    player_name = p['player_name']
    
    # Check batting stats
    cur.execute("""
        SELECT COUNT(*) as cnt FROM batting_stats 
        WHERE external_player_id = %s
    """, (player_id,))
    bat_count = cur.fetchone()['cnt'] or 0
    
    # Check bowling stats
    cur.execute("""
        SELECT COUNT(*) as cnt FROM bowling_stats 
        WHERE external_player_id = %s
    """, (player_id,))
    bowl_count = cur.fetchone()['cnt'] or 0
    
    # Infer role
    if bat_count > 0 and bowl_count > 0:
        role = 'All-rounder'
    elif bat_count > 0:
        role = 'Batsman'
    elif bowl_count > 0:
        role = 'Bowler'
    else:
        # No appearance in either; skip
        continue
    
    print(f"{player_name:30} | Batting: {bat_count:3} | Bowling: {bowl_count:3} | Role: {role}")
    
    if args.apply:
        try:
            cur.execute("""
                UPDATE players 
                SET role = %s 
                WHERE external_player_id = %s
            """, (role, player_id))
            conn.commit()
            updated += 1
        except Exception as e:
            print(f"  ERROR updating: {e}")

conn.close()

print(f'\nUpdated: {updated} players')
if not args.apply:
    print('Run with --apply to update the DB')
