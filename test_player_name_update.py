#!/usr/bin/env python3
"""
Test the updated player name change functionality
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
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"[SUCCESS] {msg}")

# Inject mock
import Cricbuzz.utils.db_connection as db_module
db_module.st = MockStreamlit()

def test_player_name_update():
    """Test updating player name"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    print("\n" + "=" * 70)
    print("TESTING PLAYER NAME UPDATE")
    print("=" * 70)
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Test 1: Create a test player
        print("\n[TEST 1] Creating test player...")
        original_name = f"Test Player {datetime.datetime.now().timestamp()}"
        player_id = db.insert_player(
            external_player_id="test_name_update",
            player_name=original_name,
            country="India",
            role="Batsman",
            batting_style="Right",
            bowling_style="N/A",
            date_of_birth="2000-01-01"
        )
        print(f"✅ Created player: '{original_name}' (ID: {player_id})")
        
        # Test 2: Update player name
        print("\n[TEST 2] Updating player name...")
        updated_name = f"Updated Player {datetime.datetime.now().timestamp()}"
        db.update_player(player_id, player_name=updated_name)
        print(f"✅ Updated name to: '{updated_name}'")
        
        # Test 3: Verify the update
        print("\n[TEST 3] Verifying update in database...")
        players_df = db.get_players()
        updated_player = players_df[players_df["id"] == player_id]
        
        if not updated_player.empty:
            actual_name = updated_player.iloc[0]["player_name"]
            if actual_name == updated_name:
                print(f"✅ Player name verified: '{actual_name}'")
            else:
                print(f"❌ Name mismatch! Expected: '{updated_name}', Got: '{actual_name}'")
        else:
            print(f"❌ Player not found in database")
        
        # Test 4: Update multiple fields including name
        print("\n[TEST 4] Updating multiple fields (name + role + country)...")
        new_name = f"All-rounder Player {datetime.datetime.now().timestamp()}"
        db.update_player(player_id, player_name=new_name, country="Australia", role="All-rounder")
        print(f"✅ Updated name, country, and role")
        
        # Verify multi-field update
        players_df = db.get_players()
        updated_player = players_df[players_df["id"] == player_id]
        if not updated_player.empty:
            row = updated_player.iloc[0]
            print(f"   - Name: {row['player_name']}")
            print(f"   - Country: {row['country']}")
            print(f"   - Role: {row['role']}")
            
            if row['player_name'] == new_name and row['country'] == "Australia" and row['role'] == "All-rounder":
                print(f"✅ All fields updated successfully")
            else:
                print(f"❌ Some fields not updated correctly")
        
        print("\n" + "=" * 70)
        print("✅ PLAYER NAME UPDATE TEST COMPLETED")
        print("=" * 70)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_player_name_update()
