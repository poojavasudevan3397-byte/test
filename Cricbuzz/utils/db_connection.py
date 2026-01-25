# # # """
# # # Database Connection and Schema Management
# # # Supports SQLite, PostgreSQL, and MySQL
# # # """

# # # # pyright: reportUnknownMemberType=false
# # # import sqlite3
# # # import pymysql
# # # # `pymysql` is optional at runtime; avoid importing it unconditionally so the
# # # # module can be imported when the package is not installed. A runtime try/except
# # # # below will attempt to import it and otherwise leave `pymysql` as None.
# # # from typing import Dict, Any, cast, Sequence
# # # from collections.abc import Mapping
# # # import pandas as pd
# # # import streamlit as st
# # # import json
# # # from typing import cast

# # # # Treat Streamlit's dynamic members as Any for Pylance (markdown, warning, error, etc.)
# # # st = cast(Any, st)

# # # # Optional MySQL support
# # # pymysql = None
# # # try:
# # #     # type: ignore[reportMissingImports]
# # #     import pymysql  # type: ignore[reportMissingImports]
# # # except Exception:
# # #     pymysql = None  # type: ignore

# # # # Optional SQLAlchemy support for better pandas compatibility with MySQL
# # # sqlalchemy = None
# # # try:
# # #     from sqlalchemy import create_engine  # type: ignore[reportMissingImports]
# # #     sqlalchemy = True  # type: ignore
# # # except Exception:
# # #     sqlalchemy = None  # type: ignore


# # # def fetch_data_from_pymysql(query: str, conn: Any) -> pd.DataFrame:
# # #     """
# # #     Helper function to safely fetch data from pymysql connection.
# # #     Converts cursor results to DataFrame, handling column names properly.
# # #     """
# # #     try:
# # #         if hasattr(conn, 'cursor'):
# # #             # Raw pymysql connection
# # #             cursor = conn.cursor()
# # #             cursor.execute(query)
# # #             # Get column names from cursor description
# # #             columns = [desc[0] for desc in cursor.description]
# # #             # Fetch all data
# # #             data = cursor.fetchall()
# # #             # Convert to DataFrame
# # #             df = pd.DataFrame(data, columns=columns)
# # #             cursor.close()
# # #             return df
# # #         else:
# # #             # SQLAlchemy engine or other connection
# # #             return pd.read_sql(query, conn)
# # #     except Exception as e:
# # #         st.error(f"Error fetching data: {str(e)[:100]}")
# # #         return pd.DataFrame()

# # # try:
# # #     # type: ignore[reportMissingImports]
# # #     from utils.mysql_sync import create_mysql_schema  # type: ignore[reportMissingImports]
# # # except Exception:
# # #     create_mysql_schema = None  # type: ignore

# # # class DatabaseConnection:
# # #     """Handle database operations for Cricbuzz analytics"""

# # #     def __init__(self, db_type: str = "sqlite", db_path: str = "cricbuzzdb.db"):
# # #         """Initialize database connection"""
# # #         self.db_type = db_type
# # #         self.db_path = db_path
# # #         self.connection = None

# # #         # Resolve default sqlite path to the package repo so the DB file inside
# # #         # the `Cricbuzz` folder is used even when the process cwd differs.
# # #         if db_type == "sqlite":
# # #             try:
# # #                 from pathlib import Path
# # #                 if self.db_path == "cricbuzzdb.db":
# # #                     repo_root = Path(__file__).resolve().parents[1]
# # #                     self.db_path = str(repo_root.joinpath("cricbuzzdb.db"))
# # #             except Exception:
# # #                 # if anything goes wrong, fall back to provided db_path
# # #                 pass

# # #             self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
# # #             self.connection.row_factory = sqlite3.Row
# # #         else:
# # #             raise NotImplementedError("PostgreSQL/MySQL support coming soon")

# # #     def init_schema(self) -> None:
# # #         """Initialize database schema"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]

# # #         # Create tables
# # #         cursor.execute("DROP TABLE IF EXISTS players")
# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE players (
# # #                 team_id INTEGER,
# # #                 player_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 external_player_id TEXT,
# # #                 player_name TEXT NOT NULL,
# # #                 date_of_birth TEXT,
# # #                 country TEXT DEFAULT '',
# # #                 role TEXT DEFAULT '',
# # #                 batting_style TEXT,
# # #                 bowling_style TEXT,
# # #                 meta TEXT,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# # #             )
# # #             """
# # #         )

# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS matches (
# # #                 match_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 match_description TEXT,
# # #                 team1 TEXT NOT NULL,
# # #                 team2 TEXT NOT NULL,
# # #                 match_format TEXT,
# # #                 venue_id INTEGER,
# # #                 match_date TIMESTAMP,
# # #                 winning_team TEXT,
# # #                 victory_margin TEXT,
# # #                 victory_type TEXT,
# # #                 toss_winner TEXT,
# # #                 toss_decision TEXT,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# # #                 FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
# # #             )
# # #             """
# # #         )

# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS venues (
# # #                 venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 venue_name TEXT NOT NULL,
# # #                 city TEXT,
# # #                 country TEXT,
# # #                 capacity INTEGER,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# # #             )
# # #             """
# # #         )
# # #         # Teams table (store short name and flag)
# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS teams (
# # #                 team_id INTEGER PRIMARY KEY,
# # #                 team_name TEXT NOT NULL,
# # #                 team_short_name TEXT,
# # #                 team_flag TEXT,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# # #             )
# # #             """
# # #         )
# # #         # Safe migrations: add missing columns if table existed before
# # #         try:
# # #             cursor.execute("ALTER TABLE teams ADD COLUMN team_short_name TEXT")
# # #         except Exception:
# # #             pass
# # #         try:
# # #             cursor.execute("ALTER TABLE teams ADD COLUMN team_flag TEXT")
# # #         except Exception:
# # #             pass

# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS series (
# # #                 series_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 series_name TEXT NOT NULL UNIQUE,
# # #                 series_short_name TEXT,
# # #                 series_type TEXT,
# # #                 start_date TIMESTAMP,
# # #                 end_date TIMESTAMP,
# # #                 host_country TEXT,
# # #                 total_matches INTEGER DEFAULT 0,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# # #             )
# # #             """
# # #         )

# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS innings (
# # #                 innings_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 match_id INTEGER NOT NULL,
# # #                 batting_team TEXT NOT NULL,
# # #                 bowling_team TEXT NOT NULL,
# # #                 total_runs INTEGER,
# # #                 total_wickets INTEGER,
# # #                 total_overs FLOAT,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# # #                 FOREIGN KEY (match_id) REFERENCES matches(match_id)
# # #             )
# # #             """
# # #         )

# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS batsmen (
# # #                 batsman_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 innings_id INTEGER NOT NULL,
# # #                 player_id INTEGER NOT NULL,
# # #                 batting_position INTEGER,
# # #                 runs_scored INTEGER,
# # #                 balls_faced INTEGER,
# # #                 fours INTEGER,
# # #                 sixes INTEGER,
# # #                 strike_rate FLOAT,
# # #                 dismissal_type TEXT,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# # #                 FOREIGN KEY (innings_id) REFERENCES innings(innings_id),
# # #                 FOREIGN KEY (player_id) REFERENCES players(player_id)
# # #             )
# # #             """
# # #         )

# # #         cursor.execute(
# # #             """
# # #             CREATE TABLE IF NOT EXISTS bowlers (
# # #                 bowler_id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #                 innings_id INTEGER NOT NULL,
# # #                 player_id INTEGER NOT NULL,
# # #                 overs_bowled FLOAT,
# # #                 maidens INTEGER,
# # #                 runs_conceded INTEGER,
# # #                 wickets_taken INTEGER,
# # #                 economy_rate FLOAT,
# # #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
# # #                 FOREIGN KEY (innings_id) REFERENCES innings(innings_id),
# # #                 FOREIGN KEY (player_id) REFERENCES players(player_id)
# # #             )
# # #             """
# # #         )

