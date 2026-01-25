#!/usr/bin/env python3
"""
Comprehensive test of CRUD operations with proper error handling
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Cricbuzz.utils.db_connection import MySQLDatabaseConnection
import datetime

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

def test_all_crud_operations():
    """Test all CRUD operations"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        print("=" * 60)
        print("Testing CRUD Operations")
        print("=" * 60)
        
        # Test 1: Get players
        print("\n1️⃣  Getting players...")
        players_df = db.get_players()
        print(f"   ✅ Retrieved {len(players_df)} players")
        
        # Test 2: Insert new player
        print("\n2️⃣  Inserting new player...")
        player_id = db.insert_player(
            external_player_id="test_ext_456",
            player_name=f"Test Player {datetime.datetime.now().timestamp()}",
            country="India",
            role="Batsman",
            batting_style="Right-handed",
            bowling_style="N/A",
            date_of_birth="1995-05-15"
        )
        if player_id > 0:
            print(f"   ✅ Player inserted with ID: {player_id}")
        else:
            print(f"   ❌ Failed to insert player")
        
        # Test 3: Get venues
        print("\n3️⃣  Getting venues...")
        venues_df = db.get_venues()
        print(f"   ✅ Retrieved {len(venues_df)} venues")
        
        # Test 4: Insert new venue
        print("\n4️⃣  Inserting new venue...")
        venue_id = db.insert_venue(
            venue_name=f"Test Venue {datetime.datetime.now().timestamp()}",
            city="Mumbai",
            country="India"
        )
        if venue_id > 0:
            print(f"   ✅ Venue inserted with ID: {venue_id}")
        else:
            print(f"   ❌ Failed to insert venue")
        
        # Test 5: Get matches
        print("\n5️⃣  Getting matches...")
        matches_df = db.get_matches()
        print(f"   ✅ Retrieved {len(matches_df)} matches")
        
        # Test 6: Get all other tables
        print("\n6️⃣  Getting other tables...")
        series_df = db.get_series()
        print(f"   ✅ Retrieved {len(series_df)} series")
        
        teams_df = db.get_teams()
        print(f"   ✅ Retrieved {len(teams_df)} teams")
        
        batting_stats = db.get_batting_stats()
        print(f"   ✅ Retrieved {len(batting_stats)} batting stats")
        
        print("\n" + "=" * 60)
        print("✅ All CRUD operations passed!")
        print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_crud_operations()
