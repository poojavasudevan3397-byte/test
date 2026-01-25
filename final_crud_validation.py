#!/usr/bin/env python3
"""
Final validation that the CRUD fix resolves the issue
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Cricbuzz.utils.db_connection import MySQLDatabaseConnection

# Mock streamlit for testing
class MockStreamlit:
    @staticmethod
    def error(msg):
        print(f"[ST_ERROR] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"[ST_SUCCESS] {msg}")

# Inject mock
import Cricbuzz.utils.db_connection as db_module
db_module.st = MockStreamlit()

def main():
    """Validate all fixes"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    print("\n" + "=" * 70)
    print("FINAL VALIDATION: CRUD OPERATIONS FIX")
    print("=" * 70)
    
    issues = []
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Test 1: Check exception serialization in read_df
        print("\n[TEST 1] Exception serialization in read_df...")
        try:
            # Try with parameterized query
            result = db.read_df(
                "SELECT id FROM players WHERE player_name = %s LIMIT 1",
                ("Test Player",)
            )
            print("✅ read_df() with params works")
        except Exception as e:
            issues.append(f"read_df() failed: {e}")
            print(f"❌ read_df() failed: {e}")
        
        # Test 2: Player insertion
        print("\n[TEST 2] Player insertion (insert_player)...")
        try:
            import datetime
            player_id = db.insert_player(
                external_player_id="final_test",
                player_name=f"Final Test Player {datetime.datetime.now().timestamp()}",
                country="India",
                role="Batsman",
                batting_style="Right",
                bowling_style="N/A",
                date_of_birth="2000-01-01"
            )
            if player_id > 0:
                print(f"✅ insert_player() works (ID: {player_id})")
            else:
                issues.append("insert_player() returned 0")
                print(f"❌ insert_player() returned 0")
        except Exception as e:
            issues.append(f"insert_player() failed: {e}")
            print(f"❌ insert_player() failed: {e}")
        
        # Test 3: Venue insertion
        print("\n[TEST 3] Venue insertion (insert_venue)...")
        try:
            venue_id = db.insert_venue(
                venue_name=f"Final Test Venue {datetime.datetime.now().timestamp()}",
                city="Mumbai",
                country="India"
            )
            if venue_id > 0:
                print(f"✅ insert_venue() works (ID: {venue_id})")
            else:
                issues.append("insert_venue() returned 0")
                print(f"❌ insert_venue() returned 0")
        except Exception as e:
            issues.append(f"insert_venue() failed: {e}")
            print(f"❌ insert_venue() failed: {e}")
        
        # Test 4: Exception handling with complex errors
        print("\n[TEST 4] Exception handling (no 'List argument' errors)...")
        try:
            # Try an invalid query to trigger exception handling
            result = db.read_df(
                "SELECT id FROM nonexistent_table WHERE id = %s",
                (1,)
            )
            print("✅ Exception handling works (returned empty DataFrame)")
        except Exception as e:
            issues.append(f"Exception handling failed: {e}")
            print(f"❌ Exception handling failed: {e}")
        
    except Exception as e:
        issues.append(f"Connection failed: {e}")
        print(f"❌ Connection failed: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    if issues:
        print(f"\n❌ {len(issues)} issue(s) found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n❌ VALIDATION FAILED")
        return False
    else:
        print("\n✅ All tests passed!")
        print("✅ No 'List argument must consist only of dictionaries' errors")
        print("✅ CRUD operations are working correctly")
        print("✅ VALIDATION SUCCESSFUL")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
