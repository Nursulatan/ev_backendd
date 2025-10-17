# test_gemini.py
import os, requests, json

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL   = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip().replace("models/","").replace("model/","").replace(":latest","")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
payload = {"contents": [{"parts": [{"text": "Салам Gemini, кандайсың?"}]}]}

print("URL:", URL)
if not API_KEY:
    print("ERROR: GEMINI_API_KEY is empty")
    raise SystemExit(1)

resp = requests.post(URL, headers={"Content-Type":"application/json"}, json=payload, timeout=30)
print("HTTP:", resp.status_code)
print("RAW:", resp.text[:800], "..." if len(resp.text) > 800 else "")
if resp.status_code != 200:
    raise SystemExit(1)

data = resp.json()
try:
    txt = data["candidates"][0]["content"]["parts"][0]["text"]
    print("ANSWER:", txt)
except Exception as e:
    print("PARSE ERROR:", e)
    print("DATA:", json.dumps(data, ensure_ascii=False)[:800])
