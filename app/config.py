# app/config.py
import os

class Settings:
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "supersecret")
    JWT_SECRET     = os.getenv("JWT_SECRET", "change-me-please")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

settings = Settings()
