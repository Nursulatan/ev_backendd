from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

# OpenAI SDK (new-style)
try:
    from openai import OpenAI
except Exception as e:
    OpenAI = None  # импорт маселеси болсо, 503 кайтарабыз

# Админ коргоосу (бар болсо колдонобуз, болбосо no-op)
def _noop_dep():
    return None

try:
    # Сизде app/deps.py ичинде require_admin бар (get_current_user ж.б.)
    from app.deps import require_admin  # type: ignore
except Exception:
    require_admin = _noop_dep  # коргоосуз иштей берет

router = APIRouter(prefix="/ai", tags=["ai"])

DEFAULT_SYSTEM_PROMPT = (
    "Сен EV Voice Assistant үчүн жардамчысың. Жоопту кыска, так жана "
    "Кыргызча (же колдонуучу тилине жараша) бер."
)

class AskIn(BaseModel):
    message: str
    system: Optional[str] = None
    # history же башка талааларды кийин кошсоңор болот

class AskOut(BaseModel):
    answer: str

@router.post("/ask", response_model=AskOut)
async def ai_ask(body: AskIn, _user=Depends(require_admin)):
    """
    OpenAI'га жөнөкөй суроо/жооп эндпойнту.
    Эгер require_admin бар болсо, JWT менен корголот.
    """
    if OpenAI is None:
        raise HTTPException(status_code=503, detail="OpenAI SDK импорт боло алган жок")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY орнотулган эмес")

    client = OpenAI(api_key=api_key)

    system = body.system or DEFAULT_SYSTEM_PROMPT
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": body.message},
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",        # жеткиликтүү, арзан, ылдам
            messages=messages,
            temperature=0.3,
        )
        answer = resp.choices[0].message.content or ""
        return AskOut(answer=answer.strip())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"OpenAI error: {e}")