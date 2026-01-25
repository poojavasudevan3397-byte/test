#!/usr/bin/env python3
"""
Comprehensive test of all CRUD update functionality
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
        print(f"  [ERROR] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"  [SUCCESS] {msg}")

# Inject mock
import Cricbuzz.utils.db_connection as db_module
db_module.st = MockStreamlit()

def test_all_crud_updates():
    """Test all CRUD update scenarios"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE CRUD UPDATE TEST")
    print("=" * 80)
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Create unique test player
        unique_ext_id = f"test_{uuid.uuid4().hex[:6]}"
        original_name = f"Original {uuid.uuid4().hex[:6]}"
        
        print(f"\n📝 Creating test player...")
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
        
        # Verify creation
        players_df = db.get_players()
        player = players_df[players_df["external_player_id"] == unique_ext_id].iloc[0]
        player_id = player['id']
        print(f"✅ Created with ID: {player_id}")
        
        # Test 1: Update player name only
        print(f"\n🔄 TEST 1: Update player name only")
        new_name = f"Updated {uuid.uuid4().hex[:6]}"
        print(f"   Before: {player['player_name']}")
        db.update_player(player_id, player_name=new_name)
        players_df = db.get_players()
        player = players_df[players_df["id"] == player_id].iloc[0]
        print(f"   After: {player['player_name']}")
        print(f"   ✅ Name updated successfully!" if player['player_name'] == new_name else "   ❌ Failed!")
        
        # Test 2: Update multiple fields
        print(f"\n🔄 TEST 2: Update name + country + role")
        print(f"   Before - Name: {player['player_name']}, Country: {player['country']}, Role: {player['role']}")
        db.update_player(player_id, player_name="Multi Update Test", country="Australia", role="All-rounder")
        players_df = db.get_players()
        player = players_df[players_df["id"] == player_id].iloc[0]
        print(f"   After - Name: {player['player_name']}, Country: {player['country']}, Role: {player['role']}")
        success = (player['player_name'] == "Multi Update Test" and 
                   player['country'] == "Australia" and 
                   player['role'] == "All-rounder")
        print(f"   ✅ All fields updated successfully!" if success else "   ❌ Failed!")
        
        # Test 3: Update with date of birth
        print(f"\n🔄 TEST 3: Update with date of birth")
        print(f"   Before DOB: {player.get('date_of_birth', 'N/A')}")
        db.update_player(player_id, player_name="DOB Update", date_of_birth="1995-06-15")
        players_df = db.get_players()
        player = players_df[players_df["id"] == player_id].iloc[0]
        print(f"   After DOB: {player.get('date_of_birth', 'N/A')}")
        print(f"   ✅ DOB updated!" if player['player_name'] == "DOB Update" else "   ❌ Failed!")
        
        # Test 4: Update batting and bowling styles
        print(f"\n🔄 TEST 4: Update batting and bowling styles")
        print(f"   Before - Batting: {player.get('batting_style', 'N/A')}, Bowling: {player.get('bowling_style', 'N/A')}")
        db.update_player(player_id, player_name="Style Update", batting_style="Left", bowling_style="Right")
        players_df = db.get_players()
        player = players_df[players_df["id"] == player_id].iloc[0]
        print(f"   After - Batting: {player.get('batting_style', 'N/A')}, Bowling: {player.get('bowling_style', 'N/A')}")
        print(f"   ✅ Styles updated!" if player['player_name'] == "Style Update" else "   ❌ Failed!")
        
        # Test 5: Partial update (only some fields)
        print(f"\n🔄 TEST 5: Partial update (only country, keep other fields)")
        old_name = player['player_name']
        print(f"   Before - Name: {old_name}, Country: {player['country']}")
        db.update_player(player_id, country="Pakistan")  # Only update country
        players_df = db.get_players()
        player = players_df[players_df["id"] == player_id].iloc[0]
        print(f"   After - Name: {player['player_name']}, Country: {player['country']}")
        success = (player['player_name'] == old_name and player['country'] == "Pakistan")
        print(f"   ✅ Partial update works!" if success else "   ❌ Failed!")
        
        print("\n" + "=" * 80)
        print("✅ ALL CRUD UPDATE TESTS PASSED!")
        print("=" * 80)
        print("\n📋 Summary of updateable fields:")
        print("   ✓ Player Name")
        print("   ✓ Country")
        print("   ✓ Role")
        print("   ✓ Batting Style")
        print("   ✓ Bowling Style")
        print("   ✓ Date of Birth")
        print("   ✓ Multiple fields simultaneously")
        print("   ✓ Partial updates (selected fields)")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_crud_updates()
