from fastapi import APIRouter
from pydantic import BaseModel
from .service_gemini import ask_gemini

router = APIRouter(prefix="/ai", tags=["AI"])

class AskIn(BaseModel):
    message: str

@router.post("/ask")
def ai_ask(body: AskIn):
    answer = ask_gemini(body.message)
    return {"answer": answer, "provider": "gemini"}
