from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# 推論API用の依存モジュール（すでに定義済）
from app.infer import InferRequest, InferResponse, infer

app = FastAPI()

# ==== 🔁 推論エンドポイント ====
@app.post("/infer", response_model=InferResponse)
def infer_endpoint(req: InferRequest):
    return infer(req)


# ==== 🧭 地図UIエンドポイント ====
templates = Jinja2Templates(directory="app/templates")

@app.get("/map", response_class=HTMLResponse)
async def map_ui(request: Request):
    return templates.TemplateResponse("map.html", {"request": request})


# ==== 📁 静的ファイル（CSS/JSなど） ====
app.mount("/static", StaticFiles(directory="app/static"), name="static")
