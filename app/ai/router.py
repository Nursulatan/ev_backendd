from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.ai.service_gemini import ask_gemini

router = APIRouter(prefix="/ai", tags=["AI"])

class AskBody(BaseModel):
    message: str

@router.post("/ask")
def ai_ask(body: AskBody):
    """
    Google Gemini'ге суроо жиберип, жооп кайтарат.
    """
    try:
        response = ask_gemini(body.message)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
