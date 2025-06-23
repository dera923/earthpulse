import csv
import requests
from datetime import datetime, timezone
import asyncpg
import asyncio

CSV_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/viirs_snpp_nrt/North_America/VIIRS_SNPP_NRT_North_America_24h.csv"

DB_CONFIG = {
    "user": "postgres",
    "password": "hnuc",  # 必要に応じて変更
    "database": "earthpulse_db",
    "host": "127.0.0.1",
    "port": "5432",
}

async def fetch_and_store():
    """NASA火災データを取得してDBに格納する非同期関数"""
    response = requests.get(CSV_URL, timeout=30)
    response.raise_for_status()

    lines = response.text.splitlines()
    reader = csv.DictReader(lines)

    conn = await asyncpg.connect(**DB_CONFIG)

    count = 0
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
            datetime.now(timezone.utc)
            )
            count += 1
        except Exception as e:
            print(f"Error inserting row: {e}")

    await conn.close()
    return count

def fetch_nasa_fire_data():
    """同期的な呼び出し用のラッパー関数"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 既にイベントループが実行中の場合は非同期タスクとして処理
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, fetch_and_store())
                return future.result()
        else:
            return asyncio.run(fetch_and_store())
    except Exception as e:
        print(f"Error in fetch_nasa_fire_data: {e}")
        return 0

if __name__ == "__main__":
    # 直接実行時のみasyncio.runを呼び出す
    result = asyncio.run(fetch_and_store())
    print(f"Stored {result} fire data records")
