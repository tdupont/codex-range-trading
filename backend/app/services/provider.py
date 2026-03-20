from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from app.services.types import DailyBar, UniverseMember


class MarketDataProvider(ABC):
    @abstractmethod
    def get_universe(self) -> list[UniverseMember]: ...

    @abstractmethod
    def get_daily_bars(self, ticker: str, start_date: date, end_date: date) -> list[DailyBar]: ...

    def get_daily_bars_bulk(
        self,
        tickers: list[str],
        start_date: date,
        end_date: date,
    ) -> dict[str, list[DailyBar]]:
        return {ticker: self.get_daily_bars(ticker, start_date, end_date) for ticker in tickers}

    @abstractmethod
    def provider_metadata(self) -> dict[str, str]: ...
