# app/ai/router.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from openai import OpenAI
import httpx

from app.config import settings
# эгер эндпоинт админ JWT талап кылса:
# from app.deps import require_admin  # сенде бар деп билем

router = APIRouter(prefix="/ai", tags=["ai"])

class AskBody(BaseModel):
    message: str

def get_openai_client() -> OpenAI:
    # ПРОКСИ КЕРЕК ЭМЕС болсо – жөнөкөй:
    if settings.OPENAI_BASE_URL:
        return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    return OpenAI(api_key=settings.OPENAI_API_KEY)

    # Эгер чынында прокси керектелсе, мисалы:
    # proxy_url = "http://user:pass@host:port"
    # http_client = httpx.Client(proxies=proxy_url, timeout=30.0)
    # return OpenAI(api_key=settings.OPENAI_API_KEY, http_client=http_client, base_url=settings.OPENAI_BASE_URL or None)

@router.post("/ask")
async def ai_ask(body: AskBody):  # , user=Depends(require_admin))  # токен талап кылса, кош
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY орнотулган эмес")

    try:
        client = get_openai_client()
        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Сен жардамчысың. Кыргызча кыска, так жооп бер."},
                {"role": "user", "content": body.message},
            ],
            temperature=0.2,
        )
        answer = resp.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        # Render логдо көрүнүшү үчүн:
        raise HTTPException(status_code=500, detail=f"AI error: {e}")
