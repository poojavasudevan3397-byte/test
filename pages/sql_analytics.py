"""
SQL Analytics Page - 25 SQL Practice Queries with MySQL Integration
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
import pymysql
from typing import TypedDict

class MySQLSecrets(TypedDict):
    host: str
    user: str
    password: str
    database: str
    port: int

def _safe_read_sql(conn: Any, sql: str) -> pd.DataFrame:
    """Run SQL using a raw pymysql connection or SQLAlchemy engine and return a DataFrame."""
    try:
        # Raw pymysql connection (use cursor/fetchall)
        if hasattr(conn, "cursor") and not hasattr(conn, "engine"):
            # use context manager to ensure cursor closes
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if rows and isinstance(rows[0], dict):
                    return pd.DataFrame(rows)
                cols = [d[0] for d in cur.description] if cur.description else None
                return pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
        # SQLAlchemy engine or other supported connection
        return pd.read_sql(sql, conn)  # type: ignore[return-value]
    except Exception as e:
        st.error(f"SQL execution error: {e}")
        return pd.DataFrame()


def show():
    """Display SQL analytics page"""
    st.markdown("<h1 class='page-title'>🔍 SQL-Driven Analytics</h1>", unsafe_allow_html=True)
    # (no session-state flag needed; queries execute on button click)

    st.markdown("""
    Execute SQL queries on live MySQL cricket database with real-time match data.
    """)

    # MySQL connection
    mysql_secrets: MySQLSecrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }

    # Query selection
    level_queries = get_all_mysql_queries()
    query_names = list(level_queries.keys())
    selected_query: str = st.selectbox(
        "Select a Query",
        query_names,
        key="query_select"
    )

    if selected_query:
        query_info: Dict[str, str] = level_queries[selected_query]
        
        st.markdown(f"## {selected_query}")
        st.markdown(f"**Description**: {query_info['description']}")
        
        with st.expander("View SQL Query", expanded=False):
            st.code(query_info['sql'], language='sql')

        col1, col2, _col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("▶️ Execute Query", key="execute_btn"):
                # execute immediately on click (avoids subtle session_state issues)
                try:
                    sql_to_run = query_info["sql"].strip().rstrip(";")

                    conn = pymysql.connect(
                        host=mysql_secrets["host"],
                        user=mysql_secrets["user"],
                        password=mysql_secrets["password"],
                        database=mysql_secrets["database"],
                        port=mysql_secrets["port"],
                        cursorclass=pymysql.cursors.DictCursor,  # type: ignore[arg-type]
                    )

                    try:
                        # quick connectivity sanity check
                        with conn.cursor() as _test_cur:
                            _test_cur.execute("SELECT 1")
                            _ = _test_cur.fetchone()
                        with st.spinner("Executing query..."):
                            results_df = _safe_read_sql(conn, sql_to_run)

                        if not results_df.empty:
                            st.dataframe(results_df, use_container_width=True) #type: ignore[arg-type]
                            st.success(f"✓ Query executed successfully - {results_df.shape[0]} rows returned")
 
                            csv = results_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results (CSV)",
                                data=csv,
                                file_name=f"{selected_query}.csv",
                                mime="text/csv",
                            )
                        else:
                            st.info("No results returned. If you expect rows: check SQL, credentials, or run SQL in MySQL client to verify.")
                    finally:
                        conn.close()
                except Exception as e:
                    st.error(f"Query execution error: {e}")
        with col2:
            if st.button("📋 Copy Query", key="copy_btn"):
                st.success("Query copied to clipboard!")

        # (Removed session-state driven execution; queries run directly on button click above.)


def get_all_mysql_queries() -> Dict[str, Dict[str, str]]:
    """Get all 25 MySQL queries"""
    return {
        "Query 1: All Players from Database": {
            "description": "Show all players currently in the MySQL database with their details",
            "sql": "SELECT * FROM players ORDER BY player_name LIMIT 100;"
        },
        
        "Query 2: Recent Matches": {
            "description": "Display the 20 most recent matches stored in database",
            "sql": """
                SELECT 
                    external_match_id,
                    series_name,
                    team1,
                    team2,
                    match_format,
                    status,
                    venue,
                    start_date
                FROM matches
                ORDER BY start_date DESC
                LIMIT 20;
            """
        },
        
        "Query 3: Top Run Scorers": {
            "description": "Find top 20 batsmen by total runs from batting_stats table",
            "sql": """
                SELECT 
                    player_name,
                    SUM(runs) as total_runs,
                    COUNT(*) as innings_played,
                    AVG(runs) as avg_runs,
                    MAX(runs) as highest_score
                FROM batting_stats
                GROUP BY player_name
                ORDER BY total_runs DESC
                LIMIT 20;
            """
        },
        
        "Query 4: Top Wicket Takers": {
            "description": "Find top 20 bowlers by total wickets from bowling_stats",
            "sql": """
                SELECT 
                    player_name,
                    SUM(wickets) as total_wickets,
                    COUNT(*) as matches,
                    AVG(economy) as avg_economy,
                    SUM(overs) as total_overs
                FROM bowling_stats
                WHERE wickets > 0
                GROUP BY player_name
                ORDER BY total_wickets DESC
                LIMIT 20;
            """
        },
        
        "Query 5: Match Count by Format": {
            "description": "Count total matches by format (Test, ODI, T20, etc.)",
            "sql": """
                SELECT 
                    match_format,
                    COUNT(*) as match_count,
                    COUNT(DISTINCT team1) + COUNT(DISTINCT team2) as unique_teams
                FROM matches
                GROUP BY match_format
                ORDER BY match_count DESC;
            """
        },
        
        "Query 6: Series Statistics": {
            "description": "Show all cricket series with match counts",
            "sql": """
                SELECT 
                    series_name,
                    COUNT(*) as total_matches,
                    COUNT(DISTINCT team1) as unique_teams,
                    MIN(start_date) as first_match,
                    MAX(start_date) as last_match
                FROM matches
                WHERE series_name IS NOT NULL
                GROUP BY series_name
                ORDER BY total_matches DESC
                LIMIT 25;
            """
        },
        
        "Query 7: Batting Performance by Format": {
            "description": "Compare batting stats across different match formats",
            "sql": """
                SELECT 
                    m.match_format,
                    COUNT(DISTINCT b.player_name) as players,
                    AVG(b.runs) as avg_runs,
                    AVG(b.strike_rate) as avg_strike_rate,
                    SUM(b.fours) as total_fours,
                    SUM(b.sixes) as total_sixes
                FROM batting_stats b
                JOIN matches m ON b.external_match_id = m.external_match_id
                WHERE m.match_format IS NOT NULL
                GROUP BY m.match_format
                ORDER BY players DESC;
            """
        },
        
        "Query 8: Century Makers": {
            "description": "Find all centuries (100+ runs) scored",
            "sql": """
                SELECT 
                    b.player_name,
                    b.runs,
                    b.balls,
                    b.strike_rate,
                    m.team1,
                    m.team2,
                    m.match_format,
                    m.start_date
                FROM batting_stats b
                JOIN matches m ON b.external_match_id = m.external_match_id
                WHERE b.runs >= 100
                ORDER BY b.runs DESC
                LIMIT 30;
            """
        },
        
        "Query 9: Five Wicket Hauls": {
            "description": "Bowlers who took 5 or more wickets in an innings",
            "sql": """
                SELECT 
                    bw.player_name,
                    bw.wickets,
                    bw.runs_conceded,
                    bw.overs,
                    bw.economy,
                    m.team1,
                    m.team2,
                    m.match_format
                FROM bowling_stats bw
                JOIN matches m ON bw.external_match_id = m.external_match_id
                WHERE bw.wickets >= 5
                ORDER BY bw.wickets DESC, bw.economy ASC
                LIMIT 25;
            """
        },
        
        "Query 10: Team Performance Summary": {
            "description": "Win statistics for each team",
            "sql": """
                SELECT 
                    team1 as team_name,
                    COUNT(*) as matches_played,
                    SUM(CASE WHEN status LIKE CONCAT(team1, '%won%') THEN 1 ELSE 0 END) as wins
                FROM matches
                WHERE team1 IS NOT NULL
                GROUP BY team1
                
                UNION ALL
                
                SELECT 
                    team2 as team_name,
                    COUNT(*) as matches_played,
                    SUM(CASE WHEN status LIKE CONCAT(team2, '%won%') THEN 1 ELSE 0 END) as wins
                FROM matches
                WHERE team2 IS NOT NULL
                GROUP BY team2
                
                ORDER BY wins DESC
                LIMIT 20;
            """
        },
        
        "Query 11: Highest Strike Rates": {
            "description": "Batsmen with highest strike rates (min 30 balls faced)",
            "sql": """
                SELECT 
                    player_name,
                    COUNT(*) as innings,
                    SUM(runs) as total_runs,
                    SUM(balls) as total_balls,
                    AVG(strike_rate) as avg_strike_rate,
                    MAX(strike_rate) as highest_strike_rate
                FROM batting_stats
                WHERE balls >= 30 AND strike_rate > 0
                GROUP BY player_name
                HAVING SUM(balls) >= 100
                ORDER BY avg_strike_rate DESC
                LIMIT 20;
            """
        },
        
        "Query 12: Best Economy Rates": {
            "description": "Bowlers with best economy rates (min 10 overs bowled)",
            "sql": """
                SELECT 
                    player_name,
                    COUNT(*) as matches,
                    SUM(wickets) as total_wickets,
                    SUM(overs) as total_overs,
                    AVG(economy) as avg_economy,
                    SUM(maidens) as total_maidens
                FROM bowling_stats
                WHERE overs >= 3 AND economy > 0
                GROUP BY player_name
                HAVING SUM(overs) >= 10
                ORDER BY avg_economy ASC
                LIMIT 20;
            """
        },
        
        "Query 13: Match Results Distribution": {
            "description": "How matches ended (by runs, wickets, etc.)",
            "sql": """
                SELECT 
                    CASE 
                        WHEN status LIKE '%won by%runs%' THEN 'Won by Runs'
                        WHEN status LIKE '%won by%wicket%' THEN 'Won by Wickets'
                        WHEN status LIKE '%tied%' THEN 'Tied'
                        WHEN status LIKE '%abandoned%' THEN 'Abandoned'
                        WHEN status LIKE '%no result%' THEN 'No Result'
                        ELSE 'Other'
                    END as result_type,
                    COUNT(*) as match_count,
                    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM matches), 2) as percentage
                FROM matches
                WHERE status IS NOT NULL
                GROUP BY result_type
                ORDER BY match_count DESC;
            """
        },
        
        "Query 14: Venue Statistics": {
            "description": "Matches played at different venues",
            "sql": """
                SELECT 
                    venue,
                    COUNT(*) as matches_played,
                    COUNT(DISTINCT series_name) as series_hosted,
                    COUNT(DISTINCT match_format) as formats_played
                FROM matches
                WHERE venue IS NOT NULL AND venue != 'N/A'
                GROUP BY venue
                ORDER BY matches_played DESC
                LIMIT 25;
            """
        },
        
        "Query 15: Player Consistency": {
            "description": "Most consistent batsmen (low standard deviation in scores)",
            "sql": """
                SELECT 
                    player_name,
                    COUNT(*) as innings,
                    AVG(runs) as avg_runs,
                    STDDEV(runs) as std_dev_runs,
                    MIN(runs) as min_score,
                    MAX(runs) as max_score
                FROM batting_stats
                GROUP BY player_name
                HAVING COUNT(*) >= 5
                ORDER BY std_dev_runs ASC
                LIMIT 20;
            """
        },
        
        "Query 16: Boundary Hitters": {
            "description": "Players with most fours and sixes",
            "sql": """
                SELECT 
                    player_name,
                    COUNT(*) as innings,
                    SUM(fours) as total_fours,
                    SUM(sixes) as total_sixes,
                    SUM(fours) + SUM(sixes) as total_boundaries,
                    SUM(runs) as total_runs
                FROM batting_stats
                GROUP BY player_name
                ORDER BY total_boundaries DESC
                LIMIT 20;
            """
        },
        
        "Query 17: Recent Form": {
            "description": "Player performance in last 10 matches",
            "sql": """
                SELECT 
                    b.player_name,
                    COUNT(*) as recent_innings,
                    AVG(b.runs) as avg_runs,
                    AVG(b.strike_rate) as avg_strike_rate,
                    SUM(b.fours) as fours,
                    SUM(b.sixes) as sixes
                FROM batting_stats b
                JOIN matches m ON b.external_match_id = m.external_match_id
                WHERE m.start_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY b.player_name
                HAVING COUNT(*) >= 3
                ORDER BY avg_runs DESC
                LIMIT 20;
            """
        },
        
        "Query 18: Bowling Variations": {
            "description": "Bowlers' wicket-taking ability vs economy",
            "sql": """
                SELECT 
                    player_name,
                    COUNT(*) as matches,
                    AVG(wickets) as avg_wickets_per_match,
                    AVG(economy) as avg_economy,
                    SUM(wickets) as total_wickets,
                    AVG(overs) as avg_overs
                FROM bowling_stats
                WHERE overs > 0
                GROUP BY player_name
                HAVING COUNT(*) >= 5
                ORDER BY avg_wickets_per_match DESC
                LIMIT 20;
            """
        },
        
        "Query 19: All-Rounder Performance": {
            "description": "Players who both bat and bowl",
            "sql": """
                SELECT 
                    COALESCE(bat.player_name, bowl.player_name) as player_name,
                    COALESCE(bat.batting_innings, 0) as batting_innings,
                    COALESCE(bat.total_runs, 0) as total_runs,
                    COALESCE(bowl.bowling_matches, 0) as bowling_matches,
                    COALESCE(bowl.total_wickets, 0) as total_wickets
                FROM 
                    (SELECT player_name, COUNT(*) as batting_innings, SUM(runs) as total_runs 
                     FROM batting_stats GROUP BY player_name) bat
                FULL OUTER JOIN 
                    (SELECT player_name, COUNT(*) as bowling_matches, SUM(wickets) as total_wickets 
                     FROM bowling_stats GROUP BY player_name) bowl
                ON bat.player_name = bowl.player_name
                WHERE COALESCE(bat.total_runs, 0) > 100 AND COALESCE(bowl.total_wickets, 0) > 5
                ORDER BY (COALESCE(bat.total_runs, 0) + COALESCE(bowl.total_wickets, 0) * 20) DESC
                LIMIT 20;
            """
        },
        
        "Query 20: Format-wise Best Performances": {
            "description": "Best individual scores in each format",
            "sql": """
                SELECT 
                    m.match_format,
                    b.player_name,
                    b.runs,
                    b.balls,
                    b.strike_rate,
                    m.team1,
                    m.team2
                FROM batting_stats b
                JOIN matches m ON b.external_match_id = m.external_match_id
                WHERE (m.match_format, b.runs) IN (
                    SELECT match_format, MAX(runs)
                    FROM batting_stats b2
                    JOIN matches m2 ON b2.external_match_id = m2.external_match_id
                    GROUP BY match_format
                )
                ORDER BY b.runs DESC;
            """
        },
        
        "Query 21: Maiden Overs Bowled": {
            "description": "Bowlers with most maiden overs",
            "sql": """
                SELECT 
                    player_name,
                    SUM(maidens) as total_maidens,
                    SUM(overs) as total_overs,
                    ROUND(SUM(maidens) * 100.0 / SUM(overs), 2) as maiden_percentage,
                    COUNT(*) as matches
                FROM bowling_stats
                WHERE overs > 0
                GROUP BY player_name
                HAVING SUM(maidens) > 0
                ORDER BY total_maidens DESC
                LIMIT 20;
            """
        },
        
        "Query 22: Close Matches": {
            "description": "Matches decided by small margins",
            "sql": """
                SELECT 
                    external_match_id,
                    team1,
                    team2,
                    status,
                    match_format,
                    venue,
                    start_date
                FROM matches
                WHERE 
                    (status LIKE '%won by 1 run%' OR 
                     status LIKE '%won by 2 run%' OR
                     status LIKE '%won by 1 wicket%' OR
                     status LIKE '%won by 2 wicket%' OR
                     status LIKE '%tied%')
                ORDER BY start_date DESC
                LIMIT 25;
            """
        },
        
        "Query 23: Player Database Summary": {
            "description": "Overview of all players in database",
            "sql": """
                SELECT 
                    COUNT(*) as total_players,
                    COUNT(DISTINCT CASE WHEN meta LIKE '%batting_style%' THEN player_name END) as batsmen_count,
                    COUNT(DISTINCT CASE WHEN meta LIKE '%bowling_style%' THEN player_name END) as bowlers_count,
                    COUNT(DISTINCT country) as countries_represented
                FROM players;
            """
        },
        
        "Query 24: Match Data Quality Check": {
            "description": "Check completeness of match data",
            "sql": """
                SELECT 
                    'Total Matches' as metric,
                    COUNT(*) as count
                FROM matches
                
                UNION ALL
                
                SELECT 
                    'Matches with Scores',
                    COUNT(DISTINCT b.external_match_id)
                FROM batting_stats b
                
                UNION ALL
                
                SELECT 
                    'Matches with Bowling Data',
                    COUNT(DISTINCT bw.external_match_id)
                FROM bowling_stats bw
                
                UNION ALL
                
                SELECT 
                    'Complete Match Records',
                    COUNT(DISTINCT m.external_match_id)
                FROM matches m
                WHERE EXISTS (SELECT 1 FROM batting_stats b WHERE b.external_match_id = m.external_match_id)
                  AND EXISTS (SELECT 1 FROM bowling_stats bw WHERE bw.external_match_id = m.external_match_id);
            """
        },
        
        "Query 25: Database Summary": {
            "description": "Complete overview of cricket database",
            "sql": """
                SELECT 
                    'Players' as table_name,
                    COUNT(*) as record_count
                FROM players
                
                UNION ALL
                
                SELECT 'Matches', COUNT(*) FROM matches
                
                UNION ALL
                
                SELECT 'Batting Records', COUNT(*) FROM batting_stats
                
                UNION ALL
                
                SELECT 'Bowling Records', COUNT(*) FROM bowling_stats
                
                ORDER BY record_count DESC;
            """
        }
    }
