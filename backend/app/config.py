from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./urbanflow.db"
    secret_key: str = "change-me-in-production-urbanflow-ai-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    environment: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    class Config:
        env_file = (".env", "../.env")
        extra = "ignore"


@lru_cache
def clear_settings_cache():
    get_settings.cache_clear()


@lru_cache
def get_settings() -> Settings:
    return Settings()
