"""
Test script to verify the Cricbuzz database setup and table structure
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Cricbuzz'))

from Cricbuzz.utils.db_connection import get_db_connection

def test_database_connection():
    """Test database connection and schema"""
    print("=" * 60)
    print("Testing Cricbuzz Database Setup")
    print("=" * 60)
    
    # MySQL credentials
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306
    }
    
    try:
        # Test connection
        print("\n1. Testing MySQL connection...")
        db = get_db_connection(mysql_secrets)
        print("   ✅ Successfully connected to MySQL")
        
        # Test each required table
        required_tables = [
            "series",
            "teams",
            "players",
            "venues",
            "matches",
            "innings",
            "batting_stats",
            "bowling_stats",
            "batting_partnerships"
        ]
        
        print("\n2. Checking required tables...")
        for table in required_tables:
            try:
                result = db.execute_query(f"SELECT COUNT(*) as cnt FROM {table}")
                count = int(result.iloc[0, 0]) if len(result) > 0 else 0
                print(f"   ✅ {table:25} - {count:6} records")
            except Exception as e:
                print(f"   ❌ {table:25} - ERROR: {str(e)[:50]}")
                return False
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Database is ready.")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nMake sure:")
        print("  1. MySQL server is running")
        print("  2. Database 'cricketdb' exists")
        print("  3. User 'root' exists with password 'Vasu@76652'")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
