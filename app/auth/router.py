# app/auth/router.py
from __future__ import annotations

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# Проекттин ички импорттору (пакеттин аты app)
from app.config import settings
from app.deps import create_jwt, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


# --------- Schemas ---------
class AdminLogin(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    sub: str
    role: str


# --------- Endpoints ---------
@router.post("/admin/login", response_model=TokenResponse, summary="Admin Login")
def admin_login(body: AdminLogin) -> TokenResponse:
    """
    Админ логин. Туура логин/пароль келсе JWT кайтарат.

    Request:
      {
        "username": "admin",
        "password": "supersecret"
      }

    Response:
      {
        "access_token": "<jwt>",
        "token_type": "bearer",
        "expires_in": 3600
      }
    """
    if (
        body.username != settings.ADMIN_USERNAME
        or body.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Токендин жашоо мөөнөтү (секунд)
    expires_in = settings.JWT_EXPIRES_IN or 3600
    token = create_jwt(
        payload={"sub": body.username, "role": "admin"},
        expires_delta=timedelta(seconds=expires_in),
    )

    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=UserInfo, summary="Who am I")
def who_am_i(user: dict = Depends(get_current_user)) -> UserInfo:
    """
    Токен аркылуу учурдагы колдонуучуну кайтарат.
    Authorization: Bearer <token>
    """
    return UserInfo(sub=user["sub"], role=user.get("role", "user"))
