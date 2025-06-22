from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/map", response_class=HTMLResponse)
async def map_ui(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT title, source, lat, lon, pub_date
            FROM news_data
            ORDER BY pub_date DESC
            LIMIT 100
            """
        )
    data = [dict(row) for row in rows]
    return templates.TemplateResponse("map.html", {"request": request, "data": data})
