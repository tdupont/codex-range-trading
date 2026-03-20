from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="range-trading-screener-api")
    app_env: str = Field(default="development")
    api_prefix: str = Field(default="/api/v1")
    backend_host: str = Field(default="0.0.0.0")
    backend_port: int = Field(default=8000)
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/range_trading"
    )
    alembic_database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/range_trading"
    )
    cors_origins: str = Field(default="http://localhost:3000")
    market_universe: str = Field(default="sp500")
    scan_timeframe: str = Field(default="1d")
    scan_lookback_days: int = Field(default=180)
    range_lookback_days: int = Field(default=30)
    adx_period: int = Field(default=14)
    sma_period: int = Field(default=20)
    atr_period: int = Field(default=14)
    rsi_period: int = Field(default=14)
    max_sma20_slope_abs: float = Field(default=0.15)
    containment_threshold: float = Field(default=0.90)
    min_touch_count: int = Field(default=2)
    min_range_width_atr_multiple: float = Field(default=1.5)
    zone_atr_multiple: float = Field(default=0.3)
    stop_buffer_atr_multiple: float = Field(default=0.5)
    touch_cooldown_days: int = Field(default=3)
    market_data_provider: str = Field(default="stooq")
    market_data_api_key: str | None = None
    local_universe_path: str = Field(default="backend/data/sp500_seed.csv")
    scoring_version: str = Field(default="mvp-v1")

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