# # #         self.connection.commit()  # type: ignore[attr-defined]

# # #     def insert_player(
# # #         self,
# # #         team_id: int,
# # #         player_name: str,
# # #         country: str,
# # #         role: str,
# # #         batting_style: str,
# # #         bowling_style: str,
# # #         meta: str = "",
# # #         date_of_birth: str | None = None,
# # #         external_player_id: str | None = None,
# # #     ) -> int:
# # #         """Insert a new player"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]
# # #         if getattr(self, "db_type", "sqlite") == "mysql":
# # #             placeholders = "%s, %s, %s, %s, %s, %s, %s, %s, %s"
# # #             sql = (
# # #                 """
# # #                 INSERT INTO players (team_id, player_name, country, role, batting_style, bowling_style, meta, date_of_birth, external_player_id)
# # #                 VALUES (""" + placeholders + ")"
# # #             )
# # #             params = (team_id, player_name, country, role, batting_style, bowling_style, meta, date_of_birth, external_player_id)
# # #         else:
# # #             placeholders = "?, ?, ?, ?, ?, ?, ?, ?, ?"
# # #             sql = (
# # #                 """
# # #                 INSERT INTO players (team_id, player_name, country, role, batting_style, bowling_style, meta, date_of_birth, external_player_id)
# # #                 VALUES (""" + placeholders + ")"
# # #             )
# # #             params = (team_id, player_name, country, role, batting_style, bowling_style, meta, date_of_birth, external_player_id)

# # #         cursor.execute(sql, params)
# # #         self.connection.commit()  # type: ignore[attr-defined]
# # #         return cursor.lastrowid or 0  # type: ignore[attr-defined]

# # #     def update_player(self, player_id: int, **kwargs: Any) -> None:
# # #         """Update player record"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]
# # #         allowed_fields = [
# # #             "player_name",
# # #             "country",
# # #             "role",
# # #             "batting_style",
# # #             "bowling_style",
# # #             "date_of_birth",
# # #             "external_player_id",
# # #             "total_runs",
# # #             "total_wickets",
# # #             "batting_average",
# # #             "bowling_average",
# # #         ]
# # #         updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
# # #         if updates:
# # #             if getattr(self, "db_type", "sqlite") == "mysql":
# # #                 ph = "%s"
# # #             else:
# # #                 ph = "?"

# # #             set_clause = ", ".join([f"{k} = {ph}" for k in updates.keys()])
# # #             values: list[Any] = list(updates.values()) + [player_id]  # type: ignore[assignment]
# # #             query = f"UPDATE players SET {set_clause} WHERE player_id = {ph}"
# # #             cursor.execute(query, tuple(values))
# # #             self.connection.commit()  # type: ignore[attr-defined]

# # #     def sync_players_from_match(self, match_data: dict[str, Any]) -> None:
# # #         """
# # #         Extract all player details from a match API response and insert/update them in the players table.
# # #         """
# # #         from typing import List, Dict, Any, cast

# # #         for team_key in ['team1', 'team2', 'teams']:
# # #             team = match_data.get(team_key)
# # #             if team is None:
# # #                 continue
# # #             if isinstance(team, dict):
# # #                 teams: List[Dict[str, Any]] = [cast(Dict[str, Any], team)]
# # #             elif isinstance(team, list):
# # #                 teams = [cast(Dict[str, Any], t) for t in team if isinstance(t, dict)]  # type: ignore
# # #             else:
# # #                 continue

# # #             for t in teams:  # type: ignore
# # #                 team_id = int(t.get('id', 0)) if 'id' in t else 0
# # #                 team_country = str(t.get('country', '') or '')  # fallback country
# # #                 players = t.get('player')
# # #                 if not isinstance(players, list):
# # #                     continue

# # #                 for p in players:  # type: ignore
# # #                     if not isinstance(p, dict):
# # #                         continue
# # #                     # Skip role header entries (e.g., 'BATSMEN', 'BOWLER', etc.)
# # #                     if 'id' not in p:
# # #                         continue

# # #                     player_name = str(p.get('name', '')).strip()  # type: ignore
# # #                     if not player_name:
# # #                         continue

# # #                     # Extract fields (try a few common keys)
# # #                     country = str(p.get('country') or p.get('nationality') or team_country or '')  # type: ignore
# # #                     batting_style = str(p.get('battingStyle', '') or p.get('batting_style', ''))  # type: ignore
# # #                     bowling_style = str(p.get('bowlingStyle', '') or p.get('bowling_style', '')) # type: ignore
# # #                     date_of_birth = str(p.get('dateOfBirth') or p.get('dob') or p.get('date_of_birth') or '') # type: ignore
# # #                     external_id = str(p.get('id') or p.get('player_id') or p.get('external_id') or '') # type: ignore

# # #                     # Role: explicit then infer from styles
# # #                     role = str(p.get('role') or p.get('playingRole') or p.get('position') or '').strip()    # type: ignore
# # #                     if not role:
# # #                         has_bat = bool(batting_style)
# # #                         has_bowl = bool(bowling_style)
# # #                         if has_bat and has_bowl:
# # #                             role = 'all-rounder'
# # #                         elif has_bat:
# # #                             role = 'batter'
# # #                         elif has_bowl:
# # #                             role = 'bowler'
# # #                         else:
# # #                             role = ''

# # #                     # Prefer matching by external id (more stable), else normalized name
# # #                     existing = pd.DataFrame()
# # #                     try:
# # #                         if external_id:
# # #                             if getattr(self, "db_type", "sqlite") == "mysql":
# # #                                 # basic quoting to avoid syntax break (internal use)
# # #                                 safe = external_id.replace("'", "''")
# # #                                 q = f"SELECT player_id FROM players WHERE external_player_id = '{safe}'"
# # #                                 existing = self.execute_query(q)
# # #                             else:
# # #                                 q = "SELECT player_id FROM players WHERE external_player_id = ?"
# # #                                 existing = self.execute_query(q, (external_id,))
# # #                         if existing.empty:
# # #                             # normalized name match (case/whitespace tolerant)
# # #                             if getattr(self, "db_type", "sqlite") == "mysql":
# # #                                 safe_name = player_name.replace("'", "''")
# # #                                 q = f"SELECT player_id FROM players WHERE lower(trim(player_name)) = lower(trim('{safe_name}'))"
# # #                                 existing = self.execute_query(q)
# # #                             else:
# # #                                 q = "SELECT player_id FROM players WHERE lower(trim(player_name)) = lower(trim(?))"
# # #                                 existing = self.execute_query(q, (player_name,))
# # #                     except Exception:
# # #                         existing = pd.DataFrame()

# # #                     if not existing.empty:
# # #                         pid_value = existing.iloc[0]['player_id']  # type: ignore[index]
# # #                         player_id_val: int = int(pid_value) if pid_value is not None else 0
# # #                         self.update_player(
# # #                             player_id_val,
# # #                             country=str(country),
# # #                             role=str(role),
# # #                             batting_style=str(batting_style),
# # #                             bowling_style=str(bowling_style),
# # #                             date_of_birth=date_of_birth,
# # #                             external_player_id=external_id,
# # #                         )
# # #                     else:
# # #                         # insert (note insert_player supports dob/external_id)
# # #                         self.insert_player(
# # #                             team_id,
# # #                             player_name,
# # #                             country,
# # #                             role,
# # #                             batting_style,
# # #                             bowling_style,
# # #                             meta='',
# # #                             date_of_birth=date_of_birth,
# # #                             external_player_id=external_id,
# # #                         )

# # #     def delete_player(self, player_id: int) -> None:
# # #         """Delete a player"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]
# # #         cursor.execute("DELETE FROM players WHERE player_id = ?", (player_id,))  # type: ignore[attr-defined]
# # #         self.connection.commit()  # type: ignore[attr-defined]

