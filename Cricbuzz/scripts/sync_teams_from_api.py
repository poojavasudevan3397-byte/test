"""
Sync all international teams from Cricbuzz API and populate countries in teams table.
Usage:
  python scripts/sync_teams_from_api.py --dry-run    # Show teams to sync
  python scripts/sync_teams_from_api.py --apply      # Apply to DB
"""
from typing import Dict, Any
try:
    from streamlit import secrets
    _s = secrets.get('mysql', {}) or {}
    mysql_secrets: Dict[str, Any] = dict(_s)
except Exception:
    mysql_secrets = {}

if not mysql_secrets:
    mysql_secrets = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'cricketdb',
        'port': 3306,
    }

try:
    from streamlit import secrets as st_secrets
    api_key = st_secrets.get('RAPIDAPI_KEY') or st_secrets.get('rapidapi_key')
except Exception:
    api_key = None

import sys
sys.path.insert(0, '.')

# Country mapping for national teams (when API doesn't provide it)
COUNTRY_MAP = {
    'India': 'India',
    'Afghanistan': 'Afghanistan',
    'Ireland': 'Ireland',
    'Pakistan': 'Pakistan',
    'Australia': 'Australia',
    'Sri Lanka': 'Sri Lanka',
    'Bangladesh': 'Bangladesh',
    'England': 'England',
    'West Indies': 'West Indies',
    'South Africa': 'South Africa',
    'Zimbabwe': 'Zimbabwe',
    'New Zealand': 'New Zealand',
    'Malaysia': 'Malaysia',
    'Nepal': 'Nepal',
    'Germany': 'Germany',
    'Namibia': 'Namibia',
    'Denmark': 'Denmark',
    'Singapore': 'Singapore',
    'Papua New Guinea': 'Papua New Guinea',
    'Kuwait': 'Kuwait',
    'Vanuatu': 'Vanuatu',
    'Jersey': 'Jersey',
    'Oman': 'Oman',
    'Fiji': 'Fiji',
    'Italy': 'Italy',
    'Botswana': 'Botswana',
    'Belgium': 'Belgium',
    'Uganda': 'Uganda',
    'Canada': 'Canada',
    'United Arab Emirates': 'United Arab Emirates',
    'Hong Kong, China': 'Hong Kong',
    'Kenya': 'Kenya',
    'United States of America': 'United States',
    'Scotland': 'Scotland',
    'Netherlands': 'Netherlands',
    'Bermuda': 'Bermuda',
    'Iran': 'Iran',
}

import argparse
import pymysql
from Cricbuzz.utils.api_client import get_api_client
from Cricbuzz.utils.mysql_sync import upsert_team

parser = argparse.ArgumentParser()
parser.add_argument('--apply', action='store_true', help='Apply updates to DB')
# Optional CLI overrides for DB credentials
parser.add_argument('--db-host', help='DB host')
parser.add_argument('--db-user', help='DB user')
parser.add_argument('--db-password', help='DB password')
parser.add_argument('--db-name', help='DB name')
parser.add_argument('--db-port', type=int, help='DB port')
# Optional API key override
parser.add_argument('--api-key', help='RapidAPI key')
args = parser.parse_args()

# Apply CLI overrides
if args.db_host:
    mysql_secrets['host'] = args.db_host
if args.db_user:
    mysql_secrets['user'] = args.db_user
if args.db_password is not None:
    mysql_secrets['password'] = args.db_password
if args.db_name:
    mysql_secrets['database'] = args.db_name
if args.db_port:
    mysql_secrets['port'] = args.db_port
if args.api_key:
    api_key = args.api_key

if not api_key:
    print('ERROR: No API key provided. Set RAPIDAPI_KEY in .streamlit/secrets.toml or use --api-key')
    sys.exit(1)

print('Fetching teams from all categories (international, league, domestic, women)...')
try:
    api_client = get_api_client(api_key)
    all_teams = []
    seen_ids = set()
    
    for category, method_name in [
        ('international', 'get_international_teams'),
        ('league', 'get_league_teams'),
        ('domestic', 'get_domestic_teams'),
        ('women', 'get_women_teams'),
    ]:
        try:
            print(f'  Fetching {category} teams...')
            method = getattr(api_client, method_name)
            response = method()
            teams_list = response.get('list', []) or response.get('teams', []) or response.get('data', []) or []
            print(f'    Found {len(teams_list)} {category} teams')
            for team in teams_list:
                team_id = team.get('id') or team.get('teamId')
                if team_id and team_id not in seen_ids:
                    all_teams.append(team)
                    seen_ids.add(team_id)
        except Exception as e:
            print(f'  WARNING: Could not fetch {category} teams: {e}')
    
    teams_list = all_teams
except Exception as e:
    print(f'ERROR: Failed to fetch teams from API: {e}')
    sys.exit(1)
if not teams_list:
    print(f'WARNING: No teams found. Check API response.')
    sys.exit(0)

print(f'\nTotal {len(teams_list)} unique teams from all categories\n')

# Upsert each team
synced = 0
for team in teams_list:
    try:
        team_id = team.get('id') or team.get('teamId')
        team_name = team.get('name') or team.get('teamName')
        country = team.get('country') or team.get('countryName')
        
        # If country is missing, try the country map
        if not country:
            country = COUNTRY_MAP.get(team_name)
        
        if not team_id or not team_name:
            continue
        
        print(f"Team {team_id} ({team_name}): country={country}")
        
        if args.apply:
            try:
                rc = upsert_team(mysql_secrets, str(team_id), team_name, country)
                if rc and rc > 0:
                    synced += 1
            except Exception as e:
                print(f"  WARNING: upsert failed: {e}")
    except Exception as e:
        print(f"  ERROR processing team: {e}")

if args.apply:
    print(f'\nSynced {synced} teams')
else:
    print('\nRun with --apply to sync teams to DB')
