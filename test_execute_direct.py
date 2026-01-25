#!/usr/bin/env python3
"""
Test execute method directly
"""
import pymysql
from pymysql.cursors import DictCursor

def test_execute():
    """Test executing update directly"""
    
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Vasu@76652",
        database="cricketdb",
        port=3306,
        charset="utf8mb4",
        cursorclass=DictCursor,
    )
    
    try:
        # Get a test player
        cur = connection.cursor()
        cur.execute("SELECT id, player_name FROM players LIMIT 1")
        player = cur.fetchone()
        player_id = player['id']
        old_name = player['player_name']
        
        print(f"Found player: ID={player_id}, Name={old_name}")
        
        # Try to update
        new_name = "Directly Updated Name"
        print(f"\nAttempting update to: {new_name}")
        
        cur.execute("UPDATE players SET player_name = %s WHERE id = %s", (new_name, player_id))
        print(f"Rows affected: {cur.rowcount}")
        
        connection.commit()
        print("Committed")
        
        # Verify
        cur.execute("SELECT player_name FROM players WHERE id = %s", (player_id,))
        result = cur.fetchone()
        print(f"Verification - Name after update: {result['player_name']}")
        
        # Revert
        cur.execute("UPDATE players SET player_name = %s WHERE id = %s", (old_name, player_id))
        connection.commit()
        print("Reverted to original")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    test_execute()
