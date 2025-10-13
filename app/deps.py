from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from .config import settings

security = HTTPBearer()
ALGO = "HS256"

def create_jwt(payload: dict) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGO)

def get_current_admin(creds: HTTPAuthorizationCredentials = Depends(security)):
    token = creds.credentials
    try:
        data = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGO])
        if data.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")
        return data
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
