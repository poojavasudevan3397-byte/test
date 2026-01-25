"""
MySQL Sync Helpers (SOURCE OF TRUTH)

- Creates all cricket tables
- Provides upsert helpers
- Used ONLY for writing data (API → DB)
"""

from typing import Any, Dict, List, Tuple, cast, Optional, Union
from datetime import datetime  #type: ignore
import json
import traceback #type: ignore

# Optional imports
create_engine = None
pymysql_module = None

try:
    from sqlalchemy import create_engine as sa_create_engine, text #type: ignore
    create_engine = sa_create_engine
except Exception:
    create_engine = None

try:
    import pymysql as pymysql_module
except Exception:
    pymysql_module = None


# -------------------------------------------------
# Internal helpers
# -------------------------------------------------
def _get_pymysql():
    if pymysql_module is None:
        raise RuntimeError("pymysql not installed")
    return pymysql_module


def _execute(engine_or_secrets: Any, sql: str, params: Tuple[Any, ...]) -> Optional[int]:
    """Execute SQL safely (SQLAlchemy or pymysql). Returns rowcount when available."""
    # SQLAlchemy engine/connection
    if hasattr(engine_or_secrets, "connect") and create_engine:
        raw = engine_or_secrets.raw_connection()
        cur = raw.cursor()
        try:
            cur.execute(sql, params)
            raw.commit()
            rowcount = getattr(cur, "rowcount", None)
        finally:
            cur.close()
            raw.close()
        return rowcount

    # Accept plain dicts as well as mapping-like objects (e.g. Streamlit secrets)
    from collections.abc import Mapping

    if isinstance(engine_or_secrets, Mapping):
        secrets: Dict[str, Any] = cast(Dict[str, Any], engine_or_secrets)
        pm = _get_pymysql()
        try:
            conn = pm.connect(
                host=str(secrets.get("host") or "127.0.0.1"),
                user=str(secrets.get("user") or "root"),
                password=str(secrets.get("password") or ""),
                database=str(secrets.get("database") or secrets.get("dbname") or ""),
                port=int(secrets.get("port") or 3306),
                charset="utf8mb4",
            )
            with conn.cursor() as cur:
                rc = cur.execute(sql, params)
            conn.commit()
            conn.close()
            return rc
        except Exception as e:
            # Log helpful debug info (do not print secrets)
            print(f"ERROR executing SQL: {e}; SQL=<{sql[:200]}>; params={params}")
            raise

    raise RuntimeError(f"Unsupported engine_or_secrets: {type(engine_or_secrets)!r}")


