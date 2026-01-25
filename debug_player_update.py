#!/usr/bin/env python3
"""
Debug player name update functionality
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

def debug_update():
    """Debug the update functionality"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    print("\n" + "=" * 70)
    print("DEBUGGING PLAYER UPDATE")
    print("=" * 70)
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Create a test player
        print("\n[1] Creating test player...")
        original_name = f"Debug Player {datetime.datetime.now().timestamp()}"
        player_id = db.insert_player(
            external_player_id="debug_update_test",
            player_name=original_name,
            country="India",
            role="Batsman",
            batting_style="Right",
            bowling_style="N/A",
            date_of_birth="2000-01-01"
        )
        print(f"✅ Created player with ID: {player_id}")
        
        # Verify player exists
        print("\n[2] Verifying player exists...")
        players_df = db.get_players()
        test_player = players_df[players_df["id"] == player_id]
        if not test_player.empty:
            print(f"✅ Found player: {test_player.iloc[0]['player_name']}")
        else:
            print(f"❌ Player not found!")
            return
        
        # Try direct update
        print("\n[3] Attempting direct update...")
        updated_name = f"Updated Debug Player {datetime.datetime.now().timestamp()}"
        print(f"   Before update - Player name: {original_name}")
        print(f"   Update query - SET player_name = '{updated_name}' WHERE id = {player_id}")
        
        # Execute raw query
        db.execute(f"UPDATE players SET player_name = %s WHERE id = %s", (updated_name, player_id))
        print(f"✅ Execute completed")
        
        # Check the result
        print("\n[4] Checking update result...")
        players_df = db.get_players()
        test_player = players_df[players_df["id"] == player_id]
        if not test_player.empty:
            actual_name = test_player.iloc[0]['player_name']
            print(f"   After update - Player name: {actual_name}")
            if actual_name == updated_name:
                print(f"✅ Update successful!")
            else:
                print(f"❌ Update failed - name is still: {actual_name}")
        else:
            print(f"❌ Player not found after update!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_update()
