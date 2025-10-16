# app/auth/router.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.deps import create_jwt

router = APIRouter(prefix="/auth", tags=["auth"])


class AdminLogin(BaseModel):
    username: str
    password: str


@router.post("/admin/login")
def admin_login(body: AdminLogin):
    if body.username != settings.admin_username or body.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_jwt({"sub": body.username, "role": "admin"}, expires_in=settings.access_token_expire_minutes)
    return {"access_token": token, "token_type": "bearer"}