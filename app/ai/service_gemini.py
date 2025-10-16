# app/ai/service_gemini.py
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

API_URL = (
    f"https://generativelanguage.googleapis.com/v1/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}


def ask_gemini(message: str) -> str:
    """
    Gemini'ден жооп алып, тексти кайтарат.
    Ката болсо, кыскача текст кайтарабыз (API 500 кетпесин).
    """
    payload = {"contents": [{"parts": [{"text": message}]}]}

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
    except Exception as e:
        return f"Gemini request error: {e}"

    if resp.status_code != 200:
        # Логго түшсүн деп жана колдонуучуга окуларлык текст
        try:
            return f"Gemini error {resp.status_code}: {resp.json()}"
        except Exception:
            return f"Gemini error {resp.status_code}: {resp.text}"

    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]
