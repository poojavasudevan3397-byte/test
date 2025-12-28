#!/usr/bin/env python3

print("Testing pymysql import...")
pymysql_module = None

try:
    import pymysql as pymysql_module
    print(f"✓ SUCCESS: pymysql_module = {pymysql_module}")
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    pymysql_module = None

print(f"Final pymysql_module value: {pymysql_module}")
