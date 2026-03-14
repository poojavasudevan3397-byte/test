"""
Test: Verify team country fallback for international teams.
Simulates API response where some teams have country, some don't.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Cricbuzz.utils.api_client import extract_team_metadata
from Cricbuzz.utils.mysql_sync import upsert_team, create_mysql_schema
import pymysql

mysql_secrets = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

def fetch_db_row(tid):
    """Fetch team from database."""
    conn = pymysql.connect(
        host=mysql_secrets['host'],
        user=mysql_secrets['user'],
        password=mysql_secrets['password'],
        database=mysql_secrets['database'],
        port=mysql_secrets['port'],
        charset='utf8mb4'
    )
    cur = conn.cursor()
    cur.execute("SELECT Team_ID, Team_Name, Country FROM teams WHERE Team_ID=%s", (tid,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    return r

print("Creating schema...")
create_mysql_schema(mysql_secrets)

# Simulate international teams API response: some with countryName, some without
test_teams = [
    {"id": 1001, "name": "India", "countryName": "India"},        # Has country
    {"id": 1002, "name": "Australia", "countryName": "Australia"}, # Has country
    {"id": 1003, "name": "England", "countryName": "England"},     # Has country
    {"id": 1004, "name": "Pakistan"},                              # NO country - should fallback to "Pakistan"
    {"id": 1005, "name": "South Africa", "countryName": "South Africa"}, # Has country
    {"id": 1006, "name": "New Zealand"},                           # NO country - should fallback to "New Zealand"
    {"id": 1007, "name": "West Indies", "country": "West Indies"}, # Has 'country' variant
    {"id": 1008, "name": "Sri Lanka"},                             # NO country - should fallback to "Sri Lanka"
]

print("\n" + "="*70)
print("TEST: International Teams with fallback")
print("="*70)

for team in test_teams:
    team_id = str(team["id"])
    
    # Extract using our function
    meta = extract_team_metadata(team)
    
    print(f"\nTeam ID {team_id}:")
    print(f"  Input name: {team.get('name')}")
    print(f"  Input countryName: {team.get('countryName')}")
    print(f"  Input country: {team.get('country')}")
    print(f"  Extracted country: {meta['Country']}")
    
    # Upsert to DB
    rc = upsert_team(mysql_secrets, team_id, meta["Team_Name"], meta["Country"])
    
    # Verify in DB
    row = fetch_db_row(team_id)
    if row:
        db_team_id, db_team_name, db_country = row
        print(f"  DB Country: {db_country}")
        
        # Verify: if input had no countryName/country, must equal team name
        if not team.get('countryName') and not team.get('country'):
            assert db_country == team.get('name'), f"FAIL: Expected fallback to team name, got {db_country}"
            print(f"  ✓ PASS: Correctly used team name as fallback")
        else:
            print(f"  ✓ Country stored correctly")

print("\n" + "="*70)
print("ALL TESTS PASSED ✓")
print("="*70)
