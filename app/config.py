from pydantic import BaseModel
import os
class Settings(BaseModel):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_me")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OTP_TTL_SECONDS: int = int(os.getenv("OTP_TTL_SECONDS", "180"))
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "1440"))
settings = Settings()
