"""Provider abstractions for historical bars and live quotes."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from app.models import HistoricalBar, LiveQuote, UniverseMember


class HistoricalMarketDataProvider(Protocol):
    """Historical provider used for all analytics inputs."""

    def get_stock_universe(self) -> list[UniverseMember]:
        """Return the S&P 500 universe snapshot."""

    def get_ohlcv(
        self,
        ticker: str,
        timeframe: str,
        start_date: date,
        end_date: date,
    ) -> list[HistoricalBar]:
        """Return completed OHLCV bars for one ticker."""

    def get_last_completed_bar_date(self, timeframe: str) -> date:
        """Return the most recent completed bar date available."""


class LiveQuoteProvider(Protocol):
    """Optional provider used only for display-time quote context."""

    def get_latest_quote(self, ticker: str) -> LiveQuote:
        """Return the latest quote for one ticker."""

    def get_latest_quotes(self, tickers: list[str]) -> dict[str, LiveQuote]:
        """Return latest quotes for many tickers."""
