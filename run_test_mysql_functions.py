from cricbuzz_app.utils.mysql_sync import create_mysql_schema, get_pymysql
from typing import Dict, Any

print('Testing get_pymysql()...')
try:
    pm = get_pymysql()
    print('OK get_pymysql returned', getattr(pm, '__name__', pm))
except Exception as e:
    print('FAILED get_pymysql', type(e).__name__, e)

print('\nTesting create_mysql_schema()...')
mysql_secrets: Dict[str, Any] = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Vasu@76652',
    'database': 'cricketdb',
    'port': 3306,
}
try:
    create_mysql_schema(mysql_secrets)
    print('OK create_mysql_schema executed')
except Exception as e:
    print('FAILED create_mysql_schema', type(e).__name__, e)