# # #     def get_players(self) -> pd.DataFrame:
# # #         """Fetch all players"""
# # #         # Return results with a leading serial column `s_no` so the UI shows a 1-based index
# # #         query = "SELECT * FROM players ORDER BY player_id ASC"
# # #         df = pd.read_sql(query, self.connection)  # type: ignore[call-arg]

# # #         # Ensure expected columns exist even on older schemas
# # #         expected_cols = [
# # #             "team_id",
# # #             "external_player_id",
# # #             "player_id",
# # #             "player_name",
# # #             "date_of_birth",
# # #             "country",
# # #             "role",
# # #             "batting_style",
# # #             "bowling_style",
# # #             "meta",
# # #             "created_at",
# # #         ]
# # #         for c in expected_cols:
# # #             if c not in df.columns:
# # #                 df[c] = pd.NA

# # #         # Reorder to preferred canonical order (keep any extra columns afterwards)
# # #         cols_order = [c for c in expected_cols if c in df.columns] + [c for c in df.columns if c not in expected_cols]
# # #         df = df[cols_order]

# # #         # Add s_no (1-based index)
# # #         try:
# # #             df.insert(0, "s_no", range(1, len(df) + 1))
# # #         except Exception:
# # #             df["s_no"] = range(1, len(df) + 1)
# # #             cols = df.columns.tolist()
# # #             if cols[-1] == "s_no":
# # #                 df = df[["s_no"] + [c for c in cols if c != "s_no"]]
# # #         return df

# # #     def get_player_by_id(self, player_id: int) -> Dict[str, Any] | None:
# # #         """Get a specific player"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]
# # #         cursor.execute("SELECT * FROM players WHERE player_id = ?", (player_id,))  # type: ignore[attr-defined]
# # #         row = cursor.fetchone()  # type: ignore[attr-defined]
# # #         return dict(row) if row else None

# # #     def insert_match(
# # #         self,
# # #         match_description: str,
# # #         team1: str,
# # #         team2: str,
# # #         match_format: str,
# # #         venue_id: int,
# # #         match_date: str,
# # #     ) -> int:
# # #         """Insert a new match"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]
# # #         cursor.execute(
# # #             """
# # #             INSERT INTO matches 
# # #             (match_description, team1, team2, match_format, venue_id, match_date)
# # #             VALUES (?, ?, ?, ?, ?, ?)
# # #             """,
# # #             (match_description, team1, team2, match_format, venue_id, match_date),
# # #         )
# # #         self.connection.commit()  # type: ignore[attr-defined]
# # #         return cursor.lastrowid or 0  # type: ignore[attr-defined]

# # #     def get_matches(self) -> pd.DataFrame:
# # #         """Fetch all matches"""
# # #         query = """
# # #         SELECT m.*, v.venue_name, v.city, v.country 
# # #         FROM matches m 
# # #         LEFT JOIN venues v ON m.venue_id = v.venue_id
# # #         ORDER BY m.match_date DESC
# # #         """
# # #         return pd.read_sql(query, self.connection)  # type: ignore[call-arg]

# # #     def insert_venue(
# # #         self, venue_name: str, city: str, country: str, capacity: int
# # #     ) -> int:
# # #         """Insert a new venue"""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]
# # #         cursor.execute(
# # #             """
# # #             INSERT INTO venues (venue_name, city, country, capacity)
# # #             VALUES (?, ?, ?, ?)
# # #             """,
# # #             (venue_name, city, country, capacity),
# # #         )
# # #         self.connection.commit()  # type: ignore[attr-defined]
# # #         return cursor.lastrowid or 0  # type: ignore[attr-defined]

# # #     def get_venues(self) -> pd.DataFrame:
# # #         """Fetch all venues"""
# # #         query = "SELECT * FROM venues ORDER BY capacity DESC"
# # #         return pd.read_sql(query, self.connection)  # type: ignore[call-arg]

# # #     def get_teams(self) -> pd.DataFrame:
# # #         """Fetch all teams"""
# # #         query = "SELECT team_id, team_name, team_short_name, team_flag, created_at FROM teams ORDER BY team_name"
# # #         return pd.read_sql(query, self.connection)  # type: ignore[call-arg]

# # #     def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> pd.DataFrame:
# # #         """Execute a custom SQL query and return results as DataFrame"""
# # #         try:
# # #             if params:
# # #                 return pd.read_sql(query, self.connection, params=params)  # type: ignore[call-arg]
# # #             return pd.read_sql(query, self.connection)  # type: ignore[call-arg]
# # #         except Exception as e:
# # #             st.error(f"Query execution error: {e}")
# # #             return pd.DataFrame()

# # #     def close(self) -> None:
# # #         """Close database connection"""
# # #         if self.connection:
# # #             self.connection.close()


# # # # Top-level MySQL-backed connection that implements same interface as DatabaseConnection
# # # class MySQLDatabaseConnection(DatabaseConnection):
# # #     def __init__(self, secrets: Dict[str, Any]):
# # #         # Do not call super() init to avoid sqlite setup
# # #         self.db_type = "mysql"
# # #         self.db_path = "mysql"
# # #         self.secrets = secrets
# # #         # mypy/pylance: secrets values are dynamic; cast to known types
# # #         host = cast(str, secrets.get("host", "localhost"))
# # #         user = cast(str, secrets.get("user"))
# # #         password = cast(str, secrets.get("password"))
# # #         database = cast(str, secrets.get("dbname") or secrets.get("database"))
# # #         try:
# # #             port = int(secrets.get("port", 3306))
# # #         except Exception:
# # #             port = 3306

# # #         # Use SQLAlchemy engine for proper pandas.read_sql() support (if available)
# # #         try:
# # #             if sqlalchemy:
# # #                 # Properly escape special characters in password
# # #                 from urllib.parse import quote_plus
# # #                 escaped_password = quote_plus(password)
# # #                 connection_string = f"mysql+pymysql://{user}:{escaped_password}@{host}:{port}/{database}?charset=utf8mb4"
# # #                 self.connection = create_engine(connection_string)  # type: ignore[attr-defined]
# # #             else:
# # #                 # Fallback to raw pymysql if SQLAlchemy not available
# # #                 assert pymysql is not None
# # #                 self.connection = pymysql.connect(
# # #                     host=host,
# # #                     user=user,
# # #                     password=password,
# # #                     database=database,
# # #                     port=port,
# # #                     charset="utf8mb4",
# # #                     cursorclass=pymysql.cursors.DictCursor,
# # #                 )
# # #         except Exception:
# # #             # Fallback to raw pymysql if anything fails
# # #             assert pymysql is not None
# # #             self.connection = pymysql.connect(
# # #                 host=host,
# # #                 user=user,
# # #                 password=password,
# # #                 database=database,
# # #                 port=port,
# # #                 charset="utf8mb4",
# # #                 cursorclass=pymysql.cursors.DictCursor,
# # #             )

# # #     def init_schema(self) -> None:  # type: ignore[override]
# # #         # Use the mysql_sync helper if available to create tables for MySQL
# # #         if create_mysql_schema is not None:
# # #             try:
# # #                 create_mysql_schema(self.secrets)
# # #             except Exception:
# # #                 # If table creation fails, continue — individual operations will report errors
# # #                 pass

# # #     def get_players(self) -> pd.DataFrame:  # type: ignore[override]
# # #         try:
# # #             query = "SELECT * FROM players ORDER BY total_runs DESC, player_id ASC"
# # #             df = pd.read_sql(query, self.connection)  # type: ignore[call-arg]

# # #             expected_cols = [
# # #                 "team_id",
# # #                 "external_player_id",
# # #                 "player_id",
# # #                 "player_name",
# # #                 "date_of_birth",
# # #                 "country",
# # #                 "role",
# # #                 "batting_style",
# # #                 "bowling_style",
# # #                 "meta",
# # #                 "created_at",
# # #             ]
# # #             for c in expected_cols:
# # #                 if c not in df.columns:
# # #                     df[c] = pd.NA

