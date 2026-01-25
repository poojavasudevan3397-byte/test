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

print("=== RECENTLY INSERTED PLAYERS ===\n")
# Check the players mentioned as having NULL fields
cur.execute('''
    SELECT id, external_player_id, player_name, country, role, date_of_birth, created_at
    FROM players 
    WHERE player_name IN ('Yaseen Valli', 'Ruan Terblanche', 'Kyle Jacobs')
    ORDER BY created_at DESC
''')

for row in cur.fetchall():
    print(f"Player: {row['player_name']} (ID {row['external_player_id']})")
    print(f"  Country: {row['country']}")
    print(f"  Role: {row['role']}")
    print(f"  DOB: {row['date_of_birth']}")
    print(f"  Created: {row['created_at']}\n")

print("\n=== PLAYERS TABLE STATS ===\n")
# Overall stats
cur.execute('SELECT COUNT(*) as total FROM players')
total = cur.fetchone()['total']

cur.execute('SELECT COUNT(*) as with_country FROM players WHERE country IS NOT NULL')
with_country = cur.fetchone()['with_country']

cur.execute('SELECT COUNT(*) as with_role FROM players WHERE role IS NOT NULL')
with_role = cur.fetchone()['with_role']

cur.execute('SELECT COUNT(*) as with_dob FROM players WHERE date_of_birth IS NOT NULL')
with_dob = cur.fetchone()['with_dob']

print(f"Total players: {total}")
print(f"With country: {with_country} ({100*with_country/total:.1f}%)")
print(f"With role: {with_role} ({100*with_role/total:.1f}%)")
print(f"With DOB: {with_dob} ({100*with_dob/total:.1f}%)")

print("\n=== RECENT PLAYERS (Last 10) ===\n")
cur.execute('''
    SELECT id, external_player_id, player_name, country, role, date_of_birth, created_at
    FROM players 
    ORDER BY created_at DESC
    LIMIT 10
''')

for row in cur.fetchall():
    country_str = row['country'] if row['country'] else 'NULL'
    role_str = row['role'] if row['role'] else 'NULL'
    dob_str = row['date_of_birth'] if row['date_of_birth'] else 'NULL'
    print(f"{row['player_name']:25} | {country_str:15} | {role_str:15} | {dob_str:12} | {row['created_at']}")

conn.close()
