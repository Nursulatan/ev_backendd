# app/ai/service_gemini.py
import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("ev-backend.ai")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
_raw_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_MODEL = _raw_model.replace("models/", "").replace("model/", "").replace(":latest", "")

# Use v1 endpoint that supports generateContent for listed models
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
HEADERS = {"Content-Type": "application/json"}

# Helper: ask Gemini with a prompt and return (ok, parsed_json_or_text)
def ask_gemini_for_json(prompt: str, max_output_tokens: int = 512, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Sends prompt to Gemini and tries to parse JSON from the response.
    Returns dict with keys: ok(bool), raw(text), json(dict|None), error(str|None)
    """
    if not GEMINI_API_KEY:
        return {"ok": False, "raw": "", "json": None, "error": "GEMINI_API_KEY not set"}

    payload = {
        "temperature": temperature,
        "candidateCount": 1,
        "maxOutputTokens": max_output_tokens,
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=25)
    except Exception as e:
        logger.exception("Gemini request exception")
        return {"ok": False, "raw": "", "json": None, "error": f"request error: {e}"}

    if resp.status_code != 200:
        logger.warning("Gemini non-200: %s %s", resp.status_code, resp.text)
        return {"ok": False, "raw": resp.text, "json": None, "error": f"HTTP {resp.status_code}"}

    try:
        data = resp.json()
    except Exception as e:
        logger.exception("Gemini resp not json")
        return {"ok": False, "raw": resp.text, "json": None, "error": f"json parse error: {e}"}

    # Try to extract text from candidates -> content -> parts -> text
    try:
        cand = (data.get("candidates") or [])
        text = ""
        if cand:
            text = cand[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            # Some models use "output" or other shape; fallback to raw text
            text = str(data)
    except Exception:
        text = resp.text

    # Try parse JSON inside text (assistant should be instructed to return JSON)
    import json
    try:
        # find first { ... } in text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            sub = text[start:end+1]
            parsed = json.loads(sub)
            return {"ok": True, "raw": text, "json": parsed, "error": None}
    except Exception as e:
        logger.info("Failed to parse JSON from Gemini text: %s", e)

    # fallback: return full text as raw string
    return {"ok": True, "raw": text, "json": None, "error": None}
