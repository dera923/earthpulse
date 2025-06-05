import requests
import asyncio
import asyncpg
from datetime import datetime

# 🔐 DB接続設定（必要に応じてパスワード変更）
DB_CONFIG = {
    "user": "postgres",
    "password": "hnuc",  # ←ここ注意
    "database": "earthpulse_db",
    "host": "localhost",
    "port": 5432,
}

# 🌍 NASA FIRMS - カナダ限定 GeoJSON URL
FIRMS_CANADA_URL = "https://firms.modaps.eosdis.nasa.gov/geojson/c6/VIIRS_I_Canada_24h.geojson"

async def fetch_and_store_fires():
    try:
        response = requests.get(FIRMS_CANADA_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print("🔥 データ取得失敗:", str(e))
        return

    features = data.get("features", [])
    print(f"🔥 {len(features)} 件の fire point を挿します")

    if not features:
        return

    conn = await asyncpg.connect(**DB_CONFIG)

    for feature in features:
        try:
            coords = feature["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]
            timestamp = feature["properties"].get("acq_date", "") + " " + feature["properties"].get("acq_time", "0000")
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H%M")

            await conn.execute("""
                INSERT INTO fire_data (latitude, longitude, timestamp)
                VALUES ($1, $2, $3)
            """, lat, lon, dt)
        except Exception as e:
            print("🔥 parse error:", e)

    await conn.close()

if __name__ == "__main__":
    asyncio.run(fetch_and_store_fires())
