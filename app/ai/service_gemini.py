# app/ai/service_gemini.py
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
# ЭМНЕ КАТА БОЛЧУ? -> v1beta жана МОДЕЛЬде "models/" префикси ЖОК!
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip() \
    .replace("models/", "").replace("model/", "").replace(":latest", "")

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    """Gemini'ге жөнөкөй суроо жөнөтөт. non-200 болсо толук текстти кайтарат (диагностика үчүн)."""
    if not GEMINI_API_KEY:
        return "Gemini error: API key is empty (GEMINI_API_KEY)."

    payload = {"contents": [{"parts": [{"text": message}]}]}

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    except Exception as e:
        return f"Gemini request error: {e}"

    if resp.status_code != 200:
        # Бул жер — сенде “Gemini error 404/400 ...” чыккан болсо, ТОЛУК raw текстти көрөсүң
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
