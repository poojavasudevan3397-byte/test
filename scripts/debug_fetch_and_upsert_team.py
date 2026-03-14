"""
Debug script: fetch team info from API and upsert team to DB (including country)
Run: python scripts/debug_fetch_and_upsert_team.py <TEAM_ID>
"""
import sys
import os
import traceback
import requests
from typing import Any, Dict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Cricbuzz.utils.mysql_sync import create_mysql_schema, upsert_team

mysql_secrets: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

if len(sys.argv) < 2:
    print("Usage: python scripts/debug_fetch_and_upsert_team.py <TEAM_ID>")
    sys.exit(1)

team_id = sys.argv[1]
api_key = ""  # replace with your RAPIDAPI_KEY or use st.secrets if running from Streamlit

print("Creating schema (if not exists)...")
create_mysql_schema(mysql_secrets)

# Allow passing API key as 2nd arg or via env var
if len(sys.argv) >= 3 and sys.argv[2]:
    api_key = sys.argv[2]
else:
    api_key = os.environ.get("RAPIDAPI_KEY", api_key)

# Try to fetch team info via API client (structured) then fall back to direct request
from Cricbuzz.utils.api_client import get_api_client
client = get_api_client(api_key or "")

Team_Name = None
Team_Country = None
api_payload = None

try:
    teams_map = client.get_all_teams_with_country()
    api_payload = teams_map.get(str(team_id))
    if api_payload:
        Team_Name = api_payload.get('name') or api_payload.get('teamName')
        Team_Country = api_payload.get('country')
        print(f"Found team in teams_map: name={Team_Name}, country={Team_Country}")
    else:
        # Single-team fetch
        try:
            raw = client._get(f"/teams/v1/{team_id}")
            if isinstance(raw, dict):
                api_payload = raw
                Team_Name = raw.get('teamName') or raw.get('name') or None
                Team_Country = raw.get('country') or raw.get('countryName') or raw.get('teamCountry') or None
                nested = raw.get('team') or raw.get('teamInfo')
                if not Team_Country and isinstance(nested, dict):
                    Team_Country = nested.get('country') or nested.get('countryName') or None
                print(f"Fetched single-team API: name={Team_Name}, country={Team_Country}")
        except Exception as e:
            print(f"Warning: single-team API fetch failed: {e}")
            traceback.print_exc()
except Exception as e:
    print(f"Warning: could not fetch teams map: {e}")
    traceback.print_exc()

# Fallbacks
if not Team_Name:
    Team_Name = f"Team {team_id}"

print("--- API RESULT ---")
print(f"team_id={team_id}")
print(f"team_name (from API)={Team_Name}")
print(f"team_country (from API)={Team_Country}")
print("------------------")

# Show DB row before any upsert
import pymysql

def fetch_db_row(tid: str):
    conn = pymysql.connect(
        host=mysql_secrets['host'],
        user=mysql_secrets['user'],
        password=mysql_secrets['password'],
        database=mysql_secrets['database'],
        port=mysql_secrets['port'],
        charset='utf8mb4'
    )
    cur = conn.cursor()
    cur.execute("SELECT ID, Team_ID, Team_Name, Country, Meta FROM teams WHERE Team_ID=%s", (tid,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    return r

print("DB row before upsert:", fetch_db_row(str(team_id)))

print("\n1) Upsert with API country (may be None)")
rc = upsert_team(mysql_secrets, str(team_id), Team_Name, Team_Country)
print("upsert_team returned:", rc)
print("DB row after upsert with API country:", fetch_db_row(str(team_id)))

print("\n2) If API country missing, demonstrate defaulting country -> team name and upsert")
if not Team_Country:
    defaulted_country = Team_Name
    print(f"Defaulting country to team name: '{defaulted_country}'")
    rc2 = upsert_team(mysql_secrets, str(team_id), Team_Name, defaulted_country)
    print("upsert_team returned:", rc2)
    print("DB row after upsert with defaulted country:", fetch_db_row(str(team_id)))
else:
    print("API provided country; no defaulting needed.")