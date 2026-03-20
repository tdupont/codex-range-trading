from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import OHLCV, Stock
from app.services.provider import MarketDataProvider


class IngestionService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def ingest_stock_history(
        self,
        session: Session,
        stock: Stock,
        start_date: date,
        end_date: date,
    ) -> int:
        bars = self.provider.get_daily_bars(stock.ticker, start_date, end_date)
        existing = {
            candle.trade_date: candle
            for candle in session.scalars(
                select(OHLCV).where(
                    OHLCV.stock_id == stock.id,
                    OHLCV.trade_date >= start_date,
                    OHLCV.trade_date <= end_date,
                )
            )
        }
        ingested_at = datetime.now(timezone.utc)
        count = 0
        for bar in bars:
            candle = existing.get(bar.trade_date)
            payload = {
                "open": Decimal(str(bar.open)),
                "high": Decimal(str(bar.high)),
                "low": Decimal(str(bar.low)),
                "close": Decimal(str(bar.close)),
                "adjusted_close": Decimal(str(bar.adjusted_close)) if bar.adjusted_close is not None else None,
                "volume": bar.volume,
                "vwap": Decimal(str(bar.vwap)) if bar.vwap is not None else None,
                "data_source": bar.data_source,
                "is_adjusted_series": bar.is_adjusted_series,
                "ingested_at": ingested_at,
            }
            if candle is None:
                candle = OHLCV(stock_id=stock.id, trade_date=bar.trade_date, **payload)
                session.add(candle)
            else:
                for field, value in payload.items():
                    setattr(candle, field, value)
            count += 1
        session.flush()
        return count

    def ingest_universe(self, session: Session, stocks: list[Stock], lookback_days: int) -> int:
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days * 2)
        total = 0
        for stock in stocks:
            if stock.is_active:
                total += self.ingest_stock_history(session, stock, start_date, end_date)
        return total
