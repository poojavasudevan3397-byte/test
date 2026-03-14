
from typing import Any, Dict, List, cast
from utils.api_client import get_api_client, normalize_matches
from utils.mysql_sync import (
    upsert_match,
    upsert_batting,
    upsert_bowling,
    create_mysql_schema,
    upsert_series,
    upsert_team,
    upsert_venue,
    upsert_innings,
    upsert_partnerships,
    upsert_player,
    upsert_toss_details,
)

"""
Live Matches Page - Real-time Match Updates with MySQL Sync
"""

import streamlit as st
from typing import Any, cast
st = cast(Any, st)
import pandas as pd
from typing import Any, Dict, List, cast
from datetime import datetime
import sys
import os
import requests
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_client import get_api_client, normalize_matches
from utils.mysql_sync import upsert_match, upsert_batting, upsert_bowling, create_mysql_schema


def show():
    """Display live matches page"""
    st.markdown("<h1 class='page-title'>⚡ Real-Time Match Updates</h1>", unsafe_allow_html=True)

   
    # Match Type Selection
    col1, col2 = st.columns(2)
    with col1:
        match_type = st.radio(
            "Select Match Type",
            ["Live", "Upcoming", "Recent"],
            horizontal=True,
            key="match_type_radio"
        )
        match_category = st.selectbox(
            "Match Category",
            ["All", "International", "Domestic", "Women"],
            index=0,
            key="match_category_select"
        )

    # Initialize session state
    if "matches_cache" not in st.session_state:
        st.session_state.matches_cache = {}
    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = {}

    # Auto-refresh settings and MySQL sync options
    with col2:
        _refresh_interval = st.selectbox(
            "Auto-refresh",
            ["Manual", "30 seconds", "1 minute", "5 minutes"],
            index=0,
            key="refresh_select"
        )
        
        # MySQL Sync Options
        st.session_state.setdefault("auto_send_mysql", True)  # Default to True
        auto_send = st.checkbox(
            "✅ Auto-sync to MySQL",
            value=st.session_state.get("auto_send_mysql", True),
            key="auto_send_mysql_checkbox",
            help="Automatically save matches to MySQL database"
        )
        st.session_state["auto_send_mysql"] = auto_send

        st.session_state.setdefault("auto_send_scorecards", False)
        include_scorecards = st.checkbox(
            "📊 Sync Scorecards",
            value=st.session_state.get("auto_send_scorecards", False),
            key="auto_send_scorecards_checkbox",
            help="Include detailed scorecards (may take longer)"
        )
        st.session_state["auto_send_scorecards"] = include_scorecards

    # Fetch matches based on type
    # Force api_key to be a string for static type checking
    api_key: str = str(st.secrets.get("RAPIDAPI_KEY", ""))
    api_client = get_api_client(api_key)

    matches_data = {}
    try:
        with st.spinner(f"Fetching {match_type} matches..."):
            if match_type == "Live":
                matches_data = api_client.get_live_matches()
            elif match_type == "Upcoming":
                matches_data = api_client.get_upcoming_matches()
            else:
                matches_data = api_client.get_recent_matches()

        matches: List[Dict[str, Any]] = normalize_matches(matches_data)

        # MySQL Sync Configuration
        mysql_secrets: Dict[str, Any] = {
            "host": "localhost",
            "user": "root",
            "password": "Vasu@76652",
            "database": "cricketdb",
            "port": 3306,
        }
        mysql_secrets = st.secrets.get("mysql", {})

        # Auto-sync to MySQL if enabled
        if st.session_state.get("auto_send_mysql", True) and matches:
            sync_progress = st.progress(0, text="Syncing matches to MySQL...")
            
            try:
                # Create schema first
                create_mysql_schema(mysql_secrets)
                st.success("✅ MySQL schema ready")

                # Prefetch teams metadata (country/name) from API client to avoid individual requests
                teams_map: Dict[str, Dict[str, Any]] = {}
                try:
                    teams_map = api_client.get_all_teams_with_country() or {}
                    print(f"DEBUG: loaded {len(teams_map)} teams from API client")
                except Exception as e:
                    print(f"Warning: Could not prefetch teams map: {e}")

                total_matches = len(matches)
                synced_matches = 0
                synced_players = 0
                synced_scorecards = 0
                
                for idx, m in enumerate(matches):
                    try:
                        # Update progress
                        progress = (idx + 1) / total_matches
                        sync_progress.progress(progress, text=f"Syncing match {idx + 1}/{total_matches}...")
                        
                        # 1. Sync Match
                        rc = upsert_match(mysql_secrets, m)
                        print(f"DEBUG: upsert_match rc={rc} for match {m.get('matchId', m.get('match_id'))}")
                        if rc and rc > 0:
                            synced_matches += 1

                        # Upsert series, teams and venue if available
                        try:
                            Series_ID = m.get('seriesId') or m.get('series_id') or m.get('external_series_id') or None
                            Series_Name = m.get('seriesName') or m.get('series_name') or None
                            # Optional series metadata
                            Series_Type = (
                                m.get('seriesType')
                                or m.get('series_type')
                                or m.get('seriesTypeName')
                                or m.get('series_type_name')
                                or None
                            )
                            Series_Start = (
                                m.get('seriesStartDt')
                                or m.get('series_start_dt')
                                or m.get('seriesStartDate')
                                or m.get('series_start_date')
                                or None
                            )
                            Series_End = (
                                m.get('seriesEndDt')
                                or m.get('series_end_dt')
                                or m.get('seriesEndDate')
                                or m.get('series_end_date')
                                or None
                            )
                            if Series_ID and Series_Name:
                                s_rc = upsert_series(
                                    mysql_secrets,
                                    str(Series_ID),
                                    Series_Name,
                                    Series_Type,
                                    Series_Start,
                                    Series_End,
                                )
                                print(f"DEBUG: upsert_series rc={s_rc} for series {Series_ID} name={Series_Name}")

                            # for team_key, name_key in [('team1_id', 'team1_name'), ('team2_id', 'team2_name')]:
                            #     Team_ID = m.get(team_key) or m.get(f'external_{team_key}') or None
                            #     Team_Name = m.get(name_key) or m.get(f'external_{name_key}') or None

                            #     # Best-effort country extraction: team object → explicit country fields → teams_map → single API → fallback to team name
                            #     team_obj_key = team_key.replace('_id', '')
                            #     team_obj = m.get(team_obj_key) or {}
                            #     #Team_Country = None
                                
                            #     if not Team_Country and Team_ID:
                            #         try:
                            #             tid = str(Team_ID)
                            #             single_team = api_client._get(f"/teams/v1/{tid}")
                            #             if isinstance(single_team, dict):
                            #                 Team_Country = (
                            #                     single_team.get('country')
                            #                     or single_team.get('countryName')
                            #                     or single_team.get('teamCountry')
                            #                     or single_team.get('country_name')
                            #                 )
                            #                 Team_Name = Team_Name or (single_team.get('name') or single_team.get('teamName'))
                            #                 if Team_Country:
                            #                     print(f"DEBUG: fetched country '{Team_Country}' for team {Team_ID} via single API call")
                            #         except Exception as e:
                            #             print(f"Warning: Could not fetch team details for {Team_ID} via API: {e}")

                            #     if Team_ID and Team_Name:
    
                            #         # Single upsert with fully resolved country
                            #         t_rc = upsert_team(mysql_secrets, str(Team_ID), Team_Name, Team_Country)
                            #         print(f"DEBUG: upsert_team rc={t_rc} for team {Team_ID} name={Team_Name} country={Team_Country}")

                            from utils.api_client import extract_venue_metadata
                            venue_id = m.get("external_venue_id")

                            if venue_id:
                                try:
                                    # Cache to avoid duplicate API calls
                                    if "venue_cache" not in st.session_state:
                                        st.session_state["venue_cache"] = set()

                                    if venue_id not in st.session_state["venue_cache"]:
                                        venue_profile = api_client.get_venue_profile(str(venue_id))
                                        print(f"DEBUG: Fetched venue_profile for venue_id={venue_id}: {venue_profile}")

                                        # Use extract_venue_metadata to normalize keys consistently
                                        venue_record = extract_venue_metadata(venue_profile)
                                        print(f"DEBUG: After extract_venue_metadata: {venue_record}")

                                        # Ensure we have ID and name before inserting
                                        if venue_record.get("Venue_ID") and venue_record.get("Venue_Name"):
                                            v_rc = upsert_venue(mysql_secrets, venue_record)
                                            print(
                                                f"DEBUG: upsert_venue rc={v_rc} "
                                                f"id={venue_record.get('Venue_ID')} "
                                                f"name={venue_record.get('Venue_Name')}"
                                            )
                                            if v_rc and v_rc > 0:
                                                print(f"✅ Venue inserted successfully: {venue_record.get('Venue_Name')} (ID={venue_record.get('Venue_ID')})")
                                            else:
                                                print(f"⚠️ Venue upsert returned {v_rc}: {venue_record.get('Venue_Name')}")
                                        else:
                                            print(f"❌ Skipping venue: missing ID or Name. ID={venue_record.get('Venue_ID')}, Name={venue_record.get('Venue_Name')}")

                                        st.session_state["venue_cache"].add(venue_id)

                                except Exception as e:
                                    print(f"Warning: venue API failed for venue {venue_id}: {e}")

                        except Exception as e:
                            print(f"Warning: Could not upsert series/team/venue: {e}")

                        # 1.5. Sync Toss Details
                        try:
                            match_id = m.get("matchId") or m.get("match_id") or m.get("external_match_id")
                            if match_id:
                                # Try to get toss details from match center API
                                toss_url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}"
                                try:
                                    headers_temp: Dict[str, str] = {
                                        "x-rapidapi-key": api_key,
                                        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
                                    }
                                    toss_resp = requests.get(toss_url, headers=headers_temp, timeout=10)
                                    
                                    if toss_resp.ok:
                                        toss_data = toss_resp.json()
                                        toss_status = toss_data.get("tossstatus")
                                        
                                        if toss_status:
                                            # Parse toss status: "Team_Name opt to bat/bowl"
                                            toss_winner = toss_status.split(" opt")[0].strip() if " opt" in toss_status else None
                                            decision = "bowl" if "bowl" in toss_status.lower() else "bat" if "bat" in toss_status.lower() else None
                                            
                                            if toss_winner and decision:
                                                toss_rc = upsert_toss_details(
                                                    mysql_secrets,
                                                    str(match_id),
                                                    toss_winner,
                                                    decision,
                                                    {"raw_toss_status": toss_status}
                                                )
                                                print(f"DEBUG: upsert_toss_details rc={toss_rc} for match {match_id} - winner={toss_winner}, decision={decision}")
                                                if toss_rc and toss_rc > 0:
                                                    print(f"✅ Toss details inserted: {toss_winner} opted to {decision}")
                                    else:
                                        print(f"Warning: Toss API returned {toss_resp.status_code} for match {match_id}")
                                except Exception as e:
                                    print(f"Warning: Could not fetch toss details from API for match {match_id}: {e}")
                        except Exception as e:
                            print(f"Warning: Could not upsert toss details: {e}")

                        # 2. Sync Players for both teams

                        # for team_key in ["team1_id", "team2_id"]:
                        #     Team_ID = m.get(team_key) or m.get(f"external_{team_key}")
                        #     if Team_ID:
                        #         try:
                        #             #import requests
                        #             url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{Team_ID}/players"
                        #             headers: Dict[str, str] = {
                        #                 "x-rapidapi-key": api_key,
                        #                 "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
                        #             }
                        #             resp = requests.get(url, headers=headers, timeout=10)
                        #             if not resp.ok:
                        #                 print(f"Warning: players API returned {resp.status_code} for team {Team_ID}: {resp.text[:200]}")
                        #             else:
                        #                 try:
                        #                     # Handle empty response body
                        #                     if not resp.text or not resp.text.strip():
                        #                         print(f"Warning: players API returned empty response for team {Team_ID}")
                        #                         team_data = {}
                        #                     else:
                        #                         team_data = resp.json()
                        #                 except ValueError as json_err:
                        #                     print(f"Warning: Could not parse JSON response for team {Team_ID}: {json_err}")
                        #                     team_data = {}

                        #                 # Insert players
                        #                 # Some endpoints return 'player', others 'players' — accept both
                        #                 players_raw = cast(
                        #                     List[Dict[str, Any]],
                        #                     team_data.get('player') or team_data.get('players') or team_data.get('playerList') or team_data.get('playersList') or [],
                        #                 )
                        #                 print(f"DEBUG: fetched {len(players_raw)} players for team {Team_ID}")
                        #                 for p in players_raw:
                        #                     if p:
                        #                         try:
                        #                             player_rc = upsert_player(mysql_secrets, p)
                        #                             print(f"DEBUG: upsert_player rc={player_rc} for player {p.get('name') or p.get('playerName')}")
                        #                             if player_rc and player_rc > 0:
                        #                                 synced_players += 1
                        #                         except Exception as insert_err:
                        #                             print(f"Error upserting player {p.get('name') or p.get('playerName')}: {insert_err}")
                        #         except Exception as e:
                        #             print(f"Warning: Could not sync players for team {Team_ID}: {e}")
                        
                        # 2️⃣ Sync Players for both teams → Fetch Full Profile Using Player API

                        if "team_players_cache" not in st.session_state:
                            st.session_state["team_players_cache"] = {}

                        if "player_profile_cache" not in st.session_state:
                            st.session_state["player_profile_cache"] = {}

                        headers: Dict[str, str] = {
                            "x-rapidapi-key": api_key,
                            "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
                        }

                        for team_key in ["team1_id", "team2_id"]:

                            Team_ID = m.get(team_key) or m.get(f"external_{team_key}")
                            if not Team_ID:
                                continue

                            try:
                                # -----------------------
                                # 1️⃣ Get Team Players
                                # -----------------------
                                if Team_ID in st.session_state["team_players_cache"]:
                                    team_data = st.session_state["team_players_cache"][Team_ID]
                                else:
                                    team_url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{Team_ID}/players"
                                    team_resp = requests.get(team_url, headers=headers, timeout=10)

                                    if not team_resp.ok:
                                        print(f"Warning: Team players API failed {team_resp.status_code}")
                                        continue

                                    team_data = team_resp.json()
                                    st.session_state["team_players_cache"][Team_ID] = team_data

                                players_raw = (
                                    team_data.get("player")
                                    or team_data.get("players")
                                    or team_data.get("playerList")
                                    or team_data.get("playersList")
                                    or []
                                )

                                print(f"DEBUG: Found {len(players_raw)} players for team {Team_ID}")

                                # -----------------------
                                # 2️⃣ Fetch Full Player Profile
                                # -----------------------
                                for p in players_raw:

                                    player_id = (
                                        p.get("id")
                                        or p.get("playerId")
                                        or p.get("external_player_id")
                                    )

                                    if not player_id:
                                        continue

                                    try:
                                        if player_id in st.session_state["player_profile_cache"]:
                                            player_profile = st.session_state["player_profile_cache"][player_id]
                                        else:
                                            profile_url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
                                            profile_resp = requests.get(profile_url, headers=headers, timeout=10)

                                            if not profile_resp.ok:
                                                print(f"Warning: Player API failed for {player_id}")
                                                continue

                                            player_profile = profile_resp.json()
                                            st.session_state["player_profile_cache"][player_id] = player_profile

                                        # Upsert Full Profile
                                        player_rc = upsert_player(mysql_secrets, player_profile)

                                        print(f"DEBUG: upsert_player rc={player_rc} for player {player_id}")

                                        if player_rc and player_rc > 0:
                                            synced_players += 1

                                    except Exception as insert_err:
                                        print(f"Error syncing player {player_id}: {insert_err}")

                            except Exception as e:
                                print(f"Warning: Could not sync players for team {Team_ID}: {e}")

                        if st.session_state.get("auto_send_scorecards", False):
                            mid = m.get("matchId") or m.get("match_id") or m.get("external_match_id")
                            if mid:
                                try:
                                    sc = api_client.get_scorecard(str(mid))
                                    if sc:
                                        changed = False
                                        for inning in sc.get("scorecard", []):
                                            innings_id = inning.get("inningsId") or inning.get("inningsid") or ""
                                            if innings_id:
                                                # Upsert innings itself
                                                try:
                                                    # Enrich inning object: normalize team keys and derive bowling team when possible
                                                    enriched_inning = dict(inning)
                                                    if "batTeamName" not in enriched_inning and "batteamname" in enriched_inning:
                                                        enriched_inning["batTeamName"] = enriched_inning.get("batteamname")
                                                    if "bowlTeamName" not in enriched_inning and "bowlteamname" in enriched_inning:
                                                        enriched_inning["bowlTeamName"] = enriched_inning.get("bowlteamname")

                                                    if not enriched_inning.get("bowlTeamName"):
                                                        t1 = m.get("team1_name") or (m.get("team1") or {}).get("teamName")
                                                        t2 = m.get("team2_name") or (m.get("team2") or {}).get("teamName")
                                                        t1_short = m.get("team1_short") or (m.get("team1") or {}).get("teamSName")
                                                        t2_short = m.get("team2_short") or (m.get("team2") or {}).get("teamSName")
                                                        bat_name = enriched_inning.get("batTeamName") or enriched_inning.get("batteamname") or enriched_inning.get("batteamsname")
                                                        if bat_name and (t1 or t2):
                                                            if (t1_short and bat_name == t1_short) or (t1 and bat_name == t1) or (t1 and isinstance(bat_name, str) and t1.startswith(bat_name)):
                                                                enriched_inning["bowlTeamName"] = t2
                                                            else:
                                                                enriched_inning["bowlTeamName"] = t1

                                                    inn_rc = upsert_innings(mysql_secrets, str(mid), enriched_inning)
                                                    print(f"DEBUG: upsert_innings rc={inn_rc} for match {mid} innings {innings_id}")
                                                    if inn_rc and inn_rc > 0:
                                                        changed = True
                                                except Exception as e:
                                                    print(f"Warning: upsert_innings failed: {e}")

                                                bats = inning.get("batsman", inning.get("batsmen", []))
                                                if bats:
                                                    b_rc = upsert_batting(mysql_secrets, str(mid), str(innings_id), bats)
                                                    print(f"DEBUG: upsert_batting rc={b_rc} for match {mid} innings {innings_id}")
                                                    if b_rc and b_rc > 0:
                                                        changed = True

                                                    # Ensure player records exist for batsmen (fallback when team players API fails)
                                                    for b in bats:
                                                        try:
                                                            player_id = b.get('batId') or b.get('external_player_id') or b.get('id')
                                                            player_name = b.get('batName') or b.get('name') or b.get('player_name') or b.get('playerName')
                                                            if player_id or player_name:
                                                                # Pass full player object with all available metadata
                                                                player_obj = {
                                                                    'id': player_id,
                                                                    'name': player_name,
                                                                    'playerName': player_name,
                                                                    # Include any additional metadata from scorecard
                                                                    **{k: v for k, v in b.items() if k not in ['batId', 'batName', 'id', 'name']}
                                                                }
                                                                pr = upsert_player(mysql_secrets, player_obj)
                                                                print(f"DEBUG: upsert_player (from batting) rc={pr} for player {player_name}")
                                                                if pr and pr > 0:
                                                                    synced_players += 1
                                                        except Exception as e:
                                                            print(f"Warning: upsert_player (bat) failed: {e}")

                                                bowls = inning.get("bowler", inning.get("bowlers", []))
                                                if bowls:
                                                    bw_rc = upsert_bowling(mysql_secrets, str(mid), str(innings_id), bowls)
                                                    print(f"DEBUG: upsert_bowling rc={bw_rc} for match {mid} innings {innings_id}")
                                                    if bw_rc and bw_rc > 0:
                                                        changed = True

                                                    # Ensure player records exist for bowlers
                                                    for bw in bowls:
                                                        try:
                                                            player_id = bw.get('bowlId') or bw.get('external_player_id') or bw.get('id')
                                                            player_name = bw.get('bowlName') or bw.get('name') or bw.get('player_name') or bw.get('playerName')
                                                            if player_id or player_name:
                                                                # Pass full player object with all available metadata
                                                                player_obj = {
                                                                    'id': player_id,
                                                                    'name': player_name,
                                                                    'playerName': player_name,
                                                                    # Include any additional metadata from scorecard
                                                                    **{k: v for k, v in bw.items() if k not in ['bowlId', 'bowlName', 'id', 'name']}
                                                                }
                                                                pr = upsert_player(mysql_secrets, player_obj)
                                                                print(f"DEBUG: upsert_player (from bowling) rc={pr} for player {player_name}")
                                                                if pr and pr > 0:
                                                                    synced_players += 1
                                                        except Exception as e:
                                                            print(f"Warning: upsert_player (bowl) failed: {e}")
                                                # Partnerships
                                                # Partnerships (nested: inning['partnership']['partnership'])
                                                partnerships = []
                                                partnership_obj = inning.get("partnership")

                                                if isinstance(partnership_obj, dict):
                                                    partnerships = partnership_obj.get("partnership", [])

                                                if partnerships:
                                                    normalized_partnerships = []
                                                    seen_players = set()

                                                    for p in partnerships:
                                                        if not isinstance(p, dict):
                                                            continue

                                                        # -------- Player 1 --------
                                                        player1_obj = p.get("batsman1") or p.get("batsmanOne")
                                                        player1_id = p.get("bat1id")
                                                        Player1 = p.get("bat1name") or None
                                                        player1_meta = {}

                                                        # if isinstance(player1_obj, dict):
                                                        #     player1_id = player1_obj.get("playerId") or player1_obj.get("batId") or player1_obj.get("id")
                                                        #     player1_name = (
                                                        #         player1_obj.get("playerName")
                                                        #         or player1_obj.get("bat1name")
                                                                
                                                        #     )
                                                        #     player1_meta = player1_obj
                                                        # elif player1_obj:
                                                        #     player1_name = str(player1_obj).strip()
                                                        #     player1_meta = {"name": player1_name}
                                                        #Player1 = player1_name

                                                        # -------- Player 2 --------
                                                        player2_obj = p.get("batsman2") or p.get("batsmanTwo")
                                                        player2_id = p.get("bat2id")
                                                        Player2 = p.get("bat2name") or None
                                                        player2_meta = {}

                                                        # if isinstance(player2_obj, dict):
                                                        #     player2_id = player2_obj.get("playerId") or player2_obj.get("batId") or player2_obj.get("id")
                                                        #     player2_name = (
                                                        #         player2_obj.get("playerName")
                                                                
                                                        #         or player2_obj.get("bat2name")
                                                        #     )
                                                        #     player2_meta = player2_obj
                                                        # elif player2_obj:
                                                        #     player2_name = str(player2_obj).strip()
                                                        #     player2_meta = {"name": player2_name}
                                                        # Player2 = player2_name

                                                        # -------- Partnership stats --------
                                                        runs = int(p.get("totalruns") or p.get("r") or 0)
                                                        balls = int(p.get("totalballs") or p.get("b") or 0)

                                                        # -------- Normalize partnership --------
                                                        norm_p = {
                                                               # keep original first
                                                            "player1_id": player1_id,
                                                            "player2_id": player2_id,
                                                            "Player1": Player1,
                                                            "Player2": Player2,
                                                            "runs": runs,
                                                            "balls": balls,
                                                        }
                                                        normalized_partnerships.append(norm_p)

                                                        # -------- Upsert players (deduplicated) --------
                                                        for pid, pname, pmeta in [
                                                            (player1_id, Player1, player1_meta),
                                                            (player2_id, Player2, player2_meta),
                                                        ]:
                                                            if not pname:
                                                                continue

                                                            key = pid or pname.lower()
                                                            if key in seen_players:
                                                                continue

                                                            seen_players.add(key)

                                                            player_record = {
                                                                "external_player_id": pid,
                                                                "player_name": pname,
                                                                "meta": pmeta,
                                                            }

                                                            try:
                                                                pr = upsert_player(mysql_secrets, player_record)
                                                                print(f"DEBUG: upsert_player rc={pr} for {pname}")
                                                                if pr and pr > 0:
                                                                    synced_players += 1
                                                            except Exception as e:
                                                                print(f"Warning: upsert_player failed for {pname}: {e}")

                                                    # -------- Upsert partnerships --------
                                                    p_rc = upsert_partnerships(
                                                        mysql_secrets, str(mid), str(innings_id), normalized_partnerships
                                                    )
                                                    print(f"DEBUG: upsert_partnerships rc={p_rc} for match {mid} innings {innings_id}")
                                                    if p_rc and p_rc > 0:
                                                        changed = True
                                                      # Handle failures when fetching/processing the scorecard for this match
                                except Exception as e:
                                    print(f"Warning: Could not sync scorecard for match {mid}: {e}")

                    except Exception as e:
                        print(f"Error syncing match {m.get('matchId', 'unknown')}: {str(e)[:200]}")
                        continue
                
                # Clear progress and show summary
                sync_progress.empty()
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Matches Synced", synced_matches)
                with col_b:
                    st.metric("Players Synced", synced_players)
                with col_c:
                    if st.session_state.get("auto_send_scorecards", False):
                        st.metric("Scorecards Synced", synced_scorecards)
                
                st.success(f"✅ Successfully synced {synced_matches} matches, {synced_players} players to MySQL!")
                
            except Exception as e:
                st.error(f"⚠️ MySQL sync error: {str(e)[:200]}")

        # Apply match category filter
        try:
            if match_category and match_category.lower() != "all":
                sel = match_category.lower()

                def _cat_ok(m: Dict[str, Any]) -> bool:
                    mt = str(m.get("matchType") or m.get("match_type") or "").lower()
                    if sel == "women":
                        return "women" in mt
                    if sel == "international":
                        return "international" in mt
                    if sel == "domestic":
                        return "domestic" in mt
                    return True

                matches = [m for m in matches if _cat_ok(m)]
        except Exception:
            pass

        if not matches:
            st.info(f"No {match_type.lower()} matches available at the moment.")
            return

        # Group matches by series
        st.markdown("---")
        st.markdown(f"## {match_type} Matches by Series")

        series_dict: Dict[str, List[Dict[str, Any]]] = {}
        for match in matches:
            series_name = match.get("seriesName") or match.get("series_name") or "Unknown"
            if series_name not in series_dict:
                series_dict[series_name] = []
            series_dict[series_name].append(match)

        # Display each series
        for series_name, series_matches in series_dict.items():
            with st.expander(
                f"📊 {series_name} ({len(series_matches)} matches)",
                expanded=True
            ):
                for idx, match in enumerate(series_matches):
                    display_match_card(match, match_type, idx)
                    st.markdown("---")

        # Summary Table
        st.markdown("---")
        st.markdown("## Match Summary Table")

        summary_df = pd.DataFrame([
            {
                "Series": m.get("seriesName") or m.get("series_name") or "N/A",
                "Team 1": m.get("team1_name", "N/A"),
                "Team 2": m.get("team2_name", "N/A"),
                "Format": m.get("matchFormat") or m.get("match_format") or "N/A",
                "Status": m.get("status", "N/A"),
                "Venue": m.get("venue") or m.get("venue_name") or m.get("ground") or "N/A",
            }
            for m in matches
        ])

        try:
            st.dataframe(summary_df, width="stretch")  # type: ignore[call-arg]
        except Exception:
            st.dataframe(summary_df)  # type: ignore[call-arg]

    except Exception as e:
        st.error(f"Error fetching matches: {e}")


