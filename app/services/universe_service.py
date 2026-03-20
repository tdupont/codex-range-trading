"""Universe loading and refresh logic."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Stock
from app.services.provider_interfaces import HistoricalMarketDataProvider
from app.services.storage_service import StorageService


class UniverseService:
    def __init__(self, provider: HistoricalMarketDataProvider) -> None:
        self.provider = provider

    def refresh(self, session: Session) -> list[Stock]:
        members = self.provider.get_stock_universe()
        now = StorageService.utc_now()
        existing = {stock.ticker: stock for stock in session.scalars(select(Stock)).all()}
        touched: set[str] = set()

        for member in members:
            touched.add(member.ticker)
            stock = existing.get(member.ticker)
            if stock is None:
                stock = Stock(
                    ticker=member.ticker,
                    name=member.name,
                    exchange=member.exchange,
                    sector=member.sector,
                    industry=member.industry,
                    is_active=True,
                    universe_source=member.source,
                    created_at=now,
                    updated_at=now,
                )
                session.add(stock)
                existing[member.ticker] = stock
            else:
                stock.name = member.name
                stock.exchange = member.exchange
                stock.sector = member.sector
                stock.industry = member.industry
                stock.is_active = True
                stock.universe_source = member.source
                stock.updated_at = now

        for ticker, stock in existing.items():
            if ticker not in touched:
                stock.is_active = False
                stock.updated_at = now

        session.flush()
        return list(session.scalars(select(Stock).order_by(Stock.ticker.asc())))
