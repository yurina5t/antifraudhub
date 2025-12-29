# app/services/clickhouse_client.py
import clickhouse_connect
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class ClickHouseSettings(BaseSettings):
    CLICK_HOST: str
    CLICK_PORT: int = 8123
    CLICK_USER: str
    CLICK_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache()
def get_ch_settings() -> ClickHouseSettings:
    return ClickHouseSettings()

def get_clickhouse_client():
    s = get_ch_settings()
    return clickhouse_connect.get_client(
        host=s.CLICK_HOST,
        port=s.CLICK_PORT,
        username=s.CLICK_USER,
        password=s.CLICK_PASSWORD,
        compression=True,
        connect_timeout=60,
        send_receive_timeout=60,
    )
