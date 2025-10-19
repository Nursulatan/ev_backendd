# app/ai/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from .service_gemini import ask_gemini_for_json
import logging

logger = logging.getLogger("ev-backend.ai")
router = APIRouter()

class AskIn(BaseModel):
    text: str
    lang: str = "ky"
    name: str = "Алиса"

@router.post("/handle")
def handle_ai(body: AskIn):
    # Build a prompt that instructs Gemini to return JSON with 'speech' and optional 'command'
    # 'command' should be an object like {"action":"lights","params":{"state":"on"}}
    prompt = f"""
You are an in-car voice assistant called {body.name}. The user speaks in {body.lang}. 
Analyze the user's utterance and return ONLY a JSON object (no extra text, no backticks) in the following format:
{{ "speech": "<reply text the assistant should say in same language>", "command": <command object or null> }}

The "command" object should be either null or like:
{{ "action": "lights", "params": {{ "state": "on" }} }}

User utterance: \"{body.text}\"

Respond with the JSON only.
"""

    res = ask_gemini_for_json(prompt)
    if not res.get("ok"):
        # return fallback text so client can TTS something
        return {"ok": False, "speech": f"AI error: {res.get('error') or 'unknown'}", "command": None}

    parsed = res.get("json")
    if parsed:
        # ensure keys present
        speech = parsed.get("speech") or parsed.get("answer") or ""
        command = parsed.get("command")
        return {"ok": True, "speech": speech, "command": command}
    else:
        # no JSON parsed — fallback to raw text
        raw = res.get("raw", "")
        # use raw as speech
        return {"ok": True, "speech": raw, "command": None}
