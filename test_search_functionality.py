#!/usr/bin/env python3
"""
Test the search functionality in the updated CRUD page
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd

def test_search_functionality():
    """Test the search logic used in the CRUD page"""
    
    # Create sample player data like in the database
    sample_data = {
        'id': [1, 2, 3, 4, 5],
        'player_name': ['Virat Kohli', 'Rohit Sharma', 'Jasprit Bumrah', 'Ravichandran Ashwin', 'Rishabh Pant'],
        'country': ['India', 'India', 'India', 'India', 'India'],
        'role': ['Batsman', 'Batsman', 'Bowler', 'Bowler', 'Wicket-keeper'],
        'external_player_id': ['ext_1', 'ext_2', 'ext_3', 'ext_4', 'ext_5']
    }
    
    players_df = pd.DataFrame(sample_data)
    
    print("\n" + "=" * 70)
    print("TESTING SEARCH FUNCTIONALITY")
    print("=" * 70)
    
    # Test cases
    test_cases = [
        ("Virat", "Search by first name"),
        ("Kohli", "Search by last name"),
        ("Rohit Sharma", "Search by full name"),
        ("1", "Search by ID"),
        ("Bumrah", "Search by player name"),
        ("ashwin", "Case-insensitive search (lowercase)"),
        ("PANT", "Case-insensitive search (uppercase)"),
        ("xyz", "Non-existent player (should return empty)"),
    ]
    
    for search_query, description in test_cases:
        print(f"\n🔍 Test: {description}")
        print(f"   Search Query: '{search_query}'")
        
        # Apply the same filter logic as in the CRUD page
        filtered_players = players_df[
            (players_df["player_name"].str.contains(search_query, case=False, na=False)) |
            (players_df["id"].astype(str).str.contains(search_query, na=False))
        ]
        
        if not filtered_players.empty:
            print(f"   ✅ Found {len(filtered_players)} player(s):")
            for idx, row in filtered_players.iterrows():
                print(f"      - {row['player_name']} (ID: {row['id']}, Role: {row['role']})")
        else:
            print(f"   ⚠️  No players found")
    
    print("\n" + "=" * 70)
    print("✅ SEARCH FUNCTIONALITY TEST COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    test_search_functionality()
