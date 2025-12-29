# app/database/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- PostgreSQL ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASS: str = "postgres"
    DB_NAME: str = "antifraudhub"

    # --- ClickHouse ---
    CLICK_HOST: str = "localhost"
    CLICK_PORT: int = 8123
    CLICK_USER: str = "default"
    CLICK_PASSWORD: str = ""

    # --- Application ---
    APP_NAME: str = "AntifraudHub API"
    APP_DESCRIPTION: str = "Backend for fraud scoring"
    API_VERSION: str = "1.0"
    DEBUG: bool = True

    # --- JWT ---
    SECRET_KEY: str = "dev-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # --- Modes ---
    USE_ASYNC: bool = False
    TESTING: bool = False

    # --- Build DB URL ---
    @property
    def DATABASE_URL(self) -> str:
        if self.TESTING:
            return "sqlite://"
        if self.USE_ASYNC:
            return (
                f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )

    def defaults_used(self) -> list[str]:
        provided = getattr(self, "__pydantic_fields_set__", set())
        return [name for name in self.model_fields.keys() if name not in provided]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
