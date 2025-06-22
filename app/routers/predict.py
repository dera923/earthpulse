from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
from geopy.geocoders import Nominatim

router = APIRouter()

# geopy 初期化
geolocator = Nominatim(user_agent="earthpulse_predict_app")

class NewsItem(BaseModel):
    title: str
    published: str
    place: str

@router.post("/predict")
async def predict_news(items: List[NewsItem], request: Request):
    results = []

    async with request.app.state.pool.acquire() as conn:
        for item in items:
            # 仮の予測ロジック
            if "Tokyo" in item.place:
                prediction = "通信遮断の可能性：高"
                confidence = 0.85
            else:
                prediction = "影響小"
                confidence = 0.3

            # Geocoding → ここで lat, lon を得する
            location = geolocator.geocode(item.place)
            if location:
                print(f"[Geocode Success] {item.place} → lat: {location.latitude}, lon: {location.longitude}")
                lat = location.latitude
                lon = location.longitude
            else:
                print(f"[Geocode Failed] {item.place} → fallback to 0.0, 0.0")
                lat, lon = 0.0, 0.0  # fallback

            # DBに保存
            try:
                result = await conn.execute("""
                    INSERT INTO predict_logs (place, prediction, confidence, lat, lon)
                    VALUES ($1, $2, $3, $4, $5)
                """, item.place, prediction, confidence, lat, lon)
                print("INSERT result:", result)
            except Exception as e:
                print("INSERT ERROR:", e)

            # 結果用配列に追加
            results.append({
                "place": item.place,
                "title": item.title,
                "prediction": prediction,
                "confidence": confidence,
                "coordinates": {"lat": lat, "lon": lon},
            })

    return {"predictions": results}

@router.get("/predict-data")
async def get_predict_data(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT place, prediction, confidence, lat, lon, timestamp
            FROM predict_logs
            ORDER BY timestamp DESC
            LIMIT 100
        """)

    result = [
        {
            "place": row["place"],
            "prediction": row["prediction"],
            "confidence": row["confidence"],
            "coordinates": {"lat": row["lat"], "lon": row["lon"]},
            "timestamp": row["timestamp"].isoformat(),
        }
        for row in rows
    ]

    return {"predictions": result}
