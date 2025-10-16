# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Админ логин/пароль
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="supersecret", alias="ADMIN_PASSWORD")

    # JWT конфигурациясы
    secret_key: str = Field(..., alias="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=3600, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # башка параметрлер болсо ушул жерге кошо бересиң…

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,   # alias менен да, талаа аты менен да толтурууга уруксат
    )

settings = Settings()