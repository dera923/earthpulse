import csv
import requests
from datetime import datetime, timezone
import asyncpg
import asyncio

# 最新のNASA FIRMS APIエンドポイント（MAP_KEY必要）
# 注意: 実際の使用前にMAP_KEYを取得してください: https://firms.modaps.eosdis.nasa.gov/api/map_key/
MAP_KEY = "your_map_key_here"  # ← 実際のMAP_KEYに変更してください
CSV_URL = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/VIIRS_SNPP_NRT/world/1"

# 代替URL（MAP_KEY不要の場合）
ALTERNATIVE_URL = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_7d.csv"

DB_CONFIG = {
    "user": "postgres",
    "password": "hnuc",  # 必要に応じて変更
    "database": "earthpulse_db",
    "host": "127.0.0.1",
    "port": "5432",
}

async def fetch_and_store():
    """NASA火災データを取得してDBに格納する非同期関数"""
    
    # まず代替URLを試行
    try:
        print("代替URL(MAP_KEY不要)でデータ取得を試行中...")
        response = requests.get(ALTERNATIVE_URL, timeout=30)
        response.raise_for_status()
        print(f"代替URL成功: ステータス {response.status_code}")
    except Exception as e:
        print(f"代替URL失敗: {e}")
        # MAP_KEYが設定されていない場合はエラー
        if MAP_KEY == "your_map_key_here":
            print("❌ MAP_KEYが設定されていません")
            print("🔑 https://firms.modaps.eosdis.nasa.gov/api/map_key/ でMAP_KEYを取得してください")
            return 0
        
        # MAP_KEY版を試行
        try:
            print("MAP_KEY版でデータ取得を試行中...")
            response = requests.get(CSV_URL, timeout=30)
            response.raise_for_status()
            print(f"MAP_KEY版成功: ステータス {response.status_code}")
        except Exception as e2:
            print(f"MAP_KEY版も失敗: {e2}")
            return 0

    lines = response.text.splitlines()
    reader = csv.DictReader(lines)

    conn = await asyncpg.connect(**DB_CONFIG)

    count = 0
    for row in reader:
        try:
            # 新しいVIIRSフォーマットに対応
            await conn.execute("""
                INSERT INTO fire_data (latitude, longitude, brightness, scan, track, acq_date, acq_time, satellite, instrument, confidence, version, bright_t31, frp, daynight, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT DO NOTHING
            """, 
            float(row["latitude"]),
            float(row["longitude"]),
            float(row.get("bright_ti4", row.get("brightness", 0))),  # 新旧フォーマット対応
            float(row["scan"]),
            float(row["track"]),
            row["acq_date"],
            row["acq_time"],
            row["satellite"],
            row["instrument"],
            row["confidence"],
            row.get("version", "2.0NRT"),
            float(row.get("bright_t31", row.get("bright_ti5", 0))),  # 新旧フォーマット対応
            float(row["frp"]),
            row["daynight"],
            datetime.now(timezone.utc)
            )
            count += 1
        except Exception as e:
            print(f"Error inserting row: {e}")
            # デバッグ用：問題のある行を表示
            print(f"Problem row: {dict(list(row.items())[:5])}")

    await conn.close()
    print(f"✅ 火災データ {count} 件をデータベースに格納しました")
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
    print(f"結果: {result} 件の火災データを処理")
