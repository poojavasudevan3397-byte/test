import json
from typing import Any, Dict, List, cast # type: ignore
import sys
sys.path.insert(0, r'D:\test\Cricbuzz')
from utils.api_client import normalize_matches
from utils.mysql_sync import (
    create_mysql_schema,
    upsert_match,
    upsert_series,
    upsert_team,
    upsert_venue,
    upsert_innings,
    upsert_batting,
    upsert_bowling,
    upsert_partnerships,
    upsert_player,
)
try:
    from streamlit import secrets
    mysql_secrets: Dict[str, Any] = secrets.get('mysql', {})
except Exception:
    mysql_secrets: Dict[str, Any] = {}

# Default local MySQL credentials (override via Streamlit secrets if available)
if not mysql_secrets:
    mysql_secrets = {
        "host": "localhost",
        "user": "root",
        "password": "Vasu@76652",
        "database": "cricketdb",
        "port": 3306,
    }

p = r'D:\test\Cricbuzz\data\api_responses\live.json'
with open(p,'r',encoding='utf-8') as f:
    data = json.load(f)
matches: List[Dict[str, Any]] = normalize_matches(data)
print('Found', len(matches), 'normalized matches')
if not matches:
    raise SystemExit('no matches')
m: Dict[str, Any] = matches[0]
print('Sample match keys:', [str(k) for k in list(m.keys())[:20]])
print('Using mysql_secrets keys:', [str(k) for k in list(mysql_secrets.keys())])
try:
    create_mysql_schema(mysql_secrets)
    print('schema ensured')

    rc = upsert_match(mysql_secrets, m)
    print(f'upsert_match rc={rc} for match {m.get("matchId", m.get("match_id", m.get("external_match_id")))}')

    # upsert series
    sid = m.get('seriesId') or m.get('series_id') or m.get('external_series_id')
    sname = m.get('seriesName') or m.get('series_name')
    series_type = m.get('seriesType') or m.get('series_type')
    series_start = m.get('seriesStartDt') or m.get('series_start_dt') or m.get('seriesStartDate')
    series_end = m.get('seriesEndDt') or m.get('series_end_dt') or m.get('seriesEndDate')
    if sid and sname:
        s_rc = upsert_series(mysql_secrets, str(sid), sname, series_type, series_start, series_end)
        print(f'upsert_series rc={s_rc} for series {sid} name={sname}')

    # upsert teams
    for team_key, name_key in [('team1_id', 'team1_name'), ('team2_id', 'team2_name'), ('external_team1_id', 'team1_name'), ('external_team2_id', 'team2_name')]:
        team_id = m.get(team_key)
        team_name = m.get(name_key)
        team_obj_key = team_key.replace('_id', '')
        team_obj = m.get(team_obj_key) or {}
        team_country = None
        if isinstance(team_obj, dict):
            team_country = team_obj.get('country') or team_obj.get('teamCountry') or team_obj.get('country_name')
        if team_id and team_name:
            t_rc = upsert_team(mysql_secrets, str(team_id), team_name, team_country)
            print(f'upsert_team rc={t_rc} for team {team_id} name={team_name} country={team_country}')

    # Try fetching team players and upserting them (debug)
    import requests
    for team_key in ['team1_id', 'team2_id', 'external_team1_id', 'external_team2_id']:
        team_id = m.get(team_key)
        if not team_id:
            continue
        try:
            url = f"https://cricbuzz-cricket.p.rapidapi.com/teams/v1/{team_id}/players"
            headers = {
                'x-rapidapi-key': '5ff5c15309msh270be5dd89152b5p1f3d98jsnf270423b3863',
                'x-rapidapi-host': 'cricbuzz-cricket.p.rapidapi.com'
            }
            resp = requests.get(url, headers=headers, timeout=10)
            if not resp.ok:
                print(f"Warning: players API returned {resp.status_code} for team {team_id}: {resp.text[:200]}")
                continue
            try:
                team_data = cast(Dict[str, Any], resp.json())
            except Exception as e:
                print(f"Warning: could not parse players JSON for team {team_id}: {e}")
                continue

            players_raw = cast(
                List[Dict[str, Any]],
                team_data.get('player') or team_data.get('players') or team_data.get('playerList') or team_data.get('playersList') or [],
            )
            print(f"DEBUG: fetched {len(players_raw)} players for team {team_id}")
            for p in players_raw:
                if p:
                    try:
                        player_rc = upsert_player(mysql_secrets, p)
                        print(f"DEBUG: upsert_player rc={player_rc} for player {p.get('name') or p.get('playerName')}")
                    except Exception as insert_err:
                        print(f"Error upserting player {p.get('name') or p.get('playerName')}: {insert_err}")
        except Exception as e:
            print(f'Warning: Could not fetch players for team {team_id}: {e}')

    # upsert venue if info available
    vid = m.get('external_venue_id') or m.get('venue')
    vname = m.get('venue_name') or m.get('venue')
    if vid or vname:
        venue_obj: Dict[str, Any] = {
            'id': vid,
            'ground': vname,
            'city': m.get('venue_city'),
            'country': m.get('venue_country'),
            'timezone': None,
        }
        v_rc = upsert_venue(mysql_secrets, venue_obj)
        print(f'upsert_venue rc={v_rc} for venue {vid} name={vname}')

    # try to fetch full scorecard and upsert innings/batting/bowling/partnerships
    from utils.api_client import get_api_client
    api_client = get_api_client('5ff5c15309msh270be5dd89152b5p1f3d98jsnf270423b3863')
    mid = m.get('matchId') or m.get('match_id') or m.get('external_match_id')
    if mid:
        sc = api_client.get_scorecard(str(mid))
        if sc:
            for inning in sc.get('scorecard', []):
                innid = inning.get('inningsId') or inning.get('inningsid')
                if innid:
                    i_rc = upsert_innings(mysql_secrets, str(mid), inning)
                    print(f'upsert_innings rc={i_rc} for match {mid} innings {innid}')
                    bats = inning.get('batsman', inning.get('batsmen', []))
                    if bats:
                        print('DEBUG: sample bats entry keys:', list(bats[0].keys()) if bats else 'none')
                        print('DEBUG: sample bats[0]:', bats[0] if bats else 'none')
                        b_rc = upsert_batting(mysql_secrets, str(mid), str(innid), bats)
                        print(f'upsert_batting rc={b_rc} for match {mid} innings {innid}')

                        # Fallback: ensure players exist from batting entries
                        for b in bats:
                            player_id = b.get('batId') or b.get('external_player_id') or b.get('id')
                            player_name = b.get('batName') or b.get('name') or b.get('player_name') or b.get('playerName')
                            if player_id or player_name:
                                try:
                                    pr = upsert_player(mysql_secrets, {'id': player_id, 'name': player_name})
                                    print(f'DEBUG: upsert_player (from batting) rc={pr} for player {player_name}')
                                except Exception as e:
                                    print(f'Warning: upsert_player (bat) failed: {e}')
                    bowls = inning.get('bowler', inning.get('bowlers', []))
                    if bowls:
                        print('DEBUG: sample bowls entry keys:', list(bowls[0].keys()) if bowls else 'none')
                        print('DEBUG: sample bowls[0]:', bowls[0] if bowls else 'none')
                        bw_rc = upsert_bowling(mysql_secrets, str(mid), str(innid), bowls)
                        print(f'upsert_bowling rc={bw_rc} for match {mid} innings {innid}')

                        # Fallback: ensure players exist from bowling entries
                        for bw in bowls:
                            player_id = bw.get('bowlId') or bw.get('external_player_id') or bw.get('id')
                            player_name = bw.get('bowlName') or bw.get('name') or bw.get('player_name') or bw.get('playerName')
                            if player_id or player_name:
                                try:
                                    pr = upsert_player(mysql_secrets, {'id': player_id, 'name': player_name})
                                    print(f'DEBUG: upsert_player (from bowling) rc={pr} for player {player_name}')
                                except Exception as e:
                                    print(f'Warning: upsert_player (bowl) failed: {e}')
                    parts = inning.get('partnerships', inning.get('partnership', []))
                    if parts:
                        p_rc = upsert_partnerships(mysql_secrets, str(mid), str(innid), parts)
                        print(f'upsert_partnerships rc={p_rc} for match {mid} innings {innid}')
except Exception as e:
    print('ERROR', e)
    import traceback
    traceback.print_exc()
