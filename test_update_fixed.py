#!/usr/bin/env python3
"""
Better test for player name update with unique external ID lookup
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Cricbuzz.utils.db_connection import MySQLDatabaseConnection
import datetime
import uuid

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

def test_update_with_unique_id():
    """Test update with unique external ID"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    print("\n" + "=" * 70)
    print("TESTING PLAYER NAME UPDATE WITH UNIQUE EXTERNAL ID")
    print("=" * 70)
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Create unique identifiers
        unique_ext_id = f"upd_{uuid.uuid4().hex[:8]}"
        original_name = f"Player {uuid.uuid4().hex[:8]}"
        updated_name = f"Updated {uuid.uuid4().hex[:8]}"
        
        print(f"\n[1] Creating test player...")
        print(f"   External ID: {unique_ext_id}")
        print(f"   Name: {original_name}")
        
        player_id = db.insert_player(
            external_player_id=unique_ext_id,
            player_name=original_name,
            country="India",
            role="Batsman",
            batting_style="Right",
            bowling_style="N/A",
            date_of_birth="2000-01-01"
        )
        print(f"✅ Created player with ID: {player_id}")
        
        # Verify by external ID (more reliable)
        print(f"\n[2] Verifying player exists by external ID...")
        players_df = db.get_players()
        test_player = players_df[players_df["external_player_id"] == unique_ext_id]
        if not test_player.empty:
            found_id = test_player.iloc[0]['id']
            found_name = test_player.iloc[0]['player_name']
            print(f"✅ Found player ID: {found_id}, Name: {found_name}")
            player_id = found_id  # Use the found ID to be sure
        else:
            print(f"❌ Player not found by external ID!")
            return
        
        # Update player name
        print(f"\n[3] Updating player name...")
        print(f"   From: {original_name}")
        print(f"   To: {updated_name}")
        db.update_player(player_id, player_name=updated_name)
        print(f"✅ Update completed")
        
        # Verify update by external ID
        print(f"\n[4] Verifying update by external ID...")
        players_df = db.get_players()
        test_player = players_df[players_df["external_player_id"] == unique_ext_id]
        if not test_player.empty:
            actual_name = test_player.iloc[0]['player_name']
            print(f"   Current name: {actual_name}")
            if actual_name == updated_name:
                print(f"✅ UPDATE SUCCESSFUL!")
            else:
                print(f"❌ Update failed - name is still: {actual_name}")
        else:
            print(f"❌ Player not found after update!")
        
        # Test multiple field update
        print(f"\n[5] Testing multiple field update...")
        db.update_player(player_id, player_name="Multi Updated", country="Pakistan", role="All-rounder")
        
        players_df = db.get_players()
        test_player = players_df[players_df["external_player_id"] == unique_ext_id]
        if not test_player.empty:
            row = test_player.iloc[0]
            print(f"   Name: {row['player_name']}")
            print(f"   Country: {row['country']}")
            print(f"   Role: {row['role']}")
            if row['player_name'] == "Multi Updated" and row['country'] == "Pakistan" and row['role'] == "All-rounder":
                print(f"✅ MULTI-FIELD UPDATE SUCCESSFUL!")
            else:
                print(f"❌ Some fields not updated")
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETED")
        print("=" * 70)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_update_with_unique_id()
