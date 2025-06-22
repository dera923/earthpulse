import csv
import requests
from datetime import datetime
import asyncpg
import asyncio

CSV_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/viirs_snpp_nrt/North_America/VIIRS_SNPP_NRT_North_America_24h.csv"

DB_CONFIG = {
    "user": "postgres",
    "password": "",  # 必要に応じて
    "database": "earthpulse_db",
    "host": "localhost",
    "port": "5432",
}

async def fetch_and_store():
    response = requests.get(CSV_URL)
    response.raise_for_status()

    lines = response.text.splitlines()
    reader = csv.DictReader(lines)

    conn = await asyncpg.connect(**DB_CONFIG)

    for row in reader:
        try:
            await conn.execute("""
                INSERT INTO fire_data (latitude, longitude, brightness, scan, track, acq_date, acq_time, satellite, instrument, confidence, version, bright_t31, frp, daynight, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT DO NOTHING
            """, 
            float(row["latitude"]),
            float(row["longitude"]),
            float(row["brightness"]),
            float(row["scan"]),
            float(row["track"]),
            row["acq_date"],
            row["acq_time"],
            row["satellite"],
            row["instrument"],
            row["confidence"],
            row["version"],
            float(row["bright_t31"]),
            float(row["frp"]),
            row["daynight"],
            datetime.utcnow()
            )
        except Exception as e:
            print(f"Error inserting row: {e}")

    await conn.close()

asyncio.run(fetch_and_store())
