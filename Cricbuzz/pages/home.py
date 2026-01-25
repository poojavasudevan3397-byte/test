# """
# Home Page - Project Overview and Navigation
# """

# import streamlit as st
# from typing import Any, cast

# # Help Pylance by treating Streamlit as Any for dynamic members like `markdown`
# st = cast(Any, st)


# def show():
#     """Display home page"""
#     st.markdown("<h1 class='page-title'>🏏 Welcome to Cricbuzz LiveStats</h1>", unsafe_allow_html=True)
    
#     st.markdown(
#         """
#         Welcome to the Cricket Analytics Dashboard!
        
#         Use the sidebar menu to navigate through different sections.
#         """
#     )



"""
Home Page – Project Overview and Navigation
This page does NOT access the database.
"""

import streamlit as st
from typing import Any, cast

# Treat Streamlit dynamic members as Any (Pylance safety)
st = cast(Any, st)


def show() -> None:
    """Display home page"""

    # Optional: emoji removed to avoid font issues
    # st.markdown("<h1 class='page-title'>🏏 Welcome to Cricbuzz LiveStats</h1>", unsafe_allow_html=True)
    st.markdown("<h1 class='page-title'>Welcome to Cricbuzz LiveStats</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        ### Cricket Analytics Dashboard

        This application provides:
        - **Real-time match updates**
        - **Detailed player statistics**
        - **SQL-driven analytics**
        - **MySQL-backed persistent storage**

        Use the **sidebar menu** to navigate through the different sections.
        """
    )

    st.markdown("---")

    st.markdown(
        """
        #### Available Sections
        - **Live Matches**: View live, upcoming, and recent matches  
        - **Player Statistics**: Analyze batting and bowling performance  
        - **SQL Analytics**: Run predefined analytical SQL queries  
        - **CRUD Operations**: Manage core data manually  
        - **Database Diagnostics**: Verify database health and consistency
        """
    )

    st.info(
        "Tip: Ensure your database connection is configured correctly "
        "before using Live Matches or Analytics pages."
    )
