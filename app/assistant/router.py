# app/assistant/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from .commands import handle_local_command
from fastapi.responses import StreamingResponse
from .tts_openai import text_to_speech_openai
import io


router = APIRouter(prefix="/assistant", tags=["assistant"])

class AskIn(BaseModel):
    message: str

@router.post("/handle")
def handle(body: AskIn):
    """
    Локалдык буйруктарды структураланган форматта кайтарат.
    Табылбаса -> {"type":"none"}.
    """
    cmd = handle_local_command(body.message)
    return cmd or {"type": "none"}


@router.post("/speak")
def speak(body: AskIn):
    """
    OpenAI аркылуу текстти үн кылып чыгарат (audio/mpeg)
    """
    try:
        audio_bytes = text_to_speech_openai(body.message)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}