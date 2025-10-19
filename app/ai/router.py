# app/ai/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.provider import answer_text          # сенин бар логикаң
from app.assistant.commands import handle_local_command

router = APIRouter(prefix="/ai", tags=["AI"])

class AskIn(BaseModel):
    message: str

@router.post("/ask")
def ai_ask(body: AskIn):
    # 1) Алгач локалдык буйрукпы?
    local = handle_local_command(body.message)
    if local:
        return {"answer": local, "provider": "local"}

    # 2) Болбосо — Gemini'ге өткөрөбүз (сеники иштеп жатат)
    ans = answer_text(body.message)
    return {"answer": ans, "provider": "gemini/local"}
