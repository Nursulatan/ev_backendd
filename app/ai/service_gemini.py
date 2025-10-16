# app/ai/service_gemini.py
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# .env/GEMINI_MODEL "gemini-1.5-flash" болсо да болот, "models/gemini-1.5-flash" болсо да болот
_gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
if not _gemini_model.startswith("models/"):
    _gemini_model = f"models/{_gemini_model}"

BASE_URL = "https://generativelanguage.googleapis.com/v1"
API_URL = f"{BASE_URL}/{_gemini_model}:generateContent"

HEADERS = {
    "Content-Type": "application/json",
    # ачкычты query-string'ке эмес, заголовокко беребиз
    "x-goog-api-key": GEMINI_API_KEY,
}

def ask_gemini(message: str) -> str:
    """
    Текст суроо берет, текст жооп алат.
    """
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": message}
                ]
            }
        ]
        # кааласаң, кошсоң болот:
        # ,"generationConfig": {"temperature": 0.8}
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=25)
        if resp.status_code != 200:
            return f"Gemini error {resp.status_code}: {resp.text}"

        data = resp.json()
        # жооптун текстин сууруп алабыз
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        return text or "Пустой ответ от Gemini 😕"
    except Exception as e:
        return f"Gemini request error: {e}"