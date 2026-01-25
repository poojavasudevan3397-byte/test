"""
Diagnostic script to check what data is available from player profile API
"""
import sys
sys.path.insert(0, '.')

import requests
import json

# Use the API key provided
api_key = "0be62878demshcfd4a74416cba00p1abe24jsn71b03a98d5de"

# Try a few well-known players
player_ids = [
    ("6635", "Virat Kohli"),
    ("13192", "MS Dhoni"),
    ("12345", "Random ID"),
]

headers = {
    "X-RapidAPI-Key": api_key,
    "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com",
}

for pid, name in player_ids:
    print(f"\n{'='*60}")
    print(f"Player: {name} (ID {pid})")
    print('='*60)
    
    try:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{pid}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"\nStatus: SUCCESS")
        print(f"Keys in response: {list(data.keys())}")
        
        # Print first level data
        for k, v in data.items():
            if isinstance(v, (str, int, float, bool)) or v is None:
                print(f"  {k}: {v}")
            elif isinstance(v, dict):
                print(f"  {k}: (dict with keys: {list(v.keys())})")
            elif isinstance(v, list):
                print(f"  {k}: (list with {len(v)} items)")
            else:
                print(f"  {k}: ({type(v).__name__})")
        
        # Look for specific fields
        print(f"\nSpecific fields:")
        print(f"  country: {data.get('country')}")
        print(f"  dateOfBirth: {data.get('dateOfBirth')}")
        print(f"  role: {data.get('role')}")
        print(f"  name: {data.get('name')}")
        
    except Exception as e:
        print(f"ERROR: {e}")
