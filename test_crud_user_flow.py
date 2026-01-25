#!/usr/bin/env python3
"""
Test scenario matching the CRUD page user experience
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Cricbuzz.utils.db_connection import MySQLDatabaseConnection
import datetime

# Mock streamlit for testing
class MockStreamlit:
    def __init__(self):
        self.errors = []
        self.successes = []
    
    def error(self, msg):
        self.errors.append(msg)
        print(f"🔴 ERROR: {msg}")
    
    def success(self, msg):
        self.successes.append(msg)
        print(f"🟢 SUCCESS: {msg}")

# Inject mock
import Cricbuzz.utils.db_connection as db_module
mock_st = MockStreamlit()
db_module.st = mock_st

def simulate_crud_page_user_flow():
    """Simulate the exact flow of a user using the CRUD page"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    print("\n" + "=" * 70)
    print("SIMULATING STREAMLIT CRUD PAGE USER FLOW")
    print("=" * 70)
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Scenario 1: User navigates to CRUD page
        print("\n📍 User navigates to CRUD → Operations → Players → Create")
        print("   Loading existing players...")
        players_df = db.get_players()
        print(f"   ✅ Page loaded with {len(players_df)} existing players")
        
        # Scenario 2: User fills in the form
        timestamp = datetime.datetime.now().timestamp()
        player_data = {
            "external_player_id": f"ext_{int(timestamp)}",
            "player_name": f"Virat Kohli Test {timestamp}",
            "country": "India",
            "role": "Batsman",
            "batting_style": "Right-handed",
            "bowling_style": "N/A",
            "date_of_birth": "1988-11-05"
        }
        
        print("\n📝 User fills in player form:")
        for key, value in player_data.items():
            print(f"   {key}: {value}")
        
        # Scenario 3: User clicks submit
        print("\n🔘 User clicks 'Create Player' button")
        player_id = db.insert_player(
            external_player_id=player_data["external_player_id"],
            player_name=player_data["player_name"],
            country=player_data["country"],
            role=player_data["role"],
            batting_style=player_data["batting_style"],
            bowling_style=player_data["bowling_style"],
            date_of_birth=player_data["date_of_birth"]
        )
        
        if player_id > 0:
            print(f"\n✅ Player successfully created with ID: {player_id}")
        else:
            print(f"\n❌ Failed to create player")
            return False
        
        # Scenario 4: Verify player was created
        print("\n🔍 Verifying player in database...")
        all_players = db.get_players()
        player_names = all_players["player_name"].tolist()
        
        if player_data["player_name"] in player_names:
            print(f"   ✅ Player '{player_data['player_name']}' found in database!")
        else:
            print(f"   ❌ Player not found in database")
            return False
        
        # Scenario 5: Test venue creation
        print("\n📍 User navigates to CRUD → Operations → Venues → Create")
        print("   Loading existing venues...")
        venues_df = db.get_venues()
        print(f"   ✅ Page loaded with {len(venues_df)} existing venues")
        
        venue_data = {
            "venue_name": f"Test Stadium {timestamp}",
            "city": "Mumbai",
            "country": "India"
        }
        
        print("\n📝 User fills in venue form:")
        for key, value in venue_data.items():
            print(f"   {key}: {value}")
        
        print("\n🔘 User clicks 'Create Venue' button")
        venue_id = db.insert_venue(
            venue_name=venue_data["venue_name"],
            city=venue_data["city"],
            country=venue_data["country"]
        )
        
        if venue_id > 0:
            print(f"\n✅ Venue successfully created with ID: {venue_id}")
        else:
            print(f"\n❌ Failed to create venue")
            return False
        
        # Final check
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        print(f"✅ Player Creation: SUCCESS (ID: {player_id})")
        print(f"✅ Venue Creation: SUCCESS (ID: {venue_id})")
        
        if mock_st.errors:
            print(f"\n❌ Errors encountered: {len(mock_st.errors)}")
            for err in mock_st.errors:
                print(f"   - {err}")
            return False
        else:
            print(f"\n✅ No errors encountered!")
        
        if mock_st.successes:
            print(f"✅ Success messages: {len(mock_st.successes)}")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - CRUD PAGE IS READY!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = simulate_crud_page_user_flow()
    sys.exit(0 if success else 1)
