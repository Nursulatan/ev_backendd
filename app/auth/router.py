from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 🔧 Туура импорттор (пакет ичинен)
from app._deps import create_jwt
from app._config import settings

# Router түзөбүз
router = APIRouter(prefix="/auth", tags=["auth"])

# Модель – админ логин үчүн
class AdminLogin(BaseModel):
    username: str
    password: str

# Маршрут – /auth/admin/login
@router.post("/admin/login")
def admin_login(body: AdminLogin):
    # Колдонуучунун атын жана сырсөзүн текшерүү
    if body.username != settings.ADMIN_USERNAME or body.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    # Токен түзүү (JWT)
    token = create_jwt({"sub": body.username, "role": "admin"})

    # Натыйжаны кайтаруу
    return {"access_token": token, "token_type": "bearer"}
