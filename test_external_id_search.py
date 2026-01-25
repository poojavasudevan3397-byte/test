#!/usr/bin/env python3
"""
Test the external player ID search functionality
"""
import pandas as pd

def test_external_id_search():
    """Test searching by external player ID"""
    
    # Sample data with external IDs
    sample_data = {
        'id': [1, 2, 3, 4, 5],
        'player_name': ['Virat Kohli', 'Rohit Sharma', 'Jasprit Bumrah', 'Ravichandran Ashwin', 'Rishabh Pant'],
        'external_player_id': ['EXT001', 'EXT002', 'EXT003', 'EXT004', 'EXT005'],
        'country': ['India', 'India', 'India', 'India', 'India'],
        'role': ['Batsman', 'Batsman', 'Bowler', 'Bowler', 'Wicket-keeper'],
    }
    
    players_df = pd.DataFrame(sample_data)
    
    print("\n" + "=" * 70)
    print("TESTING EXTERNAL PLAYER ID SEARCH")
    print("=" * 70)
    print("\nDatabase Sample:")
    print(players_df.to_string())
    
    # Test cases
    test_cases = [
        ("EXT001", "Search by exact external ID"),
        ("EXT00", "Search by partial external ID"),
        ("Virat", "Search by player name"),
        ("Kohli", "Search by last name"),
        ("ext002", "Case-insensitive external ID search"),
        ("Bumrah", "Search for Bumrah"),
        ("Ashwin", "Search for Ashwin"),
        ("xyz", "Non-existent player"),
    ]
    
    for search_query, description in test_cases:
        print(f"\n🔍 Test: {description}")
        print(f"   Search Query: '{search_query}'")
        
        # Apply the same filter logic as in the updated CRUD page
        filtered_players = players_df[
            (players_df["player_name"].str.contains(search_query, case=False, na=False)) |
            (players_df["external_player_id"].astype(str).str.contains(search_query, case=False, na=False))
        ]
        
        if not filtered_players.empty:
            print(f"   ✅ Found {len(filtered_players)} player(s):")
            for idx, row in filtered_players.iterrows():
                print(f"      - {row['player_name']} (External ID: {row['external_player_id']}, Role: {row['role']})")
        else:
            print(f"   ⚠️  No players found")
    
    print("\n" + "=" * 70)
    print("✅ EXTERNAL PLAYER ID SEARCH TEST COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    test_external_id_search()
