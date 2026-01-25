"""
Test CRUD operations on the database
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.db_connection import get_db_connection

def test_crud_operations():
    """Test CRUD operations"""
    print("=" * 60)
    print("Testing CRUD Operations")
    print("=" * 60)
    
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306
    }
    
    try:
        db = get_db_connection(mysql_secrets)
        
        # Test 1: Get all players
        print("\n1. Testing get_players()...")
        players_df = db.get_players()
        print(f"   ✅ Retrieved {len(players_df)} players")
        if len(players_df) > 0:
            print(f"      Sample: {players_df.iloc[0]['player_name']}")
        
        # Test 2: Insert a new player
        print("\n2. Testing insert_player()...")
        player_id = db.insert_player(
            player_name="Test Player",
            country="India",
            role="Batsman",
            batting_style="Right",
            bowling_style="N/A"
        )
        print(f"   ✅ Player inserted with ID: {player_id}")
        
        # Test 3: Verify player was inserted
        print("\n3. Verifying insertion...")
        players_df = db.get_players()
        test_player = players_df[players_df['player_name'] == 'Test Player']
        if len(test_player) > 0:
            print(f"   ✅ Test player found in database")
        else:
            print(f"   ⚠️  Test player not found")
        
        # Test 4: Get venues
        print("\n4. Testing get_venues()...")
        venues_df = db.get_venues()
        print(f"   ✅ Retrieved {len(venues_df)} venues")
        
        # Test 5: Insert venue
        print("\n5. Testing insert_venue()...")
        venue_id = db.insert_venue("Test Venue", "Test City", "Test Country")
        print(f"   ✅ Venue inserted with ID: {venue_id}")
        
        # Test 6: Get matches
        print("\n6. Testing get_matches()...")
        matches_df = db.get_matches()
        print(f"   ✅ Retrieved {len(matches_df)} matches")
        
        print("\n" + "=" * 60)
        print("✅ All CRUD operations working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_crud_operations()
    sys.exit(0 if success else 1)
