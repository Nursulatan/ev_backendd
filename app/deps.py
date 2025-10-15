# app/deps.py
from datetime import datetime, timedelta
from typing import Optional, Dict


from fastapi import Header, HTTPException, status

from app.config import settings  # settings.SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

ALGORITHM = "HS256"


def create_jwt(payload: Dict, expires_in: int = 3600) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(seconds=expires_in)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> Dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def _extract_bearer(authorization: Optional[str]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid",
        )
    return authorization.split(" ", 1)[1].strip()


# 👉 Мына ушул функцияны роуттордо Depends катары колдонобуз
def get_current_user(Authorization: Optional[str] = Header(None)) -> Dict:
    token = _extract_bearer(Authorization)
    payload = decode_jwt(token)

    # кааласаң кошумча текшерүү: ролу adminбы?
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return payload  # мисалы {"sub": "admin", "role": "admin", "exp": ...}