# # #             cols_order = [c for c in expected_cols if c in df.columns] + [c for c in df.columns if c not in expected_cols]
# # #             df = df[cols_order]

# # #             try:
# # #                 df.insert(0, "s_no", range(1, len(df) + 1))
# # #             except Exception:
# # #                 df["s_no"] = range(1, len(df) + 1)
# # #             return df
# # #         except Exception:
# # #             return pd.DataFrame()

# # #     def insert_player(self, player_name: str, country: str, role: str, batting_style: str, bowling_style: str) -> int:  # type: ignore[override]
# # #         """Insert player using MySQL-backed connection (handles SQLAlchemy engine or raw pymysql)."""
# # #         # Raw pymysql connection path
# # #         if hasattr(self.connection, 'cursor') and not hasattr(self.connection, 'engine'):
# # #             cur = self.connection.cursor()  # type: ignore[attr-defined]
# # #             # Inspect players table columns to handle schema differences
# # #             try:
# # #                 cur.execute("SHOW COLUMNS FROM players")
# # #                 # fetchall() may return a sequence of dicts (DictCursor) or
# # #                 # sequences/tuples (regular cursor). Provide precise local
# # #                 # typing so static checkers understand the types here.
# # #                 raw_cols = cast(Sequence[Any] | None, cur.fetchall())
# # #                 # normalize to a sequence so static type-checkers can reason about it
# # #                 cols_info: Sequence[Any] = list(raw_cols) if raw_cols else []
# # #                 # rows may be tuple or dict depending on cursorclass
# # #                 cols: set[str] = set()
# # #                 for r in cols_info:
# # #                     try:
# # #                         # r can be a dict-like mapping or a sequence/tuple
# # #                         if isinstance(r, dict):
# # #                             r_map = cast(Mapping[str, Any], r)
# # #                             # try common field name keys returned by different cursor types
# # #                             for key in ("Field", "field", "COLUMN_NAME", "column_name", "Column_name"):
# # #                                 if key in r_map and r_map[key] is not None:
# # #                                     cols.add(str(r_map[key]))
# # #                                     break
# # #                             else:
# # #                                 # fallback to first non-None value in the dict
# # #                                 for v in r_map.values():
# # #                                     if v is not None:
# # #                                         cols.add(str(v))
# # #                                         break
# # #                         else:
# # #                             # tuple/list response: first element is typically the column name
# # #                             seq = cast(Sequence[Any], r)
# # #                             if len(seq) > 0:
# # #                                 cols.add(str(seq[0]))
# # #                     except Exception:
# # #                         # ignore malformed rows
# # #                         continue
# # #             except Exception:
# # #                 cols = set()

# # #             insert_cols = []
# # #             params = []

# # #             if 'player_name' in cols or not cols:
# # #                 insert_cols.append('player_name')
# # #                 params.append(player_name)
# # #             if 'country' in cols or not cols:
# # #                 insert_cols.append('country')
# # #                 params.append(country)
# # #             if 'role' in cols or not cols:
# # #                 insert_cols.append('role')
# # #                 params.append(role)
# # #             # If table has explicit batting/bowling style columns, insert them
# # #             if 'batting_style' in cols:
# # #                 insert_cols.append('batting_style')
# # #                 params.append(batting_style)
# # #             if 'bowling_style' in cols:
# # #                 insert_cols.append('bowling_style')
# # #                 params.append(bowling_style)

# # #             # If there's a `meta` JSON column, store styles there as fallback
# # #             if 'meta' in cols and ('batting_style' not in cols and 'bowling_style' not in cols):
# # #                 insert_cols.append('meta')
# # #                 try:
# # #                     params.append(json.dumps({'batting_style': batting_style, 'bowling_style': bowling_style}))
# # #                 except Exception:
# # #                     params.append('{}')

# # #             if not insert_cols:
# # #                 # fallback to basic insert
# # #                 insert_cols = ['player_name', 'country', 'role']
# # #                 params = [player_name, country, role]

# # #             placeholders = ', '.join(['%s'] * len(insert_cols))
# # #             cols_sql = ', '.join(insert_cols)
# # #             sql = f"INSERT INTO players ({cols_sql}) VALUES ({placeholders})"

# # #             # Debug: print SQL and params before executing
# # #             try:
# # #                 print('[db.mysql] raw pymysql path: executing SQL:', sql)
# # #                 print('[db.mysql] params:', tuple(params))
# # #                 print('[db.mysql] param types:', tuple(type(p) for p in params))
# # #             except Exception:
# # #                 pass

# # #             cur.execute(sql, tuple(params))
# # #             try:
# # #                 self.connection.commit()  # type: ignore[attr-defined]
# # #             except Exception:
# # #                 pass
# # #             try:
# # #                 return int(cur.lastrowid)  # type: ignore[attr-defined]
# # #             except Exception:
# # #                 return 0

# # #         # SQLAlchemy engine path
# # #         try:
# # #             # type: ignore[reportMissingImports]
# # #             from sqlalchemy import text
# # #         except Exception:
# # #             text = None  # type: ignore

# # #         if text is not None:
# # #             stmt = text(
# # #                 "INSERT INTO players (player_name, country, role, batting_style, bowling_style)"
# # #                 " VALUES (:player_name, :country, :role, :batting_style, :bowling_style)"
# # #             )
# # #             params = {
# # #                 "player_name": player_name,
# # #                 "country": country,
# # #                 "role": role,
# # #                 "batting_style": batting_style,
# # #                 "bowling_style": bowling_style,
# # #             }
# # #             try:
# # #                 with self.connection.begin() as conn:  # type: ignore[attr-defined]
# # #                     conn.execute(stmt, params)
# # #                     # MySQL: fetch last insert id
# # #                     res = conn.execute(text("SELECT LAST_INSERT_ID() as id"))
# # #                     row = res.fetchone()
# # #                     if row:
# # #                         return int(row[0] if len(row) > 0 else row["id"])  # type: ignore[index]
# # #             except Exception:
# # #                 pass

# # #         # Fallback: unable to determine ID
# # #         return 0

# # #     def get_matches(self) -> pd.DataFrame:  # type: ignore[override]
# # #         try:
# # #             query = "SELECT * FROM matches ORDER BY start_date DESC"
# # #             return pd.read_sql(query, self.connection)  # type: ignore[call-arg]
# # #         except Exception:
# # #             return pd.DataFrame()

# # #     def execute_query(self, query: str, params: tuple[Any, ...] | None = None) -> pd.DataFrame:  # type: ignore[override]
# # #         try:
# # #             # Check if it's a raw pymysql connection (has cursor method)
# # #             if hasattr(self.connection, 'cursor') and not hasattr(self.connection, 'engine'):
# # #                 return fetch_data_from_pymysql(query, self.connection)
# # #             else:
# # #                 # SQLAlchemy engine
# # #                 if params:
# # #                     return pd.read_sql(query, self.connection, params=params)  # type: ignore[call-arg]
# # #                 return pd.read_sql(query, self.connection)  # type: ignore[call-arg]
# # #         except Exception as e:
# # #             try:
# # #                 st.error(f"MySQL query error: {e}")
# # #             except Exception:
# # #                 pass
# # #             return pd.DataFrame()

# # #     def insert_or_update_series(
# # #         self,
# # #         series_id: int | None,
# # #         series_name: str,
# # #         series_short_name: str | None = None,
# # #         series_type: str | None = None,
# # #         start_date: str | None = None,
# # #         end_date: str | None = None,
# # #         host_country: str | None = None,
# # #         total_matches: int = 0,
# # #     ) -> int:
# # #         """Insert a new series or update existing one (by id or name). Returns series_id."""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]

