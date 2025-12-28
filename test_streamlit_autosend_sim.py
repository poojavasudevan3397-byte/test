#!/usr/bin/env python3
"""Simulate Streamlit auto-send behavior for testing."""

import sys
import os
from typing import Any, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricbuzz_app'))

import pymysql  # type: ignore[import]
import json
import requests

# MySQL config
mysql_config: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

api_key = "7d43f4bd53msh4abaa77fb5edf80p14c624jsn6982e9f7e18b"

print("=" * 80)
print("STREAMLIT AUTO-SEND SIMULATION TEST")
print("=" * 80)

print("\n[1] Fetching recent matches from Cricbuzz API...")
try:
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/recent"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    matches_data = response.json()
    
    print(f"[OK] Retrieved {len(matches_data)} matches")
    
    if not matches_data:
        print("No matches available")
        sys.exit(0)
    
    # Take first match
    match = matches_data[0]
    match_id = match.get('matchId') or match.get('match_id')
    match_desc = match.get('matchDesc', 'Unknown')
    
    print(f"\nUsing match: {match_desc} (ID: {match_id})")
    
    # Get team IDs
    team1_id = match.get('team1_id') or match.get('team1Id')
    team2_id = match.get('team2_id') or match.get('team2Id')
    
    print(f"Team 1 ID: {team1_id}")
    print(f"Team 2 ID: {team2_id}")
    
    if not team1_id or not team2_id:
        print("Missing team IDs")
        sys.exit(1)
    
    # Connect to MySQL
    print("\n[2] Connecting to MySQL...")
    conn: Any = pymysql.connect(**mysql_config)  # type: ignore[reportUnknownArgumentType]
    cursor: Any = conn.cursor()
    print("[OK] Connected")
    
    # Process each team
    total_inserted = 0
    
    for team_label, team_id in [("TEAM 1", team1_id), ("TEAM 2", team2_id)]:
        print(f"\n[3] Processing {team_label} (ID: {team_id})...")
        
        try:
            url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
            print(f"  Calling API: {url}")
            
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            team_data = resp.json()
            
            print(f"  [OK] Got response, keys: {list(team_data.keys())}")
            
            players = team_data.get('player', [])
            print(f"  Found {len(players)} players")
            
            if isinstance(players, list) and players:
                inserted_count = 0
                for p in players[:5]:  # Show first 5
                    if isinstance(p, dict) and 'id' in p and 'name' in p:
                        external_player_id = str(p.get('id', ''))
                        player_name = str(p.get('name', ''))
                        batting_style = str(p.get('battingStyle', ''))
                        bowling_style = str(p.get('bowlingStyle', ''))
                        image_id = str(p.get('imageId', ''))
                        
                        meta = json.dumps({
                            "batting_style": batting_style,
                            "bowling_style": bowling_style,
                            "image_id": image_id
                        })
                        
                        try:
                            cursor.execute(
                                "INSERT IGNORE INTO players (external_player_id, player_name, country, role, meta) VALUES (%s, %s, %s, %s, %s)",
                                (external_player_id, player_name, "", "", meta)
                            )
                            if cursor.rowcount > 0:
                                inserted_count += 1
                                print(f"    [+] {player_name}")
                            else:
                                print(f"    [-] {player_name} (exists)")
                        except Exception as e:
                            print(f"    [X] Error with {player_name}: {e}")
                
                print(f"  {inserted_count} new players inserted from this team")
                total_inserted += inserted_count
            else:
                print(f"  No players data available")
        
        except requests.exceptions.RequestException as e:
            print(f"  [X] API error: {e}")
        except Exception as e:
            print(f"  [X] Error: {e}")
            import traceback
            traceback.print_exc()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print(f"RESULT: {total_inserted} total new players inserted")
    print("=" * 80)
    
except Exception as e:
    print(f"\n[X] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
