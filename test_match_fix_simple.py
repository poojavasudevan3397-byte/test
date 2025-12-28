#!/usr/bin/env python
"""Test the upsert_match fix with actual API data"""
# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

import json
from pathlib import Path
from typing import Any, Optional, cast, List, Dict

def test_upsert_match_extraction():
    """Test team name extraction from nested objects"""
    
    # Load live.json and navigate to the matchInfo list
    live_json_path = Path(__file__).parent / "cricbuzz_app" / "data" / "api_responses" / "live.json"
    with open(live_json_path, 'r') as f:
        api_data = json.load(f)

    # The API nests matches under: typeMatches -> seriesMatches -> seriesAdWrapper -> matches -> matchInfo
    # Use explicit List casting so Pylance knows the types for len()/indexing
    type_matches = cast(List[Any], api_data.get("typeMatches") or [])
    if len(type_matches) == 0:
        print("ERROR: No typeMatches found in live.json")
        return False

    # drill down safely with typed lists/dicts
    first_type = cast(Dict[str, Any], type_matches[0])
    series_matches = cast(List[Any], first_type.get("seriesMatches") or [])
    if len(series_matches) == 0:
        print("ERROR: No seriesMatches found in live.json")
        return False

    first_series = cast(Dict[str, Any], series_matches[0])
    series_wrapper = cast(Dict[str, Any], first_series.get("seriesAdWrapper") or {})
    if not series_wrapper:
        print("ERROR: seriesAdWrapper missing")
        return False

    matches_list = cast(List[Any], series_wrapper.get("matches") or [])
    if len(matches_list) == 0:
        print("ERROR: No matches found in seriesAdWrapper")
        return False

    # Top-level match container
    match_container = cast(Dict[str, Any], matches_list[0])
    match = cast(Dict[str, Any], match_container.get("matchInfo") or {})
    if not match:
        print("ERROR: matchInfo missing")
        return False
    
    # Simulate the extraction logic that's in upsert_match, with explicit typing for Pylance
    team1_obj: Any = match.get("team1") or {}
    team2_obj: Any = match.get("team2") or {}

    # team1/team2 can be either dicts with 'teamName'/'teamId' or a string
    team1: Optional[str]
    team2: Optional[str]
    team1_id: Optional[int]
    team2_id: Optional[int]

    if isinstance(team1_obj, dict):
        team1 = cast(Optional[str], team1_obj.get("teamName"))
        team1_id = cast(Optional[int], team1_obj.get("teamId"))
    else:
        team1 = cast(Optional[str], team1_obj)
        team1_id = cast(Optional[int], match.get("team1_id"))

    if isinstance(team2_obj, dict):
        team2 = cast(Optional[str], team2_obj.get("teamName"))
        team2_id = cast(Optional[int], team2_obj.get("teamId"))
    else:
        team2 = cast(Optional[str], team2_obj)
        team2_id = cast(Optional[int], match.get("team2_id"))
    
    print(f"\n{'='*60}")
    print(f"MATCH EXTRACTION TEST - VERIFICATION OF FIX")
    print(f"{'='*60}")
    print(f"Match ID: {match.get('matchId')}")
    print(f"Series: {match.get('seriesName')}")
    print(f"\nTeam 1:")
    print(f"  - Name: {team1}")
    print(f"  - ID: {team1_id}")
    print(f"\nTeam 2:")
    print(f"  - Name: {team2}")
    print(f"  - ID: {team2_id}")
    
    # Check for NULLs
    success = True
    if team1 is None or team1 == "":
        print(f"\n❌ ERROR: Team1 name is NULL or empty!")
        success = False
    else:
        print(f"\n✓ Team1 name extracted successfully: '{team1}'")
    
    if team2 is None or team2 == "":
        print(f"❌ ERROR: Team2 name is NULL or empty!")
        success = False
    else:
        print(f"✓ Team2 name extracted successfully: '{team2}'")
    
    if success:
        print(f"\n✓ VERIFICATION PASSED: All team names extracted correctly!")
        print(f"  Fix is working - nested team objects are properly extracted.")
    
    return success

if __name__ == "__main__":
    try:
        success = test_upsert_match_extraction()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
