"""
Backfill team countries from matches meta when available.
Usage:
  python scripts/backfill_teams.py --dry-run
  python scripts/backfill_teams.py --apply
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

import argparse
import json
import pymysql

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true')
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

conn = pymysql.connect(
    host=str(mysql_secrets.get('host', 'localhost')),
    user=str(mysql_secrets.get('user', 'root')),
    password=str(mysql_secrets.get('password', '')),
    database=str(mysql_secrets.get('database', 'cricketdb')),
    port=int(mysql_secrets.get('port') or 3306),
    charset='utf8mb4'
)
cur = conn.cursor()
cur.execute("SELECT id, external_team_id, team_name FROM teams WHERE country IS NULL")
rows = cur.fetchall()
if not rows:
    print('No teams need country backfill')
    conn.close()
    raise SystemExit(0)

print(f'Found {len(rows)} teams to consider')

for r in rows:
    tid = r[1]
    tname = r[2]
    print(f"\nTeam {tid} ({tname}):")
    # Search matches meta for this team id
    cur.execute("SELECT id, meta FROM matches WHERE meta LIKE %s LIMIT 20", (f'%{tid}%',))
    candidates = cur.fetchall()
    found_country = None
    for c in candidates:
        try:
            meta = json.loads(c[1]) if c[1] else {}
        except Exception:
            meta = {}
        # Try team1/team2 objects
        for key in ('team1', 'team2'):
            obj = meta.get(key) or {}
            if isinstance(obj, dict):
                # Accept country fields
                country = obj.get('country') or obj.get('teamCountry') or obj.get('country_name')
                ext_id = obj.get('teamId') or obj.get('team_id') or obj.get('id') or obj.get('external_team_id')
                if (ext_id is not None and str(ext_id) == str(tid)) and country:
                    found_country = country
                    break
        if found_country:
            break
    if found_country:
        print(f"  inferred country={found_country}")
        if args.apply:
            cur.execute("UPDATE teams SET country = %s WHERE external_team_id = %s", (found_country, tid))
            conn.commit()
            print('  applied')
    else:
        print('  no country inferred from matches meta')

conn.close()
print('\nDone')