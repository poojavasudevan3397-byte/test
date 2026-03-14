"""
Test script to debug venue insertion issue
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from utils.mysql_sync import upsert_venue, create_mysql_schema
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
print("VENUE INSERTION TEST")
print("=" * 80)

# Create schema first
print("\n1. Creating schema...")
try:
    create_mysql_schema(mysql_secrets)
    print("✅ Schema created/verified")
except Exception as e:
    print(f"❌ Schema error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test Case 1: Venue with Venue_ID/Venue_Name keys (from extract_venue_metadata)
print("\n2. Testing with Venue_ID/Venue_Name keys (expected from API)...")
venue_data_1 = {
    "Venue_ID": "123",
    "Venue_Name": "Eden Gardens",
    "City": "Kolkata",
    "Country": "India",
    "Time_Zone": "UTC+5:30",
    "Meta": {}
}
print(f"   Input: {json.dumps(venue_data_1, indent=2)}")
try:
    rc = upsert_venue(mysql_secrets, venue_data_1)
    print(f"   ✅ upsert_venue returned: {rc}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test Case 2: Venue with id/ground keys (raw API format)
print("\n3. Testing with id/ground keys (raw API format)...")
venue_data_2 = {
    "id": "456",
    "ground": "Wankhede Stadium",
    "city": "Mumbai",
    "country": "India",
    "timezone": "UTC+5:30"
}
print(f"   Input: {json.dumps(venue_data_2, indent=2)}")
try:
    rc = upsert_venue(mysql_secrets, venue_data_2)
    print(f"   ✅ upsert_venue returned: {rc}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test Case 3: Venue with missing id (should skip)
print("\n4. Testing with missing ID (should skip)...")
venue_data_3 = {
    "Venue_Name": "MCG",
    "City": "Melbourne",
    "Country": "Australia"
}
print(f"   Input: {json.dumps(venue_data_3, indent=2)}")
try:
    rc = upsert_venue(mysql_secrets, venue_data_3)
    print(f"   ✅ upsert_venue returned: {rc} (expected 0 due to missing ID)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test Case 4: Verify data in database
print("\n5. Verifying data in venues table...")
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
        cur.execute("SELECT ID, Venue_ID, Venue_Name, City, Country FROM venues;")
        rows = cur.fetchall()
        if rows:
            print(f"   ✅ Found {len(rows)} venue(s) in database:")
            for row in rows:
                print(f"      - ID={row[0]}, Venue_ID={row[1]}, Venue_Name={row[2]}, City={row[3]}, Country={row[4]}")
        else:
            print(f"   ❌ No venues found in database!")
    conn.close()
except Exception as e:
    print(f"   ❌ Error querying database: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
