# app/ai/service_gemini.py
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

API_URL = f"https://generativelanguage.googleapis.com/v1beta/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    # ЭСКЕРТҮҮ: body'де model ЖОК!
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}]
            }
        ]
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        data = resp.json()
        if resp.status_code == 200:
            # коопсуз парсинг
            return (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "Жооп бош келди 🙂")
            )
        # Google ката текстин кайтарып коёбуз
        return f"Gemini error {resp.status_code}: {data.get('error', {}).get('message', resp.text)}"
    except Exception as e:
        return f"Gemini request error: {e}"
