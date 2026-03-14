"""
Cricbuzz API Client
-------------------
Pure API access layer for Cricbuzz (RapidAPI).

Responsibilities:
- Fetch match lists (live / recent / upcoming)
- Fetch scorecards
- Extract partnerships from scorecards
- Fetch optional player / venue profiles

NO database logic
NO Streamlit UI logic
"""

from typing import Dict, Any, List, Optional
import requests

# Optional Streamlit caching helper (used by pages)
try:
    import streamlit as st
except Exception:
    st = None


def get_api_client(api_key: str) -> "CricbuzzAPIClient":
    """Factory for creating (and optionally caching) a `CricbuzzAPIClient`.

    If Streamlit is available at runtime we wrap the factory in `st.cache_data`
    to avoid recreating clients each render.
    """
    client = CricbuzzAPIClient(api_key)
    return client

# If Streamlit is available, prefer caching the factory to reuse client instances
if st is not None:
    try:
        get_api_client = st.cache_data(get_api_client)
    except Exception:
        # Older versions of Streamlit might not expose cache_data; ignore in that case
        pass


class CricbuzzAPIClient:
    """Low-level client for Cricbuzz Cricket API via RapidAPI"""

    BASE_HOST = "cricbuzz-cricket.p.rapidapi.com"

    def __init__(self, api_key: str, timeout: int = 10) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = f"https://{self.BASE_HOST}"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": self.BASE_HOST,
        }

    # ---------------------------------------------------------
    # Match list APIs
    # ---------------------------------------------------------
    def get_live_matches(self) -> Dict[str, Any]:
        return self._get("/matches/v1/live")

    def get_recent_matches(self) -> Dict[str, Any]:
        return self._get("/matches/v1/recent")

    def get_upcoming_matches(self) -> Dict[str, Any]:
        return self._get("/matches/v1/upcoming")

    # ---------------------------------------------------------
    # Scorecard API
    # ---------------------------------------------------------
    def get_scorecard(self, match_id: str) -> Dict[str, Any]:
        return self._get(f"/mcenter/v1/{match_id}/scard")

    # ---------------------------------------------------------
    # Team APIs
    # ---------------------------------------------------------
    def get_international_teams(self) -> Dict[str, Any]:
        """Fetch all international teams with metadata (country, team info)"""
        return self._get("/teams/v1/international")

    def get_league_teams(self) -> Dict[str, Any]:
        """Fetch all league teams"""
        return self._get("/teams/v1/league")

    def get_domestic_teams(self) -> Dict[str, Any]:
        """Fetch all domestic teams"""
        return self._get("/teams/v1/domestic")

    def get_women_teams(self) -> Dict[str, Any]:
        """Fetch all women's teams"""
        return self._get("/teams/v1/women")

    def get_team_players(self, team_id: str) -> Dict[str, Any]:
        """Fetch all players for a given team"""
        return self._get(f"/teams/v1/{team_id}/players")

    def get_player_profile(self, player_id: str) -> Dict[str, Any]:
        """Fetch player profile from /stats/v1/player/{player_id}
        
        Returns player metadata including country, DOB, role, etc.
        """
        return self._get(f"/stats/v1/player/{player_id}")

    def get_venue_profile(self, venue_id: str) -> Dict[str, Any]:
        return self._get(f"/venues/v1/{venue_id}/matches")

    def get_all_teams_with_country(self) -> Dict[str, Dict[str, Any]]:
        """Fetch teams from all categories and return as {team_id: {name, country, ...}}"""
        all_teams: Dict[str, Dict[str, Any]] = {}
        
        for endpoint in [
            "/teams/v1/international",
            "/teams/v1/league",
            "/teams/v1/domestic",
            "/teams/v1/women"
        ]:
            try:
                resp = self._get(endpoint)
                for team in resp.get("teams", []):
                    # Support multiple possible id fields returned by different endpoints
                    raw_id = team.get("id") or team.get("teamId") or team.get("team_id")
                    if raw_id is None:
                        continue
                    team_id = str(raw_id)

                    # Normalize name and country fields from various payload shapes
                    name = team.get("name") or team.get("teamName") or team.get("team_name")
                    country = (
                        team.get("countryName")
                        or team.get("country")
                        or (team.get("teamInfo") or {}).get("country")
                        or team.get("country_name")
                        or name
                    )

                    all_teams[team_id] = {
                        "id": team_id,
                        "name": name,
                        "country": country,
                        "type": team.get("type"),
                    }
            except Exception:
                # Silently skip if endpoint fails or team list not available
                pass
        
        return all_teams

    # ---------------------------------------------------------
    # Internal request helper
    # ---------------------------------------------------------
    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()


