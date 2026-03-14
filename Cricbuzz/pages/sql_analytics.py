"""
SQL Analytics Page - 25 SQL Practice Queries with MySQL Integration
"""

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
        if hasattr(conn, "cursor") and not hasattr(conn, "engine"):
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                if rows and isinstance(rows[0], dict):
                    return pd.DataFrame(rows)
                cols = [d[0] for d in cur.description] if cur.description else None
                return pd.DataFrame(rows, columns=cols) if cols else pd.DataFrame(rows)
        return pd.read_sql(sql, conn)  # type: ignore[return-value]
    except Exception as e:
        st.error(f"SQL execution error: {e}")
        return pd.DataFrame()


def show():
    """Display SQL analytics page"""
    st.markdown("<h1 class='page-title'>🔍 SQL-Driven Analytics</h1>", unsafe_allow_html=True)

    st.markdown(
        """
    Execute SQL queries on live MySQL cricket database with real-time match data.
    """
    )

    mysql_secrets: MySQLSecrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }

    level_queries = get_all_mysql_queries()
    query_names = list(level_queries.keys())
    selected_query: str = st.selectbox("Select a Query", query_names, key="query_select")

    if selected_query:
        query_info: Dict[str, str] = level_queries[selected_query]
        st.markdown(f"## {selected_query}")
        st.markdown(f"**Description**: {query_info['description']}")
        with st.expander("View SQL Query", expanded=False):
            st.code(query_info["sql"], language="sql")

        # Year filter for Query 16
        selected_year = None
        if "Year-on-Year Batting Performance" in selected_query:
            year_col, _, _ = st.columns([1, 2, 2])
            with year_col:
                selected_year = st.selectbox("Select Year", options=[2020, 2021, 2022, 2023, 2024, 2025, 2026], key="year_select", help="Choose a specific year")

        col1, col2, _col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("▶️ Execute Query", key="execute_btn"):
                try:
                    sql_to_run = query_info["sql"].strip().rstrip(";")
                    
                    # Modify SQL for year filter if Query 16 is selected
                    if "Year-on-Year Batting Performance" in selected_query and selected_year:
                        if selected_year <= 2025:
                            # Use year-specific tables (2020-2025) with calculated strike rate
                            table_name = f"batting_scores_{selected_year}"
                            sql_to_run = f"""
                                SELECT
                                    player_name,
                                    COUNT(*) AS matches_played,
                                    ROUND(AVG(CAST(runs AS DECIMAL(10, 2))), 2) AS avg_runs_per_match,
                                    ROUND(AVG(CASE WHEN CAST(balls AS UNSIGNED) > 0 THEN (CAST(runs AS DECIMAL(10, 2)) / CAST(balls AS UNSIGNED)) * 100 ELSE 0 END), 2) AS avg_strike_rate,
                                    ROUND(SUM(CAST(runs AS DECIMAL(10, 2))), 0) AS total_runs,
                                    SUM(CAST(fours AS UNSIGNED)) AS total_fours,
                                    SUM(CAST(sixes AS UNSIGNED)) AS total_sixes
                                FROM {table_name}
                                GROUP BY player_name
                                HAVING COUNT(*) >= 5
                                ORDER BY avg_runs_per_match DESC
                                LIMIT 100
                            """
                        else:
                            # Use batting_stats table for 2026
                            sql_to_run = f"""
                                SELECT
                                    Player_Name,
                                    COUNT(*) AS matches_played,
                                    ROUND(AVG(CAST(Runs AS DECIMAL(10, 2))), 2) AS avg_runs_per_match,
                                    ROUND(AVG(CAST(Strike_Rate AS DECIMAL(10, 2))), 2) AS avg_strike_rate,
                                    ROUND(SUM(CAST(Runs AS DECIMAL(10, 2))), 0) AS total_runs,
                                    SUM(CAST(Fours AS UNSIGNED)) AS total_fours,
                                    SUM(CAST(Sixes AS UNSIGNED)) AS total_sixes
                                FROM batting_stats
                                GROUP BY Player_Name
                                HAVING COUNT(*) >= 5
                                ORDER BY avg_runs_per_match DESC
                                LIMIT 100
                            """
                    
                    conn = pymysql.connect(
                        host=mysql_secrets["host"],
                        user=mysql_secrets["user"],
                        password=mysql_secrets["password"],
                        database=mysql_secrets["database"],
                        port=mysql_secrets["port"],
                        cursorclass=pymysql.cursors.DictCursor,  # type: ignore[arg-type]
                    )
                    try:
                        with conn.cursor() as _test_cur:
                            _test_cur.execute("SELECT 1")
                            _ = _test_cur.fetchone()
                        with st.spinner("Executing query..."):
                            results_df = _safe_read_sql(conn, sql_to_run)

                        if not results_df.empty:
                            st.dataframe(results_df, width="stretch")  # type: ignore[arg-type]
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


