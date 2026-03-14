# try:
#     from sqlalchemy import create_engine  # type: ignore
# except Exception:
#     create_engine = None
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

    def get_toss_details(self) -> pd.DataFrame:
        return self.read_df("SELECT * FROM toss_details ORDER BY Match_ID")

    # ---------------------------
    # CRUD Operations
    # ---------------------------
    def insert_player(self, Player_Name: str, Country: str, Role: str, Batting_Style: str = "N/A", Bowling_Style: str = "N/A", Player_ID: Optional[str] = None, DOB: Optional[str] = None) -> int:
        """Insert a new player - Base class stub"""
        raise NotImplementedError("insert_player not supported for SQLite. Use MySQLDatabaseConnection.")

    def update_player(self, Player_ID: int, **kwargs: Any) -> None:
        """Update a player record - Base class stub"""
        raise NotImplementedError("update_player not supported for SQLite. Use MySQLDatabaseConnection.")

    def delete_player(self, Player_ID: int) -> None:
        """Delete a player record - Base class stub"""
        raise NotImplementedError("delete_player not supported for SQLite. Use MySQLDatabaseConnection.")

    def insert_match(self, Match_Desc: str, Match_Format: str, Team1: str, Team2: str) -> int:
        """Insert a new match - Base class stub"""
        raise NotImplementedError("insert_match not supported for SQLite. Use MySQLDatabaseConnection.")

    def insert_venue(self, Venue_Name: str, City: str, Country: str) -> int:
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
                ID, 
                Player_ID, 
                Player_Name, 
                Country, 
                Role, 
                DOB,
                Created_ON
            FROM players 
            ORDER BY Player_Name
        """
        return self.read_df(query)

    def insert_player(self, Player_Name: str, Country: str, Role: str, Batting_Style: str = "N/A", Bowling_Style: str = "N/A", Player_ID: Optional[str] = None, DOB: Optional[str] = None) -> int:
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
            "playerName": Player_Name,
            "country": Country,
            "playingRole": Role,
            "battingStyle": Batting_Style,
            "bowlingStyle": Bowling_Style,
        }
        
        # Add optional fields if provided
        if Player_ID:
            player_data["id"] = Player_ID
        if DOB:
            player_data["dateOfBirth"] = DOB
        
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

    def update_player(self, Player_ID: int, **kwargs: Any) -> None:
        """Update a player record"""
        updates = []
        values = []
        
        allowed_fields = ["Player_Name", "Country", "Role", "DOB"]
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
            SELECT ID, Match_ID, Series_ID, Match_desc, 
                   ,Match_Format, Start_Date, Status FROM matches ORDER BY Start_Date DESC
        """
        return self.read_df(query)

    def insert_match(self, Match_Desc: str, Match_Format: str, Team1: str, Team2: str) -> int:
        """Insert a new match"""
        try:
            if self._engine_mode:
                query = """
                    INSERT INTO matches (Match_Desc, Match_Format, Status)
                    VALUES (:Match_Desc, :Match_Format, 'Not Started')
                """
                with self.connection.begin() as conn:
                    conn.execute(text(query), {"Match_Desc": Match_Desc, "Match_Format": Match_Format})
            else:
                query = """
                    INSERT INTO matches (Match_Desc, Match_Format, Status)
                    VALUES (%s, %s, 'Not Started')
                """
                cur = self.connection.cursor()
                cur.execute(query, (Match_Desc, Match_Format))
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
        query = "SELECT ID, Venue_Name, City, Country, Capacity FROM venues ORDER BY Venue_Name"
        return self.read_df(query)

    def insert_venue(self, Venue_Name: str, City: str, Country: str, Capacity: int = 0) -> int:
        """Insert a new venue"""
        try:
            if self._engine_mode:
                query = "INSERT INTO venues (Venue_Name, City, Country, Capacity) VALUES (:Venue_Name, :City, :Country, :Capacity)"
                with self.connection.begin() as conn:
                    conn.execute(text(query), {"venue_name": Venue_Name, "city": City, "country": Country, "capacity": Capacity})
            else:
                query = "INSERT INTO venues (Venue_Name, City, Country, Capacity) VALUES (%s, %s, %s, %s)"
                cur = self.connection.cursor()
                cur.execute(query, (Venue_Name, City, Country, Capacity))
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
                result_query = "SELECT id FROM venues WHERE Venue_Name = %s ORDER BY Created_ON DESC LIMIT 1"
                result = self.read_df(result_query, (Venue_Name,))
            else:
                cur = self.connection.cursor()
                cur.execute("SELECT id FROM venues WHERE Venue_Name = %s ORDER BY created_at DESC LIMIT 1", (Venue_Name,))
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
                st.error(f"Error fetching Venue ID: {error_msg}")
            except Exception:
                print(f"Error fetching Venue ID: {error_msg}")
        
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
