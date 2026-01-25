#!/usr/bin/env python3
"""
Test the India Players Query
"""
import pymysql

def test_india_players_query():
    """Test the India players query"""
    
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Vasu@76652",
        database="cricketdb",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    
    try:
        cur = connection.cursor()
        
        # The query from sql_analytics.py
        sql = """
            SELECT 
                player_name as 'Full Name',
                role as 'Playing Role',
                COALESCE(
                    JSON_EXTRACT(meta, '$.battingStyle'),
                    'N/A'
                ) as 'Batting Style',
                COALESCE(
                    JSON_EXTRACT(meta, '$.bowlingStyle'),
                    'N/A'
                ) as 'Bowling Style',
                external_player_id as 'External ID'
            FROM players
            WHERE country = 'India'
            ORDER BY player_name ASC;
        """
        
        print("\n" + "=" * 100)
        print("ALL PLAYERS WHO REPRESENT INDIA")
        print("=" * 100 + "\n")
        
        cur.execute(sql)
        results = cur.fetchall()
        
        if results:
            # Print header
            if results:
                headers = list(results[0].keys())
                print(f"{'Full Name':<30} {'Playing Role':<15} {'Batting Style':<15} {'Bowling Style':<15} {'External ID':<15}")
                print("-" * 100)
                
                # Print rows
                for row in results:
                    full_name = str(row['Full Name']) if row['Full Name'] else 'N/A'
                    role = str(row['Playing Role']) if row['Playing Role'] else 'N/A'
                    bat_style = str(row['Batting Style']).replace('"', '') if row['Batting Style'] else 'N/A'
                    bowl_style = str(row['Bowling Style']).replace('"', '') if row['Bowling Style'] else 'N/A'
                    ext_id = str(row['External ID']) if row['External ID'] else 'N/A'
                    print(f"{full_name:<30} {role:<15} {bat_style:<15} {bowl_style:<15} {ext_id:<15}")
                
                print("\n" + "=" * 100)
                print(f"Total Players from India: {len(results)}")
                print("=" * 100 + "\n")
        else:
            print("No players found for India")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        connection.close()

if __name__ == "__main__":
    test_india_players_query()
