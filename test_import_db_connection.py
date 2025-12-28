import importlib
try:
    m = importlib.import_module('cricbuzz_app.utils.db_connection')
    print('Imported:', m.__name__)
except Exception as e:
    print('Import failed:', e)
