from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pytz
import feedparser

router = APIRouter()

# 📦 PostgreSQL接続（app/main.py 側で pool を app.state.pool に設定しておくこと）
from fastapi import Request

class NewsRequest(BaseModel):
    source: str  # 例: "cnn", "nhk", "reuters", "nasa-fire"

# 🌍 地理情報つきソース一覧（必要に応じて増やせる）
SOURCE_FEEDS = {
    "cnn": "http://rss.cnn.com/rss/edition.rss",
    "nhk": "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "reuters": "http://feeds.reuters.com/reuters/JPTopNews",
    "nasa-fire": "https://firms.modaps.eosdis.nasa.gov/active_fire/c6/c6_rss.xml"
}

# 🌐 緯度・経度の例（必要に応じて解析）
SOURCE_LOCATIONS = {
    "cnn": (38.9072, -77.0369),       # Washington D.C.
    "nhk": (35.6812, 39.7671),       # Tokyo
    "reuters": (51.5074, -0.1278),    # London
    "nasa-fire": (34.2000, -118.2000) # NASA JPL近辺（仮）
}

@router.post("/news")
async def fetch_news(request: Request, body: NewsRequest):
    source = body.source.lower()

    if source not in SOURCE_FEEDS:
        raise HTTPException(status_code=400, detail="Unsupported source")

    feed_url = SOURCE_FEEDS[source]
    location = SOURCE_LOCATIONS.get(source, (0.0, 0.0))

    # ⏱ タイムゾーン統一
    jst = pytz.timezone("Asia/Tokyo")

    # RSS取得
    parsed = feedparser.parse(feed_url)

    if not parsed.entries:
        return {"status": "ok", "source": source, "count": 0}

    count = 0
    async with request.app.state.pool.acquire() as conn:
        for entry in parsed.entries[:10]:
            title = entry.get("title", "No Title")
            link = entry.get("link", "")
            pub_date_str = entry.get("published", "") or entry.get("updated", "")
            try:
                pub_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(jst)
                pub_date = pub_date.replace(tzinfo=None)  # PostgreSQL側が timezone-naive のため
            except Exception:
                pub_date = datetime.now(jst).replace(tzinfo=None)

            lat, lon = location

            await conn.execute("""
                INSERT INTO news_data (source, title, link, lat, lon, pub_date)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, source, title, link, lat, lon, pub_date)
            count += 1

    return {"status": "ok", "source": source, "count": count}
