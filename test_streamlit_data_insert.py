"""
Test script to verify Streamlit app can insert data into MySQL
This simulates the live_matches page data insertion workflow
"""

import sys
sys.path.insert(0, r'd:\test\cricbuzz_app')

from utils.mysql_sync import create_mysql_schema, upsert_match
from typing import Dict, Any

# MySQL credentials
mysql_secrets: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

# Test match data (simulating what comes from API)
test_match = {
    "matchId": "test_123456",
    "matchIdRaw": "test_123456",
    "seriesName": "Test Series",
    "seriesId": "test_series_1",
    "matchDesc": "Test Match Description",
    "matchFormat": "T20",
    "startDate": 1732300800000,  # Some timestamp
    "state": "Complete",
    "status": "Test Result",
    "team1": {
        "teamId": 1,
        "teamName": "Team A",
        "teamSName": "TA"
    },
    "team2": {
        "teamId": 2,
        "teamName": "Team B",
        "teamSName": "TB"
    },
    "venue": "Test Venue",
    "venueInfo": {
        "ground": "Test Ground"
    }
}

print("=" * 60)
print("Testing Streamlit Data Insertion to MySQL")
print("=" * 60)

try:
    print("\n1. Creating MySQL schema...")
    create_mysql_schema(mysql_secrets)
    print("   ✓ Schema created successfully")
except Exception as e:
    print(f"   ✗ Error creating schema: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n2. Upserting test match...")
    upsert_match(mysql_secrets, test_match)
    print("   ✓ Match inserted successfully")
except Exception as e:
    print(f"   ✗ Error inserting match: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n3. Verifying data in database...")
    import pymysql
    conn = pymysql.connect(
        host=mysql_secrets['host'],
        user=mysql_secrets['user'],
        password=mysql_secrets['password'],
        database=mysql_secrets['database'],
        port=mysql_secrets['port']
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM matches")
    match_count = cursor.fetchone()[0]
    print(f"   ✓ Total matches in DB: {match_count}")
    
    cursor.execute("SELECT external_match_id, series_name, team1, team2 FROM matches ORDER BY id DESC LIMIT 3")
    recent_matches = cursor.fetchall()
    print(f"   ✓ Recent matches:")
    for m in recent_matches:
        print(f"      - {m[0]}: {m[1]} ({m[2]} vs {m[3]})")
    
    cursor.close()
    conn.close()
    print("\n✅ Test completed successfully!")
    
except Exception as e:
    print(f"   ✗ Error verifying data: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
