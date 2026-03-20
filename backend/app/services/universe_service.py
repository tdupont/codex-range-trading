from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.models import Stock
from app.services.provider import MarketDataProvider


class UniverseService:
    def __init__(self, settings: Settings, provider: MarketDataProvider) -> None:
        self.settings = settings
        self.provider = provider

    def refresh(self, session: Session) -> list[Stock]:
        members = self.provider.get_universe()
        seen_tickers = {member.ticker for member in members}
        existing = {
            stock.ticker: stock
            for stock in session.scalars(select(Stock).where(Stock.universe == self.settings.market_universe))
        }

        for member in members:
            stock = existing.get(member.ticker)
            if stock is None:
                stock = Stock(
                    ticker=member.ticker,
                    name=member.name,
                    exchange=member.exchange,
                    sector=member.sector,
                    industry=member.industry,
                    is_active=True,
                    universe=self.settings.market_universe,
                    source=member.source,
                )
                session.add(stock)
                existing[member.ticker] = stock
            else:
                stock.name = member.name
                stock.exchange = member.exchange
                stock.sector = member.sector
                stock.industry = member.industry
                stock.is_active = True
                stock.source = member.source

        for ticker, stock in existing.items():
            if ticker not in seen_tickers:
                stock.is_active = False

        session.flush()
        return list(existing.values())
