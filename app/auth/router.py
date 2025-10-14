from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Долбоор структурасына жараша иштей берсин деп эки варианттуу импорт.
try:
    # Эгер main.py "пакетте" болсо (мисалы, app/main.py)
    from .._deps import create_jwt
    from .._config import settings
except ImportError:
    # Эгер main.py _deps.py менен бир деңгээлде турса
    from _deps import create_jwt
    from _config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class AdminLogin(BaseModel):
    username: str
    password: str

@router.post("/admin/login")
def admin_login(body: AdminLogin):
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    token = create_jwt({"sub": body.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}
