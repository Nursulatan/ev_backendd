# app/ai/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.ai import ask_gemini   # <-- Мына ушундай

router = APIRouter(prefix="/ai", tags=["AI"])

class AskBody(BaseModel):
    message: str

@router.post("/ask")
def ai_ask(body: AskBody):
    answer = ask_gemini(body.message)
    return {"answer": answer, "provider": "gemini"}
