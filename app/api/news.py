from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import pytz
import feedparser
import requests

router = APIRouter()

# 🚧 PostgreSQL接続（app/main.py 側で pool を app.state.pool に設定しておくこと）

class NewsRequest(BaseModel):
    source: str  # 例: "cnn", "nhk", "reuters", "nasa-fire"

# ✅ 地理情報つきニュース一覧（適宜拡張可能）
SOURCE_FEEDS = {
    "cnn": "http://rss.cnn.com/rss/edition.rss",
    "nhk": "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "reuters": "http://feeds.reuters.com/reuters/JPTopNews",
    "nasa-fire": "https://firms.modaps.eosdis.nasa.gov/geojson/c6/VIIRS_I_Global_24h.geojson",  # 🔥 正式GeoJSON
}

# ✅ 位置情報（仮）
SOURCE_LOCATIONS = {
    "cnn": (38.9072, -77.0369),       # Washington D.C.
    "nhk":(35.6812, 139.7671),       # Tokyo
    "reuters": (51.5074, -0.1278),    # London
    "nasa-fire": (34.2000, -118.2000) # NASA JPL 付近（仮）
}


@router.post("/news")
async def fetch_news(request: Request, body: NewsRequest):
    source = body.source.lower()

    if source not in SOURCE_FEEDS:
        raise HTTPException(status_code=400, detail="Unsupported source")

    url = SOURCE_FEEDS[source]
    location = SOURCE_LOCATIONS.get(source, (0.0, 0.0))
    items = []

    try:
        if source == "nasa-fire":
            # ✅ NASA-FIRMS専用処理（GeoJSON）
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            geojson = response.json()

            for feature in geojson.get("features", []):
                coords = feature["geometry"]["coordinates"]
                props = feature["properties"]
                title = f"🔥 Fire: {props.get('acq_date', 'unknown')} {props.get('acq_time', '')}"
                items.append({
                    "title": title,
                    "source": source,
                    "lat": coords[1],
                    "lon": coords[0],
                    "pub_date": datetime.utcnow()
                })

        else:
            # ✅ 通常のRSS処理（feedparser）
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                items.append({
                    "title": entry.title,
                    "source": source,
                    "lat": location[0],
                    "lon": location[1],
                    "pub_date": datetime.utcnow()
                })

        # ✅ PostgreSQLへ保存
        async with request.app.state.pool.acquire() as conn:
            for item in items:
                await conn.execute("""
                    INSERT INTO news_data (title, source, lat, lon, pub_date)
                    VALUES ($1, $2, $3, $4, $5)
                """, item["title"], item["source"], item["lat"], item["lon"], item["pub_date"])

        return {"status": "stored", "count": len(items)}

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"NASAデータ取得失敗: {str(e)}") 
