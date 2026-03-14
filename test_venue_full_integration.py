"""
Full integration test - simulate the venue sync flow from live_matches.py
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
print("VENUE INSERTION INTEGRATION TEST")
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

# Simulate venue_profile from API
print("\n2. Simulating venue_profile from api_client.get_venue_profile()...")
venue_profile = {
    "id": "789",
    "ground": "Lords Cricket Ground",
    "city": "London",
    "country": "England",
    "timezone": "UTC+0",
    "capacity": 30000
}
print(f"   venue_profile from API: {json.dumps(venue_profile, indent=2)}")

# Use extract_venue_metadata
print("\n3. Processing with extract_venue_metadata()...")
try:
    venue_record = extract_venue_metadata(venue_profile)
    print(f"   venue_record after extraction: {json.dumps(venue_record, indent=2)}")
except Exception as e:
    print(f"   ❌ Error in extract_venue_metadata: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check if we have required fields
print("\n4. Validating required fields...")
has_id = venue_record.get("Venue_ID")
has_name = venue_record.get("Venue_Name")
print(f"   Venue_ID: {has_id}")
print(f"   Venue_Name: {has_name}")

if has_id and has_name:
    print("\n5. Attempting upsert_venue()...")
    try:
        v_rc = upsert_venue(mysql_secrets, venue_record)
        print(f"   ✅ upsert_venue returned: {v_rc}")
        if v_rc and v_rc > 0:
            print(f"   ✅ SUCCESS: Venue '{has_name}' (ID={has_id}) inserted!")
        else:
            print(f"   ⚠️ upsert_venue returned {v_rc} (may indicate update, not insert)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"\n5. ❌ FAILED: Missing required fields - Venue_ID={has_id}, Venue_Name={has_name}")
    sys.exit(1)

# Verify in database
print("\n6. Verifying data in venues table...")
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
        cur.execute("SELECT ID, Venue_ID, Venue_Name, City, Country, Time_Zone FROM venues WHERE Venue_ID = %s;", ("789",))
        row = cur.fetchone()
        if row:
            print(f"   ✅ Found venue in database:")
            print(f"      - DB ID={row[0]}, Venue_ID={row[1]}, Venue_Name={row[2]}, City={row[3]}, Country={row[4]}, Time_Zone={row[5]}")
        else:
            print(f"   ❌ Venue NOT found in database!")
    conn.close()
except Exception as e:
    print(f"   ❌ Error querying database: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
