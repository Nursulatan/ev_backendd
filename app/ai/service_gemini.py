import os
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
)

HEADERS = {"Content-Type": "application/json"}

def ask_gemini(message: str) -> str:
    payload = {"contents": [{"parts": [{"text": message}]}]}  # <-- model ЖОК!
    try:
        # ТЕСТ үчүн лог калтырып тур (Render Logs’тан көрөсүң)
        print("DEBUG URL:", API_URL)
        print("DEBUG PAYLOAD:", payload)

        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
        data = resp.json()

        if resp.status_code == 200:
            return (
                data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "Жооп бош келип жатат 😅")
            )

        err_msg = data.get("error", {}).get("message") or data
        return f"Gemini error {resp.status_code}: {err_msg}"

    except Exception as e:
        return f"Gemini request error: {e}"
