import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# кокус .env'ге models/... деп жазылып калса да тазалап коёбуз
_raw_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
GEMINI_MODEL = _raw_model.replace("models/", "").replace("model/", "").replace(":latest", "")

API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    payload = {
        "contents": [
            {"parts": [{"text": message}]}
        ]
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
    except Exception as e:
        return f"Gemini request error: {e}"

    # HTTP ката болсо — текст менен кайтарабыз
    if resp.status_code != 200:
        # Диагностика үчүн толук текст
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