# =====================================================================
# NORMALIZATION HELPERS (NO DB, NO SQL)
# =====================================================================

def normalize_matches(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Flatten Cricbuzz match list API response into simple dictionaries.

    Used by Streamlit pages and MySQL sync layer.
    """
    matches: List[Dict[str, Any]] = []

    for type_block in data.get("typeMatches", []):
        match_type = type_block.get("matchType")

        for series_block in type_block.get("seriesMatches", []):
            wrapper = series_block.get("seriesAdWrapper")
            if not wrapper:
                continue

            series_id = wrapper.get("seriesId")
            series_name = wrapper.get("seriesName")

            for m in wrapper.get("matches", []):
                info = m.get("matchInfo", {})
                venue = info.get("venueInfo", {})

                team1 = info.get("team1", {})
                team2 = info.get("team2", {})

                matches.append({
                    "match_type": match_type,
                    "external_match_id": str(info.get("matchId")),
                    "external_series_id": str(series_id) if series_id else None,
                    "series_name": series_name,
                    "match_desc": info.get("matchDesc"),
                    "match_format": info.get("matchFormat"),
                    "start_date": info.get("startDate"),
                    "end_date": info.get("endDate"),
                    "state": info.get("state"),
                    "status": info.get("status"),

                    "team1_name": team1.get("teamName"),
                    "team1_short": team1.get("teamSName"),
                    "external_team1_id": str(team1.get("teamId")) if team1.get("teamId") else None,

                    "team2_name": team2.get("teamName"),
                    "team2_short": team2.get("teamSName"),
                    "external_team2_id": str(team2.get("teamId")) if team2.get("teamId") else None,

                    "external_venue_id": str(venue.get("id")) if venue.get("id") else None,
                    "venue_name": venue.get("ground"),
                    "venue_city": venue.get("city"),
                    "venue_country": venue.get("country"),
                    "series_start_date": info.get("seriesStartDt"),
                    "series_end_date": info.get("seriesEndDt"),
                    "series_type": info.get("matchFormat"),
                })

    return matches


# =====================================================================
# SCORECARD EXTRACTION HELPERS
# =====================================================================

def extract_innings(scorecard: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract innings summary from scorecard JSON."""
    innings_list: List[Dict[str, Any]] = []

    for inns in scorecard.get("scoreCard", []):
        innings_list.append({
            "innings_id": str(inns.get("inningsId")),
            "batting_team": inns.get("batTeamName"),
            "bowling_team": inns.get("bowlTeamName"),
            "runs": inns.get("scoreDetails", {}).get("runs"),
            "wickets": inns.get("scoreDetails", {}).get("wickets"),
            "overs": inns.get("scoreDetails", {}).get("overs"),
            "meta": inns,
        })

    return innings_list


def extract_batting(scorecard: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for inns in scorecard.get("scoreCard", []):
        innings_id = str(inns.get("inningsId"))
        batsmen = inns.get("batTeamDetails", {}).get("batsmenData", {})

        for b in batsmen.values():
            rows.append({
                "innings_id": innings_id,
                "external_player_id": str(b.get("batId")) if b.get("batId") else None,
                "player_name": b.get("batName"),
                "runs": b.get("runs"),
                "balls": b.get("balls"),
                "fours": b.get("fours"),
                "sixes": b.get("sixes"),
                "strike_rate": b.get("strikeRate"),
                "dismissal": b.get("outDesc"),
                "meta": b,
            })

    return rows


def extract_bowling(scorecard: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for inns in scorecard.get("scoreCard", []):
        innings_id = str(inns.get("inningsId"))
        bowlers = inns.get("bowlTeamDetails", {}).get("bowlersData", {})

        for bw in bowlers.values():
            rows.append({
                "innings_id": innings_id,
                "external_player_id": str(bw.get("bowlId")) if bw.get("bowlId") else None,
                "player_name": bw.get("bowlName"),
                "overs": bw.get("overs"),
                "maidens": bw.get("maidens"),
                "runs_conceded": bw.get("runs"),
                "wickets": bw.get("wickets"),
                "economy": bw.get("economy"),
                "meta": bw,
            })

    return rows


# =====================================================================
# PARTNERSHIP EXTRACTION (NEW – 9th TABLE)
# =====================================================================

def extract_partnerships(scorecard: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract partnership data from scorecard JSON.

    Used to populate the `partnerships` table.
    """
    rows: List[Dict[str, Any]] = []

    for inns in scorecard.get("scoreCard", []):
        innings_id = str(inns.get("inningsId"))
        partnerships = inns.get("partnershipsData", [])

        for p in partnerships:
            rows.append({
                "Innings_ID": innings_id,
                "wicket_number": p.get("wkts"),
                "Player1": p.get("bat1Name"),
                "Player2": p.get("bat2Name"),
                "Runs": p.get("runs"),
                "Balls": p.get("balls"),
                "Meta": p,
            })

    return rows


# =====================================================================
# PLAYER PROFILE EXTRACTION
# =====================================================================

def extract_player_metadata(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract player metadata from player profile API response.
    
    The /stats/v1/player/{player_id} endpoint returns:
    {
        "Player_ID": 6635,
        "Player_Name": "Virat Kohli",
        "Country": "India",
        "DOB": "1988-11-05",
        "Role": "Batsman" or "Bowler" or "All-rounder" or "Wicket-keeper",
        ... other fields
    }
    
    Returns a dict with normalized keys for upsert_player():
    {
        "Player_ID": player_id,
        "Player_Name": player_name,
        "Country": country,
        "DOB": DOB date string,
        "Role": role string
    }
    """
    return {
        "Player_ID": profile.get("id"),
        "Player_Name": profile.get("name"),
        "Country": profile.get("country"),
        "DOB": profile.get("dateOfBirth"),
        "Role": profile.get("role"),
        "player_role": profile.get("role"),  # Alternate key for compatibility
        "Meta": profile,
    }


# =====================================================================
# VENUE PROFILE EXTRACTION
# =====================================================================

def extract_venue_metadata(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract venue metadata from venue profile API response.

    The /venues/v1/{venue_id} endpoint returns:
    {
        "Venue_ID": 123,
        "Venue_Name": "Eden Gardens",
        "City": "Kolkata",
        "Country": "India",
        "Capacity": 66000,
        "timezone": "UTC+5:30",
        ... other fields
    }

    Returns a dict with normalized keys for upsert_venue():
    {
        "Venue_ID": venue_id,
        "Venue_Name": ground name,
        "City": city name,
        "Country": country name,
        "Capacity": integer,
        "Time_Zone": timezone string
    }
    """
    return {
        "Venue_ID": profile.get("id"),
        "Venue_Name": profile.get("ground"),
        "City": profile.get("city"),
        "Country": profile.get("country"),
        "Capacity": profile.get("capacity"),
        "Time_Zone": profile.get("timezone") or profile.get("timeZone"),
        "Meta": profile,
    }
    
# =====================================================================
# Team Profile EXTRACTION
# =====================================================================

def extract_team_metadata(team: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract team metadata from team profile API response.
    
    Supports multiple payload formats (API variants and normalized).
    Falls back to team name when country is missing.

    Returns a dict with normalized keys for upsert_team():
    {
        "Team_ID": team_id,
        "Team_Name": team name,
        "Country": country name (or team name if country missing)
    }
    """
    team_id = team.get("teamId") or team.get("id")
    team_name = (
        team.get("teamName")
        or team.get("name")
        or None
    )
    
    country = (
        team.get("countryName")
        or team.get("country")
        or team.get("country_name")
        or None
    )
    
    # Fallback: use team name as country when country is missing
    if not country and team_name:
        country = team_name
    
    return {
        "Team_ID": team_id,
        "Team_Name": team_name,
        "Country": country,
        "Meta": team
    }
    
