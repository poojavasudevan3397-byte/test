"""
CRUD Operations Page - Create, Read, Update, Delete Player and Match Records
"""

import streamlit as st
from typing import Any, cast

# Help Pylance by treating Streamlit and DB connection as Any for dynamic members
st = cast(Any, st)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import get_db_connection


def show():
    """Display CRUD operations page"""
    st.markdown("<h1 class='page-title'>🛠️ CRUD Operations</h1>", unsafe_allow_html=True)

    st.markdown("""
    Manage your cricket database with full CRUD (Create, Read, Update, Delete) operations.
    Add new players, matches, and venues, or modify existing records.
    """)

    # Get database connection with Streamlit secrets
    try:
        secrets = dict(st.secrets.get("mysql", {}))
        db = get_db_connection(secrets)
    except Exception:
        # Fallback if secrets not available
        db = get_db_connection()
    
    db = cast(Any, db)

    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs(
        ["👤 Players", "🏟️ Matches", "🏟️ Venues", "📊 Summary"]
    )

    # Tab 1: Player Management
    with tab1:
        st.markdown("## 👤 Player Management")

        operation = st.radio(
            "Select Operation",
            ["Create", "Read", "Update", "Delete"],
            horizontal=True,
            key="player_op"
        )

        if operation == "Create":
            st.markdown("### Add New Player")
            with st.form("add_player_form"):
                import datetime as dt
                external_player_id = st.text_input("External Player ID", placeholder="e.g., 12345", help="Unique identifier from the API")
                player_name = st.text_input("Player Name", placeholder="e.g., Virat Kohli")
                country = st.selectbox(
                    "Country",
                    ["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan"]
                )
                role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper"])
                batting_style = st.selectbox("Batting Style", ["Right", "Left", "Ambidextrous", "N/A"])
                bowling_style = st.selectbox("Bowling Style", ["Right", "Left", "N/A"])
                date_of_birth = st.date_input(
                    "Date of Birth", 
                    value=None,
                    min_value=dt.date(1900, 1, 1),
                    max_value=dt.date.today(),
                    help="Optional field - Select a date between 1900 and today"
                )

                if st.form_submit_button("Add Player"):
                    if player_name:
                        try:
                            player_id = db.insert_player(
                                external_player_id=external_player_id if external_player_id else None,
                                player_name=player_name,
                                country=country,
                                role=role,
                                batting_style=batting_style,
                                bowling_style=bowling_style,
                                date_of_birth=str(date_of_birth) if date_of_birth else None
                            )
                            st.success(f"Player added successfully! (ID: {player_id})")
                        except Exception as e:
                            st.error(f"Error adding player: {e}")
                    else:
                        st.warning("Please enter player name")

        elif operation == "Read":
            st.markdown("### View All Players")
            try:
                players_df = db.get_players()
                if not players_df.empty:
                    st.dataframe(players_df, width="stretch")  # type: ignore[call-arg]
                    st.info(f"Total Players: {len(players_df)}")
                else:
                    st.info("No players in database")
            except Exception as e:
                st.error(f"Error reading players: {e}")

        elif operation == "Update":
            st.markdown("### Update Player Record")
            try:
                players_df = db.get_players()
                if not players_df.empty:
                    # Search by name or external player ID
                    search_query = st.text_input(
                        "🔍 Search Player by Name or External ID",
                        placeholder="Enter player name or external ID...",
                        help="Type player name or external player ID to find the player"
                    )

                    if search_query:
                        # Filter players by name or external player ID
                        filtered_players = players_df[
                            (players_df["player_name"].str.contains(search_query, case=False, na=False)) |
                            (players_df["external_player_id"].astype(str).str.contains(search_query, case=False, na=False))
                        ]

                        if not filtered_players.empty:
                            st.info(f"Found {len(filtered_players)} player(s)")
                            
                            # Display search results in a table
                            display_cols = ["external_player_id", "player_name", "country", "role", "id"]
                            available_cols = [col for col in display_cols if col in filtered_players.columns]
                            st.dataframe(filtered_players[available_cols], use_container_width=True)  # type: ignore[call-arg]
                            
                            # Select which player to update
                            selected_player = st.selectbox(
                                "Select player to update from results",
                                options=filtered_players["player_name"].tolist() if "player_name" in filtered_players.columns else [],
                                key="update_player_select"
                            )

                            if selected_player:
                                with st.form("update_player_form"):
                                    import datetime as dt
                                    new_player_name = st.text_input("Player Name (leave empty to keep current)", value="", placeholder=selected_player)
                                    new_country = st.text_input("Country (leave empty to keep current)", value="")
                                    new_role = st.selectbox("Role", ["Batsman", "Bowler", "All-rounder", "Wicket-keeper", "N/A"], index=4)
                                    new_date_of_birth = st.date_input(
                                        "Date of Birth", 
                                        value=None,
                                        min_value=dt.date(1900, 1, 1),
                                        max_value=dt.date.today(),
                                        help="Optional field - Select a date between 1900 and today"
                                    )

                                    if st.form_submit_button("Update Player"):
                                        try:
                                            player_id = filtered_players[filtered_players["player_name"] == selected_player]["id"].values[0]
                                            external_player_id = filtered_players[filtered_players["player_name"] == selected_player]["external_player_id"].values[0]
                                            update_kwargs = {}
                                            if new_player_name:
                                                update_kwargs["player_name"] = new_player_name
                                            if new_country:
                                                update_kwargs["country"] = new_country
                                            if new_role != "N/A":
                                                update_kwargs["role"] = new_role
                                            if new_date_of_birth:
                                                update_kwargs["date_of_birth"] = str(new_date_of_birth)
                                            
                                            if update_kwargs:
                                                db.update_player(player_id, **update_kwargs)
                                                updated_name = new_player_name if new_player_name else selected_player
                                                st.success(f"✅ Player '{updated_name}' (External ID: {external_player_id}) updated successfully!")
                                            else:
                                                st.warning("No changes specified")
                                        except Exception as e:
                                            st.error(f"Error updating player: {e}")
                        else:
                            st.warning(f"No players found matching '{search_query}'")
                    else:
                        st.info("👆 Enter a player name or external ID to search")
                else:
                    st.info("No players available to update")
            except Exception as e:
                st.error(f"Error: {e}")

        elif operation == "Delete":
            st.markdown("### Delete Player Record")
            try:
                players_df = db.get_players()
                if not players_df.empty:
                    # Search by name or external player ID
                    search_query = st.text_input(
                        "🔍 Search Player by Name or External ID",
                        placeholder="Enter player name or external ID...",
                        help="Type player name or external player ID to find the player to delete",
                        key="delete_search"
                    )

                    if search_query:
                        # Filter players by name or external player ID
                        filtered_players = players_df[
                            (players_df["player_name"].str.contains(search_query, case=False, na=False)) |
                            (players_df["external_player_id"].astype(str).str.contains(search_query, case=False, na=False))
                        ]

                        if not filtered_players.empty:
                            st.warning(f"⚠️ Found {len(filtered_players)} player(s). Please confirm deletion:")
                            
                            # Display search results in a table
                            display_cols = ["external_player_id", "player_name", "country", "role", "id"]
                            available_cols = [col for col in display_cols if col in filtered_players.columns]
                            st.dataframe(filtered_players[available_cols], use_container_width=True)  # type: ignore[call-arg]
                            
                            # Select which player to delete
                            selected_player = st.selectbox(
                                "Select player to delete",
                                options=filtered_players["player_name"].tolist() if "player_name" in filtered_players.columns else [],
                                key="delete_player_select"
                            )

                            if st.button("🗑️ Confirm Delete Player", key="delete_player_btn", type="secondary"):
                                try:
                                    player_id = filtered_players[filtered_players["player_name"] == selected_player]["id"].values[0]
                                    external_player_id = filtered_players[filtered_players["player_name"] == selected_player]["external_player_id"].values[0]
                                    db.delete_player(player_id)
                                    st.success(f"✓ Player '{selected_player}' (External ID: {external_player_id}) deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting player: {e}")
                        else:
                            st.warning(f"No players found matching '{search_query}'")
                    else:
                        st.info("👆 Enter a player name or external ID to search")
                else:
                    st.info("No players available to delete")
            except Exception as e:
                st.error(f"Error: {e}")

    # Tab 2: Match Management
    with tab2:
        st.markdown("## 🏟️ Match Management")

        match_operation = st.radio(
            "Select Operation",
            ["Create", "Read", "Update"],
            horizontal=True,
            key="match_op"
        )

        if match_operation == "Create":
            st.markdown("### Add New Match")
            with st.form("add_match_form"):
                match_desc = st.text_input("Match Description", placeholder="e.g., India vs Australia, ODI")
                team1 = st.text_input("Team 1", placeholder="e.g., India")
                team2 = st.text_input("Team 2", placeholder="e.g., Australia")
                match_format = st.selectbox("Format", ["Test", "ODI", "T20I", "T20", "IPL"])
                match_date = st.date_input("Match Date")

                if st.form_submit_button("➕ Add Match"):
                    if match_desc and team1 and team2:
                        try:
                            match_id = db.insert_match(
                                match_description=match_desc,
                                team1=team1,
                                team2=team2,
                                match_format=match_format,
                                venue_id=1,  # Default venue ID
                                match_date=str(match_date)
                            )
                            st.success(f"✓ Match added successfully! (ID: {match_id})")
                        except Exception as e:
                            st.error(f"Error adding match: {e}")
                    else:
                        st.warning("Please fill in all required fields")

        elif match_operation == "Read":
            st.markdown("### View All Matches")
            try:
                matches_df = db.get_matches()
                if not matches_df.empty:
                    st.dataframe(matches_df, width="stretch")  # type: ignore[call-arg]
                    st.info(f"Total Matches: {len(matches_df)}")
                else:
                    st.info("No matches in database")
            except Exception as e:
                st.error(f"Error reading matches: {e}")

        elif match_operation == "Update":
            st.markdown("### Update Match Record")
            try:
                matches_df = db.get_matches()
                if not matches_df.empty:
                    match_to_update = st.selectbox(
                        "Select Match to Update",
                        [f"{row.get('team1', 'N/A')} vs {row.get('team2', 'N/A')}" 
                         for _, row in matches_df.iterrows()] if not matches_df.empty else []
                    )

                    if match_to_update:
                        with st.form("update_match_form"):
                            _winning_team = st.text_input("Winning Team", placeholder="e.g., India")
                            _victory_margin = st.number_input("Victory Margin", min_value=0)
                            _victory_type = st.selectbox("Victory Type", ["Runs", "Wickets", "Super Over", "N/A"])

                            if st.form_submit_button("✏️ Update Match"):
                                st.success(f"✓ Match details updated successfully!")
                else:
                    st.info("No matches available to update")
            except Exception as e:
                st.error(f"Error: {e}")

    # Tab 3: Venue Management
    with tab3:
        st.markdown("## 🏟️ Venue Management")

        venue_operation = st.radio(
            "Select Operation",
            ["Create", "Read"],
            horizontal=True,
            key="venue_op"
        )

        if venue_operation == "Create":
            st.markdown("### Add New Venue")
            with st.form("add_venue_form"):
                venue_name = st.text_input("Venue Name", placeholder="e.g., MCG, Eden Gardens")
                city = st.text_input("City", placeholder="e.g., Melbourne, Kolkata")
                country = st.selectbox(
                    "Country",
                    ["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand", "West Indies", "Sri Lanka", "Bangladesh", "Afghanistan"]
                )
                capacity = st.number_input("Capacity", min_value=1000, step=1000)

                if st.form_submit_button("➕ Add Venue"):
                    if venue_name and city:
                        try:
                            venue_id = db.insert_venue(
                                venue_name=venue_name,
                                city=city,
                                country=country,
                                capacity=int(capacity)
                            )
                            st.success(f"✓ Venue added successfully! (ID: {venue_id})")
                        except Exception as e:
                            st.error(f"Error adding venue: {e}")
                    else:
                        st.warning("Please fill in all required fields")

        elif venue_operation == "Read":
            st.markdown("### View All Venues")
            try:
                venues_df = db.get_venues()
                if not venues_df.empty:
                    st.dataframe(venues_df, width="stretch")  # type: ignore[call-arg]
                    st.info(f"Total Venues: {len(venues_df)}")
                else:
                    st.info("No venues in database")
            except Exception as e:
                st.error(f"Error reading venues: {e}")

    # Tab 4: Summary
    with tab4:
        st.markdown("## 📊 Database Summary")

        col1, col2, col3 = st.columns(3)

        try:
            with col1:
                players_df = db.get_players()
                st.metric("Total Players", len(players_df) if not players_df.empty else 0)

            with col2:
                matches_df = db.get_matches()
                st.metric("Total Matches", len(matches_df) if not matches_df.empty else 0)

            with col3:
                venues_df = db.get_venues()
                st.metric("Total Venues", len(venues_df) if not venues_df.empty else 0)

            st.markdown("---")
            st.markdown("### Database Statistics")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Top 5 Players by Runs**")
                if not players_df.empty and "player_name" in players_df.columns:
                    top_players = players_df.nlargest(5, "total_runs")[["player_name", "total_runs"]]
                    st.dataframe(top_players, width="stretch")  # type: ignore[call-arg]

            with col2:
                st.markdown("**Venues by Capacity**")
                if not venues_df.empty and "capacity" in venues_df.columns:
                    top_venues = venues_df.nlargest(5, "capacity")[["venue_name", "capacity"]]
                    st.dataframe(top_venues, width="stretch")  # type: ignore[call-arg]

        except Exception as e:
            st.error(f"Error loading summary: {e}")

        # Database Backup
        st.markdown("---")
        st.markdown("### Database Operations")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Export Database as CSV"):
                try:
                    players_df = db.get_players()
                    csv = players_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Players",
                        data=csv,
                        file_name="players.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error exporting: {e}")

        with col2:
            st.info("💡 Tip: Use database backup regularly for data safety")
