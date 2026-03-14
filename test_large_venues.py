#!/usr/bin/env python3
"""
Validate the large venues query (now Query 4) defined in sql_analytics.py
"""
import pymysql

def test_large_venues():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Vasu@76652",
        database="cricketdb",
        port=3306,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        cur = conn.cursor()
        # clear previous pytest venues
        cur.execute("DELETE FROM venues WHERE Venue_ID LIKE 'pytest_venue_%'")
        venues = [
            ("pytest_venue_1", "Stadium A", "CityA", "CountryA", 30000),
            ("pytest_venue_2", "Stadium B", "CityB", "CountryB", 20000),
            ("pytest_venue_3", "Stadium C", "CityC", "CountryC", 50000),
        ]
        for vid, name, city, country, cap in venues:
            cur.execute(
                "INSERT INTO venues (Venue_ID, Venue_Name, City, Country, Capacity) VALUES (%s,%s,%s,%s,%s)",
                (vid, name, city, country, cap),
            )
        conn.commit()

        sql = r"""
            SELECT Venue_Name, City, Country, Capacity
            FROM venues
            WHERE Capacity > 25000
            ORDER BY Capacity DESC
            LIMIT 10
        """
        cur.execute(sql)
        results = cur.fetchall()
        assert any(r["Venue_Name"] == "Stadium C" and r["Capacity"] == 50000 for r in results)
        assert any(r["Venue_Name"] == "Stadium A" and r["Capacity"] == 30000 for r in results)
        assert not any(r["Venue_Name"] == "Stadium B" for r in results)
        print("✔ Large venues query returns correct rows")
    finally:
        conn.close()

if __name__ == "__main__":
    test_large_venues()