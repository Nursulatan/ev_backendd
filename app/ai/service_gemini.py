import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Set it in Render → Environment.")

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

def ask_gemini(message: str) -> str:
    """
    Жөнөкөй текст суроо-жооп.
    """
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        # Кандидаттан текстти сууруп алабыз
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.HTTPError as e:
        # Google API’нин түшүнүктүүрөөк ката текстин чыгаруу
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Gemini error: {e} | detail={detail}") from e
