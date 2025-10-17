# app/ai/service_gemini.py
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

_raw_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
# .env’де кокус "models/..." же ":latest" болуп келсе да тазалайбыз
GEMINI_MODEL = (
    _raw_model.replace("models/", "")
              .replace("model/", "")
              .replace(":latest", "")
)

# v1beta ЭМЕС, v1 колдонообуз
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    payload = {"contents": [{"parts": [{"text": message}]}]}
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
    except Exception as e:
        return f"Gemini request error: {e}"

    if resp.status_code != 200:
        # Диагностика үчүн толук текстин беребиз
        return f"Gemini error {resp.status_code}: {resp.text}"

    try:
        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        )
        return text.strip() or "Жооп бош келди."
    except Exception as e:
        return f"Gemini parse error: {e}"
