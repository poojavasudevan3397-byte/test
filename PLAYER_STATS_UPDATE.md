# Player Statistics Page - Complete MySQL Integration

## Overview
The `pages/player_stats.py` file has been completely rewritten to display comprehensive cricket player analytics using MySQL database queries instead of sample data.

## Key Features

### Tab 1: 🏏 All Batsmen Statistics
- Queries `batting_agg` table (1859+ records)
- Sortable by: Total Runs, Batting Average, Strike Rate, Innings Played
- Searchable by player name
- Adjustable limit (5-100 batsmen)
- Display columns: Rank, Player, Total Runs, Innings, Average, Strike Rate

### Tab 2: 🎯 All Bowlers Statistics
- Queries `bowling_agg` table (1223+ records)
- Sortable by: Wickets Taken, Bowling Average, Economy Rate
- Searchable by bowler name
- Adjustable limit (5-100 bowlers)
- Display columns: Rank, Player, Wickets, Average, Economy Rate

### Tab 3: 🔀 Format Breakdown (2025)
- Format selection: Test, ODI, T20I
- Stat type toggle: Batting or Bowling
- Queries `batting_agg_format_2025` or `bowling_agg_format_2025`
- Top 30 performers per format
- Format-specific aggregated statistics

### Tab 4: 👥 Batting Partnerships
- Queries `best_batting_partnerships_2025` table (249+ records)
- Sortable by average partnership runs (highest first)
- Display columns: Rank, Partnership, Total Partnerships, Avg Runs, Highest, 50+ Runs, Success %

### Tab 5: 📈 Consistent Performers
- Queries `batting_agg` with innings grouped performance
- Shows players with most innings played (high-volume performers)
- Display columns: Rank, Player, Innings, Average Runs
- Helpful for identifying most consistent/experienced batsmen

### Database Summary Section
- Metrics display: Total Batsmen, Total Bowlers, Total Partnerships, 2025 Format Stats
- Live counts from MySQL with proper error handling

## Technical Implementation

### Database Connection
- Uses `get_db_connection()` from `utils/db_connection.py`
- Accesses `db.connection` directly for `pd.read_sql()` queries
- All queries wrapped in try-except blocks with user-friendly error messages

### Query Patterns
All queries follow this pattern:
```python
query = "SELECT ... FROM table WHERE ... ORDER BY ... LIMIT ..."
df = pd.read_sql(query, conn)
# Process and display
```

### Error Handling
- Query failures show error messages truncated to 100 characters
- Missing tables fall back gracefully with exception handling
- Metric summary has nested try-except for optional tables

### Data Processing
- DataFrames renamed for clean display
- Rank column auto-generated (1, 2, 3, ...)
- String columns sanitized with `.str.contains()` for case-insensitive search
- All numeric values formatted with proper precision

## Database Tables Used

| Table | Records | Purpose |
|-------|---------|---------|
| `batting_agg` | 1859 | Overall batting statistics |
| `bowling_agg` | 1223 | Overall bowling statistics |
| `batting_agg_format_2025` | 2207 | Format-specific batting (2025) |
| `bowling_agg_format_2025` | 1424 | Format-specific bowling (2025) |
| `best_batting_partnerships_2025` | 249 | Partnership analysis |

## Streamlit Features Used
- Multi-tab interface with 5 tabs
- `st.selectbox()` for dropdowns
- `st.slider()` for numeric input
- `st.radio()` for toggle options
- `st.text_input()` for search
- `st.dataframe()` for formatted table display
- `st.metric()` for summary statistics
- `st.error()`, `st.warning()`, `st.info()`, `st.success()` for feedback

## Code Quality
- Pylance suppressed via `cast(Any, st)` for Streamlit dynamic members
- Type hints for clarity
- Follows existing code patterns in project
- Comprehensive docstring at module level

## Testing
✓ Import test: `from pages.player_stats import show` - **PASSED**
✓ No syntax errors
✓ All database queries formatted correctly

## Future Enhancements
1. Add caching with `@st.cache_data` for frequent queries
2. Add export functionality (CSV/Excel)
3. Add player-specific deep-dive page with innings-by-innings history
4. Add historical trending charts
5. Add venue-specific performance analysis
