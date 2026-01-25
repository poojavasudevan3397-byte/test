"""
Test updated CRUD operations with external_player_id and date_of_birth
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.db_connection import get_db_connection

def test_updated_crud():
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306
    }
    
    try:
        db = get_db_connection(mysql_secrets)
        
        print("\n1. Testing insert_player with external_player_id and date_of_birth...")
        pid = db.insert_player(
            external_player_id="9999",
            player_name="New Test Player",
            country="Australia",
            role="All-rounder",
            batting_style="Left",
            bowling_style="Right",
            date_of_birth="1995-06-15"
        )
        print(f"   OK - Player inserted with ID: {pid}")
        
        print("\n2. Testing get_players with all columns...")
        players = db.get_players()
        print(f"   OK - Retrieved {len(players)} players")
        print(f"   Columns: {list(players.columns)}")
        
        # Show the newly added player
        new_player = players[players['player_name'] == 'New Test Player']
        if len(new_player) > 0:
            print(f"\n   New player details:")
            for col in new_player.columns:
                print(f"     {col}: {new_player.iloc[0][col]}")
        
        print("\nSUCCESS - Updated CRUD with external_player_id and date_of_birth!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_updated_crud()
    sys.exit(0 if success else 1)
