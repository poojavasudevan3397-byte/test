# Streamlit Cricket Dashboard (demo)

This small demo app shows Real-time match updates (Live/Upcoming/Recent) using the RapidAPI cricbuzz endpoint and allows viewing a match scorecard by clicking a button.

Files created:
- `streamlit_cricket_app.py` — main Streamlit demo app.

Run (PowerShell):

```powershell
# from d:\test
# activate your venv first if needed
python -m pip install streamlit requests
streamlit run d:\test\streamlit_cricket_app.py
```

Notes:
- The demo embeds an API key in the script for convenience; move it to `st.secrets` or environment variables for production.
- Player stats / SQL / CRUD pages are placeholders — I implemented the Real-time match updates view as requested.
