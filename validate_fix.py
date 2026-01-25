"""
Quick validation that the fix resolves the batting_stats error
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.db_connection import get_db_connection

def validate_fix():
    """Validate that batting_stats query works"""
    print("\nValidating batting_stats query fix...")
    print("-" * 60)
    
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306
    }
    
    try:
        db = get_db_connection(mysql_secrets)
        
        # Run the exact query that was failing
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
            LIMIT 5
        """
        
        df = db.execute_query(query)
        
        if len(df) > 0:
            print("✅ Query executed successfully!")
            print(f"\nTop 5 batsmen by total runs:")
            print(df.to_string())
            print("\n" + "=" * 60)
            print("✅ Fix validated! No 'no such table: batting_stats' error")
            print("=" * 60)
            return True
        else:
            print("⚠️  Query returned no results (empty batting_stats)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = validate_fix()
    sys.exit(0 if success else 1)
