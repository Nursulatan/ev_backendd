import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

API_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}


def gemini_answer(message: str) -> str:
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)

    if response.status_code != 200:
        # катаны логго түшүр
        print("Gemini API error:", response.text)
        return f"Gemini error: {response.text}"

    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
