from fastapi import FastAPI
from app.api import news
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.api import map
import asyncpg
from app.api import news, map_news  
from fetchers.fetch_usgs_quake import fetch_usgs_quake_data
from fetchers.fetch_nasa_fire_csv import fetch_nasa_fire_data
from datetime import datetime, timezone
from .routers import predict
from fastapi.responses import HTMLResponse
from app.infer import InferRequest, InferResponse, infer
from pydantic import BaseModel
from typing import List
import requests
import csv

app = FastAPI()

app.include_router(news.router)
app.include_router(map_news.router)
app.include_router(map.router)
app.include_router(predict.router)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2テンプレートの準備
templates = Jinja2Templates(directory="app/templates")

# DBプール初期化
@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(
        user="postgres",
        password="hnuc",  # 実パスワードに変更してください
        database="earthpulse_db",
        host="127.0.0.1",
        port="5432"
    )

@app.on_event("shutdown")
async def shutdown():
    await app.state.pool.close()

# 地震データ取得・格納エンドポイント
@app.post("/earthquakes")
async def store_earthquakes():
    """USGSから地震データを取得してDBに格納"""
    features = fetch_usgs_quake_data()
    pool = app.state.pool
    async with pool.acquire() as conn:
        for feature in features:
            coords = feature["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]
            mag = feature["properties"].get("mag", 0.0)
            place = feature["properties"].get("place", "Unknown location")
            time_ms = feature["properties"].get("time")
            if time_ms:
                # UNIX ms → timestamp 変換
                timestamp = datetime.fromtimestamp(time_ms / 1000.0, tz=timezone.utc)
            else:
                timestamp = datetime.now(timezone.utc)

            await conn.execute("""
                INSERT INTO earthquake_data (longitude, latitude, mag, place, timestamp)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, lon, lat, mag, place, timestamp)

    return {"message": "Earthquake data stored successfully.", "count": len(features)}

# 地震データ取得API
@app.get("/earthquakes-data")
async def get_earthquakes_data():
    """フロントエンド用の地震データ取得API"""
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT longitude, latitude, mag, place, timestamp
            FROM earthquake_data
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        result = [
            {
                "longitude": row["longitude"],
                "latitude": row["latitude"],
                "mag": row["mag"],
                "place": row["place"],
                "timestamp": row["timestamp"].isoformat()
            }
            for row in rows
        ]
        return {"features": result}

# NASA火災データ取得・格納エンドポイント
@app.post("/nasa-fires")
async def store_nasa_fires():
    """NASAから火災データを取得してDBに格納"""
    try:
        # 代替URLを使用（MAP_KEY不要）
        csv_url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_7d.csv"
        print(f"火災データ取得中: {csv_url}")
        response = requests.get(csv_url, timeout=30)
        response.raise_for_status()
        print(f"火災データ取得成功: ステータス {response.status_code}")

        lines = response.text.splitlines()
        reader = csv.DictReader(lines)
        
        count = 0
        async with app.state.pool.acquire() as conn:
            for row in reader:
                try:
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
                    print(f"Error inserting fire data row: {e}")

        return {"message": "NASA fire data stored successfully.", "count": count}
    except Exception as e:
        return {"error": f"Failed to fetch NASA fire data: {str(e)}"}, 500

# 火災データ取得API
@app.get("/fires-data")
async def get_fires_data():
    """フロントエンド用の火災データ取得API"""
    try:
        async with app.state.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT latitude, longitude, brightness, confidence, acq_date, acq_time, frp
                FROM fire_data
                ORDER BY timestamp DESC
                LIMIT 500
            """)
            result = [
                {
                    "latitude": row["latitude"],
                    "longitude": row["longitude"],
                    "brightness": row["brightness"],
                    "confidence": row["confidence"],
                    "acq_date": row["acq_date"],
                    "acq_time": row["acq_time"],
                    "frp": row["frp"]
                }
                for row in rows
            ]
            return {"features": result}
    except Exception as e:
        print(f"Error fetching fire data: {e}")
        return {"features": [], "error": "No fire data available yet"}

# Leaflet 地図用テンプレート呼び出し
@app.get("/map-earthquakes", response_class=HTMLResponse)
async def map_earthquakes(request: Request):
    return templates.TemplateResponse("map-earthquakes.html", {"request": request})

@app.get("/fire-map", response_class=HTMLResponse)
async def fire_map(request: Request):
    return templates.TemplateResponse("fire_map.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# 予測関連エンドポイント
@app.post("/infer", response_model=InferResponse)
async def infer_endpoint(request: InferRequest):
    return infer(request)

@app.get("/")
async def root():
    return {"message": "EarthPulse API is running"}

# 健康チェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
