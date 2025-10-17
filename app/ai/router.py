# app/ai/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.ai.provider import answer_text

router = APIRouter(prefix="/ai", tags=["AI"])

class AskIn(BaseModel):
    message: str

@router.post("/ask")
def ai_ask(body: AskIn):
    ans = answer_text(body.message)
    # провайдерди логдоо үчүн кошумча талаа жок, керек болсо айлана-чөйрөдөн окуп берсең болот
    return {"answer": ans, "provider": "gemini/local"}
