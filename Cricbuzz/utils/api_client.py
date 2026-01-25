# # """
# # Cricbuzz API Integration Module
# # Handles all API calls to Cricbuzz Cricket API via RapidAPI
# # """

# # import requests
# # import streamlit as st
# # from typing import Dict, Any, List, cast

# # # Treat Streamlit's dynamic members as Any so Pylance won't warn about
# # # unknown member types like `markdown`, `warning`, `cache_resource`, etc.
# # st = cast(Any, st)

# # class CricbuzzAPI:
# #     """Interface for Cricbuzz Cricket API"""

# #     def __init__(self, api_key: str):
# #         """Initialize API client with RapidAPI key"""
# #         self.api_key = api_key
# #         self.api_host = "cricbuzz-cricket.p.rapidapi.com"
# #         self.base_url = f"https://{self.api_host}"
# #         self.headers = {
# #             "X-RapidAPI-Key": api_key,
# #             "X-RapidAPI-Host": self.api_host,
# #         }
# #         self.timeout = 10

# #     def get_live_matches(self) -> Dict[str, Any]:
# #         """Fetch live matches"""
# #         try:
# #             url = f"{self.base_url}/matches/v1/live"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             # Use the exception variable so static analyzers see it's accessed
# #             st.error(f"Failed to fetch live matches: {e}")
# #             return {}

# #     def get_upcoming_matches(self) -> Dict[str, Any]:
# #         """Fetch upcoming matches"""
# #         try:
# #             url = f"{self.base_url}/matches/v1/upcoming"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             st.error(f"Failed to fetch upcoming matches: {e}")
# #             return {}

# #     def get_recent_matches(self) -> Dict[str, Any]:
# #         """Fetch recent matches"""
# #         try:
# #             url = f"{self.base_url}/matches/v1/recent"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             st.error(f"Failed to fetch recent matches: {e}")
# #             return {}

# #     def get_scorecard(self, match_id: str) -> Dict[str, Any]:
# #         """Fetch scorecard for a specific match"""
# #         try:
# #             url = f"{self.base_url}/mcenter/v1/{match_id}/scard"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             st.warning(f"Failed to fetch scorecard for match {match_id}: {e}")
# #             return {}

# #     def get_player_info(self, player_id: str) -> Dict[str, Any]:
# #         """Fetch player details by player id

# #         Endpoint: /stats/v1/player/{player_id}
# #         Returns the player profile JSON (dob, country, roles, etc.)
# #         """
# #         try:
# #             url = f"{self.base_url}/stats/v1/player/{player_id}"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             st.warning(f"Failed to fetch player info for {player_id}: {e}")
# #             return {}

# #     def get_venue_info(self, venue_id: str) -> Dict[str, Any]:
# #         """Fetch venue details by venue id

# #         Endpoint: /venues/v1/{venue_id}
# #         Returns venue metadata (ground, city, timezone, coordinates)
# #         """
# #         try:
# #             url = f"{self.base_url}/venues/v1/{venue_id}"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             st.warning(f"Failed to fetch venue info for {venue_id}: {e}")
# #             return {}

# #     def get_series(self) -> Dict[str, Any]:
# #         """Fetch cricket series information"""
# #         try:
# #             url = f"{self.base_url}/series/v1"
# #             response = requests.get(url, headers=self.headers, timeout=self.timeout)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             st.error(f"Failed to fetch series: {e}")
# #             return {}


# # @st.cache_resource
# # def get_api_client(api_key: str) -> CricbuzzAPI:
# #     """Get cached API client instance"""
# #     return CricbuzzAPI(api_key)


# # def get_player_info_by_id(api_key: str, player_id: str) -> Dict[str, Any]:
# #     """Convenience helper to fetch player info using an API key."""
# #     client = get_api_client(api_key)
# #     return client.get_player_info(player_id)


# # def get_venue_info_by_id(api_key: str, venue_id: str) -> Dict[str, Any]:
# #     """Convenience helper to fetch venue info using an API key."""
# #     client = get_api_client(api_key)
# #     return client.get_venue_info(venue_id)


# # def normalize_matches(data: Dict[str, Any]) -> List[Dict[str, Any]]:
# #     """
# #     Normalize API response into a flat list of matches
    
# #     Args:
# #         data: Raw API response
        
# #     Returns:
# #         List of normalized match dictionaries
# #     """
# #     matches: List[Dict[str, Any]] = []
    
# #     for type_match in data.get('typeMatches', []):
# #         match_type = type_match.get('matchType', 'Unknown')
        
