import requests
import psycopg2
from datetime import datetime

# USGS 地震データ取得URL
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson"

# PostgreSQL接続情報
DB_CONFIG = {
    "dbname": "earthpulse_db",
    "user": "postgres",
    "password": "hnuc",
    "host": "localhost",
    "port": 5432
}

def insert_earthquake(conn, feature):
    with conn.cursor() as cur:
        lon = feature["geometry"]["coordinates"][0]
        lat = feature["geometry"]["coordinates"][1]
        mag = feature["properties"]["mag"]
        place = feature["properties"]["place"]
        timestamp = datetime.utcfromtimestamp(feature["properties"]["time"] / 1000)

        cur.execute("""
            INSERT INTO earthquake_data (longitude, latitude , mag, place, timestamp)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (lon, lat, mag, place, timestamp))

def main():
    response = requests.get(URL)
    data = response.json()

    with psycopg2.connect(**DB_CONFIG) as conn:
        for feature in data["features"]:
            insert_earthquake(conn, feature)
        conn.commit()

if __name__ == "__main__":
    main()
