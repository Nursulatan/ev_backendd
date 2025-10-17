# test_gemini.py
import os
import json
import requests

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
URL     = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def main():
    if not API_KEY:
        print("ERROR: env GEMINI_API_KEY is empty")
        return

    payload = {"contents": [{"parts": [{"text": "Салам Gemini, кандайсың?"}]}]}
    try:
        resp = requests.post(URL, headers={"Content-Type": "application/json"}, json=payload, timeout=30)
    except Exception as e:
        print("REQUEST ERROR:", e)
        return

    print("HTTP:", resp.status_code)
    # Чийки жооптун алгачкы бөлүгүн көрсөтөбүз
    raw = resp.text
    print("RAW:", raw[:800], "..." if len(raw) > 800 else "")

    if resp.status_code != 200:
        print("ERROR BODY (non-200):", raw)
        return

    # JSON парсинг
    try:
        data = resp.json()
    except Exception as e:
        print("JSON PARSE ERROR:", e)
        return

    # Күтүлгөн текстти сууруп көрөбүз
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        print("\nANSWER:", text)
    except Exception as e:
        print("PARSE STRUCTURE ERROR:", e)
        print("DATA:", json.dumps(data, ensure_ascii=False)[:800])

if __name__ == "__main__":
    main()
