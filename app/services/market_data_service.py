"""Historical market data ingestion service."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.models import OHLCV, Stock
from app.services.provider_interfaces import HistoricalMarketDataProvider
from app.services.storage_service import StorageService

TIMEFRAME_LOOKBACK_MULTIPLIERS = {"1d": 2, "1wk": 10, "1mo": 45}


class MarketDataService:
    def __init__(self, settings: Settings, provider: HistoricalMarketDataProvider) -> None:
        self.settings = settings
        self.provider = provider

    def ingest_universe(self, session: Session, stocks: list[Stock], timeframe: str) -> tuple[int, object]:
        last_completed_bar_date = self.provider.get_last_completed_bar_date(timeframe)
        lookback_multiplier = TIMEFRAME_LOOKBACK_MULTIPLIERS.get(timeframe, 2)
        start_date = last_completed_bar_date - timedelta(days=self.settings.scan_lookback_bars * lookback_multiplier)
        now = StorageService.utc_now()
        bars_written = 0

        for stock in stocks:
            if not stock.is_active:
                continue

            bars = self.provider.get_ohlcv(stock.ticker, timeframe, start_date, last_completed_bar_date)
            if not bars:
                continue

            session.execute(delete(OHLCV).where(OHLCV.stock_id == stock.id, OHLCV.timeframe == timeframe))
            for bar in bars:
                if not bar.is_complete:
                    continue
                session.add(
                    OHLCV(
                        stock_id=stock.id,
                        timeframe=bar.timeframe,
                        bar_date=bar.bar_date,
                        open=bar.open,
                        high=bar.high,
                        low=bar.low,
                        close=bar.close,
                        adjusted_close=bar.adjusted_close,
                        volume=bar.volume,
                        provider=bar.provider,
                        provider_timezone=bar.provider_timezone,
                        is_complete=bar.is_complete,
                        ingested_at=now,
                    )
                )
                bars_written += 1

        session.flush()
        return bars_written, last_completed_bar_date

    def bars_for_stock(self, session: Session, stock_id: int, timeframe: str) -> list[OHLCV]:
        stmt = (
            select(OHLCV)
            .where(OHLCV.stock_id == stock_id, OHLCV.timeframe == timeframe, OHLCV.is_complete.is_(True))
            .order_by(OHLCV.bar_date.asc())
        )
        return list(session.scalars(stmt))
