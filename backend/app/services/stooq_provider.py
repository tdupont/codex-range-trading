from __future__ import annotations

import csv
from datetime import date
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

from app.services.provider import MarketDataProvider
from app.services.types import DailyBar, UniverseMember

if TYPE_CHECKING:
    from app.core.settings import Settings


class StooqProvider(MarketDataProvider):
    """Historical daily data provider backed by Stooq's CSV endpoint."""

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
                source="stooq_seed_snapshot",
            )
            for row in frame.itertuples(index=False)
        ]

    def get_daily_bars(self, ticker: str, start_date: date, end_date: date) -> list[DailyBar]:
        with urlopen(self._build_url(ticker), timeout=20) as response:  # noqa: S310
            payload = response.read().decode("utf-8")
        return self._parse_daily_csv(
            ticker=ticker,
            payload=payload,
            start_date=start_date,
            end_date=end_date,
        )

    def provider_metadata(self) -> dict[str, str]:
        return {
            "provider": "stooq",
            "timezone": "America/New_York",
            "adjustment_behavior": "unadjusted_ohlc_adjusted_close_equals_close",
        }

    @staticmethod
    def _build_url(ticker: str) -> str:
        query = urlencode({"s": f"{ticker.lower()}.us", "i": "d"})
        return f"https://stooq.com/q/d/l/?{query}"

    @staticmethod
    def _parse_daily_csv(
        ticker: str,
        payload: str,
        start_date: date,
        end_date: date,
    ) -> list[DailyBar]:
        bars: list[DailyBar] = []
        for row in csv.DictReader(StringIO(payload)):
            if not row:
                continue
            trade_date = date.fromisoformat(row["Date"])
            if trade_date < start_date or trade_date > end_date:
                continue
            if row["Open"] in {"", "0", "null"}:
                continue
            close = float(row["Close"])
            high = float(row["High"])
            low = float(row["Low"])
            bars.append(
                DailyBar(
                    ticker=ticker,
                    trade_date=trade_date,
                    open=float(row["Open"]),
                    high=high,
                    low=low,
                    close=close,
                    volume=int(float(row["Volume"])),
                    adjusted_close=close,
                    vwap=(high + low + close) / 3,
                    data_source="stooq",
                    is_adjusted_series=False,
                )
            )
        return bars
