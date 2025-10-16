import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
API_VERSION = "v1"                 # МУРУН: v1beta -> Азыр: v1
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
URL = f"https://generativelanguage.googleapis.com/{API_VERSION}/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}

def gemini_answer(message: str) -> str:
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
    }
    r = requests.post(URL, headers=HEADERS, json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    # Жоопту чыгаруу (v1 форматы)
    return data["candidates"][0]["content"]["parts"][0]["text"]
