#!/usr/bin/env python3
"""
Test the CRUD fix for exception serialization
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

def test_insert_player():
    """Test player insertion with proper error handling"""
    secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }
    
    try:
        db = MySQLDatabaseConnection(secrets)
        
        # Try to insert a player
        player_id = db.insert_player(
            external_player_id="test_ext_123",
            player_name="Test Player Unique 999",
            country="India",
            role="All-rounder",
            batting_style="Right-handed",
            bowling_style="Right-arm",
            date_of_birth="2000-01-01"
        )
        
        if player_id > 0:
            print(f"✅ Player insertion successful! ID: {player_id}")
        else:
            print(f"⚠️ Player insertion returned ID: {player_id}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_insert_player()
