import sqlite3
import os
import tempfile
import pytest #type: ignore
from pathlib import Path

from Cricbuzz.scripts.clean_players import ROLE_HEADERS


def setup_db(conn):
    cur = conn.cursor()
    cur.execute('''CREATE TABLE players (id INTEGER PRIMARY KEY AUTOINCREMENT, external_player_id TEXT, player_name TEXT, meta TEXT, created_at TEXT)''')
    cur.executemany('INSERT INTO players (external_player_id, player_name, meta, created_at) VALUES (?,?,?,?)', [
        (None, 'BATSMEN', '{}', '2024-01-01'),
        (None, 'Bowler', '{}', '2024-01-02'),
        ('123', 'John Doe', '{}', '2024-01-03'),
    ])
    conn.commit()


def find_candidates_sqlite(conn):
    cur = conn.cursor()
    placeholders = ','.join(['?'] * len(ROLE_HEADERS))
    sql = f"SELECT id, external_player_id, player_name, meta, created_at FROM players WHERE external_player_id IS NULL AND LOWER(TRIM(player_name)) IN ({placeholders})"
    cur.execute(sql, ROLE_HEADERS)
    return cur.fetchall()


def test_find_candidates(tmp_path):
    dbfile = tmp_path / 'test.db'
    conn = sqlite3.connect(str(dbfile))
    try:
        setup_db(conn)
        rows = find_candidates_sqlite(conn)
        assert len(rows) == 2
    finally:
        conn.close()
