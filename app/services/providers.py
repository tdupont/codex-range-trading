"""Provider implementations for the Streamlit MVP."""

from __future__ import annotations

import csv
from datetime import date, datetime, timezone
from io import StringIO
from math import pi
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import pandas as pd

from app.config.settings import Settings
from app.models import HistoricalBar, LiveQuote, UniverseMember


class LocalSeedHistoricalProvider:
    """Deterministic historical data provider for local MVP work."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._universe_frame = pd.read_csv(settings.sp500_seed_path)

    def get_stock_universe(self) -> list[UniverseMember]:
        members: list[UniverseMember] = []
        for row in self._universe_frame.itertuples(index=False):
            members.append(
                UniverseMember(
                    ticker=row.ticker,
                    name=row.name,
                    exchange=row.exchange if pd.notna(row.exchange) else None,
                    sector=row.sector if pd.notna(row.sector) else None,
                    industry=row.industry if pd.notna(row.industry) else None,
                    source="local_seed_snapshot",
                )
            )
        return members

    def get_ohlcv(
        self,
        ticker: str,
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalBar]:
        if timeframe != "1d":
            raise ValueError(f"Unsupported timeframe '{timeframe}' for MVP provider.")

        dates = pd.bdate_range(start=start_date, end=end_date)
        if len(dates) == 0:
            return []

        seed = sum(ord(char) for char in ticker)
        rng = np.random.default_rng(seed)
        anchor = 50 + (seed % 220)
        amplitude = 2.2 + ((seed % 9) * 0.45)
        phase = (seed % 360) * pi / 180
        mode = seed % 5
        path = anchor + amplitude * np.sin(np.linspace(phase, phase + 6 * pi, len(dates)))

        if mode == 0:
            path += np.linspace(-1.0, 1.0, len(dates))
        elif mode == 1:
            path += np.linspace(0.0, 6.0, len(dates))
        elif mode == 2:
            path += np.linspace(0.0, -5.0, len(dates))
        elif mode == 3:
            path += np.concatenate([np.zeros(len(dates) - 8), np.linspace(0, 4.5, 8)])

        noise_scale = 0.35 + ((seed % 7) * 0.04)
        closes = path + rng.normal(0, noise_scale, len(dates))
        opens = closes + rng.normal(0, 0.45, len(dates))
        highs = np.maximum(opens, closes) + rng.uniform(0.15, 1.0, len(dates))
        lows = np.minimum(opens, closes) - rng.uniform(0.15, 1.0, len(dates))
        volumes = (2_000_000 + rng.integers(0, 7_500_000, len(dates)) + (seed % 30) * 90_000).astype(float)

        bars: list[HistoricalBar] = []
        for trade_date, open_price, high_price, low_price, close_price, volume in zip(
            dates, opens, highs, lows, closes, volumes, strict=True
        ):
            bars.append(
                HistoricalBar(
                    ticker=ticker,
                    timeframe=timeframe,
                    bar_date=trade_date.date(),
                    open=round(max(1.0, float(open_price)), 4),
                    high=round(max(1.0, float(high_price)), 4),
                    low=round(max(0.5, float(low_price)), 4),
                    close=round(max(1.0, float(close_price)), 4),
                    adjusted_close=round(max(1.0, float(close_price)), 4),
                    volume=float(volume),
                    provider="local_seed",
                    provider_timezone="America/New_York",
                    is_complete=True,
                )
            )
        return bars

    def get_last_completed_bar_date(self, timeframe: str) -> date:
        if timeframe != "1d":
            raise ValueError(f"Unsupported timeframe '{timeframe}' for MVP provider.")
        return pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=1)[0].date()


class StooqHistoricalProvider:
    """Historical daily data provider backed by Stooq CSV downloads."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._universe_frame = pd.read_csv(settings.sp500_seed_path)

    def get_stock_universe(self) -> list[UniverseMember]:
        members: list[UniverseMember] = []
        for row in self._universe_frame.itertuples(index=False):
            members.append(
                UniverseMember(
                    ticker=row.ticker,
                    name=row.name,
                    exchange=row.exchange if pd.notna(row.exchange) else None,
                    sector=row.sector if pd.notna(row.sector) else None,
                    industry=row.industry if pd.notna(row.industry) else None,
                    source="stooq_seed_snapshot",
                )
            )
        return members

    def get_ohlcv(
        self,
        ticker: str,
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalBar]:
        if timeframe != "1d":
            raise ValueError(f"Unsupported timeframe '{timeframe}' for MVP provider.")
        with urlopen(self._build_daily_url(ticker), timeout=20) as response:  # noqa: S310
            payload = response.read().decode("utf-8")
        return self._parse_daily_csv(ticker, payload, start_date, end_date)

    def get_last_completed_bar_date(self, timeframe: str) -> date:
        if timeframe != "1d":
            raise ValueError(f"Unsupported timeframe '{timeframe}' for MVP provider.")
        return pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=1)[0].date()

    @staticmethod
    def _build_daily_url(ticker: str) -> str:
        query = urlencode({"s": f"{ticker.lower()}.us", "i": "d"})
        return f"https://stooq.com/q/d/l/?{query}"

    @staticmethod
    def _parse_daily_csv(
        ticker: str,
        payload: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalBar]:
        bars: list[HistoricalBar] = []
        for row in csv.DictReader(StringIO(payload)):
            if not row:
                continue
            bar_date = date.fromisoformat(row["Date"])
            if bar_date < start_date or bar_date > end_date:
                continue
            if row["Open"] in {"", "0", "null"}:
                continue
            close = float(row["Close"])
            bars.append(
                HistoricalBar(
                    ticker=ticker,
                    timeframe="1d",
                    bar_date=bar_date,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=close,
                    adjusted_close=close,
                    volume=float(row["Volume"]),
                    provider="stooq",
                    provider_timezone="America/New_York",
                    is_complete=True,
                )
            )
        return bars


class StooqLiveQuoteProvider:
    """Latest quote provider backed by Stooq quote CSV."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_latest_quote(self, ticker: str) -> LiveQuote:
        with urlopen(self._build_quote_url(ticker), timeout=20) as response:  # noqa: S310
            payload = response.read().decode("utf-8")
        row = self._parse_quote_csv(payload)
        last_price = float(row["close"])
        quote_dt = datetime.fromisoformat(f"{row['date']}T{row['time']}").replace(tzinfo=timezone.utc)
        return LiveQuote(
            ticker=ticker,
            quote_timestamp=quote_dt,
            last_price=round(last_price, 2),
            bid=None,
            ask=None,
            provider="stooq",
        )

    def get_latest_quotes(self, tickers: list[str]) -> dict[str, LiveQuote]:
        return {ticker: self.get_latest_quote(ticker) for ticker in tickers}

    @staticmethod
    def _build_quote_url(ticker: str) -> str:
        query = urlencode({"s": f"{ticker.lower()}.us", "f": "sd2t2ohlcvn", "e": "csv"})
        return f"https://stooq.com/q/l/?{query}"

    @staticmethod
    def _parse_quote_csv(payload: str) -> dict[str, str]:
        rows = [row for row in csv.reader(StringIO(payload)) if row]
        if not rows:
            raise ValueError("Stooq quote response was empty.")

        if rows[0][0].lower() == "symbol":
            if len(rows) < 2:
                raise ValueError("Stooq quote response contained a header but no data row.")
            header = [value.lower() for value in rows[0]]
            data = rows[1]
            return dict(zip(header, data, strict=True))

        columns = ["symbol", "date", "time", "open", "high", "low", "close", "volume", "name"]
        return dict(zip(columns, rows[0], strict=True))
