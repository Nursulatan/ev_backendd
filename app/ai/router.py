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

@router.get("/models")
def list_gemini_models():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    r = requests.get(url, timeout=20)
    return {"status": r.status_code, "data": r.json() if r.headers.get("content-type","").startswith("application/json") else r.text}