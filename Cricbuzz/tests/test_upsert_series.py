import Cricbuzz.utils.mysql_sync as mysql_sync
from datetime import datetime


def test_upsert_series_converts_timestamps(monkeypatch):
    captured = {}
    def fake_execute(engine, sql, params):
        captured['sql'] = sql
        captured['params'] = params
        return 1
    monkeypatch.setattr(mysql_sync, '_execute', fake_execute)

    start_ms = 1700000000000  # some ms timestamp
    end_ms = 1700003600000
    rc = mysql_sync.upsert_series({}, 'S1', 'Series One', 'T20', start_ms, end_ms)
    assert rc == 1
    params = captured['params']
    # params[3] and params[4] should be datetime objects (or None)
    assert isinstance(params[3], datetime)
    assert isinstance(params[4], datetime)


def test_upsert_series_sql_has_coalesce(monkeypatch):
    def fake_execute(engine, sql, params):
        assert 'COALESCE(VALUES(series_type), series_type)' in sql
        assert 'COALESCE(VALUES(start_date), start_date)' in sql
        assert 'COALESCE(VALUES(end_date), end_date)' in sql
        return 1
    monkeypatch.setattr(mysql_sync, '_execute', fake_execute)

    rc = mysql_sync.upsert_series({}, 'S2', 'Series Two')
    assert rc == 1
