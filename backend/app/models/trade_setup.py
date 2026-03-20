from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class TradeSetup(TimestampMixin, Base):
    __tablename__ = "trade_setups"
    __table_args__ = (
        UniqueConstraint("range_id", "direction", name="uq_trade_setups_range_id_direction"),
        Index("ix_trade_setups_as_of_date_status", "as_of_date", "status"),
        Index("ix_trade_setups_stock_as_of_date_desc", "stock_id", "as_of_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    range_id: Mapped[int] = mapped_column(ForeignKey("ranges.id", ondelete="CASCADE"))
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    as_of_date: Mapped[date] = mapped_column(Date)
    direction: Mapped[str] = mapped_column(String(8))
    status: Mapped[str] = mapped_column(String(16))
    entry_zone_low: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    entry_zone_high: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    stop_price: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    target_1_price: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    target_2_price: Mapped[Decimal] = mapped_column(Numeric(18, 6))
    rejection_signal: Mapped[str | None] = mapped_column(String(64), nullable=True)
    latest_close: Mapped[Decimal] = mapped_column(Numeric(18, 6))

    range = relationship("RangeSnapshot", back_populates="setups")
    stock = relationship("Stock", back_populates="setups")
    alerts = relationship("Alert", back_populates="trade_setup")
