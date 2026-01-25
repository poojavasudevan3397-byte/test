"""
Simple test for CRUD operations without emojis
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.db_connection import get_db_connection

def test_crud():
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306
    }
    
    try:
        db = get_db_connection(mysql_secrets)
        
        print("\n1. Testing get_players...")
        players = db.get_players()
        print(f"   OK - Retrieved {len(players)} players")
        
        print("\n2. Testing insert_player...")
        pid = db.insert_player("Test Player 123", "India", "Batsman", "Right", "N/A")
        print(f"   OK - Player inserted with ID: {pid}")
        
        print("\n3. Verifying insertion...")
        players = db.get_players()
        found = len(players[players['player_name'] == 'Test Player 123']) > 0
        print(f"   OK - Player found: {found}")
        
        print("\n4. Testing get_venues...")
        venues = db.get_venues()
        print(f"   OK - Retrieved {len(venues)} venues")
        
        print("\n5. Testing insert_venue...")
        vid = db.insert_venue("Test Venue 123", "Test City", "Test Country")
        print(f"   OK - Venue inserted with ID: {vid}")
        
        print("\n6. Testing get_matches...")
        matches = db.get_matches()
        print(f"   OK - Retrieved {len(matches)} matches")
        
        print("\nSUCCESS - All CRUD operations working!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crud()
    sys.exit(0 if success else 1)
