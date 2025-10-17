import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}


def ask_gemini(message: str) -> str:
    """
    Gemini API'ге суроо жөнөтөт жана жоопту кайтарат.
    Эгер API бош же ката кайтарса — жооптун чыныгы текстин көрсөтөт.
    """
    if not GEMINI_API_KEY:
        return "Gemini request error: Missing GEMINI_API_KEY"

    payload = {
        "contents": [{"parts": [{"text": message}]}]
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    except Exception as e:
        return f"Gemini request error: {e}"

    # Эгер сервер жооп берсе, бирок 200 эмес болсо
    if resp.status_code != 200:
        return f"Gemini error {resp.status_code}: {resp.text[:300]}"

    # Эми жоопту JSON кылып окуйбуз
    try:
        data = resp.json()
    except Exception as e:
        # Эгер JSON парсинг иштебесе — демек бош же текст жооп
        return f"Gemini request error: JSON parse failed ({e}) | raw={resp.text[:300]}"

    # Кандидаттардын ичинен текстти алуу
    try:
        return (
            data["candidates"][0]["content"]["parts"][0]["text"]
        )
    except Exception as e:
        # Эгер күтүлгөн структура болбосо
        return f"Gemini response parse error: {e} | raw={json.dumps(data)[:300]}"
