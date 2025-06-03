from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 地図HTMLページ
@router.get("/map", response_class=HTMLResponse)
async def show_map(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})

# GeoJSONデータAPI
@router.get("/earthquakes", response_class=JSONResponse)
async def get_earthquakes(request: Request):
    pool = request.app.state.pool
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT longitude, latitude, mag, place
            FROM earthquake_data
            ORDER BY timestamp DESC
            LIMIT 100
        """)
    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]],
            },
            "properties": {
                "mag": row["mag"],
                "place": row["place"]
            }
        })
    return {"type": "FeatureCollection", "features": features}
