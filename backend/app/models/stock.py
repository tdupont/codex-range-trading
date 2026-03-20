from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Stock(TimestampMixin, Base):
    __tablename__ = "stocks"
    __table_args__ = (Index("ix_stocks_universe_is_active", "universe", "is_active"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    exchange: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(128), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    universe: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    candles = relationship("OHLCV", back_populates="stock", cascade="all, delete-orphan")
    indicators = relationship("Indicator", back_populates="stock", cascade="all, delete-orphan")
    ranges = relationship("RangeSnapshot", back_populates="stock", cascade="all, delete-orphan")
    setups = relationship("TradeSetup", back_populates="stock", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="stock", cascade="all, delete-orphan")
