#!/usr/bin/env python3
import sys
sys.path.insert(0, 'cricbuzz_app')

print("Importing mysql_sync...")
from utils import mysql_sync

print(f"pymysql_module in mysql_sync: {mysql_sync.pymysql_module}")
print(f"create_engine in mysql_sync: {mysql_sync.create_engine}")
