import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

BASE_URL = "https://generativelanguage.googleapis.com"
API_URL = f"{BASE_URL}/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    # ЭЧ КАНДАЙ "model" ТАЛААСЫ ЖОК!
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
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