# # #         # Update by provided id
# # #         if series_id:
# # #             cursor.execute(
# # #                 """
# # #                 UPDATE series
# # #                 SET series_name = ?, series_short_name = ?, series_type = ?, start_date = ?, end_date = ?, host_country = ?, total_matches = ?
# # #                 WHERE series_id = ?
# # #                 """,
# # #                 (series_name, series_short_name, series_type, start_date, end_date, host_country, total_matches, series_id),
# # #             )
# # #             self.connection.commit()  # type: ignore[attr-defined]
# # #             return int(series_id)

# # #         # Try find by name and update
# # #         cursor.execute("SELECT series_id FROM series WHERE series_name = ?", (series_name,))  # type: ignore[attr-defined]
# # #         row = cursor.fetchone()  # type: ignore[attr-defined]
# # #         if row:
# # #             sid = int(row["series_id"]) # type: ignore[index]
# # #             cursor.execute(
# # #                 """
# # #                 UPDATE series
# # #                 SET series_short_name = ?, series_type = ?, start_date = ?, end_date = ?, host_country = ?, total_matches = ?
# # #                 WHERE series_id = ?
# # #                 """,
# # #                 (series_short_name, series_type, start_date, end_date, host_country, total_matches, sid),
# # #             )
# # #             self.connection.commit()  # type: ignore[attr-defined]
# # #             return sid

# # #         # Insert new series
# # #         cursor.execute(
# # #             """
# # #             INSERT INTO series (series_name, series_short_name, series_type, start_date, end_date, host_country, total_matches)
# # #             VALUES (?, ?, ?, ?, ?, ?, ?)
# # #             """,
# # #             (series_name, series_short_name, series_type, start_date, end_date, host_country, total_matches),
# # #         )
# # #         self.connection.commit()  # type: ignore[attr-defined]
# # #         return int(cursor.lastrowid or 0)  # type: ignore[attr-defined]

# # #     def insert_or_update_team(
# # #         self,
# # #         team_id: int | None,
# # #         team_name: str,
# # #         team_short_name: str | None = None,
# # #         team_flag: str | None = None,
# # #     ) -> int:
# # #         """Insert a new team or update existing one (by id or name). Returns team_id."""
# # #         cursor = self.connection.cursor()  # type: ignore[attr-defined]

# # #         # Update by provided team_id
# # #         if team_id:
# # #             cursor.execute(
# # #                 """
# # #                 INSERT OR REPLACE INTO teams (team_id, team_name, team_short_name, team_flag, created_at)
# # #                 VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM teams WHERE team_id = ?), CURRENT_TIMESTAMP))
# # #                 """,
# # #                 (team_id, team_name, team_short_name, team_flag, team_id),
# # #             )
# # #             self.connection.commit()  # type: ignore[attr-defined]
# # #             return int(team_id)

# # #         # Try find by name and update
# # #         cursor.execute("SELECT team_id FROM teams WHERE team_name = ?", (team_name,))  # type: ignore[attr-defined]
# # #         row = cursor.fetchone()  # type: ignore[attr-defined]
# # #         if row:
# # #             tid = int(row["team_id"])  # type: ignore[index]
# # #             cursor.execute(
# # #                 """
# # #                 UPDATE teams
# # #                 SET team_short_name = ?, team_flag = ?
# # #                 WHERE team_id = ?
# # #                 """,
# # #                 (team_short_name, team_flag, tid),
# # #             )
# # #             self.connection.commit()  # type: ignore[attr-defined]
# # #             return tid

# # #         # Insert new team (let caller supply numeric team_id or let DB assign)
# # #         # If team_id is not provided, attempt to insert without it (auto assigned)
# # #         if team_id is None:
# # #             cursor.execute(
# # #                 """
# # #                 INSERT INTO teams (team_name, team_short_name, team_flag)
# # #                 VALUES (?, ?, ?)
# # #                 """,
# # #                 (team_name, team_short_name, team_flag),
# # #             )
# # #             self.connection.commit()  # type: ignore[attr-defined]
# # #             return int(cursor.lastrowid or 0)  # type: ignore[attr-defined]

# # #         return int(team_id)


# # # def get_db_connection(secrets: Dict[str, Any] | None = None) -> "DatabaseConnection":
# # #     """
# # #     Return a database connection instance.

# # #     - If `secrets` contains keys commonly used for MySQL (host/user/password/database/dbname)
# # #       or the environment variable `DB_TYPE` is set to "mysql", attempt to return a
# # #       `MySQLDatabaseConnection(secrets)`.
# # #     - On failure or when no MySQL indicators are present, return a local `DatabaseConnection()` (SQLite).
# # #     """
# # #     secrets = secrets or {}
# # #     try:
# # #         import os

# # #         db_type = str(secrets.get("db_type") or os.environ.get("DB_TYPE") or "").lower()
# # #     except Exception:
# # #         db_type = ""

# # #     # Heuristic: secrets provided or explicit DB_TYPE
# # #     if db_type == "mysql" or any(k in secrets for k in ("host", "user", "password", "database", "dbname")):
# # #         try:
# # #             return MySQLDatabaseConnection(secrets)
# # #         except Exception as e:  # pragma: no cover - fallback behavior
# # #             try:
# # #                 st.warning(f"MySQL connection failed ({e}); falling back to sqlite.")
# # #             except Exception:
# # #                 pass
# # #             return DatabaseConnection()

# # #     # Default: local sqlite connection
# # #     return DatabaseConnection()



# # """
# # Database Connection and Schema Management
# # Supports SQLite (default) and MySQL
# # """

# # # pyright: reportUnknownMemberType=false

# # import sqlite3
# # import json
# # from typing import Dict, Any, Optional, Tuple, cast

# # import pandas as pd
# # import streamlit as st

# # st = cast(Any, st)

# # # -------------------------------------------------
# # # Optional MySQL / SQLAlchemy imports
# # # -------------------------------------------------
# # try:
# #     import pymysql  # type: ignore
# # except Exception:
# #     pymysql = None  # type: ignore

# # try:
# #     from sqlalchemy import create_engine, text  # type: ignore
# #     SQLALCHEMY_AVAILABLE = True
# # except Exception:
# #     create_engine = None  # type: ignore
# #     text = None  # type: ignore
# #     SQLALCHEMY_AVAILABLE = False


# # # =================================================
# # # Base SQLite Connection
# # # =================================================
# # class DatabaseConnection:
# #     def __init__(self, db_path: str = "cricbuzzdb.db"):
# #         self.db_type = "sqlite"
# #         self.connection = sqlite3.connect(db_path, check_same_thread=False)
# #         self.connection.row_factory = sqlite3.Row

# #     # -------------------------------------------------
# #     # SCHEMA (ALL TABLES)
# #     # -------------------------------------------------
# #     def init_schema(self) -> None:
# #         cur = self.connection.cursor()
# #         cur.executescript(
# #             """
# #             CREATE TABLE IF NOT EXISTS series (
# #                 series_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_series_id TEXT UNIQUE,
# #                 series_name TEXT NOT NULL,
# #                 series_short_name TEXT,
# #                 series_type TEXT,
# #                 start_date TEXT,
# #                 end_date TEXT,
# #                 host_country TEXT,
# #                 total_matches INTEGER DEFAULT 0,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS teams (
# #                 team_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_team_id TEXT UNIQUE,
# #                 team_name TEXT NOT NULL,
# #                 team_short_name TEXT,
# #                 team_flag TEXT,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS venues (
# #                 venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_venue_id TEXT UNIQUE,
# #                 venue_name TEXT NOT NULL,
# #                 city TEXT,
# #                 country TEXT,
# #                 capacity INTEGER,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS matches (
# #                 match_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_match_id TEXT UNIQUE,
# #                 series_id TEXT,
# #                 series_name TEXT,
# #                 match_desc TEXT,
# #                 match_format TEXT,
# #                 start_date TEXT,
# #                 end_date TEXT,
# #                 state TEXT,
# #                 status TEXT,
# #                 team1 TEXT,
# #                 team2 TEXT,
# #                 team1_id TEXT,
# #                 team2_id TEXT,
# #                 venue TEXT,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS players (
# #                 player_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_player_id TEXT UNIQUE,
# #                 player_name TEXT NOT NULL,
# #                 date_of_birth TEXT,
# #                 country TEXT,
# #                 role TEXT,
# #                 batting_style TEXT,
# #                 bowling_style TEXT,
# #                 meta TEXT,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS innings (
# #                 innings_pk INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_match_id TEXT,
# #                 innings_id TEXT,
# #                 batting_team TEXT,
# #                 bowling_team TEXT,
# #                 runs INTEGER,
# #                 wickets INTEGER,
# #                 overs REAL,
# #                 extras TEXT,
# #                 meta TEXT,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS batsmen (
# #                 batsman_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_match_id TEXT,
# #                 innings_id TEXT,
# #                 player_name TEXT,
# #                 runs INTEGER,
# #                 balls INTEGER,
# #                 fours INTEGER,
# #                 sixes INTEGER,
# #                 strike_rate REAL,
# #                 dismissal TEXT,
# #                 meta TEXT,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );

