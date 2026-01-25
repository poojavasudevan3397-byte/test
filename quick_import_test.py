"""
Quick test to verify insert_player works without import errors
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.db_connection import get_db_connection

mysql_secrets = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306
}

try:
    db = get_db_connection(mysql_secrets)
    print("Testing insert_player method...")
    pid = db.insert_player(
        external_player_id="TEST123",
        player_name="Quick Test Player",
        country="India",
        role="Batsman"
    )
    print(f"SUCCESS - Player inserted without import errors!")
    print(f"Player ID: {pid}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
