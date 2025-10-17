# app/assistant/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from .commands import handle_local_command

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
