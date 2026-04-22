from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./mmg.db"
    log_level: str = "INFO"
    app_env: str = "local"
    frontend_dir: str = "frontend"


@lru_cache
def get_settings() -> Settings:
    return Settings()
