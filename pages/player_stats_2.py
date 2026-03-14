"""
Player Statistics Page
Uses real database tables only
"""

# pyright: reportUnknownMemberType=false
import streamlit as st
import pandas as pd
from typing import Any, cast

st = cast(Any, st)

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_connection import get_db_connection


def show():
    st.markdown("<h1 class='page-title'>📊 Player Statistics</h1>", unsafe_allow_html=True)

    # Get database connection with Streamlit secrets
    try:
        secrets = dict(st.secrets.get("mysql", {}))
        db = get_db_connection(secrets)
    except Exception:
        # Fallback if secrets not available
        db = get_db_connection()
    
    db = cast(Any, db)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🧍 Players", "🏏 Batting", "🎯 Bowling", "🔁 Innings", "🤝 Partnerships"]
    )

    # -----------------------------
    # TAB 1: PLAYERS
    # -----------------------------
    with tab1:
        st.subheader("All Players")

        try:
            df = db.execute_query("SELECT * FROM players ORDER BY player_name")
            st.dataframe(df)
            st.info(f"Total players: {len(df)}")
        except Exception as e:
            st.error(f"Error loading players: {e}")

    # -----------------------------
    # TAB 2: BATTING
    # -----------------------------
    with tab2:
        st.subheader("Batting Statistics")

        try:
            query = """
                SELECT 
                    player_name,
                    COUNT(*) AS innings_played,
                    SUM(runs) AS total_runs,
                    ROUND(AVG(runs), 2) AS average_runs,
                    ROUND(AVG(strike_rate), 2) AS avg_strike_rate
                FROM batting_stats
                GROUP BY player_name
                ORDER BY total_runs DESC
            """
            df = db.execute_query(query)
            df.insert(0, "Rank", range(1, len(df) + 1))
            st.dataframe(df)

        except Exception as e:
            st.error(f"Error loading batting stats: {e}")

    # -----------------------------
    # TAB 3: BOWLING
    # -----------------------------
    with tab3:
        st.subheader("Bowling Statistics")

        try:
            query = """
                SELECT 
                    player_name,
                    COUNT(*) AS innings_bowled,
                    SUM(wickets) AS total_wickets,
                    ROUND(AVG(economy), 2) AS avg_economy,
                    ROUND(AVG(overs), 2) AS avg_overs
                FROM bowling_stats
                GROUP BY player_name
                ORDER BY total_wickets DESC
            """
            df = db.execute_query(query)
            df.insert(0, "Rank", range(1, len(df) + 1))
            st.dataframe(df)

        except Exception as e:
            st.error(f"Error loading bowling stats: {e}")

    # -----------------------------
    # TAB 4: INNINGS
    # -----------------------------
    with tab4:
        st.subheader("Innings Records")

        try:
            query = """
                SELECT 
                    external_match_id,
                    innings_id,
                    batting_team,
                    bowling_team,
                    runs,
                    wickets,
                    overs
                FROM innings
                ORDER BY external_match_id, innings_id
            """
            df = db.execute_query(query)
            st.dataframe(df)
            st.info(f"Total innings: {len(df)}")

        except Exception as e:
            st.error(f"Error loading innings: {e}")

    # -----------------------------
    # TAB 5: PARTNERSHIPS
    # -----------------------------
    with tab5:
        st.subheader("Batting Partnerships")

        try:
            query = """
                SELECT 
                    player1,
                    player2,
                    COUNT(*) AS partnerships,
                    SUM(runs) AS total_runs,
                    ROUND(AVG(runs), 2) AS avg_runs
                FROM batting_partnerships
                GROUP BY player1, player2
                ORDER BY total_runs DESC
            """
            df = db.execute_query(query)
            df.insert(0, "Rank", range(1, len(df) + 1))
            st.dataframe(df)

        except Exception as e:
            st.error(f"Error loading partnerships: {e}")

    # -----------------------------
    # SUMMARY
    # -----------------------------
    st.markdown("---")
    st.subheader("📈 Database Summary")

    try:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c = db.execute_query("SELECT COUNT(*) AS cnt FROM players")
            st.metric("Players", int(c.iloc[0, 0]))

        with col2:
            c = db.execute_query("SELECT COUNT(*) AS cnt FROM matches")
            st.metric("Matches", int(c.iloc[0, 0]))

        with col3:
            c = db.execute_query("SELECT COUNT(*) AS cnt FROM innings")
            st.metric("Innings", int(c.iloc[0, 0]))

        with col4:
            c = db.execute_query("SELECT COUNT(*) AS cnt FROM batting_partnerships")
            st.metric("Partnerships", int(c.iloc[0, 0]))

    except Exception as e:
        st.warning(f"Could not load summary: {e}")