def display_match_card(match: Dict[str, Any], match_type: str, idx: int) -> None:
    """Display a single match card"""
    col1, col2 = st.columns((3, 1))

    with col1:
        # Match Header
        team1 = match.get("team1_name", "N/A")
        team2 = match.get("team2_name", "N/A")
        st.markdown(f"### {team1} vs {team2}")

        # Match Details
        col1_details, col2_details = st.columns(2)
        with col1_details:
            st.write(f"**Format**: {match.get('matchFormat') or match.get('match_format') or 'N/A'}")
            st.write(f"**Status**: {match.get('status', 'N/A')}")
            start_date = match.get('startDate') or match.get('start_date') or 'N/A'
            if start_date != 'N/A' and str(start_date).isdigit():
                try:
                    date_obj = datetime.fromtimestamp(int(start_date) / 1000)
                    formatted_date = date_obj.strftime("%d %b %Y, %H:%M")
                    st.write(f"**Date**: {formatted_date}")
                except:
                    st.write(f"**Date**: {start_date}")
            else:
                st.write(f"**Date**: {start_date}")

        with col2_details:
            st.write(f"**Venue**: {match.get('venue') or match.get('venue_name') or match.get('ground') or 'N/A'}")
            st.write(f"**City**: {match.get('city') or match.get('venue_city') or 'N/A'}")

        # Score Information
        if match_type in ["Live", "Recent"]:
            st.markdown("### Match Score")
            score_col1, score_col2 = st.columns(2)

            # Try values from the normalized match first
            match_id = match.get("matchId") or match.get("external_match_id") or match.get("match_id")
            cache_key = f"score_cache_{match_id}" if match_id else None

            t1_runs = match.get("team1_score")
            t1_wickets = match.get("team1_wickets")
            t1_overs = match.get("team1_overs")

            t2_runs = match.get("team2_score")
            t2_wickets = match.get("team2_wickets")
            t2_overs = match.get("team2_overs")

            # If nothing is present, try a cached score fetched from the scorecard
            if cache_key and cache_key in st.session_state:
                cached = st.session_state.get(cache_key, {})
                t1_runs = t1_runs if t1_runs is not None else cached.get("team1_score")
                t1_wickets = t1_wickets if t1_wickets is not None else cached.get("team1_wickets")
                t1_overs = t1_overs if t1_overs is not None else cached.get("team1_overs")
                t2_runs = t2_runs if t2_runs is not None else cached.get("team2_score")
                t2_wickets = t2_wickets if t2_wickets is not None else cached.get("team2_wickets")
                t2_overs = t2_overs if t2_overs is not None else cached.get("team2_overs")

            # If still missing and we have an id, fetch the scorecard (best-effort) and cache it
            if (t1_runs is None or t1_runs == "") and cache_key and cache_key not in st.session_state and match_id:
                try:
                    api_key: str = str(st.secrets.get("RAPIDAPI_KEY", ""))
                    api_client = get_api_client(api_key)
                    sc = api_client.get_scorecard(str(match_id))
                    innings = sc.get("scorecard") or sc.get("scoreCard") or []
                    if innings:
                        def _safe(inn, field):
                            return inn.get("scoreDetails", {}).get(field) if isinstance(inn, dict) else inn.get(field)

                        t1 = innings[0]
                        t1_runs = _safe(t1, "runs") or t1.get("runs") or t1.get("score")
                        t1_wickets = _safe(t1, "wickets") or t1.get("wickets")
                        t1_overs = _safe(t1, "overs") or t1.get("overs")

                        if len(innings) > 1:
                            t2 = innings[1]
                            t2_runs = _safe(t2, "runs") or t2.get("runs") or t2.get("score")
                            t2_wickets = _safe(t2, "wickets") or t2.get("wickets")
                            t2_overs = _safe(t2, "overs") or t2.get("overs")

                        st.session_state[cache_key] = {
                            "team1_score": t1_runs,
                            "team1_wickets": t1_wickets,
                            "team1_overs": t1_overs,
                            "team2_score": t2_runs,
                            "team2_wickets": t2_wickets,
                            "team2_overs": t2_overs,
                        }
                except Exception as e:
                    print(f"Warning: could not fetch scorecard for match {match_id}: {e}")

            with score_col1:
                if t1_runs is not None and str(t1_runs) != "":
                    st.write(f"**{team1}**: {t1_runs}/{t1_wickets or 'N/A'} ({t1_overs or 'N/A'} ov)")
                else:
                    st.write(f"**{team1}**: Score not available")

            with score_col2:
                if t2_runs is not None and str(t2_runs) != "":
                    st.write(f"**{team2}**: {t2_runs}/{t2_wickets or 'N/A'} ({t2_overs or 'N/A'} ov)")
                else:
                    st.write(f"**{team2}**: Score not available")
            
            if st.button(
                "📋 View Scorecard",
                key=f"scard_{match.get('matchId') or match.get('external_match_id')}_{idx}",
            ):
                st.session_state[f"show_scorecard_{idx}"] = True
            
            if st.session_state.get(f"show_scorecard_{idx}", False):
                display_scorecard(match)

        if match.get("matchDesc") or match.get('match_desc'):
            st.info(f"📝 {match.get('matchDesc') or match.get('match_desc')}")

    with col2:
        pass


