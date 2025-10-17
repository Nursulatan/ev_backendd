# app/ai/service_gemini.py
import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
_raw_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
# .env'ге "models/gemini-1.5-flash[:latest]" болуп кетсе тазалап коёбуз
GEMINI_MODEL = _raw_model.replace("models/", "").replace("model/", "").replace(":latest", "")

API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY is missing."

    payload = {"contents": [{"parts": [{"text": message}]}]}
    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=25)
        # HTTP non-200 болсо – толук текстти кайтарып, кайсы жерде ката экенин көрөбүз
        if resp.status_code != 200:
            return f"Gemini error {resp.status_code}: {resp.text}"
        data = resp.json()
        text = (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
        ).strip()
        return text or "Жооп бош келди."
    except requests.exceptions.RequestException as e:
        return f"Gemini request error: {e}"
    except Exception as e:
        return f"Gemini parse error: {e}"
