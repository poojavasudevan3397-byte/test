"""
Backfill script for populating missing series metadata (series_type, start_date, end_date)
Uses the `matches` table as the source of truth: takes MIN(start_date) as series start, MAX(start_date) as series end,
and infers `series_type` from the most common `match_format` within the series.

Usage:
  python scripts/backfill_series.py          # dry-run, shows intended updates
  python scripts/backfill_series.py --apply  # apply updates to DB
"""
from typing import Dict, Any, Optional
try:
    from streamlit import secrets
    # Copy secrets into a plain dict so we can override with CLI args if needed
    _s = secrets.get('mysql', {}) or {}
    mysql_secrets: Dict[str, Any] = dict(_s)
except Exception:
    mysql_secrets: Dict[str, Any] = {}

if not mysql_secrets:
    mysql_secrets = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'cricketdb',
        'port': 3306,
    }

import argparse
import pymysql
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply updates to the DB')
# Optional CLI overrides for DB credentials (useful for running locally without editing secrets)
parser.add_argument('--db-host', help='DB host, e.g. 127.0.0.1')
parser.add_argument('--db-user', help='DB user name')
parser.add_argument('--db-password', help='DB password')
parser.add_argument('--db-name', help='DB name')
parser.add_argument('--db-port', type=int, help='DB port')
args = parser.parse_args()

# Apply CLI overrides to mysql_secrets if provided
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
# Find series rows that are missing any of the target columns
cur.execute("SELECT id, external_series_id, series_name, series_type, start_date, end_date FROM series WHERE series_type IS NULL OR start_date IS NULL OR end_date IS NULL")
cands = cur.fetchall()
if not cands:
    print('No series rows need backfill')
    conn.close()
    raise SystemExit(0)

print(f"Found {len(cands)} series rows to consider for backfill")

for row in cands:
    sid = row[1]
    sname = row[2]
    print(f"\nSeries {sid} ({sname}):")

    # Derive start/end from matches table
    cur.execute("SELECT MIN(start_date), MAX(start_date) FROM matches WHERE external_series_id = %s AND start_date IS NOT NULL", (sid,))
    start_max = cur.fetchone()
    start_dt = start_max[0] #type: ignore
    end_dt = start_max[1] #type: ignore

    # Derive series_type from most common match_format within the series
    cur.execute("SELECT match_format, COUNT(*) as cnt FROM matches WHERE external_series_id = %s AND match_format IS NOT NULL GROUP BY match_format ORDER BY cnt DESC LIMIT 1", (sid,))
    mt = cur.fetchone()
    inferred_type = mt[0] if mt and mt[0] else None

    print(f"  inferred start_date={start_dt} end_date={end_dt} series_type={inferred_type}")

    if args.apply:
        print('  Applying update...')
        cur.execute(
            "UPDATE series SET series_type = COALESCE(%s, series_type), start_date = COALESCE(%s, start_date), end_date = COALESCE(%s, end_date) WHERE external_series_id = %s",
            (inferred_type, start_dt, end_dt, sid),
        )
        conn.commit()
        print('  Done')

conn.close()
print('\nBackfill completed')
