from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class OHLCV(TimestampMixin, Base):
    __tablename__ = "ohlcv"
    __table_args__ = (
        UniqueConstraint("stock_id", "trade_date", name="uq_ohlcv_stock_trade_date"),
        Index("ix_ohlcv_trade_date", "trade_date"),
        Index("ix_ohlcv_stock_trade_date_desc", "stock_id", "trade_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    trade_date: Mapped[date] = mapped_column(Date)
    open: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    high: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    low: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    close: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    adjusted_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    volume: Mapped[int] = mapped_column(BigInteger)
    vwap: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    data_source: Mapped[str] = mapped_column(String(64))
    is_adjusted_series: Mapped[bool] = mapped_column(Boolean, default=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    stock = relationship("Stock", back_populates="candles")
