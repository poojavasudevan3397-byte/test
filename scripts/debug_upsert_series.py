"""
Diagnostic script to test upserting a series and verify it's written to DB.
Run: python scripts/debug_upsert_series.py
"""
from typing import Any, Dict
import sys
import os
import pymysql
import traceback

# Ensure project root is on sys.path so 'Cricbuzz' package can be imported when running from scripts/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Cricbuzz.utils.mysql_sync import create_mysql_schema, upsert_series

# Update these credentials to match your Streamlit secrets or local MySQL
mysql_secrets: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

print("Creating schema (if not exists)...")
try:
    create_mysql_schema(mysql_secrets)
    print("Schema created / verified")
except Exception as e:
    print("ERROR creating schema:", e)
    traceback.print_exc()

# Sample series
sid = "test_series_diag"
name = "Test Series (diag)"
stype = "TestType"
start_ms = 1672531200000  # 2023-01-01
end_ms = 1704067200000    # 2024-01-01

print(f"Upserting series id={sid} name={name}")
try:
    rc = upsert_series(mysql_secrets, sid, name, stype, start_ms, end_ms)
    print("upsert_series returned:", rc)
except Exception as e:
    print("ERROR upserting series:", e)
    traceback.print_exc()

print("Querying series table for the inserted row...")
try:
    conn = pymysql.connect(
        host=mysql_secrets['host'],
        user=mysql_secrets['user'],
        password=mysql_secrets['password'],
        database=mysql_secrets['database'],
        port=mysql_secrets['port'],
        charset='utf8mb4'
    )
    cur = conn.cursor()
    cur.execute("SELECT Series_ID, Series_Name, Series_Type, Start_Date, End_Date, Meta FROM series WHERE Series_ID=%s", (sid,))
    rows = cur.fetchall()
    if not rows:
        print("No rows found for Series_ID=", sid)
    else:
        for r in rows:
            print("ROW:", r)
    cur.close()
    conn.close()
except Exception as e:
    print("ERROR querying series:", e)
    traceback.print_exc()
