import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Кээ бир моделдер v1 эмес, v1beta2 астында гана жеткиликтүү.
API_URL = f"https://generativelanguage.googleapis.com/v1beta2/models:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    payload = {
        "model": f"models/{GEMINI_MODEL}",
        "contents": [{"parts": [{"text": message}]}],
    }
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Жооп бош келди 😅")
            )
        return f"Gemini error {resp.status_code}: {resp.text}"
    except Exception as e:
        return f"Gemini request error: {e}"
