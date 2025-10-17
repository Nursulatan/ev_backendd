import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# v1beta керек — көп аккаунттарда дал ушул иштейт
API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    """
    Колдонуучудан келген текстти Gemini'ге жөнөтүп, текст жоопту кайтарат.
    """
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
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
    except Exception as e:
        return f"Gemini request error: {e}"

    # HTTP ката болсо — текст катары кайтаруу
    if resp.status_code != 200:
        try:
            err = resp.json()
        except Exception:
            err = resp.text
        return f"Gemini error {resp.status_code}: {err}"

    # Ийгиликтүү жоопту парсинг
    try:
        data = resp.json()
        # candidates[0].content.parts[0].text схемасы
        return (
            data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
                .strip()
            or "Жооп бош келди."
        )
    except Exception as e:
        return f"Gemini parse error: {e}"