# #             CREATE TABLE IF NOT EXISTS bowlers (
# #                 bowler_id INTEGER PRIMARY KEY AUTOINCREMENT,
# #                 external_match_id TEXT,
# #                 innings_id TEXT,
# #                 player_name TEXT,
# #                 overs REAL,
# #                 maidens INTEGER,
# #                 runs_conceded INTEGER,
# #                 wickets INTEGER,
# #                 economy REAL,
# #                 meta TEXT,
# #                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# #             );
# #             """
# #         )
# #         self.connection.commit()

# #     # -------------------------------------------------
# #     # SQLite UPSERT / INSERT HELPERS
# #     # -------------------------------------------------
# #     def upsert_series(self, ext_id: str, name: str) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO series (external_series_id, series_name)
# #             VALUES (?, ?)
# #             ON CONFLICT(external_series_id)
# #             DO UPDATE SET series_name = excluded.series_name
# #             """,
# #             (ext_id, name),
# #         )
# #         self.connection.commit()

# #     def upsert_team(self, ext_id: str, name: str) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO teams (external_team_id, team_name)
# #             VALUES (?, ?)
# #             ON CONFLICT(external_team_id)
# #             DO UPDATE SET team_name = excluded.team_name
# #             """,
# #             (ext_id, name),
# #         )
# #         self.connection.commit()

# #     def upsert_venue(self, ext_id: str, name: str, city: str, country: str) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO venues (external_venue_id, venue_name, city, country)
# #             VALUES (?, ?, ?, ?)
# #             ON CONFLICT(external_venue_id)
# #             DO UPDATE SET venue_name = excluded.venue_name
# #             """,
# #             (ext_id, name, city, country),
# #         )
# #         self.connection.commit()

# #     def upsert_match(self, ext_id: str, series: str, team1: str, team2: str) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO matches (external_match_id, series_name, team1, team2)
# #             VALUES (?, ?, ?, ?)
# #             ON CONFLICT(external_match_id)
# #             DO UPDATE SET team1 = excluded.team1, team2 = excluded.team2
# #             """,
# #             (ext_id, series, team1, team2),
# #         )
# #         self.connection.commit()

# #     def insert_player(self, name: str, role: str, country: str) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT OR IGNORE INTO players (player_name, role, country)
# #             VALUES (?, ?, ?)
# #             """,
# #             (name, role, country),
# #         )
# #         self.connection.commit()

# #     def insert_innings(self, match_id: str, innings_id: str, batting: str, bowling: str) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO innings (external_match_id, innings_id, batting_team, bowling_team)
# #             VALUES (?, ?, ?, ?)
# #             """,
# #             (match_id, innings_id, batting, bowling),
# #         )
# #         self.connection.commit()

# #     def insert_batsman(self, match_id: str, innings_id: str, name: str, runs: int) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO batsmen (external_match_id, innings_id, player_name, runs)
# #             VALUES (?, ?, ?, ?)
# #             """,
# #             (match_id, innings_id, name, runs),
# #         )
# #         self.connection.commit()

# #     def insert_bowler(self, match_id: str, innings_id: str, name: str, wickets: int) -> None:
# #         self.connection.execute(
# #             """
# #             INSERT INTO bowlers (external_match_id, innings_id, player_name, wickets)
# #             VALUES (?, ?, ?, ?)
# #             """,
# #             (match_id, innings_id, name, wickets),
# #         )
# #         self.connection.commit()

# #     def close(self) -> None:
# #         self.connection.close()


# # # =================================================
# # # MySQL Connection (FULLY IMPLEMENTED)
# # # =================================================
# # class MySQLDatabaseConnection(DatabaseConnection):
# #     def __init__(self, secrets: Dict[str, Any]):
# #         self.db_type = "mysql"
# #         self.secrets = secrets

# #         host = secrets.get("host", "localhost")
# #         user = secrets.get("user")
# #         password = secrets.get("password")
# #         database = secrets.get("database") or secrets.get("dbname")
# #         port = int(secrets.get("port", 3306))

# #         if SQLALCHEMY_AVAILABLE:
# #             from urllib.parse import quote_plus
# #             pwd = quote_plus(password)
# #             uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{database}?charset=utf8mb4"
# #             self.connection = create_engine(uri)
# #         else:
# #             if pymysql is None:
# #                 raise RuntimeError("PyMySQL not available")
# #             self.connection = pymysql.connect(
# #                 host=host,
# #                 user=user,
# #                 password=password,
# #                 database=database,
# #                 port=port,
# #                 charset="utf8mb4",
# #                 cursorclass=pymysql.cursors.DictCursor,
# #             )

# #     def init_schema(self) -> None:
# #         # MySQL schema should be created via mysql_sync.py
# #         from utils.mysql_sync import create_mysql_schema  # type: ignore
# #         create_mysql_schema(self.secrets)


# # # =================================================
# # # FACTORY
# # # =================================================
# # def get_db_connection(secrets: Optional[Dict[str, Any]] = None) -> DatabaseConnection:
# #     secrets = secrets or {}

# #     if any(k in secrets for k in ("host", "user", "password", "database", "dbname")):
# #         try:
# #             return MySQLDatabaseConnection(secrets)
# #         except Exception as e:
# #             st.warning(f"MySQL connection failed, falling back to SQLite: {e}")

# #     return DatabaseConnection()


# """
# Database Connection Layer
# Delegates ALL schema + insert logic to mysql_sync.py

# This file is intentionally THIN.
# """

# from typing import Any, Dict, Optional, List, Tuple, cast
# import sqlite3
# import pandas as pd
# import streamlit as st

# st = cast(Any, st)

# # mysql_sync helpers (SOURCE OF TRUTH)
# from utils.mysql_sync import (
#     create_mysql_schema,
#     upsert_series,
#     upsert_team,
#     upsert_match,
#     upsert_batting,
#     upsert_bowling,
# )

# # Optional MySQL support
# pymysql = None
# create_engine = None

# try:
#     import pymysql  # type: ignore
# except Exception:
#     pymysql = None

# try:
#     from sqlalchemy import create_engine  # type: ignore
# except Exception:
#     create_engine = None


# # =====================================================
# # SQLite (local / UI / read-only analytics)
# # =====================================================
# class DatabaseConnection:
#     def __init__(self, db_path: str = "cricbuzz.db"):
#         self.db_type = "sqlite"
#         self.connection = sqlite3.connect(db_path, check_same_thread=False)
#         self.connection.row_factory = sqlite3.Row

#     # ---------------- READ HELPERS ----------------
#     def fetch_df(self, sql: str, params: Tuple[Any, ...] = ()) -> pd.DataFrame:
#         return pd.read_sql(sql, self.connection, params=params)

#     def get_series(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM series ORDER BY created_at DESC")

