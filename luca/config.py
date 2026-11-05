from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"


class Settings(BaseSettings):
    """Runtime configuration loaded from the environment and `.env`."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    db_uri: str = "postgresql+psycopg://:@/luca"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    env: str = "development"
    app_name: str = "luca"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
