import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# НУСКА: v1beta + модель URL'да
BASE_URL = "https://generativelanguage.googleapis.com"
API_VERSION = "v1beta"
API_URL = f"{BASE_URL}/{API_VERSION}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": message}
                ]
            }
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
