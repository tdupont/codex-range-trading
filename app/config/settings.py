"""Application settings for the Range Trading Screener MVP."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional local convenience dependency
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "range-trading-screener")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/range_trading.db")
    streamlit_server_port: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    market_universe: str = os.getenv("MARKET_UNIVERSE", "sp500")
    default_timeframe: str = os.getenv("DEFAULT_TIMEFRAME", "1d")
    supported_scan_timeframes: tuple[str, ...] = tuple(
        part.strip() for part in os.getenv("SUPPORTED_SCAN_TIMEFRAMES", "1d,1wk,1mo").split(",") if part.strip()
    )
    scan_lookback_bars: int = int(os.getenv("SCAN_LOOKBACK_BARS", "180"))
    range_lookback_bars: int = int(os.getenv("RANGE_LOOKBACK_BARS", "30"))
    adx_period: int = int(os.getenv("ADX_PERIOD", "14"))
    sma_period: int = int(os.getenv("SMA_PERIOD", "20"))
    atr_period: int = int(os.getenv("ATR_PERIOD", "14"))
    rsi_period: int = int(os.getenv("RSI_PERIOD", "14"))
    max_normalized_sma_slope: float = float(os.getenv("MAX_NORMALIZED_SMA_SLOPE", "0.15"))
    min_touch_count: int = int(os.getenv("MIN_TOUCH_COUNT", "2"))
    touch_separation_bars: int = int(os.getenv("TOUCH_SEPARATION_BARS", "3"))
    touch_tolerance_atr_multiple: float = float(os.getenv("TOUCH_TOLERANCE_ATR_MULTIPLE", "0.30"))
    min_range_width_atr_multiple: float = float(os.getenv("MIN_RANGE_WIDTH_ATR_MULTIPLE", "2.0"))
    max_drift_to_range_ratio: float = float(os.getenv("MAX_DRIFT_TO_RANGE_RATIO", "0.25"))
    zone_atr_multiple: float = float(os.getenv("ZONE_ATR_MULTIPLE", "0.30"))
    stop_buffer_atr_multiple: float = float(os.getenv("STOP_BUFFER_ATR_MULTIPLE", "0.50"))
    recent_breakout_lookback_bars: int = int(os.getenv("RECENT_BREAKOUT_LOOKBACK_BARS", "3"))
    default_scan_limit: int = int(os.getenv("DEFAULT_SCAN_LIMIT", "100"))
    liquidity_lookback_bars: int = int(os.getenv("LIQUIDITY_LOOKBACK_BARS", "20"))
    historical_market_data_provider: str = os.getenv("HISTORICAL_MARKET_DATA_PROVIDER", "stooq")
    historical_market_data_api_key: str = os.getenv("HISTORICAL_MARKET_DATA_API_KEY", "")
    live_quote_provider: str = os.getenv("LIVE_QUOTE_PROVIDER", "stooq")
    live_quote_api_key: str = os.getenv("LIVE_QUOTE_API_KEY", "")
    base_dir: Path = Path(__file__).resolve().parents[2]

    @property
    def data_dir(self) -> Path:
        return self.base_dir / "data"

    @property
    def seeds_dir(self) -> Path:
        return self.data_dir / "seeds"

    @property
    def sample_dir(self) -> Path:
        return self.data_dir / "sample"

    @property
    def sp500_seed_path(self) -> Path:
        return self.seeds_dir / "sp500_seed.csv"


settings = Settings()
