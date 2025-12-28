from Cricbuzz.utils.db_connection import DatabaseConnection
print('Creating DatabaseConnection()')
db = DatabaseConnection()
print('db_path ->', db.db_path)
try:
    df = db.get_players()
    print('get_players() rows:', len(df))
except Exception as e:
    print('get_players() error:', e)
