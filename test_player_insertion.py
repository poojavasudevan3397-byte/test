#!/usr/bin/env python3
"""Test script to verify player data insertion into MySQL database."""

import pymysql
import json
from typing import Any, Dict

# MySQL connection details
mysql_config: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

def test_player_table() -> None:
    """Test and display player table data."""
    try:
        # Connect to MySQL
        conn: Any = pymysql.connect(**mysql_config)  # type: ignore[reportUnknownArgumentType]
        cursor: Any = conn.cursor(pymysql.cursors.DictCursor)
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'players'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ Players table does not exist!")
            return
        
        print("✅ Players table exists")
        print("-" * 80)
        
        # Get table structure
        cursor.execute("DESCRIBE players")
        columns = cursor.fetchall()
        print("📋 Table Structure:")
        for col in columns:
            print(f"  - {col['Field']:25} {col['Type']:30} {col.get('Null', 'NULL'):5} {col.get('Key', ''):5}")
        
        print("\n" + "-" * 80)
        
        # Count total players
        cursor.execute("SELECT COUNT(*) as count FROM players")
        count_result = cursor.fetchone()
        total_players = count_result['count'] if count_result else 0
        
        print(f"\n📊 Total Players in Database: {total_players}")
        print("-" * 80)
        
        # Get all players
        cursor.execute("""
            SELECT 
                id, 
                external_player_id, 
                player_name, 
                country, 
                role, 
                meta,
                created_at 
            FROM players 
            ORDER BY created_at DESC
        """)
        
        players = cursor.fetchall()
        
        if not players:
            print("⚠️  No players found in the database!")
            return
        
        print(f"\n👥 Displaying all {len(players)} players:\n")
        
        for idx, player in enumerate(players, 1):
            print(f"{idx}. Player ID: {player['id']}")
            print(f"   External ID: {player['external_player_id']}")
            print(f"   Name: {player['player_name']}")
            print(f"   Country: {player['country']}")
            print(f"   Role: {player['role']}")
            
            # Parse and display meta data
            if player['meta']:
                try:
                    meta_data = json.loads(player['meta'])
                    print(f"   Meta Data: {meta_data}")
                except json.JSONDecodeError:
                    print(f"   Meta Data: {player['meta']}")
            
            print(f"   Created: {player['created_at']}")
            print()
        
        # Get statistics by role
        print("-" * 80)
        print("\n📈 Players by Role:")
        cursor.execute("""
            SELECT role, COUNT(*) as count 
            FROM players 
            GROUP BY role 
            ORDER BY count DESC
        """)
        
        role_stats = cursor.fetchall()
        for stat in role_stats:
            print(f"  {stat['role'] or 'Unknown':20} : {stat['count']:3} players")
        
        # Get statistics by country
        print("\n🌍 Players by Country:")
        cursor.execute("""
            SELECT country, COUNT(*) as count 
            FROM players 
            WHERE country IS NOT NULL AND country != ''
            GROUP BY country 
            ORDER BY count DESC
        """)
        
        country_stats = cursor.fetchall()
        for stat in country_stats[:10]:  # Show top 10
            print(f"  {stat['country']:20} : {stat['count']:3} players")
        
        if len(country_stats) > 10:
            print(f"  ... and {len(country_stats) - 10} more countries")
        
        print("\n" + "=" * 80)
        print("✅ Player table test completed successfully!")
        
        cursor.close()
        conn.close()
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("🏏 PLAYER TABLE DATA TEST")
    print("=" * 80)
    print()
    test_player_table()
