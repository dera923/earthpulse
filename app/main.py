from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api import map
import asyncpg

app = FastAPI()

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2テンプレートの準備
templates = Jinja2Templates(directory="app/templates")

# DBプール初期化
@app.on_event("startup")
async def startup():
    app.state.pool = await asyncpg.create_pool(
        user="postgres",
        password="hnuc",  # ←ここは実パスワードに必ず変更
        database="earthpulse_db",
        host="localhost"
    )

# ルータ読み込み
app.include_router(map.router)