# -------------------------------------------------
# Schema creation (9 tables)
# -------------------------------------------------
def create_mysql_schema(engine_or_secrets: Any):
    tables = [

        # 1. Series
        """
        CREATE TABLE IF NOT EXISTS series (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_series_id VARCHAR(50) UNIQUE,
            series_name VARCHAR(255),
            series_type VARCHAR(100),
            start_date DATETIME,
            end_date DATETIME,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 2. Teams
        """
        CREATE TABLE IF NOT EXISTS teams (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_team_id VARCHAR(50) UNIQUE,
            team_name VARCHAR(255),
            country VARCHAR(100),
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 3. Players
        """
        CREATE TABLE IF NOT EXISTS players (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_player_id VARCHAR(50) UNIQUE,
            player_name VARCHAR(255),
            country VARCHAR(100),
            role VARCHAR(100),
            date_of_birth DATE,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 4. Venues ✅ (FIXED)
        """
        CREATE TABLE IF NOT EXISTS venues (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_venue_id VARCHAR(50) UNIQUE,
            venue_name VARCHAR(255),
            city VARCHAR(100),
            country VARCHAR(100),
            timezone VARCHAR(50),
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 5. Matches
        """
        CREATE TABLE IF NOT EXISTS matches (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(50) UNIQUE,
            external_series_id VARCHAR(50),
            external_venue_id VARCHAR(50),
            match_desc VARCHAR(255),
            match_format VARCHAR(20),
            start_date DATETIME,
            status VARCHAR(255),
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 6. Innings
        """
        CREATE TABLE IF NOT EXISTS innings (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(50),
            innings_id VARCHAR(50),
            batting_team VARCHAR(255),
            bowling_team VARCHAR(255),
            runs INT,
            wickets INT,
            overs FLOAT,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 7. Batting stats
        """
        CREATE TABLE IF NOT EXISTS batting_stats (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(50),
            innings_id VARCHAR(50),
            player_name VARCHAR(255),
            runs INT,
            balls INT,
            fours INT,
            sixes INT,
            strike_rate FLOAT,
            dismissal VARCHAR(255),
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 8. Bowling stats
        """
        CREATE TABLE IF NOT EXISTS bowling_stats (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(50),
            innings_id VARCHAR(50),
            player_name VARCHAR(255),
            overs FLOAT,
            maidens INT,
            runs_conceded INT,
            wickets INT,
            economy FLOAT,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,

        # 9. Partnerships
        """
        CREATE TABLE IF NOT EXISTS batting_partnerships (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            external_match_id VARCHAR(50),
            innings_id VARCHAR(50),
            player1 VARCHAR(255),
            player2 VARCHAR(255),
            runs INT,
            balls INT,
            meta JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]

    for stmt in tables:
        _execute(engine_or_secrets, stmt, ())

    # Backwards-compatible migrations (safe to re-run)
    try:
        # Older MySQL versions don't support "ADD COLUMN IF NOT EXISTS"; attempt and ignore "column exists" errors
        _execute(engine_or_secrets, "ALTER TABLE players ADD COLUMN date_of_birth DATE", ())
    except Exception as e:
        msg = str(e).lower()
        if "duplicate column" in msg or "already exists" in msg or "1060" in msg:
            # Column already exists; nothing to do
            pass
        else:
            # Log the warning but do not raise to keep schema creation resilient
            print(f"Warning: could not add date_of_birth column: {e}")


# -------------------------------------------------
# UPSERT HELPERS
# -------------------------------------------------
def upsert_series(
    engine_or_secrets: Any,
    series_id: str,
    series_name: str,
    series_type: Optional[str] = None,
    series_start_ms: Optional[int] = None,
    series_end_ms: Optional[int] = None,
) -> Optional[int]:
    """
    Upsert a series record with optional type and start/end dates (timestamps in ms).
    Dates are converted to datetimes if provided; existing non-null values are preserved.
    """
    # Convert timestamps in milliseconds to Python datetimes or None
    start_dt = None
    end_dt = None
    try:
        if series_start_ms is not None and series_start_ms != 0:
            start_dt = datetime.fromtimestamp(int(series_start_ms) / 1000)
    except Exception:
        start_dt = None
    try:
        if series_end_ms is not None and series_end_ms != 0:
            end_dt = datetime.fromtimestamp(int(series_end_ms) / 1000)
    except Exception:
        end_dt = None

    sql = """
    INSERT INTO series (external_series_id, series_name, series_type, start_date, end_date, meta)
    VALUES (%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        series_name = VALUES(series_name),
        series_type = COALESCE(VALUES(series_type), series_type),
        start_date = COALESCE(VALUES(start_date), start_date),
        end_date = COALESCE(VALUES(end_date), end_date),
        meta = VALUES(meta)
    """

    rc = _execute(
        engine_or_secrets,
        sql,
        (
            series_id,
            series_name,
            series_type,
            start_dt,
            end_dt,
            json.dumps({}),
        ),
    )
    return rc


def upsert_team(engine_or_secrets: Any, team_id: str, team_name: str, country: Optional[str] = None) -> Optional[int]:
    """
    Upsert a team record and optionally record its country. Existing non-null country is preserved.
    """
    sql = """
    INSERT INTO teams (external_team_id, team_name, country, meta)
    VALUES (%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        team_name = VALUES(team_name),
        country = COALESCE(VALUES(country), country),
        meta = VALUES(meta)
    """
    rc = _execute(engine_or_secrets, sql, (team_id, team_name, country, json.dumps({})))
    return rc


def upsert_player(engine_or_secrets: Any, player: Dict[str, Any]) -> Optional[int]:
    """Insert or update a player record with best-effort extraction of country, role and date_of_birth."""
    sql = """
    INSERT INTO players (external_player_id, player_name, country, role, date_of_birth, meta)
    VALUES (%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        player_name = VALUES(player_name),
        country = COALESCE(VALUES(country), country),
        role = COALESCE(VALUES(role), role),
        date_of_birth = COALESCE(VALUES(date_of_birth), date_of_birth),
        meta = VALUES(meta)
    """

    # Support a variety of player id/name fields returned by different endpoints
    pid = player.get("id") or player.get("pid") or player.get("playerId") or player.get("player_id") or player.get("external_player_id")
    external_id = str(pid) if pid is not None else None
    name = player.get("name") or player.get("playerName") or player.get("player_name") or player.get("fullName") or None

    # Defensive: some APIs include header rows like "BATSMEN" or "ALL ROUNDER" as 'player' objects
    # Skip inserting those when there is no external_id and the name matches common role headings
    def _is_role_header(n: Optional[str]) -> bool:
        if not n:
            return False
        norm = n.strip().lower()
        headers = {
            "batsmen", "batsman", "batters", "batter", "batting",
            "bowlers", "bowler", "bowling",
            "all rounder", "all-rounder", "allrounder", "all rounders",
            "wicket keeper", "wicket-keeper", "wicketkeeper",
            "batting allrounder", "batting all-rounder"
        }
        return norm in headers

    if external_id is None and _is_role_header(name):
        # Skip placeholder/header entries
        print(f"Skipping placeholder player row for name='{name}'")
        return 0

    # Country extraction (safely handle meta possibly being non-dict)
    meta_obj = player.get("meta")
    meta_country = None
    if isinstance(meta_obj, dict):
        meta_country = meta_obj.get("country")
    country = (
        player.get("country")
        or player.get("nationality")
        or player.get("country_name")
        or meta_country
        or None
    )

    # DOB extraction (store as-is; DB will accept YYYY-MM-DD or NULL)
    meta_dob = None
    if isinstance(meta_obj, dict):
        meta_dob = meta_obj.get("dateOfBirth")
    dob = (
        player.get("dateOfBirth")
        or player.get("dob")
        or player.get("birthDate")
        or meta_dob
        or None
    )

    # Role extraction: prefer explicit role, else infer from batting/bowling styles in meta
    role = player.get("role") or player.get("playingRole") or player.get("playerRole") or None
    if not role:
        meta_obj = player.get("meta")
        try:
            if isinstance(meta_obj, str):
                meta_obj = json.loads(meta_obj)
        except Exception:
            meta_obj = None

        bat_style = None
        bowl_style = None
        if isinstance(meta_obj, dict):
            bat_style = meta_obj.get("batting_style") or meta_obj.get("battingStyle")
            bowl_style = meta_obj.get("bowling_style") or meta_obj.get("bowlingStyle")
        bat_style = (bat_style or player.get("battingStyle") or "")
        bowl_style = (bowl_style or player.get("bowlingStyle") or "")

        try:
            bs = str(bat_style).lower()
            bw = str(bowl_style).lower()
            has_bat = bool(bs and bs.strip() and bs not in ["n/a", "none", ""])
            has_bowl = bool(bw and bw.strip() and bw not in ["n/a", "none", ""])
            if "wicket" in bs or "keeper" in bs:
                role = "Wicket-keeper"
            elif has_bat and has_bowl:
                role = "All-rounder"
            elif has_bat:
                role = "Batsman"
            elif has_bowl:
                role = "Bowler"
        except Exception:
            role = role or None

    rc = _execute(
        engine_or_secrets,
        sql,
        (
            external_id,
            name,
            country,
            role,
            dob,
            json.dumps(player),
        ),
    )
    return rc


def upsert_venue(engine_or_secrets: Any, venue: Dict[str, Any]) -> Optional[int]:
    sql = """
    INSERT INTO venues (external_venue_id, venue_name, city, country, timezone, meta)
    VALUES (%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE venue_name = VALUES(venue_name)
    """
    rc = _execute(
        engine_or_secrets,
        sql,
        (
            str(venue.get("id")),
            venue.get("ground"),
            venue.get("city"),
            venue.get("country"),
            venue.get("timezone"),
            json.dumps(venue),
        ),
    )
    return rc


def upsert_match(engine_or_secrets: Any, match: Dict[str, Any]) -> Optional[int]:
    # Tolerate both the raw API 'matchInfo' objects and the normalized match dicts
    def _first(*keys: str):
        for k in keys:
            v = match.get(k)
            if v is not None:
                return v
        return None

    match_id = _first("matchId", "match_id", "external_match_id")
    series_id = _first("seriesId", "series_id", "external_series_id")

    # venue may be an object under 'venueInfo' or just an id under 'external_venue_id' or 'venue'
    venue_obj_raw = _first("venueInfo", "venue")
    venue_id: Optional[str] = None
    if isinstance(venue_obj_raw, dict):
        venue_obj = cast(Dict[str, Any], venue_obj_raw)
        vid = venue_obj.get("id")
        if vid is not None:
            venue_id = str(vid)
    else:
        if venue_obj_raw is not None:
            venue_id = str(venue_obj_raw)

    if venue_id is None:
        ext_vid = _first("external_venue_id", "venue")
        if ext_vid is not None:
            venue_id = str(ext_vid)

    sql = """
    INSERT INTO matches (
        external_match_id,
        external_series_id,
        external_venue_id,
        match_desc,
        match_format,
        start_date,
        status,
        meta
    )
    VALUES (%s,%s,%s,%s,%s,FROM_UNIXTIME(%s/1000),%s,%s)
    ON DUPLICATE KEY UPDATE status = VALUES(status)
    """

    rc = _execute(
        engine_or_secrets,
        sql,
        (
            str(match_id) if match_id is not None else None,
            str(series_id) if series_id is not None else None,
            str(venue_id) if venue_id is not None else None,
            _first("matchDesc", "match_desc"),
            _first("matchFormat", "match_format"),
            _first("startDate", "start_date") or 0,
            _first("status"),
            json.dumps(match),
        ),
    )
    return rc


def upsert_batting(engine_or_secrets: Any, match_id: str, innings_id: str, rows: List[Dict[str, Any]]) -> Optional[int]:
    sql = """
    INSERT INTO batting_stats
    (external_match_id, innings_id, player_name, runs, balls, fours, sixes, strike_rate, dismissal, meta)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    total_rc = 0
    for r in rows:
        rc = _execute(
            engine_or_secrets,
            sql,
            (
                match_id,
                innings_id,
                r.get("name"),
                r.get("runs"),
                r.get("balls"),
                r.get("fours"),
                r.get("sixes"),
                r.get("strkrate"),
                r.get("outdec"),
                json.dumps(r),
            ),
        )
        if rc:
            total_rc += rc
    return total_rc


def upsert_bowling(engine_or_secrets: Any, match_id: str, innings_id: str, rows: List[Dict[str, Any]]) -> Optional[int]:
    sql = """
    INSERT INTO bowling_stats
    (external_match_id, innings_id, player_name, overs, maidens, runs_conceded, wickets, economy, meta)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    total_rc = 0
    for r in rows:
        rc = _execute(
            engine_or_secrets,
            sql,
            (
                match_id,
                innings_id,
                r.get("name"),
                r.get("overs"),
                r.get("maidens"),
                r.get("runs"),
                r.get("wickets"),
                r.get("economy"),
                json.dumps(r),
            ),
        )
        if rc:
            total_rc += rc
    return total_rc
def upsert_innings(
    engine_or_secrets: Any,
    match_id: str,
    inning: Dict[str, Any],
) -> Optional[int]:
    """
    Upsert a single innings record
    """
    sql = """
    INSERT INTO innings (
        external_match_id,
        innings_id,
        batting_team,
        bowling_team,
        runs,
        wickets,
        overs,
        meta
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        runs = VALUES(runs),
        wickets = VALUES(wickets),
        overs = VALUES(overs),
        meta = VALUES(meta)
    """

    innings_id = str(inning.get("inningsId") or inning.get("inningsid") or "")

    # Batting / Bowling team keys vary across APIs - accept multiple casings
    batting_team = (
        inning.get("batTeamName")
        or inning.get("batteamname")
        or inning.get("battingTeam")
        or inning.get("batting_team")
        or inning.get("batteam")
        or inning.get("batteamname")
    )

    bowling_team = (
        inning.get("bowlTeamName")
        or inning.get("bowlteamname")
        or inning.get("bowlingTeam")
        or inning.get("bowling_team")
        or inning.get("bowlteam")
    )

    # Runs may be under different keys (runs, score) or inside scoreDetails
    runs = inning.get("runs")
    if runs is None:
        runs = inning.get("score")
    if runs is None:
        sd = inning.get("scoreDetails") or {}
        runs = sd.get("runs") or sd.get("score")

    wickets = inning.get("wickets") or inning.get("wkt") or None

    overs = inning.get("overs") or inning.get("ovrs") or None

    rc = _execute(
        engine_or_secrets,
        sql,
        (
            match_id,
            innings_id,
            batting_team,
            bowling_team,
            runs,
            wickets,
            overs,
            json.dumps(inning),
        ),
    )
    return rc
def upsert_partnerships(
    engine_or_secrets: Any,
    match_id: str,
    innings_id: str,
    partnerships: List[Union[Dict[str, Any], str]],
) -> Optional[int]:
    """
    Upsert batting partnerships for an innings.

    The `partnerships` list may contain dicts (with keys like 'players', 'runs', 'balls')
    or raw strings; dicts are processed to extract player names and stats, strings are stored
    as raw text in the `meta` column.
    """
    sql = """
    INSERT INTO batting_partnerships (
        external_match_id,
        innings_id,
        player1,
        player2,
        runs,
        balls,
        meta
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    total_rc = 0
    for p in partnerships:
        if isinstance(p, dict):
            players = p.get("players", [])
            player1 = players[0].get("name") if len(players) > 0 and isinstance(players[0], dict) else None
            player2 = players[1].get("name") if len(players) > 1 and isinstance(players[1], dict) else None
            runs = p.get("runs")
            balls = p.get("balls")
            meta = json.dumps(p)
        else:
            # Some APIs return partnership as a simple string; store as raw text in meta
            player1 = None
            player2 = None
            runs = None
            balls = None
            meta = json.dumps({"raw": str(p)})

        rc = _execute(
            engine_or_secrets,
            sql,
            (
                match_id,
                innings_id,
                player1,
                player2,
                runs,
                balls,
                meta,
            ),
        )
        if rc:
            total_rc += rc
    return total_rc
