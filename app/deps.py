# app/deps.py
from datetime import datetime, timedelta
from typing import Dict, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer()  # <-- Мына ушул security схемасы Swagger’ге "Authorize" чыгарат


def create_jwt(payload: Dict, expires_in: int = 3600) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    return jwt.encode(to_encode, settings.secret_key,ALGORITHM)


def decode_jwt(token: str) -> Dict:
    try:
        return jwt.decode(token, settings.secret_key,[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict:
    token = credentials.credentials  # Bearer <token>’догу токен бөлүгү
    return decode_jwt(token)


def require_admin(user: Dict = Depends(get_current_user)) -> Dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user
