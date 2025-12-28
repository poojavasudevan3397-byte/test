#!/usr/bin/env python3
"""Test MySQL functions for player data synchronization."""
import sys
import os
from typing import Any, Dict

# Add the cricbuzz_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cricbuzz_app'))

# Import after path is set
from utils.mysql_sync import create_mysql_schema, get_pymysql  # type: ignore[reportMissingImports]

# Test getting pymysql
print("Testing get_pymysql()...")
try:
    pm: Any = get_pymysql()  # type: ignore[reportUnknownVariableType]
    print(f"✓ get_pymysql() returned: {pm}")
except Exception as e:
    print(f"✗ get_pymysql() failed: {e}")

# Test create_mysql_schema
print("\nTesting create_mysql_schema()...")
mysql_secrets: Dict[str, Any] = {
    "host": "localhost",
    "user": "root",
    "password": "Vasu@76652",
    "database": "cricketdb",
    "port": 3306,
}

try:
    create_mysql_schema(mysql_secrets)  # type: ignore[reportUnknownVariableType]
    print("✓ create_mysql_schema() succeeded!")
except Exception as e:
    print(f"✗ create_mysql_schema() failed: {e}")
    import traceback
    traceback.print_exc()
