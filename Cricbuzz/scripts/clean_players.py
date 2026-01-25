"""
Clean placeholder player rows inserted by bad API responses.
Usage: python scripts/clean_players.py [--delete]
Without --delete will show candidates; with --delete will remove them.
"""
from typing import List
import pymysql
import argparse
from pathlib import Path
import re

# Basic .streamlit/secrets.toml parse (only what we need)
def load_mysql_secrets():
    p = Path(__file__).parents[1] / '.streamlit' / 'secrets.toml'
    defaults = {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'cricketdb', 'port': 3306}
    if not p.exists():
        return defaults
    data = p.read_text().splitlines()
    cfg = defaults.copy()
    in_mysql = False
    for l in data:
        l = l.strip()
        if l.startswith('[mysql]'):
            in_mysql = True
            continue
        if l.startswith('[') and in_mysql:
            break
        if in_mysql and '=' in l:
            k, v = [s.strip() for s in l.split('=', 1)]
            v = v.strip('"').strip("'")
            if k == 'host': cfg['host'] = v
            if k == 'user': cfg['user'] = v
            if k == 'password': cfg['password'] = v
            if k == 'database': cfg['database'] = v
            if k == 'port': cfg['port'] = int(v)
    return cfg

ROLE_HEADERS = [
    'batsmen', 'batsman', 'batters', 'batter', 'batting',
    'bowlers', 'bowler', 'bowling',
    'all rounder', 'all-rounder', 'allrounder', 'all rounders',
    'wicket keeper', 'wicket-keeper', 'wicketkeeper'
]

def find_candidates(conn) -> List[dict]:
    with conn.cursor(pymysql.cursors.DictCursor) as cur:
        placeholders = ','.join(['%s'] * len(ROLE_HEADERS))
        sql = f"SELECT id, external_player_id, player_name, meta, created_at FROM players WHERE external_player_id IS NULL AND LOWER(TRIM(player_name)) IN ({placeholders})"
        cur.execute(sql, ROLE_HEADERS)
        return cur.fetchall()


def delete_candidates(conn, ids: List[int]):
    if not ids:
        return 0
    with conn.cursor() as cur:
        sql = f"DELETE FROM players WHERE id IN ({','.join(['%s']*len(ids))})"
        rc = cur.execute(sql, ids)
    conn.commit()
    return rc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--delete', action='store_true', help='Actually delete matching rows')
    args = parser.parse_args()

    secrets = load_mysql_secrets()
    conn = pymysql.connect(host=secrets['host'], user=secrets['user'], password=secrets['password'], database=secrets['database'], port=int(secrets['port']), charset='utf8mb4')

    candidates = find_candidates(conn)
    if not candidates:
        print('No placeholder player rows found')
        return

    print('Found candidate placeholder rows:')
    for c in candidates:
        print(f"  id={c['id']} name={c['player_name']} meta={c['meta']} created_at={c['created_at']}")

    if args.delete:
        ids = [c['id'] for c in candidates]
        rc = delete_candidates(conn, ids)
        print(f'Deleted {rc} rows')
    else:
        print('\nRun this script again with --delete to remove these rows')

    conn.close()

if __name__ == '__main__':
    main()
