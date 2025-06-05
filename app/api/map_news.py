# app/api/map_news.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/map-news")
async def map_news(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT title, lat, lon, source FROM news_data
            WHERE lat IS NOT NULL AND lon IS NOT NULL
            ORDER BY pub_date DESC LIMIT 100
        """)
    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["lon"], row["lat"]],
            },
            "properties": {
                "title": row["title"],
               "source": row["source"],
            }
        })
    return JSONResponse({
        "type": "FeatureCollection",
        "features": features
    }) 
