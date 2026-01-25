import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='Vasu@76652',
    database='cricketdb',
    charset='utf8mb4'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

# Check batting_stats columns
print("=== batting_stats columns ===")
cur.execute("DESCRIBE batting_stats")
for row in cur.fetchall():
    print(f"{row['Field']:25} {row['Type']:20} {row['Null']:5} {row['Key']}")

print("\n=== bowling_stats columns ===")
cur.execute("DESCRIBE bowling_stats")
for row in cur.fetchall():
    print(f"{row['Field']:25} {row['Type']:20} {row['Null']:5} {row['Key']}")

conn.close()
