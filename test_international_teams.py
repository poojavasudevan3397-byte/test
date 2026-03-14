import requests
import json

url = 'https://cricbuzz-cricket.p.rapidapi.com/teams/v1/international'
headers = {
    'x-rapidapi-key': '40a5651741msh35d147acca2336fp15cf57jsn1e8cb31efe5b',
    'x-rapidapi-host': 'cricbuzz-cricket.p.rapidapi.com'
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    data = response.json()
    
    # Show structure for first 10 teams
    teams = data.get('teams', [])
    print(f'Total teams: {len(teams)}\n')
    
    for i, team in enumerate(teams[:10]):
        team_id = team.get('id')
        team_name = team.get('name')
        country_name = team.get('countryName')
        country = team.get('country')
        
        print(f'Team {i+1}:')
        print(f'  ID: {team_id}')
        print(f'  Name: {team_name}')
        print(f'  countryName: {country_name}')
        print(f'  country: {country}')
        print()
    
    # Count teams with/without country
    with_country = sum(1 for t in teams if t.get('countryName') or t.get('country'))
    without_country = len(teams) - with_country
    print(f'Summary:')
    print(f'  Teams with country: {with_country}')
    print(f'  Teams without country: {without_country}')
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
