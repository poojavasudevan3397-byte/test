"""
Final verification test - Exact flow from live_matches.py venue sync
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from utils.mysql_sync import upsert_venue, create_mysql_schema
from utils.api_client import extract_venue_metadata
import json

# Test database config
mysql_secrets = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

print("=" * 80)
print("FINAL VERIFICATION: Live Matches Venue Sync Flow")
print("=" * 80)

# Create schema
print("\n✅ Step 1: Schema initialization")
create_mysql_schema(mysql_secrets)

# Test multiple venues as would happen in live_matches.py
test_venues = [
    {
        "id": "991",
        "ground": "MCG",
        "city": "Melbourne",
        "country": "Australia",
        "timezone": "UTC+10",
        "capacity": 100024
    },
    {
        "id": "992",
        "ground": "SCG",
        "city": "Sydney",
        "country": "Australia",
        "timezone": "UTC+10",
        "capacity": 48000
    },
    {
        "id": "993",
        "ground": "Arun Jaitley Stadium",
        "city": "Delhi",
        "country": "India",
        "timezone": "UTC+5:30",
        "capacity": 41820
    },
]

print("\n✅ Step 2: Process and insert multiple venues")
insert_count = 0
for idx, venue_profile in enumerate(test_venues, 1):
    print(f"\n   [{idx}/{len(test_venues)}] Processing {venue_profile.get('ground')}...")
    
    # This is the exact flow from live_matches.py:
    # Step A: Fetch venue profile (simulated here)
    # Step B: Extract metadata
    venue_record = extract_venue_metadata(venue_profile)
    
    # Step C: Check for required fields
    if venue_record.get("Venue_ID") and venue_record.get("Venue_Name"):
        # Step D: Upsert to database
        v_rc = upsert_venue(mysql_secrets, venue_record)
        if v_rc and v_rc > 0:
            insert_count += 1
            print(f"      ✅ Inserted: {venue_record['Venue_Name']} (ID={venue_record['Venue_ID']}, TZ={venue_record.get('Time_Zone')})")
        else:
            print(f"      ⚠️ Update returned {v_rc}: {venue_record['Venue_Name']}")
    else:
        print(f"      ❌ Skipped: Missing ID or Name")

print(f"\n✅ Step 3: Results - {insert_count} venues inserted/updated")

# Verify all venues in database
print("\n✅ Step 4: Database verification")
try:
    import pymysql
    conn = pymysql.connect(
        host=mysql_secrets["host"],
        user=mysql_secrets["user"],
        password=mysql_secrets["password"],
        database=mysql_secrets["database"],
        port=mysql_secrets["port"],
        charset="utf8mb4"
    )
    with conn.cursor() as cur:
        cur.execute("""
            SELECT Venue_ID, Venue_Name, City, Country, Time_Zone 
            FROM venues 
            WHERE Venue_ID IN ('991', '992', '993')
            ORDER BY Venue_ID
        """)
        rows = cur.fetchall()
        print(f"\n   Found {len(rows)} venues in database:")
        for row in rows:
            print(f"      - ID: {row[0]}, Name: {row[1]}, City: {row[2]}, Country: {row[3]}, TZ: {row[4]}")
        
        if len(rows) == 3:
            print("\n   ✅ SUCCESS: All test venues inserted correctly!")
        else:
            print(f"\n   ⚠️ WARNING: Expected 3 venues, found {len(rows)}")
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("VENUE SYNC FIX COMPLETE")
print("=" * 80)
