from Cricbuzz.utils.db_connection import get_db_connection

try:
    db = get_db_connection()
    print('db_type:', getattr(db, 'db_type', None))
    print('connection type:', type(db.connection))
    print('has engine:', hasattr(db.connection, 'engine'))
except Exception as e:
    import traceback
    traceback.print_exc()
