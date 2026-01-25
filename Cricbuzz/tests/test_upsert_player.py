import pytest
import Cricbuzz.utils.mysql_sync as mysql_sync


def test_skip_placeholder_player(monkeypatch, capsys):
    # Ensure _execute is NOT called for placeholder player rows
    def fake_execute(*args, **kwargs):
        raise AssertionError("_execute should not be called for placeholder rows")
    monkeypatch.setattr(mysql_sync, "_execute", fake_execute)

    rc = mysql_sync.upsert_player({}, {"name": "BATSMEN"})
    out = capsys.readouterr().out
    assert "Skipping placeholder player row" in out
    assert rc == 0


def test_upsert_player_calls_execute(monkeypatch):
    called = {}
    def fake_execute(engine_or_secrets, sql, params):
        called['called'] = True
        # validate params contain external id and name
        assert params[0] == '123'
        assert params[1] == 'John'
        return 1

    monkeypatch.setattr(mysql_sync, "_execute", fake_execute)

    rc = mysql_sync.upsert_player({}, {"id": "123", "name": "John"})
    assert rc == 1
    assert called.get('called') is True