#     def get_teams(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM teams ORDER BY team_name")

#     def get_players(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM players ORDER BY player_name")

#     def get_matches(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM matches ORDER BY start_date DESC")

#     def get_venues(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM venues ORDER BY venue_name")

#     def get_batting_stats(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM batting_stats")

#     def get_bowling_stats(self) -> pd.DataFrame:
#         return self.fetch_df("SELECT * FROM bowling_stats")

#     def close(self) -> None:
#         self.connection.close()


# # =====================================================
# # MySQL (production / full write support)
# # =====================================================
# class MySQLDatabaseConnection(DatabaseConnection):
#     def __init__(self, secrets: Dict[str, Any]):
#         self.db_type = "mysql"
#         self.secrets = secrets

#         host = secrets.get("host", "localhost")
#         user = secrets.get("user")
#         password = secrets.get("password")
#         database = secrets.get("database") or secrets.get("dbname")
#         port = int(secrets.get("port", 3306))

#         if create_engine:
#             from urllib.parse import quote_plus
#             pwd = quote_plus(password)
#             uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{database}?charset=utf8mb4"
#             self.connection = create_engine(uri)
#         else:
#             assert pymysql is not None
#             self.connection = pymysql.connect(
#                 host=host,
#                 user=user,
#                 password=password,
#                 database=database,
#                 port=port,
#                 charset="utf8mb4",
#                 cursorclass=pymysql.cursors.DictCursor,
#             )

#     # ---------------- SCHEMA ----------------
#     def init_schema(self) -> None:
#         create_mysql_schema(self.secrets)

#     # ---------------- WRITE DELEGATION ----------------
#     def save_match(self, match: Dict[str, Any]) -> None:
#         upsert_match(self.secrets, match)

#     def save_batting(self, match_id: str, innings_id: str, rows: List[Dict[str, Any]]) -> None:
#         upsert_batting(self.secrets, match_id, innings_id, rows)

#     def save_bowling(self, match_id: str, innings_id: str, rows: List[Dict[str, Any]]) -> None:
#         upsert_bowling(self.secrets, match_id, innings_id, rows)


# # =====================================================
# # Factory
# # =====================================================
# def get_db_connection(secrets: Optional[Dict[str, Any]] = None) -> DatabaseConnection:
#     if secrets and any(k in secrets for k in ("host", "user", "password", "database", "dbname")):
#         return MySQLDatabaseConnection(secrets)
#     return DatabaseConnection()


"""
Database Connection Layer (UI / Read Layer)

Used ONLY by Streamlit UI pages.
- No CREATE TABLE
- No UPSERT / INSERT of API data
- Only READ + minimal safe execute
"""

from typing import Any, Dict, Optional, Tuple
import sqlite3
import pandas as pd
import streamlit as st
from typing import cast

# Optional MySQL / SQLAlchemy
try:
    import pymysql  # type: ignore
except Exception:
    pymysql = None  # type: ignore

try:
    from sqlalchemy import create_engine, text  # type: ignore
except Exception:
    create_engine = None  # type: ignore
    text = None  # type: ignore

st = cast(Any, st)


