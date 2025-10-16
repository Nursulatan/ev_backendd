from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from app.config import settings

router = APIRouter(prefix="/ai", tags=["ai"])

class AskBody(BaseModel):
    message: str

@router.post("/ask")
async def ai_ask(body: AskBody):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY орнотулган эмес")

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Сен жардамчысың, кыргызча так жооп бер."},
                {"role": "user", "content": body.message},
            ],
        )

        return {"answer": completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))