from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# ТУУРА импорт:
from app.deps import create_jwt
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class AdminLogin(BaseModel):
    username: str
    password: str

@router.post("/admin/login")
def admin_login(body: AdminLogin):
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt({"sub": body.username, "role": "admin"})
    return {"access_token": token, "token_type": "bearer"}
