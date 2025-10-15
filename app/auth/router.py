# app/auth/router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.config import settings
from app.deps import create_jwt, get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["auth"])

class AdminLogin(BaseModel):
    username: str
    password: str

@router.post("/admin/login")
def admin_login(body: AdminLogin):
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({"sub": body.username, "role": "admin"}, expires_in=3600)
    return {"access_token": token, "token_type": "bearer"}
