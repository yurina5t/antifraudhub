# app/core/config.py
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # antifraud thresholds
    FRAUD_REVIEW_THRESHOLD: float = 0.134
    FRAUD_BLOCK_THRESHOLD: float = 0.70

    AUTH_ENABLED: bool = False

    model_config = ConfigDict(
        env_prefix="",
        extra="ignore", 
    )

def get_settings() -> Settings:
    return Settings()