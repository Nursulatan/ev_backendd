from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from jose import jwt

# Эгерде сенде settings бар болсо (app/config.py), ошондон алабыз.
# Болбосо, төмөнкү DEFAULT_* маанилери иштеп кетет.
try:
    # app/config.py ичинде Settings сыяктуу класс болсо:
    #   ADMIN_USERNAME, ADMIN_PASSWORD, JWT_SECRET, JWT_EXPIRES_MIN
    from app.config import settings  # type: ignore
    ADMIN_USERNAME = getattr(settings, "ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = getattr(settings, "ADMIN_PASSWORD", "supersecret")
    JWT_SECRET     = getattr(settings, "JWT_SECRET", "change-me-please")
    JWT_EXPIRES_MIN = int(getattr(settings, "JWT_EXPIRES_MIN", 60))
except Exception:
    # Фолбэк (локалда же демо үчүн)
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "supersecret"
    JWT_SECRET     = "change-me-please"
    JWT_EXPIRES_MIN = 60

JWT_ALG = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])


# --------- Schemas ----------
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # секунда менен


# --------- Helpers ----------
def _create_access_token(payload: Dict[str, Any], minutes: int) -> str:
    now = datetime.utcnow()
    to_encode = {
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        **payload,
    }
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)


def _do_login(body: LoginRequest) -> TokenResponse:
    if body.username != ADMIN_USERNAME or body.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = _create_access_token(
        {"sub": body.username, "role": "admin"},
        minutes=JWT_EXPIRES_MIN,
    )
    return TokenResponse(access_token=token, expires_in=JWT_EXPIRES_MIN * 60)


# --------- Routes ----------
@router.post("/login", response_model=TokenResponse, summary="Login")
async def login(body: LoginRequest) -> TokenResponse:
    """
    Негизги логин маршруту. Flutter’ди `/auth/login` кылсаң да, иштейт.
    """
    return _do_login(body)


@router.post("/admin/login", response_model=TokenResponse, summary="Admin Login (legacy)")
async def admin_login(body: LoginRequest) -> TokenResponse:
    """
    Flutter’деги азыркы жолду бузбайлы деп кошумча маршрут.
    `/auth/admin/login` да ошол эле токенди берет.
    """
    return _do_login(body)
 