# #         for series in type_match.get('seriesMatches', []):
# #             if 'ad' in series:
# #                 continue
                
# #             wrapper = series.get('seriesAdWrapper', series)
# #             series_name = wrapper.get('seriesName', 'N/A')
# #             series_id = wrapper.get('seriesId', '')
            
# #             for match in wrapper.get('matches', []):
# #                 match_info = match.get('matchInfo', {})
# #                 match_score = match.get('matchScore', {})
                
# #                 team1 = match_info.get('team1', {})
# #                 team2 = match_info.get('team2', {})
# #                 venue = match_info.get('venueInfo', {})
                
# #                 t1_score = match_score.get('team1Score', {})
# #                 t2_score = match_score.get('team2Score', {})
                
# #                 match_data: Dict[str, Any] = {
# #                     'matchType': match_type,
# #                     'seriesId': series_id,
# #                     'seriesName': series_name,
# #                     'matchId': match_info.get('matchId', ''),
# #                     'matchDesc': match_info.get('matchDesc', ''),
# #                     'matchFormat': match_info.get('matchFormat', ''),
# #                     'startDate': match_info.get('startDate'),
# #                     'endDate': match_info.get('endDate'),
# #                     'state': match_info.get('state', 'N/A'),
# #                     'status': match_info.get('status', 'N/A'),
# #                     'team1_name': team1.get('teamName', 'N/A'),
# #                     'team2_name': team2.get('teamName', 'N/A'),
# #                     'team1_short': team1.get('teamSName', ''),
# #                     'team2_short': team2.get('teamSName', ''),
# #                     'team1_id': team1.get('teamId', ''),
# #                     'team2_id': team2.get('teamId', ''),
# #                     'venue': venue.get('ground', 'N/A'),
# #                     'city': venue.get('city', 'N/A'),
# #                     'country': venue.get('country', 'N/A'),
# #                     'team1_score': t1_score.get('inngs1', {}).get('runs', 'N/A'),
# #                     'team1_wickets': t1_score.get('inngs1', {}).get('wickets', 'N/A'),
# #                     'team1_overs': t1_score.get('inngs1', {}).get('overs', 'N/A'),
# #                     'team2_score': t2_score.get('inngs1', {}).get('runs', 'N/A'),
# #                     'team2_wickets': t2_score.get('inngs1', {}).get('wickets', 'N/A'),
# #                     'team2_overs': t2_score.get('inngs1', {}).get('overs', 'N/A'),
# #                 }
                
# #                 matches.append(match_data)  # type: ignore[attr-defined]
    
# #     return matches



# """
# Cricbuzz API Integration Module
# Handles all API calls to Cricbuzz Cricket API via RapidAPI
# """

# import requests
# import streamlit as st
# from typing import Dict, Any, List, cast

# # FIX: cast Streamlit to Any only once
# st = cast(Any, st)


# class CricbuzzAPI:
#     """Interface for Cricbuzz Cricket API"""

#     def __init__(self, api_key: str):
#         """Initialize API client with RapidAPI key"""
#         self.api_key = api_key
#         self.api_host = "cricbuzz-cricket.p.rapidapi.com"
#         self.base_url = f"https://{self.api_host}"
#         self.headers = {
#             "X-RapidAPI-Key": api_key,
#             "X-RapidAPI-Host": self.api_host,
#         }
#         self.timeout = 10

#     # FIX: central request handler for safety
#     def _get(self, endpoint: str) -> Dict[str, Any]:
#         try:
#             url = f"{self.base_url}{endpoint}"
#             response = requests.get(url, headers=self.headers, timeout=self.timeout)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             st.error(f"API request failed ({endpoint}): {e}")
#             return {}

#     def get_live_matches(self) -> Dict[str, Any]:
#         return self._get("/matches/v1/live")

#     def get_upcoming_matches(self) -> Dict[str, Any]:
#         return self._get("/matches/v1/upcoming")

#     def get_recent_matches(self) -> Dict[str, Any]:
#         return self._get("/matches/v1/recent")

#     def get_scorecard(self, match_id: str) -> Dict[str, Any]:
#         return self._get(f"/mcenter/v1/{match_id}/scard")

#     def get_player_info(self, player_id: str) -> Dict[str, Any]:
#         return self._get(f"/stats/v1/player/{player_id}")

#     def get_venue_info(self, venue_id: str) -> Dict[str, Any]:
#         return self._get(f"/venues/v1/{venue_id}")

#     def get_series(self) -> Dict[str, Any]:
#         return self._get("/series/v1")


