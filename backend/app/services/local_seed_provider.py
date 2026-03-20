from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from app.core.settings import Settings
from app.services.provider import MarketDataProvider
from app.services.types import DailyBar, UniverseMember


class LocalSeedProvider(MarketDataProvider):
    """Deterministic local provider for MVP development.

    Assumption documented for the MVP: when no external market data provider is configured,
    the app uses a bundled S&P 500 constituent snapshot and generates deterministic daily
    OHLCV bars so the full screening pipeline remains runnable locally.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._universe_path = Path(settings.local_universe_path)

    def get_universe(self) -> list[UniverseMember]:
        frame = pd.read_csv(self._universe_path)
        return [
            UniverseMember(
                ticker=row.ticker,
                name=row.name,
                exchange=row.exchange if pd.notna(row.exchange) else None,
                sector=row.sector if pd.notna(row.sector) else None,
                industry=row.industry if pd.notna(row.industry) else None,
                source="local_seed_snapshot",
            )
            for row in frame.itertuples(index=False)
        ]

    def get_daily_bars(self, ticker: str, start_date: date, end_date: date) -> list[DailyBar]:
        dates = pd.bdate_range(start=start_date, end=end_date)
        seed = sum(ord(char) for char in ticker)
        rng = np.random.default_rng(seed)
        anchor = 60 + (seed % 140)
        amplitude = 3 + ((seed % 12) / 2)
        slope = ((seed % 7) - 3) * 0.01
        phase = (seed % 360) * np.pi / 180
        price = anchor + amplitude * np.sin(np.linspace(phase, phase + 5 * np.pi, len(dates)))
        trend = np.linspace(0, slope * len(dates), len(dates))
        noise = rng.normal(0, 0.45 + (seed % 4) * 0.08, len(dates))
        closes = price + trend + noise
        opens = closes + rng.normal(0, 0.55, len(dates))
        highs = np.maximum(opens, closes) + rng.uniform(0.15, 1.25, len(dates))
        lows = np.minimum(opens, closes) - rng.uniform(0.15, 1.25, len(dates))
        volumes = (1_500_000 + rng.integers(0, 8_000_000, len(dates)) + (seed % 40) * 75_000).astype(int)

        return [
            DailyBar(
                ticker=ticker,
                trade_date=trade_date.date(),
                open=round(float(open_price), 4),
                high=round(float(high_price), 4),
                low=round(float(low_price), 4),
                close=round(float(close_price), 4),
                volume=int(volume),
                adjusted_close=round(float(close_price), 4),
                vwap=round(float((high_price + low_price + close_price) / 3), 4),
                data_source="local_seed",
                is_adjusted_series=False,
            )
            for trade_date, open_price, high_price, low_price, close_price, volume in zip(
                dates,
                opens,
                highs,
                lows,
                closes,
                volumes,
                strict=True,
            )
        ]

    def provider_metadata(self) -> dict[str, str]:
        return {
            "provider": "local_seed",
            "timezone": "America/New_York",
            "adjustment_behavior": "unadjusted_ohlc_adjusted_close_equals_close",
        }
