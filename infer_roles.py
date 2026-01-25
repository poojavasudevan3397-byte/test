"""
Infer and populate player roles from batting/bowling stats using player_name join.
"""

import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Vasu@76652',
    database='cricketdb',
    charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

print('Finding players with NULL role that appear in stats...')

# Get all players with NULL role
cur.execute("""
    SELECT DISTINCT p.id, p.external_player_id, p.player_name
    FROM players p
    WHERE p.role IS NULL
    AND p.external_player_id IS NOT NULL
    ORDER BY p.player_name
    LIMIT 100
""")
candidates = cur.fetchall()

print(f'Found {len(candidates)} players\n')

updated = 0

for p in candidates:
    pid = p['id']
    player_name = p['player_name']
    
    # Check if in batting stats
    cur.execute("""
        SELECT COUNT(*) as cnt FROM batting_stats 
        WHERE player_name = %s
    """, (player_name,))
    bat_count = cur.fetchone()['cnt'] or 0
    
    # Check if in bowling stats
    cur.execute("""
        SELECT COUNT(*) as cnt FROM bowling_stats 
        WHERE player_name = %s
    """, (player_name,))
    bowl_count = cur.fetchone()['cnt'] or 0
    
    # Infer role
    if bat_count == 0 and bowl_count == 0:
        continue
    
    if bat_count > 0 and bowl_count > 0:
        role = 'All-rounder'
    elif bat_count > 0:
        role = 'Batsman'
    else:
        role = 'Bowler'
    
    print(f"{player_name:30} | Batting: {bat_count:3} | Bowling: {bowl_count:3} | Role: {role}")
    
    # Update
    cur.execute("""
        UPDATE players 
        SET role = %s 
        WHERE id = %s
    """, (role, pid))
    conn.commit()
    updated += 1

conn.close()

print(f'\nUpdated: {updated} players')