# =====================================================
# Base SQLite connection
# =====================================================
class DatabaseConnection:
    """
    Base database connection for Streamlit UI (SQLite).
    """

    def __init__(self, db_path: str = "cricbuzz.db"):
        self.db_type = "sqlite"
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

    # ---------------------------
    # Core helpers
    # ---------------------------
    def read_df(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        try:
            if params:
                return pd.read_sql(query, self.connection, params=params)
            return pd.read_sql(query, self.connection)
        except Exception as e:
            st.error(f"SQLite read error: {e}")
            return pd.DataFrame()

    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        """Alias for read_df to support legacy code"""
        return self.read_df(query, params)

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        try:
            cur = self.connection.cursor()
            cur.execute(query, params or ())
            self.connection.commit()
        except Exception as e:
            st.error(f"SQLite execute error: {e}")

    def close(self) -> None:
        if self.connection:
            self.connection.close()

    # =================================================
    # READ HELPERS (ALL TABLES)
    # =================================================
    def get_series(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM series ORDER BY start_date DESC")

    def get_teams(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM teams ORDER BY team_name")

    def get_players(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM players ORDER BY player_name")

    def get_matches(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM matches ORDER BY start_date DESC")

    def get_innings(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM innings ORDER BY id")

    def get_batting_stats(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM batting_stats ORDER BY external_match_id")

    def get_bowling_stats(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM bowling_stats ORDER BY external_match_id")

    def get_venues(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM venues ORDER BY venue_name")

    def get_partnerships(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM partnerships ORDER BY external_match_id")

    # ---------------------------
    # CRUD Operations
    # ---------------------------
    def insert_player(self, player_name: str, country: str, role: str, batting_style: str = "N/A", bowling_style: str = "N/A", external_player_id: Optional[str] = None, date_of_birth: Optional[str] = None) -> int:
        """Insert a new player - Base class stub"""
        raise NotImplementedError("insert_player not supported for SQLite. Use MySQLDatabaseConnection.")

    def update_player(self, player_id: int, **kwargs: Any) -> None:
        """Update a player record - Base class stub"""
        raise NotImplementedError("update_player not supported for SQLite. Use MySQLDatabaseConnection.")

    def delete_player(self, player_id: int) -> None:
        """Delete a player record - Base class stub"""
        raise NotImplementedError("delete_player not supported for SQLite. Use MySQLDatabaseConnection.")

    def insert_match(self, match_desc: str, match_format: str, team1: str, team2: str) -> int:
        """Insert a new match - Base class stub"""
        raise NotImplementedError("insert_match not supported for SQLite. Use MySQLDatabaseConnection.")

    def insert_venue(self, venue_name: str, city: str, country: str) -> int:
        """Insert a new venue - Base class stub"""
        raise NotImplementedError("insert_venue not supported for SQLite. Use MySQLDatabaseConnection.")


# =====================================================
# MySQL connection (same interface)
# =====================================================
class MySQLDatabaseConnection(DatabaseConnection):
    """
    MySQL-backed DB connection for Streamlit UI.
    """

    def __init__(self, secrets: Dict[str, Any]):
        self.db_type = "mysql"
        self.secrets = secrets

        host = secrets.get("host", "localhost")
        user = secrets.get("user")
        password = secrets.get("password")
        database = secrets.get("dbname") or secrets.get("database")
        port = int(secrets.get("port", 3306))

        if not (user and password and database):
            raise ValueError("MySQL secrets missing required fields")

        # SQLAlchemy preferred
        if create_engine is not None:
            from urllib.parse import quote_plus

            pwd = quote_plus(password)
            url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{database}?charset=utf8mb4"
            self.connection = create_engine(url)
            self._engine_mode = True
        else:
            assert pymysql is not None
            self.connection = pymysql.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port,
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            self._engine_mode = False

    # ---------------------------
    # Overrides
    # ---------------------------
    def read_df(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        try:
            if self._engine_mode and not params:
                # Only use SQLAlchemy for queries without parameters
                return pd.read_sql(text(query), self.connection)
            else:
                # Use pymysql cursor for all parameterized queries or fallback
                cur = self.connection.cursor() if not self._engine_mode else self.connection.raw_connection().cursor()
                cur.execute(query, params or ())
                rows = cur.fetchall()

                
                # If using DictCursor, rows will be list of dicts
                if rows and isinstance(rows[0], dict):
                    return pd.DataFrame(rows)
                else:
                    # Regular cursor - rows are tuples
                    cols = [d[0] for d in cur.description] if cur.description else []
                    return pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"MySQL read error: {error_msg}")
            except Exception:
                # If st.error fails, silently continue
                print(f"MySQL read error: {error_msg}")
            return pd.DataFrame()

    def execute_query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> pd.DataFrame:
        """Alias for read_df to support legacy code"""
        return self.read_df(query, params)

    def execute(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> None:
        try:
            if self._engine_mode:
                # For engine mode, use pymysql cursor to handle parameters properly
                conn = self.connection.raw_connection()
                cur = conn.cursor()
                cur.execute(query, params or ())
                conn.commit()
            else:
                cur = self.connection.cursor()
                cur.execute(query, params or ())
                self.connection.commit()
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"MySQL execute error: {error_msg}")
            except Exception:
                print(f"MySQL execute error: {error_msg}")

    # ---------------------------
    # CRUD Operations
    # ---------------------------
    def get_players(self) -> pd.DataFrame:
        """Fetch all players from the database"""
        query = """
            SELECT 
                id, 
                external_player_id, 
                player_name, 
                country, 
                role, 
                date_of_birth,
                created_at
            FROM players 
            ORDER BY player_name
        """
        return self.read_df(query)

    def insert_player(self, player_name: str, country: str, role: str, batting_style: str = "N/A", bowling_style: str = "N/A", external_player_id: Optional[str] = None, date_of_birth: Optional[str] = None) -> int:
        """Insert a new player and return the player ID"""
        try:
            from .mysql_sync import upsert_player
        except ImportError:
            # Fallback if relative import doesn't work
            import sys
            import os
            utils_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, utils_dir)
            from mysql_sync import upsert_player
        
        player_data = {
            "playerName": player_name,
            "country": country,
            "playingRole": role,
            "battingStyle": batting_style,
            "bowlingStyle": bowling_style,
        }
        
        # Add optional fields if provided
        if external_player_id:
            player_data["id"] = external_player_id
        if date_of_birth:
            player_data["dateOfBirth"] = date_of_birth
        
        rc = upsert_player(self.secrets, player_data)
        
        # Fetch the inserted player's ID
        try:
            if self._engine_mode:
                query = "SELECT id FROM players WHERE player_name = %s ORDER BY created_at DESC LIMIT 1"
                result = self.read_df(query, (player_name,))
            else:
                cur = self.connection.cursor()
                cur.execute("SELECT id FROM players WHERE player_name = %s ORDER BY created_at DESC LIMIT 1", (player_name,))
                rows = cur.fetchall()
                
                # Handle DictCursor (returns list of dicts)
                if rows and isinstance(rows[0], dict):
                    result = pd.DataFrame(rows)
                else:
                    # Handle regular cursor (returns tuples)
                    cols = [d[0] for d in cur.description] if cur.description else None
                    result = pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
            
            if len(result) > 0:
                return int(result.iloc[0, 0])
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"Error fetching player ID: {error_msg}")
            except Exception:
                print(f"Error fetching player ID: {error_msg}")
        
        return 0

    def update_player(self, player_id: int, **kwargs: Any) -> None:
        """Update a player record"""
        updates = []
        values = []
        
        allowed_fields = ["player_name", "country", "role", "date_of_birth"]
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = %s")
                values.append(kwargs[field])
        
        if not updates:
            return
        
        values.append(player_id)
        query = f"UPDATE players SET {', '.join(updates)} WHERE id = %s"
        self.execute(query, tuple(values))

    def delete_player(self, player_id: int) -> None:
        """Delete a player record"""
        query = "DELETE FROM players WHERE id = %s"
        self.execute(query, (player_id,))

    def get_matches(self) -> pd.DataFrame:
        """Fetch all matches from the database"""
        query = """
            SELECT id, external_match_id, external_series_id, match_desc, 
                   match_format, start_date, status FROM matches ORDER BY start_date DESC
        """
        return self.read_df(query)

    def insert_match(self, match_desc: str, match_format: str, team1: str, team2: str) -> int:
        """Insert a new match"""
        try:
            if self._engine_mode:
                query = """
                    INSERT INTO matches (match_desc, match_format, status)
                    VALUES (:match_desc, :match_format, 'Not Started')
                """
                with self.connection.begin() as conn:
                    conn.execute(text(query), {"match_desc": match_desc, "match_format": match_format})
            else:
                query = """
                    INSERT INTO matches (match_desc, match_format, status)
                    VALUES (%s, %s, 'Not Started')
                """
                cur = self.connection.cursor()
                cur.execute(query, (match_desc, match_format))
                self.connection.commit()
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"MySQL execute error: {error_msg}")
            except Exception:
                print(f"MySQL execute error: {error_msg}")
            return 0
        
        # Fetch the inserted match's ID
        try:
            if self._engine_mode:
                result_query = "SELECT id FROM matches WHERE match_desc = %s ORDER BY created_at DESC LIMIT 1"
                result = self.read_df(result_query, (match_desc,))
            else:
                cur = self.connection.cursor()
                cur.execute("SELECT id FROM matches WHERE match_desc = %s ORDER BY created_at DESC LIMIT 1", (match_desc,))
                rows = cur.fetchall()
                
                # Handle DictCursor (returns list of dicts)
                if rows and isinstance(rows[0], dict):
                    result = pd.DataFrame(rows)
                else:
                    # Handle regular cursor (returns tuples)
                    cols = [d[0] for d in cur.description] if cur.description else None
                    result = pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
            
            if len(result) > 0:
                return int(result.iloc[0, 0])
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"Error fetching match ID: {error_msg}")
            except Exception:
                print(f"Error fetching match ID: {error_msg}")
        
        return 0

    def get_venues(self) -> pd.DataFrame:
        """Fetch all venues from the database"""
        query = "SELECT id, venue_name, city, country FROM venues ORDER BY venue_name"
        return self.read_df(query)

    def insert_venue(self, venue_name: str, city: str, country: str) -> int:
        """Insert a new venue"""
        try:
            if self._engine_mode:
                query = "INSERT INTO venues (venue_name, city, country) VALUES (:venue_name, :city, :country)"
                with self.connection.begin() as conn:
                    conn.execute(text(query), {"venue_name": venue_name, "city": city, "country": country})
            else:
                query = "INSERT INTO venues (venue_name, city, country) VALUES (%s, %s, %s)"
                cur = self.connection.cursor()
                cur.execute(query, (venue_name, city, country))
                self.connection.commit()
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"MySQL execute error: {error_msg}")
            except Exception:
                print(f"MySQL execute error: {error_msg}")
            return 0
        
        # Fetch the inserted venue's ID
        try:
            if self._engine_mode:
                result_query = "SELECT id FROM venues WHERE venue_name = %s ORDER BY created_at DESC LIMIT 1"
                result = self.read_df(result_query, (venue_name,))
            else:
                cur = self.connection.cursor()
                cur.execute("SELECT id FROM venues WHERE venue_name = %s ORDER BY created_at DESC LIMIT 1", (venue_name,))
                rows = cur.fetchall()
                
                # Handle DictCursor (returns list of dicts)
                if rows and isinstance(rows[0], dict):
                    result = pd.DataFrame(rows)
                else:
                    # Handle regular cursor (returns tuples)
                    cols = [d[0] for d in cur.description] if cur.description else None
                    result = pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
            
            if len(result) > 0:
                return int(result.iloc[0, 0])
        except Exception as e:
            error_msg = str(e)
            try:
                st.error(f"Error fetching venue ID: {error_msg}")
            except Exception:
                print(f"Error fetching venue ID: {error_msg}")
        
        return 0

    def close(self) -> None:
        try:
            if not self._engine_mode:
                self.connection.close()
        except Exception:
            pass


# =====================================================
# Factory (used by ALL Streamlit pages)
# =====================================================
def get_db_connection(secrets: Optional[Dict[str, Any]] = None) -> DatabaseConnection:
    """
    Return a DB connection for Streamlit UI.

    - MySQL if secrets provided
    - SQLite fallback
    """
    secrets = secrets or {}

    if any(k in secrets for k in ("host", "user", "password", "database", "dbname")):
        try:
            return MySQLDatabaseConnection(secrets)
        except Exception as e:
            st.warning(f"MySQL failed, falling back to SQLite: {e}")

    return DatabaseConnection()
