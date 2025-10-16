# app/ai/router.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.deps import require_admin  # сендеги токен текшергич
from app.ai.service import ask

router = APIRouter(prefix="/ai", tags=["ai"])

class AskBody(BaseModel):
    message: str

@router.post("/ask", dependencies=[Depends(require_admin)])
def ai_ask(body: AskBody):
    try:
        answer = ask(body.message)
        return {"answer": answer}
    except Exception as e:
        # Кыска жана түшүнүктүү 500
        raise HTTPException(status_code=500, detail=str(e))
