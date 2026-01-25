import pymysql
import json

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Vasu@76652',
    database='cricketdb',
    charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# Check a player with NULL fields
cur.execute('''
    SELECT id, external_player_id, player_name, meta, country, role, date_of_birth
    FROM players 
    WHERE player_name IN ('Yaseen Valli', 'Ruan Terblanche', 'Kyle Jacobs')
    LIMIT 3
''')

for row in cur.fetchall():
    print(f"Player: {row['player_name']} (ID {row['external_player_id']})")
    print(f"Current fields: country={row['country']}, role={row['role']}, dob={row['date_of_birth']}")
    if row['meta']:
        try:
            meta = json.loads(row['meta'])
            print(f"Meta keys: {list(meta.keys())}")
            print(f"Meta sample: {str(meta)[:300]}")
        except:
            print(f"Meta: {row['meta'][:200]}")
    else:
        print("Meta: NULL")
    print()

conn.close()
