import os
import requests

class GeminiClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY environment variable is missing.")
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"

    def generate(self, prompt: str) -> str:
        body = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            r = requests.post(self.url, json=body)
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

_client = None

def get_gemini():
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client

def ask_gemini(prompt: str) -> str:
    return get_gemini().generate(prompt)
