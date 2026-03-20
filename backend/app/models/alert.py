from __future__ import annotations

from sqlalchemy import ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_created_at_desc", "created_at"),
        Index("ix_alerts_stock_created_at_desc", "stock_id", "created_at"),
        Index("ix_alerts_alert_type_created_at_desc", "alert_type", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id", ondelete="CASCADE"), index=True)
    range_id: Mapped[int | None] = mapped_column(ForeignKey("ranges.id", ondelete="SET NULL"), nullable=True)
    trade_setup_id: Mapped[int | None] = mapped_column(
        ForeignKey("trade_setups.id", ondelete="SET NULL"), nullable=True
    )
    alert_type: Mapped[str] = mapped_column(String(32))
    direction: Mapped[str | None] = mapped_column(String(8), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    payload_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    stock = relationship("Stock", back_populates="alerts")
    trade_setup = relationship("TradeSetup", back_populates="alerts")
