from pathlib import Path
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "尚图工坊"
    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(default="sqlite+aiosqlite:///./shangtugongfang.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=720, alias="JWT_EXPIRE_MINUTES")
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="Admin12345!", alias="ADMIN_PASSWORD")
    admin_email: str = Field(default="admin@example.com", alias="ADMIN_EMAIL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    matting_api_url: str | None = Field(default=None, alias="MATTING_API_URL")
    matting_api_key: str | None = Field(default=None, alias="MATTING_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
