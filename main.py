import streamlit as st

st.set_page_config(page_title="Cricbuzz Analytics", layout="wide")

PAGES = {
    "Home": "home",
    "Live Matches": "live_matches",
    "Player Statistics": "player_statistics",
    "SQL Analytics": "sql_analytics"
}

choice = st.sidebar.radio("Menu", list(PAGES.keys()))
module = __import__(f"pages.{PAGES[choice]}", fromlist=["show"])
module.show()
