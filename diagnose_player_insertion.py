#!/usr/bin/env python3
"""Comprehensive test to diagnose player insertion issues."""

import sys
import os
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricbuzz_app'))

import pymysql  # type: ignore[import]
from utils.mysql_sync import create_mysql_schema, upsert_match  # type: ignore[reportMissingImports]
from utils.api_client import CricbuzzAPI  # type: ignore[reportMissingImports]

# MySQL config
mysql_config: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

print("=" * 80)
print("PLAYER INSERTION DIAGNOSTIC TEST")
print("=" * 80)

# Step 1: Verify schema exists
print("\n[STEP 1] Verifying MySQL schema...")
try:
    create_mysql_schema(mysql_config)
    print("✓ Schema created/verified")
except Exception as e:
    print(f"✗ Schema error: {e}")
    sys.exit(1)

# Step 2: Check if players table exists
print("\n[STEP 2] Checking players table...")
try:
    conn: Any = pymysql.connect(**mysql_config)  # type: ignore[reportUnknownArgumentType]
    cursor: Any = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SHOW TABLES LIKE 'players'")
    if cursor.fetchone():
        print("✓ Players table exists")
    else:
        print("✗ Players table does NOT exist")
        sys.exit(1)
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Error checking table: {e}")
    sys.exit(1)

# Step 3: Get recent matches from API
print("\n[STEP 3] Fetching recent matches from Cricbuzz API...")
try:
    api_key = "7d43f4bd53msh4abaa77fb5edf80p14c624jsn6982e9f7e18b"
    api_client: Any = CricbuzzAPI(api_key)  # type: ignore[reportUnknownVariableType]
    matches_data: Any = api_client.get_recent_matches()  # type: ignore[reportUnknownVariableType]
    
    if not matches_data:
        print("✗ No matches retrieved from API")
        sys.exit(1)
    
    print(f"✓ Retrieved {len(matches_data)} matches")
    
    # Show first match details
    if matches_data:
        first_match = matches_data[0]
        print(f"\n  First match: {first_match.get('matchDesc', 'Unknown')}")
        print(f"  Team 1 ID: {first_match.get('team1_id', first_match.get('team1Id'))}")
        print(f"  Team 2 ID: {first_match.get('team2_id', first_match.get('team2Id'))}")
        
except Exception as e:
    print(f"✗ Error fetching matches: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Test player insertion via upsert_match
print("\n[STEP 4] Testing player insertion via upsert_match...")
try:
    if matches_data:
        match = matches_data[0]
        print(f"  Testing with match: {match.get('matchDesc', 'Unknown')}")
        
        # Check team IDs
        team1_id = match.get('team1_id') or match.get('team1Id')
        team2_id = match.get('team2_id') or match.get('team2Id')
        
        print(f"  Team 1 ID: {team1_id}")
        print(f"  Team 2 ID: {team2_id}")
        
        if not team1_id or not team2_id:
            print("✗ Missing team IDs in match data")
            sys.exit(1)
        
        # Get players for each team from API
        print("\n  Fetching team players from Cricbuzz API...")
        
        for team_key, team_id in [("team1", team1_id), ("team2", team2_id)]:
            try:
                print(f"\n  {team_key.upper()} (ID: {team_id}):")
                
                team_data = api_client.get_team_players(str(team_id))
                
                if not team_data:
                    print(f"    ✗ No team data retrieved")
                    continue
                
                players = team_data.get('player', [])
                print(f"    ✓ Retrieved {len(players)} players")
                
                if players:
                    # Show first 3 players
                    for idx, player in enumerate(players[:3], 1):
                        if isinstance(player, dict):
                            print(f"      {idx}. {player.get('name', 'Unknown')} (ID: {player.get('id')})")
                            print(f"         Batting: {player.get('battingStyle', 'N/A')}")
                            print(f"         Bowling: {player.get('bowlingStyle', 'N/A')}")
                    
                    if len(players) > 3:
                        print(f"      ... and {len(players) - 3} more")
                    
                    # Now test inserting players to MySQL
                    print(f"\n    Inserting {len(players)} players to MySQL...")
                    conn = pymysql.connect(**mysql_config)  # type: ignore[reportUnknownArgumentType]
                    cursor = conn.cursor()
                    
                    inserted_count = 0
                    for player in players:
                        if isinstance(player, dict) and 'id' in player and 'name' in player:
                            try:
                                external_player_id = str(player.get('id', ''))
                                player_name = str(player.get('name', ''))
                                batting_style = str(player.get('battingStyle', ''))
                                bowling_style = str(player.get('bowlingStyle', ''))
                                image_id = str(player.get('imageId', ''))
                                
                                import json
                                meta = json.dumps({
                                    "batting_style": batting_style,
                                    "bowling_style": bowling_style,
                                    "image_id": image_id
                                })
                                
                                cursor.execute(
                                    "INSERT IGNORE INTO players (external_player_id, player_name, country, role, meta) VALUES (%s, %s, %s, %s, %s)",
                                    (external_player_id, player_name, "", "", meta)
                                )
                                
                                if cursor.rowcount > 0:
                                    inserted_count += 1
                                    print(f"      ✓ Inserted: {player_name}")
                                else:
                                    print(f"      - Already exists: {player_name}")
                                    
                            except Exception as e:
                                print(f"      ✗ Error inserting {player.get('name', 'Unknown')}: {e}")
                    
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    print(f"    ✓ {inserted_count} new player(s) inserted")
                    
            except Exception as e:
                print(f"    ✗ Error: {e}")
                import traceback
                traceback.print_exc()
        
except Exception as e:
    print(f"✗ Error in player insertion test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Verify players were inserted
print("\n[STEP 5] Verifying players in database...")
try:
    conn = pymysql.connect(**mysql_config)  # type: ignore[reportUnknownArgumentType]
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT COUNT(*) as count FROM players")
    result = cursor.fetchone()
    total_players = result['count'] if result else 0
    
    print(f"✓ Total players in database: {total_players}")
    
    # Get recently added players
    cursor.execute("""
        SELECT external_player_id, player_name, created_at 
        FROM players 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    print("\n  Recently added players:")
    for player in recent:
        print(f"    - {player['player_name']} (ID: {player['external_player_id']}, added: {player['created_at']})")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"✗ Error verifying players: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC TEST COMPLETE")
print("=" * 80)
