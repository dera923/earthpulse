from pydantic import BaseModel
import requests

class InferRequest(BaseModel):
    event: str

class InferResponse(BaseModel):
    event: str
    hypothesis_ja: str
    hypothesis_en: str

def infer(req: InferRequest):
    # 日本語プロンプト
    prompt_ja = f"""
あなたはプロフェッショナルな日本語レポーターです。
次の通信障害イベントについて、発生原因として考えられる仮説を提示してください。
背景にある自然災害・国際状況・社会的要因などを考慮し、
日本語で分かりやすく5つ程度に必ず箇条書きでまとめてください。

【絶対条件】
・出力はすべて日本語で、英語は一切使わないでください。
・可能な限り具体的かつ現実的な仮説にしてください。

イベント：
{req.event}
"""

    # 英語プロンプト
    prompt_en = f"""
You are a professional analyst.
For the following communication disruption event, hypothesize possible causes, considering natural disasters, international situations, and social factors.
Respond in clear English and use bullet points.

Event:
{req.event}
"""

    # --- 日本語で推論 ---
    response_ja = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt_ja, "stream": False}
    )

    # --- 英語で推論 ---
    response_en = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt_en, "stream": False}
    )

    # --- 応答のパース ---
    result_ja = response_ja.json() if response_ja.status_code == 200 else {}
    result_en = response_en.json() if response_en.status_code == 200 else {}

    return {
        "event": req.event,
        "hypothesis_ja": result_ja.get("response", "日本語の応答なし"),
        "hypothesis_en": result_en.get("response", "No English response")
    }