def display_scorecard(match: Dict[str, Any]) -> None:
    """Display full scorecard for a match"""
    st.markdown("---")
    st.markdown("### 📊 Full Scorecard")

    match_id = match.get("matchId") or match.get("external_match_id")
    if not match_id:
        st.warning("Match ID not available")
        return

    try:
        api_key: str = str(st.secrets.get("RAPIDAPI_KEY", "5ff5c15309msh270be5dd89152b5p1f3d98jsnf270423b3863"))
        api_client = get_api_client(api_key)

        with st.spinner("Loading scorecard..."):
            scorecard_data = api_client.get_scorecard(str(match_id))

        if not scorecard_data:
            st.warning("Unable to fetch scorecard")
            return

        # Store match data in MySQL
        try:
            mysql_secrets: Dict[str, Any] = {
                "host": "localhost",
                "user": "root",
                "password": "Vasu@76652",
                "database": "cricketdb",
                "port": 3306,
            }
            
            # create_mysql_schema(mysql_secrets)
            if "mysql_schema_ready" not in st.session_state:
                create_mysql_schema(mysql_secrets)
                st.session_state["mysql_schema_ready"] = True

            rc = upsert_match(mysql_secrets, match)
            print(f"DEBUG: display_scorecard upsert_match rc={rc} for match {match_id}")
            
            innings_list_for_db = scorecard_data.get("scorecard", [])
            for inning in innings_list_for_db:
                innings_id = inning.get("inningsId", "")
                if innings_id:
                    try:
                        enriched_inning = dict(inning)
                        if "batTeamName" not in enriched_inning and "batteamname" in enriched_inning:
                            enriched_inning["batTeamName"] = enriched_inning.get("batteamname")
                        if "bowlTeamName" not in enriched_inning and "bowlteamname" in enriched_inning:
                            enriched_inning["bowlTeamName"] = enriched_inning.get("bowlteamname")

                        if not enriched_inning.get("bowlTeamName"):
                            t1 = match.get("team1_name") or (match.get("team1") or {}).get("teamName")
                            t2 = match.get("team2_name") or (match.get("team2") or {}).get("teamName")
                            t1_short = match.get("team1_short") or (match.get("team1") or {}).get("teamSName")
                            t2_short = match.get("team2_short") or (match.get("team2") or {}).get("teamSName")
                            bat_name = enriched_inning.get("batTeamName") or enriched_inning.get("batteamname") or enriched_inning.get("batteamsname")
                            if bat_name and (t1 or t2):
                                if (t1_short and bat_name == t1_short) or (t1 and bat_name == t1) or (t1 and isinstance(bat_name, str) and t1.startswith(bat_name)):
                                    enriched_inning["bowlTeamName"] = t2
                                else:
                                    enriched_inning["bowlTeamName"] = t1

                        inn_rc = upsert_innings(mysql_secrets, str(match_id), enriched_inning)
                        print(f"DEBUG: display_scorecard upsert_innings rc={inn_rc} for match {match_id} innings {innings_id}")
                    except Exception as e:
                        print(f"Warning: display_scorecard upsert_innings failed: {e}")

                    batsmen = inning.get("batsman", inning.get("batsmen", []))
                    if batsmen:
                        b_rc = upsert_batting(mysql_secrets, str(match_id), str(innings_id), batsmen)
                        print(f"DEBUG: display_scorecard upsert_batting rc={b_rc} for match {match_id} innings {innings_id}")

                    bowlers = inning.get("bowler", inning.get("bowlers", []))
                    if bowlers:
                        bw_rc = upsert_bowling(mysql_secrets, str(match_id), str(innings_id), bowlers)
                        print(f"DEBUG: display_scorecard upsert_bowling rc={bw_rc} for match {match_id} innings {innings_id}")

                    partnerships = inning.get("partnerships", inning.get("partnership", []))
                    if partnerships:
                        p_rc = upsert_partnerships(mysql_secrets, str(match_id), str(innings_id), partnerships)
                        print(f"DEBUG: display_scorecard upsert_partnerships rc={p_rc} for match {match_id} innings {innings_id}")
            
            st.success("✅ Scorecard saved to MySQL")
        except Exception as e:
            st.warning(f"Note: Could not save to MySQL: {e}")

        # Display innings
        innings_list = scorecard_data.get("scorecard", [])
        if innings_list:
            for inning in innings_list:
                inning_desc = inning.get(
                    "inningDescription",
                    f"Innings {inning.get('inningsid', 'N/A')}"
                )
                st.markdown(f"#### {inning_desc}")

                # Batting Table
                batting_data: List[Dict[str, Any]] = []
                batsmen = inning.get("batsman", inning.get("batsmen", []))
                if batsmen:
                    for raw_batter in batsmen:
                        batter = cast(Dict[str, Any], raw_batter)

                        sr_raw = (
                            batter.get("strkrate")
                            or batter.get("sr")
                            or batter.get("strikerate")
                            or ""
                        )
                        if sr_raw is None or sr_raw == "":
                            sr = ""
                        else:
                            try:
                                sr = f"{float(sr_raw):.2f}"
                            except Exception:
                                sr = str(sr_raw)

                        wicket_info = batter.get('wicketInfo')
                        wicket_dict = cast(Dict[str, Any], wicket_info) if isinstance(wicket_info, dict) else {}
                        dismissal = (
                            batter.get('outdec', '')
                            or batter.get('dismissalText', '')
                            or wicket_dict.get('dismissalText', 'not out')
                        )

                        batting_data.append({
                            "Batter": batter.get("name", ""),
                            "Runs": batter.get("runs", ""),
                            "Balls": batter.get("balls", ""),
                            "4s": batter.get("fours", ""),
                            "6s": batter.get("sixes", ""),
                            "SR": sr,
                            "Dismissal": dismissal,
                        })

                extras_any = inning.get('extras')
                extras: Dict[str, Any] = cast(Dict[str, Any], extras_any) if isinstance(extras_any, dict) else {}
                if extras:
                    batting_data.append({
                        'Batter': 'Extras',
                        'Runs': str(extras.get('total', 0)),
                        'Balls': '-',
                        '4s': '-',
                        '6s': '-',
                        'SR': '',
                        'Dismissal': f"w {extras.get('wides', 0)}, nb {extras.get('noballs', 0)}, b {extras.get('byes', 0)}, lb {extras.get('legbyes', 0)}"
                    })
                try:
                    st.dataframe(batting_data, width="stretch")  # type: ignore[call-arg]
                except Exception:
                    st.dataframe(batting_data)  # type: ignore[call-arg]
                # Bowling Table
                bowlers = inning.get("bowler", inning.get("bowlers", []))
                if bowlers:
                    st.markdown("**Bowling**")
                    bowling_rows = [
                        {
                            "Bowler": bw.get("name", ""),
                            "Overs": bw.get("overs", ""),
                            "Maidens": bw.get("maidens", ""),
                            "Runs": bw.get("runs", ""),
                            "Wickets": bw.get("wickets", ""),
                            "Economy": bw.get("economy", ""),
                        }
                        for bw in bowlers
                    ]
                    try:
                        st.dataframe(bowling_rows, width="stretch")  # type: ignore[call-arg]
                    except Exception:
                        st.dataframe(bowling_rows)  # type: ignore[call-arg]
        else:
            st.info("Detailed scorecard not available yet")

    except Exception as e:
        st.error(f"Error loading scorecard: {e}")