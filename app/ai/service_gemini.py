import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Туура endpoint: v1beta жана модель URL'да гана, payload'да ЖОК!
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    # payload'да "model" ТАПТЫК ЖОК
    payload = {"contents": [{"parts": [{"text": message}]}]}
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        data = resp.json()

        if resp.status_code == 200:
            # жоопту коопсуз алып чыгуу
            return (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "Жооп бош келип жатат 😅")
            )

        # Ката болсо — Google’дун билдирүүсүн түз эле чыгаралы
        err_msg = data.get("error", {}).get("message") or data
        return f"Gemini error {resp.status_code}: {err_msg}"

    except Exception as e:
        return f"Gemini request error: {e}"
