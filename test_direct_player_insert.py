#!/usr/bin/env python3
"""Direct test of player insertion to MySQL database."""

import sys
import os
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricbuzz_app'))

import pymysql  # type: ignore[import]
import json

# MySQL config
mysql_config: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

print("=" * 80)
print("DIRECT PLAYER INSERTION TEST")
print("=" * 80)

# Test inserting sample players
test_players = [
    {
        "id": "8001",
        "name": "Test Player Live (Direct Insert)",
        "battingStyle": "Right-hand bat",
        "bowlingStyle": "Right-arm medium",
        "imageId": "test_img_001"
    },
    {
        "id": "8002",
        "name": "Another Test Player",
        "battingStyle": "Left-hand bat",
        "bowlingStyle": "Left-arm orthodox",
        "imageId": "test_img_002"
    },
]

try:
    print("\n[1] Connecting to MySQL...")
    conn: Any = pymysql.connect(**mysql_config)  # type: ignore[reportUnknownArgumentType]
    cursor: Any = conn.cursor()
    print("[OK] Connected")
    
    print("\n[2] Inserting test players...")
    inserted_count = 0
    
    for player in test_players:
        external_player_id = str(player.get('id', ''))
        player_name = str(player.get('name', ''))
        batting_style = str(player.get('battingStyle', ''))
        bowling_style = str(player.get('bowlingStyle', ''))
        image_id = str(player.get('imageId', ''))
        
        meta = json.dumps({
            "batting_style": batting_style,
            "bowling_style": bowling_style,
            "image_id": image_id
        })
        
        sql = "INSERT IGNORE INTO players (external_player_id, player_name, country, role, meta) VALUES (%s, %s, %s, %s, %s)"
        params = (external_player_id, player_name, "", "", meta)
        
        try:
            cursor.execute(sql, params)
            if cursor.rowcount > 0:
                print(f"  [+] Inserted: {player_name}")
                inserted_count += cursor.rowcount
            else:
                print(f"  [-] Already exists: {player_name}")
        except Exception as e:
            print(f"  [X] Error inserting {player_name}: {e}")
    
    conn.commit()
    print(f"\n[OK] {inserted_count} player(s) inserted")
    
    # Verify insertion
    print("\n[3] Verifying insertion...")
    cursor.execute("SELECT COUNT(*) as count FROM players WHERE external_player_id IN ('8001', '8002')")
    result = cursor.fetchone()
    count = result[0] if result else 0
    print(f"  Found {count} test players in database")
    
    if count > 0:
        cursor.execute("SELECT id, external_player_id, player_name FROM players WHERE external_player_id IN ('8001', '8002') ORDER BY created_at DESC")
        rows = cursor.fetchall()
        for row in rows:
            print(f"    - ID {row[0]}: {row[2]} (external_id: {row[1]})")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE - Players inserted successfully!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n[X] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