def get_all_mysql_queries() -> Dict[str, Dict[str, str]]:
    """Return a dictionary of named SQL queries aligned with mysql_sync.py schema."""
    return {
        "Query 1: All Players from India": {
            "description": "Find all players who represent India with their full name, playing role, batting style, and bowling style",
            "sql": """
                SELECT
                    Player_Name AS Full_Name,
                    Role AS Playing_Role,
                    Country,
                    Batting_Style,
                    Bowling_Style
                FROM players
                WHERE UPPER(Country) IN ('INDIA','IND') OR Country LIKE '%India%'
                ORDER BY Player_Name ASC;
            """,
        },

        "Query 2: Recent Matches": {
            "description": "Show all cricket matches. Include match description, both team names (handles several JSON metadata formats such as team1_name, team1.teamName, or simple string), venue name with city, and match date. Sort by most recent matches first.",
            "sql": """
                SELECT
                    m.Match_ID,
                    m.Match_Desc AS Match_Description,
                    COALESCE(
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1_name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1.teamName')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1Name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1')),
                        'N/A'
                    ) AS Team1,
                    COALESCE(
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2_name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2.teamName')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2Name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2')),
                        'N/A'
                    ) AS Team2,
                    COALESCE(v.Venue_Name, JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.venue')), 'N/A') AS Venue,
                    COALESCE(v.City, 'N/A') AS City,
                    m.Start_Date AS Match_Date
                FROM matches m
                LEFT JOIN venues v ON m.Venue_ID = v.Venue_ID
                ORDER BY m.Start_Date DESC
                LIMIT 30
            """,
        },

        "Query 3: Top ODI Run Scorers": {
            "description": "Top 10 batsmen by total runs in ODI matches, with batting average and century count",
            "sql": """
                SELECT
                    b.Player_Name,
                    SUM(b.Runs) AS total_runs,
                    AVG(b.Runs) AS batting_avg,
                    SUM(CASE WHEN b.Runs >= 100 THEN 1 ELSE 0 END) AS centuries
                FROM batting_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                WHERE m.Match_Format = 'ODI'
                GROUP BY b.Player_Name
                ORDER BY total_runs DESC
                LIMIT 10
            """,
        },

        "Query 4: Large Venues": {
            "description": "Display venues with capacity over 25,000 showing name, city, country and capacity",
            "sql": """
                SELECT Venue_Name, City, Country, Capacity
                FROM venues
                WHERE Capacity > 25000
                ORDER BY Capacity DESC
                LIMIT 10
            """,
        },

        "Query 5: Team Wins by Counts": {
            "description": "Calculate how many matches each team has won",
            "sql": """
                SELECT 
                    TRIM(LEFT(Status, POSITION(' won' IN Status) - 1)) AS team_name,
                    COUNT(*) AS total_wins
                FROM matches
                WHERE Status LIKE '% won %'
                GROUP BY team_name
                ORDER BY total_wins DESC
            """,
        },

        "Query 6: Player Role Counts": {
            "description": "Count how many players belong to each playing role (combine all-rounders)",
            "sql": """
                SELECT 
                    CASE 
                        WHEN Role LIKE '%Allrounder%' THEN 'Allrounder'
                        ELSE Role
                    END AS playing_role,
                    COUNT(*) AS player_count
                FROM players
                WHERE Role IS NOT NULL AND Role != ''
                GROUP BY playing_role
                ORDER BY player_count DESC
            """,
        },

        "Query 7: Highest Score by Format": {
            "description": "Find the highest individual batting score in each match format",
            "sql": """
                SELECT m.Match_Format, MAX(b.Runs) AS highest_score
                FROM batting_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                WHERE m.Match_Format IS NOT NULL
                GROUP BY m.Match_Format
                ORDER BY highest_score DESC
            """,
        },

        "Query 8: Series in 2024": {
            "description": "Show all cricket series that started in 2024 with series name, match type, start date, and total matches",
            "sql": """
                SELECT 
                    Series_Name,
                    Match_Format,
                    MIN(Start_Date) AS start_date,
                    COUNT(*) AS total_matches_planned
                FROM matches_2024
                WHERE YEAR(Start_Date) = 2024
                GROUP BY Series_Name, Match_Format
                ORDER BY start_date ASC
            """,
        },

        "Query 9: All-Rounders (>1000 runs & >50 wickets by format)": {
            "description": "Players with over 1000 runs AND over 50 wickets broken down by match format (TEST, ODI, T20)",
            "sql": """
                SELECT
                    b.Player_Name,
                    m.Match_Format,
                    SUM(b.Runs) AS Total_Runs,
                    SUM(bw.Wickets) AS Total_Wickets
                FROM batting_stats b
                JOIN bowling_stats bw 
                    ON b.Player_Name = bw.Player_Name
                    AND b.Match_ID = bw.Match_ID
                JOIN matches m ON b.Match_ID = m.Match_ID
                GROUP BY b.Player_Name, m.Match_Format
                HAVING SUM(b.Runs) > 1000 AND SUM(bw.Wickets) > 50
                ORDER BY m.Match_Format, Total_Runs DESC
                LIMIT 200
            """,
        },

        "Query 10: Last 20 Completed Matches": {
            "description": "Details of the last 20 completed matches with teams, winning team, victory margin and type, venue, and match date",
            "sql": """
                SELECT
                    m.Match_Desc,
                    COALESCE(
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1_name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1.teamName')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1Name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team1')),
                        'N/A'
                    ) AS Team1,
                    COALESCE(
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2_name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2.teamName')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2Name')),
                        JSON_UNQUOTE(JSON_EXTRACT(m.Meta, '$.team2')),
                        'N/A'
                    ) AS Team2,
                    TRIM(LEFT(m.Status, POSITION(' won' IN m.Status) - 1)) AS Winning_Team,
                    TRIM(SUBSTRING(m.Status, POSITION('by' IN m.Status) + 2)) AS Victory_Margin,
                    CASE
                        WHEN m.Status LIKE '%runs%' THEN 'Runs'
                        WHEN m.Status LIKE '%wickets%' THEN 'Wickets'
                        ELSE 'Other'
                    END AS Victory_Type,
                    COALESCE(v.Venue_Name, 'N/A') AS Venue_Name,
                    m.Start_Date AS Match_Date
                FROM matches m
                LEFT JOIN venues v ON m.Venue_ID = v.Venue_ID
                WHERE m.Status LIKE '% won %'
                ORDER BY m.Start_Date DESC
                LIMIT 20
            """,
        },

        "Query 11: Format Comparison by Batsman": {
            "description": "Players' batting performance across different formats (Test, ODI, T20) - shows total runs per format and overall batting average for players who played 2+ formats",
            "sql": """
                SELECT
                    b.Player_Name,
                    COUNT(DISTINCT m.Match_Format) AS Formats_Played,
                    COALESCE(SUM(CASE WHEN m.Match_Format = 'TEST' THEN b.Runs END), 0) AS Test_Runs,
                    COALESCE(SUM(CASE WHEN m.Match_Format = 'ODI' THEN b.Runs END), 0) AS ODI_Runs,
                    COALESCE(SUM(CASE WHEN m.Match_Format = 'T20' THEN b.Runs END), 0) AS T20_Runs,
                    ROUND(AVG(b.Runs), 2) AS Overall_Batting_Average
                FROM batting_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                GROUP BY b.Player_Name
                HAVING COUNT(DISTINCT m.Match_Format) >= 2
                ORDER BY Overall_Batting_Average DESC
                LIMIT 50
            """,
        },

        "Query 12: Home vs Away Wins by Team": {
            "description": "Count of wins for each team when playing at home versus away (venue country compared to team name)",
            "sql": """
                SELECT
                    winner AS Team,
                    SUM(CASE WHEN v.Country IS NOT NULL AND v.Country <> '' AND winner = v.Country THEN 1 ELSE 0 END) AS Home_Wins,
                    SUM(CASE WHEN v.Country IS NOT NULL AND v.Country <> '' AND winner <> v.Country THEN 1 ELSE 0 END) AS Away_Wins
                FROM (
                    SELECT
                        m.Match_ID,
                        TRIM(LEFT(m.Status, POSITION(' won' IN m.Status) - 1)) AS winner
                    FROM matches m
                    WHERE m.Status LIKE '% won %'
                ) w
                JOIN matches m ON w.Match_ID = m.Match_ID
                LEFT JOIN venues v ON m.Venue_ID = v.Venue_ID
                GROUP BY winner
                ORDER BY Home_Wins DESC, Away_Wins DESC
            """,
        },

        "Query 13: Batting Partnerships (>=100 runs)": {
            "description": "Batting partnerships where two consecutive batsmen scored 100+ combined runs in the same innings",
            "sql": """
                SELECT
                    bat1_name AS Batsman1,
                    bat2_name AS Batsman2,
                    total_runs AS Partnership_Runs,
                    bat_team_name AS Team,
                    matchId AS Match_ID
                FROM partnerships_2025
                WHERE total_runs >= 100
                ORDER BY total_runs DESC
                LIMIT 50
            """,
        },

        "Query 14: Bowling Performance at Venues": {
            "description": "Bowling performance at different venues for bowlers who played at least 3 matches at the same venue and bowled at least 4 overs in each match",
            "sql": """
                SELECT
                    v.Venue_Name,
                    b.Player_Name,
                    COUNT(*) AS matches_played,
                    ROUND(AVG(b.Economy), 2) AS avg_economy,
                    SUM(b.Wickets) AS total_wickets
                FROM bowling_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                JOIN venues v ON m.Venue_ID = v.Venue_ID
                WHERE b.Overs >= 4
                GROUP BY v.Venue_ID, b.Player_Name
                HAVING COUNT(*) >= 3
                ORDER BY avg_economy ASC
                LIMIT 25
            """,
        },

        "Query 15: Performance in Close Matches": {
            "description": "Players who perform exceptionally well in close matches (decided by <50 runs or <5 wickets), showing average runs, close matches played, and team wins when they batted",
            "sql": """
                WITH close_matches AS (
                    SELECT
                        m.Match_ID,
                        TRIM(LEFT(m.Status, POSITION(' won' IN m.Status) - 1)) AS winner
                    FROM matches m
                    WHERE m.Status LIKE '% won %'
                      AND (
                          (m.Status LIKE '%runs%' AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.Status, 'by ', -1), ' runs', 1) AS UNSIGNED) < 50)
                          OR
                          (m.Status LIKE '%wickets%' AND CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(m.Status, 'by ', -1), ' wickets', 1) AS UNSIGNED) < 5)
                      )
                )
                SELECT
                    b.Player_Name,
                    ROUND(AVG(b.Runs), 2) AS avg_runs_in_close_matches,
                    COUNT(DISTINCT b.Match_ID) AS close_matches_played,
                    SUM(CASE WHEN i.Batting_Team = cm.winner THEN 1 ELSE 0 END) AS team_wins_when_batted
                FROM batting_stats b
                JOIN innings i ON b.Match_ID = i.Match_ID AND b.Innings_ID = i.Innings_ID
                JOIN close_matches cm ON b.Match_ID = cm.Match_ID
                GROUP BY b.Player_Name
                HAVING close_matches_played >= 3
                ORDER BY avg_runs_in_close_matches DESC
                LIMIT 20
            """,
        },

        "Query 16: Year-on-Year Batting Performance (Since 2020)": {
            "description": "Track how players' batting performance changes over different years. Shows each player's average runs per match and average strike rate for each year, for players with at least 5 matches in that year.",
            "sql": """
                SELECT
                    b.Player_Name,
                    YEAR(m.Start_Date) AS Year,
                    COUNT(*) AS matches_played,
                    ROUND(AVG(b.Runs), 2) AS avg_runs_per_match,
                    ROUND(AVG(b.Strike_Rate), 2) AS avg_strike_rate,
                    ROUND(SUM(b.Runs), 0) AS total_runs,
                    SUM(b.Fours) AS total_fours,
                    SUM(b.Sixes) AS total_sixes
                FROM batting_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                WHERE YEAR(m.Start_Date) >= 2020
                GROUP BY b.Player_Name, YEAR(m.Start_Date)
                HAVING COUNT(*) >= 5
                ORDER BY Year DESC, avg_runs_per_match DESC
                LIMIT 100
            """,
        },

        "Query 17: Toss Advantage Analysis": {
            "description": "Investigate whether winning the toss gives teams an advantage in winning matches. Calculate what percentage of matches are won by the team that wins the toss, broken down by their toss decision (choosing to bat first or bowl first).",
            "sql": """
                SELECT
                    t.decision AS toss_decision,
                    COUNT(*) AS total_matches,
                    SUM(CASE WHEN t.toss_winner_team = TRIM(LEFT(m.Status, POSITION(' won' IN m.Status) - 1)) THEN 1 ELSE 0 END) AS toss_winner_won,
                    ROUND((SUM(CASE WHEN t.toss_winner_team = TRIM(LEFT(m.Status, POSITION(' won' IN m.Status) - 1)) THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS win_percentage
                FROM toss_details t
                JOIN matches m ON t.Match_ID = m.Match_ID
                WHERE m.Status LIKE '% won %'
                GROUP BY t.decision
                ORDER BY win_percentage DESC
            """,
        },

        "Query 18: Most Economical Bowlers in Limited-Overs Cricket": {
            "description": "Find the most economical bowlers in limited-overs cricket (ODI and T20 formats). Calculate each bowler's overall economy rate and total wickets taken. Only consider bowlers who have bowled in at least 10 matches and bowled at least 2 overs per match on average.",
            "sql": """
                SELECT
                    b.Player_Name,
                    COUNT(*) AS matches_played,
                    ROUND(AVG(b.Economy), 2) AS overall_economy_rate,
                    SUM(b.Wickets) AS total_wickets,
                    ROUND(AVG(b.Overs), 1) AS avg_overs_per_match,
                    ROUND(SUM(b.Overs), 1) AS total_overs_bowled
                FROM bowling_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                WHERE m.Match_Format IN ('ODI', 'T20') AND b.Overs > 0
                GROUP BY b.Player_Name
                HAVING COUNT(*) >= 10 AND AVG(b.Overs) >= 2
                ORDER BY overall_economy_rate ASC
                LIMIT 20
            """,
        },

        "Query 19: Most Consistent Batsmen (2025-2026)": {
            "description": "Determine which batsmen are most consistent in their scoring. Calculate the average runs scored and the standard deviation of runs for each player. Only include players who have faced at least 10 balls per innings and played in both 2025 and 2026. A lower standard deviation indicates more consistent performance.",
            "sql": """
                SELECT
                    b.Player_Name,
                    COUNT(DISTINCT b.Match_ID) AS matches_played,
                    ROUND(AVG(b.Runs), 2) AS avg_runs_per_match,
                    ROUND(STDDEV(b.Runs), 2) AS runs_standard_deviation,
                    ROUND(AVG(b.Balls), 1) AS avg_balls_faced,
                    ROUND(AVG(b.Strike_Rate), 2) AS avg_strike_rate,
                    SUM(b.Runs) AS total_runs,
                    MAX(b.Runs) AS highest_score,
                    COUNT(DISTINCT YEAR(m.Start_Date)) AS years_played
                FROM batting_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                WHERE b.Balls >= 10 AND YEAR(m.Start_Date) IN (2025, 2026)
                GROUP BY b.Player_Name
                HAVING COUNT(DISTINCT b.Match_ID) >= 3 AND COUNT(DISTINCT YEAR(m.Start_Date)) = 2
                ORDER BY runs_standard_deviation ASC
                LIMIT 20
            """,
        },

        "Query 20: Format-wise Match Count & Batting Average": {
            "description": "Analyze how many matches each player has played in different formats (Test, ODI, T20) with their respective batting averages. Only includes players with 5+ total matches across all formats.",
            "sql": """
                SELECT
                    b.Player_Name,
                    COUNT(DISTINCT CASE WHEN UPPER(m.Match_Format) = 'TEST' THEN b.Match_ID END) AS test_matches,
                    ROUND(AVG(CASE WHEN UPPER(m.Match_Format) = 'TEST' THEN b.Runs ELSE NULL END), 2) AS test_batting_avg,
                    COUNT(DISTINCT CASE WHEN UPPER(m.Match_Format) = 'ODI' THEN b.Match_ID END) AS odi_matches,
                    ROUND(AVG(CASE WHEN UPPER(m.Match_Format) = 'ODI' THEN b.Runs ELSE NULL END), 2) AS odi_batting_avg,
                    COUNT(DISTINCT CASE WHEN UPPER(m.Match_Format) = 'T20' OR UPPER(m.Match_Format) LIKE '%T20%' THEN b.Match_ID END) AS t20_matches,
                    ROUND(AVG(CASE WHEN UPPER(m.Match_Format) = 'T20' OR UPPER(m.Match_Format) LIKE '%T20%' THEN b.Runs ELSE NULL END), 2) AS t20_batting_avg,
                    COUNT(DISTINCT b.Match_ID) AS total_matches,
                    ROUND(AVG(b.Runs), 2) AS overall_batting_avg,
                    ROUND(AVG(COALESCE(b.Strike_Rate, 0)), 2) AS overall_strike_rate,
                    SUM(CASE WHEN b.Runs >= 100 THEN 1 ELSE 0 END) AS total_centuries,
                    SUM(CASE WHEN b.Runs >= 50 AND b.Runs < 100 THEN 1 ELSE 0 END) AS total_fifties
                FROM batting_stats b
                JOIN matches m ON b.Match_ID = m.Match_ID
                WHERE m.Match_Format IS NOT NULL AND m.Match_Format != ''
                GROUP BY b.Player_Name
                HAVING COUNT(DISTINCT b.Match_ID) >= 5
                ORDER BY total_matches DESC, overall_batting_avg DESC
                LIMIT 100
            """,
        },

        "Query 21: Maiden Overs Bowled": {
            "description": "Bowlers with most maiden overs",
            "sql": """
                SELECT Player_Name, SUM(Maidens) as total_maidens, SUM(Overs) as total_overs, ROUND(SUM(Maidens)*100.0/NULLIF(SUM(Overs),0),2) as maiden_percentage, COUNT(*) as matches
                FROM bowling_stats
                WHERE Overs > 0
                GROUP BY Player_Name
                HAVING SUM(Maidens) > 0
                ORDER BY total_maidens DESC
                LIMIT 20
            """,
        },

        "Query 22: Close Matches": {
            "description": "Matches decided by small margins",
            "sql": """
                SELECT Match_ID, Match_Desc, Status, Match_Format, Venue_ID, Start_Date
                FROM matches
                WHERE (Status LIKE '%won by 1 run%' OR Status LIKE '%won by 2 run%' OR Status LIKE '%won by 1 wicket%' OR Status LIKE '%won by 2 wicket%' OR Status LIKE '%tied%')
                ORDER BY Start_Date DESC
                LIMIT 25
            """,
        },

        "Query 23: Player Database Summary": {
            "description": "Overview of all players in database",
            "sql": """
                SELECT COUNT(*) as total_players, COUNT(DISTINCT CASE WHEN Meta LIKE '%batting_style%' THEN Player_Name END) as batsmen_count, COUNT(DISTINCT CASE WHEN Meta LIKE '%bowling_style%' THEN Player_Name END) as bowlers_count, COUNT(DISTINCT Country) as countries_represented
                FROM players
            """,
        },

        "Query 24: Match Data Quality Check": {
            "description": "Check completeness of match data",
            "sql": """
                SELECT 'Total Matches' as metric, COUNT(*) as count FROM matches
                UNION ALL
                SELECT 'Matches with Scores', COUNT(DISTINCT b.Match_ID) FROM batting_stats b
                UNION ALL
                SELECT 'Matches with Bowling Data', COUNT(DISTINCT bw.Match_ID) FROM bowling_stats bw
                UNION ALL
                SELECT 'Complete Match Records', COUNT(DISTINCT m.Match_ID) FROM matches m WHERE EXISTS (SELECT 1 FROM batting_stats b WHERE b.Match_ID = m.Match_ID) AND EXISTS (SELECT 1 FROM bowling_stats bw WHERE bw.Match_ID = m.Match_ID)
            """,
        },

        "Query 25: Database Summary": {
            "description": "Complete overview of cricket database",
            "sql": """
                SELECT 'Players' as table_name, COUNT(*) as record_count FROM players
                UNION ALL
                SELECT 'Matches', COUNT(*) FROM matches
                UNION ALL
                SELECT 'Batting Records', COUNT(*) FROM batting_stats
                UNION ALL
                SELECT 'Bowling Records', COUNT(*) FROM bowling_stats
                ORDER BY record_count DESC
            """,
        },
    }
    
