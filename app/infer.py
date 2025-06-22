from pydantic import BaseModel
from datetime import datetime
from app.utils.predict_to_dag import add_predict_node
from app.utils.parse_causal_pairs import extract_causal_pairs
from app.utils.predict_to_dag import add_predict_node, add_predict_edge


class InferRequest(BaseModel):
    event: str

class InferResponse(BaseModel):
    event: str
    hypothesis_ja: str
    hypothesis_en: str

def infer(req: InferRequest) -> InferResponse:
    # === プロンプト構築（仮） ===
    prompt = f"""
    以下のイベントに関して、通信障害などの事象と関連しそうな因果関係を仮説として述べてください。
    背景にある自然災害・国際状況・社会的要因などを踏まえて、LLM視点で考察してください。

    【出力は必ず日本語でお願いします】

    イベント：
    {req.event}
    """

    # === 仮説（ダミー実装。将来 Ollama 等と連携） ===
    hypothesis_ja = "仮説：北海道の地震と国際ケーブルの障害が重なった可能性があります。"
    hypothesis_en = "Hypothesis: A possible disruption caused by both an earthquake in Hokkaido and damage to international cables."

    # === DAGノード登録 ===
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    add_predict_node("LLM仮説", hypothesis_ja, confidence=0.6, timestamp=timestamp)
    
    # 因果ペア抽出 → エッジ追加
    pairs = extract_causal_pairs(hypothesis_ja)
    for cause, effect in pairs:
        add_predict_edge("LLM仮説", f"{cause} → {effect}", confidence=0.6)

    # === レスポンスとして返却 ===
    return InferResponse(
        event=req.event,
        hypothesis_ja=hypothesis_ja,
        hypothesis_en=hypothesis_en
    )
