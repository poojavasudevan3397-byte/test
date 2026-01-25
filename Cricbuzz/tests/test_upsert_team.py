import Cricbuzz.utils.mysql_sync as mysql_sync


def test_upsert_team_includes_country(monkeypatch):
    captured = {}
    def fake_execute(engine, sql, params):
        captured['sql'] = sql
        captured['params'] = params
        return 1
    monkeypatch.setattr(mysql_sync, '_execute', fake_execute)

    rc = mysql_sync.upsert_team({}, 'T1', 'Team One', 'India')
    assert rc == 1
    params = captured['params']
    assert params[0] == 'T1'
    assert params[1] == 'Team One'
    assert params[2] == 'India'


def test_upsert_team_sql_has_coalesce(monkeypatch):
    def fake_execute(engine, sql, params):
        assert 'COALESCE(VALUES(country), country)' in sql
        return 1
    monkeypatch.setattr(mysql_sync, '_execute', fake_execute)

    rc = mysql_sync.upsert_team({}, 'T2', 'Team Two')
    assert rc == 1
