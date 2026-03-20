from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, JSON, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class RangeSnapshot(TimestampMixin, Base):
    __tablename__ = "ranges"
    __table_args__ = (
        UniqueConstraint("stock_id", "as_of_date", name="uq_ranges_stock_as_of_date"),
        Index("ix_ranges_as_of_date_desc", "as_of_date"),
        Index("ix_ranges_qualified_as_of_date_desc", "qualified", "as_of_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date)
    lookback_days: Mapped[int] = mapped_column(Integer)
    upper_bound: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    lower_bound: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    midline: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    range_width: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    range_width_atr_multiple: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    support_zone_low: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    support_zone_high: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    resistance_zone_low: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    resistance_zone_high: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    containment_ratio: Mapped[Decimal] = mapped_column(Numeric(8, 6))
    support_touch_count: Mapped[int] = mapped_column(Integer)
    resistance_touch_count: Mapped[int] = mapped_column(Integer)
    latest_close: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    qualified: Mapped[bool] = mapped_column(Boolean, default=True)
    notes_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    stock = relationship("Stock", back_populates="ranges")
    score = relationship("RangeScore", back_populates="range", uselist=False, cascade="all, delete-orphan")
    setups = relationship("TradeSetup", back_populates="range", cascade="all, delete-orphan")
