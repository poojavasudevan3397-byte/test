import pymysql
import pandas as pd

conn = pymysql.connect(host='localhost', user='root', password='Vasu@76652', database='cricketdb', cursorclass=pymysql.cursors.DictCursor)
df = pd.read_sql("SELECT team_id FROM cricketdb.teams LIMIT 50", conn)
print(df)
print('\nDTYPES:')
print(df.dtypes)
print('\nTYPE COUNTS:')
print(df['team_id'].apply(type).value_counts())
print('\nUNIQUE SAMPLE:')
print(df['team_id'].unique()[:50])
conn.close()
