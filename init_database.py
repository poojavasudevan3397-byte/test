"""
Initialize MySQL database schema for Cricbuzz application
This script creates all necessary tables if they don't exist
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.mysql_sync import create_mysql_schema

# MySQL credentials from secrets
mysql_secrets = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306
}

def init_database():
    """Initialize the database schema"""
    try:
        print("Initializing MySQL database schema...")
        create_mysql_schema(mysql_secrets)
        print("✅ Database schema initialized successfully!")
        print("The following tables have been created/verified:")
        print("  - series")
        print("  - teams")
        print("  - players")
        print("  - venues")
        print("  - matches")
        print("  - innings")
        print("  - batting_stats")
        print("  - bowling_stats")
        print("  - batting_partnerships")
        print("  - toss_details")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