# # FIX: cache_data is safer than cache_resource for API clients
# @st.cache_data(show_spinner=False)
# def get_api_client(api_key: str) -> CricbuzzAPI:
#     return CricbuzzAPI(api_key)


# def get_player_info_by_id(api_key: str, player_id: str) -> Dict[str, Any]:
#     return get_api_client(api_key).get_player_info(player_id)


# def get_venue_info_by_id(api_key: str, venue_id: str) -> Dict[str, Any]:
#     return get_api_client(api_key).get_venue_info(venue_id)


# def normalize_matches(data: Dict[str, Any]) -> List[Dict[str, Any]]:
#     """
#     Normalize API response into a flat list of matches
#     """

#     matches: List[Dict[str, Any]] = []

#     for type_match in data.get("typeMatches", []):
#         match_type = type_match.get("matchType", "Unknown")

#         for series in type_match.get("seriesMatches", []):

#             # FIX: correct ad detection
#             wrapper = series.get("seriesAdWrapper")
#             if not wrapper:
#                 continue

#             series_name = wrapper.get("seriesName", "N/A")
#             series_id = wrapper.get("seriesId", "")

#             for match in wrapper.get("matches", []):
#                 match_info = match.get("matchInfo", {})
#                 match_score = match.get("matchScore", {})

#                 team1 = match_info.get("team1", {})
#                 team2 = match_info.get("team2", {})
#                 venue = match_info.get("venueInfo", {})

#                 # FIX: handle multiple innings safely
#                 def extract_score(team_score: Dict[str, Any]) -> Dict[str, Any]:
#                     for k in ("inngs1", "inngs2", "inngs3", "inngs4"):
#                         if k in team_score:
#                             return team_score[k]
#                     return {}

#                 t1 = extract_score(match_score.get("team1Score", {}))
#                 t2 = extract_score(match_score.get("team2Score", {}))

#                 match_data: Dict[str, Any] = {
#                     "matchType": match_type,
#                     "seriesId": series_id,
#                     "seriesName": series_name,
#                     "matchId": match_info.get("matchId"),
#                     "matchDesc": match_info.get("matchDesc"),
#                     "matchFormat": match_info.get("matchFormat"),
#                     "startDate": match_info.get("startDate"),
#                     "endDate": match_info.get("endDate"),
#                     "state": match_info.get("state"),
#                     "status": match_info.get("status"),
#                     "team1_name": team1.get("teamName"),
#                     "team2_name": team2.get("teamName"),
#                     "team1_short": team1.get("teamSName"),
#                     "team2_short": team2.get("teamSName"),
#                     "team1_id": team1.get("teamId"),
#                     "team2_id": team2.get("teamId"),
#                     "venue": venue.get("ground"),
#                     "city": venue.get("city"),
#                     "country": venue.get("country"),
#                     "team1_score": t1.get("runs"),
#                     "team1_wickets": t1.get("wickets"),
#                     "team1_overs": t1.get("overs"),
#                     "team2_score": t2.get("runs"),
#                     "team2_wickets": t2.get("wickets"),
#                     "team2_overs": t2.get("overs"),
#                 }

#                 matches.append(match_data)

#     return matches


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

    # ---------------------------------------------------------
    # Optional enrichers
    # ---------------------------------------------------------
    def get_player_profile(self, player_id: str) -> Dict[str, Any]:
        """Fetch player profile from /stats/v1/player/{player_id}
        
        Returns player metadata including country, DOB, role, etc.
        """
        return self._get(f"/stats/v1/player/{player_id}")

    def get_venue_profile(self, venue_id: str) -> Dict[str, Any]:
        return self._get(f"/venues/v1/{venue_id}")

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
                "innings_id": innings_id,
                "wicket_number": p.get("wkts"),
                "batsman1_name": p.get("bat1Name"),
                "batsman2_name": p.get("bat2Name"),
                "runs": p.get("runs"),
                "balls": p.get("balls"),
                "meta": p,
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
        "id": 6635,
        "name": "Virat Kohli",
        "country": "India",
        "dateOfBirth": "1988-11-05",
        "role": "Batsman" or "Bowler" or "All-rounder" or "Wicket-keeper",
        ... other fields
    }
    
    Returns a dict with normalized keys for upsert_player():
    {
        "id": player_id,
        "name": player_name,
        "country": country,
        "date_of_birth": DOB date string,
        "role": role string
    }
    """
    return {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "country": profile.get("country"),
        "date_of_birth": profile.get("dateOfBirth"),
        "role": profile.get("role"),
        "player_role": profile.get("role"),  # Alternate key for compatibility
        "meta": profile,
    }
