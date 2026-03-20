from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Indicator(TimestampMixin, Base):
    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint("stock_id", "trade_date", name="uq_indicators_stock_trade_date"),
        Index("ix_indicators_trade_date", "trade_date"),
        Index("ix_indicators_stock_trade_date_desc", "stock_id", "trade_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date)
    sma_20: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    sma_20_slope: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    atr_14: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    adx_14: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    rsi_14: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    avg_dollar_volume_20: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    stock = relationship("Stock", back_populates="indicators")
