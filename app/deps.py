# app/deps.py
from datetime import datetime, timedelta
from typing import Optional, Dict

import jwt
from fastapi import Header, HTTPException, status

from app.config import settings  # SECRET_KEY, ж.б. ушул жерден келет

ALGORITHM = "HS256"


def create_jwt(payload: dict, expires_in: int = 3600) -> str:
    """
    JWT түзөт. expires_in секунда (дефолт 1 саат).
    payload'га exp кошуп, HS256 менен кол тамга коёт.
    """
    to_encode = payload.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> Dict:
    """
    JWT текшерип-декоддойт. Мөөнөтү өтсө же туура эмес болсо — 401.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def _extract_bearer(authorization: Optional[str] = Header(default=None)) -> str:
    """
    Authorization хедерден 'Bearer <token>' бөлүп чыгарат.
    Жок болсо же формат туура эмес болсо — 401.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header must be 'Bearer <token>'",
        )

    return parts[1]


def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> Dict:
    """
    FastAPI dependency: учурдагы колдонуучунун клеймдерин кайтарат.
    Маршруттарда Depends(get_current_user) катары колдонулат.
    """
    token = _extract_bearer(authorization)
    claims = decode_jwt(token)
    return claims


def require_admin(
    authorization: Optional[str] = Header(default=None),
) -> Dict:
    """
    Админ гана кирчү маршруттар үчүн.
    role == 'admin' болбосо — 403 кайтарат.
    """
    claims = get_current_user(authorization)
    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return claims
