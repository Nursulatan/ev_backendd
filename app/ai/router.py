# app/ai/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from openai import OpenAI
import os

from app.deps import require_admin  # токен текшерүүң кандай болсо ошол

router = APIRouter(prefix="/ai", tags=["ai"])

class AskBody(BaseModel):
    message: str

# ЭЧ кандай proxies/extra параметр бербейбиз!
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # кааласаң ENV’ге кой

@router.post("/ask", dependencies=[Depends(require_admin)])
def ai_ask(body: AskBody):
    if not client.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY орнотулган эмес")

    try:
        # Responses API (v1) – жөнөкөй жолу
        resp = client.responses.create(
            model=MODEL,
            input=body.message,
        )
        # Жооптун жөнөкөй тексти:
        answer = getattr(resp, "output_text", None) or "no output"
        return {"answer": answer}

    except Exception as e:
        # Диагностика үчүн кыска, 500 кайтарабыз
        raise HTTPException(status_code=500, detail=str(e))
